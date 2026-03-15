from fastapi import Depends

from app.api.dependencies.dependencies import get_current_user_service
from app.services.current_user_service import CurrentUserService, oauth2_scheme


def get_current_user(
        token: str = Depends(oauth2_scheme),
        service: CurrentUserService = Depends(get_current_user_service),
):
    return service.get_current_user(token)
