from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app.configs.database import get_db
from app.configs.dependencies import require_admin
from app.controllers import company_profile_controller
from app.schemas.company_profile import (
    CompanyProfileCreate,
    CompanyProfileDetailResponse,
    CompanyProfileListResponse,
    CompanyProfileUpdate,
)
from app.schemas.response import EmptyResponse

router = APIRouter(
    prefix="/company-profiles", tags=["Company profiles"], dependencies=[Depends(require_admin)]
)


@router.post("", response_model=CompanyProfileDetailResponse, status_code=201)
def create_company_profile(
    payload: CompanyProfileCreate,
    db: Session = Depends(get_db),
) -> CompanyProfileDetailResponse:
    return company_profile_controller.create_company_profile(db=db, payload=payload)


@router.get("", response_model=CompanyProfileListResponse, status_code=200)
def list_company_profiles(
    db: Session = Depends(get_db),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    user_id: int | None = Query(default=None, gt=0, le=18446744073709551615),
    industry: str | None = Query(default=None, max_length=120),
    city: str | None = Query(default=None, max_length=120),
    province: str | None = Query(default=None, max_length=120),
) -> CompanyProfileListResponse:
    return company_profile_controller.list_company_profiles(
        db=db,
        offset=offset,
        limit=limit,
        user_id=user_id,
        industry=industry,
        city=city,
        province=province,
    )


@router.get("/{company_profile_id}", response_model=CompanyProfileDetailResponse, status_code=200)
def get_company_profile(
    company_profile_id: int = Path(..., gt=0, le=18446744073709551615),
    db: Session = Depends(get_db),
) -> CompanyProfileDetailResponse:
    return company_profile_controller.get_company_profile(
        db=db, company_profile_id=company_profile_id
    )


@router.patch("/{company_profile_id}", response_model=CompanyProfileDetailResponse, status_code=200)
def update_company_profile(
    payload: CompanyProfileUpdate,
    company_profile_id: int = Path(..., gt=0, le=18446744073709551615),
    db: Session = Depends(get_db),
) -> CompanyProfileDetailResponse:
    return company_profile_controller.update_company_profile(
        db=db, payload=payload, company_profile_id=company_profile_id
    )


@router.delete("/{company_profile_id}", response_model=EmptyResponse, status_code=200)
def delete_company_profile(
    company_profile_id: int = Path(..., gt=0, le=18446744073709551615),
    db: Session = Depends(get_db),
) -> EmptyResponse:
    return company_profile_controller.delete_company_profile(
        db=db, company_profile_id=company_profile_id
    )
