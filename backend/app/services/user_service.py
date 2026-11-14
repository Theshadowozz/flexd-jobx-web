from sqlalchemy import func, or_, select
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from app.models import CandidateProfile, CompanyProfile, JobMatch, JobPost, User
from app.schemas.user import AccountStatus, AccountType, UserCreate, UserUpdate
from app.utils.database_errors import translate_database_error
from app.utils.exceptions import AppError
from app.utils.security import hash_password


def lock_user_accounts(db: Session) -> None:
    db.scalars(
        select(User).order_by(User.id).with_for_update().execution_options(populate_existing=True)
    ).all()


def ensure_active_admin_remains(
    db: Session, record: User, values: dict[str, object] | None = None
) -> None:
    if record.account_type != "admin" or record.account_status != "active":
        return
    if (
        values
        and values.get("account_type") == "admin"
        and (values.get("account_status") == "active")
    ):
        return
    count = db.scalar(
        select(func.count())
        .select_from(User)
        .where(User.account_type == "admin", User.account_status == "active")
    )
    if count <= 1:
        raise AppError(409, "business_rule", {"user": "Admin aktif terakhir harus dipertahankan"})


def get_user(db: Session, user_id: int) -> User:
    statement = select(User).where(User.id == user_id)
    user = db.scalar(statement)
    if user is None:
        raise AppError(
            status_code=404, category="not_found", errors={"user": "Data tidak ditemukan"}
        )
    return user


def list_users(
    db: Session,
    offset: int,
    limit: int,
    account_type: AccountType | None = None,
    account_status: AccountStatus | None = None,
    search: str | None = None,
) -> tuple[list[User], int]:
    conditions = []
    if account_type is not None:
        conditions.append(User.account_type == account_type)
    if account_status is not None:
        conditions.append(User.account_status == account_status)
    if search:
        conditions.append(
            or_(
                User.name.contains(search, autoescape=True),
                User.email.contains(search, autoescape=True),
            )
        )
    total_statement = select(func.count()).select_from(User).where(*conditions)
    total = db.scalar(total_statement) or 0
    statement = select(User).where(*conditions).order_by(User.id).offset(offset).limit(limit)
    records = list(db.scalars(statement).all())
    return (records, total)


def create_user(db: Session, payload: UserCreate) -> User:
    try:
        lock_user_accounts(db)
        record = None
        values = {
            "name": payload.name,
            "email": payload.email,
            "account_type": payload.account_type,
            "account_status": payload.account_status,
        }
        payload.model_dump()
        if values["name"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"name": "Field tidak boleh null"},
            )
        if values["email"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"email": "Field tidak boleh null"},
            )
        if values["account_type"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"account_type": "Field tidak boleh null"},
            )
        if values["account_status"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"account_status": "Field tidak boleh null"},
            )
        if record is not None and values["account_type"] != record.account_type:
            relations = (
                (CandidateProfile, CandidateProfile.user_id),
                (CompanyProfile, CompanyProfile.user_id),
                (JobPost, JobPost.user_id),
                (JobMatch, JobMatch.candidate_user_id),
            )
            if any(
                (
                    db.scalar(select(column).where(column == record.id).limit(1)) is not None
                    for _, column in relations
                )
            ):
                raise AppError(
                    409,
                    "business_rule",
                    {"account_type": "Akun masih memiliki data sesuai role lama"},
                )
        record = User(
            name=values["name"],
            email=values["email"],
            password_hash=hash_password(payload.password.get_secret_value()),
            account_type=values["account_type"],
            account_status=values["account_status"],
        )
        db.add(record)
        db.flush()
        db.refresh(record)
        db.commit()
        return record
    except DBAPIError as exc:
        db.rollback()
        translate_database_error(exc, "user")
        raise
    except Exception:
        db.rollback()
        raise


def update_user(db: Session, user_id: int, payload: UserUpdate) -> User:
    try:
        lock_user_accounts(db)
        statement = (
            select(User)
            .where(User.id == user_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        record = db.scalar(statement)
        if record is None:
            raise AppError(
                status_code=404, category="not_found", errors={"user": "Data tidak ditemukan"}
            )
        values = {
            "name": payload.name if "name" in payload.model_fields_set else record.name,
            "email": payload.email if "email" in payload.model_fields_set else record.email,
            "account_type": payload.account_type
            if "account_type" in payload.model_fields_set
            else record.account_type,
            "account_status": payload.account_status
            if "account_status" in payload.model_fields_set
            else record.account_status,
        }
        ensure_active_admin_remains(db, record, values)
        payload.model_dump(exclude_unset=True)
        if values["name"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"name": "Field tidak boleh null"},
            )
        if values["email"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"email": "Field tidak boleh null"},
            )
        if values["account_type"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"account_type": "Field tidak boleh null"},
            )
        if values["account_status"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"account_status": "Field tidak boleh null"},
            )
        if record is not None and values["account_type"] != record.account_type:
            relations = (
                (CandidateProfile, CandidateProfile.user_id),
                (CompanyProfile, CompanyProfile.user_id),
                (JobPost, JobPost.user_id),
                (JobMatch, JobMatch.candidate_user_id),
            )
            if any(
                (
                    db.scalar(select(column).where(column == record.id).limit(1)) is not None
                    for _, column in relations
                )
            ):
                raise AppError(
                    409,
                    "business_rule",
                    {"account_type": "Akun masih memiliki data sesuai role lama"},
                )
        if "name" in payload.model_fields_set:
            record.name = values["name"]
        if "email" in payload.model_fields_set:
            record.email = values["email"]
        if "account_type" in payload.model_fields_set:
            record.account_type = values["account_type"]
        if "account_status" in payload.model_fields_set:
            record.account_status = values["account_status"]
        db.flush()
        db.refresh(record)
        db.commit()
        return record
    except DBAPIError as exc:
        db.rollback()
        translate_database_error(exc, "user")
        raise
    except Exception:
        db.rollback()
        raise


def delete_user(db: Session, user_id: int) -> None:
    try:
        lock_user_accounts(db)
        statement = (
            select(User)
            .where(User.id == user_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        record = db.scalar(statement)
        if record is None:
            raise AppError(
                status_code=404, category="not_found", errors={"user": "Data tidak ditemukan"}
            )
        ensure_active_admin_remains(db, record)
        db.delete(record)
        db.commit()
    except DBAPIError as exc:
        db.rollback()
        translate_database_error(exc, "user")
        raise
    except Exception:
        db.rollback()
        raise
