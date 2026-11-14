from sqlalchemy.orm import Session

from app.schemas import candidate_profile as schema
from app.schemas.candidate_profile import (
    CandidateProfileCreate,
    CandidateProfileDetailData,
    CandidateProfileDetailResponse,
    CandidateProfileListData,
    CandidateProfileListResponse,
    CandidateProfileRead,
    CandidateProfileUpdate,
)
from app.schemas.response import EmptyResponse, Pagination
from app.services import candidate_profile_service


def create_candidate_profile(
    db: Session, payload: CandidateProfileCreate
) -> CandidateProfileDetailResponse:
    candidate_profile = candidate_profile_service.create_candidate_profile(db=db, payload=payload)
    candidate_profile_data = CandidateProfileRead.model_validate(candidate_profile)
    return CandidateProfileDetailResponse(
        message={"success": "Data berhasil dibuat"},
        data=CandidateProfileDetailData(candidate_profile=candidate_profile_data),
    )


def get_candidate_profile(db: Session, user_id: int) -> CandidateProfileDetailResponse:
    candidate_profile = candidate_profile_service.get_candidate_profile(db=db, user_id=user_id)
    candidate_profile_data = CandidateProfileRead.model_validate(candidate_profile)
    return CandidateProfileDetailResponse(
        message={"success": "Data berhasil diambil"},
        data=CandidateProfileDetailData(candidate_profile=candidate_profile_data),
    )


def update_candidate_profile(
    db: Session, user_id: int, payload: CandidateProfileUpdate
) -> CandidateProfileDetailResponse:
    candidate_profile = candidate_profile_service.update_candidate_profile(
        db=db, user_id=user_id, payload=payload
    )
    candidate_profile_data = CandidateProfileRead.model_validate(candidate_profile)
    return CandidateProfileDetailResponse(
        message={"success": "Data berhasil diperbarui"},
        data=CandidateProfileDetailData(candidate_profile=candidate_profile_data),
    )


def list_candidate_profiles(
    db: Session,
    offset: int,
    limit: int,
    city: str | None = None,
    province: str | None = None,
    preferred_employment_type: schema.EmploymentPreference | None = None,
    preferred_work_mode: schema.WorkPreference | None = None,
    profile_visibility: schema.ProfileVisibility | None = None,
) -> CandidateProfileListResponse:
    records, total = candidate_profile_service.list_candidate_profiles(
        db=db,
        offset=offset,
        limit=limit,
        city=city,
        province=province,
        preferred_employment_type=preferred_employment_type,
        preferred_work_mode=preferred_work_mode,
        profile_visibility=profile_visibility,
    )
    items = [CandidateProfileRead.model_validate(record) for record in records]
    return CandidateProfileListResponse(
        message={"success": "Daftar data berhasil diambil"},
        data=CandidateProfileListData(
            candidate_profiles=items, pagination=Pagination(offset=offset, limit=limit, total=total)
        ),
    )


def delete_candidate_profile(db: Session, user_id: int) -> EmptyResponse:
    candidate_profile_service.delete_candidate_profile(db=db, user_id=user_id)
    return EmptyResponse(message={"success": "Data berhasil dihapus"}, data={})
