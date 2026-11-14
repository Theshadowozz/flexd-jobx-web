from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.configs.database import get_db
from app.configs.dependencies import require_admin
from app.controllers import skill_controller as controller
from app.schemas.common import UnsignedId
from app.schemas.skill import SkillCreate, SkillUpdate

router = APIRouter(prefix="/skills", tags=["skills"], dependencies=[Depends(require_admin)])


@router.post("", status_code=201)
async def create(schema: SkillCreate, db: AsyncSession = Depends(get_db)):
    return await controller.create_skill(db, schema)


@router.get("")
async def list_(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    return await controller.list_skills(db, limit, offset)


@router.get("/{record_id}")
async def get(record_id: UnsignedId, db: AsyncSession = Depends(get_db)):
    return await controller.get_skill(db, record_id)


@router.patch("/{record_id}")
async def update(record_id: UnsignedId, schema: SkillUpdate, db: AsyncSession = Depends(get_db)):
    return await controller.update_skill(db, record_id, schema)


@router.delete("/{record_id}")
async def delete(record_id: UnsignedId, db: AsyncSession = Depends(get_db)):
    return await controller.delete_skill(db, record_id)
