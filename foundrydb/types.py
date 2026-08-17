"""
FoundryDB SDK - Python data models and type definitions.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional

# Supported database engine types.
# postgresql: 14, 15, 16, 17, 18
# mysql: 8.4
# mongodb: 6.0, 7.0, 8.0
# valkey: 7.2, 8.0, 8.1, 9.0
# kafka: 3.6, 3.7, 3.8, 3.9, 4.0
# opensearch: 2
# mssql: 4.8
DatabaseType = Literal[
    "postgresql",
    "mysql",
    "mongodb",
    "valkey",
    "kafka",
    "opensearch",
    "mssql",
]


# ---- Organization models ----

@dataclass
class Organization:
    """Represents a FoundryDB organization (personal or team)."""

    id: str
    name: str
    slug: str
    is_personal: bool
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Organization":
        return cls(
            id=d.get("id", ""),
            name=d.get("name", ""),
            slug=d.get("slug", ""),
            is_personal=d.get("is_personal", False),
            raw=d,
        )


# ---- Service creation request ----

@dataclass
class CreateServiceRequest:
    """Parameters for creating a new managed service."""

    name: str
    database_type: DatabaseType
    version: str
    plan_name: str
    zone: str
    storage_size_gb: int
    storage_tier: str
    organization_id: Optional[str] = None
    node_count: Optional[int] = None
    auto_failover_enabled: Optional[bool] = None
    replication_mode: Optional[str] = None
    encryption_enabled: Optional[bool] = None
    allowed_cidrs: Optional[List[str]] = None
    maintenance_window: Optional[str] = None
    preset: Optional[str] = None
    is_ephemeral: Optional[bool] = None
    ttl_hours: Optional[int] = None
    created_by_agent_id: Optional[str] = None
    agent_framework: Optional[str] = None
    agent_purpose: Optional[str] = None
    labels: Optional[Dict[str, str]] = None

    def to_dict(self) -> Dict[str, Any]:
        body: Dict[str, Any] = {
            "name": self.name,
            "database_type": self.database_type,
            "version": self.version,
            "plan_name": self.plan_name,
            "zone": self.zone,
            "storage_size_gb": self.storage_size_gb,
            "storage_tier": self.storage_tier,
        }
        if self.node_count is not None:
            body["node_count"] = self.node_count
        if self.auto_failover_enabled is not None:
            body["auto_failover_enabled"] = self.auto_failover_enabled
        if self.replication_mode is not None:
            body["replication_mode"] = self.replication_mode
        if self.encryption_enabled is not None:
            body["encryption_enabled"] = self.encryption_enabled
        if self.allowed_cidrs is not None:
            body["allowed_cidrs"] = self.allowed_cidrs
        if self.maintenance_window is not None:
            body["maintenance_window"] = self.maintenance_window
        if self.preset is not None:
            body["preset"] = self.preset
        if self.is_ephemeral is not None:
            body["is_ephemeral"] = self.is_ephemeral
        if self.ttl_hours is not None:
            body["ttl_hours"] = self.ttl_hours
        if self.created_by_agent_id is not None:
            body["created_by_agent_id"] = self.created_by_agent_id
        if self.agent_framework is not None:
            body["agent_framework"] = self.agent_framework
        if self.agent_purpose is not None:
            body["agent_purpose"] = self.agent_purpose
        if self.labels is not None:
            body["labels"] = self.labels
        return body


# ---- Service models ----

@dataclass
class DNSRecord:
    full_domain: str
    record_type: str
    value: str
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "DNSRecord":
        return cls(
            full_domain=d.get("full_domain", ""),
            record_type=d.get("record_type", ""),
            value=d.get("value", ""),
            raw=d,
        )


@dataclass
class Service:
    id: str
    name: str
    database_type: str
    version: str
    status: str
    plan_name: str
    zone: str
    storage_size_gb: int
    storage_tier: str
    created_at: str
    updated_at: str
    dns_records: List[DNSRecord] = field(default_factory=list)
    allowed_cidrs: List[str] = field(default_factory=list)
    maintenance_window: Optional[str] = None
    is_ephemeral: Optional[bool] = None
    ttl_hours: Optional[int] = None
    scheduled_deletion_at: Optional[str] = None
    preset: Optional[str] = None
    agent_framework: Optional[str] = None
    agent_purpose: Optional[str] = None
    labels: Optional[Dict[str, str]] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Service":
        dns = [DNSRecord.from_dict(r) for r in d.get("dns_records", [])]
        return cls(
            id=d.get("id", ""),
            name=d.get("name", ""),
            database_type=d.get("database_type", ""),
            version=d.get("version", ""),
            status=d.get("status", ""),
            plan_name=d.get("plan_name", ""),
            zone=d.get("zone", ""),
            storage_size_gb=d.get("storage_size_gb", 0),
            storage_tier=d.get("storage_tier", ""),
            created_at=d.get("created_at", ""),
            updated_at=d.get("updated_at", ""),
            dns_records=dns,
            allowed_cidrs=d.get("allowed_cidrs", []),
            maintenance_window=d.get("maintenance_window"),
            is_ephemeral=d.get("is_ephemeral"),
            ttl_hours=d.get("ttl_hours"),
            scheduled_deletion_at=d.get("scheduled_deletion_at"),
            preset=d.get("preset"),
            agent_framework=d.get("agent_framework"),
            agent_purpose=d.get("agent_purpose"),
            labels=d.get("labels"),
            raw=d,
        )


# ---- User / credential models ----

@dataclass
class DatabaseUser:
    username: str
    roles: List[str] = field(default_factory=list)
    created_at: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "DatabaseUser":
        return cls(
            username=d.get("username", ""),
            roles=d.get("roles", []),
            created_at=d.get("created_at"),
            raw=d,
        )


@dataclass
class RevealPasswordResponse:
    username: str
    password: str
    host: str
    port: int
    database: str
    connection_string: str
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "RevealPasswordResponse":
        return cls(
            username=d.get("username", ""),
            password=d.get("password", ""),
            host=d.get("host", ""),
            port=d.get("port", 0),
            database=d.get("database", ""),
            connection_string=d.get("connection_string", ""),
            raw=d,
        )


# ---- Backup models ----

@dataclass
class Backup:
    id: str
    service_id: str
    status: str
    backup_type: str
    size_bytes: Optional[int]
    created_at: str
    completed_at: Optional[str]
    error_message: Optional[str]
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Backup":
        return cls(
            id=d.get("id", ""),
            service_id=d.get("service_id", ""),
            status=d.get("status", ""),
            backup_type=d.get("backup_type", ""),
            size_bytes=d.get("size_bytes"),
            created_at=d.get("created_at", ""),
            completed_at=d.get("completed_at"),
            error_message=d.get("error_message"),
            raw=d,
        )


@dataclass
class TriggerBackupResponse:
    backup_id: Optional[str]
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "TriggerBackupResponse":
        return cls(
            backup_id=d.get("backup_id"),
            raw=d,
        )


# ---- Monitoring models ----

@dataclass
class ServiceMetrics:
    cpu_usage_percent: Optional[float]
    memory_usage_percent: Optional[float]
    disk_usage_percent: Optional[float]
    connections_active: Optional[int]
    connections_max: Optional[int]
    replication_lag_ms: Optional[float]
    queries_per_second: Optional[float]
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ServiceMetrics":
        return cls(
            cpu_usage_percent=d.get("cpu_usage_percent"),
            memory_usage_percent=d.get("memory_usage_percent"),
            disk_usage_percent=d.get("disk_usage_percent"),
            connections_active=d.get("connections_active"),
            connections_max=d.get("connections_max"),
            replication_lag_ms=d.get("replication_lag_ms"),
            queries_per_second=d.get("queries_per_second"),
            raw=d,
        )


@dataclass
class LogsTaskResponse:
    task_id: str

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "LogsTaskResponse":
        return cls(task_id=d.get("task_id", ""))


@dataclass
class LogsResultResponse:
    status: str
    logs: str

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "LogsResultResponse":
        return cls(
            status=d.get("status", ""),
            logs=d.get("logs", ""),
        )


# ---- Preset models ----

@dataclass
class ServicePreset:
    """A predefined service configuration template."""

    id: str
    name: str
    description: str
    database_type: str
    default_version: str
    default_plan: str
    default_storage_gb: int
    default_storage_tier: str
    config_template_id: Optional[str] = None
    is_ephemeral: Optional[bool] = None
    default_ttl_hours: Optional[int] = None
    node_count: Optional[int] = None
    replication_mode: Optional[str] = None
    extensions: List[str] = field(default_factory=list)
    recommended_features: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ServicePreset":
        return cls(
            id=d.get("id", ""),
            name=d.get("name", ""),
            description=d.get("description", ""),
            database_type=d.get("database_type", ""),
            default_version=d.get("default_version", ""),
            default_plan=d.get("default_plan", ""),
            default_storage_gb=d.get("default_storage_gb", 0),
            default_storage_tier=d.get("default_storage_tier", ""),
            config_template_id=d.get("config_template_id"),
            is_ephemeral=d.get("is_ephemeral"),
            default_ttl_hours=d.get("default_ttl_hours"),
            node_count=d.get("node_count"),
            replication_mode=d.get("replication_mode"),
            extensions=d.get("extensions", []),
            recommended_features=d.get("recommended_features", []),
            tags=d.get("tags", []),
            raw=d,
        )


# ---- App service models ----

@dataclass
class AppContainerConfig:
    """Container configuration for an app service."""

    image_ref: str
    container_port: int
    env: Optional[Dict[str, str]] = None
    custom_domains: Optional[List[str]] = None
    registry_username: Optional[str] = None
    health_check_path: Optional[str] = None
    health_check_interval_seconds: Optional[int] = None
    health_check_timeout_seconds: Optional[int] = None
    health_check_healthy_threshold: Optional[int] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "AppContainerConfig":
        return cls(
            image_ref=d.get("image_ref", ""),
            container_port=d.get("container_port", 0),
            env=d.get("env"),
            custom_domains=d.get("custom_domains"),
            registry_username=d.get("registry_username"),
            health_check_path=d.get("health_check_path"),
            health_check_interval_seconds=d.get("health_check_interval_seconds"),
            health_check_timeout_seconds=d.get("health_check_timeout_seconds"),
            health_check_healthy_threshold=d.get("health_check_healthy_threshold"),
            raw=d,
        )

    def to_dict(self) -> Dict[str, Any]:
        body: Dict[str, Any] = {
            "image_ref": self.image_ref,
            "container_port": self.container_port,
        }
        if self.env is not None:
            body["env"] = self.env
        if self.custom_domains is not None:
            body["custom_domains"] = self.custom_domains
        if self.registry_username is not None:
            body["registry_username"] = self.registry_username
        if self.health_check_path is not None:
            body["health_check_path"] = self.health_check_path
        if self.health_check_interval_seconds is not None:
            body["health_check_interval_seconds"] = self.health_check_interval_seconds
        if self.health_check_timeout_seconds is not None:
            body["health_check_timeout_seconds"] = self.health_check_timeout_seconds
        if self.health_check_healthy_threshold is not None:
            body["health_check_healthy_threshold"] = self.health_check_healthy_threshold
        return body


@dataclass
class ServiceAttachment:
    """A database or app attached to an app service."""

    id: str
    attached_service_id: str
    status: str
    env_prefix: Optional[str] = None
    error_message: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ServiceAttachment":
        return cls(
            id=d.get("id", ""),
            attached_service_id=d.get("attached_service_id", ""),
            status=d.get("status", ""),
            env_prefix=d.get("env_prefix"),
            error_message=d.get("error_message"),
            raw=d,
        )


@dataclass
class AppService:
    """A container app hosted on the platform."""

    id: str
    name: str
    service_kind: str
    status: str
    zone: str
    plan_name: str
    storage_size_gb: int
    created_at: str
    updated_at: str
    app_config: Optional[AppContainerConfig] = None
    url: Optional[str] = None
    attachments: List[ServiceAttachment] = field(default_factory=list)
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "AppService":
        cfg = AppContainerConfig.from_dict(d["app_config"]) if d.get("app_config") else None
        attachments = [ServiceAttachment.from_dict(a) for a in d.get("attachments", [])]
        return cls(
            id=d.get("id", ""),
            name=d.get("name", ""),
            service_kind=d.get("service_kind", "app"),
            status=d.get("status", ""),
            zone=d.get("zone", ""),
            plan_name=d.get("plan_name", ""),
            storage_size_gb=d.get("storage_size_gb", 0),
            created_at=d.get("created_at", ""),
            updated_at=d.get("updated_at", ""),
            app_config=cfg,
            url=d.get("url"),
            attachments=attachments,
            raw=d,
        )


@dataclass
class AppDeployStep:
    """One phase of an app deploy or redeploy, captured on the agent.

    ``status`` is one of ``"ok"``, ``"failed"``, or ``"info"``.
    ``duration_ms`` is omitted when the step has not yet completed.
    """

    step: str
    status: str
    started_at: str
    message: Optional[str] = None
    detail: Optional[str] = None
    duration_ms: Optional[int] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "AppDeployStep":
        return cls(
            step=d.get("step", ""),
            status=d.get("status", ""),
            started_at=d.get("started_at", ""),
            message=d.get("message"),
            detail=d.get("detail"),
            duration_ms=d.get("duration_ms"),
            raw=d,
        )


@dataclass
class AppDeployment:
    """A single revision in an app service's deploy history.

    The newest entry reflects the currently serving container. Pass an older
    entry's ``id`` to ``rollback`` to redeploy it.
    ``deploy_logs`` is the ordered list of deploy steps the agent executed for
    this revision (image start, health probe, ingress cutover, previous-color
    teardown). It is distinct from runtime container logs and is empty for
    revisions deployed before the platform captured deploy steps.
    """

    id: str
    service_id: str
    image_ref: str
    container_port: int
    created_at: str
    env: Optional[Dict[str, str]] = None
    custom_domains: Optional[List[str]] = None
    registry_username: Optional[str] = None
    reason: Optional[str] = None
    deploy_logs: List[AppDeployStep] = field(default_factory=list)
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "AppDeployment":
        logs = [AppDeployStep.from_dict(s) for s in d.get("deploy_logs", [])]
        return cls(
            id=d.get("id", ""),
            service_id=d.get("service_id", ""),
            image_ref=d.get("image_ref", ""),
            container_port=d.get("container_port", 0),
            created_at=d.get("created_at", ""),
            env=d.get("env"),
            custom_domains=d.get("custom_domains"),
            registry_username=d.get("registry_username"),
            reason=d.get("reason"),
            deploy_logs=logs,
            raw=d,
        )


# ---- Auth models ----

@dataclass
class SmtpConfig:
    """SMTP credentials for magic-link email delivery.

    Write-only at the API boundary: accepted on enable, stored in the platform
    secret store, and never returned in any response.
    """

    host: str
    port: int
    username: str
    password: str
    from_address: str
    from_name: Optional[str] = None
    insecure_skip_verify: bool = False

    def to_dict(self) -> Dict[str, Any]:
        body: Dict[str, Any] = {
            "host": self.host,
            "port": self.port,
            "username": self.username,
            "password": self.password,
            "from_address": self.from_address,
        }
        if self.from_name is not None:
            body["from_name"] = self.from_name
        if self.insecure_skip_verify:
            body["insecure_skip_verify"] = self.insecure_skip_verify
        return body


@dataclass
class AuthTheme:
    """Non-PII branding applied to the hosted login pages."""

    display_name: Optional[str] = None
    brand_color: Optional[str] = None
    logo_url: Optional[str] = None
    support_url: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "AuthTheme":
        return cls(
            display_name=d.get("display_name"),
            brand_color=d.get("brand_color"),
            logo_url=d.get("logo_url"),
            support_url=d.get("support_url"),
            raw=d,
        )

    def to_dict(self) -> Dict[str, Any]:
        body: Dict[str, Any] = {}
        if self.display_name is not None:
            body["display_name"] = self.display_name
        if self.brand_color is not None:
            body["brand_color"] = self.brand_color
        if self.logo_url is not None:
            body["logo_url"] = self.logo_url
        if self.support_url is not None:
            body["support_url"] = self.support_url
        return body


@dataclass
class IdpProviderRequest:
    """One social-login provider supplied at enable time.

    The ``client_secret`` is write-only: stored in the platform secret store
    and never returned in any response.
    """

    provider: str
    client_id: str
    client_secret: str
    display_name: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        body: Dict[str, Any] = {
            "provider": self.provider,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        if self.display_name is not None:
            body["display_name"] = self.display_name
        return body


@dataclass
class IdpProviderConfig:
    """Stored, non-secret configuration of one social-login provider.

    Returned as part of ``AuthConfiguration``. The ``client_secret`` is never
    returned; it is custodied in the platform secret store.
    """

    provider: str
    client_id: str
    display_name: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "IdpProviderConfig":
        return cls(
            provider=d.get("provider", ""),
            client_id=d.get("client_id", ""),
            display_name=d.get("display_name"),
            raw=d,
        )


@dataclass
class AuthEnableRequest:
    """Parameters for enabling end-user authentication on an app service.

    ``attachment_id`` must reference a healthy PostgreSQL attachment of the app.
    ``issuer_domain_choice`` is fixed at enable time: ``"fallback"`` uses a
    platform subdomain; ``"custom"`` uses your own domain.
    ``smtp`` is mandatory and write-only. ``idp_providers`` optionally enables
    social login (Google and GitHub).
    """

    attachment_id: str
    issuer_domain_choice: str
    smtp: SmtpConfig
    theme: Optional[AuthTheme] = None
    idp_providers: Optional[List[IdpProviderRequest]] = None

    def to_dict(self) -> Dict[str, Any]:
        body: Dict[str, Any] = {
            "attachment_id": self.attachment_id,
            "issuer_domain_choice": self.issuer_domain_choice,
            "smtp": self.smtp.to_dict(),
        }
        if self.theme is not None:
            body["theme"] = self.theme.to_dict()
        if self.idp_providers:
            body["idp_providers"] = [p.to_dict() for p in self.idp_providers]
        return body


@dataclass
class AuthConfiguration:
    """Auth enablement record for an app service.

    Holds enablement state only. The end-user identity data lives in the
    customer's own PostgreSQL database. Secret custody locations are never
    serialized.
    """

    id: str
    app_service_id: str
    database_service_id: str
    attachment_id: str
    issuer_url: str
    fallback_domain: str
    status: str
    theme: Optional[AuthTheme] = None
    idp_providers: List[IdpProviderConfig] = field(default_factory=list)
    user_id: Optional[str] = None
    organization_id: Optional[str] = None
    custom_domain: Optional[str] = None
    schema_version_applied: Optional[str] = None
    failure_reason: Optional[str] = None
    auth_app_service_id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "AuthConfiguration":
        theme_raw = d.get("theme")
        theme = AuthTheme.from_dict(theme_raw) if theme_raw else None
        idp_providers = [IdpProviderConfig.from_dict(p) for p in d.get("idp_providers", [])]
        return cls(
            id=d.get("id", ""),
            app_service_id=d.get("app_service_id", ""),
            database_service_id=d.get("database_service_id", ""),
            attachment_id=d.get("attachment_id", ""),
            issuer_url=d.get("issuer_url", ""),
            fallback_domain=d.get("fallback_domain", ""),
            status=d.get("status", ""),
            theme=theme,
            idp_providers=idp_providers,
            user_id=d.get("user_id"),
            organization_id=d.get("organization_id"),
            custom_domain=d.get("custom_domain"),
            schema_version_applied=d.get("schema_version_applied"),
            failure_reason=d.get("failure_reason"),
            auth_app_service_id=d.get("auth_app_service_id"),
            created_at=d.get("created_at"),
            updated_at=d.get("updated_at"),
            raw=d,
        )


@dataclass
class AuthSigningKey:
    """Controller-side record of one JWT signing keypair.

    Key material is held in the platform secret store and never returned.
    Only the key id, algorithm, and lifecycle status are exposed.
    """

    id: str
    auth_configuration_id: str
    kid: str
    algorithm: str
    status: str
    activated_at: Optional[str] = None
    retired_at: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "AuthSigningKey":
        return cls(
            id=d.get("id", ""),
            auth_configuration_id=d.get("auth_configuration_id", ""),
            kid=d.get("kid", ""),
            algorithm=d.get("algorithm", ""),
            status=d.get("status", ""),
            activated_at=d.get("activated_at"),
            retired_at=d.get("retired_at"),
            created_at=d.get("created_at"),
            updated_at=d.get("updated_at"),
            raw=d,
        )


@dataclass
class AuthConfigurationWithKeys:
    """Auth configuration and its signing key records."""

    auth: Optional[AuthConfiguration]
    signing_keys: List[AuthSigningKey] = field(default_factory=list)
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "AuthConfigurationWithKeys":
        auth_raw = d.get("auth")
        auth = AuthConfiguration.from_dict(auth_raw) if auth_raw else None
        signing_keys = [AuthSigningKey.from_dict(k) for k in d.get("signing_keys", [])]
        return cls(auth=auth, signing_keys=signing_keys, raw=d)


# ---- Edge gateway models ----

# Lifecycle of a customer custom domain on the edge tier.
EdgeDomainStatus = Literal[
    "pending_verification",
    "verifying",
    "issuing_certificate",
    "propagating",
    "active",
    "failed",
    "deleting",
]

# How the edge web application firewall treats matching requests. "block"
# inspects, logs, and rejects matching requests with a 403 so the malicious
# request never reaches the origin.
EdgeWAFMode = Literal["off", "detect", "block"]

# What an edge rate-limit bucket is keyed on.
EdgeRateLimitKey = Literal["ip", "api_key"]

# Where an inbound API key is read from on a request.
EdgeAPIKeyLocation = Literal["header", "query"]

# What the bot-management layer does with a request it flags as a bot.
EdgeBotAction = Literal["log", "block", "challenge"]

# What the account-takeover protection layer does when a threshold trips.
EdgeATOAction = Literal["alert", "ratelimit", "lock"]


@dataclass
class EdgeDomain:
    """A customer custom domain attached to an app service, served through
    the edge tier. Created in pending_verification status; the platform
    verifies DNS ownership and then provisions a TLS certificate."""

    id: str
    service_id: str
    user_id: str
    domain: str
    status: EdgeDomainStatus
    cname_target: str
    created_at: str
    updated_at: str
    certificate_id: Optional[str] = None
    verification_checked_at: Optional[str] = None
    error_message: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EdgeDomain":
        return cls(
            id=d.get("id", ""),
            service_id=d.get("service_id", ""),
            user_id=d.get("user_id", ""),
            domain=d.get("domain", ""),
            status=d.get("status", ""),
            cname_target=d.get("cname_target", ""),
            created_at=d.get("created_at", ""),
            updated_at=d.get("updated_at", ""),
            certificate_id=d.get("certificate_id"),
            verification_checked_at=d.get("verification_checked_at"),
            error_message=d.get("error_message"),
            raw=d,
        )


@dataclass
class EdgeCacheKey:
    """Selects which request attributes a cached entry varies on. An empty
    EdgeCacheKey varies on nothing beyond the request path."""

    vary_query_params: Optional[List[str]] = None
    vary_headers: Optional[List[str]] = None
    vary_cookies: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        if self.vary_query_params:
            out["vary_query_params"] = list(self.vary_query_params)
        if self.vary_headers:
            out["vary_headers"] = list(self.vary_headers)
        if self.vary_cookies:
            out["vary_cookies"] = list(self.vary_cookies)
        return out

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EdgeCacheKey":
        return cls(
            vary_query_params=d.get("vary_query_params"),
            vary_headers=d.get("vary_headers"),
            vary_cookies=d.get("vary_cookies"),
        )


@dataclass
class EdgeCacheRule:
    """Caches responses under one path prefix for a fixed TTL. The optional
    stale-while-revalidate and stale-if-error windows let the edge serve a
    stale entry while it refreshes (or when the origin errors); cache_key
    narrows what the entry varies on; request_collapsing folds concurrent
    cache-fill requests for the same key into one origin fetch."""

    path_prefix: str
    ttl_seconds: int
    stale_while_revalidate_seconds: Optional[int] = None
    stale_if_error_seconds: Optional[int] = None
    cache_key: Optional["EdgeCacheKey"] = None
    request_collapsing: Optional[bool] = None

    def to_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {
            "path_prefix": self.path_prefix,
            "ttl_seconds": self.ttl_seconds,
        }
        if self.stale_while_revalidate_seconds:
            out["stale_while_revalidate_seconds"] = self.stale_while_revalidate_seconds
        if self.stale_if_error_seconds:
            out["stale_if_error_seconds"] = self.stale_if_error_seconds
        if self.cache_key is not None:
            out["cache_key"] = self.cache_key.to_dict()
        if self.request_collapsing:
            out["request_collapsing"] = self.request_collapsing
        return out

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EdgeCacheRule":
        ck = d.get("cache_key")
        return cls(
            path_prefix=d.get("path_prefix", ""),
            ttl_seconds=d.get("ttl_seconds", 0),
            stale_while_revalidate_seconds=d.get("stale_while_revalidate_seconds"),
            stale_if_error_seconds=d.get("stale_if_error_seconds"),
            cache_key=EdgeCacheKey.from_dict(ck) if ck else None,
            request_collapsing=d.get("request_collapsing"),
        )


@dataclass
class EdgeRateLimit:
    """Token bucket enforced per PoP at the edge."""

    requests_per_second: int
    burst: int
    key: EdgeRateLimitKey

    def to_dict(self) -> Dict[str, Any]:
        return {
            "requests_per_second": self.requests_per_second,
            "burst": self.burst,
            "key": self.key,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EdgeRateLimit":
        return cls(
            requests_per_second=d.get("requests_per_second", 0),
            burst=d.get("burst", 0),
            key=d.get("key", "ip"),
        )


# ---- Edge access / auth models ----


@dataclass
class EdgeJWTClaim:
    """One required JWT claim: the claim must be present with the given value."""

    name: str
    value: str

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "value": self.value}

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EdgeJWTClaim":
        return cls(name=d.get("name", ""), value=d.get("value", ""))


@dataclass
class EdgeJWTAuth:
    """Validates a bearer JWT at the edge for the matching paths before the
    request reaches the origin. Carries no secret, so it is echoed verbatim on
    the settings response."""

    enabled: bool
    paths: Optional[List[str]] = None
    jwks_url: Optional[str] = None
    public_keys: Optional[List[str]] = None
    issuer: Optional[str] = None
    audiences: Optional[List[str]] = None
    required_claims: Optional[List[EdgeJWTClaim]] = None
    forward_claims_header: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {"enabled": self.enabled}
        if self.paths:
            out["paths"] = list(self.paths)
        if self.jwks_url:
            out["jwks_url"] = self.jwks_url
        if self.public_keys:
            out["public_keys"] = list(self.public_keys)
        if self.issuer:
            out["issuer"] = self.issuer
        if self.audiences:
            out["audiences"] = list(self.audiences)
        if self.required_claims:
            out["required_claims"] = [c.to_dict() for c in self.required_claims]
        if self.forward_claims_header:
            out["forward_claims_header"] = self.forward_claims_header
        return out

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EdgeJWTAuth":
        claims = d.get("required_claims")
        return cls(
            enabled=d.get("enabled", False),
            paths=d.get("paths"),
            jwks_url=d.get("jwks_url"),
            public_keys=d.get("public_keys"),
            issuer=d.get("issuer"),
            audiences=d.get("audiences"),
            required_claims=[EdgeJWTClaim.from_dict(c) for c in claims] if claims else None,
            forward_claims_header=d.get("forward_claims_header"),
        )


@dataclass
class EdgeSignedURLs:
    """Requires a valid signature query parameter on the matching paths. The
    secret is referenced by name only (never the value); the response carries
    the identical non-secret shape since no secret is ever stored."""

    enabled: bool
    paths: Optional[List[str]] = None
    secret_name: Optional[str] = None
    ttl_seconds: Optional[int] = None
    signature_param: Optional[str] = None
    expires_param: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {"enabled": self.enabled}
        if self.paths:
            out["paths"] = list(self.paths)
        if self.secret_name:
            out["secret_name"] = self.secret_name
        if self.ttl_seconds:
            out["ttl_seconds"] = self.ttl_seconds
        if self.signature_param:
            out["signature_param"] = self.signature_param
        if self.expires_param:
            out["expires_param"] = self.expires_param
        return out

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EdgeSignedURLs":
        return cls(
            enabled=d.get("enabled", False),
            paths=d.get("paths"),
            secret_name=d.get("secret_name"),
            ttl_seconds=d.get("ttl_seconds"),
            signature_param=d.get("signature_param"),
            expires_param=d.get("expires_param"),
        )


@dataclass
class EdgeAPIKeyRequest:
    """One inbound API key on the settings request. ``key`` is the PLAINTEXT
    key value; it is write-only, hashed server-side, and never echoed. An
    optional per-key rate limit overrides the app-wide limit for this key."""

    name: str
    key: Optional[str] = None
    rate_tier: Optional[EdgeRateLimit] = None

    def to_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {"name": self.name}
        if self.key:
            out["key"] = self.key
        if self.rate_tier is not None:
            out["rate_tier"] = self.rate_tier.to_dict()
        return out


@dataclass
class EdgeAPIKeyAuthRequest:
    """Inbound API-key authentication on the settings request. Keys carry
    plaintext key material that the controller hashes and discards; the stored
    document only ever carries the resulting hashes."""

    enabled: bool
    paths: Optional[List[str]] = None
    key_location: Optional[EdgeAPIKeyLocation] = None
    key_name: Optional[str] = None
    keys: Optional[List[EdgeAPIKeyRequest]] = None

    def to_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {"enabled": self.enabled}
        if self.paths:
            out["paths"] = list(self.paths)
        if self.key_location:
            out["key_location"] = self.key_location
        if self.key_name:
            out["key_name"] = self.key_name
        if self.keys:
            out["keys"] = [k.to_dict() for k in self.keys]
        return out


@dataclass
class EdgeAPIKeyView:
    """One inbound API key as echoed on the settings response: no hash, no
    plaintext, only the key name and any per-key rate limit."""

    name: str
    rate_tier: Optional[EdgeRateLimit] = None

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EdgeAPIKeyView":
        rt = d.get("rate_tier")
        return cls(
            name=d.get("name", ""),
            rate_tier=EdgeRateLimit.from_dict(rt) if rt else None,
        )


@dataclass
class EdgeAPIKeyAuthView:
    """Inbound API-key authentication as echoed on the settings response. No
    key material is ever returned, only the key names."""

    enabled: bool
    paths: Optional[List[str]] = None
    key_location: Optional[EdgeAPIKeyLocation] = None
    key_name: Optional[str] = None
    keys: Optional[List[EdgeAPIKeyView]] = None

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EdgeAPIKeyAuthView":
        keys = d.get("keys")
        return cls(
            enabled=d.get("enabled", False),
            paths=d.get("paths"),
            key_location=d.get("key_location"),
            key_name=d.get("key_name"),
            keys=[EdgeAPIKeyView.from_dict(k) for k in keys] if keys else None,
        )


# ---- Edge security hardening models ----


@dataclass
class EdgeWAFExclusion:
    """Excludes a managed WAF rule (by id) or a request target from WAF
    inspection. At least one of rule_id or target is set."""

    rule_id: Optional[int] = None
    target: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        if self.rule_id:
            out["rule_id"] = self.rule_id
        if self.target:
            out["target"] = self.target
        return out

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EdgeWAFExclusion":
        return cls(rule_id=d.get("rule_id"), target=d.get("target"))


@dataclass
class EdgeDDoSProfile:
    """Per-IP volumetric protection at the edge: caps requests-per-second,
    burst, and concurrent connections per source IP."""

    enabled: bool
    per_ip_requests_per_second: Optional[int] = None
    per_ip_burst: Optional[int] = None
    per_ip_conn_cap: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {"enabled": self.enabled}
        if self.per_ip_requests_per_second:
            out["per_ip_requests_per_second"] = self.per_ip_requests_per_second
        if self.per_ip_burst:
            out["per_ip_burst"] = self.per_ip_burst
        if self.per_ip_conn_cap:
            out["per_ip_conn_cap"] = self.per_ip_conn_cap
        return out

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EdgeDDoSProfile":
        return cls(
            enabled=d.get("enabled", False),
            per_ip_requests_per_second=d.get("per_ip_requests_per_second"),
            per_ip_burst=d.get("per_ip_burst"),
            per_ip_conn_cap=d.get("per_ip_conn_cap"),
        )


@dataclass
class EdgeBotManagement:
    """Bot detection at the edge. ``action`` selects what a flagged request
    gets (log, block, or challenge); the heuristics combine a known-bad-bot
    list with a rate-based signal."""

    enabled: bool
    action: Optional[EdgeBotAction] = None
    known_bad_bots: Optional[bool] = None
    rate_based_heuristic: Optional[bool] = None

    def to_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {"enabled": self.enabled}
        if self.action:
            out["action"] = self.action
        if self.known_bad_bots:
            out["known_bad_bots"] = self.known_bad_bots
        if self.rate_based_heuristic:
            out["rate_based_heuristic"] = self.rate_based_heuristic
        return out

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EdgeBotManagement":
        return cls(
            enabled=d.get("enabled", False),
            action=d.get("action"),
            known_bad_bots=d.get("known_bad_bots"),
            rate_based_heuristic=d.get("rate_based_heuristic"),
        )


@dataclass
class EdgeATOProtection:
    """Account-takeover protection: watches authentication paths for repeated
    failures keyed per source IP and per username, and takes ``action`` when a
    threshold trips."""

    enabled: bool
    auth_paths: Optional[List[str]] = None
    failure_status_codes: Optional[List[int]] = None
    per_ip_threshold_per_min: Optional[int] = None
    per_username_threshold_per_min: Optional[int] = None
    username_field: Optional[str] = None
    action: Optional[EdgeATOAction] = None

    def to_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {"enabled": self.enabled}
        if self.auth_paths:
            out["auth_paths"] = list(self.auth_paths)
        if self.failure_status_codes:
            out["failure_status_codes"] = list(self.failure_status_codes)
        if self.per_ip_threshold_per_min:
            out["per_ip_threshold_per_min"] = self.per_ip_threshold_per_min
        if self.per_username_threshold_per_min:
            out["per_username_threshold_per_min"] = self.per_username_threshold_per_min
        if self.username_field:
            out["username_field"] = self.username_field
        if self.action:
            out["action"] = self.action
        return out

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EdgeATOProtection":
        return cls(
            enabled=d.get("enabled", False),
            auth_paths=d.get("auth_paths"),
            failure_status_codes=d.get("failure_status_codes"),
            per_ip_threshold_per_min=d.get("per_ip_threshold_per_min"),
            per_username_threshold_per_min=d.get("per_username_threshold_per_min"),
            username_field=d.get("username_field"),
            action=d.get("action"),
        )


@dataclass
class EdgeAppApplication:
    """One PoP's convergence state for an app service."""

    zone: str
    applied_version: int
    status: str
    error_message: str = ""
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EdgeAppApplication":
        return cls(
            zone=d.get("zone", ""),
            applied_version=d.get("applied_version", 0),
            status=d.get("status", ""),
            error_message=d.get("error_message", ""),
            raw=d,
        )


