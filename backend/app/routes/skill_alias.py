from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app.configs.database import get_db
from app.configs.dependencies import require_admin
from app.controllers import skill_alias_controller
from app.schemas.response import EmptyResponse
from app.schemas.skill_alias import (
    SkillAliasCreate,
    SkillAliasDetailResponse,
    SkillAliasListResponse,
    SkillAliasUpdate,
)

router = APIRouter(
    prefix="/skill-aliases", tags=["Skill aliases"], dependencies=[Depends(require_admin)]
)


@router.post("", response_model=SkillAliasDetailResponse, status_code=201)
def create_skill_alias(
    payload: SkillAliasCreate,
    db: Session = Depends(get_db),
) -> SkillAliasDetailResponse:
    return skill_alias_controller.create_skill_alias(db=db, payload=payload)


@router.get("", response_model=SkillAliasListResponse, status_code=200)
def list_skill_aliases(
    db: Session = Depends(get_db),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    skill_id: int | None = Query(default=None, gt=0, le=18446744073709551615),
    search: str | None = Query(default=None, max_length=140),
) -> SkillAliasListResponse:
    return skill_alias_controller.list_skill_aliases(
        db=db, offset=offset, limit=limit, skill_id=skill_id, search=search
    )


@router.get("/{skill_alias_id}", response_model=SkillAliasDetailResponse, status_code=200)
def get_skill_alias(
    skill_alias_id: int = Path(..., gt=0, le=18446744073709551615),
    db: Session = Depends(get_db),
) -> SkillAliasDetailResponse:
    return skill_alias_controller.get_skill_alias(db=db, skill_alias_id=skill_alias_id)


@router.patch("/{skill_alias_id}", response_model=SkillAliasDetailResponse, status_code=200)
def update_skill_alias(
    payload: SkillAliasUpdate,
    skill_alias_id: int = Path(..., gt=0, le=18446744073709551615),
    db: Session = Depends(get_db),
) -> SkillAliasDetailResponse:
    return skill_alias_controller.update_skill_alias(
        db=db, payload=payload, skill_alias_id=skill_alias_id
    )


@router.delete("/{skill_alias_id}", response_model=EmptyResponse, status_code=200)
def delete_skill_alias(
    skill_alias_id: int = Path(..., gt=0, le=18446744073709551615),
    db: Session = Depends(get_db),
) -> EmptyResponse:
    return skill_alias_controller.delete_skill_alias(db=db, skill_alias_id=skill_alias_id)
