"""
Tests for foundrydb.inference - InferenceAPI (sync) and AsyncInferenceAPI
(async): data-plane keys, the provider chain and its per-surface overrides,
and the usage summary with its free-tier standing.
"""
from __future__ import annotations

import json

import httpx
import pytest
import respx

from foundrydb.inference import AsyncInferenceAPI, InferenceAPI
from foundrydb.client import AsyncHTTPClient, HTTPClient
from foundrydb.types import (
    CreateInferenceKeyResult,
    InferenceChainOverride,
    InferenceKey,
    InferenceProviderChainInfo,
    InferenceUsageSummary,
)

BASE = "https://api.foundrydb.test"
ORG = "org-001"
SVC = "svc-001"

KEY_PAYLOAD = {
    "id": "key-001",
    "name": "checkout-service",
    "key_prefix": "fdb-inf-3f4a",
    "monthly_token_limit": 1000000,
    "rate_limit_rpm": 60,
    "status": "active",
    "tokens_used_cycle": 12345,
    "cycle_month": "2026-08-01T00:00:00Z",
    "service_id": SVC,
    "created_at": "2026-08-01T00:00:00Z",
    "revoked_at": None,
}

ORG_SCOPED_KEY_PAYLOAD = dict(KEY_PAYLOAD, id="key-002", service_id=None)

CREATE_KEY_PAYLOAD = {
    "key": KEY_PAYLOAD,
    "secret": "fdb-inf-3f4a-supersecret",
    "activation_note": (
        "The key activates at the inference endpoint within a few seconds, "
        "once the edge fleet applies it. A request sent immediately after "
        "minting can answer invalid_key; retry shortly."
    ),
}

USAGE_PAYLOAD = {
    "from": "2026-08-01T00:00:00Z",
    "to": "2026-08-18T00:00:00Z",
    "group_by": "model",
    "rows": [
        {
            "group_key": "mistral-small",
            "provider": "foundrydb_managed",
            "calls": 400,
            "input_tokens": 120000,
            "output_tokens": 40000,
            "total_tokens": 160000,
            "cost_microcents": 0,
        }
    ],
    "free_tier": {
        "cycle_month": "2026-08-01T00:00:00Z",
        "monthly_tokens": 1000000,
        "tokens_used": 160000,
        "tokens_remaining": 840000,
    },
}

CHAIN_PAYLOAD = {
    "provider_chain": ["foundrydb_managed", "openai", "none"],
    "fully_eu_resident": False,
    "overrides": [
        {
            "organization_id": ORG,
            "surface": "chat",
            "provider_chain": ["foundrydb_managed"],
            "created_at": "2026-08-01T00:00:00Z",
            "updated_at": "2026-08-01T00:00:00Z",
        }
    ],
}

OVERRIDE_PAYLOAD = {
    "organization_id": ORG,
    "surface": "embedding",
    "provider_chain": ["foundrydb_managed", "none"],
    "created_at": "2026-08-01T00:00:00Z",
    "updated_at": "2026-08-01T00:00:00Z",
}


def make_sync_api() -> InferenceAPI:
    return InferenceAPI(HTTPClient(BASE, "admin", "admin"))


def make_async_api() -> AsyncInferenceAPI:
    return AsyncInferenceAPI(AsyncHTTPClient(BASE, "admin", "admin"))


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------

class TestInferenceKey:
    def test_from_dict_service_scoped(self):
        k = InferenceKey.from_dict(KEY_PAYLOAD)
        assert k.id == "key-001"
        assert k.key_prefix == "fdb-inf-3f4a"
        assert k.monthly_token_limit == 1000000
        assert k.rate_limit_rpm == 60
        assert k.status == "active"
        assert k.tokens_used_cycle == 12345
        assert k.service_id == SVC
        assert k.revoked_at is None

    def test_from_dict_org_scoped_has_no_service_id(self):
        k = InferenceKey.from_dict(ORG_SCOPED_KEY_PAYLOAD)
        assert k.service_id is None


class TestCreateInferenceKeyResult:
    def test_from_dict_carries_activation_note(self):
        r = CreateInferenceKeyResult.from_dict(CREATE_KEY_PAYLOAD)
        assert isinstance(r.key, InferenceKey)
        assert r.key.service_id == SVC
        assert r.secret == "fdb-inf-3f4a-supersecret"
        assert "invalid_key" in r.activation_note

    def test_from_dict_absent_activation_note(self):
        r = CreateInferenceKeyResult.from_dict(
            {"key": KEY_PAYLOAD, "secret": "abc"}
        )
        assert r.activation_note == ""


