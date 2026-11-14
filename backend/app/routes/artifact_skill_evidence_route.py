from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.configs.database import get_db
from app.configs.dependencies import require_admin
from app.controllers import artifact_skill_evidence_controller as controller
from app.schemas.artifact_skill_evidence import (
    ArtifactSkillEvidenceCreate,
    ArtifactSkillEvidenceUpdate,
)
from app.schemas.common import UnsignedId

router = APIRouter(
    prefix="/artifact-skill-evidences",
    tags=["artifact_skill_evidences"],
    dependencies=[Depends(require_admin)],
)


@router.post("", status_code=201)
async def create(schema: ArtifactSkillEvidenceCreate, db: AsyncSession = Depends(get_db)):
    return await controller.create_artifact_skill_evidence(db, schema)


@router.get("")
async def list_(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    return await controller.list_artifact_skill_evidences(db, limit, offset)


@router.get("/{record_id}")
async def get(record_id: UnsignedId, db: AsyncSession = Depends(get_db)):
    return await controller.get_artifact_skill_evidence(db, record_id)


@router.patch("/{record_id}")
async def update(
    record_id: UnsignedId, schema: ArtifactSkillEvidenceUpdate, db: AsyncSession = Depends(get_db)
):
    return await controller.update_artifact_skill_evidence(db, record_id, schema)


@router.delete("/{record_id}")
async def delete(record_id: UnsignedId, db: AsyncSession = Depends(get_db)):
    return await controller.delete_artifact_skill_evidence(db, record_id)
