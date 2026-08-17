"""
Tests for foundrydb.inference_services - InferenceServicesAPI (sync) and
AsyncInferenceServicesAPI (async).
"""
from __future__ import annotations

import json

import httpx
import pytest
import respx

from foundrydb.inference_services import (
    AsyncInferenceServicesAPI,
    InferenceServicesAPI,
)
from foundrydb.client import AsyncHTTPClient, HTTPClient
from foundrydb.types import (
    FoundryDBError,
    InferenceConfig,
    InferenceFitCheckResult,
    InferenceModelAdapter,
    InferenceModelRate,
    InferenceService,
    InferenceServiceMetrics,
    InferenceServiceUsage,
    ServerlessInferenceModel,
)

BASE = "https://api.foundrydb.test"
SVC = "svc-001"
ADAPTER = "ada-001"

SERVICE_PAYLOAD = {
    "id": SVC,
    "user_id": "user-001",
    "organization_id": "org-001",
    "name": "my-llm",
    "service_kind": "inference",
    "status": "Running",
    "zone": "fi-hel2",
    "inference_sku": "dedicated",
    "plan_name": "gpu-l40s-1",
    "storage_size_gb": 200,
    "storage_tier": "maxiops",
    "node_count": 1,
    "inference_config": {
        "model_id": "mistral-small",
        "model_source": "curated",
        "served_model_name": "mistral-small",
        "hf_repo": "mistralai/Mistral-Small-3.2-24B-Instruct-2506",
        "dtype": "auto",
        "max_model_len": 32768,
        "gpu_memory_utilization": 0.9,
        "tensor_parallel_size": 1,
        "kv_cache_dtype": "fp8",
        "license_accepted": True,
        "enable_fine_tuned_serving": True,
        "max_loras": 2,
        "max_lora_rank": 16,
        "keep_warm_minutes": 30,
    },
    "tls_enabled": True,
    "created_at": "2026-08-01T00:00:00Z",
    "updated_at": "2026-08-01T01:00:00Z",
    "endpoint_hostname": "my-llm-a1b2c3.inf.foundrydb.com",
    "endpoint_base_url": "https://my-llm-a1b2c3.inf.foundrydb.com/v1",
    "provisioning_message": "downloading weights (42%)",
}

SERVERLESS_SERVICE_PAYLOAD = {
    "id": "svc-002",
    "user_id": "user-001",
    "name": "cheap-llm",
    "service_kind": "inference",
    "status": "Running",
    "zone": "",
    "inference_sku": "serverless",
    "plan_name": "",
    "node_count": 0,
    "tls_enabled": True,
    "created_at": "2026-08-02T00:00:00Z",
    "updated_at": "2026-08-02T00:00:00Z",
    "inference_config": {"model_id": "bge-m3", "model_source": "curated"},
}

USAGE_PAYLOAD = {
    "service_id": SVC,
    "from": "2026-08-01T00:00:00Z",
    "to": "2026-08-02T00:00:00Z",
    "bucket_seconds": 3600,
    "totals": {
        "calls": 120,
        "errors": 3,
        "input_tokens": 45000,
        "output_tokens": 12000,
        "total_tokens": 57000,
        "cost_microcents": 0,
        "images": 0,
        "avg_latency_ms": 240,
        "p95_latency_ms": 910,
        "error_rate": 0.025,
    },
    "series": [
        {
            "bucket_start": "2026-08-01T00:00:00Z",
            "calls": 60,
            "errors": 1,
            "input_tokens": 20000,
            "output_tokens": 5000,
            "total_tokens": 25000,
            "cost_microcents": 0,
            "images": 0,
            "avg_latency_ms": 210,
            "p95_latency_ms": 700,
        },
        {
            "bucket_start": "2026-08-01T01:00:00Z",
            "calls": 60,
            "errors": 2,
            "input_tokens": 25000,
            "output_tokens": 7000,
            "total_tokens": 32000,
            "cost_microcents": 0,
            "images": 0,
            "avg_latency_ms": 270,
            "p95_latency_ms": 940,
        },
    ],
    "gpu_hour": {
        "billed_hours": 24,
        "hourly_rate_eur": 1.85,
        "cost_eur": 44.4,
    },
    "month_to_date": {
        "from": "2026-08-01T00:00:00Z",
        "tokens": {
            "calls": 900,
            "errors": 10,
            "input_tokens": 300000,
            "output_tokens": 90000,
            "total_tokens": 390000,
            "cost_microcents": 0,
            "images": 0,
            "avg_latency_ms": 255,
            "p95_latency_ms": 880,
            "error_rate": 0.011,
        },
        "gpu_hour": {
            "billed_hours": 48,
            "hourly_rate_eur": 1.85,
            "cost_eur": 88.8,
        },
    },
}

