from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from app.models import JobMatch, User
from app.models.job_post import JobPost
from app.schemas import job_match as schema
from app.schemas.job_match import JobMatchCreate, JobMatchUpdate
from app.utils.database_errors import translate_database_error
from app.utils.exceptions import AppError


def get_job_match(db: Session, job_match_id: int) -> JobMatch:
    statement = select(JobMatch).where(JobMatch.id == job_match_id)
    job_match = db.scalar(statement)
    if job_match is None:
        raise AppError(
            status_code=404, category="not_found", errors={"job_match": "Data tidak ditemukan"}
        )
    return job_match


def list_job_matches(
    db: Session,
    offset: int,
    limit: int,
    job_id: int | None = None,
    candidate_user_id: int | None = None,
    match_status: schema.MatchStatus | None = None,
    candidate_decision: schema.Decision | None = None,
    employer_decision: schema.Decision | None = None,
) -> tuple[list[JobMatch], int]:
    conditions = []
    if job_id is not None:
        conditions.append(JobMatch.job_id == job_id)
    if candidate_user_id is not None:
        conditions.append(JobMatch.candidate_user_id == candidate_user_id)
    if match_status is not None:
        conditions.append(JobMatch.match_status == match_status)
    if candidate_decision is not None:
        conditions.append(JobMatch.candidate_decision == candidate_decision)
    if employer_decision is not None:
        conditions.append(JobMatch.employer_decision == employer_decision)
    total_statement = select(func.count()).select_from(JobMatch).where(*conditions)
    total = db.scalar(total_statement) or 0
    statement = (
        select(JobMatch).where(*conditions).order_by(JobMatch.id).offset(offset).limit(limit)
    )
    records = list(db.scalars(statement).all())
    return (records, total)


def create_job_match(db: Session, payload: JobMatchCreate) -> JobMatch:
    try:
        record = None
        values = {
            "match_score": payload.match_score,
            "score_breakdown": payload.score_breakdown,
            "explanation": payload.explanation,
            "candidate_decision": payload.candidate_decision,
            "employer_decision": payload.employer_decision,
            "match_status": payload.match_status,
            "job_id": payload.job_id,
            "candidate_user_id": payload.candidate_user_id,
        }
        changes = payload.model_dump()
        now = datetime.now(UTC).replace(tzinfo=None)
        if "candidate_decision" in changes:
            if record is None or changes["candidate_decision"] != record.candidate_decision:
                changes["candidate_decided_at"] = (
                    None if changes["candidate_decision"] == "pending" else now
                )
        if "employer_decision" in changes:
            if record is None or changes["employer_decision"] != record.employer_decision:
                changes["employer_decided_at"] = (
                    None if changes["employer_decision"] == "pending" else now
                )
        decisions = (values["candidate_decision"], values["employer_decision"])
        derived = (
            "rejected"
            if "rejected" in decisions
            else "mutually_accepted"
            if decisions == ("accepted", "accepted")
            else "one_side_interested"
            if "accepted" in decisions
            else "recommended"
        )
        if values.get("match_status") != "expired":
            if "match_status" in payload.model_fields_set and changes["match_status"] != derived:
                raise AppError(
                    status_code=422,
                    category="validation",
                    message="Validasi gagal",
                    errors={"match_status": "Status tidak sesuai keputusan kedua pihak"},
                )
            changes["match_status"] = derived
        if values["job_id"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"job_id": "Field tidak boleh null"},
            )
        if values["job_id"] is not None:
            referenced_job_id = db.scalar(
                select(JobPost)
                .where(JobPost.id == values["job_id"])
                .with_for_update(read=True)
                .execution_options(populate_existing=True)
            )
            if referenced_job_id is None:
                raise AppError(
                    status_code=422,
                    category="validation",
                    message="Validasi gagal",
                    errors={"job_id": "Referensi tidak ditemukan"},
                )
        if values["candidate_user_id"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"candidate_user_id": "Field tidak boleh null"},
            )
        if values["candidate_user_id"] is not None:
            referenced_candidate_user_id = db.scalar(
                select(User)
                .where(User.id == values["candidate_user_id"])
                .with_for_update(read=True)
                .execution_options(populate_existing=True)
            )
            if referenced_candidate_user_id is None:
                raise AppError(
                    status_code=422,
                    category="validation",
                    message="Validasi gagal",
                    errors={"candidate_user_id": "Referensi tidak ditemukan"},
                )
        if values["match_score"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"match_score": "Field tidak boleh null"},
            )
        if values["score_breakdown"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"score_breakdown": "Field tidak boleh null"},
            )
        if values["explanation"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"explanation": "Field tidak boleh null"},
            )
        if values["candidate_decision"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"candidate_decision": "Field tidak boleh null"},
            )
        if values["employer_decision"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"employer_decision": "Field tidak boleh null"},
            )
        if values["match_status"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"match_status": "Field tidak boleh null"},
            )
        role_field = ("candidate_user_id", "candidate")
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
        record = JobMatch(
            match_score=values["match_score"],
            score_breakdown=values["score_breakdown"],
            explanation=values["explanation"],
            candidate_decision=values["candidate_decision"],
            employer_decision=values["employer_decision"],
            match_status=changes["match_status"],
            job_id=values["job_id"],
            candidate_user_id=values["candidate_user_id"],
            candidate_decided_at=changes.get("candidate_decided_at"),
            employer_decided_at=changes.get("employer_decided_at"),
        )
        db.add(record)
        db.flush()
        db.refresh(record)
        db.commit()
        return record
    except DBAPIError as exc:
        db.rollback()
        translate_database_error(exc, "job_match")
        raise
    except Exception:
        db.rollback()
        raise


