from fastapi import APIRouter, File, Header, HTTPException, Request, UploadFile, status

from presentation.http.schemas import (
    AvatarUploadResponse,
    ProfileMetaResponse,
    ProfileNameSummariesRequest,
    ProfileNameSummariesResponse,
    ProfileResponse,
    QuestionnaireStatusResponse,
    UpsertProfileRequest,
)


class ProfileRoutes:
    def __init__(self) -> None:
        self.router = APIRouter(prefix="/api/v1/profiles", tags=["profiles"])
        self.router.add_api_route(
            "/meta",
            self.get_profile_meta,
            methods=["GET"],
            response_model=ProfileMetaResponse,
        )
        self.router.add_api_route(
            "/{user_id}",
            self.upsert_profile,
            methods=["PUT"],
            response_model=ProfileResponse,
        )
        self.router.add_api_route(
            "/{user_id}",
            self.get_profile,
            methods=["GET"],
            response_model=ProfileResponse,
        )
        self.router.add_api_route(
            "/internal/{user_id}/questionnaire-status",
            self.get_questionnaire_status,
            methods=["GET"],
            response_model=QuestionnaireStatusResponse,
        )
        self.router.add_api_route(
            "/internal/summaries",
            self.list_profile_name_summaries,
            methods=["POST"],
            response_model=ProfileNameSummariesResponse,
        )
        self.router.add_api_route(
            "/{user_id}/avatar",
            self.upload_avatar,
            methods=["POST"],
            response_model=AvatarUploadResponse,
        )
        self.router.add_api_route(
            "/media/{object_key:path}",
            self.get_media,
            methods=["GET"],
        )

    @staticmethod
    def upsert_profile(
        request: Request,
        user_id: str,
        payload: UpsertProfileRequest,
        authorization: str | None = Header(default=None),
    ) -> ProfileResponse:
        return request.app.state.profile_handler.upsert_profile(user_id, payload, authorization)

    @staticmethod
    def get_profile(
        request: Request,
        user_id: str,
        authorization: str | None = Header(default=None),
    ) -> ProfileResponse:
        return request.app.state.profile_handler.get_profile(user_id, authorization)

    @staticmethod
    def get_questionnaire_status(request: Request, user_id: str) -> QuestionnaireStatusResponse:
        return request.app.state.profile_handler.get_questionnaire_status(user_id)

    @staticmethod
    def list_profile_name_summaries(
        request: Request,
        payload: ProfileNameSummariesRequest,
    ) -> ProfileNameSummariesResponse:
        return request.app.state.profile_handler.list_profile_name_summaries(payload)

    @staticmethod
    def get_profile_meta(request: Request) -> ProfileMetaResponse:
        return request.app.state.profile_handler.get_profile_meta()

    @staticmethod
    async def upload_avatar(
        request: Request,
        user_id: str,
        file: UploadFile = File(...),
        authorization: str | None = Header(default=None),
    ) -> AvatarUploadResponse:
        if not file.filename:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="filename is required")
        data = await file.read()
        return await request.app.state.profile_handler.upload_avatar(
            user_id=user_id,
            filename=file.filename,
            data=data,
            authorization=authorization,
        )

    @staticmethod
    async def get_media(request: Request, object_key: str):
        return await request.app.state.profile_handler.get_media(object_key)
