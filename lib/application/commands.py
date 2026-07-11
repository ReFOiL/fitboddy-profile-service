from dataclasses import dataclass


@dataclass(frozen=True)
class UpsertProfileCommand:
    user_id: str
    full_name: str | None
    city: str | None
    bio: str | None
    goal: str | None
    experience_level: str | None
    workout_location: str | None
    unavailable_equipment: list[str]
    limitations: str | None
    medical_notes: str | None
    acting_user_id: str
    acting_role: str


@dataclass(frozen=True)
class GetProfileCommand:
    user_id: str
    acting_user_id: str
    acting_role: str
