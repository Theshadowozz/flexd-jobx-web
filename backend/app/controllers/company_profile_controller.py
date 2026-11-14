from sqlalchemy.orm import Session

from app.schemas.company_profile import (
    CompanyProfileCreate,
    CompanyProfileDetailData,
    CompanyProfileDetailResponse,
    CompanyProfileListData,
    CompanyProfileListResponse,
    CompanyProfileRead,
    CompanyProfileUpdate,
)
from app.schemas.response import EmptyResponse, Pagination
from app.services import company_profile_service


def create_company_profile(
    db: Session, payload: CompanyProfileCreate
) -> CompanyProfileDetailResponse:
    company_profile = company_profile_service.create_company_profile(db=db, payload=payload)
    company_profile_data = CompanyProfileRead.model_validate(company_profile)
    return CompanyProfileDetailResponse(
        message={"success": "Data berhasil dibuat"},
        data=CompanyProfileDetailData(company_profile=company_profile_data),
    )


def get_company_profile(db: Session, company_profile_id: int) -> CompanyProfileDetailResponse:
    company_profile = company_profile_service.get_company_profile(
        db=db, company_profile_id=company_profile_id
    )
    company_profile_data = CompanyProfileRead.model_validate(company_profile)
    return CompanyProfileDetailResponse(
        message={"success": "Data berhasil diambil"},
        data=CompanyProfileDetailData(company_profile=company_profile_data),
    )


def update_company_profile(
    db: Session, company_profile_id: int, payload: CompanyProfileUpdate
) -> CompanyProfileDetailResponse:
    company_profile = company_profile_service.update_company_profile(
        db=db, company_profile_id=company_profile_id, payload=payload
    )
    company_profile_data = CompanyProfileRead.model_validate(company_profile)
    return CompanyProfileDetailResponse(
        message={"success": "Data berhasil diperbarui"},
        data=CompanyProfileDetailData(company_profile=company_profile_data),
    )


def list_company_profiles(
    db: Session,
    offset: int,
    limit: int,
    user_id: int | None = None,
    industry: str | None = None,
    city: str | None = None,
    province: str | None = None,
) -> CompanyProfileListResponse:
    records, total = company_profile_service.list_company_profiles(
        db=db,
        offset=offset,
        limit=limit,
        user_id=user_id,
        industry=industry,
        city=city,
        province=province,
    )
    items = [CompanyProfileRead.model_validate(record) for record in records]
    return CompanyProfileListResponse(
        message={"success": "Daftar data berhasil diambil"},
        data=CompanyProfileListData(
            company_profiles=items, pagination=Pagination(offset=offset, limit=limit, total=total)
        ),
    )


def delete_company_profile(db: Session, company_profile_id: int) -> EmptyResponse:
    company_profile_service.delete_company_profile(db=db, company_profile_id=company_profile_id)
    return EmptyResponse(message={"success": "Data berhasil dihapus"}, data={})
