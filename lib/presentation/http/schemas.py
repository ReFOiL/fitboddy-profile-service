from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str


ProfileGoal = Literal["weight_loss", "muscle_gain", "endurance", "maintenance", "rehabilitation"]
ProfileLevel = Literal["beginner", "intermediate", "advanced"]
ProfileWorkoutLocation = Literal["home", "gym"]


class UpsertProfileRequest(BaseModel):
    full_name: str | None = Field(default=None, max_length=120)
    city: str | None = Field(default=None, max_length=120)
    bio: str | None = Field(default=None, max_length=2000)
    goal: ProfileGoal | None = Field(default=None)
    experience_level: ProfileLevel | None = Field(default=None)
    workout_location: ProfileWorkoutLocation | None = Field(default=None)
    unavailable_equipment: list[str] = Field(default_factory=list)
    limitations: str | None = Field(default=None, max_length=1000)
    medical_notes: str | None = Field(default=None, max_length=1000)


class ProfileResponse(BaseModel):
    profile_id: str
    tenant_id: str
    user_id: str
    full_name: str | None
    avatar_url: str | None
    city: str | None
    bio: str | None
    goal: str | None
    experience_level: str | None
    workout_location: str | None
    unavailable_equipment: list[str]
    limitations: str | None
    medical_notes: str | None
    created_at: datetime
    updated_at: datetime


class QuestionnaireStatusResponse(BaseModel):
    user_id: str
    is_completed: bool


class AvatarUploadResponse(BaseModel):
    user_id: str
    avatar_url: str


class ProfileMetaOption(BaseModel):
    value: str
    label: str


class ProfileMetaResponse(BaseModel):
    goals: list[ProfileMetaOption]
    levels: list[ProfileMetaOption]
    workout_locations: list[ProfileMetaOption]
    equipment: list[ProfileMetaOption]


class ProfileNameSummariesRequest(BaseModel):
    user_ids: list[str] = Field(default_factory=list, max_length=500)


class ProfileNameSummaryItem(BaseModel):
    user_id: str
    full_name: str | None


class ProfileNameSummariesResponse(BaseModel):
    items: list[ProfileNameSummaryItem]


class AdminProfileListResponse(BaseModel):
    items: list[ProfileResponse] = Field(default_factory=list)
    total: int
    page: int
    page_size: int
