from sqlalchemy.orm import Session

from app.schemas.response import EmptyResponse, Pagination
from app.schemas.skill import (
    SkillCreate,
    SkillDetailData,
    SkillDetailResponse,
    SkillListData,
    SkillListResponse,
    SkillRead,
    SkillUpdate,
)
from app.services import skill_service


def create_skill(db: Session, payload: SkillCreate) -> SkillDetailResponse:
    skill = skill_service.create_skill(db=db, payload=payload)
    skill_data = SkillRead.model_validate(skill)
    return SkillDetailResponse(
        message={"success": "Data berhasil dibuat"}, data=SkillDetailData(skill=skill_data)
    )


def get_skill(db: Session, skill_id: int) -> SkillDetailResponse:
    skill = skill_service.get_skill(db=db, skill_id=skill_id)
    skill_data = SkillRead.model_validate(skill)
    return SkillDetailResponse(
        message={"success": "Data berhasil diambil"}, data=SkillDetailData(skill=skill_data)
    )


def update_skill(db: Session, skill_id: int, payload: SkillUpdate) -> SkillDetailResponse:
    skill = skill_service.update_skill(db=db, skill_id=skill_id, payload=payload)
    skill_data = SkillRead.model_validate(skill)
    return SkillDetailResponse(
        message={"success": "Data berhasil diperbarui"}, data=SkillDetailData(skill=skill_data)
    )


def list_skills(
    db: Session,
    offset: int,
    limit: int,
    category: str | None = None,
    parent_skill_id: int | None = None,
    search: str | None = None,
) -> SkillListResponse:
    records, total = skill_service.list_skills(
        db=db,
        offset=offset,
        limit=limit,
        category=category,
        parent_skill_id=parent_skill_id,
        search=search,
    )
    items = [SkillRead.model_validate(record) for record in records]
    return SkillListResponse(
        message={"success": "Daftar data berhasil diambil"},
        data=SkillListData(
            skills=items, pagination=Pagination(offset=offset, limit=limit, total=total)
        ),
    )


def delete_skill(db: Session, skill_id: int) -> EmptyResponse:
    skill_service.delete_skill(db=db, skill_id=skill_id)
    return EmptyResponse(message={"success": "Data berhasil dihapus"}, data={})
