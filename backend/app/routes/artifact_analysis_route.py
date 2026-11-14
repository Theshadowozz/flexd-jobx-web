from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.configs.database import get_db
from app.configs.dependencies import require_admin
from app.controllers import artifact_analysis_controller as controller
from app.schemas.artifact_analysis import ArtifactAnalysisCreate, ArtifactAnalysisUpdate
from app.schemas.common import UnsignedId

router = APIRouter(
    prefix="/artifact-analyses", tags=["artifact_analyses"], dependencies=[Depends(require_admin)]
)


@router.post("", status_code=201)
async def create(schema: ArtifactAnalysisCreate, db: AsyncSession = Depends(get_db)):
    return await controller.create_artifact_analysis(db, schema)


@router.get("")
async def list_(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    return await controller.list_artifact_analyses(db, limit, offset)


@router.get("/{record_id}")
async def get(record_id: UnsignedId, db: AsyncSession = Depends(get_db)):
    return await controller.get_artifact_analysis(db, record_id)


@router.patch("/{record_id}")
async def update(
    record_id: UnsignedId, schema: ArtifactAnalysisUpdate, db: AsyncSession = Depends(get_db)
):
    return await controller.update_artifact_analysis(db, record_id, schema)


@router.delete("/{record_id}")
async def delete(record_id: UnsignedId, db: AsyncSession = Depends(get_db)):
    return await controller.delete_artifact_analysis(db, record_id)
