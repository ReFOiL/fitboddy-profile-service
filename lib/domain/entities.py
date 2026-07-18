from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ClientProfile:
    profile_id: str
    tenant_id: str
    user_id: str
    full_name: str | None
    avatar_url: str | None
    city: str | None
    bio: str | None
    age: int | None
    gender: str | None
    goal: str | None
    experience_level: str | None
    workout_location: str | None
    unavailable_equipment: list[str]
    limitations: str | None
    medical_notes: str | None
    created_at: datetime
    updated_at: datetime
