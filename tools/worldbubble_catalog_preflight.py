#!/usr/bin/env python3
"""Build a conservative, read-only world-bubble resource candidate closure.

The runtime export is a registration/recipe snapshot.  It is intentionally
not treated as proof that a resource is obtainable in survival.  A separate
roots manifest is required before any node can be approved for delivery.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any, Iterable


GT_FULL_VIEW = "gt_full_codec_and_resolved_candidates"
GENERIC_VIEW = "generic_ingredients_and_result_only"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def registry_ids(registries: dict[str, Any]) -> tuple[set[str], set[str]]:
    items = {value for value in registries.get("items", []) if isinstance(value, str)}
    fluids: set[str] = set()
    for value in registries.get("fluids", []):
        if isinstance(value, str):
            fluids.add(value)
        elif isinstance(value, dict) and isinstance(value.get("id"), str):
            fluids.add(value["id"])
    return items, fluids


def alternative_id(value: Any) -> str | None:
    if isinstance(value, str):
        return value
    if isinstance(value, dict) and isinstance(value.get("id"), str):
        return value["id"]
    return None


def input_slots(row: dict[str, Any], key: str) -> list[list[str]]:
    slots: list[list[str]] = []
    resolved = row.get("resolved_inputs")
    if isinstance(resolved, list):
        raw_values = resolved if key == "items" else []
    elif isinstance(resolved, dict):
        raw_values = resolved.get(key, []) or []
    else:
        raw_values = []
    for raw in raw_values:
        alternatives = []
        for value in raw.get("alternatives", []) if isinstance(raw, dict) else []:
            identity = alternative_id(value)
            if identity is not None:
                alternatives.append(identity)
        slots.append(sorted(set(alternatives)))
    return slots


def output_ids(row: dict[str, Any], key: str) -> list[str]:
    result: list[str] = []
    resolved = row.get("resolved_outputs")
    if isinstance(resolved, dict):
        for raw in resolved.get(key, []) or []:
            for value in raw.get("alternatives", []) if isinstance(raw, dict) else []:
                identity = alternative_id(value)
                if identity is not None:
                    result.append(identity)
    if key == "items" and not result:
        raw_result = row.get("result")
        identity = alternative_id(raw_result)
        if identity is not None:
            result.append(identity)
    return sorted(set(result))


def recipe_tier(row: dict[str, Any]) -> int | None:
    data = row.get("definition", {}).get("data", {})
    value = data.get("euTier") if isinstance(data, dict) else None
    return value if isinstance(value, int) else None


def load_roots(path: Path | None, items: set[str], fluids: set[str]) -> list[dict[str, Any]]:
    if path is None:
        return []
    root = read_json(path)
    rows = root.get("roots")
    if not isinstance(rows, list):
        raise ValueError("roots manifest must contain an array named roots")
    result = []
    seen: set[str] = set()
    for raw in rows:
        if not isinstance(raw, dict) or not isinstance(raw.get("id"), str):
            raise ValueError("invalid root entry")
        identity = raw["id"]
        kind = raw.get("kind")
        pool = items if kind == "item" else fluids if kind == "fluid" else set()
        if kind not in {"item", "fluid"} or identity not in pool:
            raise ValueError(f"root is not a registered {kind}: {identity}")
        if identity in seen:
            raise ValueError(f"duplicate root: {identity}")
        seen.add(identity)
        result.append({
            "id": identity,
            "kind": kind,
            "tier": raw.get("tier"),
            "source_type": raw.get("source_type"),
            "source": raw.get("source"),
        })
    return result


def load_recipes(path: Path, items: set[str], fluids: set[str]) -> tuple[list[dict[str, Any]], Counter[str], Counter[str]]:
    rows: list[dict[str, Any]] = []
    eligibility: Counter[str] = Counter()
    views: Counter[str] = Counter()
    with path.open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict) or not isinstance(row.get("id"), str):
                raise ValueError(f"invalid recipe row {line_number}")
            item_slots = input_slots(row, "items")
            fluid_slots = input_slots(row, "fluids")
            outputs = [(identity, "item") for identity in output_ids(row, "items")]
            outputs += [(identity, "fluid") for identity in output_ids(row, "fluids")]
            known = items | fluids
            references = {identity for slots in item_slots + fluid_slots for identity in slots}
            references.update(identity for identity, _ in outputs)
            unknown = sorted(references - known)
            entry = {
                "id": row["id"],
                "type": row.get("type"),
                "view": row.get("view"),
                "gates": sorted(set(row.get("gates") or [])),
                "survival_eligibility": row.get("survival_eligibility"),
                "tier": recipe_tier(row),
                "item_slots": item_slots,
                "fluid_slots": fluid_slots,
                "outputs": outputs,
                "unknown_references": unknown,
            }
            rows.append(entry)
            eligibility[str(entry["survival_eligibility"])] += 1
            views[str(entry["view"])] += 1
    return rows, eligibility, views


def cycle_nodes(graph: dict[str, set[str]]) -> set[str]:
    cycles: set[str] = set()
    state: dict[str, int] = {}
    for start in graph:
        if state.get(start, 0):
            continue
        path: list[str] = []
        positions: dict[str, int] = {}
        stack: list[tuple[str, Iterable[str]]] = [(start, iter(sorted(graph.get(start, ()) )))]
        state[start] = 1
        positions[start] = 0
        path.append(start)
        while stack:
            node, targets = stack[-1]
            try:
                target = next(targets)
            except StopIteration:
                state[node] = 2
                stack.pop()
                positions.pop(node, None)
                if path and path[-1] == node:
                    path.pop()
                continue
            target_state = state.get(target, 0)
            if target_state == 0:
                state[target] = 1
                positions[target] = len(path)
                path.append(target)
                stack.append((target, iter(sorted(graph.get(target, ()) ))))
            elif target_state == 1 and target in positions:
                cycles.update(path[positions[target]:])
    return cycles


def build_closure(audit_dir: Path, roots_path: Path | None) -> dict[str, Any]:
    manifest_path = audit_dir / "manifest.json"
    report_path = audit_dir / "report.json"
    registries_path = audit_dir / "registries.json"
    recipes_path = audit_dir / "recipes.jsonl"
    research_gates_path = audit_dir / "research-gates.json"
    for path in (manifest_path, report_path, registries_path, recipes_path, research_gates_path):
        if not path.is_file():
            raise FileNotFoundError(path)

    manifest = read_json(manifest_path)
    report = read_json(report_path)
    registries = read_json(registries_path)
    research_gates = read_json(research_gates_path)
    items, fluids = registry_ids(registries)
    roots = load_roots(roots_path, items, fluids)
    recipes, eligibility, views = load_recipes(recipes_path, items, fluids)

    output_recipes: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    graph: defaultdict[str, set[str]] = defaultdict(set)
    for recipe in recipes:
        input_ids = {identity for slots in recipe["item_slots"] + recipe["fluid_slots"] for identity in slots}
        for output, _kind in recipe["outputs"]:
            output_recipes[output].append(recipe)
            graph[output].update(input_ids)

    root_ids = {row["id"] for row in roots}
    reachable = set(root_ids)
    changed = True
    while changed:
        changed = False
        for recipe in recipes:
            if recipe["gates"] or recipe["unknown_references"] or recipe["view"] != GT_FULL_VIEW:
                continue
            slots = recipe["item_slots"] + recipe["fluid_slots"]
            if not slots or any(not slot or not any(value in reachable for value in slot) for slot in slots):
                continue
            for output, _kind in recipe["outputs"]:
                if output not in reachable:
                    reachable.add(output)
                    changed = True

    cycles = cycle_nodes(graph)
    output_ids_set = set(output_recipes)
    dynamic_nodes = set()
    gate_nodes = set()
    unknown_nodes = set()
    for identity, rows in output_recipes.items():
        for recipe in rows:
            if recipe["view"] != GT_FULL_VIEW or not recipe["outputs"]:
                dynamic_nodes.add(identity)
            if recipe["gates"]:
                gate_nodes.add(identity)
            if recipe["unknown_references"]:
                unknown_nodes.add(identity)

    statuses: dict[str, str] = {}
    for identity in sorted(output_ids_set | root_ids):
        if identity in reachable:
            statuses[identity] = "reachable"
        elif identity in dynamic_nodes:
            statuses[identity] = "dynamic_unresolved"
        elif identity in unknown_nodes or identity in gate_nodes:
            statuses[identity] = "blocked"
        elif identity in cycles:
            statuses[identity] = "cycle"
        else:
            statuses[identity] = "blocked"

    export_complete = bool(report.get("export_complete"))
    recipe_export_complete = bool(report.get("registered_recipe_export_complete"))
    snapshot_unchanged = bool(report.get("recipe_snapshot_unchanged"))
    candidates = {
        "items": sorted(identity for identity in output_ids_set if identity in items),
        "fluids": sorted(identity for identity in output_ids_set if identity in fluids),
    }
    return {
        "schema": 1,
        "status": "CANDIDATES_ONLY_NOT_AN_APPROVED_DROP_POOL",
        "approved": False,
        "source": {
            "audit_dir": audit_dir.as_posix(),
            "revision": manifest.get("revision"),
            "captured_at": manifest.get("captured_at"),
            "manifest_sha256": sha256(manifest_path),
            "registries_sha256": sha256(registries_path),
            "recipes_sha256": sha256(recipes_path),
            "research_gates_sha256": sha256(research_gates_path),
        },
        "evidence_boundary": {
            "export_complete": export_complete,
            "registered_recipe_export_complete": recipe_export_complete,
            "recipe_snapshot_unchanged": snapshot_unchanged,
            "survival_catalog_verified": bool(report.get("survival_catalog_verified")),
            "gameplay_verified": bool(report.get("gameplay_verified")),
            "ordinary_recipe_view_limit": views.get(GENERIC_VIEW, 0),
            "dynamic_recipe_sources_not_exported": ["loot_tables", "worldgen", "dynamic_machine_recipes"],
        },
        "registries": {"items": len(items), "fluids": len(fluids)},
        "recipes": {
            "count": len(recipes),
            "survival_eligibility": dict(sorted(eligibility.items())),
            "views": dict(sorted(views.items())),
            "with_research_gates": sum(bool(row["gates"]) for row in recipes),
            "with_unknown_references": sum(bool(row["unknown_references"]) for row in recipes),
            "with_empty_input": sum(not row["item_slots"] and not row["fluid_slots"] for row in recipes),
        },
        "roots": roots,
        "candidate_pool": candidates,
        "closure": {
            "reachable_scope": "仅表示输入候选图中的拓扑可达，不证明生存获取或批准入池。",
            "reachable": sum(status == "reachable" for status in statuses.values()),
            "blocked": sum(status == "blocked" for status in statuses.values()),
            "dynamic_unresolved": sum(status == "dynamic_unresolved" for status in statuses.values()),
            "cycle": sum(status == "cycle" for status in statuses.values()),
            "cycles": sorted(cycles),
            "nodes": statuses,
        },
        "research_gates": {
            "exported": isinstance(research_gates, dict),
            "entry_count": len(research_gates.get("entries", [])) if isinstance(research_gates.get("entries"), list) else None,
        },
        "decision": "仅生成候选图；任何输入均不能使本工具批准生存资源池。",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("audit_dir", type=Path)
    parser.add_argument("--roots", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    closure = build_closure(args.audit_dir, args.roots)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(closure, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    receipt = {
        "schema": 1,
        "passed": not closure["approved"],
        "mode": "candidate-closure",
        "approved": closure["approved"],
        "closure_sha256": sha256(args.output),
        "source": closure["source"],
        "counts": {
            key: value
            for key, value in closure["closure"].items()
            if key not in {"nodes", "cycles"}
        },
        "reason": closure["decision"],
    }
    args.receipt.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": receipt["passed"], "approved": receipt["approved"], "closure_sha256": receipt["closure_sha256"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
