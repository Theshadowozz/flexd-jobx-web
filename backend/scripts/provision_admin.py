"""Explicit operator command; never invoked at startup."""

import asyncio
from getpass import getpass

from sqlalchemy import select

from app.configs.database import get_session_factory
from app.models.user import User
from app.schemas.user import UserCreate
from app.services.user_service import create_user


async def provision():
    schema = UserCreate(
        name=input("Admin name: "),
        email=input("Admin email: "),
        password=getpass("Admin password (12+ characters): "),
        account_type="admin",
    )
    if getpass("Confirm password: ") != schema.password:
        raise SystemExit("Passwords do not match")
    factory = get_session_factory()
    try:
        async with factory() as db:
            existing = await db.scalar(
                select(User.id).where(User.email == str(schema.email).lower())
            )
            if existing is not None:
                raise SystemExit("Email already exists; no changes made")
            print("This command creates an active admin in the configured database.")
            if input("Type CREATE ADMIN to continue: ") != "CREATE ADMIN":
                raise SystemExit("Cancelled")
            await create_user(db, schema)
            print("Admin created")
    finally:
        await factory.kw["bind"].dispose()


if __name__ == "__main__":
    asyncio.run(provision())