@dataclass
class EdgeStatus:
    """Edge overview for an app service: whether the edge tier is enabled,
    the home PoP, CNAME target, desired-state version, and per-PoP
    convergence status."""

    edge_enabled: bool
    config_version: int
    home_pop: str = ""
    cname_target: str = ""
    applications: List[EdgeAppApplication] = field(default_factory=list)
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EdgeStatus":
        apps = [EdgeAppApplication.from_dict(a) for a in d.get("applications") or []]
        return cls(
            edge_enabled=d.get("edge_enabled", False),
            config_version=d.get("config_version", 0),
            home_pop=d.get("home_pop", ""),
            cname_target=d.get("cname_target", ""),
            applications=apps,
            raw=d,
        )


@dataclass
class EdgeSettings:
    """Customer-tunable edge settings echoed back after an update. Domains
    and origin are platform-derived and are not included here. signed_urls and
    api_key_auth are projected to their non-secret view shapes; jwt_auth is
    echoed verbatim (it carries no secret). The ``raw`` dict preserves every
    field returned by the server, including ones not modeled explicitly."""

    waf_mode: EdgeWAFMode
    config_version: int
    cache_rules: Optional[List[EdgeCacheRule]] = None
    rate_limit: Optional[EdgeRateLimit] = None
    # Access / auth (echoed on the response).
    jwt_auth: Optional[EdgeJWTAuth] = None
    signed_urls: Optional[EdgeSignedURLs] = None
    api_key_auth: Optional[EdgeAPIKeyAuthView] = None
    # Security hardening (echoed on the response).
    waf_paranoia_level: Optional[int] = None
    waf_rule_exclusions: Optional[List[EdgeWAFExclusion]] = None
    ddos_profile: Optional[EdgeDDoSProfile] = None
    bot_management: Optional[EdgeBotManagement] = None
    ato_protection: Optional[EdgeATOProtection] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EdgeSettings":
        rules_data = d.get("cache_rules")
        rules = [EdgeCacheRule.from_dict(r) for r in rules_data] if rules_data else None
        rl_data = d.get("rate_limit")
        rate_limit = EdgeRateLimit.from_dict(rl_data) if rl_data else None
        jwt_data = d.get("jwt_auth")
        signed_data = d.get("signed_urls")
        apikey_data = d.get("api_key_auth")
        excl_data = d.get("waf_rule_exclusions")
        ddos_data = d.get("ddos_profile")
        bot_data = d.get("bot_management")
        ato_data = d.get("ato_protection")
        return cls(
            waf_mode=d.get("waf_mode", "off"),
            config_version=d.get("config_version", 0),
            cache_rules=rules,
            rate_limit=rate_limit,
            jwt_auth=EdgeJWTAuth.from_dict(jwt_data) if jwt_data else None,
            signed_urls=EdgeSignedURLs.from_dict(signed_data) if signed_data else None,
            api_key_auth=EdgeAPIKeyAuthView.from_dict(apikey_data) if apikey_data else None,
            waf_paranoia_level=d.get("waf_paranoia_level"),
            waf_rule_exclusions=[EdgeWAFExclusion.from_dict(e) for e in excl_data] if excl_data else None,
            ddos_profile=EdgeDDoSProfile.from_dict(ddos_data) if ddos_data else None,
            bot_management=EdgeBotManagement.from_dict(bot_data) if bot_data else None,
            ato_protection=EdgeATOProtection.from_dict(ato_data) if ato_data else None,
            raw=d,
        )


