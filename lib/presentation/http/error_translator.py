from fastapi import HTTPException, status

from application.errors import ForbiddenError, IntegrationError, ProfileError, ProfileNotFoundError, UnauthorizedError


class ErrorTranslator:
    @staticmethod
    def raise_http_error(exc: ProfileError) -> None:
        if isinstance(exc, UnauthorizedError):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
        if isinstance(exc, ForbiddenError):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
        if isinstance(exc, ProfileNotFoundError):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        if isinstance(exc, IntegrationError):
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
