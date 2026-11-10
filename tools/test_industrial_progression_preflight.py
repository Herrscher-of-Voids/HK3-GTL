"""16阶工业静态合同预检测试。"""
import unittest

from industrial_progression_preflight import (
    EXPECTED_TIERS,
    compatibility_contract,
    plans_contract,
    rated_contract,
    tier_constants,
)


class IndustrialProgressionPreflightTest(unittest.TestCase):
    def test_tier_constants_are_contiguous(self):
        source = "\n".join(
            f"public static final int {name} = {value};"
            for name, value in EXPECTED_TIERS.items()
        )
        self.assertEqual(EXPECTED_TIERS, tier_constants(source))

    def test_compatibility_does_not_become_rating(self):
        source = '.tier(GTValues.MAX)\n' + "\n".join(
            f'register("{name}", "{role}")'
            for name, role in {
                "soulium_polymerization_die_caster": "i14",
                "soulium_reconstruction_annealing_furnace": "i15",
                "soulium_precision_processing_center": "i16",
                "honkai_fuel_rod_encapsulation_array": "i18",
            }.items()
        )
        result = compatibility_contract(source)
        self.assertTrue(result["rating_is_not_inferred_from_compatibility"])

    def test_unknown_ratings_and_explicit_process_approval_are_separate(self):
        source = 'Map.entry("I18", 15)'
        self.assertEqual({"I14": None, "I15": None, "I16": None, "I18": 15},
                         rated_contract(source)["rated_tiers"])
        data = {"recipes": [
            {"role": "I14", "id": "a", "energy_tier": 14, "provisional": False},
            {"role": "I15", "id": "b", "energy_tier": 14, "provisional": False},
            {"role": "I16", "id": "c", "energy_tier": 26, "provisional": False},
            {"role": "I18", "id": "d", "energy_tier": 15, "provisional": True},
        ]}
        self.assertEqual({"I14": 1, "I15": 1, "I16": 1, "I18": 1},
                         {key: value["count"] for key, value in plans_contract(data).items()})
        data["recipes"][-1]["provisional"] = False
        with self.assertRaises(ValueError):
            plans_contract(data)


if __name__ == "__main__":
    unittest.main()