METRICS_PAYLOAD = {
    "service_id": SVC,
    "from": "2026-08-01T00:00:00Z",
    "to": "2026-08-01T00:30:00Z",
    "snapshots": [
        {
            "collected_at": "2026-08-01T00:00:00Z",
            "model_name": "mistral-small",
            "server_reachable": False,
            "requests_running": 0,
            "requests_waiting": 0,
            "gpu_cache_usage_perc": 0,
            "generation_tokens_per_sec": 0,
            "prompt_tokens_per_sec": 0,
            "avg_ttft_ms": 0,
            "avg_tpot_ms": 0,
            "avg_e2e_latency_ms": 0,
            "requests_success_total": 0,
        },
        {
            "collected_at": "2026-08-01T00:15:00Z",
            "model_name": "mistral-small",
            "server_reachable": True,
            "requests_running": 4,
            "requests_waiting": 1,
            "gpu_cache_usage_perc": 0.42,
            "generation_tokens_per_sec": 310.5,
            "prompt_tokens_per_sec": 1200.25,
            "avg_ttft_ms": 85.5,
            "avg_tpot_ms": 12.25,
            "avg_e2e_latency_ms": 640.75,
            "requests_success_total": 1024,
            "gpus": [
                {
                    "index": 0,
                    "util_percent": 87.5,
                    "mem_used_mb": 40960,
                    "mem_total_mb": 46080,
                    "temp_c": 68,
                    "power_w": 295.5,
                }
            ],
        },
    ],
    "latest": {
        "collected_at": "2026-08-01T00:15:00Z",
        "model_name": "mistral-small",
        "server_reachable": True,
        "requests_running": 4,
        "requests_waiting": 1,
        "gpu_cache_usage_perc": 0.42,
        "generation_tokens_per_sec": 310.5,
        "prompt_tokens_per_sec": 1200.25,
        "avg_ttft_ms": 85.5,
        "avg_tpot_ms": 12.25,
        "avg_e2e_latency_ms": 640.75,
        "requests_success_total": 1024,
        "gpus": [
            {
                "index": 0,
                "util_percent": 87.5,
                "mem_used_mb": 40960,
                "mem_total_mb": 46080,
                "temp_c": 68,
                "power_w": 295.5,
            }
        ],
    },
}

FIT_REFUSAL_PAYLOAD = {
    "fits": False,
    "weights_gb": 65,
    "kv_cache_gb": 5.2,
    "overhead_gb": 1,
    "budget_gb": 21.6,
    "plan_vram_gb": 24,
    "max_context_that_fits": 0,
    "limiting_factor": "weights",
    "suggestions": [
        {
            "kind": "larger_plan",
            "detail": "Move to gpu-h100-1, the smallest plan whose budget holds these weights.",
            "plan_name": "gpu-h100-1",
            "tensor_parallel_size": 2,
        }
    ],
    "recommended_plan": "gpu-h100-1",
    "recommended_tensor_parallel_size": 2,
}

ADAPTER_PAYLOAD = {
    "id": ADAPTER,
    "organization_id": "org-001",
    "inference_service_id": SVC,
    "base_model_id": "mistral-small",
    "served_model_name": "support-bot",
    "version": 3,
    "files_bucket": "org-001-adapters",
    "files_key_prefix": "support-bot/v3/",
    "adapter_sha256": "a" * 64,
    "size_bytes": 134217728,
    "base_model_license": "apache-2.0",
    "status": "active",
    "created_at": "2026-08-01T00:00:00Z",
    "promoted_at": "2026-08-01T02:00:00Z",
    "deleted_at": None,
}

UPLOADED_ADAPTER_PAYLOAD = dict(
    ADAPTER_PAYLOAD,
    id="ada-002",
    inference_service_id=None,
    version=4,
    status="uploaded",
    promoted_at=None,
)

RATE_PAYLOAD = {
    "model_id": "mistral-small",
    "rate_unit": "tokens",
    "prompt_microcents_per_1k": 28000,
    "completion_microcents_per_1k": 85000,
    "effective_from": "2026-08-16T16:00:00Z",
}

IMAGE_RATE_PAYLOAD = {
    "model_id": "flux-schnell",
    "rate_unit": "image",
    "prompt_microcents_per_1k": 0,
    "completion_microcents_per_1k": 0,
    "image_microcents_per_unit": 1800000,
    "effective_from": "2026-08-16T16:00:00Z",
}

SERVERLESS_MODEL_PAYLOAD = {
    "model_id": "mistral-small",
    "display_name": "Mistral Small 3.2 24B",
    "capability": "chat",
    "serving": True,
    "deprecated": False,
}


def make_sync_api() -> InferenceServicesAPI:
    return InferenceServicesAPI(HTTPClient(BASE, "admin", "admin"))


def make_async_api() -> AsyncInferenceServicesAPI:
    return AsyncInferenceServicesAPI(AsyncHTTPClient(BASE, "admin", "admin"))


# ---------------------------------------------------------------------------
# Model tests (wire format decoding)
# ---------------------------------------------------------------------------

