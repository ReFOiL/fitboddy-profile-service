from __future__ import annotations

import json
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from application.models import ClientProfileModel
from domain.entities import ClientProfile
from domain.equipment import normalize_equipment_list


class ClientProfileRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def upsert(
        self,
        *,
        tenant_id: str,
        user_id: str,
        full_name: str | None,
        city: str | None,
        bio: str | None,
        goal: str | None,
        experience_level: str | None,
        workout_location: str | None,
        unavailable_equipment: list[str],
        limitations: str | None,
        medical_notes: str | None,
    ) -> ClientProfileModel:
        profile = self.find_by_tenant_user(tenant_id, user_id)
        now = datetime.now(UTC).replace(tzinfo=None)
        normalized_goal = (goal or "").strip()
        normalized_experience_level = (experience_level or "").strip()
        normalized_workout_location = (workout_location or "").strip()
        unavailable_json = json.dumps(normalize_equipment_list(unavailable_equipment))
        if profile is None:
            profile = ClientProfileModel(
                profile_id=str(uuid4()),
                tenant_id=tenant_id,
                user_id=user_id,
                full_name=full_name,
                city=city,
                bio=bio,
                goal=normalized_goal,
                experience_level=normalized_experience_level,
                workout_location=normalized_workout_location,
                unavailable_equipment_json=unavailable_json,
                limitations=limitations,
                medical_notes=medical_notes,
                created_at=now,
                updated_at=now,
            )
            self._session.add(profile)
            self._session.flush()
            return profile

        profile.goal = normalized_goal
        profile.experience_level = normalized_experience_level
        profile.workout_location = normalized_workout_location
        profile.full_name = full_name
        profile.city = city
        profile.bio = bio
        profile.unavailable_equipment_json = unavailable_json
        profile.limitations = limitations
        profile.medical_notes = medical_notes
        profile.updated_at = now
        self._session.flush()
        return profile

    def find_by_tenant_user(self, tenant_id: str, user_id: str) -> ClientProfileModel | None:
        return (
            self._session.query(ClientProfileModel)
            .filter(ClientProfileModel.tenant_id == tenant_id, ClientProfileModel.user_id == user_id)
            .one_or_none()
        )

    def has_completed_questionnaire(self, tenant_id: str, user_id: str) -> bool:
        profile = self.find_by_tenant_user(tenant_id, user_id)
        if profile is None:
            return False
        return (
            bool((profile.goal or "").strip())
            and bool((profile.experience_level or "").strip())
            and bool((profile.workout_location or "").strip())
        )

    def get_full_names_by_user_ids(self, tenant_id: str, user_ids: list[str]) -> dict[str, str | None]:
        if not user_ids:
            return {}
        statement = (
            select(ClientProfileModel.user_id, ClientProfileModel.full_name)
            .where(ClientProfileModel.tenant_id == tenant_id, ClientProfileModel.user_id.in_(user_ids))
        )
        rows = self._session.execute(statement).all()
        return {user_id: full_name for user_id, full_name in rows}

    def set_avatar_url(self, tenant_id: str, user_id: str, avatar_url: str) -> ClientProfileModel:
        profile = self.find_by_tenant_user(tenant_id, user_id)
        now = datetime.now(UTC).replace(tzinfo=None)
        if profile is None:
            profile = ClientProfileModel(
                profile_id=str(uuid4()),
                tenant_id=tenant_id,
                user_id=user_id,
                full_name=None,
                avatar_url=avatar_url,
                city=None,
                bio=None,
                goal="",
                experience_level="",
                workout_location="",
                unavailable_equipment_json="[]",
                limitations=None,
                medical_notes=None,
                created_at=now,
                updated_at=now,
            )
            self._session.add(profile)
            self._session.flush()
            return profile
        profile.avatar_url = avatar_url
        profile.updated_at = now
        self._session.flush()
        return profile


class ClientProfileMapper:
    @staticmethod
    def to_domain(model: ClientProfileModel) -> ClientProfile:
        try:
            unavailable = json.loads(model.unavailable_equipment_json or "[]")
        except json.JSONDecodeError:
            unavailable = []
        if not isinstance(unavailable, list):
            unavailable = []
        return ClientProfile(
            profile_id=model.profile_id,
            tenant_id=model.tenant_id,
            user_id=model.user_id,
            full_name=model.full_name,
            avatar_url=model.avatar_url,
            city=model.city,
            bio=model.bio,
            goal=model.goal if model.goal.strip() else None,
            experience_level=model.experience_level if model.experience_level.strip() else None,
            workout_location=model.workout_location if model.workout_location.strip() else None,
            unavailable_equipment=normalize_equipment_list([str(item) for item in unavailable]),
            limitations=model.limitations,
            medical_notes=model.medical_notes,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
