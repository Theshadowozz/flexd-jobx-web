from sqlalchemy import func, select
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from app.models import CandidateProfile, User
from app.schemas import candidate_profile as schema
from app.schemas.candidate_profile import CandidateProfileCreate, CandidateProfileUpdate
from app.utils.database_errors import translate_database_error
from app.utils.exceptions import AppError


def get_candidate_profile(db: Session, user_id: int) -> CandidateProfile:
    statement = select(CandidateProfile).where(CandidateProfile.user_id == user_id)
    candidate_profile = db.scalar(statement)
    if candidate_profile is None:
        raise AppError(
            status_code=404,
            category="not_found",
            errors={"candidate_profile": "Data tidak ditemukan"},
        )
    return candidate_profile


def list_candidate_profiles(
    db: Session,
    offset: int,
    limit: int,
    city: str | None = None,
    province: str | None = None,
    preferred_employment_type: schema.EmploymentPreference | None = None,
    preferred_work_mode: schema.WorkPreference | None = None,
    profile_visibility: schema.ProfileVisibility | None = None,
) -> tuple[list[CandidateProfile], int]:
    conditions = []
    if city is not None:
        conditions.append(CandidateProfile.city == city)
    if province is not None:
        conditions.append(CandidateProfile.province == province)
    if preferred_employment_type is not None:
        conditions.append(CandidateProfile.preferred_employment_type == preferred_employment_type)
    if preferred_work_mode is not None:
        conditions.append(CandidateProfile.preferred_work_mode == preferred_work_mode)
    if profile_visibility is not None:
        conditions.append(CandidateProfile.profile_visibility == profile_visibility)
    total_statement = select(func.count()).select_from(CandidateProfile).where(*conditions)
    total = db.scalar(total_statement) or 0
    statement = (
        select(CandidateProfile)
        .where(*conditions)
        .order_by(CandidateProfile.user_id)
        .offset(offset)
        .limit(limit)
    )
    records = list(db.scalars(statement).all())
    return (records, total)


def create_candidate_profile(db: Session, payload: CandidateProfileCreate) -> CandidateProfile:
    try:
        record = None
        values = {
            "headline": payload.headline,
            "biography": payload.biography,
            "city": payload.city,
            "province": payload.province,
            "country": payload.country,
            "years_experience": payload.years_experience,
            "preferred_employment_type": payload.preferred_employment_type,
            "preferred_work_mode": payload.preferred_work_mode,
            "expected_salary_min": payload.expected_salary_min,
            "expected_salary_max": payload.expected_salary_max,
            "available_from": payload.available_from,
            "profile_visibility": payload.profile_visibility,
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
        if values["country"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"country": "Field tidak boleh null"},
            )
        if values["preferred_employment_type"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"preferred_employment_type": "Field tidak boleh null"},
            )
        if values["preferred_work_mode"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"preferred_work_mode": "Field tidak boleh null"},
            )
        if values["profile_visibility"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"profile_visibility": "Field tidak boleh null"},
            )
        role_field = ("user_id", "candidate")
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
        for low, high in (("expected_salary_min", "expected_salary_max"),):
            if (
                values.get(low) is not None
                and values.get(high) is not None
                and (values[low] > values[high])
            ):
                raise AppError(
                    status_code=422,
                    category="validation",
                    message="Validasi gagal",
                    errors={high: "Nilai akhir tidak boleh lebih kecil dari nilai awal"},
                )
        record = CandidateProfile(
            headline=values["headline"],
            biography=values["biography"],
            city=values["city"],
            province=values["province"],
            country=values["country"],
            years_experience=values["years_experience"],
            preferred_employment_type=values["preferred_employment_type"],
            preferred_work_mode=values["preferred_work_mode"],
            expected_salary_min=values["expected_salary_min"],
            expected_salary_max=values["expected_salary_max"],
            available_from=values["available_from"],
            profile_visibility=values["profile_visibility"],
            user_id=values["user_id"],
        )
        db.add(record)
        db.flush()
        db.refresh(record)
        db.commit()
        return record
    except DBAPIError as exc:
        db.rollback()
        translate_database_error(exc, "candidate_profile")
        raise
    except Exception:
        db.rollback()
        raise


