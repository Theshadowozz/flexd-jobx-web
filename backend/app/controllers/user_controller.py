from sqlalchemy.orm import Session

from app.schemas.response import EmptyResponse, Pagination
from app.schemas.user import (
    AccountStatus,
    AccountType,
    UserCreate,
    UserDetailData,
    UserDetailResponse,
    UserListData,
    UserListResponse,
    UserRead,
    UserUpdate,
)
from app.services import user_service


def create_user(db: Session, payload: UserCreate) -> UserDetailResponse:
    user = user_service.create_user(db=db, payload=payload)
    user_data = UserRead.model_validate(user)
    return UserDetailResponse(
        message={"success": "Data berhasil dibuat"}, data=UserDetailData(user=user_data)
    )


def get_user(db: Session, user_id: int) -> UserDetailResponse:
    user = user_service.get_user(db=db, user_id=user_id)
    user_data = UserRead.model_validate(user)
    return UserDetailResponse(
        message={"success": "Data berhasil diambil"}, data=UserDetailData(user=user_data)
    )


def update_user(db: Session, user_id: int, payload: UserUpdate) -> UserDetailResponse:
    user = user_service.update_user(db=db, user_id=user_id, payload=payload)
    user_data = UserRead.model_validate(user)
    return UserDetailResponse(
        message={"success": "Data berhasil diperbarui"}, data=UserDetailData(user=user_data)
    )


def list_users(
    db: Session,
    offset: int,
    limit: int,
    account_type: AccountType | None = None,
    account_status: AccountStatus | None = None,
    search: str | None = None,
) -> UserListResponse:
    records, total = user_service.list_users(
        db=db,
        offset=offset,
        limit=limit,
        account_type=account_type,
        account_status=account_status,
        search=search,
    )
    items = [UserRead.model_validate(record) for record in records]
    return UserListResponse(
        message={"success": "Daftar data berhasil diambil"},
        data=UserListData(
            users=items, pagination=Pagination(offset=offset, limit=limit, total=total)
        ),
    )


def delete_user(db: Session, user_id: int) -> EmptyResponse:
    user_service.delete_user(db=db, user_id=user_id)
    return EmptyResponse(message={"success": "Data berhasil dihapus"}, data={})