class TestInferenceService:
    def test_from_dict_dedicated(self):
        s = InferenceService.from_dict(SERVICE_PAYLOAD)
        assert s.id == SVC
        assert s.user_id == "user-001"
        assert s.organization_id == "org-001"
        assert s.name == "my-llm"
        assert s.service_kind == "inference"
        assert s.status == "Running"
        assert s.zone == "fi-hel2"
        assert s.inference_sku == "dedicated"
        assert s.plan_name == "gpu-l40s-1"
        assert s.storage_size_gb == 200
        assert s.storage_tier == "maxiops"
        assert s.node_count == 1
        assert s.tls_enabled is True
        assert s.endpoint_hostname == "my-llm-a1b2c3.inf.foundrydb.com"
        assert s.endpoint_base_url == "https://my-llm-a1b2c3.inf.foundrydb.com/v1"
        assert s.provisioning_message == "downloading weights (42%)"
        assert s.error_message == ""
        assert s.raw == SERVICE_PAYLOAD

    def test_from_dict_nested_inference_config(self):
        cfg = InferenceService.from_dict(SERVICE_PAYLOAD).inference_config
        assert cfg is not None
        assert cfg.model_id == "mistral-small"
        assert cfg.model_source == "curated"
        assert cfg.served_model_name == "mistral-small"
        assert cfg.max_model_len == 32768
        assert cfg.gpu_memory_utilization == 0.9
        assert cfg.tensor_parallel_size == 1
        assert cfg.kv_cache_dtype == "fp8"
        assert cfg.license_accepted is True
        assert cfg.enable_fine_tuned_serving is True
        assert cfg.max_loras == 2
        assert cfg.max_lora_rank == 16
        assert cfg.keep_warm_minutes == 30
        # The write-only token is never returned.
        assert cfg.hf_token == ""

    def test_from_dict_serverless_has_no_plan(self):
        s = InferenceService.from_dict(SERVERLESS_SERVICE_PAYLOAD)
        assert s.inference_sku == "serverless"
        assert s.plan_name == ""
        assert s.storage_size_gb is None
        assert s.endpoint_base_url == ""
        assert s.organization_id == ""

    def test_from_dict_no_inference_config(self):
        s = InferenceService.from_dict({"id": SVC, "name": "bare"})
        assert s.inference_config is None
        assert s.node_count == 0


class TestInferenceConfigToDict:
    def test_to_dict_omits_unset_fields(self):
        cfg = InferenceConfig(model_id="mistral-small")
        assert cfg.to_dict() == {
            "model_id": "mistral-small",
            "model_source": "curated",
        }

    def test_to_dict_sends_set_fields(self):
        cfg = InferenceConfig(
            model_id="meta-llama/Llama-3.3-70B-Instruct",
            model_source="huggingface",
            served_model_name="llama-70b",
            hf_token="hf_secret",
            max_model_len=8192,
            quantization="fp8",
            license_accepted=True,
            keep_warm_minutes=15,
        )
        assert cfg.to_dict() == {
            "model_id": "meta-llama/Llama-3.3-70B-Instruct",
            "model_source": "huggingface",
            "served_model_name": "llama-70b",
            "hf_token": "hf_secret",
            "max_model_len": 8192,
            "quantization": "fp8",
            "license_accepted": True,
            "keep_warm_minutes": 15,
        }


class TestInferenceServiceUsageDecoding:
    def test_from_dict_totals_and_series(self):
        u = InferenceServiceUsage.from_dict(USAGE_PAYLOAD)
        assert u.service_id == SVC
        assert u.from_ == "2026-08-01T00:00:00Z"
        assert u.to == "2026-08-02T00:00:00Z"
        assert u.bucket_seconds == 3600
        assert u.totals.calls == 120
        assert u.totals.errors == 3
        assert u.totals.total_tokens == 57000
        assert u.totals.cost_microcents == 0
        assert u.totals.images == 0
        assert u.totals.p95_latency_ms == 910
        assert u.totals.error_rate == 0.025
        assert len(u.series) == 2
        assert u.series[0].bucket_start == "2026-08-01T00:00:00Z"
        assert u.series[1].calls == 60
        assert u.series[1].p95_latency_ms == 940

    def test_from_dict_gpu_hour_and_month_to_date(self):
        u = InferenceServiceUsage.from_dict(USAGE_PAYLOAD)
        assert u.gpu_hour is not None
        assert u.gpu_hour.billed_hours == 24
        assert u.gpu_hour.hourly_rate_eur == 1.85
        assert u.gpu_hour.cost_eur == 44.4
        assert u.month_to_date is not None
        assert u.month_to_date.from_ == "2026-08-01T00:00:00Z"
        assert u.month_to_date.tokens.total_tokens == 390000
        assert u.month_to_date.gpu_hour is not None
        assert u.month_to_date.gpu_hour.cost_eur == 88.8

    def test_from_dict_serverless_has_no_gpu_hour(self):
        payload = {
            k: v
            for k, v in USAGE_PAYLOAD.items()
            if k not in ("gpu_hour", "month_to_date")
        }
        u = InferenceServiceUsage.from_dict(payload)
        assert u.gpu_hour is None
        assert u.month_to_date is None
        assert u.totals.calls == 120


