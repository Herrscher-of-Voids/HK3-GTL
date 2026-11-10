#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
JAVA_ROOT = ROOT / "src" / "main" / "java" / "com" / "sirin" / "hk3gtl"
RECIPE_ROOT = JAVA_ROOT / "common" / "recipe"
MACHINE_ROOT = JAVA_ROOT / "common" / "machine"
EVENT_ROOT = JAVA_ROOT / "common" / "event"
REG_TAB_FILE = JAVA_ROOT / "common" / "registration" / "Hk3CreativeTabsImpl.java"


MULTIBLOCK_ARRAY_RE = re.compile(
    r"MULTIBLOCK_CONTROLLER_PATHS\s*=\s*\{(?P<body>.*?)\};",
    re.DOTALL,
)
STRING_RE = re.compile(r'"([^"]+)"')
RECIPE_BUILDER_RE = re.compile(
    r"(?P<type>[A-Za-z0-9_\.]+)\s*\.recipeBuilder\(\"(?P<id>[^\"]+)\"\)"
)
RECIPE_TYPE_DEF_RE = re.compile(
    r"public\s+static\s+final\s+GTRecipeType\s+([A-Z0-9_]+)\s*=\s*GTRecipeTypes\.register\(\s*\"([^\"]+)\"",
    re.DOTALL,
)
MACHINE_DEF_RE = re.compile(
    r'multiblock\("(?P<path>[^"]+)"\s*,\s*(?P<name>[A-Z0-9_]+)\)\s*(?P<body>.*?)(?=REGISTRATE\.multiblock\(|\Z)',
    re.DOTALL,
)
MACHINE_RECIPE_TYPE_RE = re.compile(r"\.recipeType\((?P<type>[A-Za-z0-9_\.]+)\)")
CASE_STRING_RE = re.compile(r'case\s+"(?P<path>[^"]+)"')


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_controllers() -> list[str]:
    text = read_text(REG_TAB_FILE)
    m = MULTIBLOCK_ARRAY_RE.search(text)
    if not m:
        raise RuntimeError("Failed to locate MULTIBLOCK_CONTROLLER_PATHS")
    return [s for s in STRING_RE.findall(m.group("body")) if s]


def parse_recipe_types() -> dict[str, str]:
    result: dict[str, str] = {}
    for file in RECIPE_ROOT.glob("Hk3RecipeTypes*.java"):
        text = read_text(file)
        cls_name = file.stem
        for const_name, recipe_id in RECIPE_TYPE_DEF_RE.findall(text):
            result[f"{cls_name}.{const_name}"] = recipe_id
    return result


def parse_recipe_builder_calls() -> dict[str, list[str]]:
    usage: dict[str, list[str]] = defaultdict(list)
    for file in RECIPE_ROOT.rglob("*.java"):
        text = read_text(file)
        for match in RECIPE_BUILDER_RE.finditer(text):
            recipe_type = match.group("type")
            recipe_id = match.group("id")
            usage[recipe_type].append(recipe_id)
    return usage


def parse_machine_recipe_bindings() -> dict[str, str]:
    result: dict[str, str] = {}
    for file in MACHINE_ROOT.glob("Hk3Machines*.java"):
        text = read_text(file)
        for machine_match in MACHINE_DEF_RE.finditer(text):
            machine_path = machine_match.group("path")
            body = machine_match.group("body")
            recipe_type_match = MACHINE_RECIPE_TYPE_RE.search(body)
            if recipe_type_match:
                result[machine_path] = recipe_type_match.group("type")
    return result


def parse_event_machine_refs() -> dict[str, set[str]]:
    refs: dict[str, set[str]] = {}
    for file in EVENT_ROOT.glob("*.java"):
        paths = {m.group("path") for m in CASE_STRING_RE.finditer(read_text(file))}
        if paths:
            refs[file.name] = paths
    return refs


