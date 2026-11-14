from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app.configs.database import get_db
from app.configs.dependencies import require_admin
from app.controllers import candidate_profile_controller
from app.schemas import candidate_profile as schema
from app.schemas.candidate_profile import (
    CandidateProfileCreate,
    CandidateProfileDetailResponse,
    CandidateProfileListResponse,
    CandidateProfileUpdate,
)
from app.schemas.response import EmptyResponse

router = APIRouter(
    prefix="/candidate-profiles", tags=["Candidate profiles"], dependencies=[Depends(require_admin)]
)


@router.post("", response_model=CandidateProfileDetailResponse, status_code=201)
def create_candidate_profile(
    payload: CandidateProfileCreate,
    db: Session = Depends(get_db),
) -> CandidateProfileDetailResponse:
    return candidate_profile_controller.create_candidate_profile(db=db, payload=payload)


@router.get("", response_model=CandidateProfileListResponse, status_code=200)
def list_candidate_profiles(
    db: Session = Depends(get_db),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    city: str | None = Query(default=None, max_length=120),
    province: str | None = Query(default=None, max_length=120),
    preferred_employment_type: schema.EmploymentPreference | None = Query(default=None),
    preferred_work_mode: schema.WorkPreference | None = Query(default=None),
    profile_visibility: schema.ProfileVisibility | None = Query(default=None),
) -> CandidateProfileListResponse:
    return candidate_profile_controller.list_candidate_profiles(
        db=db,
        offset=offset,
        limit=limit,
        city=city,
        province=province,
        preferred_employment_type=preferred_employment_type,
        preferred_work_mode=preferred_work_mode,
        profile_visibility=profile_visibility,
    )


@router.get("/{user_id}", response_model=CandidateProfileDetailResponse, status_code=200)
def get_candidate_profile(
    user_id: int = Path(..., gt=0, le=18446744073709551615),
    db: Session = Depends(get_db),
) -> CandidateProfileDetailResponse:
    return candidate_profile_controller.get_candidate_profile(db=db, user_id=user_id)


@router.patch("/{user_id}", response_model=CandidateProfileDetailResponse, status_code=200)
def update_candidate_profile(
    payload: CandidateProfileUpdate,
    user_id: int = Path(..., gt=0, le=18446744073709551615),
    db: Session = Depends(get_db),
) -> CandidateProfileDetailResponse:
    return candidate_profile_controller.update_candidate_profile(
        db=db, payload=payload, user_id=user_id
    )


@router.delete("/{user_id}", response_model=EmptyResponse, status_code=200)
def delete_candidate_profile(
    user_id: int = Path(..., gt=0, le=18446744073709551615),
    db: Session = Depends(get_db),
) -> EmptyResponse:
    return candidate_profile_controller.delete_candidate_profile(db=db, user_id=user_id)