# ---- Edge cache purge ----


@dataclass
class EdgeCachePurgeResult:
    """The rolling purge plan a cache-purge request started. The purge flushes
    nodes one at a time in the background, so the result reports the plan rather
    than a completed flush."""

    planned_nodes: int
    rolling: bool
    node_ids: List[str] = field(default_factory=list)
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EdgeCachePurgeResult":
        return cls(
            planned_nodes=d.get("planned_nodes", 0),
            rolling=d.get("rolling", False),
            node_ids=list(d.get("node_ids") or []),
            raw=d,
        )


# ---- Edge analytics ----


@dataclass
class EdgeMetricsTopPath:
    """One (path, count) entry in a top-paths or suspicious-paths list."""

    path: str
    count: int

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EdgeMetricsTopPath":
        return cls(path=d.get("path", ""), count=d.get("count", 0))


@dataclass
class EdgeStatusClassCounts:
    """Request total broken down by HTTP status class."""

    c2xx: int = 0
    c3xx: int = 0
    c4xx: int = 0
    c5xx: int = 0

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EdgeStatusClassCounts":
        return cls(
            c2xx=d.get("2xx", 0),
            c3xx=d.get("3xx", 0),
            c4xx=d.get("4xx", 0),
            c5xx=d.get("5xx", 0),
        )


@dataclass
class EdgeCacheCounts:
    """Cache hit/miss summary with the derived hit ratio."""

    hit: int = 0
    miss: int = 0
    hit_ratio: float = 0.0

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EdgeCacheCounts":
        return cls(
            hit=d.get("hit", 0),
            miss=d.get("miss", 0),
            hit_ratio=d.get("hit_ratio", 0.0),
        )


@dataclass
class EdgeLatencyPercentiles:
    """Latency percentiles (milliseconds) from the request latency histogram."""

    p50: float = 0.0
    p95: float = 0.0
    p99: float = 0.0

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EdgeLatencyPercentiles":
        return cls(p50=d.get("p50", 0.0), p95=d.get("p95", 0.0), p99=d.get("p99", 0.0))


@dataclass
class EdgeAnalyticsThreat:
    """Per-scope security/threat summary: the WAF detection total plus the
    observed top paths matching credential-scanner shapes."""

    waf_detections_total: int = 0
    suspicious_paths: List[EdgeMetricsTopPath] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EdgeAnalyticsThreat":
        sp = d.get("suspicious_paths") or []
        return cls(
            waf_detections_total=d.get("waf_detections_total", 0),
            suspicious_paths=[EdgeMetricsTopPath.from_dict(p) for p in sp],
        )


@dataclass
class EdgeAnalyticsSummary:
    """Folded edge analytics for one scope (the app total or one PoP). zone is
    empty for the app-wide total."""

    requests_total: int = 0
    error_rate_pct: float = 0.0
    rate_limited_total: int = 0
    waf_detections_total: int = 0
    zone: str = ""
    by_status_class: EdgeStatusClassCounts = field(default_factory=EdgeStatusClassCounts)
    cache: EdgeCacheCounts = field(default_factory=EdgeCacheCounts)
    latency_ms: EdgeLatencyPercentiles = field(default_factory=EdgeLatencyPercentiles)
    waf_by_rule: Dict[str, int] = field(default_factory=dict)
    top_paths: List[EdgeMetricsTopPath] = field(default_factory=list)
    threat: EdgeAnalyticsThreat = field(default_factory=EdgeAnalyticsThreat)
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EdgeAnalyticsSummary":
        tp = d.get("top_paths") or []
        return cls(
            requests_total=d.get("requests_total", 0),
            error_rate_pct=d.get("error_rate_pct", 0.0),
            rate_limited_total=d.get("rate_limited_total", 0),
            waf_detections_total=d.get("waf_detections_total", 0),
            zone=d.get("zone", ""),
            by_status_class=EdgeStatusClassCounts.from_dict(d.get("by_status_class") or {}),
            cache=EdgeCacheCounts.from_dict(d.get("cache") or {}),
            latency_ms=EdgeLatencyPercentiles.from_dict(d.get("latency_ms") or {}),
            waf_by_rule=dict(d.get("waf_by_rule") or {}),
            top_paths=[EdgeMetricsTopPath.from_dict(p) for p in tp],
            threat=EdgeAnalyticsThreat.from_dict(d.get("threat") or {}),
            raw=d,
        )


@dataclass
class EdgeAnalytics:
    """Account-scoped, server-aggregated edge analytics for one app over a
    window, folded across the app's PoPs with a per-PoP breakdown."""

    window_minutes: int
    total: EdgeAnalyticsSummary
    pops: List[EdgeAnalyticsSummary] = field(default_factory=list)
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EdgeAnalytics":
        pops = d.get("pops") or []
        return cls(
            window_minutes=d.get("window_minutes", 0),
            total=EdgeAnalyticsSummary.from_dict(d.get("total") or {}),
            pops=[EdgeAnalyticsSummary.from_dict(p) for p in pops],
            raw=d,
        )


# ---- Edge config version history / rollback ----


@dataclass
class EdgeConfigVersion:
    """One entry in the append-only edge config version history."""

    version: int
    config_hash: str
    source: str
    created_at: str
    active: bool = False
    created_by: Optional[str] = None
    rolled_back_from: Optional[int] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EdgeConfigVersion":
        return cls(
            version=d.get("version", 0),
            config_hash=d.get("config_hash", ""),
            source=d.get("source", ""),
            created_at=d.get("created_at", ""),
            active=d.get("active", False),
            created_by=d.get("created_by"),
            rolled_back_from=d.get("rolled_back_from"),
            raw=d,
        )


@dataclass
class EdgeConfigVersions:
    """The app's edge config version history (newest first, bounded) and the
    live active version."""

    active_version: int
    versions: List[EdgeConfigVersion] = field(default_factory=list)
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EdgeConfigVersions":
        vs = d.get("versions") or []
        return cls(
            active_version=d.get("active_version", 0),
            versions=[EdgeConfigVersion.from_dict(v) for v in vs],
            raw=d,
        )


@dataclass
class EdgeRollbackResult:
    """The new active version a rollback produced. The rollback writes a NEW
    forward version restoring the target's customer-settable subset; it never
    mutates the history."""

    active_version: int
    rolled_back_from: int
    source: str
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EdgeRollbackResult":
        return cls(
            active_version=d.get("active_version", 0),
            rolled_back_from=d.get("rolled_back_from", 0),
            source=d.get("source", ""),
            raw=d,
        )


# ---- Edge staged config rollouts ----


@dataclass
class EdgeRollout:
    """One staged edge config rollout. A rollout stages a new config version to
    a canary subset (one node, or one PoP) first, then either promotes it to the
    rest of the fleet or aborts."""

    id: str
    target_version: int
    phase: str
    canary_scope: str
    started_at: str
    updated_at: str
    canary_selector: str = ""
    promoted_at: Optional[str] = None
    aborted_at: Optional[str] = None
    abort_reason: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EdgeRollout":
        return cls(
            id=d.get("id", ""),
            target_version=d.get("target_version", 0),
            phase=d.get("phase", ""),
            canary_scope=d.get("canary_scope", ""),
            started_at=d.get("started_at", ""),
            updated_at=d.get("updated_at", ""),
            canary_selector=d.get("canary_selector", ""),
            promoted_at=d.get("promoted_at"),
            aborted_at=d.get("aborted_at"),
            abort_reason=d.get("abort_reason"),
            raw=d,
        )


@dataclass
class EdgeRolloutStatus:
    """The app's current (or most recent) staged config rollout. active is True
    when the rollout is in a non-terminal phase (canary or promoting); rollout is
    None when the app has never had a rollout."""

    active: bool
    rollout: Optional[EdgeRollout] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EdgeRolloutStatus":
        r = d.get("rollout")
        return cls(
            active=d.get("active", False),
            rollout=EdgeRollout.from_dict(r) if r else None,
            raw=d,
        )


# ---- Edge fleet administration (admin only) ----
#
# The platform-owned edge gateway PoPs (points of presence) are created, scaled,
# rolled, and retired only through the admin endpoints under /admin/edge. A PoP
# is one edge service with node_count >= 2 (a primary that holds the serving
# floating IP plus one or more hot standbys), giving in-house intra-PoP high
# availability via floating-IP handoff on failure.


@dataclass
class EdgeNode:
    """The admin-facing shape of one edge PoP. node_count and target_node_count
    expose the PoP's primary-plus-standby sizing for HA."""

    id: str
    name: str
    zone: str
    plan_name: str
    status: str
    node_count: int = 0
    target_node_count: int = 0
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EdgeNode":
        return cls(
            id=d.get("id", ""),
            name=d.get("name", ""),
            zone=d.get("zone", ""),
            plan_name=d.get("plan_name", ""),
            status=d.get("status", ""),
            node_count=d.get("node_count", 0),
            target_node_count=d.get("target_node_count", 0),
            raw=d,
        )


@dataclass
class EdgeRollStatus:
    """An edge PoP's image-roll progress. in_progress is True while any node
    still predates the roll request."""

    in_progress: bool
    target_nodes: int = 0
    running_nodes: int = 0
    remaining_old_nodes: int = 0
    replaced_nodes: int = 0
    requested_at: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EdgeRollStatus":
        return cls(
            in_progress=d.get("in_progress", False),
            target_nodes=d.get("target_nodes", 0),
            running_nodes=d.get("running_nodes", 0),
            remaining_old_nodes=d.get("remaining_old_nodes", 0),
            replaced_nodes=d.get("replaced_nodes", 0),
            requested_at=d.get("requested_at"),
            raw=d,
        )


@dataclass
class EdgeAutoscaleConfig:
    """The static edge autoscale policy (display only). None of these values
    feeds a live scaling decision from the overview endpoint."""

    enabled: bool = False
    max_nodes: int = 0
    scale_up_rps: float = 0.0
    scale_down_rps: float = 0.0
    cooldown_seconds: int = 0
    lookback_seconds: int = 0
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EdgeAutoscaleConfig":
        return cls(
            enabled=d.get("enabled", False),
            max_nodes=d.get("max_nodes", 0),
            scale_up_rps=d.get("scale_up_rps", 0.0),
            scale_down_rps=d.get("scale_down_rps", 0.0),
            cooldown_seconds=d.get("cooldown_seconds", 0),
            lookback_seconds=d.get("lookback_seconds", 0),
            raw=d,
        )


@dataclass
class EdgeAutoscaleState:
    """Per-PoP autoscale telemetry for display; it never influences scaling."""

    current_rps: float = 0.0
    per_node_rps: float = 0.0
    last_decision: str = ""
    cooldown_remaining_seconds: int = 0
    last_action_at: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EdgeAutoscaleState":
        return cls(
            current_rps=d.get("current_rps", 0.0),
            per_node_rps=d.get("per_node_rps", 0.0),
            last_decision=d.get("last_decision", ""),
            cooldown_remaining_seconds=d.get("cooldown_remaining_seconds", 0),
            last_action_at=d.get("last_action_at"),
            raw=d,
        )


@dataclass
class EdgeOverviewNode:
    """One VM in an edge PoP. is_serving marks the node currently holding the
    serving floating IP."""

    id: str
    name: str
    role: str
    status: str
    is_serving: bool = False
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EdgeOverviewNode":
        return cls(
            id=d.get("id", ""),
            name=d.get("name", ""),
            role=d.get("role", ""),
            status=d.get("status", ""),
            is_serving=d.get("is_serving", False),
            raw=d,
        )


@dataclass
class EdgeRecoveryStatus:
    """An in-flight HA auto-recovery cycle for a PoP (self-heal replacement,
    failover, scale-out). Present on an overview row only while recovery is
    active."""

    in_progress: bool
    phase: str = ""
    started_at: Optional[str] = None
    estimated_eta: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EdgeRecoveryStatus":
        return cls(
            in_progress=d.get("in_progress", False),
            phase=d.get("phase", ""),
            started_at=d.get("started_at"),
            estimated_eta=d.get("estimated_eta"),
            raw=d,
        )