def build_report() -> dict:
    controllers = parse_controllers()
    controller_set = set(controllers)

    recipe_types = parse_recipe_types()
    recipe_usage = parse_recipe_builder_calls()
    machine_recipe_bindings = parse_machine_recipe_bindings()
    event_machine_refs = parse_event_machine_refs()

    assembler_recipe_ids = set(recipe_usage.get("GTRecipeTypes.ASSEMBLER_RECIPES", []))
    missing_controller_assembler = sorted(
        controller for controller in controllers if f"hk3gtl_{controller}" not in assembler_recipe_ids
    )

    bound_recipe_types = set(machine_recipe_bindings.values())
    recipe_type_usage = {
        recipe_type: ids
        for recipe_type, ids in recipe_usage.items()
        if recipe_type.startswith("Hk3RecipeTypes")
    }

    recipe_types_declared = sorted(recipe_types.keys())
    unreferenced_recipe_types = sorted(
        rt for rt in recipe_types_declared if rt not in recipe_type_usage
    )
    orphan_recipe_types = sorted(
        rt for rt, ids in recipe_type_usage.items() if ids and rt not in bound_recipe_types
    )

    stale_event_refs = {
        file_name: sorted(path for path in paths if path not in controller_set)
        for file_name, paths in event_machine_refs.items()
    }
    stale_event_refs = {k: v for k, v in stale_event_refs.items() if v}

    missing_recipe_type_coverage = sorted(
        path for path, recipe_type in machine_recipe_bindings.items()
        if recipe_type.startswith("Hk3RecipeTypes") and recipe_type not in recipe_type_usage
    )

    return {
        "controllerCount": len(controllers),
        "recipeTypeCount": len(recipe_types_declared),
        "machineWithRecipeTypeCount": len(machine_recipe_bindings),
        "missingControllerAssemblerRecipes": missing_controller_assembler,
        "orphanRecipeTypesWithoutMachine": orphan_recipe_types,
        "recipeTypesDeclaredButNeverUsed": unreferenced_recipe_types,
        "machineRecipeTypesWithoutRecipes": missing_recipe_type_coverage,
        "staleEventMachineRefs": stale_event_refs,
    }


def write_outputs(report: dict) -> None:
    out_json = ROOT / "tools" / "audit_recipes_report.json"
    out_txt = ROOT / "tools" / "audit_recipes_report.txt"
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines: list[str] = []
    lines.append("HK3GTL Recipe Audit Report")
    lines.append("=" * 64)
    lines.append(f"Controllers: {report['controllerCount']}")
    lines.append(f"RecipeTypes: {report['recipeTypeCount']}")
    lines.append(f"MachinesWithRecipeType: {report['machineWithRecipeTypeCount']}")
    lines.append("")

    def section(title: str, values) -> None:
        lines.append(f"[{title}]")
        if isinstance(values, dict):
            if not values:
                lines.append("- None")
            else:
                for k, v in values.items():
                    lines.append(f"- {k}: {', '.join(v)}")
        else:
            if not values:
                lines.append("- None")
            else:
                for item in values:
                    lines.append(f"- {item}")
        lines.append("")

    section("Missing Controller Assembler Recipes", report["missingControllerAssemblerRecipes"])
    section("Orphan RecipeTypes Without Machine", report["orphanRecipeTypesWithoutMachine"])
    section("RecipeTypes Declared But Never Used", report["recipeTypesDeclaredButNeverUsed"])
    section("Machine RecipeTypes Without Recipes", report["machineRecipeTypesWithoutRecipes"])
    section("Stale Event Machine References", report["staleEventMachineRefs"])

    out_txt.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    report = build_report()
    write_outputs(report)
    print("Audit completed:")
    print((ROOT / "tools" / "audit_recipes_report.json").as_posix())
    print((ROOT / "tools" / "audit_recipes_report.txt").as_posix())


if __name__ == "__main__":
    main()