def update_candidate_profile(
    db: Session, user_id: int, payload: CandidateProfileUpdate
) -> CandidateProfile:
    try:
        statement = (
            select(CandidateProfile)
            .where(CandidateProfile.user_id == user_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        record = db.scalar(statement)
        if record is None:
            raise AppError(
                status_code=404,
                category="not_found",
                errors={"candidate_profile": "Data tidak ditemukan"},
            )
        values = {
            "headline": payload.headline
            if "headline" in payload.model_fields_set
            else record.headline,
            "biography": payload.biography
            if "biography" in payload.model_fields_set
            else record.biography,
            "city": payload.city if "city" in payload.model_fields_set else record.city,
            "province": payload.province
            if "province" in payload.model_fields_set
            else record.province,
            "country": payload.country if "country" in payload.model_fields_set else record.country,
            "years_experience": payload.years_experience
            if "years_experience" in payload.model_fields_set
            else record.years_experience,
            "preferred_employment_type": payload.preferred_employment_type
            if "preferred_employment_type" in payload.model_fields_set
            else record.preferred_employment_type,
            "preferred_work_mode": payload.preferred_work_mode
            if "preferred_work_mode" in payload.model_fields_set
            else record.preferred_work_mode,
            "expected_salary_min": payload.expected_salary_min
            if "expected_salary_min" in payload.model_fields_set
            else record.expected_salary_min,
            "expected_salary_max": payload.expected_salary_max
            if "expected_salary_max" in payload.model_fields_set
            else record.expected_salary_max,
            "available_from": payload.available_from
            if "available_from" in payload.model_fields_set
            else record.available_from,
            "profile_visibility": payload.profile_visibility
            if "profile_visibility" in payload.model_fields_set
            else record.profile_visibility,
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
        if values["country"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"country": "Field tidak boleh null"},
            )
        if values["preferred_employment_type"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"preferred_employment_type": "Field tidak boleh null"},
            )
        if values["preferred_work_mode"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"preferred_work_mode": "Field tidak boleh null"},
            )
        if values["profile_visibility"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"profile_visibility": "Field tidak boleh null"},
            )
        role_field = ("user_id", "candidate")
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
        for low, high in (("expected_salary_min", "expected_salary_max"),):
            if (
                values.get(low) is not None
                and values.get(high) is not None
                and (values[low] > values[high])
            ):
                raise AppError(
                    status_code=422,
                    category="validation",
                    message="Validasi gagal",
                    errors={high: "Nilai akhir tidak boleh lebih kecil dari nilai awal"},
                )
        if "headline" in payload.model_fields_set:
            record.headline = values["headline"]
        if "biography" in payload.model_fields_set:
            record.biography = values["biography"]
        if "city" in payload.model_fields_set:
            record.city = values["city"]
        if "province" in payload.model_fields_set:
            record.province = values["province"]
        if "country" in payload.model_fields_set:
            record.country = values["country"]
        if "years_experience" in payload.model_fields_set:
            record.years_experience = values["years_experience"]
        if "preferred_employment_type" in payload.model_fields_set:
            record.preferred_employment_type = values["preferred_employment_type"]
        if "preferred_work_mode" in payload.model_fields_set:
            record.preferred_work_mode = values["preferred_work_mode"]
        if "expected_salary_min" in payload.model_fields_set:
            record.expected_salary_min = values["expected_salary_min"]
        if "expected_salary_max" in payload.model_fields_set:
            record.expected_salary_max = values["expected_salary_max"]
        if "available_from" in payload.model_fields_set:
            record.available_from = values["available_from"]
        if "profile_visibility" in payload.model_fields_set:
            record.profile_visibility = values["profile_visibility"]
        db.flush()
        db.refresh(record)
        db.commit()
        return record
    except DBAPIError as exc:
        db.rollback()
        translate_database_error(exc, "candidate_profile")
        raise
    except Exception:
        db.rollback()
        raise


def delete_candidate_profile(db: Session, user_id: int) -> None:
    try:
        statement = (
            select(CandidateProfile)
            .where(CandidateProfile.user_id == user_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        record = db.scalar(statement)
        if record is None:
            raise AppError(
                status_code=404,
                category="not_found",
                errors={"candidate_profile": "Data tidak ditemukan"},
            )
        db.delete(record)
        db.commit()
    except DBAPIError as exc:
        db.rollback()
        translate_database_error(exc, "candidate_profile")
        raise
    except Exception:
        db.rollback()
        raise
