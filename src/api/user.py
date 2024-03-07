from fastapi import APIRouter, Depends, HTTPException
from starlette.background import BackgroundTasks

from api.schema.user.user_create_otp_dto import CreateOTPRequest
from api.schema.user.user_login_dto import LoginRequest, LoginResponse
from api.schema.user.user_schema import UserSchema
from api.schema.user.user_sign_up_dto import SignUpRequest
from api.schema.user.user_verify_otp_dto import VerifyOTPRequest
from cache import redis_client
from domain.user import User
from repository.user import UserRepository
from security.security import get_authenticated_user
from service.user import UserService

router = APIRouter(prefix="/users")


@router.post("/sign-up", status_code=201)
def user_sign_up_handler(
        request: SignUpRequest,
        user_service: UserService = Depends(),
        user_repo: UserRepository = Depends(),
) -> UserSchema:
    password = user_service.hash_password(plain_password=request.password)

    user = User.create(username=request.username, password=password)

    user = user_repo.save_user(user)

    return UserSchema.from_orm(user)


@router.post("/log-in")
def user_log_in_handler(
        request: LoginRequest,
        user_service: UserService = Depends(),
        user_repo: UserRepository = Depends(),
) -> LoginResponse:
    user = user_repo.get_user_by_username(username=request.username)

    if not user:
        raise HTTPException(status_code=404, detail="User Not Found")

    verified = user_service.verify_password(
        plain_password=request.password,
        hashed_password=user.password
    )

    if not verified:
        raise HTTPException(status_code=401, detail="Not Authorized")

    jwt = user_service.create_jwt(username=user.username)

    return LoginResponse(access_token=jwt)


@router.post("/email/otp")
def create_otp_handler(
        request: CreateOTPRequest,
        _: str = Depends(get_authenticated_user),
        user_service: UserService = Depends(),
):
    otp = user_service.create_otp()

    redis_client.set(request.email, otp)
    redis_client.expire(request.email, 3 * 60)

    return {"otp": otp}


@router.post("/email/otp/verify")
def verify_otp_handler(
        request: VerifyOTPRequest,
        background_tasks: BackgroundTasks,
        access_token: str = Depends(get_authenticated_user),
        user_service: UserService = Depends(),
        user_repo: UserRepository = Depends(),
):
    otp: str | None = redis_client.get(request.email)

    if otp is None:
        raise HTTPException(status_code=400, detail="Bad Request")
    elif request.otp != int(otp):
        raise HTTPException(status_code=400, detail="Bad Request")

    username: str = user_service.decode_jwt(access_token=access_token)

    user = user_repo.get_user_by_username(username)

    if not user:
        raise HTTPException(status_code=404, detail="User Not Found")

    # save email to user
    background_tasks.add_task(
        user_service.send_email_to_user,
        email="admin@fastapi.com"
    )

    return UserSchema.from_orm(user)
