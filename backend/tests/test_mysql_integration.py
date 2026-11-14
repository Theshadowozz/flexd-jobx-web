"""Opt-in, rollback-only MySQL tests. Requires externally provisioned test schema."""

import os
import unittest
import uuid

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.schemas.skill import SkillCreate, SkillUpdate
from app.schemas.skill_alias import SkillAliasCreate
from app.services import skill_alias_service, skill_service
from app.utils.exceptions import AppError


@unittest.skipUnless(os.environ.get("DB_TEST_URL"), "DB_TEST_URL not configured")
class MySQLIntegrationTests(unittest.TestCase):
    def setUp(self):
        url = make_url(os.environ["DB_TEST_URL"])
        if url.drivername != "mysql+pymysql" or not (url.database or "").endswith("_test"):
            self.fail("DB_TEST_URL must select mysql+pymysql and a separate *_test database")
        if url.host == "103.175.217.179":
            self.fail("Remote application host is forbidden for write tests")
        self.engine = create_engine(url, connect_args={"ssl_disabled": True})
        self.connection = self.engine.connect()
        self.transaction = self.connection.begin()
        self.db = Session(bind=self.connection, join_transaction_mode="create_savepoint")

    def tearDown(self):
        self.db.close()
        self.transaction.rollback()
        self.connection.close()
        self.engine.dispose()

    def test_skill_alias_constraint_and_crud(self):
        suffix = uuid.uuid4().hex
        skill = skill_service.create_skill(self.db, SkillCreate(canonical_name="Test", slug=suffix))
        alias = skill_alias_service.create_skill_alias(
            self.db, SkillAliasCreate(skill_id=skill.id, alias_name="Test", normalized_alias=suffix)
        )
        with self.assertRaises(AppError) as result:
            skill_alias_service.create_skill_alias(
                self.db,
                SkillAliasCreate(skill_id=skill.id, alias_name="Test", normalized_alias=suffix),
            )
        self.assertEqual(result.exception.status_code, 409)
        changed = skill_service.update_skill(self.db, skill.id, SkillUpdate(description="Changed"))
        self.assertEqual(changed.description, "Changed")
        skill_alias_service.delete_skill_alias(self.db, alias.id)
        skill_service.delete_skill(self.db, skill.id)
