from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.configs.database import get_db
from app.configs.dependencies import get_current_user
from app.controllers import auth_controller as controller
from app.models.user import User
from app.schemas.auth import ChangePassword, Login, Register
from app.utils.rate_limit import limit_login, limit_register

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=201, dependencies=[Depends(limit_register)])
async def register(schema: Register, db: AsyncSession = Depends(get_db)):
    return await controller.register(db, schema)


@router.post("/login", dependencies=[Depends(limit_login)])
async def login(schema: Login, db: AsyncSession = Depends(get_db)):
    return await controller.login(db, schema)


@router.get("/me")
async def me(user: User = Depends(get_current_user)):
    return controller.me(user)


@router.patch("/password")
async def change_password(
    schema: ChangePassword,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await controller.change_password(db, user, schema)
