from app.schemas.job_skill_requirement import JobSkillRequirementRead
from app.services import job_skill_requirement_service as service
from app.utils.responses import empty_response, item_response, list_response


async def list_job_skill_requirements(db, limit, offset):
    records, total = await service.list_job_skill_requirements(db, limit, offset)
    return list_response(
        "Job skill requirements retrieved",
        "job_skill_requirements",
        [JobSkillRequirementRead.model_validate(r) for r in records],
        total,
        limit,
        offset,
    )


async def get_job_skill_requirement(db, record_id):
    record = await service.get_job_skill_requirement(db, record_id)
    return item_response(
        "Job skill requirement retrieved",
        "job_skill_requirement",
        JobSkillRequirementRead.model_validate(record),
    )


async def create_job_skill_requirement(db, schema):
    record = await service.create_job_skill_requirement(db, schema)
    return item_response(
        "Job skill requirement created",
        "job_skill_requirement",
        JobSkillRequirementRead.model_validate(record),
    )


async def update_job_skill_requirement(db, record_id, schema):
    record = await service.update_job_skill_requirement(db, record_id, schema)
    return item_response(
        "Job skill requirement updated",
        "job_skill_requirement",
        JobSkillRequirementRead.model_validate(record),
    )


async def delete_job_skill_requirement(db, record_id):
    await service.delete_job_skill_requirement(db, record_id)
    return empty_response("Job skill requirement deleted")
