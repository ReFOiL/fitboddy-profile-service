from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from application.commands import GetProfileCommand, UpsertProfileCommand
from application.errors import ForbiddenError, ProfileError, ProfileNotFoundError
from application.gateways import AuthGateway, TenantGateway
from application.repositories import ClientProfileMapper, ClientProfileRepository
from domain.entities import ClientProfile


@dataclass(frozen=True)
class AccessContext:
    user_id: str
    tenant_id: str
    role: str


class ProfileAccessService:
    def __init__(self, auth_gateway: AuthGateway, tenant_gateway: TenantGateway) -> None:
        self._auth_gateway = auth_gateway
        self._tenant_gateway = tenant_gateway

    def authorize_profile_access(self, access_token: str, target_user_id: str) -> AccessContext:
        user = self._auth_gateway.get_current_user(access_token)
        actor_profile = self._tenant_gateway.get_profile_access(user.user_id, ["trainer", "client"])
        if not actor_profile.exists:
            raise ForbiddenError("actor profile not found in marketplace")

        actor_role = actor_profile.role or user.role
        if actor_role == "client":
            if user.user_id != target_user_id:
                raise ForbiddenError("client can access only own profile")
            return AccessContext(user_id=user.user_id, tenant_id=user.tenant_id, role=actor_role)

        if actor_role == "trainer":
            if user.user_id == target_user_id:
                return AccessContext(user_id=user.user_id, tenant_id=user.tenant_id, role=actor_role)
            if not self._tenant_gateway.has_active_relation(user.user_id, target_user_id):
                raise ForbiddenError("trainer can access only active clients")
            return AccessContext(user_id=user.user_id, tenant_id=user.tenant_id, role=actor_role)

        raise ForbiddenError("unsupported actor role")


class ProfileService:
    _PROFILE_TENANT_SCOPE = "marketplace"
    def __init__(self, session: Session) -> None:
        self._session = session
        self._profiles = ClientProfileRepository(session)
        self._mapper = ClientProfileMapper()

    def upsert_profile(self, command: UpsertProfileCommand) -> ClientProfile:
        self._ensure_write_access(command.acting_user_id, command.acting_role, command.user_id)
        self._validate_questionnaire(command)
        model = self._profiles.upsert(
            tenant_id=self._PROFILE_TENANT_SCOPE,
            user_id=command.user_id,
            full_name=command.full_name,
            city=command.city,
            bio=command.bio,
            goal=command.goal,
            experience_level=command.experience_level,
            workout_location=command.workout_location,
            equipment=command.equipment,
            limitations=command.limitations,
            medical_notes=command.medical_notes,
        )
        self._session.commit()
        return self._mapper.to_domain(model)

    def get_profile(self, command: GetProfileCommand) -> ClientProfile:
        self._ensure_read_access(command.acting_user_id, command.acting_role, command.user_id)
        model = self._profiles.find_by_tenant_user(self._PROFILE_TENANT_SCOPE, command.user_id)
        if model is None:
            raise ProfileNotFoundError("profile not found")
        return self._mapper.to_domain(model)

    def has_completed_questionnaire(self, user_id: str) -> bool:
        return self._profiles.has_completed_questionnaire(self._PROFILE_TENANT_SCOPE, user_id)

    def set_avatar_url(self, user_id: str, acting_user_id: str, acting_role: str, avatar_url: str) -> ClientProfile:
        self._ensure_write_access(acting_user_id, acting_role, user_id)
        model = self._profiles.set_avatar_url(self._PROFILE_TENANT_SCOPE, user_id, avatar_url)
        self._session.commit()
        return self._mapper.to_domain(model)

    def get_profile_name_summaries(self, user_ids: list[str]) -> dict[str, str | None]:
        normalized_ids = [item.strip() for item in user_ids if item.strip()]
        unique_ids = list(dict.fromkeys(normalized_ids))
        if not unique_ids:
            return {}
        return self._profiles.get_full_names_by_user_ids(self._PROFILE_TENANT_SCOPE, unique_ids)

    @staticmethod
    def _ensure_write_access(acting_user_id: str, acting_role: str, target_user_id: str) -> None:
        if acting_role == "client" and acting_user_id != target_user_id:
            raise ForbiddenError("client can update only own profile")

    @staticmethod
    def _ensure_read_access(acting_user_id: str, acting_role: str, target_user_id: str) -> None:
        if acting_role == "client" and acting_user_id != target_user_id:
            raise ForbiddenError("client can read only own profile")

    @staticmethod
    def _validate_questionnaire(command: UpsertProfileCommand) -> None:
        # Trainer can keep personal profile without client questionnaire fields.
        is_trainer_own_profile = command.acting_role == "trainer" and command.acting_user_id == command.user_id
        if is_trainer_own_profile:
            return
        if not (command.goal or "").strip():
            raise ProfileError("goal is required for client questionnaire")
        if not (command.experience_level or "").strip():
            raise ProfileError("experience_level is required for client questionnaire")
        if not (command.workout_location or "").strip():
            raise ProfileError("workout_location is required for client questionnaire")