class TestInferenceServiceMetricsDecoding:
    def test_from_dict_snapshots_and_latest(self):
        m = InferenceServiceMetrics.from_dict(METRICS_PAYLOAD)
        assert m.service_id == SVC
        assert m.from_ == "2026-08-01T00:00:00Z"
        assert m.to == "2026-08-01T00:30:00Z"
        assert len(m.snapshots) == 2
        first = m.snapshots[0]
        assert first.server_reachable is False
        assert first.gpus == []
        second = m.snapshots[1]
        assert second.server_reachable is True
        assert second.model_name == "mistral-small"
        assert second.requests_running == 4
        assert second.requests_waiting == 1
        assert second.gpu_cache_usage_perc == 0.42
        assert second.generation_tokens_per_sec == 310.5
        assert second.prompt_tokens_per_sec == 1200.25
        assert second.avg_ttft_ms == 85.5
        assert second.avg_tpot_ms == 12.25
        assert second.avg_e2e_latency_ms == 640.75
        assert second.requests_success_total == 1024
        assert m.latest is not None
        assert m.latest.collected_at == "2026-08-01T00:15:00Z"

    def test_from_dict_gpu_stats(self):
        m = InferenceServiceMetrics.from_dict(METRICS_PAYLOAD)
        gpus = m.snapshots[1].gpus
        assert len(gpus) == 1
        assert gpus[0].index == 0
        assert gpus[0].util_percent == 87.5
        assert gpus[0].mem_used_mb == 40960
        assert gpus[0].mem_total_mb == 46080
        assert gpus[0].temp_c == 68
        assert gpus[0].power_w == 295.5

    def test_from_dict_empty_window(self):
        m = InferenceServiceMetrics.from_dict(
            {"service_id": SVC, "from": "a", "to": "b", "snapshots": []}
        )
        assert m.snapshots == []
        assert m.latest is None


class TestInferenceFitCheckResultDecoding:
    def test_from_dict_refusal_with_suggestions(self):
        r = InferenceFitCheckResult.from_dict(FIT_REFUSAL_PAYLOAD)
        assert r.fits is False
        assert r.weights_gb == 65
        assert r.kv_cache_gb == 5.2
        assert r.overhead_gb == 1
        assert r.budget_gb == 21.6
        assert r.plan_vram_gb == 24
        assert r.max_context_that_fits == 0
        assert r.limiting_factor == "weights"
        assert len(r.suggestions) == 1
        assert r.suggestions[0].kind == "larger_plan"
        assert r.suggestions[0].plan_name == "gpu-h100-1"
        assert r.suggestions[0].tensor_parallel_size == 2
        assert r.recommended_plan == "gpu-h100-1"
        assert r.recommended_tensor_parallel_size == 2

    def test_from_dict_fits_has_no_suggestions(self):
        r = InferenceFitCheckResult.from_dict(
            {
                "fits": True,
                "weights_gb": 14.2,
                "kv_cache_gb": 3.1,
                "overhead_gb": 1,
                "budget_gb": 21.6,
                "plan_vram_gb": 24,
                "max_context_that_fits": 32768,
                "limiting_factor": "fits",
                "suggestions": [],
            }
        )
        assert r.fits is True
        assert r.limiting_factor == "fits"
        assert r.suggestions == []


class TestInferenceModelAdapterDecoding:
    def test_from_dict_active(self):
        a = InferenceModelAdapter.from_dict(ADAPTER_PAYLOAD)
        assert a.id == ADAPTER
        assert a.organization_id == "org-001"
        assert a.inference_service_id == SVC
        assert a.base_model_id == "mistral-small"
        assert a.served_model_name == "support-bot"
        assert a.version == 3
        assert a.files_bucket == "org-001-adapters"
        assert a.files_key_prefix == "support-bot/v3/"
        assert a.adapter_sha256 == "a" * 64
        assert a.size_bytes == 134217728
        assert a.base_model_license == "apache-2.0"
        assert a.status == "active"
        assert a.promoted_at == "2026-08-01T02:00:00Z"
        assert a.deleted_at is None

    def test_from_dict_uploaded_is_unbound(self):
        a = InferenceModelAdapter.from_dict(UPLOADED_ADAPTER_PAYLOAD)
        assert a.status == "uploaded"
        assert a.inference_service_id is None
        assert a.promoted_at is None


class TestInferenceModelRateDecoding:
    def test_from_dict_token_rate(self):
        r = InferenceModelRate.from_dict(RATE_PAYLOAD)
        assert r.model_id == "mistral-small"
        assert r.rate_unit == "tokens"
        assert r.prompt_microcents_per_1k == 28000
        assert r.completion_microcents_per_1k == 85000
        assert r.image_microcents_per_unit == 0
        assert r.effective_from == "2026-08-16T16:00:00Z"

    def test_from_dict_image_rate(self):
        r = InferenceModelRate.from_dict(IMAGE_RATE_PAYLOAD)
        assert r.rate_unit == "image"
        assert r.image_microcents_per_unit == 1800000
        assert r.prompt_microcents_per_1k == 0

    def test_from_dict_absent_rate_unit_reads_as_tokens(self):
        payload = {k: v for k, v in RATE_PAYLOAD.items() if k != "rate_unit"}
        assert InferenceModelRate.from_dict(payload).rate_unit == "tokens"


class TestServerlessInferenceModelDecoding:
    def test_from_dict(self):
        m = ServerlessInferenceModel.from_dict(SERVERLESS_MODEL_PAYLOAD)
        assert m.model_id == "mistral-small"
        assert m.display_name == "Mistral Small 3.2 24B"
        assert m.capability == "chat"
        assert m.serving is True
        assert m.deprecated is False


# ---------------------------------------------------------------------------
# Sync InferenceServicesAPI
# ---------------------------------------------------------------------------