class TestInferenceUsageSummaryFreeTier:
    def test_from_dict_with_free_tier(self):
        s = InferenceUsageSummary.from_dict(USAGE_PAYLOAD)
        assert s.group_by == "model"
        assert len(s.rows) == 1
        assert s.rows[0].total_tokens == 160000
        assert s.free_tier is not None
        assert s.free_tier.cycle_month == "2026-08-01T00:00:00Z"
        assert s.free_tier.monthly_tokens == 1000000
        assert s.free_tier.tokens_used == 160000
        assert s.free_tier.tokens_remaining == 840000

    def test_from_dict_without_free_tier(self):
        payload = {k: v for k, v in USAGE_PAYLOAD.items() if k != "free_tier"}
        s = InferenceUsageSummary.from_dict(payload)
        assert s.free_tier is None
        assert len(s.rows) == 1


class TestInferenceProviderChainInfo:
    def test_from_dict(self):
        info = InferenceProviderChainInfo.from_dict(CHAIN_PAYLOAD)
        assert info.provider_chain == ["foundrydb_managed", "openai", "none"]
        assert info.fully_eu_resident is False
        assert len(info.overrides) == 1
        assert isinstance(info.overrides[0], InferenceChainOverride)
        assert info.overrides[0].surface == "chat"
        assert info.overrides[0].provider_chain == ["foundrydb_managed"]

    def test_from_dict_empty_chain(self):
        info = InferenceProviderChainInfo.from_dict({})
        assert info.provider_chain == []
        assert info.fully_eu_resident is False
        assert info.overrides == []


# ---------------------------------------------------------------------------
# Sync InferenceAPI
# ---------------------------------------------------------------------------

class TestInferenceAPISync:
    @respx.mock
    def test_create_key_sends_service_id(self):
        route = respx.post(f"{BASE}/organizations/{ORG}/inference/keys").mock(
            return_value=httpx.Response(201, json=CREATE_KEY_PAYLOAD)
        )
        result = make_sync_api().create_key(
            ORG,
            name="checkout-service",
            monthly_token_limit=1000000,
            rate_limit_rpm=60,
            service_id=SVC,
        )
        assert isinstance(result, CreateInferenceKeyResult)
        assert result.activation_note != ""
        sent = json.loads(route.calls.last.request.content)
        assert sent == {
            "name": "checkout-service",
            "monthly_token_limit": 1000000,
            "rate_limit_rpm": 60,
            "service_id": SVC,
        }

    @respx.mock
    def test_create_key_omits_service_id_when_org_scoped(self):
        route = respx.post(f"{BASE}/organizations/{ORG}/inference/keys").mock(
            return_value=httpx.Response(
                201, json={"key": ORG_SCOPED_KEY_PAYLOAD, "secret": "abc"}
            )
        )
        result = make_sync_api().create_key(
            ORG, name="any-service", monthly_token_limit=500
        )
        assert result.key.service_id is None
        sent = json.loads(route.calls.last.request.content)
        assert sent == {"name": "any-service", "monthly_token_limit": 500}

    @respx.mock
    def test_get_provider_chain(self):
        route = respx.get(f"{BASE}/organizations/{ORG}/inference/chain").mock(
            return_value=httpx.Response(200, json=CHAIN_PAYLOAD)
        )
        info = make_sync_api().get_provider_chain(ORG)
        assert isinstance(info, InferenceProviderChainInfo)
        assert info.provider_chain[0] == "foundrydb_managed"
        assert route.calls.last.request.method == "GET"

    @respx.mock
    def test_set_provider_chain_puts_chain(self):
        route = respx.put(f"{BASE}/organizations/{ORG}/inference/chain").mock(
            return_value=httpx.Response(200, json=CHAIN_PAYLOAD)
        )
        info = make_sync_api().set_provider_chain(
            ORG, ["foundrydb_managed", "openai", "none"]
        )
        assert info.overrides[0].surface == "chat"
        assert route.calls.last.request.method == "PUT"
        sent = json.loads(route.calls.last.request.content)
        assert sent == {
            "provider_chain": ["foundrydb_managed", "openai", "none"]
        }

    @respx.mock
    def test_set_surface_override_puts_to_surface_path(self):
        route = respx.put(
            f"{BASE}/organizations/{ORG}/inference/chain/overrides/embedding"
        ).mock(return_value=httpx.Response(200, json=OVERRIDE_PAYLOAD))
        ov = make_sync_api().set_surface_override(
            ORG, "embedding", ["foundrydb_managed", "none"]
        )
        assert isinstance(ov, InferenceChainOverride)
        assert ov.surface == "embedding"
        assert ov.provider_chain == ["foundrydb_managed", "none"]
        sent = json.loads(route.calls.last.request.content)
        assert sent == {"provider_chain": ["foundrydb_managed", "none"]}

    @respx.mock
    def test_delete_surface_override(self):
        route = respx.delete(
            f"{BASE}/organizations/{ORG}/inference/chain/overrides/chat"
        ).mock(return_value=httpx.Response(204, content=b""))
        assert make_sync_api().delete_surface_override(ORG, "chat") is None
        assert route.called

    @respx.mock
    def test_get_usage_decodes_free_tier(self):
        route = respx.get(f"{BASE}/organizations/{ORG}/inference/usage").mock(
            return_value=httpx.Response(200, json=USAGE_PAYLOAD)
        )
        summary = make_sync_api().get_usage(ORG, group_by="model")
        assert isinstance(summary, InferenceUsageSummary)
        assert summary.free_tier is not None
        assert summary.free_tier.tokens_remaining == 840000
        assert route.calls.last.request.url.params["group_by"] == "model"


