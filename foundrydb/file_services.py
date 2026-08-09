"""
FoundryDB SDK - File Services API (sync and async).

File services are managed S3-compatible object storage buckets with scoped
access keys, presigned URLs, and quota enforcement. Provisioning is
asynchronous: a new service starts in Pending and reaches Running once the
bucket is ready.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from .client import HTTPClient, AsyncHTTPClient
from .types import (
    FilesService,
    FilesAccessKey,
    FilesAccessKeyWithSecret,
    FilesKeyPolicy,
    FilesPresignedURL,
    FilesObjectPage,
    FilesUsage,
)


def _files_usage_params(
    range_: str, granularity: str, live: bool
) -> Optional[Dict[str, Any]]:
    """Build the query params for a files usage request."""
    params: Dict[str, Any] = {}
    if range_:
        params["range"] = range_
    if granularity:
        params["granularity"] = granularity
    if live:
        params["live"] = "true"
    return params or None


def _files_access_key_body(
    name: str,
    permissions: Optional[str],
    prefix: str,
    policy: Optional[Union["FilesKeyPolicy", Dict[str, Any]]],
) -> Dict[str, Any]:
    """Build the create-access-key request body. Scope the key with either the
    prefix + permissions shorthand or a custom policy (mutually exclusive)."""
    if policy is not None:
        pol = policy.to_dict() if isinstance(policy, FilesKeyPolicy) else policy
        return {"name": name, "policy": pol}
    body: Dict[str, Any] = {"name": name}
    if permissions is not None:
        body["permissions"] = permissions
    if prefix:
        body["prefix"] = prefix
    return body


class FileServicesAPI:
    """Manages file services (object storage) (sync)."""

    def __init__(self, http: HTTPClient) -> None:
        self._http = http

    # ------------------------------------------------------------------
    # Service lifecycle
    # ------------------------------------------------------------------

    def list(self) -> List[FilesService]:
        """Return all file services visible to the authenticated user."""
        data = self._http.get("/file-services")
        return [FilesService.from_dict(s) for s in data.get("file_services", [])]

    def get(self, service_id: str) -> Optional[FilesService]:
        """Return a file service by ID, or ``None`` when not found."""
        try:
            data = self._http.get(f"/file-services/{service_id}")
        except Exception as exc:
            from .types import FoundryDBError
            if isinstance(exc, FoundryDBError) and exc.status_code == 404:
                return None
            raise
        return FilesService.from_dict(data)

    def get_usage(
        self,
        service_id: str,
        *,
        range: str = "",
        granularity: str = "",
        live: bool = False,
    ) -> FilesUsage:
        """Return storage-usage monitoring for a files service.

        Args:
            service_id: ID of the file service.
            range: History window, e.g. ``"30d"`` or ``"24h"`` (default 30d).
            granularity: ``"hour"`` or ``"day"``; empty auto-selects by window.
            live: Read the current footprint on demand from the provider
                instead of the last metering tick.
        """
        params = _files_usage_params(range, granularity, live)
        data = self._http.get(f"/file-services/{service_id}/usage", params=params)
        return FilesUsage.from_dict(data)

    def create(
        self,
        *,
        name: str,
        zone: str = "",
        quota_gb_soft: Optional[int] = None,
        quota_gb_hard: Optional[int] = None,
        organization_id: Optional[str] = None,
    ) -> FilesService:
        """Provision a new file service.

        The service is created in the Pending status and reaches Running once
        the bucket is provisioned.

        Args:
            name: Display name for the service.
            zone: Provider region for the bucket. Empty uses the platform
                default.
            quota_gb_soft: Stored-GB threshold that triggers a notification.
            quota_gb_hard: Stored-GB ceiling; uploads are blocked once
                exceeded.
            organization_id: Assign the service to an organization.
        """
        body: Dict[str, Any] = {"name": name}
        if zone:
            body["zone"] = zone
        if quota_gb_soft is not None:
            body["quota_gb_soft"] = quota_gb_soft
        if quota_gb_hard is not None:
            body["quota_gb_hard"] = quota_gb_hard
        if organization_id:
            body["organization_id"] = organization_id
        data = self._http.post("/file-services", body)
        return FilesService.from_dict(data)

    def delete(self, service_id: str) -> None:
        """Delete a file service and all its bucket contents.

        Idempotent: a 404 response is treated as success.
        """
        try:
            self._http.delete(f"/file-services/{service_id}")
        except Exception as exc:
            from .types import FoundryDBError
            if isinstance(exc, FoundryDBError) and exc.status_code == 404:
                return
            raise

    # ------------------------------------------------------------------
    # Access keys
    # ------------------------------------------------------------------

    def create_access_key(
        self,
        service_id: str,
        *,
        name: str,
        permissions: Optional[str] = None,
        prefix: str = "",
        policy: Optional[Union[FilesKeyPolicy, Dict[str, Any]]] = None,
    ) -> FilesAccessKeyWithSecret:
        """Mint a new scoped S3 credential.

        The secret access key is returned exactly once in this response;
        store it immediately. Key creation is blocked while the service is
        over its hard storage quota.

        Scope the key with either the ``permissions`` (+ optional ``prefix``)
        shorthand or a custom ``policy``; the two are mutually exclusive.

        Args:
            service_id: ID of the file service.
            name: Human-readable label for the key.
            permissions: ``"read"``, ``"write"``, or ``"readwrite"``. Required
                unless ``policy`` is given.
            prefix: Object key prefix the credential is scoped to. Empty
                grants the whole bucket. Ignored when ``policy`` is given.
            policy: A :class:`FilesKeyPolicy` (or an equivalent dict) of
                custom statements. Mutually exclusive with permissions/prefix.
        """
        body = _files_access_key_body(name, permissions, prefix, policy)
        data = self._http.post(f"/file-services/{service_id}/keys", body)
        return FilesAccessKeyWithSecret.from_dict(data)

    def list_access_keys(self, service_id: str) -> List[FilesAccessKey]:
        """Return the service's access keys (no secret halves)."""
        data = self._http.get(f"/file-services/{service_id}/keys")
        return [FilesAccessKey.from_dict(k) for k in data.get("keys", [])]

    def revoke_access_key(self, service_id: str, key_id: str) -> None:
        """Revoke one access key. Revocation is permanent and immediate."""
        self._http.delete(f"/file-services/{service_id}/keys/{key_id}")

    # ------------------------------------------------------------------
    # Presigned URLs
    # ------------------------------------------------------------------

    def presign(
        self,
        service_id: str,
        *,
        method: str,
        key: str,
        expires_seconds: int = 0,
        content_type: str = "",
    ) -> FilesPresignedURL:
        """Presign one S3 operation and return the URL.

        The URL is used directly against the bucket endpoint without further
        credentials, until it expires. Upload (PUT) presigning is blocked
        while the service is over its hard storage quota.

        Args:
            service_id: ID of the file service.
            method: HTTP method to presign: ``GET``, ``PUT``, ``HEAD``, or
                ``DELETE`` (uppercase).
            key: Object key the URL operates on.
            expires_seconds: URL lifetime; 0 applies the platform default
                (15 minutes), maximum is 604800 (7 days).
            content_type: When set on a PUT, signed into the URL so the
                upload must send the same Content-Type header.
        """
        body: Dict[str, Any] = {"method": method, "key": key}
        if expires_seconds > 0:
            body["expires_seconds"] = expires_seconds
        if content_type:
            body["content_type"] = content_type
        data = self._http.post(f"/file-services/{service_id}/presign", body)
        return FilesPresignedURL.from_dict(data)

    # ------------------------------------------------------------------
    # Object listing
    # ------------------------------------------------------------------

    def list_objects(
        self,
        service_id: str,
        *,
        prefix: str = "",
        cursor: str = "",
        max: int = 0,
        delimiter: str = "",
    ) -> FilesObjectPage:
        """Return one page of the bucket's objects.

        Args:
            service_id: ID of the file service.
            prefix: Filter to objects whose key starts with this prefix.
            cursor: ``next_cursor`` from a previous page to continue listing.
            max: Page size cap (0 applies the server default of 100, maximum
                is 1000).
        """
        params: Dict[str, Any] = {}
        if prefix:
            params["prefix"] = prefix
        if cursor:
            params["cursor"] = cursor
        if max > 0:
            params["max"] = max
        if delimiter:
            params["delimiter"] = delimiter
        data = self._http.get(
            f"/file-services/{service_id}/objects",
            params=params or None,
        )
        return FilesObjectPage.from_dict(data)

    def delete_object(self, service_id: str, key: str) -> None:
        """Remove one object from the service's bucket."""
        self._http.delete(f"/file-services/{service_id}/objects?key={key}")