class TestInferenceServicesAPISync:
    @respx.mock
    def test_list_returns_service_objects(self):
        respx.get(f"{BASE}/inference-services").mock(
            return_value=httpx.Response(
                200, json={"inference_services": [SERVICE_PAYLOAD]}
            )
        )
        services = make_sync_api().list()
        assert len(services) == 1
        assert isinstance(services[0], InferenceService)
        assert services[0].id == SVC

    @respx.mock
    def test_list_empty(self):
        respx.get(f"{BASE}/inference-services").mock(
            return_value=httpx.Response(200, json={"inference_services": []})
        )
        assert make_sync_api().list() == []

    @respx.mock
    def test_get_returns_service(self):
        respx.get(f"{BASE}/inference-services/{SVC}").mock(
            return_value=httpx.Response(200, json=SERVICE_PAYLOAD)
        )
        svc = make_sync_api().get(SVC)
        assert isinstance(svc, InferenceService)
        assert svc.endpoint_base_url.endswith("/v1")

    @respx.mock
    def test_get_404_returns_none(self):
        respx.get(f"{BASE}/inference-services/{SVC}").mock(
            return_value=httpx.Response(404, json={"error": "not found"})
        )
        assert make_sync_api().get(SVC) is None

    @respx.mock
    def test_get_other_error_raises(self):
        respx.get(f"{BASE}/inference-services/{SVC}").mock(
            return_value=httpx.Response(500, json={"error": "boom"})
        )
        with pytest.raises(FoundryDBError) as exc_info:
            make_sync_api().get(SVC)
        assert exc_info.value.status_code == 500

    @respx.mock
    def test_create_posts_dedicated_body(self):
        route = respx.post(f"{BASE}/inference-services").mock(
            return_value=httpx.Response(201, json=SERVICE_PAYLOAD)
        )
        svc = make_sync_api().create(
            name="my-llm",
            inference_config=InferenceConfig(
                model_id="mistral-small",
                model_source="curated",
                max_model_len=32768,
                license_accepted=True,
            ),
            plan_name="gpu-l40s-1",
            zone="fi-hel2",
        )
        assert isinstance(svc, InferenceService)
        assert route.calls.last.request.method == "POST"
        assert route.calls.last.request.url.path == "/inference-services"
        sent = json.loads(route.calls.last.request.content)
        assert sent == {
            "name": "my-llm",
            "inference_config": {
                "model_id": "mistral-small",
                "model_source": "curated",
                "max_model_len": 32768,
                "license_accepted": True,
            },
            "plan_name": "gpu-l40s-1",
            "zone": "fi-hel2",
        }

    @respx.mock
    def test_create_serverless_sends_sku_and_curated_model(self):
        route = respx.post(f"{BASE}/inference-services").mock(
            return_value=httpx.Response(201, json=SERVERLESS_SERVICE_PAYLOAD)
        )
        svc = make_sync_api().create_serverless(
            name="cheap-llm",
            model_id="bge-m3",
            organization_id="org-001",
            license_accepted=True,
        )
        assert svc.inference_sku == "serverless"
        sent = json.loads(route.calls.last.request.content)
        assert sent == {
            "name": "cheap-llm",
            "inference_config": {
                "model_id": "bge-m3",
                "model_source": "curated",
                "license_accepted": True,
            },
            "inference_sku": "serverless",
            "organization_id": "org-001",
        }
        assert "plan_name" not in sent

    @respx.mock
    def test_create_raises_on_unaccepted_license(self):
        respx.post(f"{BASE}/inference-services").mock(
            return_value=httpx.Response(400, json={"error": "license not accepted"})
        )
        with pytest.raises(FoundryDBError) as exc_info:
            make_sync_api().create(
                name="my-llm",
                inference_config=InferenceConfig(model_id="llama-3.3-70b"),
                plan_name="gpu-h100-1",
            )
        assert exc_info.value.status_code == 400

    @respx.mock
    def test_delete_succeeds(self):
        respx.delete(f"{BASE}/inference-services/{SVC}").mock(
            return_value=httpx.Response(204, content=b"")
        )
        assert make_sync_api().delete(SVC) is None

    @respx.mock
    def test_delete_404_is_idempotent(self):
        respx.delete(f"{BASE}/inference-services/{SVC}").mock(
            return_value=httpx.Response(404, json={"error": "not found"})
        )
        assert make_sync_api().delete(SVC) is None

    @respx.mock
    def test_list_model_rates(self):
        respx.get(f"{BASE}/inference-services/model-rates").mock(
            return_value=httpx.Response(
                200, json={"models": [RATE_PAYLOAD, IMAGE_RATE_PAYLOAD]}
            )
        )
        rates = make_sync_api().list_model_rates()
        assert len(rates) == 2
        assert isinstance(rates[0], InferenceModelRate)
        assert rates[1].rate_unit == "image"

    @respx.mock
    def test_list_serverless_models(self):
        respx.get(f"{BASE}/inference-services/serverless-models").mock(
            return_value=httpx.Response(
                200, json={"models": [SERVERLESS_MODEL_PAYLOAD]}
            )
        )
        models = make_sync_api().list_serverless_models()
        assert len(models) == 1
        assert isinstance(models[0], ServerlessInferenceModel)
        assert models[0].serving is True

    @respx.mock
    def test_list_serverless_models_empty_is_not_an_error(self):
        respx.get(f"{BASE}/inference-services/serverless-models").mock(
            return_value=httpx.Response(200, json={"models": []})
        )
        assert make_sync_api().list_serverless_models() == []

    @respx.mock
    def test_check_fit_posts_to_fit_check(self):
        route = respx.post(f"{BASE}/inference-services/fit-check").mock(
            return_value=httpx.Response(200, json=FIT_REFUSAL_PAYLOAD)
        )
        result = make_sync_api().check_fit(
            model_source="curated",
            model_id="llama-3.3-70b",
            plan_name="gpu-l4-1",
            max_model_len=32768,
            kv_cache_dtype="fp8",
        )
        assert isinstance(result, InferenceFitCheckResult)
        # A configuration that does not fit is still a successful call.
        assert result.fits is False
        assert route.calls.last.request.method == "POST"
        assert route.calls.last.request.url.path == "/inference-services/fit-check"
        sent = json.loads(route.calls.last.request.content)
        assert sent == {
            "model_source": "curated",
            "model_id": "llama-3.3-70b",
            "plan_name": "gpu-l4-1",
            "max_model_len": 32768,
            "kv_cache_dtype": "fp8",
        }

    @respx.mock
    def test_check_fit_omits_unset_knobs(self):
        route = respx.post(f"{BASE}/inference-services/fit-check").mock(
            return_value=httpx.Response(200, json=FIT_REFUSAL_PAYLOAD)
        )
        make_sync_api().check_fit(
            model_source="huggingface",
            model_id="meta-llama/Llama-3.3-70B-Instruct",
            plan_name="gpu-h100-1",
        )
        sent = json.loads(route.calls.last.request.content)
        assert sent == {
            "model_source": "huggingface",
            "model_id": "meta-llama/Llama-3.3-70B-Instruct",
            "plan_name": "gpu-h100-1",
        }

    @respx.mock
    def test_switch_model_posts_to_switch_model(self):
        switching = dict(SERVICE_PAYLOAD, status="SwitchingModel")
        route = respx.post(f"{BASE}/inference-services/{SVC}/switch-model").mock(
            return_value=httpx.Response(200, json=switching)
        )
        svc = make_sync_api().switch_model(
            SVC, model_id="qwen3-32b", license_accepted=True
        )
        assert svc.status == "SwitchingModel"
        assert route.calls.last.request.method == "POST"
        assert (
            route.calls.last.request.url.path
            == f"/inference-services/{SVC}/switch-model"
        )
        sent = json.loads(route.calls.last.request.content)
        assert sent == {"model_id": "qwen3-32b", "license_accepted": True}

    @respx.mock
    def test_switch_model_omits_unset_license(self):
        route = respx.post(f"{BASE}/inference-services/{SVC}/switch-model").mock(
            return_value=httpx.Response(200, json=SERVICE_PAYLOAD)
        )
        make_sync_api().switch_model(SVC, model_id="qwen3-32b")
        sent = json.loads(route.calls.last.request.content)
        assert sent == {"model_id": "qwen3-32b"}

    @respx.mock
    def test_get_usage_returns_usage(self):
        route = respx.get(f"{BASE}/inference-services/{SVC}/usage").mock(
            return_value=httpx.Response(200, json=USAGE_PAYLOAD)
        )
        usage = make_sync_api().get_usage(SVC, since="24h")
        assert isinstance(usage, InferenceServiceUsage)
        assert usage.totals.calls == 120
        assert route.calls.last.request.url.params["since"] == "24h"

    @respx.mock
    def test_get_usage_omits_since_when_empty(self):
        route = respx.get(f"{BASE}/inference-services/{SVC}/usage").mock(
            return_value=httpx.Response(200, json=USAGE_PAYLOAD)
        )
        make_sync_api().get_usage(SVC)
        assert "since" not in route.calls.last.request.url.params

    @respx.mock
    def test_get_usage_404_returns_none(self):
        respx.get(f"{BASE}/inference-services/{SVC}/usage").mock(
            return_value=httpx.Response(404, json={"error": "not found"})
        )
        assert make_sync_api().get_usage(SVC) is None

    @respx.mock
    def test_get_metrics_returns_metrics(self):
        route = respx.get(f"{BASE}/inference-services/{SVC}/metrics").mock(
            return_value=httpx.Response(200, json=METRICS_PAYLOAD)
        )
        metrics = make_sync_api().get_metrics(SVC, since="30m")
        assert isinstance(metrics, InferenceServiceMetrics)
        assert len(metrics.snapshots) == 2
        assert metrics.latest is not None
        assert route.calls.last.request.url.params["since"] == "30m"

    @respx.mock
    def test_get_metrics_404_returns_none(self):
        respx.get(f"{BASE}/inference-services/{SVC}/metrics").mock(
            return_value=httpx.Response(404, json={"error": "not found"})
        )
        assert make_sync_api().get_metrics(SVC) is None

    @respx.mock
    def test_list_adapters_returns_adapters(self):
        respx.get(f"{BASE}/inference-services/{SVC}/adapters").mock(
            return_value=httpx.Response(
                200,
                json={"adapters": [ADAPTER_PAYLOAD, UPLOADED_ADAPTER_PAYLOAD]},
            )
        )
        adapters = make_sync_api().list_adapters(SVC)
        assert adapters is not None
        assert len(adapters) == 2
        assert isinstance(adapters[0], InferenceModelAdapter)
        assert adapters[1].status == "uploaded"

    @respx.mock
    def test_list_adapters_404_returns_none(self):
        respx.get(f"{BASE}/inference-services/{SVC}/adapters").mock(
            return_value=httpx.Response(404, json={"error": "not found"})
        )
        assert make_sync_api().list_adapters(SVC) is None

    @respx.mock
    def test_promote_adapter_unwraps_envelope(self):
        route = respx.post(
            f"{BASE}/inference-services/{SVC}/adapters/{ADAPTER}/promote"
        ).mock(return_value=httpx.Response(200, json={"adapter": ADAPTER_PAYLOAD}))
        adapter = make_sync_api().promote_adapter(SVC, ADAPTER)
        assert isinstance(adapter, InferenceModelAdapter)
        assert adapter.status == "active"
        assert route.calls.last.request.method == "POST"
        # Promote carries no body.
        assert route.calls.last.request.content == b""

    @respx.mock
    def test_demote_adapter_unwraps_envelope(self):
        superseded = dict(ADAPTER_PAYLOAD, status="superseded")
        route = respx.post(
            f"{BASE}/inference-services/{SVC}/adapters/{ADAPTER}/demote"
        ).mock(return_value=httpx.Response(200, json={"adapter": superseded}))
        adapter = make_sync_api().demote_adapter(SVC, ADAPTER)
        assert adapter.status == "superseded"
        assert (
            route.calls.last.request.url.path
            == f"/inference-services/{SVC}/adapters/{ADAPTER}/demote"
        )

    @respx.mock
    def test_delete_adapter_hits_collection_root(self):
        route = respx.delete(f"{BASE}/inference-services/adapters/{ADAPTER}").mock(
            return_value=httpx.Response(204, content=b"")
        )
        assert make_sync_api().delete_adapter(ADAPTER) is None
        assert route.called

    @respx.mock
    def test_delete_adapter_raises_when_actively_served(self):
        respx.delete(f"{BASE}/inference-services/adapters/{ADAPTER}").mock(
            return_value=httpx.Response(409, json={"error": "adapter is active"})
        )
        with pytest.raises(FoundryDBError) as exc_info:
            make_sync_api().delete_adapter(ADAPTER)
        assert exc_info.value.status_code == 409

    @respx.mock
    def test_register_adapter_posts_body(self):
        route = respx.post(f"{BASE}/inference-services/adapters").mock(
            return_value=httpx.Response(
                201, json={"adapter": UPLOADED_ADAPTER_PAYLOAD}
            )
        )
        adapter = make_sync_api().register_adapter(
            base_model_id="mistral-small",
            served_model_name="support-bot",
            version=4,
            files_bucket="org-001-adapters",
            files_key_prefix="support-bot/v4/",
            adapter_sha256="b" * 64,
            size_bytes=134217728,
            base_model_license="apache-2.0",
        )
        assert adapter.status == "uploaded"
        assert adapter.inference_service_id is None
        sent = json.loads(route.calls.last.request.content)
        assert sent == {
            "base_model_id": "mistral-small",
            "served_model_name": "support-bot",
            "version": 4,
            "files_bucket": "org-001-adapters",
            "files_key_prefix": "support-bot/v4/",
            "adapter_sha256": "b" * 64,
            "size_bytes": 134217728,
            "base_model_license": "apache-2.0",
        }


