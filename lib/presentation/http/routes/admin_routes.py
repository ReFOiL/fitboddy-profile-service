from fastapi import APIRouter, Header, Query, Request

from presentation.http.schemas import AdminProfileListResponse, ProfileResponse, UpsertProfileRequest


class AdminRoutes:
    def __init__(self) -> None:
        self.router = APIRouter(prefix="/api/v1/admin/profiles", tags=["admin"])
        self.router.add_api_route("", self.list_profiles, methods=["GET"], response_model=AdminProfileListResponse)
        self.router.add_api_route("/{user_id}", self.get_profile, methods=["GET"], response_model=ProfileResponse)
        self.router.add_api_route("/{user_id}", self.upsert_profile, methods=["PUT"], response_model=ProfileResponse)

    def list_profiles(
        self,
        request: Request,
        authorization: str | None = Header(default=None, alias="Authorization"),
        q: str | None = Query(default=None),
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=20, ge=1, le=100),
    ) -> AdminProfileListResponse:
        return request.app.state.profile_handler.admin_list_profiles(
            authorization=authorization,
            query=q,
            page=page,
            page_size=page_size,
        )

    def get_profile(
        self,
        user_id: str,
        request: Request,
        authorization: str | None = Header(default=None, alias="Authorization"),
    ) -> ProfileResponse:
        return request.app.state.profile_handler.admin_get_profile(authorization=authorization, user_id=user_id)

    def upsert_profile(
        self,
        user_id: str,
        payload: UpsertProfileRequest,
        request: Request,
        authorization: str | None = Header(default=None, alias="Authorization"),
    ) -> ProfileResponse:
        return request.app.state.profile_handler.admin_upsert_profile(
            authorization=authorization,
            user_id=user_id,
            payload=payload,
        )
