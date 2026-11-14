from sqlalchemy.orm import Session

from app.schemas.response import EmptyResponse, Pagination
from app.schemas.skill_alias import (
    SkillAliasCreate,
    SkillAliasDetailData,
    SkillAliasDetailResponse,
    SkillAliasListData,
    SkillAliasListResponse,
    SkillAliasRead,
    SkillAliasUpdate,
)
from app.services import skill_alias_service


def create_skill_alias(db: Session, payload: SkillAliasCreate) -> SkillAliasDetailResponse:
    skill_alias = skill_alias_service.create_skill_alias(db=db, payload=payload)
    skill_alias_data = SkillAliasRead.model_validate(skill_alias)
    return SkillAliasDetailResponse(
        message={"success": "Data berhasil dibuat"},
        data=SkillAliasDetailData(skill_alias=skill_alias_data),
    )


def get_skill_alias(db: Session, skill_alias_id: int) -> SkillAliasDetailResponse:
    skill_alias = skill_alias_service.get_skill_alias(db=db, skill_alias_id=skill_alias_id)
    skill_alias_data = SkillAliasRead.model_validate(skill_alias)
    return SkillAliasDetailResponse(
        message={"success": "Data berhasil diambil"},
        data=SkillAliasDetailData(skill_alias=skill_alias_data),
    )


def update_skill_alias(
    db: Session, skill_alias_id: int, payload: SkillAliasUpdate
) -> SkillAliasDetailResponse:
    skill_alias = skill_alias_service.update_skill_alias(
        db=db, skill_alias_id=skill_alias_id, payload=payload
    )
    skill_alias_data = SkillAliasRead.model_validate(skill_alias)
    return SkillAliasDetailResponse(
        message={"success": "Data berhasil diperbarui"},
        data=SkillAliasDetailData(skill_alias=skill_alias_data),
    )


def list_skill_aliases(
    db: Session, offset: int, limit: int, skill_id: int | None = None, search: str | None = None
) -> SkillAliasListResponse:
    records, total = skill_alias_service.list_skill_aliases(
        db=db, offset=offset, limit=limit, skill_id=skill_id, search=search
    )
    items = [SkillAliasRead.model_validate(record) for record in records]
    return SkillAliasListResponse(
        message={"success": "Daftar data berhasil diambil"},
        data=SkillAliasListData(
            skill_aliases=items, pagination=Pagination(offset=offset, limit=limit, total=total)
        ),
    )


def delete_skill_alias(db: Session, skill_alias_id: int) -> EmptyResponse:
    skill_alias_service.delete_skill_alias(db=db, skill_alias_id=skill_alias_id)
    return EmptyResponse(message={"success": "Data berhasil dihapus"}, data={})
