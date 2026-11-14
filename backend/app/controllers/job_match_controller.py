from sqlalchemy.orm import Session

from app.schemas import job_match as schema
from app.schemas.job_match import (
    JobMatchCreate,
    JobMatchDetailData,
    JobMatchDetailResponse,
    JobMatchListData,
    JobMatchListResponse,
    JobMatchRead,
    JobMatchUpdate,
)
from app.schemas.response import EmptyResponse, Pagination
from app.services import job_match_service


def create_job_match(db: Session, payload: JobMatchCreate) -> JobMatchDetailResponse:
    job_match = job_match_service.create_job_match(db=db, payload=payload)
    job_match_data = JobMatchRead.model_validate(job_match)
    return JobMatchDetailResponse(
        message={"success": "Data berhasil dibuat"},
        data=JobMatchDetailData(job_match=job_match_data),
    )


def get_job_match(db: Session, job_match_id: int) -> JobMatchDetailResponse:
    job_match = job_match_service.get_job_match(db=db, job_match_id=job_match_id)
    job_match_data = JobMatchRead.model_validate(job_match)
    return JobMatchDetailResponse(
        message={"success": "Data berhasil diambil"},
        data=JobMatchDetailData(job_match=job_match_data),
    )


def update_job_match(
    db: Session, job_match_id: int, payload: JobMatchUpdate
) -> JobMatchDetailResponse:
    job_match = job_match_service.update_job_match(
        db=db, job_match_id=job_match_id, payload=payload
    )
    job_match_data = JobMatchRead.model_validate(job_match)
    return JobMatchDetailResponse(
        message={"success": "Data berhasil diperbarui"},
        data=JobMatchDetailData(job_match=job_match_data),
    )


def list_job_matches(
    db: Session,
    offset: int,
    limit: int,
    job_id: int | None = None,
    candidate_user_id: int | None = None,
    match_status: schema.MatchStatus | None = None,
    candidate_decision: schema.Decision | None = None,
    employer_decision: schema.Decision | None = None,
) -> JobMatchListResponse:
    records, total = job_match_service.list_job_matches(
        db=db,
        offset=offset,
        limit=limit,
        job_id=job_id,
        candidate_user_id=candidate_user_id,
        match_status=match_status,
        candidate_decision=candidate_decision,
        employer_decision=employer_decision,
    )
    items = [JobMatchRead.model_validate(record) for record in records]
    return JobMatchListResponse(
        message={"success": "Daftar data berhasil diambil"},
        data=JobMatchListData(
            job_matches=items, pagination=Pagination(offset=offset, limit=limit, total=total)
        ),
    )


def delete_job_match(db: Session, job_match_id: int) -> EmptyResponse:
    job_match_service.delete_job_match(db=db, job_match_id=job_match_id)
    return EmptyResponse(message={"success": "Data berhasil dihapus"}, data={})
