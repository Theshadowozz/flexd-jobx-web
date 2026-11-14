from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app.configs.database import get_db
from app.configs.dependencies import require_admin
from app.controllers import skill_controller
from app.schemas.response import EmptyResponse
from app.schemas.skill import SkillCreate, SkillDetailResponse, SkillListResponse, SkillUpdate

router = APIRouter(prefix="/skills", tags=["Skills"], dependencies=[Depends(require_admin)])


@router.post("", response_model=SkillDetailResponse, status_code=201)
def create_skill(
    payload: SkillCreate,
    db: Session = Depends(get_db),
) -> SkillDetailResponse:
    return skill_controller.create_skill(db=db, payload=payload)


@router.get("", response_model=SkillListResponse, status_code=200)
def list_skills(
    db: Session = Depends(get_db),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    category: str | None = Query(default=None, max_length=100),
    parent_skill_id: int | None = Query(default=None, gt=0, le=18446744073709551615),
    search: str | None = Query(default=None, max_length=140),
) -> SkillListResponse:
    return skill_controller.list_skills(
        db=db,
        offset=offset,
        limit=limit,
        category=category,
        parent_skill_id=parent_skill_id,
        search=search,
    )


@router.get("/{skill_id}", response_model=SkillDetailResponse, status_code=200)
def get_skill(
    skill_id: int = Path(..., gt=0, le=18446744073709551615),
    db: Session = Depends(get_db),
) -> SkillDetailResponse:
    return skill_controller.get_skill(db=db, skill_id=skill_id)


@router.patch("/{skill_id}", response_model=SkillDetailResponse, status_code=200)
def update_skill(
    payload: SkillUpdate,
    skill_id: int = Path(..., gt=0, le=18446744073709551615),
    db: Session = Depends(get_db),
) -> SkillDetailResponse:
    return skill_controller.update_skill(db=db, payload=payload, skill_id=skill_id)


@router.delete("/{skill_id}", response_model=EmptyResponse, status_code=200)
def delete_skill(
    skill_id: int = Path(..., gt=0, le=18446744073709551615),
    db: Session = Depends(get_db),
) -> EmptyResponse:
    return skill_controller.delete_skill(db=db, skill_id=skill_id)
