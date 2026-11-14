from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app.configs.database import get_db
from app.configs.dependencies import require_admin
from app.controllers import job_match_controller
from app.schemas import job_match as schema
from app.schemas.job_match import (
    JobMatchCreate,
    JobMatchDetailResponse,
    JobMatchListResponse,
    JobMatchUpdate,
)
from app.schemas.response import EmptyResponse

router = APIRouter(
    prefix="/job-matches", tags=["Job matches"], dependencies=[Depends(require_admin)]
)


@router.post("", response_model=JobMatchDetailResponse, status_code=201)
def create_job_match(
    payload: JobMatchCreate,
    db: Session = Depends(get_db),
) -> JobMatchDetailResponse:
    return job_match_controller.create_job_match(db=db, payload=payload)


@router.get("", response_model=JobMatchListResponse, status_code=200)
def list_job_matches(
    db: Session = Depends(get_db),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    job_id: int | None = Query(default=None, gt=0, le=18446744073709551615),
    candidate_user_id: int | None = Query(default=None, gt=0, le=18446744073709551615),
    match_status: schema.MatchStatus | None = Query(default=None),
    candidate_decision: schema.Decision | None = Query(default=None),
    employer_decision: schema.Decision | None = Query(default=None),
) -> JobMatchListResponse:
    return job_match_controller.list_job_matches(
        db=db,
        offset=offset,
        limit=limit,
        job_id=job_id,
        candidate_user_id=candidate_user_id,
        match_status=match_status,
        candidate_decision=candidate_decision,
        employer_decision=employer_decision,
    )


@router.get("/{job_match_id}", response_model=JobMatchDetailResponse, status_code=200)
def get_job_match(
    job_match_id: int = Path(..., gt=0, le=18446744073709551615),
    db: Session = Depends(get_db),
) -> JobMatchDetailResponse:
    return job_match_controller.get_job_match(db=db, job_match_id=job_match_id)


@router.patch("/{job_match_id}", response_model=JobMatchDetailResponse, status_code=200)
def update_job_match(
    payload: JobMatchUpdate,
    job_match_id: int = Path(..., gt=0, le=18446744073709551615),
    db: Session = Depends(get_db),
) -> JobMatchDetailResponse:
    return job_match_controller.update_job_match(db=db, payload=payload, job_match_id=job_match_id)


@router.delete("/{job_match_id}", response_model=EmptyResponse, status_code=200)
def delete_job_match(
    job_match_id: int = Path(..., gt=0, le=18446744073709551615),
    db: Session = Depends(get_db),
) -> EmptyResponse:
    return job_match_controller.delete_job_match(db=db, job_match_id=job_match_id)
