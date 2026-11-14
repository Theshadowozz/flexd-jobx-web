from app.schemas.user import UserRead
from app.services import auth_service
from app.utils.responses import empty_response, item_response


async def register(db, schema):
    user = await auth_service.register(db, schema)
    return item_response("Registration successful", "user", UserRead.model_validate(user))


async def login(db, schema):
    user, token = await auth_service.login(db, schema)
    return {
        "message": {"success": "Login successful"},
        "error": {},
        "data": {
            "user": UserRead.model_validate(user).model_dump(mode="json"),
            "auth": {"access_token": token, "token_type": "bearer"},
        },
    }


def me(user):
    return item_response("User retrieved", "user", UserRead.model_validate(user))


async def change_password(db, user, schema):
    await auth_service.change_password(db, user.id, schema)
    return empty_response("Password changed")
