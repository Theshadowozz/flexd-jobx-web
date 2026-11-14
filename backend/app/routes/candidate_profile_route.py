from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.configs.database import get_db
from app.configs.dependencies import require_admin
from app.controllers import candidate_profile_controller as controller
from app.schemas.candidate_profile import CandidateProfileCreate, CandidateProfileUpdate
from app.schemas.common import UnsignedId

router = APIRouter(
    prefix="/candidate-profiles", tags=["candidate_profiles"], dependencies=[Depends(require_admin)]
)


@router.post("", status_code=201)
async def create(schema: CandidateProfileCreate, db: AsyncSession = Depends(get_db)):
    return await controller.create_candidate_profile(db, schema)


@router.get("")
async def list_(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    return await controller.list_candidate_profiles(db, limit, offset)


@router.get("/{user_id}")
async def get(user_id: UnsignedId, db: AsyncSession = Depends(get_db)):
    return await controller.get_candidate_profile(db, user_id)


@router.patch("/{user_id}")
async def update(
    user_id: UnsignedId, schema: CandidateProfileUpdate, db: AsyncSession = Depends(get_db)
):
    return await controller.update_candidate_profile(db, user_id, schema)


@router.delete("/{user_id}")
async def delete(user_id: UnsignedId, db: AsyncSession = Depends(get_db)):
    return await controller.delete_candidate_profile(db, user_id)
