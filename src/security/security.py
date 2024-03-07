from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from domain.user import User
from repository.user import UserRepository
from service.user import UserService


def get_authenticated_user(
        auth_header: HTTPAuthorizationCredentials | None = Depends(HTTPBearer(auto_error=False)),
        user_service: UserService = Depends(UserService),
        user_repo: UserRepository = Depends(UserRepository)
) -> User:
    if auth_header is None:
        raise HTTPException(
            status_code=401,
            detail="Not Authorized"
        )

    username: str = user_service.decode_jwt(access_token=auth_header.credentials)

    user = user_repo.get_user_by_username(username)

    if not user:
        raise HTTPException(status_code=401, detail="Not Authorized")

    return user
