"""
FoundryDB SDK - Managed Inference Services API (sync and async).

A managed inference service is an open-weight LLM served by vLLM, exposing an
OpenAI-compatible endpoint on the service's own hostname. This is the service
management plane (create, list, get, delete an inference service); it is
distinct from the inference proxy management plane in ``inference.py``.

There are two SKUs, selected by ``inference_sku`` (or inferred from
``plan_name``):

* ``serverless`` multiplexes the service onto a platform-owned shared GPU
  pool. It takes no plan and rents no card, is limited to curated catalog
  models a pool is already serving, and is billed per token (and per image for
  the diffusion models) against the published rate card, with the
  organization's monthly free token allowance consumed first.
* ``dedicated`` rents a whole-card GPU server for the tenant. It takes a GPU
  plan, serves curated or Hugging Face models, supports LoRA adapters and
  keep-warm, and is billed per GPU-hour for as long as the card is allocated
  rather than per token.

Either way the customer calls ``endpoint_base_url`` with an ``fdb-inf`` key.
On that per-service hostname the model field is
``foundrydb_managed/<served_model_name>``; the unprefixed served model name is
also accepted there as a convenience for apps that hardcode it.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from .client import AsyncHTTPClient, HTTPClient
from .types import (
    InferenceConfig,
    InferenceFitCheckResult,
    InferenceModelAdapter,
    InferenceModelRate,
    InferenceService,
    InferenceServiceMetrics,
    InferenceServiceUsage,
    ServerlessInferenceModel,
)


def _create_body(
    name: str,
    inference_config: InferenceConfig,
    inference_sku: Optional[str],
    plan_name: Optional[str],
    zone: Optional[str],
    organization_id: Optional[str],
) -> Dict[str, Any]:
    body: Dict[str, Any] = {
        "name": name,
        "inference_config": inference_config.to_dict(),
    }
    if inference_sku is not None:
        body["inference_sku"] = inference_sku
    if plan_name is not None:
        body["plan_name"] = plan_name
    if zone is not None:
        body["zone"] = zone
    if organization_id is not None:
        body["organization_id"] = organization_id
    return body


def _fit_check_body(
    model_source: str,
    model_id: str,
    plan_name: str,
    max_model_len: Optional[int],
    quantization: Optional[str],
    kv_cache_dtype: Optional[str],
    gpu_memory_utilization: Optional[float],
) -> Dict[str, Any]:
    body: Dict[str, Any] = {
        "model_source": model_source,
        "model_id": model_id,
        "plan_name": plan_name,
    }
    if max_model_len is not None:
        body["max_model_len"] = max_model_len
    if quantization is not None:
        body["quantization"] = quantization
    if kv_cache_dtype is not None:
        body["kv_cache_dtype"] = kv_cache_dtype
    if gpu_memory_utilization is not None:
        body["gpu_memory_utilization"] = gpu_memory_utilization
    return body


def _register_adapter_body(
    base_model_id: str,
    served_model_name: str,
    version: int,
    files_bucket: str,
    files_key_prefix: str,
    adapter_sha256: str,
    size_bytes: int,
    base_model_license: Optional[str],
    organization_id: Optional[str],
) -> Dict[str, Any]:
    body: Dict[str, Any] = {
        "base_model_id": base_model_id,
        "served_model_name": served_model_name,
        "version": version,
        "files_bucket": files_bucket,
        "files_key_prefix": files_key_prefix,
        "adapter_sha256": adapter_sha256,
        "size_bytes": size_bytes,
    }
    if base_model_license is not None:
        body["base_model_license"] = base_model_license
    if organization_id is not None:
        body["organization_id"] = organization_id
    return body


def _serverless_config(model_id: str, license_accepted: bool) -> InferenceConfig:
    return InferenceConfig(
        model_id=model_id,
        model_source="curated",
        license_accepted=license_accepted,
    )


class InferenceServicesAPI:
    """Manages inference services: model serving on GPU (sync)."""

    def __init__(self, http: HTTPClient) -> None:
        self._http = http

    @staticmethod
    def _base() -> str:
        return "/inference-services"

    @classmethod
    def _service(cls, service_id: str) -> str:
        return f"{cls._base()}/{service_id}"

    # ------------------------------------------------------------------
    # Service lifecycle
    # ------------------------------------------------------------------

    def list(self) -> List[InferenceService]:
        """Return the inference services visible to the authenticated user
        (the active organization's, or the caller's own)."""
        data = self._http.get(self._base())
        return [
            InferenceService.from_dict(s)
            for s in data.get("inference_services", [])
        ]

    def get(self, service_id: str) -> Optional[InferenceService]:
        """Return one inference service.

        Returns ``None`` when it does not exist (404).
        """
        try:
            data = self._http.get(self._service(service_id))
        except Exception as exc:
            from .types import FoundryDBError
            if isinstance(exc, FoundryDBError) and exc.status_code == 404:
                return None
            raise
        return InferenceService.from_dict(data)

    def create(
        self,
        *,
        name: str,
        inference_config: InferenceConfig,
        inference_sku: Optional[str] = None,
        plan_name: Optional[str] = None,
        zone: Optional[str] = None,
        organization_id: Optional[str] = None,
    ) -> InferenceService:
        """Provision an inference service and return its initial state.

        The service is created in the ``Pending`` status; poll :meth:`get`
        until it reaches ``Running`` and ``endpoint_base_url`` is set.

        A GPU ``plan_name`` creates a dedicated whole-card service, billed per
        GPU-hour. Omitting ``plan_name`` (or setting ``inference_sku`` to
        ``"serverless"``) binds the service to the platform shared pool,
        billed per token. Serverless additionally requires a curated catalog
        model that a pool is already serving (see
        :meth:`list_serverless_models`): an unserved model is refused with
        503, and a fleet whose pools are all at their binding ceiling with
        409.

        A conditional curated model, and every Hugging Face model, requires
        ``inference_config.license_accepted`` to be true. The write-only
        ``hf_token`` is accepted here and never returned.

        Args:
            name: Service name.
            inference_config: Model selection and vLLM serving knobs.
            inference_sku: ``"dedicated"`` or ``"serverless"``. Empty is
                inferred from ``plan_name``: a GPU plan is dedicated, no plan
                is serverless.
            plan_name: GPU plan alias for a dedicated service.
            zone: Zone to provision the GPU server in.
            organization_id: Organization to assign the service to.
        """
        body = _create_body(
            name, inference_config, inference_sku, plan_name, zone, organization_id
        )
        data = self._http.post(self._base(), body)
        return InferenceService.from_dict(data)

    def create_serverless(
        self,
        *,
        name: str,
        model_id: str,
        organization_id: Optional[str] = None,
        license_accepted: bool = False,
    ) -> InferenceService:
        """Provision a serverless inference service on the platform shared
        pool for one curated catalog model.

        That model is the whole of what a serverless create takes: there is no
        plan, no zone, and no serving knobs, because the card is the
        platform's and its serving shape is fixed.

        ``model_id`` must be a curated catalog id a pool is serving right now;
        take it from :meth:`list_serverless_models` rather than guessing,
        since an unserved model is refused. It is a convenience over
        :meth:`create`: use that directly to reach the dedicated SKU or any
        other field.

        Args:
            name: Service name.
            model_id: Curated catalog model id a pool is already serving.
            organization_id: Organization to assign the service to.
            license_accepted: Accept the model's license (accept-gated
                models require it).
        """
        return self.create(
            name=name,
            inference_config=_serverless_config(model_id, license_accepted),
            inference_sku="serverless",
            organization_id=organization_id,
        )

    def delete(self, service_id: str) -> None:
        """Initiate deletion of the inference service.

        The platform tears down the vLLM runtime, ingress, certificates, DNS,
        floating IP, and the GPU server. A 404 response is treated as success
        (idempotent).
        """
        try:
            self._http.delete(self._service(service_id))
        except Exception as exc:
            from .types import FoundryDBError
            if isinstance(exc, FoundryDBError) and exc.status_code == 404:
                return
            raise

    # ------------------------------------------------------------------
    # Catalog
    # ------------------------------------------------------------------

    def list_model_rates(self) -> List[InferenceModelRate]:
        """Return the price in force right now for every curated model that
        has one, so a create flow can quote what a serverless service will
        cost before anyone commits.

        It is the same resolution the metering path uses, so the quoted price
        and the billed price cannot diverge. A model with no rate is omitted
        rather than reported at zero: zero would read as free, when the truth
        is that its price is not set yet. An empty list means nothing is
        priced yet, never an error. The listing is a property of the platform,
        not of the caller's organization.
        """
        data = self._http.get(f"{self._base()}/model-rates")
        return [InferenceModelRate.from_dict(m) for m in data.get("models", [])]

    def list_serverless_models(self) -> List[ServerlessInferenceModel]:
        """Return the curated models a serverless create can bind to right
        now: those a platform pool is already serving.

        It is the question to ask before :meth:`create_serverless`, which
        refuses any other model. An empty list is the honest "serverless has
        nothing to offer yet" answer rather than an error. The dedicated SKU
        is not constrained by this listing: it rents its own card and can
        serve any curated or Hugging Face model that fits.
        """
        data = self._http.get(f"{self._base()}/serverless-models")
        return [
            ServerlessInferenceModel.from_dict(m) for m in data.get("models", [])
        ]

    def check_fit(
        self,
        *,
        model_source: str,
        model_id: str,
        plan_name: str,
        max_model_len: Optional[int] = None,
        quantization: Optional[str] = None,
        kv_cache_dtype: Optional[str] = None,
        gpu_memory_utilization: Optional[float] = None,
    ) -> InferenceFitCheckResult:
        """Answer whether a model, at a context length, runs on a GPU plan,
        without provisioning anything: nothing is created, nothing is billed,
        and no GPU is touched.

        The fit model is weights plus kv_cache(max_model_len) plus serving
        overhead within the memory-utilization budget of the plan's VRAM.
        :meth:`create` and :meth:`switch_model` enforce the same equation, so
        a false ``fits`` here is the refusal those calls would return, and
        ``suggestions`` names the closest fix.

        A configuration that does not fit is still a successful call: the
        question was answered. An error is raised for an unknown model or plan
        (400), or when a Hugging Face model's metadata could not be fetched so
        its size is unknown (502); a curated model is sized from the catalog
        and never hits the latter.

        Args:
            model_source: ``"curated"`` or ``"huggingface"``.
            model_id: Curated catalog id, or the Hugging Face repo id.
            plan_name: GPU plan alias to test the model against.
            max_model_len: Context length to size the KV cache at.
            quantization: Format the weights are served at (for example
                ``"fp8"``, ``"awq"``).
            kv_cache_dtype: ``"auto"`` or ``"fp8"``, which halves the cache.
            gpu_memory_utilization: Fraction of the plan's VRAM the budget is
                drawn from, between 0.10 and 0.99.
        """
        body = _fit_check_body(
            model_source,
            model_id,
            plan_name,
            max_model_len,
            quantization,
            kv_cache_dtype,
            gpu_memory_utilization,
        )
        data = self._http.post(f"{self._base()}/fit-check", body)
        return InferenceFitCheckResult.from_dict(data)

    # ------------------------------------------------------------------
    # Model switch
    # ------------------------------------------------------------------

    def switch_model(
        self,
        service_id: str,
        *,
        model_id: str,
        license_accepted: bool = False,
    ) -> InferenceService:
        """Change which curated model an existing inference service serves,
        in place.

        The service's model volume is replaced by a clone of the target
        model's pre-baked volume template when the platform holds one for the
        service's zone (minutes, no weight download), or by a fresh volume
        taking the ordinary download path otherwise; the GPU server, GPU plan,
        endpoint hostname, TLS certificate, firewall rules, inference keys,
        and billing identity are unchanged, and the old volume is deleted only
        once the new model is in place.

        The service must be Running or Stopped and single-node, with no other
        transition in flight and no active LoRA adapter bound to the current
        base model (demote it first). Returns the service in the
        ``SwitchingModel`` status; poll :meth:`get` until it returns to the
        state it came from.

        Args:
            service_id: Inference service ID.
            model_id: Curated catalog id to switch to. It must differ from the
                model the service serves today and must fit the VRAM of the
                plan the service already runs on.
            license_accepted: Accept the target model's license. Required when
                the target is a license-gated curated model; ungated targets
                ignore it.
        """
        body: Dict[str, Any] = {"model_id": model_id}
        if license_accepted:
            body["license_accepted"] = True
        data = self._http.post(f"{self._service(service_id)}/switch-model", body)
        return InferenceService.from_dict(data)

    # ------------------------------------------------------------------
    # Usage and metrics
    # ------------------------------------------------------------------

    def get_usage(
        self,
        service_id: str,
        *,
        since: str = "",
    ) -> Optional[InferenceServiceUsage]:
        """Return the service's metered usage and cost as a time-bucketed
        series with rolled-up totals, plus the month-to-date rollup.

        Which figure is the charge depends on the SKU:
        ``month_to_date.tokens`` for a serverless service (billed per token)
        and ``month_to_date.gpu_hour`` for a dedicated one (billed per
        allocated GPU-hour). The other is a usage signal, not a bill. Returns
        ``None`` when the service does not exist (404).

        Args:
            service_id: Inference service ID.
            since: A duration (for example ``"1h"``, ``"24h"``) or an RFC 3339
                start time. Empty defaults to 24 hours and it is capped at 30
                days. The effective window never starts before the service was
                created.
        """
        params: Dict[str, Any] = {}
        if since:
            params["since"] = since
        try:
            data = self._http.get(
                f"{self._service(service_id)}/usage",
                params=params or None,
            )
        except Exception as exc:
            from .types import FoundryDBError
            if isinstance(exc, FoundryDBError) and exc.status_code == 404:
                return None
            raise
        return InferenceServiceUsage.from_dict(data)

    def get_metrics(
        self,
        service_id: str,
        *,
        since: str = "",
    ) -> Optional[InferenceServiceMetrics]:
        """Return the service's live vLLM and GPU serving telemetry as an
        ordered snapshot series with the most recent snapshot broken out as
        ``latest``.

        Returns ``None`` when the service does not exist (404).

        Args:
            service_id: Inference service ID.
            since: A duration (for example ``"30m"``, ``"1h"``) or an RFC 3339
                start time. Empty defaults to 30 minutes and the window is
                capped at 24 hours.
        """
        params: Dict[str, Any] = {}
        if since:
            params["since"] = since
        try:
            data = self._http.get(
                f"{self._service(service_id)}/metrics",
                params=params or None,
            )
        except Exception as exc:
            from .types import FoundryDBError
            if isinstance(exc, FoundryDBError) and exc.status_code == 404:
                return None
            raise
        return InferenceServiceMetrics.from_dict(data)

    # ------------------------------------------------------------------
    # LoRA fine-tuned adapters
    # ------------------------------------------------------------------

    def list_adapters(
        self, service_id: str
    ) -> Optional[List[InferenceModelAdapter]]:
        """Return the LoRA fine-tuned adapter versions relevant to the
        service, newest first.

        Those are the versions bound to it (the currently active version plus
        its superseded history) together with the organization's uploaded,
        not-yet-promoted versions trained on this service's base model, so a
        freshly registered adapter can be promoted from here. An uploaded
        version carries status ``uploaded`` until it is promoted; uploaded
        versions for another base model, organization, or service are not
        listed. Returns an empty list when nothing is bound or promotable, and
        ``None`` when the service does not exist (404).
        """
        try:
            data = self._http.get(f"{self._service(service_id)}/adapters")
        except Exception as exc:
            from .types import FoundryDBError
            if isinstance(exc, FoundryDBError) and exc.status_code == 404:
                return None
            raise
        return [InferenceModelAdapter.from_dict(a) for a in data.get("adapters", [])]

    def promote_adapter(
        self, service_id: str, adapter_id: str
    ) -> InferenceModelAdapter:
        """Promote a LoRA fine-tuned adapter version onto the service's
        serving GPU.

        The platform downloads the adapter weights from Files, verifies their
        hash, and hot-loads them into vLLM with no restart. The promoted
        version becomes active and any previously active version is marked
        superseded. Rollback is achieved through this same method by promoting
        a prior (superseded) version. Requires manage-level authority; the
        request has no body.
        """
        data = self._http.post(
            f"{self._service(service_id)}/adapters/{adapter_id}/promote"
        )
        return InferenceModelAdapter.from_dict(data.get("adapter", data))

    def demote_adapter(
        self, service_id: str, adapter_id: str
    ) -> InferenceModelAdapter:
        """Stop serving the active LoRA fine-tuned adapter version without
        promoting a replacement.

        The registry row moves to superseded and the adapter is hot-unloaded
        from the running vLLM, so the served name stops answering and its
        adapter slot is freed. It is the inverse of :meth:`promote_adapter`
        and the only exit from active that does not require another version.
        Callers still addressing ``foundrydb_managed/<served_model_name>``
        receive errors afterwards; the service keeps serving its base model
        and the version stays promotable. Requires manage-level authority; the
        request has no body.
        """
        data = self._http.post(
            f"{self._service(service_id)}/adapters/{adapter_id}/demote"
        )
        return InferenceModelAdapter.from_dict(data.get("adapter", data))

    def delete_adapter(self, adapter_id: str) -> None:
        """Remove one LoRA fine-tuned adapter version from the organization's
        serving registry.

        It is the lifecycle counterpart to :meth:`register_adapter`: an
        uploaded (never-promoted) or superseded (rolled-off) version can be
        removed so the registry does not accumulate stale rows. An
        actively-served version is refused (409): promote a different version
        or delete the inference service first. Organization-scoped; a
        cross-org, unknown, or already-removed adapter id raises a not-found
        error.
        """
        self._http.delete(f"{self._base()}/adapters/{adapter_id}")

    def register_adapter(
        self,
        *,
        base_model_id: str,
        served_model_name: str,
        version: int,
        files_bucket: str,
        files_key_prefix: str,
        adapter_sha256: str,
        size_bytes: int,
        base_model_license: Optional[str] = None,
        organization_id: Optional[str] = None,
    ) -> InferenceModelAdapter:
        """Record an uploaded LoRA fine-tuned adapter version in the serving
        registry, making it promotable.

        Call it after uploading the adapter artifact
        (``adapter_model.safetensors`` and ``adapter_config.json``) to the
        organization's Files bucket; :meth:`promote_adapter` later binds the
        version to a GPU and hot-loads it. The row is org-scoped and unbound
        (its ``inference_service_id`` is ``None``) until promote, and it
        enters the registry with status ``uploaded``. The owning organization
        is resolved from the caller's auth, or from ``organization_id`` when
        set and the caller is a member of it; it is never trusted from the
        artifact.

        Args:
            base_model_id: The base model the adapter was trained against; it
                must later match the serving service's model id or Hugging
                Face repo.
            served_model_name: The customer-facing name the adapter answers
                to, becoming ``foundrydb_managed/<served_model_name>``.
            version: Monotonic per (organization, served model name), at least
                1.
            files_bucket: The organization's Files bucket holding the artifact.
            files_key_prefix: The Files key prefix holding the artifact.
            adapter_sha256: The 64-character lowercase hex sha256 of
                ``adapter_model.safetensors``, re-verified after download
                before loading.
            size_bytes: The artifact size in bytes.
            base_model_license: The base-model license that travels with the
                weights.
            organization_id: Register under a specific organization the caller
                belongs to. Empty uses the caller's active organization.
        """
        body = _register_adapter_body(
            base_model_id,
            served_model_name,
            version,
            files_bucket,
            files_key_prefix,
            adapter_sha256,
            size_bytes,
            base_model_license,
            organization_id,
        )
        data = self._http.post(f"{self._base()}/adapters", body)
        return InferenceModelAdapter.from_dict(data.get("adapter", data))


class AsyncInferenceServicesAPI:
    """Manages inference services: model serving on GPU (async)."""

    def __init__(self, http: AsyncHTTPClient) -> None:
        self._http = http

    @staticmethod
    def _base() -> str:
        return "/inference-services"

    @classmethod
    def _service(cls, service_id: str) -> str:
        return f"{cls._base()}/{service_id}"

    async def list(self) -> List[InferenceService]:
        """Return the inference services visible to the authenticated user."""
        data = await self._http.get(self._base())
        return [
            InferenceService.from_dict(s)
            for s in data.get("inference_services", [])
        ]

    async def get(self, service_id: str) -> Optional[InferenceService]:
        """Return one inference service, or ``None`` when it does not exist."""
        try:
            data = await self._http.get(self._service(service_id))
        except Exception as exc:
            from .types import FoundryDBError
            if isinstance(exc, FoundryDBError) and exc.status_code == 404:
                return None
            raise
        return InferenceService.from_dict(data)

    async def create(
        self,
        *,
        name: str,
        inference_config: InferenceConfig,
        inference_sku: Optional[str] = None,
        plan_name: Optional[str] = None,
        zone: Optional[str] = None,
        organization_id: Optional[str] = None,
    ) -> InferenceService:
        """Provision an inference service and return its initial state.

        A GPU ``plan_name`` creates a dedicated whole-card service billed per
        GPU-hour; omitting it (or setting ``inference_sku`` to
        ``"serverless"``) binds the service to the platform shared pool,
        billed per token. Poll :meth:`get` until the service reaches
        ``Running`` and ``endpoint_base_url`` is set.
        """
        body = _create_body(
            name, inference_config, inference_sku, plan_name, zone, organization_id
        )
        data = await self._http.post(self._base(), body)
        return InferenceService.from_dict(data)

    async def create_serverless(
        self,
        *,
        name: str,
        model_id: str,
        organization_id: Optional[str] = None,
        license_accepted: bool = False,
    ) -> InferenceService:
        """Provision a serverless inference service on the platform shared
        pool for one curated catalog model.

        ``model_id`` must be a curated catalog id a pool is serving right now;
        take it from :meth:`list_serverless_models`, since an unserved model
        is refused.
        """
        return await self.create(
            name=name,
            inference_config=_serverless_config(model_id, license_accepted),
            inference_sku="serverless",
            organization_id=organization_id,
        )

    async def delete(self, service_id: str) -> None:
        """Initiate deletion of the inference service (404 treated as
        success)."""
        try:
            await self._http.delete(self._service(service_id))
        except Exception as exc:
            from .types import FoundryDBError
            if isinstance(exc, FoundryDBError) and exc.status_code == 404:
                return
            raise

    async def list_model_rates(self) -> List[InferenceModelRate]:
        """Return the price in force right now for every curated model that
        has one. A model with no rate is omitted rather than reported at
        zero."""
        data = await self._http.get(f"{self._base()}/model-rates")
        return [InferenceModelRate.from_dict(m) for m in data.get("models", [])]

    async def list_serverless_models(self) -> List[ServerlessInferenceModel]:
        """Return the curated models a serverless create can bind to right
        now: those a platform pool is already serving."""
        data = await self._http.get(f"{self._base()}/serverless-models")
        return [
            ServerlessInferenceModel.from_dict(m) for m in data.get("models", [])
        ]

    async def check_fit(
        self,
        *,
        model_source: str,
        model_id: str,
        plan_name: str,
        max_model_len: Optional[int] = None,
        quantization: Optional[str] = None,
        kv_cache_dtype: Optional[str] = None,
        gpu_memory_utilization: Optional[float] = None,
    ) -> InferenceFitCheckResult:
        """Answer whether a model, at a context length, runs on a GPU plan,
        without provisioning anything.

        A configuration that does not fit is still a successful call: the
        question was answered, and ``suggestions`` names the closest fix.
        """
        body = _fit_check_body(
            model_source,
            model_id,
            plan_name,
            max_model_len,
            quantization,
            kv_cache_dtype,
            gpu_memory_utilization,
        )
        data = await self._http.post(f"{self._base()}/fit-check", body)
        return InferenceFitCheckResult.from_dict(data)

    async def switch_model(
        self,
        service_id: str,
        *,
        model_id: str,
        license_accepted: bool = False,
    ) -> InferenceService:
        """Change which curated model an existing inference service serves,
        in place.

        The service must be Running or Stopped and single-node, with no active
        LoRA adapter bound to the current base model (demote it first).
        Returns the service in the ``SwitchingModel`` status.
        """
        body: Dict[str, Any] = {"model_id": model_id}
        if license_accepted:
            body["license_accepted"] = True
        data = await self._http.post(
            f"{self._service(service_id)}/switch-model", body
        )
        return InferenceService.from_dict(data)

    async def get_usage(
        self,
        service_id: str,
        *,
        since: str = "",
    ) -> Optional[InferenceServiceUsage]:
        """Return the service's metered usage and cost, plus the
        month-to-date rollup. ``None`` when the service does not exist."""
        params: Dict[str, Any] = {}
        if since:
            params["since"] = since
        try:
            data = await self._http.get(
                f"{self._service(service_id)}/usage",
                params=params or None,
            )
        except Exception as exc:
            from .types import FoundryDBError
            if isinstance(exc, FoundryDBError) and exc.status_code == 404:
                return None
            raise
        return InferenceServiceUsage.from_dict(data)

    async def get_metrics(
        self,
        service_id: str,
        *,
        since: str = "",
    ) -> Optional[InferenceServiceMetrics]:
        """Return the service's live vLLM and GPU serving telemetry. ``None``
        when the service does not exist."""
        params: Dict[str, Any] = {}
        if since:
            params["since"] = since
        try:
            data = await self._http.get(
                f"{self._service(service_id)}/metrics",
                params=params or None,
            )
        except Exception as exc:
            from .types import FoundryDBError
            if isinstance(exc, FoundryDBError) and exc.status_code == 404:
                return None
            raise
        return InferenceServiceMetrics.from_dict(data)

    async def list_adapters(
        self, service_id: str
    ) -> Optional[List[InferenceModelAdapter]]:
        """Return the LoRA fine-tuned adapter versions relevant to the
        service, newest first. ``None`` when the service does not exist."""
        try:
            data = await self._http.get(f"{self._service(service_id)}/adapters")
        except Exception as exc:
            from .types import FoundryDBError
            if isinstance(exc, FoundryDBError) and exc.status_code == 404:
                return None
            raise
        return [InferenceModelAdapter.from_dict(a) for a in data.get("adapters", [])]

    async def promote_adapter(
        self, service_id: str, adapter_id: str
    ) -> InferenceModelAdapter:
        """Promote a LoRA fine-tuned adapter version onto the service's
        serving GPU, hot-loading it into vLLM with no restart."""
        data = await self._http.post(
            f"{self._service(service_id)}/adapters/{adapter_id}/promote"
        )
        return InferenceModelAdapter.from_dict(data.get("adapter", data))

    async def demote_adapter(
        self, service_id: str, adapter_id: str
    ) -> InferenceModelAdapter:
        """Stop serving the active LoRA fine-tuned adapter version without
        promoting a replacement."""
        data = await self._http.post(
            f"{self._service(service_id)}/adapters/{adapter_id}/demote"
        )
        return InferenceModelAdapter.from_dict(data.get("adapter", data))

    async def delete_adapter(self, adapter_id: str) -> None:
        """Remove one LoRA fine-tuned adapter version from the organization's
        serving registry. An actively-served version is refused (409)."""
        await self._http.delete(f"{self._base()}/adapters/{adapter_id}")

    async def register_adapter(
        self,
        *,
        base_model_id: str,
        served_model_name: str,
        version: int,
        files_bucket: str,
        files_key_prefix: str,
        adapter_sha256: str,
        size_bytes: int,
        base_model_license: Optional[str] = None,
        organization_id: Optional[str] = None,
    ) -> InferenceModelAdapter:
        """Record an uploaded LoRA fine-tuned adapter version in the serving
        registry, making it promotable.

        The row is org-scoped and unbound until promote, and it enters the
        registry with status ``uploaded``.
        """
        body = _register_adapter_body(
            base_model_id,
            served_model_name,
            version,
            files_bucket,
            files_key_prefix,
            adapter_sha256,
            size_bytes,
            base_model_license,
            organization_id,
        )
        data = await self._http.post(f"{self._base()}/adapters", body)
        return InferenceModelAdapter.from_dict(data.get("adapter", data))
