from app.schemas.artifact_analysis import ArtifactAnalysisRead
from app.services import artifact_analysis_service as service
from app.utils.responses import empty_response, item_response, list_response


async def list_artifact_analyses(db, limit, offset):
    records, total = await service.list_artifact_analyses(db, limit, offset)
    return list_response(
        "Artifact analyses retrieved",
        "artifact_analyses",
        [ArtifactAnalysisRead.model_validate(r) for r in records],
        total,
        limit,
        offset,
    )


async def get_artifact_analysis(db, record_id):
    record = await service.get_artifact_analysis(db, record_id)
    return item_response(
        "Artifact analysis retrieved",
        "artifact_analysis",
        ArtifactAnalysisRead.model_validate(record),
    )


async def create_artifact_analysis(db, schema):
    record = await service.create_artifact_analysis(db, schema)
    return item_response(
        "Artifact analysis created",
        "artifact_analysis",
        ArtifactAnalysisRead.model_validate(record),
    )


async def update_artifact_analysis(db, record_id, schema):
    record = await service.update_artifact_analysis(db, record_id, schema)
    return item_response(
        "Artifact analysis updated",
        "artifact_analysis",
        ArtifactAnalysisRead.model_validate(record),
    )


async def delete_artifact_analysis(db, record_id):
    await service.delete_artifact_analysis(db, record_id)
    return empty_response("Artifact analysis deleted")