@dataclass
class EdgeOverviewPoP:
    """One PoP row of the edge overview: its node roster, serving floating IP,
    node deficit, in-flight recovery status, and current load."""

    id: str
    name: str
    zone: str
    plan_name: str
    status: str
    node_count: int = 0
    target_node_count: int = 0
    deficit: int = 0
    serving_fip: Optional[str] = None
    recovery: Optional[EdgeRecoveryStatus] = None
    nodes: List[EdgeOverviewNode] = field(default_factory=list)
    autoscale_state: Optional[EdgeAutoscaleState] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EdgeOverviewPoP":
        rec = d.get("recovery")
        auto = d.get("autoscale_state")
        return cls(
            id=d.get("id", ""),
            name=d.get("name", ""),
            zone=d.get("zone", ""),
            plan_name=d.get("plan_name", ""),
            status=d.get("status", ""),
            node_count=d.get("node_count", 0),
            target_node_count=d.get("target_node_count", 0),
            deficit=d.get("deficit", 0),
            serving_fip=d.get("serving_fip"),
            recovery=EdgeRecoveryStatus.from_dict(rec) if rec else None,
            nodes=[EdgeOverviewNode.from_dict(n) for n in (d.get("nodes") or [])],
            autoscale_state=EdgeAutoscaleState.from_dict(auto) if auto else None,
            raw=d,
        )


@dataclass
class EdgeOverview:
    """The consolidated, read-only snapshot of the edge fleet for the admin
    console: the static autoscale policy plus one row per PoP."""

    autoscale: EdgeAutoscaleConfig
    pops: List[EdgeOverviewPoP] = field(default_factory=list)
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EdgeOverview":
        return cls(
            autoscale=EdgeAutoscaleConfig.from_dict(d.get("autoscale") or {}),
            pops=[EdgeOverviewPoP.from_dict(p) for p in (d.get("pops") or [])],
            raw=d,
        )


@dataclass
class EdgeRecoveryByKind:
    """Aggregated HA recovery activity for one service kind."""

    service_kind: str
    attempts: int = 0
    errors: int = 0
    avg_duration_seconds: float = 0.0
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EdgeRecoveryByKind":
        return cls(
            service_kind=d.get("service_kind", ""),
            attempts=d.get("attempts", 0),
            errors=d.get("errors", 0),
            avg_duration_seconds=d.get("avg_duration_seconds", 0.0),
            raw=d,
        )


@dataclass
class EdgeRecoveryDeficit:
    """One service's current node deficit."""

    service_id: str
    deficit: float = 0.0
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EdgeRecoveryDeficit":
        return cls(
            service_id=d.get("service_id", ""),
            deficit=d.get("deficit", 0.0),
            raw=d,
        )


@dataclass
class EdgeReconcilerTicks:
    """The failed-node reconciler loop counters."""

    scanned: int = 0
    candidates_found: int = 0
    query_failed: int = 0
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EdgeReconcilerTicks":
        return cls(
            scanned=d.get("scanned", 0),
            candidates_found=d.get("candidates_found", 0),
            query_failed=d.get("query_failed", 0),
            raw=d,
        )


@dataclass
class EdgeRecovery:
    """A snapshot of the shared HA recovery telemetry read from the in-process
    metrics gatherer: recovery attempts, errors, and average duration per
    service kind; the failed-node reconciler loop counters; and the per-service
    node deficit."""

    by_kind: List[EdgeRecoveryByKind] = field(default_factory=list)
    deficit_by_service: List[EdgeRecoveryDeficit] = field(default_factory=list)
    reconciler_ticks: EdgeReconcilerTicks = field(default_factory=EdgeReconcilerTicks)
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EdgeRecovery":
        return cls(
            by_kind=[EdgeRecoveryByKind.from_dict(k) for k in (d.get("by_kind") or [])],
            deficit_by_service=[
                EdgeRecoveryDeficit.from_dict(x) for x in (d.get("deficit_by_service") or [])
            ],
            reconciler_ticks=EdgeReconcilerTicks.from_dict(d.get("reconciler_ticks") or {}),
            raw=d,
        )


@dataclass
class EdgeRouteApp:
    """One app routed through the edge, with the PoP zone it is served from and
    its measured request rate over the window."""

    service_id: str
    name: str
    status: str
    zone: str
    requests_per_sec: float = 0.0
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EdgeRouteApp":
        return cls(
            service_id=d.get("service_id", ""),
            name=d.get("name", ""),
            status=d.get("status", ""),
            zone=d.get("zone", ""),
            requests_per_sec=d.get("requests_per_sec", 0.0),
            raw=d,
        )


@dataclass
class EdgeRoutes:
    """The apps currently routed through the edge and their per-PoP request
    rate, ordered busiest first."""

    window_minutes: int = 0
    apps: List[EdgeRouteApp] = field(default_factory=list)
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EdgeRoutes":
        return cls(
            window_minutes=d.get("window_minutes", 0),
            apps=[EdgeRouteApp.from_dict(a) for a in (d.get("apps") or [])],
            raw=d,
        )


# ---- Edge access-log drains ----

# How a log drain transforms the client IP before a line leaves the platform.
EdgeIPRedactionMode = Literal["full", "truncated", "hashed", "omitted"]


@dataclass
class EdgeRedactionPolicy:
    """Per-drain privacy policy applied to every access log line before export.
    Authorization and Cookie are always dropped regardless of header_allow_list."""

    ip_mode: Optional[EdgeIPRedactionMode] = None
    ip_hash_salt: Optional[str] = None
    strip_query_string: Optional[bool] = None
    header_allow_list: Optional[List[str]] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    def to_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        if self.ip_mode:
            out["ip_mode"] = self.ip_mode
        if self.ip_hash_salt:
            out["ip_hash_salt"] = self.ip_hash_salt
        if self.strip_query_string is not None:
            out["strip_query_string"] = self.strip_query_string
        if self.header_allow_list:
            out["header_allow_list"] = list(self.header_allow_list)
        return out

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EdgeRedactionPolicy":
        return cls(
            ip_mode=d.get("ip_mode"),
            ip_hash_salt=d.get("ip_hash_salt"),
            strip_query_string=d.get("strip_query_string"),
            header_allow_list=d.get("header_allow_list"),
            raw=d,
        )


@dataclass
class EdgeLogDrain:
    """Streams an app's per-request edge access logs to a customer destination.
    The destination configuration is write-only and never returned."""

    id: str
    app_service_id: str
    name: str
    destination_type: str
    is_enabled: bool
    created_at: str
    updated_at: str
    description: str = ""
    export_interval_seconds: int = 0
    consecutive_failures: int = 0
    last_export_error: str = ""
    last_export_at: Optional[str] = None
    redaction_policy: EdgeRedactionPolicy = field(default_factory=EdgeRedactionPolicy)
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EdgeLogDrain":
        return cls(
            id=d.get("id", ""),
            app_service_id=d.get("app_service_id", ""),
            name=d.get("name", ""),
            destination_type=d.get("destination_type", ""),
            is_enabled=d.get("is_enabled", False),
            created_at=d.get("created_at", ""),
            updated_at=d.get("updated_at", ""),
            description=d.get("description", ""),
            export_interval_seconds=d.get("export_interval_seconds", 0),
            consecutive_failures=d.get("consecutive_failures", 0),
            last_export_error=d.get("last_export_error", ""),
            last_export_at=d.get("last_export_at"),
            redaction_policy=EdgeRedactionPolicy.from_dict(d.get("redaction_policy") or {}),
            raw=d,
        )


@dataclass
class EdgeLogDrainTestResult:
    """Whether a drain's destination is reachable."""

    ok: bool
    error: str = ""
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EdgeLogDrainTestResult":
        return cls(ok=d.get("ok", False), error=d.get("error", ""), raw=d)


# ---- App jobs models ----

@dataclass
class AppJob:
    """A job definition on an app service: a container run with an optional
    cron schedule. A ``None`` schedule_cron means the job only runs when
    invoked explicitly via run()."""

    id: str
    service_id: str
    name: str
    timezone: str
    enabled: bool
    max_retries: int
    retry_backoff_seconds: int
    max_runtime_seconds: int
    concurrency_cap: int
    overlap_policy: str
    created_at: str
    updated_at: str
    schedule_cron: Optional[str] = None
    image_ref: Optional[str] = None
    command: Optional[List[str]] = None
    env: Optional[Dict[str, str]] = None
    next_run_at: Optional[str] = None
    last_run_at: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "AppJob":
        return cls(
            id=d.get("id", ""),
            service_id=d.get("service_id", ""),
            name=d.get("name", ""),
            timezone=d.get("timezone", "UTC"),
            enabled=d.get("enabled", True),
            max_retries=d.get("max_retries", 0),
            retry_backoff_seconds=d.get("retry_backoff_seconds", 0),
            max_runtime_seconds=d.get("max_runtime_seconds", 3600),
            concurrency_cap=d.get("concurrency_cap", 1),
            overlap_policy=d.get("overlap_policy", ""),
            created_at=d.get("created_at", ""),
            updated_at=d.get("updated_at", ""),
            schedule_cron=d.get("schedule_cron"),
            image_ref=d.get("image_ref"),
            command=d.get("command"),
            env=d.get("env"),
            next_run_at=d.get("next_run_at"),
            last_run_at=d.get("last_run_at"),
            raw=d,
        )


@dataclass
class AppJobInvocation:
    """One execution (or recorded skip) of an app job.

    ``status`` is one of queued, running, succeeded, failed, timed_out, or
    skipped.
    """

    id: str
    job_id: str
    service_id: str
    status: str
    attempt: int
    triggered_by: str
    queued_at: str
    created_at: str
    updated_at: str
    triggered_by_user_id: Optional[str] = None
    agent_task_id: Optional[str] = None
    unit_name: Optional[str] = None
    scheduled_for: Optional[str] = None
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    duration_ms: Optional[int] = None
    exit_code: Optional[int] = None
    error_message: Optional[str] = None
    log_tail: Optional[str] = None
    retry_enqueued: bool = False
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "AppJobInvocation":
        return cls(
            id=d.get("id", ""),
            job_id=d.get("job_id", ""),
            service_id=d.get("service_id", ""),
            status=d.get("status", ""),
            attempt=d.get("attempt", 0),
            triggered_by=d.get("triggered_by", ""),
            queued_at=d.get("queued_at", ""),
            created_at=d.get("created_at", ""),
            updated_at=d.get("updated_at", ""),
            triggered_by_user_id=d.get("triggered_by_user_id"),
            agent_task_id=d.get("agent_task_id"),
            unit_name=d.get("unit_name"),
            scheduled_for=d.get("scheduled_for"),
            started_at=d.get("started_at"),
            finished_at=d.get("finished_at"),
            duration_ms=d.get("duration_ms"),
            exit_code=d.get("exit_code"),
            error_message=d.get("error_message"),
            log_tail=d.get("log_tail"),
            retry_enqueued=d.get("retry_enqueued", False),
            raw=d,
        )


@dataclass
class AppJobLogLines:
    """Log payload inside a completed invocation logs fetch."""

    lines: List[str]
    log_file_path: str
    truncated_at: Optional[int] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "AppJobLogLines":
        return cls(
            lines=d.get("lines", []),
            log_file_path=d.get("log_file_path", ""),
            truncated_at=d.get("truncated_at"),
            raw=d,
        )


@dataclass
class AppJobInvocationLogs:
    """Poll response for an invocation logs fetch task.

    ``status`` mirrors the agent task lifecycle (PENDING, DISPATCHED,
    IN_PROGRESS, COMPLETED, FAILED, TIMEOUT, CANCELLED). ``result`` is set
    once COMPLETED.
    """

    task_id: str
    status: str
    result: Optional[AppJobLogLines] = None
    error_message: str = ""
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "AppJobInvocationLogs":
        result_raw = d.get("result")
        return cls(
            task_id=d.get("task_id", ""),
            status=d.get("status", ""),
            result=AppJobLogLines.from_dict(result_raw) if result_raw else None,
            error_message=d.get("error_message", ""),
            raw=d,
        )


# ---- Queue models ----

@dataclass
class Queue:
    """A named message queue hosted on a PostgreSQL managed service.

    Status is one of Pending, Provisioning, Active, Deprovisioning, or
    Failed. Brokered data-plane operations require Active status.
    """

    id: str
    service_id: str
    name: str
    database_name: str
    visibility_timeout_seconds: int
    max_attempts: int
    dlq_enabled: bool
    status: str
    created_at: str
    updated_at: str
    user_id: str = ""
    organization_id: Optional[str] = None
    error_message: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Queue":
        return cls(
            id=d.get("id", ""),
            service_id=d.get("service_id", ""),
            name=d.get("name", ""),
            database_name=d.get("database_name", ""),
            visibility_timeout_seconds=d.get("visibility_timeout_seconds", 30),
            max_attempts=d.get("max_attempts", 5),
            dlq_enabled=d.get("dlq_enabled", True),
            status=d.get("status", ""),
            created_at=d.get("created_at", ""),
            updated_at=d.get("updated_at", ""),
            user_id=d.get("user_id", ""),
            organization_id=d.get("organization_id"),
            error_message=d.get("error_message"),
            raw=d,
        )


@dataclass
class QueueEnqueueMessageIDs:
    """Assigned message IDs from a completed enqueue task, in request order."""

    message_ids: List[int]
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "QueueEnqueueMessageIDs":
        return cls(message_ids=d.get("message_ids", []), raw=d)


@dataclass
class QueueEnqueueResult:
    """Poll response for an enqueue task.

    ``status`` mirrors the agent task lifecycle. ``result`` is set once
    COMPLETED.
    """

    task_id: str
    status: str
    result: Optional[QueueEnqueueMessageIDs] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "QueueEnqueueResult":
        result_raw = d.get("result")
        return cls(
            task_id=d.get("task_id", ""),
            status=d.get("status", ""),
            result=QueueEnqueueMessageIDs.from_dict(result_raw) if result_raw else None,
            raw=d,
        )


@dataclass
class QueueStats:
    """Per-queue depth snapshot."""

    queue_name: str
    ready_messages: int
    inflight_messages: int
    dead_messages: int
    oldest_age_seconds: float
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "QueueStats":
        return cls(
            queue_name=d.get("queue_name", ""),
            ready_messages=d.get("ready_messages", 0),
            inflight_messages=d.get("inflight_messages", 0),
            dead_messages=d.get("dead_messages", 0),
            oldest_age_seconds=d.get("oldest_age_seconds", 0.0),
            raw=d,
        )


@dataclass
class QueueStatsResult:
    """Poll response for a queue stats task."""

    task_id: str
    status: str
    result: Optional[QueueStats] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "QueueStatsResult":
        result_raw = d.get("result")
        return cls(
            task_id=d.get("task_id", ""),
            status=d.get("status", ""),
            result=QueueStats.from_dict(result_raw) if result_raw else None,
            raw=d,
        )


# ---- File service models ----

@dataclass
class FilesBucket:
    """One bucket backing a files service."""

    region: str
    bucket: str
    endpoint: str
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "FilesBucket":
        return cls(
            region=d.get("region", ""),
            bucket=d.get("bucket", ""),
            endpoint=d.get("endpoint", ""),
            raw=d,
        )


@dataclass
class FilesConfig:
    """Per-service configuration of a files service."""

    buckets: List[FilesBucket]
    quota_gb_soft: int
    quota_gb_hard: int
    versioning: bool
    sse: bool
    lifecycle_enabled: bool
    measured_bytes: int
    over_quota: bool
    measured_at: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "FilesConfig":
        return cls(
            buckets=[FilesBucket.from_dict(b) for b in d.get("buckets", [])],
            quota_gb_soft=d.get("quota_gb_soft", 0),
            quota_gb_hard=d.get("quota_gb_hard", 0),
            versioning=d.get("versioning", False),
            sse=d.get("sse", False),
            lifecycle_enabled=d.get("lifecycle_enabled", False),
            measured_bytes=d.get("measured_bytes", 0),
            over_quota=d.get("over_quota", False),
            measured_at=d.get("measured_at"),
            raw=d,
        )


@dataclass
class FilesService:
    """A managed S3-compatible bucket service."""

    id: str
    name: str
    service_kind: str
    status: str
    zone: str
    created_at: str
    updated_at: str
    user_id: str = ""
    organization_id: Optional[str] = None
    files_config: Optional[FilesConfig] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "FilesService":
        cfg_raw = d.get("files_config")
        return cls(
            id=d.get("id", ""),
            name=d.get("name", ""),
            service_kind=d.get("service_kind", "files"),
            status=d.get("status", ""),
            zone=d.get("zone", ""),
            created_at=d.get("created_at", ""),
            updated_at=d.get("updated_at", ""),
            user_id=d.get("user_id", ""),
            organization_id=d.get("organization_id"),
            files_config=FilesConfig.from_dict(cfg_raw) if cfg_raw else None,
            raw=d,
        )


@dataclass
class FilesUsagePoint:
    """One time-bucketed sample of a bucket's storage footprint."""

    timestamp: str
    bytes: int
    objects: int

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "FilesUsagePoint":
        return cls(
            timestamp=d.get("timestamp", ""),
            bytes=int(d.get("bytes", 0)),
            objects=int(d.get("objects", 0)),
        )


@dataclass
class FilesUsageCurrent:
    """Point-in-time storage footprint of a files service."""

    bytes: int
    objects: int
    live: bool
    monthly_cost_eur: float
    measured_at: Optional[str] = None

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "FilesUsageCurrent":
        return cls(
            bytes=int(d.get("bytes", 0)),
            objects=int(d.get("objects", 0)),
            live=bool(d.get("live", False)),
            monthly_cost_eur=float(d.get("monthly_cost_eur", 0.0)),
            measured_at=d.get("measured_at"),
        )


