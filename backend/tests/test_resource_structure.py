import ast
import unittest
from pathlib import Path


class ResourceStructureTests(unittest.TestCase):
    def test_removed_helpers_have_no_remaining_imports(self):
        root = Path(__file__).resolve().parents[1] / "app"
        for relative in (
            "controllers/_responses.py",
            "routes/_registration.py",
            "services/_persistence.py",
        ):
            with self.subTest(path=relative):
                self.assertFalse((root / relative).exists())
        for path in root.rglob("*.py"):
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
                if isinstance(node, ast.ImportFrom):
                    imported = [node.module or "", *(alias.name for alias in node.names)]
                    self.assertFalse(
                        any(
                            name.split(".")[-1] in {"_responses", "_registration", "_persistence"}
                            for name in imported
                        ),
                        str(path),
                    )
