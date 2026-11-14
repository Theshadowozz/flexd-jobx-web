from app.schemas.user import UserRead
from app.services import user_service as service
from app.utils.responses import empty_response, item_response, list_response


async def list_users(db, limit, offset):
    records, total = await service.list_users(db, limit, offset)
    return list_response(
        "Users retrieved",
        "users",
        [UserRead.model_validate(r) for r in records],
        total,
        limit,
        offset,
    )


async def get_user(db, record_id):
    record = await service.get_user(db, record_id)
    return item_response("User retrieved", "user", UserRead.model_validate(record))


async def create_user(db, schema):
    record = await service.create_user(db, schema)
    return item_response("User created", "user", UserRead.model_validate(record))


async def update_user(db, record_id, schema):
    record = await service.update_user(db, record_id, schema)
    return item_response("User updated", "user", UserRead.model_validate(record))


async def delete_user(db, record_id):
    await service.delete_user(db, record_id)
    return empty_response("User deleted")