@dataclass
class FilesUsage:
    """Storage-usage payload: the current footprint plus an over-time series."""

    current: FilesUsageCurrent
    series: List[FilesUsagePoint]
    granularity: str  # "hour" | "day"

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "FilesUsage":
        return cls(
            current=FilesUsageCurrent.from_dict(d.get("current", {})),
            series=[FilesUsagePoint.from_dict(p) for p in d.get("series", [])],
            granularity=d.get("granularity", ""),
        )


@dataclass
class FilesPolicyStatement:
    """One statement of a custom inline access-key policy.

    The client controls the effect, the S3 actions, and the object-key
    prefixes; the platform always scopes resource ARNs to the key's own bucket,
    so a statement can never reach another tenant's data.
    """

    effect: str  # "Allow" | "Deny"
    actions: List[str]
    prefixes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {"effect": self.effect, "actions": list(self.actions)}
        if self.prefixes:
            d["prefixes"] = list(self.prefixes)
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "FilesPolicyStatement":
        return cls(
            effect=d.get("effect", ""),
            actions=list(d.get("actions", [])),
            prefixes=list(d.get("prefixes", [])),
        )


@dataclass
class FilesKeyPolicy:
    """A custom inline policy: statements compiled into a bucket-scoped IAM document."""

    statements: List[FilesPolicyStatement]

    def to_dict(self) -> Dict[str, Any]:
        return {"statements": [s.to_dict() for s in self.statements]}

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "FilesKeyPolicy":
        return cls(
            statements=[FilesPolicyStatement.from_dict(s) for s in d.get("statements", [])]
        )


@dataclass
class FilesAccessKey:
    """One scoped S3 credential for a files service.

    Only the public half (access_key_id) is returned in list and get
    operations. The secret is returned exactly once at creation time.
    """

    id: str
    service_id: str
    name: str
    access_key_id: str
    prefix: str
    permissions: str
    purpose: str
    status: str
    created_at: str
    updated_at: str
    user_id: str = ""
    organization_id: Optional[str] = None
    # Custom policy the key was minted with, when created from a statement list
    # rather than the prefix + permission shorthand. None for shorthand keys.
    inline_policy: Optional[FilesKeyPolicy] = None
    last_used_at: Optional[str] = None
    revoked_at: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "FilesAccessKey":
        return cls(
            id=d.get("id", ""),
            service_id=d.get("service_id", ""),
            name=d.get("name", ""),
            access_key_id=d.get("access_key_id", ""),
            prefix=d.get("prefix", ""),
            permissions=d.get("permissions", "readwrite"),
            purpose=d.get("purpose", "user"),
            status=d.get("status", "active"),
            created_at=d.get("created_at", ""),
            updated_at=d.get("updated_at", ""),
            user_id=d.get("user_id", ""),
            organization_id=d.get("organization_id"),
            inline_policy=(
                FilesKeyPolicy.from_dict(d["inline_policy"])
                if d.get("inline_policy")
                else None
            ),
            last_used_at=d.get("last_used_at"),
            revoked_at=d.get("revoked_at"),
            raw=d,
        )


@dataclass
class FilesAccessKeyWithSecret:
    """CreateFilesAccessKey response. The secret is returned exactly once."""

    key: FilesAccessKey
    secret_access_key: str
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "FilesAccessKeyWithSecret":
        return cls(
            key=FilesAccessKey.from_dict(d),
            secret_access_key=d.get("secret_access_key", ""),
            raw=d,
        )


@dataclass
class FilesPresignedURL:
    """A presigned S3 URL and its validity window."""

    url: str
    method: str
    expires_at: str
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "FilesPresignedURL":
        return cls(
            url=d.get("url", ""),
            method=d.get("method", ""),
            expires_at=d.get("expires_at", ""),
            raw=d,
        )


@dataclass
class FilesObject:
    """One object in a bucket listing."""

    key: str
    size: int
    last_modified: str
    etag: str
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "FilesObject":
        return cls(
            key=d.get("key", ""),
            size=d.get("size", 0),
            last_modified=d.get("last_modified", ""),
            etag=d.get("etag", ""),
            raw=d,
        )


@dataclass
class FilesObjectPage:
    """One page of a bucket listing. ``next_cursor`` is non-empty when more
    objects follow; pass it as the cursor of the next call."""

    objects: List[FilesObject]
    next_cursor: str = ""
    # Common prefixes ("folders") under the current prefix, present when the
    # request used a delimiter. Each ends with the delimiter.
    prefixes: List[str] = field(default_factory=list)
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "FilesObjectPage":
        return cls(
            objects=[FilesObject.from_dict(o) for o in d.get("objects", [])],
            next_cursor=d.get("next_cursor", ""),
            prefixes=list(d.get("prefixes", [])),
            raw=d,
        )


# ---- Inference models ----

@dataclass
class InferenceProviderConfig:
    """API view of one configured AI provider for an organization.

    The provider API key is never returned; ``has_api_key`` only indicates
    its presence.
    """

    id: str
    provider: str
    eu_endpoint: bool
    enabled: bool
    has_api_key: bool
    eu_resident: bool
    created_at: str
    updated_at: str
    base_url: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "InferenceProviderConfig":
        return cls(
            id=d.get("id", ""),
            provider=d.get("provider", ""),
            eu_endpoint=d.get("eu_endpoint", False),
            enabled=d.get("enabled", True),
            has_api_key=d.get("has_api_key", False),
            eu_resident=d.get("eu_resident", False),
            created_at=d.get("created_at", ""),
            updated_at=d.get("updated_at", ""),
            base_url=d.get("base_url"),
            raw=d,
        )


@dataclass
class InferenceKey:
    """API view of a data-plane inference key.

    The secret is never returned after creation. ``key_prefix`` identifies
    the key in customer code.
    """

    id: str
    name: str
    key_prefix: str
    monthly_token_limit: int
    rate_limit_rpm: int
    status: str
    tokens_used_cycle: int
    cycle_month: str
    created_at: str
    service_id: Optional[str] = None
    revoked_at: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "InferenceKey":
        return cls(
            id=d.get("id", ""),
            name=d.get("name", ""),
            key_prefix=d.get("key_prefix", ""),
            monthly_token_limit=d.get("monthly_token_limit", 0),
            rate_limit_rpm=d.get("rate_limit_rpm", 0),
            status=d.get("status", ""),
            tokens_used_cycle=d.get("tokens_used_cycle", 0),
            cycle_month=d.get("cycle_month", ""),
            created_at=d.get("created_at", ""),
            service_id=d.get("service_id"),
            revoked_at=d.get("revoked_at"),
            raw=d,
        )


@dataclass
class CreateInferenceKeyResult:
    """Response from creating an inference key. The secret is shown exactly
    once; store it immediately.

    ``activation_note`` states when the secret starts working at the
    inference endpoint. The key hash reaches the data plane through an edge
    config reconcile that the mint requests immediately, so a request sent in
    the same breath as the mint can still answer ``invalid_key`` and should be
    retried shortly. It is advisory text rather than a status field, because
    the control plane cannot confirm per-node application at mint time.
    """

    key: InferenceKey
    secret: str
    activation_note: str = ""
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "CreateInferenceKeyResult":
        key_raw = d.get("key", d)
        return cls(
            key=InferenceKey.from_dict(key_raw),
            secret=d.get("secret", ""),
            activation_note=d.get("activation_note", ""),
            raw=d,
        )


@dataclass
class OrgInferenceSettings:
    """Org-wide inference proxy policy: EU-only routing and cost circuit
    breaker."""

    organization_id: str
    eu_only: bool
    monthly_cost_limit_cents: int
    circuit_open: bool
    updated_at: str
    circuit_opened_at: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "OrgInferenceSettings":
        return cls(
            organization_id=d.get("organization_id", ""),
            eu_only=d.get("eu_only", False),
            monthly_cost_limit_cents=d.get("monthly_cost_limit_cents", 0),
            circuit_open=d.get("circuit_open", False),
            updated_at=d.get("updated_at", ""),
            circuit_opened_at=d.get("circuit_opened_at"),
            raw=d,
        )


@dataclass
class InferenceUsageRow:
    """One aggregated usage row. ``group_key`` is the model name or key id
    depending on the requested grouping."""

    group_key: str
    provider: str
    calls: int
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost_microcents: int
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "InferenceUsageRow":
        return cls(
            group_key=d.get("group_key", ""),
            provider=d.get("provider", ""),
            calls=d.get("calls", 0),
            input_tokens=d.get("input_tokens", 0),
            output_tokens=d.get("output_tokens", 0),
            total_tokens=d.get("total_tokens", 0),
            cost_microcents=d.get("cost_microcents", 0),
            raw=d,
        )


@dataclass
class OrgInferenceFreeTierStatus:
    """An organization's monthly free token allowance for platform-served
    (``foundrydb_managed``) inference, as it stands now.

    Tokens inside the allowance are metered exactly like paid tokens but
    recorded at zero cost, so the allowance is consumed before any billing
    starts. Only platform-served token calls draw on it: a call to the
    organization's own third-party provider is billed on that provider's
    account, and an image generation is priced per image and reports no
    tokens, so neither consumes the allowance.
    """

    cycle_month: str
    monthly_tokens: int
    tokens_used: int
    tokens_remaining: int
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "OrgInferenceFreeTierStatus":
        return cls(
            cycle_month=d.get("cycle_month", ""),
            monthly_tokens=d.get("monthly_tokens", 0),
            tokens_used=d.get("tokens_used", 0),
            tokens_remaining=d.get("tokens_remaining", 0),
            raw=d,
        )


@dataclass
class InferenceUsageSummary:
    """Aggregated inference usage for an organization.

    ``free_tier`` always describes the current calendar month regardless of
    the queried window, because the allowance is a monthly meter and not an
    aggregate of the window. It is ``None`` when the standing could not be
    read; the rows still answer.
    """

    from_: str
    to: str
    group_by: str
    rows: List[InferenceUsageRow]
    free_tier: Optional[OrgInferenceFreeTierStatus] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "InferenceUsageSummary":
        free_tier_raw = d.get("free_tier")
        return cls(
            from_=d.get("from", ""),
            to=d.get("to", ""),
            group_by=d.get("group_by", ""),
            rows=[InferenceUsageRow.from_dict(r) for r in d.get("rows", [])],
            free_tier=(
                OrgInferenceFreeTierStatus.from_dict(free_tier_raw)
                if free_tier_raw
                else None
            ),
            raw=d,
        )


# The platform AI surfaces whose provider chain may be overridden.
InferenceSurface = Literal["chat", "advisor", "embedding", "agent", "explainer"]


@dataclass
class InferenceChainOverride:
    """One platform AI surface's provider chain override. While it exists,
    that surface resolves through ``provider_chain`` instead of the org-level
    chain."""

    surface: str
    provider_chain: List[str]
    organization_id: str = ""
    created_at: str = ""
    updated_at: str = ""
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "InferenceChainOverride":
        return cls(
            surface=d.get("surface", ""),
            provider_chain=list(d.get("provider_chain") or []),
            organization_id=d.get("organization_id", ""),
            created_at=d.get("created_at", ""),
            updated_at=d.get("updated_at", ""),
            raw=d,
        )


@dataclass
class InferenceProviderChainInfo:
    """An organization's provider chain configuration: the ordered chain,
    whether every provider in it routes EU-resident, and the per-surface
    overrides currently in place. An empty chain is not EU-resident, because
    there is nothing to attest."""

    provider_chain: List[str]
    fully_eu_resident: bool
    overrides: List[InferenceChainOverride]
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "InferenceProviderChainInfo":
        return cls(
            provider_chain=list(d.get("provider_chain") or []),
            fully_eu_resident=d.get("fully_eu_resident", False),
            overrides=[
                InferenceChainOverride.from_dict(o) for o in d.get("overrides", [])
            ],
            raw=d,
        )


# ---- Inference service models ----

# How an inference service is placed. "dedicated" rents a whole-card GPU
# server for the tenant and bills per GPU-hour; it requires a GPU plan.
# "serverless" binds the service to a platform-owned shared pool and bills
# per token; it takes no plan.
InferenceSKU = Literal["dedicated", "serverless"]

# How a model's weights are obtained. "curated" is a blessed catalog model
# the platform has license-verified; "huggingface" is an on-demand pull by
# Hugging Face repo id, whose license is the customer's responsibility.
InferenceModelSource = Literal["curated", "huggingface"]

# What a published model rate charges per. "tokens" carries the two token
# figures; "image" carries image_microcents_per_unit and reads zero tokens.
InferenceModelRateUnit = Literal["tokens", "image"]

# The surface a serverless model answers on.
ServerlessModelCapability = Literal["chat", "embeddings", "rerank", "image"]

# The term of the fit equation that broke the plan's memory budget.
# "weights" means the weights alone exceed the budget, so no context length
# makes the configuration fit; "kv_cache" means the weights fit but the
# requested context does not; "fits" is reported when the configuration fits.
InferenceFitLimitingFactor = Literal["weights", "kv_cache", "fits"]

# The shape of a proposed fix for a configuration that does not fit.
InferenceFitSuggestionKind = Literal["reduce_context", "fp8_kv_cache", "larger_plan"]

# Lifecycle status of a LoRA fine-tuned adapter in the serving registry.
InferenceAdapterStatus = Literal["uploaded", "active", "superseded", "archived"]


