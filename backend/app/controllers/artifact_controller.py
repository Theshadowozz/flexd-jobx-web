from app.schemas.artifact import ArtifactRead
from app.services import artifact_service as service
from app.utils.responses import empty_response, item_response, list_response


async def list_artifacts(db, limit, offset):
    records, total = await service.list_artifacts(db, limit, offset)
    return list_response(
        "Artifacts retrieved",
        "artifacts",
        [ArtifactRead.model_validate(r) for r in records],
        total,
        limit,
        offset,
    )


async def get_artifact(db, record_id):
    record = await service.get_artifact(db, record_id)
    return item_response("Artifact retrieved", "artifact", ArtifactRead.model_validate(record))


async def create_artifact(db, schema):
    record = await service.create_artifact(db, schema)
    return item_response("Artifact created", "artifact", ArtifactRead.model_validate(record))


async def update_artifact(db, record_id, schema):
    record = await service.update_artifact(db, record_id, schema)
    return item_response("Artifact updated", "artifact", ArtifactRead.model_validate(record))


async def delete_artifact(db, record_id):
    await service.delete_artifact(db, record_id)
    return empty_response("Artifact deleted")
