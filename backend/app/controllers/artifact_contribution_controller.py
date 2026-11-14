from app.schemas.artifact_contribution import ArtifactContributionRead
from app.services import artifact_contribution_service as service
from app.utils.responses import empty_response, item_response, list_response


async def list_artifact_contributions(db, limit, offset):
    records, total = await service.list_artifact_contributions(db, limit, offset)
    return list_response(
        "Artifact contributions retrieved",
        "artifact_contributions",
        [ArtifactContributionRead.model_validate(r) for r in records],
        total,
        limit,
        offset,
    )


async def get_artifact_contribution(db, record_id):
    record = await service.get_artifact_contribution(db, record_id)
    return item_response(
        "Artifact contribution retrieved",
        "artifact_contribution",
        ArtifactContributionRead.model_validate(record),
    )


async def create_artifact_contribution(db, schema):
    record = await service.create_artifact_contribution(db, schema)
    return item_response(
        "Artifact contribution created",
        "artifact_contribution",
        ArtifactContributionRead.model_validate(record),
    )


async def update_artifact_contribution(db, record_id, schema):
    record = await service.update_artifact_contribution(db, record_id, schema)
    return item_response(
        "Artifact contribution updated",
        "artifact_contribution",
        ArtifactContributionRead.model_validate(record),
    )


async def delete_artifact_contribution(db, record_id):
    await service.delete_artifact_contribution(db, record_id)
    return empty_response("Artifact contribution deleted")
