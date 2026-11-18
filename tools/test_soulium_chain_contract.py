"""修订160：验证L3八步物料衔接，拒绝以I09残渣跳过纳米与压铸工序。

只检查工艺物料与既有注册声明，不代表I14–I16自然首建或游戏内验收完成。
"""
import copy
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src/main/resources/data/hk3gtl/research/industrial_processes.json"
CHAIN = (
    "industrial_soulium_precursor", "industrial_nano_building", "industrial_nano_assembly",
    "industrial_nano_control", "industrial_nano_coating", "industrial_soulium_polymerization",
    "industrial_soulium_reconstruction", "industrial_soulium_processing",
)
PROTO = "hk3gtl:soulium_proto_mass"
STABLE = "hk3gtl:stabilized_soulium_proto_mass"
PLATE = "material:soulium/plate"


def ids(recipe, direction):
    return {entry["id"] for field in ("item_" + direction, "fluid_" + direction)
            for entry in recipe[field]}


def reachable(recipes, removed=()):
    """提供链外辅料，按必须同时具备全部主料的规则计算L3支线可达性。"""
    produced = set().union(*(ids(p, "outputs") for p in recipes))
    stock = set().union(*(ids(p, "inputs") for p in recipes)) - produced
    # 两个模板/规则载体由现有GT辅助配方制造；I09等量返还模板不能自产首件。
    stock |= {"hk3gtl:soulium_microstructure_template", "hk3gtl:reconstruction_rule_carrier"}
    while True:
        before = len(stock)
        for recipe in recipes:
            if recipe["id"] not in removed and ids(recipe, "inputs") <= stock:
                stock |= ids(recipe, "outputs")
        if len(stock) == before:
            return stock


def retirement_errors(sources):
    """检查全Java入口，历史实现只允许保留私有声明，不允许被重新调用。"""
    clean = {path: re.sub(r"/\*.*?\*/|//[^\n]*", "", source, flags=re.S)
             for path, source in sources.items()}
    errors = []
    for path, source in clean.items():
        if re.search(r"\baddSouliumSmeltingRecipes\s*\(", source):
            errors.append("旧生产入口被恢复：" + path)
        declarations = re.findall(r"\bprivate\s+static\s+void\s+retiredSouliumSmeltingRecipes\s*\(", source)
        occurrences = re.findall(r"\bretiredSouliumSmeltingRecipes\s*\(", source)
        if len(occurrences) != len(declarations):
            errors.append("历史生产方法被调用或公开：" + path)
        if "/common/machine/" in path:
            for recipe_type in ("SOULIUM_SMELTING_RECIPES", "ABYSS_VACUUM_SMELTING_RECIPES",
                                "ABYSS_PRECISION_ASSEMBLY_RECIPES"):
                if recipe_type in source:
                    errors.append("退休RecipeType重新绑定机器：" + path + ":" + recipe_type)
    return errors


class SouliumChainContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(SOURCE.read_text(encoding="utf-8-sig"))
        cls.plans = {recipe["id"]: recipe for recipe in cls.data["recipes"]}
        cls.chain = [cls.plans[recipe_id] for recipe_id in CHAIN]

    def test_eight_steps_are_materially_connected(self):
        for previous, following in zip(self.chain, self.chain[1:]):
            self.assertTrue(ids(previous, "outputs") & ids(following, "inputs"),
                            (previous["id"], following["id"]))
        self.assertIn(PLATE, reachable(self.chain))
        for step in CHAIN:
            self.assertNotIn(PLATE, reachable(self.chain, {step}), step + "可被旁路")

    def test_reconstruction_requires_cast_mass_and_processing_requires_stable_mass(self):
        cast, anneal, finish = self.chain[-3:]
        self.assertIn({"id": PROTO, "count": 8}, cast["item_outputs"])
        self.assertIn({"id": PROTO, "count": 8}, anneal["item_inputs"])
        self.assertIn({"id": STABLE, "count": 4}, anneal["item_outputs"])
        self.assertIn({"id": STABLE, "count": 4}, finish["item_inputs"])
        self.assertNotIn("hk3gtl:soulium_polymerization_residue", ids(anneal, "inputs"))
        self.assertNotIn("hk3gtl:soulium_data_substrate", ids(finish, "inputs"))

    def test_residue_bypass_regression_is_detected(self):
        broken = copy.deepcopy(self.chain)
        broken[-2]["item_inputs"][0]["id"] = "hk3gtl:soulium_polymerization_residue"
        # I09确有残渣副产；旧错误能跳过I10–I14，本夹具须重现而非空检查。
        self.assertIn(PLATE, reachable(broken, {"industrial_soulium_polymerization"}))
        self.assertNotIn(PLATE, reachable(self.chain, {"industrial_soulium_polymerization"}))

    def test_chain_hk3_inputs_and_outputs_use_existing_registrations(self):
        java_root = ROOT / "src/main/java/com/sirin/hk3gtl/common"
        content = (java_root / "registration/Hk3IndustrialContent.java").read_text(encoding="utf-8")
        soulium = (java_root / "item/soulium/SouliumChainItems.java").read_text(encoding="utf-8")
        registered = set(re.findall(r'\bitem\("([a-z0-9_]+)"', content))
        registered |= set(re.findall(r'ITEMS\.register\("([a-z0-9_]+)"', soulium))
        fluids = (java_root / "registration/Hk3IndustrialFluids.java").read_text(encoding="utf-8")
        registered_fluids = set(re.findall(r'\badd\("([a-z0-9_]+)"', fluids))
        for plan in self.chain:
            for direction in ("inputs", "outputs"):
                for item in plan["item_" + direction]:
                    if item["id"].startswith("hk3gtl:"):
                        self.assertIn(item["id"].split(":", 1)[1], registered, item["id"])
                for fluid in plan["fluid_" + direction]:
                    if ":" not in fluid["id"]:
                        self.assertIn(fluid["id"], registered_fluids, fluid["id"])
        material = (java_root / "material/SouliumMaterial.java").read_text(encoding="utf-8")
        self.assertIn('MOD_ID + ":soulium"', material)
        for flag in ("GENERATE_PLATE", "GENERATE_FINE_WIRE"):
            self.assertIn(flag, material)
        for helper in ("industrial_soulium_template", "industrial_rule_carrier"):
            self.assertIn(helper, self.plans)

    def test_costs_gates_and_provisional_boundary_are_preserved(self):
        for plan, gate, ticks in zip(self.chain[-3:], ("RN-SPC", "RN-SRA", "RN-SPM"),
                                     (1600, 1600, 1200)):
            self.assertEqual([gate], plan["requirements"])
            self.assertEqual(14, plan["energy_tier"])
            self.assertEqual(ticks, plan["ticks"])
            self.assertFalse(plan["provisional"])
        self.assertTrue(self.data["provisional"])

    def test_retired_legacy_production_has_no_registration_or_executor(self):
        source_root = ROOT / "src/main/java"
        sources = {path.relative_to(source_root).as_posix(): path.read_text(encoding="utf-8")
                   for path in source_root.rglob("*.java")}
        self.assertEqual([], retirement_errors(sources))
        entry = "com/sirin/hk3gtl/common/recipe/Hk3RecipeAdderImpl.java"
        self.assertIn("SouliumRecipes.addSouliumProcessingRecipes(provider)", sources[entry])
        self.assertNotIn("SouliumRecipes.addSouliumSmeltingRecipes(provider)", sources[entry])
        for call in ("SouliumRecipes.addSouliumSmeltingRecipes(provider);",
                     "SouliumRecipes.retiredSouliumSmeltingRecipes(provider);"):
            broken = dict(sources)
            broken[entry] += "\n" + call
            self.assertTrue(retirement_errors(broken), "漏检重新接入的旧魂钢入口")
        broken = dict(sources)
        broken["com/sirin/hk3gtl/common/machine/Fixture.java"] = (
            ".recipeType(Hk3RecipeTypes.ABYSS_PRECISION_ASSEMBLY_RECIPES)")
        self.assertTrue(retirement_errors(broken), "漏检恢复的旧执行器")


if __name__ == "__main__":
    unittest.main()

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
