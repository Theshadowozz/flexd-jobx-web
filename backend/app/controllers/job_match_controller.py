from app.schemas.job_match import JobMatchRead
from app.services import job_match_service as service
from app.utils.responses import empty_response, item_response, list_response


async def list_job_matches(db, limit, offset):
    records, total = await service.list_job_matches(db, limit, offset)
    return list_response(
        "Job matches retrieved",
        "job_matches",
        [JobMatchRead.model_validate(r) for r in records],
        total,
        limit,
        offset,
    )


async def get_job_match(db, record_id):
    record = await service.get_job_match(db, record_id)
    return item_response("Job match retrieved", "job_match", JobMatchRead.model_validate(record))


async def create_job_match(db, schema):
    record = await service.create_job_match(db, schema)
    return item_response("Job match created", "job_match", JobMatchRead.model_validate(record))


async def update_job_match(db, record_id, schema):
    record = await service.update_job_match(db, record_id, schema)
    return item_response("Job match updated", "job_match", JobMatchRead.model_validate(record))


async def delete_job_match(db, record_id):
    await service.delete_job_match(db, record_id)
    return empty_response("Job match deleted")
