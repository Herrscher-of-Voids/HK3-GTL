from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from worldbubble_catalog_preflight import build_closure


class WorldBubbleCatalogPreflightTest(unittest.TestCase):
    def write_fixture(self, root: Path, recipes: list[dict], roots: list[dict] | None = None) -> Path:
        audit = root / "audit"
        audit.mkdir()
        (audit / "manifest.json").write_text(json.dumps({"revision": 1, "captured_at": "test"}), encoding="utf-8")
        (audit / "report.json").write_text(json.dumps({
            "export_complete": True,
            "registered_recipe_export_complete": True,
            "recipe_snapshot_unchanged": True,
            "survival_catalog_verified": False,
            "gameplay_verified": False,
        }), encoding="utf-8")
        (audit / "registries.json").write_text(json.dumps({
            "items": ["minecraft:iron_ore", "minecraft:iron_ingot", "hk3gtl:loop"],
            "fluids": [{"id": "hk3gtl:liquid"}],
        }), encoding="utf-8")
        (audit / "research-gates.json").write_text(json.dumps({"entries": []}), encoding="utf-8")
        with (audit / "recipes.jsonl").open("w", encoding="utf-8") as stream:
            for row in recipes:
                stream.write(json.dumps(row) + "\n")
        root_path = None
        if roots is not None:
            root_path = root / "roots.json"
            root_path.write_text(json.dumps({"roots": roots}), encoding="utf-8")
        return audit, root_path

    @staticmethod
    def recipe(recipe_id, inputs, output, view="gt_full_codec_and_resolved_candidates", gates=None):
        return {
            "id": recipe_id,
            "type": "fixture",
            "view": view,
            "gates": gates or [],
            "survival_eligibility": "UNVERIFIED",
            "resolved_inputs": {"items": [{"alternatives": [{"id": value} for value in slot]} for slot in inputs], "fluids": []},
            "resolved_outputs": {"items": [{"alternatives": [{"id": output}]}], "fluids": []},
        }

    def test_no_roots_is_candidate_only(self):
        with tempfile.TemporaryDirectory() as directory:
            audit, roots = self.write_fixture(Path(directory), [self.recipe("fixture:smelt", [["minecraft:iron_ore"]], "minecraft:iron_ingot")])
            result = build_closure(audit, roots)
            self.assertFalse(result["approved"])
            self.assertEqual(result["closure"]["reachable"], 0)
            self.assertEqual(result["closure"]["blocked"], 1)
            self.assertEqual(result["status"], "CANDIDATES_ONLY_NOT_AN_APPROVED_DROP_POOL")

    def test_root_reaches_full_recipe_in_candidate_graph(self):
        with tempfile.TemporaryDirectory() as directory:
            audit, roots = self.write_fixture(Path(directory), [self.recipe("fixture:smelt", [["minecraft:iron_ore"]], "minecraft:iron_ingot")], [{
                "id": "minecraft:iron_ore", "kind": "item", "tier": 0, "source_type": "worldgen", "source": "fixture"
            }])
            result = build_closure(audit, roots)
            self.assertFalse(result["approved"])
            self.assertEqual(result["closure"]["reachable"], 2)
            self.assertIn("不证明生存获取", result["closure"]["reachable_scope"])
            self.assertEqual(result["candidate_pool"]["items"], ["minecraft:iron_ingot"])

    def test_verified_rows_and_roots_never_approve_catalog(self):
        with tempfile.TemporaryDirectory() as directory:
            recipe = self.recipe("fixture:smelt", [["minecraft:iron_ore"]], "minecraft:iron_ingot")
            recipe["survival_eligibility"] = "VERIFIED"
            audit, roots = self.write_fixture(Path(directory), [recipe], [{
                "id": "minecraft:iron_ore", "kind": "item", "tier": 0,
                "source_type": "worldgen", "source": "fixture"
            }])
            report_path = audit / "report.json"
            report = json.loads(report_path.read_text(encoding="utf-8"))
            report["survival_catalog_verified"] = True
            report_path.write_text(json.dumps(report), encoding="utf-8")
            result = build_closure(audit, roots)
            self.assertEqual(result["closure"]["reachable"], 2)
            self.assertFalse(result["approved"])
            self.assertEqual(result["status"], "CANDIDATES_ONLY_NOT_AN_APPROVED_DROP_POOL")

    def test_dynamic_recipe_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            audit, roots = self.write_fixture(Path(directory), [self.recipe("fixture:dynamic", [["minecraft:iron_ore"]], "hk3gtl:loop", view="generic_ingredients_and_result_only")], [{
                "id": "minecraft:iron_ore", "kind": "item", "tier": 0, "source_type": "worldgen", "source": "fixture"
            }])
            result = build_closure(audit, roots)
            self.assertEqual(result["closure"]["dynamic_unresolved"], 1)
            self.assertEqual(result["closure"]["nodes"]["hk3gtl:loop"], "dynamic_unresolved")

    def test_recipe_cycle_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            audit, roots = self.write_fixture(Path(directory), [self.recipe("fixture:cycle", [["hk3gtl:loop"]], "hk3gtl:loop")])
            result = build_closure(audit, roots)
            self.assertEqual(result["closure"]["cycle"], 1)
            self.assertEqual(result["closure"]["cycles"], ["hk3gtl:loop"])


if __name__ == "__main__":
    unittest.main()
