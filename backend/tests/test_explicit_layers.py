import ast
import unittest
from pathlib import Path


class ExplicitLayerTests(unittest.TestCase):
    def test_no_annotated_in_application(self):
        root = Path(__file__).resolve().parents[1] / "app"
        for path in root.rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    self.assertNotEqual(node.id, "Annotated", str(path))
                if isinstance(node, ast.ImportFrom):
                    self.assertNotIn("Annotated", [alias.name for alias in node.names], str(path))

    def test_resource_services_have_explicit_operations(self):
        root = Path(__file__).resolve().parents[1] / "app"
        plurals = {
            "artifact_analysis": "artifact_analyses",
            "skill_alias": "skill_aliases",
            "job_match": "job_matches",
        }
        for path in (root / "models").glob("*.py"):
            entity = path.stem
            if entity in {"base", "__init__"}:
                continue
            plural = plurals.get(entity, entity + "s")
            for layer, suffix in (("services", "service"), ("controllers", "controller")):
                target = root / layer / f"{entity}_{suffix}.py"
                tree = ast.parse(target.read_text(encoding="utf-8"))
                functions = {
                    node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)
                }
                for name in (
                    f"create_{entity}",
                    f"list_{plural}",
                    f"get_{entity}",
                    f"update_{entity}",
                    f"delete_{entity}",
                ):
                    self.assertIn(name, functions, str(target))
                    self.assertIsNotNone(functions[name].returns, f"{target}: {name}")
                self.assertFalse(
                    {"invalid", "validate", "_write", "detail"} & functions.keys(), str(target)
                )
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                        self.assertNotIn(
                            node.func.id, {"getattr", "setattr", "hasattr", "inspect"}, str(target)
                        )

    def test_routes_use_five_explicit_decorators(self):
        root = Path(__file__).resolve().parents[1] / "app/routes"
        for path in root.glob("*.py"):
            if path.stem in {"__init__", "auth"}:
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"))
            methods = [
                decorator.func.attr
                for node in tree.body
                if isinstance(node, ast.FunctionDef)
                for decorator in node.decorator_list
                if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute)
            ]
            self.assertCountEqual(methods, ["post", "get", "get", "patch", "delete"], str(path))
