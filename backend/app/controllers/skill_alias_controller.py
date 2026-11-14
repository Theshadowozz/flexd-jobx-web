from app.schemas.skill_alias import SkillAliasRead
from app.services import skill_alias_service as service
from app.utils.responses import empty_response, item_response, list_response


async def list_skill_aliases(db, limit, offset):
    records, total = await service.list_skill_aliases(db, limit, offset)
    return list_response(
        "Skill aliases retrieved",
        "skill_aliases",
        [SkillAliasRead.model_validate(r) for r in records],
        total,
        limit,
        offset,
    )


async def get_skill_alias(db, record_id):
    record = await service.get_skill_alias(db, record_id)
    return item_response(
        "Skill alias retrieved", "skill_alias", SkillAliasRead.model_validate(record)
    )


async def create_skill_alias(db, schema):
    record = await service.create_skill_alias(db, schema)
    return item_response(
        "Skill alias created", "skill_alias", SkillAliasRead.model_validate(record)
    )


async def update_skill_alias(db, record_id, schema):
    record = await service.update_skill_alias(db, record_id, schema)
    return item_response(
        "Skill alias updated", "skill_alias", SkillAliasRead.model_validate(record)
    )


async def delete_skill_alias(db, record_id):
    await service.delete_skill_alias(db, record_id)
    return empty_response("Skill alias deleted")