@dataclass
class InferenceConfig:
    """Model selection and vLLM serving knobs for an inference service.

    For a curated model the platform resolves the repository, served name,
    and context length from the catalog. For a Hugging Face model,
    ``model_id`` is the ``org/name`` repo id and ``served_model_name`` is
    required.

    ``hf_token`` is write-only: it is accepted on create and never returned
    by any response. ``kv_cache_dtype`` is read-only: it is catalog-owned and
    never accepted from a create request.
    """

    model_id: str
    model_source: str = "curated"
    served_model_name: str = ""
    hf_repo: str = ""
    hf_token: str = ""
    dtype: str = ""
    max_model_len: int = 0
    gpu_memory_utilization: float = 0.0
    tensor_parallel_size: int = 0
    quantization: str = ""
    kv_cache_dtype: str = ""
    license_accepted: bool = False
    enable_fine_tuned_serving: bool = False
    max_loras: int = 0
    max_lora_rank: int = 0
    keep_warm_minutes: int = 0
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for a request body, omitting the fields left unset so
        the platform applies its own defaults."""
        body: Dict[str, Any] = {
            "model_id": self.model_id,
            "model_source": self.model_source,
        }
        if self.served_model_name:
            body["served_model_name"] = self.served_model_name
        if self.hf_repo:
            body["hf_repo"] = self.hf_repo
        if self.hf_token:
            body["hf_token"] = self.hf_token
        if self.dtype:
            body["dtype"] = self.dtype
        if self.max_model_len:
            body["max_model_len"] = self.max_model_len
        if self.gpu_memory_utilization:
            body["gpu_memory_utilization"] = self.gpu_memory_utilization
        if self.tensor_parallel_size:
            body["tensor_parallel_size"] = self.tensor_parallel_size
        if self.quantization:
            body["quantization"] = self.quantization
        if self.license_accepted:
            body["license_accepted"] = True
        if self.enable_fine_tuned_serving:
            body["enable_fine_tuned_serving"] = True
        if self.max_loras:
            body["max_loras"] = self.max_loras
        if self.max_lora_rank:
            body["max_lora_rank"] = self.max_lora_rank
        if self.keep_warm_minutes:
            body["keep_warm_minutes"] = self.keep_warm_minutes
        return body

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "InferenceConfig":
        return cls(
            model_id=d.get("model_id", ""),
            model_source=d.get("model_source", ""),
            served_model_name=d.get("served_model_name", ""),
            hf_repo=d.get("hf_repo", ""),
            hf_token=d.get("hf_token", ""),
            dtype=d.get("dtype", ""),
            max_model_len=d.get("max_model_len", 0),
            gpu_memory_utilization=d.get("gpu_memory_utilization", 0.0),
            tensor_parallel_size=d.get("tensor_parallel_size", 0),
            quantization=d.get("quantization", ""),
            kv_cache_dtype=d.get("kv_cache_dtype", ""),
            license_accepted=d.get("license_accepted", False),
            enable_fine_tuned_serving=d.get("enable_fine_tuned_serving", False),
            max_loras=d.get("max_loras", 0),
            max_lora_rank=d.get("max_lora_rank", 0),
            keep_warm_minutes=d.get("keep_warm_minutes", 0),
            raw=d,
        )


@dataclass
class InferenceService:
    """A managed inference service: an open-weight LLM served by vLLM, on a
    whole-card GPU server (``inference_sku`` ``dedicated``) or on a
    platform-owned shared pool (``serverless``).

    ``endpoint_base_url`` is the complete OpenAI-compatible base URL to point
    an SDK at, so no client has to assemble a scheme, a host and a ``/v1``
    suffix of its own. It is always a platform address and never the upstream
    the platform forwards to. Call it with an ``fdb-inf`` key and the model
    ``foundrydb_managed/<served_model_name>``.

    ``provisioning_message`` is the newest live provisioning heartbeat while
    a deploy is in flight, so it is worth surfacing only while polling a
    create. It is returned by the single-service read only.
    """

    id: str
    user_id: str
    name: str
    service_kind: str
    status: str
    zone: str
    plan_name: str
    node_count: int
    tls_enabled: bool
    created_at: str
    updated_at: str
    organization_id: str = ""
    inference_sku: str = ""
    storage_size_gb: Optional[int] = None
    storage_tier: str = ""
    inference_config: Optional[InferenceConfig] = None
    error_message: str = ""
    endpoint_hostname: str = ""
    endpoint_base_url: str = ""
    provisioning_message: str = ""
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "InferenceService":
        config_raw = d.get("inference_config")
        return cls(
            id=d.get("id", ""),
            user_id=d.get("user_id", ""),
            name=d.get("name", ""),
            service_kind=d.get("service_kind", ""),
            status=d.get("status", ""),
            zone=d.get("zone", ""),
            plan_name=d.get("plan_name", ""),
            node_count=d.get("node_count", 0),
            tls_enabled=d.get("tls_enabled", False),
            created_at=d.get("created_at", ""),
            updated_at=d.get("updated_at", ""),
            organization_id=d.get("organization_id") or "",
            inference_sku=d.get("inference_sku", ""),
            storage_size_gb=d.get("storage_size_gb"),
            storage_tier=d.get("storage_tier", ""),
            inference_config=(
                InferenceConfig.from_dict(config_raw) if config_raw else None
            ),
            error_message=d.get("error_message") or "",
            endpoint_hostname=d.get("endpoint_hostname") or "",
            endpoint_base_url=d.get("endpoint_base_url") or "",
            provisioning_message=d.get("provisioning_message") or "",
            raw=d,
        )


@dataclass
class InferenceModelRate:
    """One curated model's published price as it stands right now, the rate a
    serverless call on that model is metered at.

    ``prompt_microcents_per_1k`` and ``completion_microcents_per_1k`` are in
    microcents per one thousand tokens; divide by 100,000 for the currency
    amount per one million tokens. Both are zero on an image-priced rate,
    where ``image_microcents_per_unit`` prices one generated image; divide
    that by 100,000,000 for the currency amount per image.
    """

    model_id: str
    prompt_microcents_per_1k: int
    completion_microcents_per_1k: int
    effective_from: str
    rate_unit: str = "tokens"
    image_microcents_per_unit: int = 0
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "InferenceModelRate":
        return cls(
            model_id=d.get("model_id", ""),
            prompt_microcents_per_1k=d.get("prompt_microcents_per_1k", 0),
            completion_microcents_per_1k=d.get("completion_microcents_per_1k", 0),
            effective_from=d.get("effective_from", ""),
            rate_unit=d.get("rate_unit") or "tokens",
            image_microcents_per_unit=d.get("image_microcents_per_unit", 0),
            raw=d,
        )


@dataclass
class ServerlessInferenceModel:
    """One curated model a shared pool can answer for right now, and so one a
    serverless create can bind to. It describes the model, never the pool.

    ``serving`` is always true on a listed model: a model with no serving
    pool is omitted rather than listed as unavailable. ``deprecated`` marks a
    model whose weights are end of life upstream; it is still listed and
    still bindable, so treat it as retiring rather than as a default choice.
    """

    model_id: str
    display_name: str
    capability: str
    serving: bool
    deprecated: bool
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ServerlessInferenceModel":
        return cls(
            model_id=d.get("model_id", ""),
            display_name=d.get("display_name", ""),
            capability=d.get("capability", ""),
            serving=d.get("serving", False),
            deprecated=d.get("deprecated", False),
            raw=d,
        )


@dataclass
class InferenceFitSuggestion:
    """One concrete way to make a refused configuration fit. Suggestions are
    only offered when they would actually work, so a weights-limited refusal
    never proposes trimming the context."""

    kind: str
    detail: str
    plan_name: str = ""
    max_model_len: int = 0
    tensor_parallel_size: int = 0
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "InferenceFitSuggestion":
        return cls(
            kind=d.get("kind", ""),
            detail=d.get("detail", ""),
            plan_name=d.get("plan_name", ""),
            max_model_len=d.get("max_model_len", 0),
            tensor_parallel_size=d.get("tensor_parallel_size", 0),
            raw=d,
        )


@dataclass
class InferenceFitCheckResult:
    """The verdict of the VRAM fit preflight, the memory breakdown it was
    reached from, and the closest fixes when it is a refusal. All sizes are
    gibibytes of VRAM.

    ``max_context_that_fits`` is zero when the weights alone exceed the
    budget, in which case no context length helps. ``recommended_plan`` is
    the smallest GPU plan on which the request fits, answered whether or not
    the plan that was asked about fits.
    """

    fits: bool
    weights_gb: float
    kv_cache_gb: float
    overhead_gb: float
    budget_gb: float
    plan_vram_gb: int
    max_context_that_fits: int
    limiting_factor: str
    suggestions: List[InferenceFitSuggestion] = field(default_factory=list)
    recommended_plan: str = ""
    recommended_tensor_parallel_size: int = 0
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "InferenceFitCheckResult":
        return cls(
            fits=d.get("fits", False),
            weights_gb=d.get("weights_gb", 0.0),
            kv_cache_gb=d.get("kv_cache_gb", 0.0),
            overhead_gb=d.get("overhead_gb", 0.0),
            budget_gb=d.get("budget_gb", 0.0),
            plan_vram_gb=d.get("plan_vram_gb", 0),
            max_context_that_fits=d.get("max_context_that_fits", 0),
            limiting_factor=d.get("limiting_factor", ""),
            suggestions=[
                InferenceFitSuggestion.from_dict(s) for s in d.get("suggestions", [])
            ],
            recommended_plan=d.get("recommended_plan", ""),
            recommended_tensor_parallel_size=d.get(
                "recommended_tensor_parallel_size", 0
            ),
            raw=d,
        )


@dataclass
class InferenceServiceUsageTotals:
    """Usage counters rolled up across every bucket in the requested window.

    ``images`` stays zero for a text model, which produces none; an image
    model meters images rather than output tokens, so it is the only usage
    figure that moves there. ``p95_latency_ms`` is computed over the metered
    calls rather than folded up from the series, because a percentile is not
    summable.
    """

    calls: int
    errors: int
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost_microcents: int
    images: int = 0
    avg_latency_ms: int = 0
    p95_latency_ms: int = 0
    error_rate: float = 0.0
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "InferenceServiceUsageTotals":
        return cls(
            calls=d.get("calls", 0),
            errors=d.get("errors", 0),
            input_tokens=d.get("input_tokens", 0),
            output_tokens=d.get("output_tokens", 0),
            total_tokens=d.get("total_tokens", 0),
            cost_microcents=d.get("cost_microcents", 0),
            images=d.get("images", 0),
            avg_latency_ms=d.get("avg_latency_ms", 0),
            p95_latency_ms=d.get("p95_latency_ms", 0),
            error_rate=d.get("error_rate", 0.0),
            raw=d,
        )


@dataclass
class InferenceServiceUsagePoint:
    """One time bucket of usage. Empty buckets are omitted from the series."""

    bucket_start: str
    calls: int
    errors: int
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost_microcents: int
    images: int = 0
    avg_latency_ms: int = 0
    p95_latency_ms: int = 0
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "InferenceServiceUsagePoint":
        return cls(
            bucket_start=d.get("bucket_start", ""),
            calls=d.get("calls", 0),
            errors=d.get("errors", 0),
            input_tokens=d.get("input_tokens", 0),
            output_tokens=d.get("output_tokens", 0),
            total_tokens=d.get("total_tokens", 0),
            cost_microcents=d.get("cost_microcents", 0),
            images=d.get("images", 0),
            avg_latency_ms=d.get("avg_latency_ms", 0),
            p95_latency_ms=d.get("p95_latency_ms", 0),
            raw=d,
        )


@dataclass
class InferenceServiceGpuHourCost:
    """The accrued GPU-hour spend for a dedicated inference service over the
    window, in EUR.

    ``billed_hours`` is the number of hourly billing snapshots counted,
    ``hourly_rate_eur`` the most recent hourly rate, and ``cost_eur`` the
    summed spend, approximately ``hourly_rate_eur * billed_hours``.
    """

    billed_hours: int
    hourly_rate_eur: float
    cost_eur: float
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "InferenceServiceGpuHourCost":
        return cls(
            billed_hours=d.get("billed_hours", 0),
            hourly_rate_eur=d.get("hourly_rate_eur", 0.0),
            cost_eur=d.get("cost_eur", 0.0),
            raw=d,
        )


@dataclass
class InferenceServiceUsageMonthToDate:
    """One service's calendar-month-to-date rollup, independent of the window
    the caller asked for.

    Both charges sit on it so a client does not issue a second request per
    range change: ``tokens`` is the per-token charge a serverless service
    accrues, ``gpu_hour`` the per-GPU-hour charge a dedicated one accrues.
    ``from_`` is the first instant of the current UTC month, or the service's
    creation time when it is younger than the month, so a two-day-old service
    never claims a full month.
    """

    from_: str
    tokens: InferenceServiceUsageTotals
    gpu_hour: Optional[InferenceServiceGpuHourCost] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "InferenceServiceUsageMonthToDate":
        gpu_hour_raw = d.get("gpu_hour")
        return cls(
            from_=d.get("from", ""),
            tokens=InferenceServiceUsageTotals.from_dict(d.get("tokens") or {}),
            gpu_hour=(
                InferenceServiceGpuHourCost.from_dict(gpu_hour_raw)
                if gpu_hour_raw
                else None
            ),
            raw=d,
        )


@dataclass
class InferenceServiceUsage:
    """A service's metered usage over a window: rolled-up totals plus the
    ordered bucket series.

    Usage is attributed to the service's dedicated endpoint within the owning
    organization, so two services serving the same model never share each
    other's usage, and the window never starts before the service was
    created. Which figure is the charge depends on the SKU:
    ``month_to_date.tokens`` for a serverless service and
    ``month_to_date.gpu_hour`` for a dedicated one. The other is a usage
    signal, not a bill.
    """

    service_id: str
    from_: str
    to: str
    bucket_seconds: int
    totals: InferenceServiceUsageTotals
    series: List[InferenceServiceUsagePoint] = field(default_factory=list)
    gpu_hour: Optional[InferenceServiceGpuHourCost] = None
    month_to_date: Optional[InferenceServiceUsageMonthToDate] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "InferenceServiceUsage":
        gpu_hour_raw = d.get("gpu_hour")
        mtd_raw = d.get("month_to_date")
        return cls(
            service_id=d.get("service_id", ""),
            from_=d.get("from", ""),
            to=d.get("to", ""),
            bucket_seconds=d.get("bucket_seconds", 0),
            totals=InferenceServiceUsageTotals.from_dict(d.get("totals") or {}),
            series=[
                InferenceServiceUsagePoint.from_dict(p) for p in d.get("series", [])
            ],
            gpu_hour=(
                InferenceServiceGpuHourCost.from_dict(gpu_hour_raw)
                if gpu_hour_raw
                else None
            ),
            month_to_date=(
                InferenceServiceUsageMonthToDate.from_dict(mtd_raw)
                if mtd_raw
                else None
            ),
            raw=d,
        )


@dataclass
class InferenceGPUStats:
    """A single GPU's hardware telemetry sampled from nvidia-smi on the
    inference node. Memory is in mebibytes and power in watts."""

    index: int
    util_percent: float
    mem_used_mb: float
    mem_total_mb: float
    temp_c: float
    power_w: float
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "InferenceGPUStats":
        return cls(
            index=d.get("index", 0),
            util_percent=d.get("util_percent", 0.0),
            mem_used_mb=d.get("mem_used_mb", 0.0),
            mem_total_mb=d.get("mem_total_mb", 0.0),
            temp_c=d.get("temp_c", 0.0),
            power_w=d.get("power_w", 0.0),
            raw=d,
        )


@dataclass
class InferenceServerMetricsSnapshot:
    """One sampled reading of a GPU inference node's live serving telemetry:
    the vLLM server's own Prometheus metrics plus the node's GPU hardware
    counters.

    Token throughput and the average-latency fields are interval rates
    derived on the node from the delta between two consecutive scrapes, so
    the first scrape after start reports zero for those. ``server_reachable``
    is false when the vLLM metrics endpoint could not be scraped this tick
    (still starting, crash-looping, or draining), in which case the GPU
    fields may still be present.
    """

    collected_at: str
    server_reachable: bool = False
    model_name: str = ""
    requests_running: float = 0.0
    requests_waiting: float = 0.0
    gpu_cache_usage_perc: float = 0.0
    generation_tokens_per_sec: float = 0.0
    prompt_tokens_per_sec: float = 0.0
    avg_ttft_ms: float = 0.0
    avg_tpot_ms: float = 0.0
    avg_e2e_latency_ms: float = 0.0
    requests_success_total: float = 0.0
    gpus: List[InferenceGPUStats] = field(default_factory=list)
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "InferenceServerMetricsSnapshot":
        return cls(
            collected_at=d.get("collected_at", ""),
            server_reachable=d.get("server_reachable", False),
            model_name=d.get("model_name", ""),
            requests_running=d.get("requests_running", 0.0),
            requests_waiting=d.get("requests_waiting", 0.0),
            gpu_cache_usage_perc=d.get("gpu_cache_usage_perc", 0.0),
            generation_tokens_per_sec=d.get("generation_tokens_per_sec", 0.0),
            prompt_tokens_per_sec=d.get("prompt_tokens_per_sec", 0.0),
            avg_ttft_ms=d.get("avg_ttft_ms", 0.0),
            avg_tpot_ms=d.get("avg_tpot_ms", 0.0),
            avg_e2e_latency_ms=d.get("avg_e2e_latency_ms", 0.0),
            requests_success_total=d.get("requests_success_total", 0.0),
            gpus=[InferenceGPUStats.from_dict(g) for g in d.get("gpus") or []],
            raw=d,
        )


@dataclass
class InferenceServiceMetrics:
    """The live-metrics payload for one inference service: the ordered
    snapshot series over the requested window plus the most recent snapshot
    for the realtime tiles.

    It is the live vLLM and GPU telemetry the inference node samples,
    distinct from the metered usage and cost.
    """

    service_id: str
    from_: str
    to: str
    snapshots: List[InferenceServerMetricsSnapshot] = field(default_factory=list)
    latest: Optional[InferenceServerMetricsSnapshot] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "InferenceServiceMetrics":
        latest_raw = d.get("latest")
        return cls(
            service_id=d.get("service_id", ""),
            from_=d.get("from", ""),
            to=d.get("to", ""),
            snapshots=[
                InferenceServerMetricsSnapshot.from_dict(s)
                for s in d.get("snapshots") or []
            ],
            latest=(
                InferenceServerMetricsSnapshot.from_dict(latest_raw)
                if latest_raw
                else None
            ),
            raw=d,
        )


@dataclass
class InferenceModelAdapter:
    """One version of a customer LoRA fine-tuned adapter in the serving
    registry.

    The adapter is trained on the organization's data and its weights stored
    in Files (object storage); promoting it downloads the weights onto the
    base-model GPU, verifies their hash, and hot-loads them into vLLM. Once
    active, the service answers to the adapter as
    ``foundrydb_managed/<served_model_name>`` on the OpenAI-compatible
    endpoint. An adapter never leaves its owning organization's boundary.

    ``inference_service_id`` is ``None`` while the row is only uploaded and
    not yet promoted; ``version`` is monotonic per organization and served
    model name, and a rollback re-promotes a prior version.
    """

    id: str
    organization_id: str
    base_model_id: str
    served_model_name: str
    version: int
    files_bucket: str
    files_key_prefix: str
    adapter_sha256: str
    size_bytes: int
    status: str
    created_at: str
    inference_service_id: Optional[str] = None
    base_model_license: str = ""
    promoted_at: Optional[str] = None
    deleted_at: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "InferenceModelAdapter":
        return cls(
            id=d.get("id", ""),
            organization_id=d.get("organization_id", ""),
            base_model_id=d.get("base_model_id", ""),
            served_model_name=d.get("served_model_name", ""),
            version=d.get("version", 0),
            files_bucket=d.get("files_bucket", ""),
            files_key_prefix=d.get("files_key_prefix", ""),
            adapter_sha256=d.get("adapter_sha256", ""),
            size_bytes=d.get("size_bytes", 0),
            status=d.get("status", ""),
            created_at=d.get("created_at", ""),
            inference_service_id=d.get("inference_service_id"),
            base_model_license=d.get("base_model_license", ""),
            promoted_at=d.get("promoted_at"),
            deleted_at=d.get("deleted_at"),
            raw=d,
        )


# ---- Webhook and event models ----

@dataclass
class WebhookEndpoint:
    """A customer-configured HTTP endpoint that receives signed event
    notifications. The signing secret is returned only on creation."""

    id: str
    url: str
    events: List[str]
    active: bool
    consecutive_failures: int
    total_delivered: int
    total_failed: int
    created_at: str
    updated_at: str
    secret: str = ""
    last_success_at: Optional[str] = None
    last_failure_at: Optional[str] = None
    disabled_at: Optional[str] = None
    disabled_reason: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "WebhookEndpoint":
        return cls(
            id=d.get("id", ""),
            url=d.get("url", ""),
            events=d.get("events", []),
            active=d.get("active", True),
            consecutive_failures=d.get("consecutive_failures", 0),
            total_delivered=d.get("total_delivered", 0),
            total_failed=d.get("total_failed", 0),
            created_at=d.get("created_at", ""),
            updated_at=d.get("updated_at", ""),
            secret=d.get("secret", ""),
            last_success_at=d.get("last_success_at"),
            last_failure_at=d.get("last_failure_at"),
            disabled_at=d.get("disabled_at"),
            disabled_reason=d.get("disabled_reason"),
            raw=d,
        )


@dataclass
class WebhookDelivery:
    """One entry in a webhook endpoint's delivery history."""

    id: str
    webhook_id: str
    event_type: str
    status: str
    attempt_count: int
    created_at: str
    updated_at: str
    event_id: Optional[str] = None
    next_retry_at: Optional[str] = None
    response_status: Optional[int] = None
    response_body: Optional[str] = None
    delivered_at: Optional[str] = None
    failed_at: Optional[str] = None
    error_message: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "WebhookDelivery":
        return cls(
            id=d.get("id", ""),
            webhook_id=d.get("webhook_id", ""),
            event_type=d.get("event_type", ""),
            status=d.get("status", ""),
            attempt_count=d.get("attempt_count", 0),
            created_at=d.get("created_at", ""),
            updated_at=d.get("updated_at", ""),
            event_id=d.get("event_id"),
            next_retry_at=d.get("next_retry_at"),
            response_status=d.get("response_status"),
            response_body=d.get("response_body"),
            delivered_at=d.get("delivered_at"),
            failed_at=d.get("failed_at"),
            error_message=d.get("error_message"),
            raw=d,
        )


