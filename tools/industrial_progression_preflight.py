"""核验16阶工业的兼容档、额定档与暂定工艺边界。"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "logs/voltage-progression-preflight-20261106/progression-contract.json"
TIERS = ROOT / "src/main/java/com/sirin/hk3gtl/common/constants/Hk3TiersImpl.java"
EXTENSION_MACHINES = ROOT / "src/main/java/com/sirin/hk3gtl/common/machine/Hk3IndustrialExtensionMachines.java"
ENERGY_POLICY = ROOT / "src/main/java/com/sirin/hk3gtl/common/recipe/Hk3ResearchProcessEnergy.java"
PLANS = ROOT / "src/main/resources/data/hk3gtl/research/industrial_processes.json"
EXECUTION = ROOT / "src/main/resources/data/hk3gtl/research/research_execution.json"
STRUCTURES = ROOT / "src/main/resources/data/hk3gtl/structures/approved"
EXPECTED_TIERS = {
    "HBV": 15, "HCV": 16, "HRV": 17, "HDV": 18,
    "QSV": 19, "QCV": 20, "QEV": 21, "QAV": 22,
    "IMV": 23, "ICV": 24, "IRV": 25, "IWV": 26,
    "WFV": 27, "WSV": 28, "CIV": 29, "CEV": 30,
}
ROLES = ("I14", "I15", "I16", "I18")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def tier_constants(source: str) -> dict[str, int]:
    found = dict(re.findall(r"public static final int\s+([A-Z]+)\s*=\s*(\d+);", source))
    result = {key: int(value) for key, value in found.items() if key in EXPECTED_TIERS}
    if result != EXPECTED_TIERS:
        raise ValueError(f"16阶常量不完整或数值改变：{result}")
    return result


def compatibility_contract(source: str) -> dict[str, object]:
    if ".tier(GTValues.MAX)" not in source:
        raise ValueError("I14-I18兼容档入口改变，需重新审核")
    layouts = dict(re.findall(
        r'register\("([^"]+)",\s*"([a-z0-9]+)"\)', source
    ))
    expected = {
        "soulium_polymerization_die_caster": "i14",
        "soulium_reconstruction_annealing_furnace": "i15",
        "soulium_precision_processing_center": "i16",
        "honkai_fuel_rod_encapsulation_array": "i18",
    }
    if layouts != expected:
        raise ValueError(f"I14-I18注册映射改变：{layouts}")
    return {
        "machine_compatibility_tier": "MAX",
        "registered_layouts": expected,
        "rating_is_not_inferred_from_compatibility": True,
    }


def rated_contract(source: str) -> dict[str, object]:
    entries = dict(re.findall(r'Map\.entry\("([^"]+)",\s*(\d+)\)', source))
    rated = {role: int(entries[role]) for role in ROLES if role in entries}
    if rated != {"I18": 15}:
        raise ValueError(f"额定档映射改变或未知项被擅自填入：{rated}")
    return {
        "rated_tiers": {"I14": None, "I15": None, "I16": None, "I18": rated["I18"]},
        "known": {"I18": "HBV / tier15"},
        "unknown_requires_approval": ["I14", "I15", "I16"],
    }


def plans_contract(data: dict) -> dict[str, object]:
    rows = [row for row in data["recipes"] if row["role"] in ROLES]
    by_role = {}
    for role in ROLES:
        group = [row for row in rows if row["role"] == role]
        provisional = role == "I18"
        if not group or not all(row["provisional"] is provisional for row in group):
            raise ValueError(f"{role}与修订213工艺批准范围不符")
        by_role[role] = {
            "count": len(group),
            "max_energy_tier": max(row["energy_tier"] for row in group),
            "all_provisional": provisional,
            "ids": [row["id"] for row in group],
        }
    return by_role


def structure_contract() -> dict[str, object]:
    result = {}
    for role in ROLES:
        path = STRUCTURES / f"{role.lower()}.json"
        if not path.is_file():
            raise ValueError(f"缺少批准结构资源：{path}")
        value = json.loads(path.read_text(encoding="utf-8"))
        result[role] = {
            "path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "machine": value.get("machine"),
            "game_verified": value.get("game_verified"),
        }
        if value.get("game_verified") is not False:
            raise ValueError(f"{role}结构资源误标实机通过")
    return result


def build(source_root: Path, output: Path) -> dict:
    tier_source = read(source_root / TIERS.relative_to(ROOT))
    machine_source = read(source_root / EXTENSION_MACHINES.relative_to(ROOT))
    policy_source = read(source_root / ENERGY_POLICY.relative_to(ROOT))
    plans = json.loads(read(source_root / PLANS.relative_to(ROOT)))
    execution = json.loads(read(source_root / EXECUTION.relative_to(ROOT)))
    if execution.get("structure_approval") is not False:
        raise ValueError("研究执行合同不再明确禁止未批准结构")
    result = {
        "checked_at": datetime.now().astimezone().isoformat(),
        "scope": "I14/I15/I16/I18静态兼容档、额定档、暂定工艺及结构实机状态",
        "tier_constants": tier_constants(tier_source),
        "compatibility": compatibility_contract(machine_source),
        "rated": rated_contract(policy_source),
        "plans": plans_contract(plans),
        "structures": structure_contract(),
        "source_sha256": {
            "tiers": sha256(source_root / TIERS.relative_to(ROOT)),
            "machines": sha256(source_root / EXTENSION_MACHINES.relative_to(ROOT)),
            "energy_policy": sha256(source_root / ENERGY_POLICY.relative_to(ROOT)),
            "plans": sha256(source_root / PLANS.relative_to(ROOT)),
            "execution": sha256(source_root / EXECUTION.relative_to(ROOT)),
        },
        "result": {
            "passed": True,
            "compatibility_and_rating_separated": True,
            "unapproved_processes_rejected_by_policy": True,
            "approved_I14_I15_I16_enabled": True,
            "runtime_verified": False,
            "natural_first_build_verified": False,
            "note": "I14-I16内测工艺已批准接入；额定档、自然首建及实机成型仍须独立验收。",
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="16阶工业电压合同预检")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    result = build(ROOT, args.output.resolve())
    print(json.dumps({
        "passed": result["result"]["passed"],
        "compatibility_and_rating_separated": result["result"]["compatibility_and_rating_separated"],
        "I14_I15_I16_rated": result["rated"]["rated_tiers"],
        "I18_rated": result["rated"]["rated_tiers"]["I18"],
        "plan_counts": {key: value["count"] for key, value in result["plans"].items()},
        "output": str(args.output),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
