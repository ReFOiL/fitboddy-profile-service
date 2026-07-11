from urllib.parse import quote

from fastapi import HTTPException, Response, status

from application.errors import IntegrationError, ProfileError, UnauthorizedError
from application.media_storage import MediaValidationError
from application.runtime import ProfileApplicationRuntime
from presentation.http.error_translator import ErrorTranslator
from presentation.http.request_factory import ProfileRequestFactory
from presentation.http.response_factory import ProfileResponseFactory
from presentation.http.schemas import (
    AvatarUploadResponse,
    ProfileMetaOption,
    ProfileMetaResponse,
    ProfileNameSummariesRequest,
    ProfileNameSummariesResponse,
    ProfileNameSummaryItem,
    ProfileResponse,
    QuestionnaireStatusResponse,
    UpsertProfileRequest,
)


class ProfileHttpHandler:
    def __init__(
        self,
        runtime: ProfileApplicationRuntime,
        request_factory: ProfileRequestFactory,
        response_factory: ProfileResponseFactory,
        error_translator: ErrorTranslator,
    ) -> None:
        self._runtime = runtime
        self._request_factory = request_factory
        self._response_factory = response_factory
        self._error_translator = error_translator
        self._access_service = runtime.access_service

    def health(self) -> dict[str, str]:
        return {"status": "ok"}

    def ready(self) -> dict[str, str]:
        self._runtime.check_ready()
        return {"status": "ready"}

    def upsert_profile(
        self, user_id: str, payload: UpsertProfileRequest, authorization: str | None
    ) -> ProfileResponse:
        try:
            access_token = self._extract_bearer_token(authorization)
            access_context = self._access_service.authorize_profile_access(access_token, user_id)
            with self._runtime.profile_service_scope() as profile_service:
                profile = profile_service.upsert_profile(
                    self._request_factory.to_upsert_command(
                        user_id=user_id,
                        payload=payload,
                        acting_user_id=access_context.user_id,
                        acting_role=access_context.role,
                    )
                )
                return self._response_factory.from_domain(profile)
        except ProfileError as exc:
            self._error_translator.raise_http_error(exc)
        raise AssertionError("unreachable")

    def get_profile(self, user_id: str, authorization: str | None) -> ProfileResponse:
        try:
            access_token = self._extract_bearer_token(authorization)
            access_context = self._access_service.authorize_profile_access(access_token, user_id)
            with self._runtime.profile_service_scope() as profile_service:
                profile = profile_service.get_profile(
                    self._request_factory.to_get_command(
                        user_id=user_id,
                        acting_user_id=access_context.user_id,
                        acting_role=access_context.role,
                    )
                )
                return self._response_factory.from_domain(profile)
        except ProfileError as exc:
            self._error_translator.raise_http_error(exc)
        raise AssertionError("unreachable")

    def get_questionnaire_status(self, user_id: str) -> QuestionnaireStatusResponse:
        try:
            with self._runtime.profile_service_scope() as profile_service:
                return QuestionnaireStatusResponse(
                    user_id=user_id,
                    is_completed=profile_service.has_completed_questionnaire(user_id),
                )
        except ProfileError as exc:
            self._error_translator.raise_http_error(exc)
        raise AssertionError("unreachable")

    @staticmethod
    def get_profile_meta() -> ProfileMetaResponse:
        return ProfileMetaResponse(
            goals=[
                ProfileMetaOption(value="weight_loss", label="Снижение веса"),
                ProfileMetaOption(value="muscle_gain", label="Набор мышечной массы"),
                ProfileMetaOption(value="endurance", label="Выносливость"),
                ProfileMetaOption(value="maintenance", label="Поддержание формы"),
                ProfileMetaOption(value="rehabilitation", label="Реабилитация"),
            ],
            levels=[
                ProfileMetaOption(value="beginner", label="Начальный"),
                ProfileMetaOption(value="intermediate", label="Средний"),
                ProfileMetaOption(value="advanced", label="Продвинутый"),
            ],
            workout_locations=[
                ProfileMetaOption(value="home", label="Дом"),
                ProfileMetaOption(value="gym", label="Зал"),
            ],
            equipment=[
                ProfileMetaOption(value="dumbbells", label="Гантели"),
                ProfileMetaOption(value="barbell", label="Штанга"),
                ProfileMetaOption(value="resistance_bands", label="Эспандеры / резинки"),
                ProfileMetaOption(value="kettlebell", label="Гиря"),
                ProfileMetaOption(value="treadmill", label="Беговая дорожка"),
            ],
        )

    async def upload_avatar(self, user_id: str, filename: str, data: bytes, authorization: str | None) -> AvatarUploadResponse:
        try:
            access_token = self._extract_bearer_token(authorization)
            access_context = self._access_service.authorize_profile_access(access_token, user_id)
            storage = self._runtime.avatar_storage
            if storage is None:
                raise IntegrationError("s3 media storage is not configured")
            object_key = await storage.upload_avatar(user_id=user_id, filename=filename, data=data)
            avatar_url = f"/api/v1/profiles/media/{quote(object_key, safe='/')}"
            with self._runtime.profile_service_scope() as profile_service:
                profile_service.set_avatar_url(
                    user_id=user_id,
                    acting_user_id=access_context.user_id,
                    acting_role=access_context.role,
                    avatar_url=avatar_url,
                )
            return AvatarUploadResponse(user_id=user_id, avatar_url=avatar_url)
        except MediaValidationError as exc:
            self._error_translator.raise_http_error(ProfileError(str(exc)))
        except ProfileError as exc:
            self._error_translator.raise_http_error(exc)
        raise AssertionError("unreachable")

    async def get_media(self, object_key: str) -> Response:
        storage = self._runtime.avatar_storage
        if storage is None:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="s3 media storage is not configured")
        try:
            data, content_type = await storage.download_media(object_key)
            return Response(content=data, media_type=content_type)
        except ProfileError as exc:
            self._error_translator.raise_http_error(exc)
        except Exception as exc:  # pragma: no cover
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="media not found") from exc
        raise AssertionError("unreachable")

    def list_profile_name_summaries(self, payload: ProfileNameSummariesRequest) -> ProfileNameSummariesResponse:
        try:
            with self._runtime.profile_service_scope() as profile_service:
                names_map = profile_service.get_profile_name_summaries(payload.user_ids)
                items = [ProfileNameSummaryItem(user_id=user_id, full_name=names_map.get(user_id)) for user_id in payload.user_ids]
                return ProfileNameSummariesResponse(items=items)
        except ProfileError as exc:
            self._error_translator.raise_http_error(exc)
        raise AssertionError("unreachable")

    @staticmethod
    def _extract_bearer_token(authorization: str | None) -> str:
        if authorization is None or not authorization.startswith("Bearer "):
            raise UnauthorizedError("missing bearer token")
        token = authorization.removeprefix("Bearer ").strip()
        if not token:
            raise UnauthorizedError("empty bearer token")
        return token
