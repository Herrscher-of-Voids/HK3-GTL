"""魂钢研究首件物料回归；验证前序产物与研究顺序，不代表自然通关。"""
import copy
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "src/main/resources/data/hk3gtl/research"
IDS = ("industrial_soulium_polymerization", "industrial_soulium_reconstruction",
       "industrial_soulium_processing", "industrial_prepare_sra", "industrial_prepare_spm",
       "industrial_soulium_data_substrate", "industrial_soulium_ingot")
ROOTS = {
    "hk3gtl:coated_nano_swarm", "gtceu:tungsten_steel_dust", "soulium_precursor_fluid",
    "hk3gtl:reconstruction_rule_carrier", "honkai_stabilization_medium", "honkai_coolant",
    "gtceu:platinum_foil", "gtceu:tungsten_steel_plate",
    "gtceu:soldering_alloy",
    # I09的真实副产不能冒充已经由I14压铸完成的粗魂钢。
    "hk3gtl:soulium_polymerization_residue",
}


def materials(plan, direction):
    return {entry["id"] for key in ("item_" + direction, "fluid_" + direction)
            for entry in plan[key]}


def closure(plans, completed, omitted=()):
    stock = set(ROOTS)
    while True:
        previous = set(stock)
        for plan in plans:
            if (plan["id"] not in omitted and set(plan["requirements"]) <= completed
                    and materials(plan, "inputs") <= stock):
                stock |= materials(plan, "outputs")
        if stock == previous:
            return stock


class SouliumResearchBootstrapTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        plans = json.loads((DATA / "industrial_processes.json").read_text(encoding="utf-8"))
        cls.plans = [p for p in plans["recipes"] if p["id"] in IDS]
        cls.by_id = {p["id"]: p for p in cls.plans}
        execution = json.loads((DATA / "research_execution.json").read_text(encoding="utf-8"))
        cls.contracts = {p["id"]: p for p in execution["topics"]}

    def test_sra_requires_i14_output_but_not_sra_permission(self):
        gates = {"RN-SPC"}
        sample = "hk3gtl:research_specimen_sra"
        self.assertIn(sample, closure(self.plans, gates))
        self.assertNotIn(sample, closure(self.plans, gates, {"industrial_soulium_polymerization"}))
        self.assertNotIn(sample, closure(self.plans, set()))

    def test_spm_requires_i15_output_but_not_spm_permission(self):
        gates = {"RN-SPC", "RN-SRA"}
        sample = "hk3gtl:research_specimen_spm"
        stock = closure(self.plans, gates)
        self.assertIn(sample, stock)
        self.assertNotIn("material:soulium/plate", stock)
        for step in ("industrial_soulium_polymerization", "industrial_soulium_reconstruction"):
            self.assertNotIn(sample, closure(self.plans, gates, {step}), step)
        self.assertNotIn(sample, closure(self.plans, {"RN-SPC"}))

    def test_original_residue_bypass_and_missing_substrate_are_detected(self):
        plans = copy.deepcopy(self.plans)
        by_id = {p["id"]: p for p in plans}
        by_id["industrial_prepare_sra"]["item_inputs"][0]["id"] = "hk3gtl:soulium_polymerization_residue"
        self.assertIn("hk3gtl:research_specimen_sra", closure(
            plans, {"RN-SPC"}, {"industrial_soulium_polymerization"}))
        by_id["industrial_prepare_spm"]["item_inputs"][0]["id"] = "hk3gtl:soulium_data_substrate"
        self.assertNotIn("hk3gtl:research_specimen_spm", closure(plans, {"RN-SPC", "RN-SRA"}))

    def test_substrate_and_ingot_require_completed_spm_and_all_production_steps(self):
        gates = {"RN-SPC", "RN-SRA", "RN-SPM"}
        for material in ("hk3gtl:soulium_data_substrate", "material:soulium/ingot"):
            self.assertIn(material, closure(self.plans, gates))
            self.assertNotIn(material, closure(self.plans, gates - {"RN-SPM"}))
            for step in ("industrial_soulium_polymerization", "industrial_soulium_reconstruction"):
                self.assertNotIn(material, closure(self.plans, gates, {step}))

    def test_contract_matches_MAX_preparation_with_existing_material_costs(self):
        for code in ("sra", "spm"):
            plan = self.by_id["industrial_prepare_" + code]
            contract = self.contracts["RN-" + code.upper()]
            self.assertEqual("hk3gtl:" + contract["precursor"], plan["item_inputs"][0]["id"])
            self.assertEqual([1, 2, 2], [p["count"] for p in plan["item_inputs"]])
            self.assertEqual(480, plan["ticks"])
            self.assertEqual(14, plan["energy_tier"])
            self.assertEqual(contract["prerequisites"], plan["requirements"])

    def test_ingot_and_plate_routes_have_exclusive_fluid_inputs(self):
        ingot = self.by_id["industrial_soulium_ingot"]
        plate = self.by_id["industrial_soulium_processing"]
        self.assertEqual(ingot["item_inputs"], plate["item_inputs"])
        for selected, other in ((ingot, plate), (plate, ingot)):
            supplied = {p["id"] for p in selected["fluid_inputs"]}
            self.assertFalse({p["id"] for p in other["fluid_inputs"]} <= supplied)


if __name__ == "__main__":
    unittest.main()