# ---------------------------------------------------------------------------
# Async AsyncInferenceAPI
# ---------------------------------------------------------------------------

class TestAsyncInferenceAPI:
    @respx.mock
    @pytest.mark.asyncio
    async def test_create_key_sends_service_id(self):
        route = respx.post(f"{BASE}/organizations/{ORG}/inference/keys").mock(
            return_value=httpx.Response(201, json=CREATE_KEY_PAYLOAD)
        )
        api = make_async_api()
        result = await api.create_key(
            ORG,
            name="checkout-service",
            monthly_token_limit=1000000,
            service_id=SVC,
        )
        assert result.key.service_id == SVC
        sent = json.loads(route.calls.last.request.content)
        assert sent["service_id"] == SVC
        await api._http.aclose()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_provider_chain(self):
        respx.get(f"{BASE}/organizations/{ORG}/inference/chain").mock(
            return_value=httpx.Response(200, json=CHAIN_PAYLOAD)
        )
        api = make_async_api()
        info = await api.get_provider_chain(ORG)
        assert info.fully_eu_resident is False
        assert len(info.overrides) == 1
        await api._http.aclose()

    @respx.mock
    @pytest.mark.asyncio
    async def test_set_provider_chain(self):
        route = respx.put(f"{BASE}/organizations/{ORG}/inference/chain").mock(
            return_value=httpx.Response(200, json=CHAIN_PAYLOAD)
        )
        api = make_async_api()
        await api.set_provider_chain(ORG, ["foundrydb_managed", "none"])
        sent = json.loads(route.calls.last.request.content)
        assert sent == {"provider_chain": ["foundrydb_managed", "none"]}
        await api._http.aclose()

    @respx.mock
    @pytest.mark.asyncio
    async def test_set_and_delete_surface_override(self):
        respx.put(
            f"{BASE}/organizations/{ORG}/inference/chain/overrides/embedding"
        ).mock(return_value=httpx.Response(200, json=OVERRIDE_PAYLOAD))
        delete_route = respx.delete(
            f"{BASE}/organizations/{ORG}/inference/chain/overrides/embedding"
        ).mock(return_value=httpx.Response(204, content=b""))
        api = make_async_api()
        ov = await api.set_surface_override(
            ORG, "embedding", ["foundrydb_managed", "none"]
        )
        assert ov.surface == "embedding"
        assert await api.delete_surface_override(ORG, "embedding") is None
        assert delete_route.called
        await api._http.aclose()

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_usage_decodes_free_tier(self):
        respx.get(f"{BASE}/organizations/{ORG}/inference/usage").mock(
            return_value=httpx.Response(200, json=USAGE_PAYLOAD)
        )
        api = make_async_api()
        summary = await api.get_usage(ORG)
        assert summary.free_tier is not None
        assert summary.free_tier.monthly_tokens == 1000000
        await api._http.aclose()