@dataclass
class Event:
    """One entry in the queryable event stream."""

    seq: int
    id: str
    event_type: str
    data: Any
    created_at: str
    organization_id: Optional[str] = None
    service_id: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Event":
        return cls(
            seq=d.get("seq", 0),
            id=d.get("id", ""),
            event_type=d.get("event_type", ""),
            data=d.get("data"),
            created_at=d.get("created_at", ""),
            organization_id=d.get("organization_id"),
            service_id=d.get("service_id"),
            raw=d,
        )


@dataclass
class EventPage:
    """One page of the event feed."""

    events: List[Event]
    next_cursor: Optional[int] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EventPage":
        return cls(
            events=[Event.from_dict(e) for e in d.get("events", [])],
            next_cursor=d.get("next_cursor"),
            raw=d,
        )


# ---- Data pipeline models ----

@dataclass
class DataPipelineConfig:
    """Optional configuration for a data pipeline."""

    database_name: str = ""
    tables: List[str] = field(default_factory=list)
    topic_prefix: str = ""
    snapshot_mode: str = ""
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "DataPipelineConfig":
        return cls(
            database_name=d.get("database_name", ""),
            tables=d.get("tables", []),
            topic_prefix=d.get("topic_prefix", ""),
            snapshot_mode=d.get("snapshot_mode", ""),
            raw=d,
        )

    def to_dict(self) -> Dict[str, Any]:
        body: Dict[str, Any] = {}
        if self.database_name:
            body["database_name"] = self.database_name
        if self.tables:
            body["tables"] = self.tables
        if self.topic_prefix:
            body["topic_prefix"] = self.topic_prefix
        if self.snapshot_mode:
            body["snapshot_mode"] = self.snapshot_mode
        return body


@dataclass
class DataPipeline:
    """A data flow between two managed services."""

    id: str
    organization_id: str
    name: str
    pipeline_type: str
    source_service_id: str
    sink_service_id: str
    status: str
    config: DataPipelineConfig
    created_at: str
    updated_at: str
    provision_step: Optional[str] = None
    connector_name: Optional[str] = None
    publication_name: Optional[str] = None
    slot_name: Optional[str] = None
    topic_prefix: Optional[str] = None
    last_connector_state: Optional[str] = None
    source_lag_bytes: Optional[int] = None
    last_health_check_at: Optional[str] = None
    error_message: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "DataPipeline":
        cfg_raw = d.get("config", {})
        return cls(
            id=d.get("id", ""),
            organization_id=d.get("organization_id", ""),
            name=d.get("name", ""),
            pipeline_type=d.get("pipeline_type", ""),
            source_service_id=d.get("source_service_id", ""),
            sink_service_id=d.get("sink_service_id", ""),
            status=d.get("status", ""),
            config=DataPipelineConfig.from_dict(cfg_raw) if cfg_raw else DataPipelineConfig(),
            created_at=d.get("created_at", ""),
            updated_at=d.get("updated_at", ""),
            provision_step=d.get("provision_step"),
            connector_name=d.get("connector_name"),
            publication_name=d.get("publication_name"),
            slot_name=d.get("slot_name"),
            topic_prefix=d.get("topic_prefix"),
            last_connector_state=d.get("last_connector_state"),
            source_lag_bytes=d.get("source_lag_bytes"),
            last_health_check_at=d.get("last_health_check_at"),
            error_message=d.get("error_message"),
            raw=d,
        )


@dataclass
class DataPipelineStatus:
    """Latest reconciler-observed status of a data pipeline."""

    id: str
    status: str
    connector_name: Optional[str] = None
    connector_state: Optional[str] = None
    task_states: Optional[Any] = None
    source_lag_bytes: Optional[int] = None
    topic_prefix: Optional[str] = None
    last_health_check_at: Optional[str] = None
    error_message: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "DataPipelineStatus":
        return cls(
            id=d.get("id", ""),
            status=d.get("status", ""),
            connector_name=d.get("connector_name"),
            connector_state=d.get("connector_state"),
            task_states=d.get("task_states"),
            source_lag_bytes=d.get("source_lag_bytes"),
            topic_prefix=d.get("topic_prefix"),
            last_health_check_at=d.get("last_health_check_at"),
            error_message=d.get("error_message"),
            raw=d,
        )


# ---- Embedding pipeline models ----

# Embedding pipeline mode: how the pipeline processes its source table.
EmbeddingPipelineMode = Literal["continuous", "scheduled", "manual"]


@dataclass
class EmbeddingPipeline:
    """One auto-vectorization pipeline on a managed service."""

    id: str
    service_id: str
    database_name: str
    source_schema: str
    source_table: str
    text_columns: List[str]
    model_provider: str
    embedding_model: str
    model_dimensions: int
    target_schema: str
    target_table: str
    batch_size: int
    poll_interval_seconds: int
    mode: str
    status: str
    rows_processed: int
    rows_pending: int
    tokens_used: int
    created_at: str
    updated_at: str
    provider_base_url: Optional[str] = None
    schedule_cron: Optional[str] = None
    source_filter: Optional[str] = None
    max_row_retries: int = 0
    next_run_at: Optional[str] = None
    error_message: Optional[str] = None
    last_processed_at: Optional[str] = None
    last_error: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EmbeddingPipeline":
        return cls(
            id=d.get("id", ""),
            service_id=d.get("service_id", ""),
            database_name=d.get("database_name", ""),
            source_schema=d.get("source_schema", ""),
            source_table=d.get("source_table", ""),
            text_columns=d.get("text_columns", []),
            model_provider=d.get("model_provider", ""),
            embedding_model=d.get("embedding_model", ""),
            model_dimensions=d.get("model_dimensions", 0),
            target_schema=d.get("target_schema", ""),
            target_table=d.get("target_table", ""),
            batch_size=d.get("batch_size", 100),
            poll_interval_seconds=d.get("poll_interval_seconds", 60),
            mode=d.get("mode", "continuous"),
            status=d.get("status", ""),
            rows_processed=d.get("rows_processed", 0),
            rows_pending=d.get("rows_pending", 0),
            tokens_used=d.get("tokens_used", 0),
            created_at=d.get("created_at", ""),
            updated_at=d.get("updated_at", ""),
            provider_base_url=d.get("provider_base_url"),
            schedule_cron=d.get("schedule_cron"),
            source_filter=d.get("source_filter"),
            max_row_retries=d.get("max_row_retries", 0),
            next_run_at=d.get("next_run_at"),
            error_message=d.get("error_message"),
            last_processed_at=d.get("last_processed_at"),
            last_error=d.get("last_error"),
            raw=d,
        )


@dataclass
class EmbeddingRunErrorSample:
    """One failed source row in an embedding pipeline run."""

    source_row_id: str
    error: str
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EmbeddingRunErrorSample":
        return cls(
            source_row_id=d.get("source_row_id", ""),
            error=d.get("error", ""),
            raw=d,
        )


@dataclass
class EmbeddingPipelineRun:
    """One discrete embedding job execution for a scheduled or manual
    pipeline."""

    id: str
    pipeline_id: str
    status: str
    trigger: str
    rows_scanned: int
    rows_embedded: int
    rows_failed: int
    tokens_used: int
    created_at: str
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    error_message: Optional[str] = None
    error_sample: List[EmbeddingRunErrorSample] = field(default_factory=list)
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EmbeddingPipelineRun":
        return cls(
            id=d.get("id", ""),
            pipeline_id=d.get("pipeline_id", ""),
            status=d.get("status", ""),
            trigger=d.get("trigger", ""),
            rows_scanned=d.get("rows_scanned", 0),
            rows_embedded=d.get("rows_embedded", 0),
            rows_failed=d.get("rows_failed", 0),
            tokens_used=d.get("tokens_used", 0),
            created_at=d.get("created_at", ""),
            started_at=d.get("started_at"),
            finished_at=d.get("finished_at"),
            error_message=d.get("error_message"),
            error_sample=[EmbeddingRunErrorSample.from_dict(e) for e in d.get("error_sample", [])],
            raw=d,
        )


# ---- Vector search models ----

# Distance operator for vector similarity search.
VectorSearchMetric = Literal["cosine", "l2", "ip"]


@dataclass
class VectorSearchFilter:
    """One column filter applied to a vector search. Only ``eq`` is
    supported."""

    column: str
    op: str
    value: Any

    def to_dict(self) -> Dict[str, Any]:
        return {"column": self.column, "op": self.op, "value": self.value}


@dataclass
class VectorSearchColumn:
    """Describes one result column."""

    name: str
    type: str
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "VectorSearchColumn":
        return cls(name=d.get("name", ""), type=d.get("type", ""), raw=d)


@dataclass
class VectorSearchResponse:
    """Result of a vector search, with the search parameters echoed back."""

    columns: List[VectorSearchColumn]
    rows: List[List[Any]]
    row_count: int
    truncated: bool
    execution_ms: int
    metric: str
    top_k: int
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "VectorSearchResponse":
        return cls(
            columns=[VectorSearchColumn.from_dict(c) for c in d.get("columns", [])],
            rows=d.get("rows", []),
            row_count=d.get("row_count", 0),
            truncated=d.get("truncated", False),
            execution_ms=d.get("execution_ms", 0),
            metric=d.get("metric", "cosine"),
            top_k=d.get("top_k", 0),
            raw=d,
        )


# ---- AI actions models ----

@dataclass
class AIActionRef:
    """How a client can act on a feed item."""

    type: str
    tier: str
    target: str
    href: str
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "AIActionRef":
        return cls(
            type=d.get("type", ""),
            tier=d.get("tier", ""),
            target=d.get("target", ""),
            href=d.get("href", ""),
            raw=d,
        )


@dataclass
class AIActionItem:
    """One prioritized entry in the AI actions feed."""

    id: str
    kind: str
    severity: str
    service_id: str
    service_name: str
    title: str
    summary: str
    action: AIActionRef
    created_at: str
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "AIActionItem":
        return cls(
            id=d.get("id", ""),
            kind=d.get("kind", ""),
            severity=d.get("severity", ""),
            service_id=d.get("service_id", ""),
            service_name=d.get("service_name", ""),
            title=d.get("title", ""),
            summary=d.get("summary", ""),
            action=AIActionRef.from_dict(d.get("action", {})),
            created_at=d.get("created_at", ""),
            raw=d,
        )


@dataclass
class AIActionsResponse:
    """Feed envelope for the AI actions feed."""

    items: List[AIActionItem]
    total: int
    truncated: bool
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "AIActionsResponse":
        return cls(
            items=[AIActionItem.from_dict(i) for i in d.get("items", [])],
            total=d.get("total", 0),
            truncated=d.get("truncated", False),
            raw=d,
        )


@dataclass
class CopilotStep:
    """One proposed tool call in a copilot plan."""

    tool: str
    tier: str
    preview: str
    args: Optional[Dict[str, Any]] = None
    rationale: str = ""
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "CopilotStep":
        return cls(
            tool=d.get("tool", ""),
            tier=d.get("tier", ""),
            preview=d.get("preview", ""),
            args=d.get("args"),
            rationale=d.get("rationale", ""),
            raw=d,
        )


@dataclass
class CopilotPlan:
    """A previewable plan for a natural-language intent. Executes nothing."""

    summary: str
    steps: List[CopilotStep]
    unsupported: bool
    note: str = ""
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "CopilotPlan":
        return cls(
            summary=d.get("summary", ""),
            steps=[CopilotStep.from_dict(s) for s in d.get("steps", [])],
            unsupported=d.get("unsupported", False),
            note=d.get("note", ""),
            raw=d,
        )


@dataclass
class ExecuteAIActionResult:
    """Response envelope for an AI action execution attempt."""

    action_type: str
    status: str
    http_status: int
    message: str
    detail: Optional[Any] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ExecuteAIActionResult":
        return cls(
            action_type=d.get("action_type", ""),
            status=d.get("status", ""),
            http_status=d.get("http_status", 0),
            message=d.get("message", ""),
            detail=d.get("detail"),
            raw=d,
        )


@dataclass
class AIActionExecution:
    """API view of one persisted Action Center execution."""

    id: str
    service_id: str
    action_type: str
    status: str
    http_status: int
    created_at: str
    organization_id: Optional[str] = None
    target_id: str = ""
    actor_user_id: str = ""
    reverted_at: str = ""
    revert_status: str = ""
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "AIActionExecution":
        return cls(
            id=d.get("id", ""),
            service_id=d.get("service_id", ""),
            action_type=d.get("action_type", ""),
            status=d.get("status", ""),
            http_status=d.get("http_status", 0),
            created_at=d.get("created_at", ""),
            organization_id=d.get("organization_id"),
            target_id=d.get("target_id", ""),
            actor_user_id=d.get("actor_user_id", ""),
            reverted_at=d.get("reverted_at", ""),
            revert_status=d.get("revert_status", ""),
            raw=d,
        )


@dataclass
class AIActionExecutionListResponse:
    """Outcome-loop execution history envelope."""

    executions: List[AIActionExecution]
    total_count: int
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "AIActionExecutionListResponse":
        return cls(
            executions=[AIActionExecution.from_dict(e) for e in d.get("executions", [])],
            total_count=d.get("total_count", 0),
            raw=d,
        )


@dataclass
class AIActionRollbackResult:
    """Response envelope for an accepted rollback."""

    execution_id: str
    action_type: str
    revert_status: str
    message: str
    task_id: str = ""
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "AIActionRollbackResult":
        return cls(
            execution_id=d.get("execution_id", ""),
            action_type=d.get("action_type", ""),
            revert_status=d.get("revert_status", ""),
            message=d.get("message", ""),
            task_id=d.get("task_id", ""),
            raw=d,
        )


# ---- Compliance models ----

@dataclass
class ControlAssertion:
    """One evaluated control in a compliance packet."""

    control_id: str
    title: str
    assertion: str
    status: str
    evidence_refs: List[str] = field(default_factory=list)
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ControlAssertion":
        return cls(
            control_id=d.get("control_id", ""),
            title=d.get("title", ""),
            assertion=d.get("assertion", ""),
            status=d.get("status", ""),
            evidence_refs=d.get("evidence_refs", []),
            raw=d,
        )


@dataclass
class CompliancePacket:
    """Structured evidence packet covering one compliance framework and period."""

    schema_version: str
    framework: str
    generated_at: str
    period_start: str
    period_end: str
    organization: Dict[str, Any]
    scope_boundary: str
    controls: List[ControlAssertion]
    summary: Dict[str, Any]
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "CompliancePacket":
        return cls(
            schema_version=d.get("schema_version", ""),
            framework=d.get("framework", ""),
            generated_at=d.get("generated_at", ""),
            period_start=d.get("period_start", ""),
            period_end=d.get("period_end", ""),
            organization=d.get("organization", {}),
            scope_boundary=d.get("scope_boundary", ""),
            controls=[ControlAssertion.from_dict(c) for c in d.get("controls", [])],
            summary=d.get("summary", {}),
            raw=d,
        )


@dataclass
class CompliancePacketSignature:
    """Detached signature covering the canonical serialization of a compliance packet."""

    algorithm: str
    key_id: str
    value: str
    canonical_sha256: str
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "CompliancePacketSignature":
        return cls(
            algorithm=d.get("algorithm", ""),
            key_id=d.get("key_id", ""),
            value=d.get("value", ""),
            canonical_sha256=d.get("canonical_sha256", ""),
            raw=d,
        )