# ---------------------------------------------------------------------------
# Async AsyncInferenceServicesAPI
# ---------------------------------------------------------------------------

class TestAsyncInferenceServicesAPI:
    @respx.mock
    @pytest.mark.asyncio
    async def test_list_returns_service_objects(self):
        respx.get(f"{BASE}/inference-services").mock(
            return_value=httpx.Response(
                200, json={"inference_services": [SERVICE_PAYLOAD]}
            )
        )
        api = make_async_api()
        services = await api.list()
        assert len(services) == 1
        assert services[0].id == SVC
        await api._http.aclose()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_404_returns_none(self):
        respx.get(f"{BASE}/inference-services/{SVC}").mock(
            return_value=httpx.Response(404, json={"error": "not found"})
        )
        api = make_async_api()
        assert await api.get(SVC) is None
        await api._http.aclose()

    @respx.mock
    @pytest.mark.asyncio
    async def test_create_posts_body(self):
        route = respx.post(f"{BASE}/inference-services").mock(
            return_value=httpx.Response(201, json=SERVICE_PAYLOAD)
        )
        api = make_async_api()
        svc = await api.create(
            name="my-llm",
            inference_config=InferenceConfig(model_id="mistral-small"),
            plan_name="gpu-l40s-1",
        )
        assert isinstance(svc, InferenceService)
        assert route.calls.last.request.method == "POST"
        sent = json.loads(route.calls.last.request.content)
        assert sent == {
            "name": "my-llm",
            "inference_config": {
                "model_id": "mistral-small",
                "model_source": "curated",
            },
            "plan_name": "gpu-l40s-1",
        }
        await api._http.aclose()

    @respx.mock
    @pytest.mark.asyncio
    async def test_create_serverless_sends_sku(self):
        route = respx.post(f"{BASE}/inference-services").mock(
            return_value=httpx.Response(201, json=SERVERLESS_SERVICE_PAYLOAD)
        )
        api = make_async_api()
        svc = await api.create_serverless(name="cheap-llm", model_id="bge-m3")
        assert svc.inference_sku == "serverless"
        sent = json.loads(route.calls.last.request.content)
        assert sent["inference_sku"] == "serverless"
        assert "plan_name" not in sent
        await api._http.aclose()

    @respx.mock
    @pytest.mark.asyncio
    async def test_delete_404_is_idempotent(self):
        respx.delete(f"{BASE}/inference-services/{SVC}").mock(
            return_value=httpx.Response(404, json={"error": "not found"})
        )
        api = make_async_api()
        assert await api.delete(SVC) is None
        await api._http.aclose()

    @respx.mock
    @pytest.mark.asyncio
    async def test_check_fit_posts_to_fit_check(self):
        route = respx.post(f"{BASE}/inference-services/fit-check").mock(
            return_value=httpx.Response(200, json=FIT_REFUSAL_PAYLOAD)
        )
        api = make_async_api()
        result = await api.check_fit(
            model_source="curated", model_id="llama-3.3-70b", plan_name="gpu-l4-1"
        )
        assert result.fits is False
        assert result.recommended_plan == "gpu-h100-1"
        assert route.calls.last.request.url.path == "/inference-services/fit-check"
        await api._http.aclose()

    @respx.mock
    @pytest.mark.asyncio
    async def test_switch_model_posts_body(self):
        route = respx.post(f"{BASE}/inference-services/{SVC}/switch-model").mock(
            return_value=httpx.Response(
                200, json=dict(SERVICE_PAYLOAD, status="SwitchingModel")
            )
        )
        api = make_async_api()
        svc = await api.switch_model(SVC, model_id="qwen3-32b")
        assert svc.status == "SwitchingModel"
        sent = json.loads(route.calls.last.request.content)
        assert sent == {"model_id": "qwen3-32b"}
        await api._http.aclose()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_usage_returns_usage(self):
        respx.get(f"{BASE}/inference-services/{SVC}/usage").mock(
            return_value=httpx.Response(200, json=USAGE_PAYLOAD)
        )
        api = make_async_api()
        usage = await api.get_usage(SVC, since="1h")
        assert usage is not None
        assert usage.month_to_date is not None
        assert usage.month_to_date.gpu_hour is not None
        await api._http.aclose()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_metrics_404_returns_none(self):
        respx.get(f"{BASE}/inference-services/{SVC}/metrics").mock(
            return_value=httpx.Response(404, json={"error": "not found"})
        )
        api = make_async_api()
        assert await api.get_metrics(SVC) is None
        await api._http.aclose()

    @respx.mock
    @pytest.mark.asyncio
    async def test_adapter_promote_and_demote(self):
        respx.post(
            f"{BASE}/inference-services/{SVC}/adapters/{ADAPTER}/promote"
        ).mock(return_value=httpx.Response(200, json={"adapter": ADAPTER_PAYLOAD}))
        respx.post(
            f"{BASE}/inference-services/{SVC}/adapters/{ADAPTER}/demote"
        ).mock(
            return_value=httpx.Response(
                200, json={"adapter": dict(ADAPTER_PAYLOAD, status="superseded")}
            )
        )
        api = make_async_api()
        promoted = await api.promote_adapter(SVC, ADAPTER)
        demoted = await api.demote_adapter(SVC, ADAPTER)
        assert promoted.status == "active"
        assert demoted.status == "superseded"
        await api._http.aclose()

    @respx.mock
    @pytest.mark.asyncio
    async def test_register_adapter_posts_body(self):
        route = respx.post(f"{BASE}/inference-services/adapters").mock(
            return_value=httpx.Response(
                201, json={"adapter": UPLOADED_ADAPTER_PAYLOAD}
            )
        )
        api = make_async_api()
        adapter = await api.register_adapter(
            base_model_id="mistral-small",
            served_model_name="support-bot",
            version=4,
            files_bucket="org-001-adapters",
            files_key_prefix="support-bot/v4/",
            adapter_sha256="b" * 64,
            size_bytes=1024,
            organization_id="org-001",
        )
        assert adapter.status == "uploaded"
        sent = json.loads(route.calls.last.request.content)
        assert sent["organization_id"] == "org-001"
        assert "base_model_license" not in sent
        await api._http.aclose()

    @respx.mock
    @pytest.mark.asyncio
    async def test_list_serverless_models(self):
        respx.get(f"{BASE}/inference-services/serverless-models").mock(
            return_value=httpx.Response(
                200, json={"models": [SERVERLESS_MODEL_PAYLOAD]}
            )
        )
        api = make_async_api()
        models = await api.list_serverless_models()
        assert models[0].capability == "chat"
        await api._http.aclose()

    @respx.mock
    @pytest.mark.asyncio
    async def test_list_model_rates(self):
        respx.get(f"{BASE}/inference-services/model-rates").mock(
            return_value=httpx.Response(200, json={"models": [RATE_PAYLOAD]})
        )
        api = make_async_api()
        rates = await api.list_model_rates()
        assert rates[0].prompt_microcents_per_1k == 28000
        await api._http.aclose()
