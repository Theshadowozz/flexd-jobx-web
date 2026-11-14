from datetime import UTC, datetime
from typing import Literal

from sqlalchemy import func, select
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from app.models import JobPost, User
from app.schemas import job_post as schema
from app.schemas.job_post import JobPostCreate, JobPostUpdate
from app.utils.database_errors import translate_database_error
from app.utils.exceptions import AppError


def get_job_post(db: Session, job_post_id: int) -> JobPost:
    statement = select(JobPost).where(JobPost.id == job_post_id)
    job_post = db.scalar(statement)
    if job_post is None:
        raise AppError(
            status_code=404, category="not_found", errors={"job_post": "Data tidak ditemukan"}
        )
    return job_post


def list_job_posts(
    db: Session,
    offset: int,
    limit: int,
    user_id: int | None = None,
    city: str | None = None,
    province: str | None = None,
    employment_type: schema.EmploymentType | None = None,
    work_mode: schema.WorkMode | None = None,
    approval_status: Literal["draft", "pending_approval", "approved", "rejected"] | None = None,
    publication_status: Literal["unpublished", "published", "paused", "closed"] | None = None,
    search: str | None = None,
) -> tuple[list[JobPost], int]:
    conditions = []
    if user_id is not None:
        conditions.append(JobPost.user_id == user_id)
    if city is not None:
        conditions.append(JobPost.city == city)
    if province is not None:
        conditions.append(JobPost.province == province)
    if employment_type is not None:
        conditions.append(JobPost.employment_type == employment_type)
    if work_mode is not None:
        conditions.append(JobPost.work_mode == work_mode)
    if approval_status is not None:
        conditions.append(JobPost.approval_status == approval_status)
    if publication_status is not None:
        conditions.append(JobPost.publication_status == publication_status)
    if search:
        conditions.append(JobPost.title.contains(search, autoescape=True))
    total_statement = select(func.count()).select_from(JobPost).where(*conditions)
    total = db.scalar(total_statement) or 0
    statement = select(JobPost).where(*conditions).order_by(JobPost.id).offset(offset).limit(limit)
    records = list(db.scalars(statement).all())
    return (records, total)


def create_job_post(db: Session, payload: JobPostCreate) -> JobPost:
    try:
        record = None
        values = {
            "title": payload.title,
            "business_problem": payload.business_problem,
            "job_summary": payload.job_summary,
            "job_description": payload.job_description,
            "employment_type": payload.employment_type,
            "work_mode": payload.work_mode,
            "city": payload.city,
            "province": payload.province,
            "country": payload.country,
            "salary_min": payload.salary_min,
            "salary_max": payload.salary_max,
            "currency": payload.currency,
            "ai_generation_metadata": payload.ai_generation_metadata,
            "approval_status": payload.approval_status,
            "publication_status": payload.publication_status,
            "closes_at": payload.closes_at,
            "user_id": payload.user_id,
        }
        changes = payload.model_dump()
        now = datetime.now(UTC).replace(tzinfo=None)
        if values.get("publication_status") == "published":
            if not values.get("published_at"):
                values["published_at"] = changes["published_at"] = now
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
        if values["title"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"title": "Field tidak boleh null"},
            )
        if values["business_problem"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"business_problem": "Field tidak boleh null"},
            )
        if values["employment_type"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"employment_type": "Field tidak boleh null"},
            )
        if values["work_mode"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"work_mode": "Field tidak boleh null"},
            )
        if values["country"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"country": "Field tidak boleh null"},
            )
        if values["currency"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"currency": "Field tidak boleh null"},
            )
        if values["approval_status"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"approval_status": "Field tidak boleh null"},
            )
        if values["publication_status"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"publication_status": "Field tidak boleh null"},
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
        for low, high in (("salary_min", "salary_max"),):
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
        if (
            values.get("publication_status") == "published"
            and values.get("approval_status") != "approved"
        ):
            raise AppError(409, "business_rule", {"publication_status": "Lowongan belum disetujui"})
        closes, published = (values.get("closes_at"), values.get("published_at"))
        if closes is not None:
            if closes.tzinfo is not None:
                closes = closes.astimezone(UTC).replace(tzinfo=None)
                values["closes_at"] = closes
            if published is not None and closes <= published:
                raise AppError(
                    status_code=422,
                    category="validation",
                    message="Validasi gagal",
                    errors={"closes_at": "Penutupan harus setelah publikasi"},
                )
        record = JobPost(
            title=values["title"],
            business_problem=values["business_problem"],
            job_summary=values["job_summary"],
            job_description=values["job_description"],
            employment_type=values["employment_type"],
            work_mode=values["work_mode"],
            city=values["city"],
            province=values["province"],
            country=values["country"],
            salary_min=values["salary_min"],
            salary_max=values["salary_max"],
            currency=values["currency"],
            ai_generation_metadata=values["ai_generation_metadata"],
            approval_status=values["approval_status"],
            publication_status=values["publication_status"],
            closes_at=values["closes_at"],
            user_id=values["user_id"],
            published_at=changes.get("published_at"),
        )
        db.add(record)
        db.flush()
        db.refresh(record)
        db.commit()
        return record
    except DBAPIError as exc:
        db.rollback()
        translate_database_error(exc, "job_post")
        raise
    except Exception:
        db.rollback()
        raise


