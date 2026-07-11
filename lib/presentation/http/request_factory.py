from application.commands import GetProfileCommand, UpsertProfileCommand
from presentation.http.schemas import UpsertProfileRequest


class ProfileRequestFactory:
    @staticmethod
    def to_upsert_command(
        user_id: str,
        payload: UpsertProfileRequest,
        acting_user_id: str,
        acting_role: str,
    ) -> UpsertProfileCommand:
        return UpsertProfileCommand(
            user_id=user_id,
            full_name=payload.full_name,
            city=payload.city,
            bio=payload.bio,
            goal=payload.goal,
            experience_level=payload.experience_level,
            workout_location=payload.workout_location,
            unavailable_equipment=list(payload.unavailable_equipment),
            limitations=payload.limitations,
            medical_notes=payload.medical_notes,
            acting_user_id=acting_user_id,
            acting_role=acting_role,
        )

    @staticmethod
    def to_get_command(user_id: str, acting_user_id: str, acting_role: str) -> GetProfileCommand:
        return GetProfileCommand(
            user_id=user_id,
            acting_user_id=acting_user_id,
            acting_role=acting_role,
        )
