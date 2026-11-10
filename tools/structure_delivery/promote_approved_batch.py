"""Promote one immutable five-machine archive into the formal resource tree.

Usage: python promote_approved_batch.py <snapshot-directory> <zip-file> <batch-id>
The existing promotion implementation remains the single source of pattern rules;
this wrapper only pins its input archive and machine subset.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "tools/structure_delivery/promote_reviewed_structures.py"
spec = importlib.util.spec_from_file_location("promote_reviewed_structures", MODULE_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(MODULE_PATH)
promote = importlib.util.module_from_spec(spec)
spec.loader.exec_module(promote)


MACHINE_ORDER = {
    "I01-1": ("i01", "i01_honkai_collection_tower"),
    "I01-2": ("i01_2", "i01_2_honkai_collection_tower"),
    "I01-3": ("i01_3", "i01_3_honkai_collection_tower"),
    "I01-4": ("i01_4", "i01_4_honkai_collection_tower"),
    "I02": ("i02", "i02_spectrum_analysis_array"),
    "I03": ("i03", "liquid_honkai_fractionation_center"),
    "I04": ("i04", "liquid_honkai_stabilization_tower"),
    "I05": ("i05", "stabilization_medium_regeneration_tower"),
    "I06": ("i06", "honkai_fuel_blending_plant"),
    "I07": ("i07", "honkai_detector_calibration_bench"),
    "I08": ("i08", "imitation_core_crystallization_chamber"),
    "I09": ("i09", "soulium_precursor_mixing_kettle"),
    "I10": ("i10", "nano_basic_unit_synthesizer"),
    "I11": ("i11", "nanobot_assembly_array"),
    "I12": ("i12", "nano_self_organizing_programming_chamber"),
}


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit("usage: promote_approved_batch.py SNAPSHOT ZIP BATCH_ID")
    snapshot, bundle, batch = map(Path, sys.argv[1:])
    if not snapshot.is_dir() or not bundle.is_file():
        raise FileNotFoundError("snapshot or zip does not exist")
    expected = hashlib.sha256(bundle.read_bytes()).hexdigest()
    index = snapshot / "确认与校验清单.json"
    manifest = json.loads(index.read_text(encoding="utf-8"))
    if manifest.get("batch") != batch.name and manifest.get("batch") != str(batch):
        raise RuntimeError(f"manifest batch mismatch: {manifest.get('batch')} != {batch}")
    ids = [entry["id"] for entry in manifest["entries"]]
    if len(ids) != 5 or any(machine_id not in MACHINE_ORDER for machine_id in ids):
        raise RuntimeError(f"not a complete approved five-machine batch: {ids}")
    promote.ARCHIVE = snapshot
    promote.ZIP = bundle
    promote.ZIP_SHA256 = expected
    promote.MACHINES = {machine_id: MACHINE_ORDER[machine_id] for machine_id in ids}
    promote.main()
    result = {
        "batch": manifest["batch"],
        "snapshot": str(snapshot),
        "zip": str(bundle),
        "zip_sha256": expected,
        "machines": ids,
        "resources": str(promote.RES),
    }
    (snapshot / "接入结果.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
