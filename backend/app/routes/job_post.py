from typing import Literal

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app.configs.database import get_db
from app.configs.dependencies import require_admin
from app.controllers import job_post_controller
from app.schemas import job_post as schema
from app.schemas.job_post import (
    JobPostCreate,
    JobPostDetailResponse,
    JobPostListResponse,
    JobPostUpdate,
)
from app.schemas.response import EmptyResponse

router = APIRouter(prefix="/job-posts", tags=["Job posts"], dependencies=[Depends(require_admin)])


@router.post("", response_model=JobPostDetailResponse, status_code=201)
def create_job_post(
    payload: JobPostCreate,
    db: Session = Depends(get_db),
) -> JobPostDetailResponse:
    return job_post_controller.create_job_post(db=db, payload=payload)


@router.get("", response_model=JobPostListResponse, status_code=200)
def list_job_posts(
    db: Session = Depends(get_db),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    user_id: int | None = Query(default=None, gt=0, le=18446744073709551615),
    city: str | None = Query(default=None, max_length=120),
    province: str | None = Query(default=None, max_length=120),
    employment_type: schema.EmploymentType | None = Query(default=None),
    work_mode: schema.WorkMode | None = Query(default=None),
    approval_status: Literal["draft", "pending_approval", "approved", "rejected"] | None = Query(
        default=None
    ),
    publication_status: Literal["unpublished", "published", "paused", "closed"] | None = Query(
        default=None
    ),
    search: str | None = Query(default=None, max_length=200),
) -> JobPostListResponse:
    return job_post_controller.list_job_posts(
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


@router.get("/{job_post_id}", response_model=JobPostDetailResponse, status_code=200)
def get_job_post(
    job_post_id: int = Path(..., gt=0, le=18446744073709551615),
    db: Session = Depends(get_db),
) -> JobPostDetailResponse:
    return job_post_controller.get_job_post(db=db, job_post_id=job_post_id)


@router.patch("/{job_post_id}", response_model=JobPostDetailResponse, status_code=200)
def update_job_post(
    payload: JobPostUpdate,
    job_post_id: int = Path(..., gt=0, le=18446744073709551615),
    db: Session = Depends(get_db),
) -> JobPostDetailResponse:
    return job_post_controller.update_job_post(db=db, payload=payload, job_post_id=job_post_id)


@router.delete("/{job_post_id}", response_model=EmptyResponse, status_code=200)
def delete_job_post(
    job_post_id: int = Path(..., gt=0, le=18446744073709551615),
    db: Session = Depends(get_db),
) -> EmptyResponse:
    return job_post_controller.delete_job_post(db=db, job_post_id=job_post_id)
