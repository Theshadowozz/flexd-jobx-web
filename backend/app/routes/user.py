from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app.configs.database import get_db
from app.configs.dependencies import require_admin
from app.controllers import user_controller
from app.schemas.response import EmptyResponse
from app.schemas.user import (
    AccountStatus,
    AccountType,
    UserCreate,
    UserDetailResponse,
    UserListResponse,
    UserUpdate,
)

router = APIRouter(prefix="/users", tags=["Users"], dependencies=[Depends(require_admin)])


@router.post("", response_model=UserDetailResponse, status_code=201)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
) -> UserDetailResponse:
    return user_controller.create_user(db=db, payload=payload)


@router.get("", response_model=UserListResponse, status_code=200)
def list_users(
    db: Session = Depends(get_db),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    account_type: AccountType | None = Query(default=None),
    account_status: AccountStatus | None = Query(default=None),
    search: str | None = Query(default=None, max_length=150),
) -> UserListResponse:
    return user_controller.list_users(
        db=db,
        offset=offset,
        limit=limit,
        account_type=account_type,
        account_status=account_status,
        search=search,
    )


@router.get("/{user_id}", response_model=UserDetailResponse, status_code=200)
def get_user(
    user_id: int = Path(..., gt=0, le=18446744073709551615),
    db: Session = Depends(get_db),
) -> UserDetailResponse:
    return user_controller.get_user(db=db, user_id=user_id)


@router.patch("/{user_id}", response_model=UserDetailResponse, status_code=200)
def update_user(
    payload: UserUpdate,
    user_id: int = Path(..., gt=0, le=18446744073709551615),
    db: Session = Depends(get_db),
) -> UserDetailResponse:
    return user_controller.update_user(db=db, payload=payload, user_id=user_id)


@router.delete("/{user_id}", response_model=EmptyResponse, status_code=200)
def delete_user(
    user_id: int = Path(..., gt=0, le=18446744073709551615),
    db: Session = Depends(get_db),
) -> EmptyResponse:
    return user_controller.delete_user(db=db, user_id=user_id)
