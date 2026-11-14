import unittest

from sqlalchemy.dialects.mysql import CHAR, dialect

from app.models import JobPost
from app.models.base import Base


class ModelTests(unittest.TestCase):
    def test_twelve_existing_tables_mapped(self):
        self.assertEqual(len(Base.metadata.tables), 12)

    def test_currency_matches_existing_fixed_width_char(self):
        self.assertIsInstance(JobPost.__table__.c.currency.type, CHAR)
        self.assertEqual(JobPost.__table__.c.currency.type.compile(dialect=dialect()), "CHAR(3)")
