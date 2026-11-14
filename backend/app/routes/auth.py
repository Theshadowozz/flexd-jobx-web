from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.configs.database import get_db
from app.configs.dependencies import current_user
from app.controllers import auth_controller
from app.models.user import User
from app.schemas.auth import Login, PasswordChange, TokenResponse
from app.schemas.response import EmptyResponse
from app.schemas.user import UserDetailResponse
from app.services.auth_service import check_rate_limit

router = APIRouter(prefix="/auth", tags=["Auth"])


def login_limit(request: Request) -> None:
    check_rate_limit(request.client.host if request.client else "unknown")


@router.post("/login", response_model=TokenResponse, dependencies=[Depends(login_limit)])
def login(payload: Login, db: Session = Depends(get_db)) -> TokenResponse:
    return auth_controller.login(payload=payload, db=db)


@router.get("/me", response_model=UserDetailResponse)
def me(user: User = Depends(current_user)) -> UserDetailResponse:
    return auth_controller.me(user=user)


@router.patch("/password", response_model=EmptyResponse)
def password(
    payload: PasswordChange, db: Session = Depends(get_db), user: User = Depends(current_user)
) -> EmptyResponse:
    return auth_controller.password(payload=payload, db=db, user=user)
