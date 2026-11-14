from sqlalchemy import func, select
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from app.models import CompanyProfile, User
from app.schemas.company_profile import CompanyProfileCreate, CompanyProfileUpdate
from app.utils.database_errors import translate_database_error
from app.utils.exceptions import AppError


def get_company_profile(db: Session, company_profile_id: int) -> CompanyProfile:
    statement = select(CompanyProfile).where(CompanyProfile.id == company_profile_id)
    company_profile = db.scalar(statement)
    if company_profile is None:
        raise AppError(
            status_code=404,
            category="not_found",
            errors={"company_profile": "Data tidak ditemukan"},
        )
    return company_profile


def list_company_profiles(
    db: Session,
    offset: int,
    limit: int,
    user_id: int | None = None,
    industry: str | None = None,
    city: str | None = None,
    province: str | None = None,
) -> tuple[list[CompanyProfile], int]:
    conditions = []
    if user_id is not None:
        conditions.append(CompanyProfile.user_id == user_id)
    if industry is not None:
        conditions.append(CompanyProfile.industry == industry)
    if city is not None:
        conditions.append(CompanyProfile.city == city)
    if province is not None:
        conditions.append(CompanyProfile.province == province)
    total_statement = select(func.count()).select_from(CompanyProfile).where(*conditions)
    total = db.scalar(total_statement) or 0
    statement = (
        select(CompanyProfile)
        .where(*conditions)
        .order_by(CompanyProfile.id)
        .offset(offset)
        .limit(limit)
    )
    records = list(db.scalars(statement).all())
    return (records, total)


def create_company_profile(db: Session, payload: CompanyProfileCreate) -> CompanyProfile:
    try:
        record = None
        values = {
            "name": payload.name,
            "industry": payload.industry,
            "description": payload.description,
            "logo_storage_key": payload.logo_storage_key,
            "city": payload.city,
            "province": payload.province,
            "country": payload.country,
            "user_id": payload.user_id,
        }
        payload.model_dump()
        if values["user_id"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"user_id": "Field tidak boleh null"},
            )
        if values["user_id"] is not None:
            referenced_user_id = db.scalar(
                select(User)
                .where(User.id == values["user_id"])
                .with_for_update(read=True)
                .execution_options(populate_existing=True)
            )
            if referenced_user_id is None:
                raise AppError(
                    status_code=422,
                    category="validation",
                    message="Validasi gagal",
                    errors={"user_id": "Referensi tidak ditemukan"},
                )
        if values["name"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"name": "Field tidak boleh null"},
            )
        if values["country"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"country": "Field tidak boleh null"},
            )
        role_field = ("user_id", "employer")
        if role_field:
            field, role = role_field
            account = db.get(User, values[field])
            if account is None or account.account_type != role:
                raise AppError(
                    status_code=422,
                    category="validation",
                    message="Validasi gagal",
                    errors={field: f"Akun harus memiliki role {role}"},
                )
        record = CompanyProfile(
            name=values["name"],
            industry=values["industry"],
            description=values["description"],
            logo_storage_key=values["logo_storage_key"],
            city=values["city"],
            province=values["province"],
            country=values["country"],
            user_id=values["user_id"],
        )
        db.add(record)
        db.flush()
        db.refresh(record)
        db.commit()
        return record
    except DBAPIError as exc:
        db.rollback()
        translate_database_error(exc, "company_profile")
        raise
    except Exception:
        db.rollback()
        raise


def update_company_profile(
    db: Session, company_profile_id: int, payload: CompanyProfileUpdate
) -> CompanyProfile:
    try:
        statement = (
            select(CompanyProfile)
            .where(CompanyProfile.id == company_profile_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        record = db.scalar(statement)
        if record is None:
            raise AppError(
                status_code=404,
                category="not_found",
                errors={"company_profile": "Data tidak ditemukan"},
            )
        values = {
            "name": payload.name if "name" in payload.model_fields_set else record.name,
            "industry": payload.industry
            if "industry" in payload.model_fields_set
            else record.industry,
            "description": payload.description
            if "description" in payload.model_fields_set
            else record.description,
            "logo_storage_key": payload.logo_storage_key
            if "logo_storage_key" in payload.model_fields_set
            else record.logo_storage_key,
            "city": payload.city if "city" in payload.model_fields_set else record.city,
            "province": payload.province
            if "province" in payload.model_fields_set
            else record.province,
            "country": payload.country if "country" in payload.model_fields_set else record.country,
            "user_id": record.user_id,
        }
        payload.model_dump(exclude_unset=True)
        if values["user_id"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"user_id": "Field tidak boleh null"},
            )
        if values["user_id"] is not None:
            referenced_user_id = db.scalar(
                select(User)
                .where(User.id == values["user_id"])
                .with_for_update(read=True)
                .execution_options(populate_existing=True)
            )
            if referenced_user_id is None:
                raise AppError(
                    status_code=422,
                    category="validation",
                    message="Validasi gagal",
                    errors={"user_id": "Referensi tidak ditemukan"},
                )
        if values["name"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"name": "Field tidak boleh null"},
            )
        if values["country"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"country": "Field tidak boleh null"},
            )
        role_field = ("user_id", "employer")
        if role_field:
            field, role = role_field
            account = db.get(User, values[field])
            if account is None or account.account_type != role:
                raise AppError(
                    status_code=422,
                    category="validation",
                    message="Validasi gagal",
                    errors={field: f"Akun harus memiliki role {role}"},
                )
        if "name" in payload.model_fields_set:
            record.name = values["name"]
        if "industry" in payload.model_fields_set:
            record.industry = values["industry"]
        if "description" in payload.model_fields_set:
            record.description = values["description"]
        if "logo_storage_key" in payload.model_fields_set:
            record.logo_storage_key = values["logo_storage_key"]
        if "city" in payload.model_fields_set:
            record.city = values["city"]
        if "province" in payload.model_fields_set:
            record.province = values["province"]
        if "country" in payload.model_fields_set:
            record.country = values["country"]
        db.flush()
        db.refresh(record)
        db.commit()
        return record
    except DBAPIError as exc:
        db.rollback()
        translate_database_error(exc, "company_profile")
        raise
    except Exception:
        db.rollback()
        raise


def delete_company_profile(db: Session, company_profile_id: int) -> None:
    try:
        statement = (
            select(CompanyProfile)
            .where(CompanyProfile.id == company_profile_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        record = db.scalar(statement)
        if record is None:
            raise AppError(
                status_code=404,
                category="not_found",
                errors={"company_profile": "Data tidak ditemukan"},
            )
        db.delete(record)
        db.commit()
    except DBAPIError as exc:
        db.rollback()
        translate_database_error(exc, "company_profile")
        raise
    except Exception:
        db.rollback()
        raise
