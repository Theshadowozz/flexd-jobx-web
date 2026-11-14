from typing import Literal

from sqlalchemy.orm import Session

from app.schemas import job_post as schema
from app.schemas.job_post import (
    JobPostCreate,
    JobPostDetailData,
    JobPostDetailResponse,
    JobPostListData,
    JobPostListResponse,
    JobPostRead,
    JobPostUpdate,
)
from app.schemas.response import EmptyResponse, Pagination
from app.services import job_post_service


def create_job_post(db: Session, payload: JobPostCreate) -> JobPostDetailResponse:
    job_post = job_post_service.create_job_post(db=db, payload=payload)
    job_post_data = JobPostRead.model_validate(job_post)
    return JobPostDetailResponse(
        message={"success": "Data berhasil dibuat"}, data=JobPostDetailData(job_post=job_post_data)
    )


def get_job_post(db: Session, job_post_id: int) -> JobPostDetailResponse:
    job_post = job_post_service.get_job_post(db=db, job_post_id=job_post_id)
    job_post_data = JobPostRead.model_validate(job_post)
    return JobPostDetailResponse(
        message={"success": "Data berhasil diambil"}, data=JobPostDetailData(job_post=job_post_data)
    )


def update_job_post(db: Session, job_post_id: int, payload: JobPostUpdate) -> JobPostDetailResponse:
    job_post = job_post_service.update_job_post(db=db, job_post_id=job_post_id, payload=payload)
    job_post_data = JobPostRead.model_validate(job_post)
    return JobPostDetailResponse(
        message={"success": "Data berhasil diperbarui"},
        data=JobPostDetailData(job_post=job_post_data),
    )


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
) -> JobPostListResponse:
    records, total = job_post_service.list_job_posts(
        db=db,
        offset=offset,
        limit=limit,
        user_id=user_id,
        city=city,
        province=province,
        employment_type=employment_type,
        work_mode=work_mode,
        approval_status=approval_status,
        publication_status=publication_status,
        search=search,
    )
    items = [JobPostRead.model_validate(record) for record in records]
    return JobPostListResponse(
        message={"success": "Daftar data berhasil diambil"},
        data=JobPostListData(
            job_posts=items, pagination=Pagination(offset=offset, limit=limit, total=total)
        ),
    )


def delete_job_post(db: Session, job_post_id: int) -> EmptyResponse:
    job_post_service.delete_job_post(db=db, job_post_id=job_post_id)
    return EmptyResponse(message={"success": "Data berhasil dihapus"}, data={})
