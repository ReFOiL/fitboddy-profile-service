from domain.entities import ClientProfile  # type: ignore[import-not-found]
from presentation.http.schemas import ProfileResponse  # type: ignore[import-not-found]


class ProfileResponseFactory:
    @staticmethod
    def from_domain(profile: ClientProfile) -> ProfileResponse:
        return ProfileResponse(
            profile_id=profile.profile_id,
            tenant_id=profile.tenant_id,
            user_id=profile.user_id,
            full_name=profile.full_name,
            avatar_url=profile.avatar_url,
            city=profile.city,
            bio=profile.bio,
            goal=profile.goal,
            experience_level=profile.experience_level,
            workout_location=profile.workout_location,
            equipment=profile.equipment,
            limitations=profile.limitations,
            medical_notes=profile.medical_notes,
            created_at=profile.created_at,
            updated_at=profile.updated_at,
        )