def update_job_post(db: Session, job_post_id: int, payload: JobPostUpdate) -> JobPost:
    try:
        statement = (
            select(JobPost)
            .where(JobPost.id == job_post_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        record = db.scalar(statement)
        if record is None:
            raise AppError(
                status_code=404, category="not_found", errors={"job_post": "Data tidak ditemukan"}
            )
        values = {
            "title": payload.title if "title" in payload.model_fields_set else record.title,
            "business_problem": payload.business_problem
            if "business_problem" in payload.model_fields_set
            else record.business_problem,
            "job_summary": payload.job_summary
            if "job_summary" in payload.model_fields_set
            else record.job_summary,
            "job_description": payload.job_description
            if "job_description" in payload.model_fields_set
            else record.job_description,
            "employment_type": payload.employment_type
            if "employment_type" in payload.model_fields_set
            else record.employment_type,
            "work_mode": payload.work_mode
            if "work_mode" in payload.model_fields_set
            else record.work_mode,
            "city": payload.city if "city" in payload.model_fields_set else record.city,
            "province": payload.province
            if "province" in payload.model_fields_set
            else record.province,
            "country": payload.country if "country" in payload.model_fields_set else record.country,
            "salary_min": payload.salary_min
            if "salary_min" in payload.model_fields_set
            else record.salary_min,
            "salary_max": payload.salary_max
            if "salary_max" in payload.model_fields_set
            else record.salary_max,
            "currency": payload.currency
            if "currency" in payload.model_fields_set
            else record.currency,
            "ai_generation_metadata": payload.ai_generation_metadata
            if "ai_generation_metadata" in payload.model_fields_set
            else record.ai_generation_metadata,
            "approval_status": payload.approval_status
            if "approval_status" in payload.model_fields_set
            else record.approval_status,
            "publication_status": payload.publication_status
            if "publication_status" in payload.model_fields_set
            else record.publication_status,
            "closes_at": payload.closes_at
            if "closes_at" in payload.model_fields_set
            else record.closes_at,
            "user_id": record.user_id,
            "published_at": record.published_at,
        }
        changes = payload.model_dump(exclude_unset=True)
        now = datetime.now(UTC).replace(tzinfo=None)
        if values.get("publication_status") == "published":
            if not values.get("published_at"):
                values["published_at"] = changes["published_at"] = now
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
        if values["title"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"title": "Field tidak boleh null"},
            )
        if values["business_problem"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"business_problem": "Field tidak boleh null"},
            )
        if values["employment_type"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"employment_type": "Field tidak boleh null"},
            )
        if values["work_mode"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"work_mode": "Field tidak boleh null"},
            )
        if values["country"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"country": "Field tidak boleh null"},
            )
        if values["currency"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"currency": "Field tidak boleh null"},
            )
        if values["approval_status"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"approval_status": "Field tidak boleh null"},
            )
        if values["publication_status"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"publication_status": "Field tidak boleh null"},
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
        for low, high in (("salary_min", "salary_max"),):
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
        if (
            values.get("publication_status") == "published"
            and values.get("approval_status") != "approved"
        ):
            raise AppError(409, "business_rule", {"publication_status": "Lowongan belum disetujui"})
        closes, published = (values.get("closes_at"), values.get("published_at"))
        if closes is not None:
            if closes.tzinfo is not None:
                closes = closes.astimezone(UTC).replace(tzinfo=None)
                values["closes_at"] = closes
            if published is not None and closes <= published:
                raise AppError(
                    status_code=422,
                    category="validation",
                    message="Validasi gagal",
                    errors={"closes_at": "Penutupan harus setelah publikasi"},
                )
        if "title" in payload.model_fields_set:
            record.title = values["title"]
        if "business_problem" in payload.model_fields_set:
            record.business_problem = values["business_problem"]
        if "job_summary" in payload.model_fields_set:
            record.job_summary = values["job_summary"]
        if "job_description" in payload.model_fields_set:
            record.job_description = values["job_description"]
        if "employment_type" in payload.model_fields_set:
            record.employment_type = values["employment_type"]
        if "work_mode" in payload.model_fields_set:
            record.work_mode = values["work_mode"]
        if "city" in payload.model_fields_set:
            record.city = values["city"]
        if "province" in payload.model_fields_set:
            record.province = values["province"]
        if "country" in payload.model_fields_set:
            record.country = values["country"]
        if "salary_min" in payload.model_fields_set:
            record.salary_min = values["salary_min"]
        if "salary_max" in payload.model_fields_set:
            record.salary_max = values["salary_max"]
        if "currency" in payload.model_fields_set:
            record.currency = values["currency"]
        if "ai_generation_metadata" in payload.model_fields_set:
            record.ai_generation_metadata = values["ai_generation_metadata"]
        if "approval_status" in payload.model_fields_set:
            record.approval_status = values["approval_status"]
        if "publication_status" in payload.model_fields_set:
            record.publication_status = values["publication_status"]
        if "closes_at" in payload.model_fields_set:
            record.closes_at = values["closes_at"]
        if "published_at" in changes:
            record.published_at = changes["published_at"]
        db.flush()
        db.refresh(record)
        db.commit()
        return record
    except DBAPIError as exc:
        db.rollback()
        translate_database_error(exc, "job_post")
        raise
    except Exception:
        db.rollback()
        raise


def delete_job_post(db: Session, job_post_id: int) -> None:
    try:
        statement = (
            select(JobPost)
            .where(JobPost.id == job_post_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        record = db.scalar(statement)
        if record is None:
            raise AppError(
                status_code=404, category="not_found", errors={"job_post": "Data tidak ditemukan"}
            )
        db.delete(record)
        db.commit()
    except DBAPIError as exc:
        db.rollback()
        translate_database_error(exc, "job_post")
        raise
    except Exception:
        db.rollback()
        raise
