from app.schemas.skill import SkillRead
from app.services import skill_service as service
from app.utils.responses import empty_response, item_response, list_response


async def list_skills(db, limit, offset):
    records, total = await service.list_skills(db, limit, offset)
    return list_response(
        "Skills retrieved",
        "skills",
        [SkillRead.model_validate(r) for r in records],
        total,
        limit,
        offset,
    )


async def get_skill(db, record_id):
    record = await service.get_skill(db, record_id)
    return item_response("Skill retrieved", "skill", SkillRead.model_validate(record))


async def create_skill(db, schema):
    record = await service.create_skill(db, schema)
    return item_response("Skill created", "skill", SkillRead.model_validate(record))


async def update_skill(db, record_id, schema):
    record = await service.update_skill(db, record_id, schema)
    return item_response("Skill updated", "skill", SkillRead.model_validate(record))


async def delete_skill(db, record_id):
    await service.delete_skill(db, record_id)
    return empty_response("Skill deleted")
