from app.schemas.job_post import JobPostRead
from app.services import job_post_service as service
from app.utils.responses import empty_response, item_response, list_response


async def list_job_posts(db, limit, offset):
    records, total = await service.list_job_posts(db, limit, offset)
    return list_response(
        "Job posts retrieved",
        "job_posts",
        [JobPostRead.model_validate(r) for r in records],
        total,
        limit,
        offset,
    )


async def get_job_post(db, record_id):
    record = await service.get_job_post(db, record_id)
    return item_response("Job post retrieved", "job_post", JobPostRead.model_validate(record))


async def create_job_post(db, schema):
    record = await service.create_job_post(db, schema)
    return item_response("Job post created", "job_post", JobPostRead.model_validate(record))


async def update_job_post(db, record_id, schema):
    record = await service.update_job_post(db, record_id, schema)
    return item_response("Job post updated", "job_post", JobPostRead.model_validate(record))


async def delete_job_post(db, record_id):
    await service.delete_job_post(db, record_id)
    return empty_response("Job post deleted")