@dataclass
class CompliancePacketResponse:
    """GET /compliance-reports/{id} response: packet with its detached signature."""

    packet: CompliancePacket
    signature: CompliancePacketSignature
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "CompliancePacketResponse":
        return cls(
            packet=CompliancePacket.from_dict(d.get("packet", {})),
            signature=CompliancePacketSignature.from_dict(d.get("signature", {})),
            raw=d,
        )


@dataclass
class GenerateComplianceReportResponse:
    """Response from POST /compliance-reports: the new report ID plus the packet."""

    report_id: str
    packet: CompliancePacket
    signature: CompliancePacketSignature
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "GenerateComplianceReportResponse":
        return cls(
            report_id=d.get("report_id", ""),
            packet=CompliancePacket.from_dict(d.get("packet", {})),
            signature=CompliancePacketSignature.from_dict(d.get("signature", {})),
            raw=d,
        )


@dataclass
class ComplianceReportRecord:
    """One entry in the compliance report index for an organization."""

    id: str
    organization_id: str
    framework: str
    schema_version: str
    period_start: str
    period_end: str
    generated_at: str
    generated_by: str
    signing_key_id: str
    algorithm: str
    status: str
    has_pdf: bool
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ComplianceReportRecord":
        return cls(
            id=d.get("id", ""),
            organization_id=d.get("organization_id", ""),
            framework=d.get("framework", ""),
            schema_version=d.get("schema_version", ""),
            period_start=d.get("period_start", ""),
            period_end=d.get("period_end", ""),
            generated_at=d.get("generated_at", ""),
            generated_by=d.get("generated_by", ""),
            signing_key_id=d.get("signing_key_id", ""),
            algorithm=d.get("algorithm", ""),
            status=d.get("status", ""),
            has_pdf=d.get("has_pdf", False),
            raw=d,
        )


@dataclass
class ComplianceSigningKey:
    """One public signing key in the platform key set."""

    key_id: str
    algorithm: str
    public_key: str
    active: bool
    retired_at: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ComplianceSigningKey":
        return cls(
            key_id=d.get("key_id", ""),
            algorithm=d.get("algorithm", ""),
            public_key=d.get("public_key", ""),
            active=d.get("active", False),
            retired_at=d.get("retired_at"),
            raw=d,
        )


@dataclass
class ComplianceSigningKeySet:
    """JWKS-style response from /.well-known/compliance-signing-keys."""

    algorithm: str
    keys: List[ComplianceSigningKey]
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ComplianceSigningKeySet":
        return cls(
            algorithm=d.get("algorithm", ""),
            keys=[ComplianceSigningKey.from_dict(k) for k in d.get("keys", [])],
            raw=d,
        )


@dataclass
class ComplianceSubscription:
    """One compliance framework subscription for an organization.

    ``subscribed_at`` is set when the subscription was activated.
    ``canceled_at`` is set if the subscription has been canceled and is
    otherwise ``None``. ``monthly_price_eur`` is the current monthly price in
    EUR, expressed as a float (e.g. ``29.0``).
    """

    framework: str
    enabled: bool
    monthly_price_eur: float
    subscribed_at: Optional[str] = None
    canceled_at: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ComplianceSubscription":
        return cls(
            framework=d.get("framework", ""),
            enabled=d.get("enabled", False),
            monthly_price_eur=d.get("monthly_price_eur", 0.0),
            subscribed_at=d.get("subscribed_at"),
            canceled_at=d.get("canceled_at"),
            raw=d,
        )


# ---- Companion-app attachment models ----

@dataclass
class AttachmentCatalogEntry:
    """One entry in the companion-app attachment catalog.

    ``kind`` is the stable identifier used when creating an attachment
    (e.g. ``"metabase"``). ``requires_parent_kinds`` lists the database
    engine types the companion app can attach to.
    """

    kind: str
    display_name: str
    description: str
    category: str
    default_plan: str
    requires_parent_kinds: List[str] = field(default_factory=list)
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "AttachmentCatalogEntry":
        return cls(
            kind=d.get("kind", ""),
            display_name=d.get("display_name", ""),
            description=d.get("description", ""),
            category=d.get("category", ""),
            default_plan=d.get("default_plan", ""),
            requires_parent_kinds=d.get("requires_parent_kinds", []),
            raw=d,
        )


@dataclass
class AttachmentSummary:
    """Summary of one companion-app attachment on a managed service."""

    attachment_id: str
    app_service_id: str
    kind: str
    name: str
    status: str
    wiring_status: str
    url: str = ""
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "AttachmentSummary":
        return cls(
            attachment_id=d.get("attachment_id", ""),
            app_service_id=d.get("app_service_id", ""),
            kind=d.get("kind", ""),
            name=d.get("name", ""),
            status=d.get("status", ""),
            wiring_status=d.get("wiring_status", ""),
            url=d.get("url", ""),
            raw=d,
        )


@dataclass
class AttachmentCredentials:
    """Admin credentials for a companion-app attachment.

    ``generated`` holds any extra key/value pairs the companion app
    exposes (e.g. API tokens, embed secrets).
    """

    admin_email: str
    admin_password: str
    login_url: str
    generated: Dict[str, str] = field(default_factory=dict)
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "AttachmentCredentials":
        return cls(
            admin_email=d.get("admin_email", ""),
            admin_password=d.get("admin_password", ""),
            login_url=d.get("login_url", ""),
            generated=d.get("generated", {}),
            raw=d,
        )


# ---- Stack models ----

# Lifecycle status of a stack.
StackStatus = Literal[
    "Pending",
    "Provisioning",
    "Wiring",
    "Running",
    "RollingBack",
    "Failed",
    "Deleting",
    "Deleted",
]

# Kind of resource provisioned inside a stack.
StackResourceKind = Literal["database", "files", "inference", "app"]

# Visibility of a custom stack template in the marketplace.
StackVisibility = Literal["private", "public"]

# Publication lifecycle of a custom stack template.
StackPublicationStatus = Literal["draft", "pending_review", "published", "unpublished"]


@dataclass
class StackDescriptor:
    """One resource descriptor inside a custom stack template definition.

    ``kind`` must be one of the ``StackResourceKind`` literals. ``symbolic_name``
    is the stable intra-template identifier used in ``depends_on`` references.
    ``config`` holds kind-specific parameters (plan, version, zone, etc.).
    ``depends_on`` lists ``symbolic_name`` values of resources that must be
    Running before this one is provisioned.
    """

    symbolic_name: str
    kind: str
    config: Dict[str, Any]
    depends_on: List[str] = field(default_factory=list)
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "StackDescriptor":
        return cls(
            symbolic_name=d.get("symbolic_name", ""),
            kind=d.get("kind", ""),
            config=d.get("config", {}),
            depends_on=d.get("depends_on", []),
            raw=d,
        )

    def to_dict(self) -> Dict[str, Any]:
        body: Dict[str, Any] = {
            "symbolic_name": self.symbolic_name,
            "kind": self.kind,
            "config": self.config,
        }
        if self.depends_on:
            body["depends_on"] = self.depends_on
        return body


@dataclass
class CustomTemplateRequest:
    """Parameters for creating or updating a custom stack template.

    ``display_name`` and ``description`` are human-readable metadata.
    ``version`` is a semver string (e.g. ``"1.0.0"``).
    ``resources`` is the ordered list of resource descriptors that define what
    the template provisions. ``visibility`` controls whether the template is
    visible only to the owning organization (``"private"``) or listed in the
    marketplace (``"public"`` after publication review).
    """

    display_name: str
    description: str
    version: str
    resources: List[StackDescriptor]
    visibility: StackVisibility = "private"
    tags: Optional[List[str]] = None
    readme: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        body: Dict[str, Any] = {
            "display_name": self.display_name,
            "description": self.description,
            "version": self.version,
            "resources": [r.to_dict() for r in self.resources],
            "visibility": self.visibility,
        }
        if self.tags is not None:
            body["tags"] = self.tags
        if self.readme is not None:
            body["readme"] = self.readme
        return body


@dataclass
class CustomStackTemplate:
    """A customer-authored stack template registered in the platform.

    ``name`` is the system-assigned stable identifier. ``publication_status``
    tracks the review and publication lifecycle. ``source_template_id`` is set
    when the template was forked from a marketplace entry.
    """

    id: str
    name: str
    display_name: str
    description: str
    version: str
    visibility: str
    publication_status: str
    organization_id: str
    created_at: str
    updated_at: str
    resources: List[StackDescriptor] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    readme: Optional[str] = None
    source_template_id: Optional[str] = None
    source_publisher_org_id: Optional[str] = None
    published_at: Optional[str] = None
    unpublished_at: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "CustomStackTemplate":
        return cls(
            id=d.get("id", ""),
            name=d.get("name", ""),
            display_name=d.get("display_name", ""),
            description=d.get("description", ""),
            version=d.get("version", ""),
            visibility=d.get("visibility", "private"),
            publication_status=d.get("publication_status", "draft"),
            organization_id=d.get("organization_id", ""),
            created_at=d.get("created_at", ""),
            updated_at=d.get("updated_at", ""),
            resources=[StackDescriptor.from_dict(r) for r in d.get("resources", [])],
            tags=d.get("tags", []),
            readme=d.get("readme"),
            source_template_id=d.get("source_template_id"),
            source_publisher_org_id=d.get("source_publisher_org_id"),
            published_at=d.get("published_at"),
            unpublished_at=d.get("unpublished_at"),
            raw=d,
        )


@dataclass
class ResourceChange:
    """One resource-level change in a stack upgrade plan.

    ``action`` is one of ``"add"``, ``"update"``, or ``"delete"``.
    ``symbolic_name`` identifies the resource within the template.
    ``detail`` carries human-readable description of what will change.
    """

    symbolic_name: str
    kind: str
    action: str
    detail: str
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ResourceChange":
        return cls(
            symbolic_name=d.get("symbolic_name", ""),
            kind=d.get("kind", ""),
            action=d.get("action", ""),
            detail=d.get("detail", ""),
            raw=d,
        )


@dataclass
class StackUpgradePlan:
    """Preview of what applying a stack upgrade will change.

    ``from_version`` and ``to_version`` are the template semver strings.
    ``changes`` is the ordered list of resource-level diffs. ``warnings``
    carries advisory notes (e.g. brief downtime, data migration required).
    ``estimated_monthly_cost`` is the projected cost after the upgrade.
    """

    stack_id: str
    from_version: str
    to_version: str
    changes: List[ResourceChange]
    warnings: List[str] = field(default_factory=list)
    estimated_monthly_cost: Optional[float] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "StackUpgradePlan":
        return cls(
            stack_id=d.get("stack_id", ""),
            from_version=d.get("from_version", ""),
            to_version=d.get("to_version", ""),
            changes=[ResourceChange.from_dict(c) for c in d.get("changes", [])],
            warnings=d.get("warnings", []),
            estimated_monthly_cost=d.get("estimated_monthly_cost"),
            raw=d,
        )


@dataclass
class StackMigration:
    """A recorded stack upgrade execution.

    ``status`` is one of ``"pending"``, ``"in_progress"``, ``"completed"``, or
    ``"failed"``. ``from_version`` and ``to_version`` reflect the template
    versions involved.
    """

    id: str
    stack_id: str
    from_version: str
    to_version: str
    status: str
    created_at: str
    updated_at: str
    completed_at: Optional[str] = None
    error_message: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "StackMigration":
        return cls(
            id=d.get("id", ""),
            stack_id=d.get("stack_id", ""),
            from_version=d.get("from_version", ""),
            to_version=d.get("to_version", ""),
            status=d.get("status", ""),
            created_at=d.get("created_at", ""),
            updated_at=d.get("updated_at", ""),
            completed_at=d.get("completed_at"),
            error_message=d.get("error_message"),
            raw=d,
        )


@dataclass
class StackTemplate:
    """One entry in the stack template catalog.

    ``name`` is the stable identifier used when launching a stack (e.g.
    ``"rag-chatbot"``). ``cost_preview`` holds the same shape as
    ``StackCostPreview`` but may be omitted when the template has no fixed
    cost estimate.
    """

    name: str
    display_name: str
    description: str
    version: str
    cost_preview: Optional[Dict[str, Any]] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "StackTemplate":
        return cls(
            name=d.get("name", ""),
            display_name=d.get("display_name", ""),
            description=d.get("description", ""),
            version=d.get("version", ""),
            cost_preview=d.get("cost_preview"),
            raw=d,
        )


@dataclass
class StackCostLineItem:
    """One component of a stack cost preview."""

    symbolic_name: str
    kind: str
    description: str
    monthly_cost: float
    is_ceiling: bool
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "StackCostLineItem":
        return cls(
            symbolic_name=d.get("symbolic_name", ""),
            kind=d.get("kind", ""),
            description=d.get("description", ""),
            monthly_cost=d.get("monthly_cost", 0.0),
            is_ceiling=d.get("is_ceiling", False),
            raw=d,
        )


@dataclass
class StackCostPreview:
    """Estimated monthly cost for launching a stack template.

    Show this to the user and pass ``monthly_total`` as
    ``accepted_monthly_cost`` when calling ``launch_stack``.
    ``warnings`` carries advisory notes (e.g. cost ceiling caveats).
    """

    template_name: str
    currency: str
    monthly_total: float
    line_items: List[StackCostLineItem]
    warnings: List[str] = field(default_factory=list)
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "StackCostPreview":
        return cls(
            template_name=d.get("template_name", ""),
            currency=d.get("currency", "EUR"),
            monthly_total=d.get("monthly_total", 0.0),
            line_items=[StackCostLineItem.from_dict(i) for i in d.get("line_items", [])],
            warnings=d.get("warnings", []),
            raw=d,
        )


@dataclass
class StackResource:
    """One constituent resource inside a stack.

    ``kind`` is one of ``database``, ``files``, ``inference``, or ``app``.
    ``service_id`` is set once the resource has been provisioned; ``ref_id``
    holds opaque provider-level identifiers for non-service resources.
    ``depends_on`` lists the ``symbolic_name`` values of resources that must
    be Running before this one is provisioned.
    """

    id: str
    stack_id: str
    symbolic_name: str
    kind: str
    status: str
    sequence: int
    created_at: str
    updated_at: str
    service_id: Optional[str] = None
    ref_id: Optional[str] = None
    status_detail: Optional[str] = None
    depends_on: List[str] = field(default_factory=list)
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "StackResource":
        return cls(
            id=d.get("id", ""),
            stack_id=d.get("stack_id", ""),
            symbolic_name=d.get("symbolic_name", ""),
            kind=d.get("kind", ""),
            status=d.get("status", ""),
            sequence=d.get("sequence", 0),
            created_at=d.get("created_at", ""),
            updated_at=d.get("updated_at", ""),
            service_id=d.get("service_id"),
            ref_id=d.get("ref_id"),
            status_detail=d.get("status_detail"),
            depends_on=d.get("depends_on", []),
            raw=d,
        )


@dataclass
class Stack:
    """A vertical-starter stack composed from platform primitives.

    ``status`` progresses from Pending through Provisioning and Wiring to
    Running once all constituent resources are ready. A rollback leaves the
    stack in RollingBack and then Failed if any resource cannot be cleaned up.
    ``endpoint_url`` is set once the stack's primary app service is reachable.
    ``estimated_monthly_cost`` reflects the accepted cost at launch time.
    ``source_template_id`` and ``source_publisher_org_id`` are set when the
    stack was launched from a marketplace custom template rather than a
    first-party template.
    """

    id: str
    name: str
    template_name: str
    template_version: str
    status: str
    created_at: str
    updated_at: str
    status_detail: Optional[str] = None
    endpoint_url: Optional[str] = None
    estimated_monthly_cost: Optional[float] = None
    organization_id: Optional[str] = None
    template_id: Optional[str] = None
    source_template_id: Optional[str] = None
    source_publisher_org_id: Optional[str] = None
    resources: List[StackResource] = field(default_factory=list)
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Stack":
        return cls(
            id=d.get("id", ""),
            name=d.get("name", ""),
            template_name=d.get("template_name", ""),
            template_version=d.get("template_version", ""),
            status=d.get("status", ""),
            created_at=d.get("created_at", ""),
            updated_at=d.get("updated_at", ""),
            status_detail=d.get("status_detail"),
            endpoint_url=d.get("endpoint_url"),
            estimated_monthly_cost=d.get("estimated_monthly_cost"),
            organization_id=d.get("organization_id"),
            template_id=d.get("template_id"),
            source_template_id=d.get("source_template_id"),
            source_publisher_org_id=d.get("source_publisher_org_id"),
            resources=[StackResource.from_dict(r) for r in d.get("resources", [])],
            raw=d,
        )


# ---- Error types ----

class FoundryDBError(Exception):
    """Raised when the FoundryDB API returns a non-2xx response."""

    def __init__(self, message: str, status_code: int, body: Dict[str, Any]) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.body = body

    def __repr__(self) -> str:
        return f"FoundryDBError(status_code={self.status_code}, message={str(self)!r})"
