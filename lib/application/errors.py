class ProfileError(Exception):
    pass


class UnauthorizedError(ProfileError):
    pass


class ForbiddenError(ProfileError):
    pass


class ProfileNotFoundError(ProfileError):
    pass


class IntegrationError(ProfileError):
    pass
