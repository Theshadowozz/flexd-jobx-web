from app.schemas.artifact_skill_evidence import ArtifactSkillEvidenceRead
from app.services import artifact_skill_evidence_service as service
from app.utils.responses import empty_response, item_response, list_response


async def list_artifact_skill_evidences(db, limit, offset):
    records, total = await service.list_artifact_skill_evidences(db, limit, offset)
    return list_response(
        "Artifact skill evidences retrieved",
        "artifact_skill_evidences",
        [ArtifactSkillEvidenceRead.model_validate(r) for r in records],
        total,
        limit,
        offset,
    )


async def get_artifact_skill_evidence(db, record_id):
    record = await service.get_artifact_skill_evidence(db, record_id)
    return item_response(
        "Artifact skill evidence retrieved",
        "artifact_skill_evidence",
        ArtifactSkillEvidenceRead.model_validate(record),
    )


async def create_artifact_skill_evidence(db, schema):
    record = await service.create_artifact_skill_evidence(db, schema)
    return item_response(
        "Artifact skill evidence created",
        "artifact_skill_evidence",
        ArtifactSkillEvidenceRead.model_validate(record),
    )


async def update_artifact_skill_evidence(db, record_id, schema):
    record = await service.update_artifact_skill_evidence(db, record_id, schema)
    return item_response(
        "Artifact skill evidence updated",
        "artifact_skill_evidence",
        ArtifactSkillEvidenceRead.model_validate(record),
    )


async def delete_artifact_skill_evidence(db, record_id):
    await service.delete_artifact_skill_evidence(db, record_id)
    return empty_response("Artifact skill evidence deleted")