class AsyncFileServicesAPI:
    """Manages file services (object storage) (async)."""

    def __init__(self, http: AsyncHTTPClient) -> None:
        self._http = http

    async def list(self) -> List[FilesService]:
        """Return all file services visible to the authenticated user."""
        data = await self._http.get("/file-services")
        return [FilesService.from_dict(s) for s in data.get("file_services", [])]

    async def get(self, service_id: str) -> Optional[FilesService]:
        """Return a file service by ID, or ``None`` when not found."""
        try:
            data = await self._http.get(f"/file-services/{service_id}")
        except Exception as exc:
            from .types import FoundryDBError
            if isinstance(exc, FoundryDBError) and exc.status_code == 404:
                return None
            raise
        return FilesService.from_dict(data)

    async def get_usage(
        self,
        service_id: str,
        *,
        range: str = "",
        granularity: str = "",
        live: bool = False,
    ) -> FilesUsage:
        """Return storage-usage monitoring for a files service (current
        footprint, live reading, and a storage-over-time series)."""
        params = _files_usage_params(range, granularity, live)
        data = await self._http.get(f"/file-services/{service_id}/usage", params=params)
        return FilesUsage.from_dict(data)

    async def create(
        self,
        *,
        name: str,
        zone: str = "",
        quota_gb_soft: Optional[int] = None,
        quota_gb_hard: Optional[int] = None,
        organization_id: Optional[str] = None,
    ) -> FilesService:
        """Provision a new file service."""
        body: Dict[str, Any] = {"name": name}
        if zone:
            body["zone"] = zone
        if quota_gb_soft is not None:
            body["quota_gb_soft"] = quota_gb_soft
        if quota_gb_hard is not None:
            body["quota_gb_hard"] = quota_gb_hard
        if organization_id:
            body["organization_id"] = organization_id
        data = await self._http.post("/file-services", body)
        return FilesService.from_dict(data)

    async def delete(self, service_id: str) -> None:
        """Delete a file service and all its bucket contents (idempotent)."""
        try:
            await self._http.delete(f"/file-services/{service_id}")
        except Exception as exc:
            from .types import FoundryDBError
            if isinstance(exc, FoundryDBError) and exc.status_code == 404:
                return
            raise

    async def create_access_key(
        self,
        service_id: str,
        *,
        name: str,
        permissions: Optional[str] = None,
        prefix: str = "",
        policy: Optional[Union[FilesKeyPolicy, Dict[str, Any]]] = None,
    ) -> FilesAccessKeyWithSecret:
        """Mint a new scoped S3 credential.

        Scope the key with either the ``permissions`` (+ optional ``prefix``)
        shorthand or a custom ``policy``; the two are mutually exclusive.
        """
        body = _files_access_key_body(name, permissions, prefix, policy)
        data = await self._http.post(f"/file-services/{service_id}/keys", body)
        return FilesAccessKeyWithSecret.from_dict(data)

    async def list_access_keys(self, service_id: str) -> List[FilesAccessKey]:
        """Return the service's access keys (no secret halves)."""
        data = await self._http.get(f"/file-services/{service_id}/keys")
        return [FilesAccessKey.from_dict(k) for k in data.get("keys", [])]

    async def revoke_access_key(self, service_id: str, key_id: str) -> None:
        """Revoke one access key."""
        await self._http.delete(f"/file-services/{service_id}/keys/{key_id}")

    async def presign(
        self,
        service_id: str,
        *,
        method: str,
        key: str,
        expires_seconds: int = 0,
        content_type: str = "",
    ) -> FilesPresignedURL:
        """Presign one S3 operation and return the URL."""
        body: Dict[str, Any] = {"method": method, "key": key}
        if expires_seconds > 0:
            body["expires_seconds"] = expires_seconds
        if content_type:
            body["content_type"] = content_type
        data = await self._http.post(f"/file-services/{service_id}/presign", body)
        return FilesPresignedURL.from_dict(data)

    async def list_objects(
        self,
        service_id: str,
        *,
        prefix: str = "",
        cursor: str = "",
        max: int = 0,
        delimiter: str = "",
    ) -> FilesObjectPage:
        """Return one page of the bucket's objects."""
        params: Dict[str, Any] = {}
        if prefix:
            params["prefix"] = prefix
        if cursor:
            params["cursor"] = cursor
        if max > 0:
            params["max"] = max
        if delimiter:
            params["delimiter"] = delimiter
        data = await self._http.get(
            f"/file-services/{service_id}/objects",
            params=params or None,
        )
        return FilesObjectPage.from_dict(data)

    async def delete_object(self, service_id: str, key: str) -> None:
        """Remove one object from the service's bucket."""
        await self._http.delete(f"/file-services/{service_id}/objects?key={key}")
