from __future__ import annotations

import json
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from application.models import ClientProfileModel
from domain.entities import ClientProfile


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
        equipment: list[str],
        limitations: str | None,
        medical_notes: str | None,
    ) -> ClientProfileModel:
        profile = self.find_by_tenant_user(tenant_id, user_id)
        now = datetime.now(UTC).replace(tzinfo=None)
        normalized_goal = (goal or "").strip()
        normalized_experience_level = (experience_level or "").strip()
        normalized_workout_location = (workout_location or "").strip()
        normalized_equipment = self._normalize_equipment(equipment)
        equipment_json = json.dumps(normalized_equipment)
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
                equipment_json=equipment_json,
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
        profile.equipment_json = equipment_json
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
                equipment_json="[]",
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

    @staticmethod
    def _normalize_equipment(equipment: list[str]) -> list[str]:
        normalized: list[str] = []
        seen: set[str] = set()
        for item in equipment:
            value = item.strip().lower()
            if not value or value in seen:
                continue
            seen.add(value)
            normalized.append(value)
        return normalized


class ClientProfileMapper:
    @staticmethod
    def to_domain(model: ClientProfileModel) -> ClientProfile:
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
            equipment=json.loads(model.equipment_json),
            limitations=model.limitations,
            medical_notes=model.medical_notes,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