def update_job_match(db: Session, job_match_id: int, payload: JobMatchUpdate) -> JobMatch:
    try:
        statement = (
            select(JobMatch)
            .where(JobMatch.id == job_match_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        record = db.scalar(statement)
        if record is None:
            raise AppError(
                status_code=404, category="not_found", errors={"job_match": "Data tidak ditemukan"}
            )
        values = {
            "match_score": payload.match_score
            if "match_score" in payload.model_fields_set
            else record.match_score,
            "score_breakdown": payload.score_breakdown
            if "score_breakdown" in payload.model_fields_set
            else record.score_breakdown,
            "explanation": payload.explanation
            if "explanation" in payload.model_fields_set
            else record.explanation,
            "candidate_decision": payload.candidate_decision
            if "candidate_decision" in payload.model_fields_set
            else record.candidate_decision,
            "employer_decision": payload.employer_decision
            if "employer_decision" in payload.model_fields_set
            else record.employer_decision,
            "match_status": payload.match_status
            if "match_status" in payload.model_fields_set
            else record.match_status,
            "job_id": record.job_id,
            "candidate_user_id": record.candidate_user_id,
        }
        changes = payload.model_dump(exclude_unset=True)
        now = datetime.now(UTC).replace(tzinfo=None)
        if "candidate_decision" in changes:
            if record is None or changes["candidate_decision"] != record.candidate_decision:
                changes["candidate_decided_at"] = (
                    None if changes["candidate_decision"] == "pending" else now
                )
        if "employer_decision" in changes:
            if record is None or changes["employer_decision"] != record.employer_decision:
                changes["employer_decided_at"] = (
                    None if changes["employer_decision"] == "pending" else now
                )
        decisions = (values["candidate_decision"], values["employer_decision"])
        derived = (
            "rejected"
            if "rejected" in decisions
            else "mutually_accepted"
            if decisions == ("accepted", "accepted")
            else "one_side_interested"
            if "accepted" in decisions
            else "recommended"
        )
        if values.get("match_status") != "expired":
            if "match_status" in payload.model_fields_set and changes["match_status"] != derived:
                raise AppError(
                    status_code=422,
                    category="validation",
                    message="Validasi gagal",
                    errors={"match_status": "Status tidak sesuai keputusan kedua pihak"},
                )
            changes["match_status"] = derived
        if values["job_id"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"job_id": "Field tidak boleh null"},
            )
        if values["job_id"] is not None:
            referenced_job_id = db.scalar(
                select(JobPost)
                .where(JobPost.id == values["job_id"])
                .with_for_update(read=True)
                .execution_options(populate_existing=True)
            )
            if referenced_job_id is None:
                raise AppError(
                    status_code=422,
                    category="validation",
                    message="Validasi gagal",
                    errors={"job_id": "Referensi tidak ditemukan"},
                )
        if values["candidate_user_id"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"candidate_user_id": "Field tidak boleh null"},
            )
        if values["candidate_user_id"] is not None:
            referenced_candidate_user_id = db.scalar(
                select(User)
                .where(User.id == values["candidate_user_id"])
                .with_for_update(read=True)
                .execution_options(populate_existing=True)
            )
            if referenced_candidate_user_id is None:
                raise AppError(
                    status_code=422,
                    category="validation",
                    message="Validasi gagal",
                    errors={"candidate_user_id": "Referensi tidak ditemukan"},
                )
        if values["match_score"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"match_score": "Field tidak boleh null"},
            )
        if values["score_breakdown"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"score_breakdown": "Field tidak boleh null"},
            )
        if values["explanation"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"explanation": "Field tidak boleh null"},
            )
        if values["candidate_decision"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"candidate_decision": "Field tidak boleh null"},
            )
        if values["employer_decision"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"employer_decision": "Field tidak boleh null"},
            )
        if values["match_status"] is None:
            raise AppError(
                status_code=422,
                category="validation",
                message="Validasi gagal",
                errors={"match_status": "Field tidak boleh null"},
            )
        role_field = ("candidate_user_id", "candidate")
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
        if "match_score" in payload.model_fields_set:
            record.match_score = values["match_score"]
        if "score_breakdown" in payload.model_fields_set:
            record.score_breakdown = values["score_breakdown"]
        if "explanation" in payload.model_fields_set:
            record.explanation = values["explanation"]
        if "candidate_decision" in payload.model_fields_set:
            record.candidate_decision = values["candidate_decision"]
        if "employer_decision" in payload.model_fields_set:
            record.employer_decision = values["employer_decision"]
        if "match_status" in payload.model_fields_set:
            record.match_status = values["match_status"]
        if "match_status" in changes:
            record.match_status = changes["match_status"]
        if "candidate_decided_at" in changes:
            record.candidate_decided_at = changes["candidate_decided_at"]
        if "employer_decided_at" in changes:
            record.employer_decided_at = changes["employer_decided_at"]
        db.flush()
        db.refresh(record)
        db.commit()
        return record
    except DBAPIError as exc:
        db.rollback()
        translate_database_error(exc, "job_match")
        raise
    except Exception:
        db.rollback()
        raise


def delete_job_match(db: Session, job_match_id: int) -> None:
    try:
        statement = (
            select(JobMatch)
            .where(JobMatch.id == job_match_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        record = db.scalar(statement)
        if record is None:
            raise AppError(
                status_code=404, category="not_found", errors={"job_match": "Data tidak ditemukan"}
            )
        db.delete(record)
        db.commit()
    except DBAPIError as exc:
        db.rollback()
        translate_database_error(exc, "job_match")
        raise
    except Exception:
        db.rollback()
        raise
