from contextlib import asynccontextmanager

from fastapi import FastAPI

from application.config import Settings
from application.runtime import ProfileApplicationRuntime
from presentation.http.error_translator import ErrorTranslator
from presentation.http.handlers.profile_handler import ProfileHttpHandler
from presentation.http.request_factory import ProfileRequestFactory
from presentation.http.response_factory import ProfileResponseFactory
from presentation.http.routes.admin_routes import AdminRoutes
from presentation.http.routes.profile_routes import ProfileRoutes
from presentation.http.routes.system_routes import SystemRoutes


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = Settings()
    runtime = ProfileApplicationRuntime(settings=settings)
    app.state.profile_handler = ProfileHttpHandler(
        runtime=runtime,
        request_factory=ProfileRequestFactory(),
        response_factory=ProfileResponseFactory(),
        error_translator=ErrorTranslator(),
    )
    try:
        yield
    finally:
        runtime.shutdown()


app = FastAPI(title="profile-service", version="0.1.0", lifespan=lifespan)
app.include_router(SystemRoutes().router)
app.include_router(ProfileRoutes().router)
app.include_router(AdminRoutes().router)
