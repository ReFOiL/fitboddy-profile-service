from __future__ import annotations

from dataclasses import dataclass

import httpx

from application.errors import IntegrationError, UnauthorizedError


@dataclass(frozen=True)
class AuthUser:
    user_id: str
    tenant_id: str
    role: str


@dataclass(frozen=True)
class ProfileAccessCheckResult:
    exists: bool
    role: str | None


class AuthGateway:
    def __init__(self, http_client: httpx.Client, auth_service_url: str) -> None:
        self._http_client = http_client
        self._auth_service_url = auth_service_url.rstrip("/")

    def get_current_user(self, access_token: str) -> AuthUser:
        try:
            response = self._http_client.get(
                f"{self._auth_service_url}/api/v1/auth/me",
                headers={"Authorization": f"Bearer {access_token}"},
            )
        except httpx.HTTPError as exc:
            raise IntegrationError("auth-service is unavailable") from exc

        if response.status_code == 401:
            raise UnauthorizedError("invalid access token")
        if response.status_code >= 500:
            raise IntegrationError("auth-service returned server error")
        if response.status_code != 200:
            raise IntegrationError("auth-service returned unexpected response")

        payload = response.json()
        return AuthUser(user_id=payload["user_id"], tenant_id=payload["tenant_id"], role=payload["role"])


class TenantGateway:
    def __init__(self, http_client: httpx.Client, tenant_service_url: str) -> None:
        self._http_client = http_client
        self._tenant_service_url = tenant_service_url.rstrip("/")

    def get_profile_access(self, user_id: str, allowed_roles: list[str] | None = None) -> ProfileAccessCheckResult:
        roles = allowed_roles or []
        try:
            response = self._http_client.post(
                f"{self._tenant_service_url}/api/v1/marketplace/profiles/check",
                json={"user_id": user_id, "allowed_roles": roles},
            )
        except httpx.HTTPError as exc:
            raise IntegrationError("tenant-service is unavailable") from exc

        if response.status_code >= 500:
            raise IntegrationError("tenant-service returned server error")
        if response.status_code != 200:
            raise IntegrationError("tenant-service returned unexpected response")

        payload = response.json()
        return ProfileAccessCheckResult(exists=bool(payload.get("exists")), role=payload.get("role"))

    def has_active_relation(self, trainer_user_id: str, client_user_id: str) -> bool:
        try:
            response = self._http_client.get(
                f"{self._tenant_service_url}/api/v1/marketplace/trainers/{trainer_user_id}/clients",
                params={"status": "active"},
            )
        except httpx.HTTPError as exc:
            raise IntegrationError("tenant-service is unavailable") from exc

        if response.status_code >= 500:
            raise IntegrationError("tenant-service returned server error")
        if response.status_code != 200:
            raise IntegrationError("tenant-service returned unexpected response")

        payload = response.json()
        return any(item.get("client_user_id") == client_user_id for item in payload)
