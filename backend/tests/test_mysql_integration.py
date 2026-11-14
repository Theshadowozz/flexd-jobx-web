"""Opt-in MySQL test. Requires precreated tables in a dedicated local *_test schema."""

from uuid import uuid4

import pytest
from sqlalchemy import select, text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.configs.settings import get_settings
from app.models import Skill
from app.schemas.skill import SkillCreate
from app.schemas.skill_alias import SkillAliasCreate
from app.services.skill_alias_service import create_skill_alias
from app.services.skill_service import create_skill


async def test_mysql_transactions_and_unsigned_ids():
    raw_url = get_settings().db_test_url.get_secret_value()
    if not raw_url:
        pytest.skip("DB_TEST_URL not configured; MySQL integration not run")
    url = make_url(raw_url)
    if (
        url.drivername != "mysql+asyncmy"
        or url.host not in {"localhost", "127.0.0.1"}
        or not url.database
        or not url.database.endswith("_test")
    ):
        pytest.fail("DB_TEST_URL must use mysql+asyncmy, localhost/127.0.0.1, and *_test schema")
    engine = create_async_engine(url, connect_args={"ssl": False})
    try:
        async with engine.connect() as connection:
            outer = await connection.begin()
            suffix = uuid4().hex
            try:
                db = AsyncSession(
                    bind=connection,
                    expire_on_commit=False,
                    join_transaction_mode="create_savepoint",
                )
                async with db:
                    assert await db.scalar(text("SELECT VERSION()"))
                    skill = await create_skill(
                        db, SkillCreate(canonical_name="Integration test", slug=f"test-{suffix}")
                    )
                    alias = await create_skill_alias(
                        db, SkillAliasCreate(skill_id=skill.id, alias_name=f"Alias {suffix}")
                    )
                    assert alias.normalized_alias == f"alias {suffix}"
            finally:
                await outer.rollback()
            assert (
                await connection.scalar(select(Skill.id).where(Skill.slug == f"test-{suffix}"))
                is None
            )
    finally:
        await engine.dispose()
