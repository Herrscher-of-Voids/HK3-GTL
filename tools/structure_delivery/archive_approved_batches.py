"""Create immutable five-machine delivery batches from the current reviewed previews.

The batch boundary is part of the delivery contract: a later preview cannot silently
replace an already approved machine. Each snapshot contains the complete preview
folder, the source metadata, per-file SHA256 values, and a zip-level digest.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import shutil
import zipfile
from pathlib import Path

import nbtlib


ROOT = Path(__file__).resolve().parents[2]
DELIVERIES = ROOT / "deliveries"
OUT = DELIVERIES / "多方块确认归档"

BATCHES = {
    "batch-01": [
        ("I01-1", "I01-1_天命工业采集塔_风格预览"),
        ("I01-2", "I01-2_2阶崩坏能采集塔_无拆除扩建预览"),
        ("I01-3", "I01-3_3阶崩坏能采集塔_无拆除扩建预览"),
        ("I01-4", "I01-4_4阶崩坏能采集塔_无拆除扩建预览"),
        ("I02", "I02_样本光谱分析阵列_自由设计预览"),
    ],
    "batch-02": [
        ("I03", "I03_崩坏能离心分离中心_自由设计预览"),
        ("I04", "I04_液态崩坏能稳定塔_自由设计预览"),
        ("I05", "I05_稳定介质再生塔_自由设计预览"),
        ("I06", "I06_崩坏能燃料调配厂_自由设计预览"),
        ("I07", "I07_探测器精密校准台_自由设计预览"),
    ],
    "batch-03": [
        ("I08", "I08_仿制核心结晶反应室_自由设计预览"),
        ("I09", "I09_魂钢前驱体配制釜_自由设计预览"),
        ("I10", "I10_纳米基元合成器_自由设计预览"),
        ("I11", "I11_纳米机器人装配阵列_自由设计预览"),
        ("I12", "I12_纳米自组织编程舱_自由设计预览"),
    ],
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_metadata(source: Path) -> dict:
    path = source / "设计与检查.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    data = value["data"]
    nbt_files = sorted(source.glob("*.nbt"))
    if len(nbt_files) != 1:
        raise RuntimeError(f"expected one NBT in {source}, got {len(nbt_files)}")
    structure = nbtlib.load(nbt_files[0])
    declared = [int(v) for v in structure["size"]]
    if declared != [int(v) for v in data["size"]]:
        raise RuntimeError(f"{source.name}: metadata size {data['size']} != NBT {declared}")
    positions = [tuple(int(v) for v in block["pos"]) for block in structure["blocks"]]
    if len(positions) != len(set(positions)):
        raise RuntimeError(f"{source.name}: duplicate block positions")
    for x, y, z in positions:
        if not (0 <= x < declared[0] and 0 <= y < declared[1] and 0 <= z < declared[2]):
            raise RuntimeError(f"{source.name}: block outside declared size at {(x, y, z)}")
    ports = {tuple(int(v) for v in port["pos"]): port for port in data["ports"]}
    states = structure["palette"]
    port_states = {}
    for position in ports:
        if position not in positions:
            raise RuntimeError(f"{source.name}: port missing from NBT at {position}")
        block = next(block for block in structure["blocks"] if tuple(int(v) for v in block["pos"]) == position)
        port_states["%d,%d,%d" % position] = str(states[int(block["state"])]["Name"])
    return {
        "size": declared,
        "controller": [int(v) for v in data["controller"]],
        "ports": data["ports"],
        "nbt": nbt_files[0].name,
        "block_count": len(positions),
        "nbt_sha256": sha(nbt_files[0]),
        "metadata_sha256": sha(source / "设计与检查.json"),
        "source_port_states": port_states,
    }


def archive_batch(batch: str, entries: list[tuple[str, str]], stamp: str) -> dict:
    snapshot = OUT / f"{stamp}_{batch}"
    snapshot.mkdir(parents=True, exist_ok=False)
    manifest_entries = []
    for machine_id, folder in entries:
        source = DELIVERIES / folder
        if not source.is_dir():
            raise FileNotFoundError(source)
        metadata = read_metadata(source)
        target = snapshot / machine_id
        shutil.copytree(source, target)
        # The approved geometry uses a single closed industrial casing for all
        # candidate ports. Older previews used diamond ore as a visual marker;
        # only the immutable delivery copy is normalized here.
        delivery_nbt = target / metadata["nbt"]
        structure = nbtlib.load(delivery_nbt)
        industrial_index = None
        for index, state in enumerate(structure["palette"]):
            if str(state["Name"]) == "hk3gtl:industrial_port_casing":
                industrial_index = index
                break
        if industrial_index is None:
            structure["palette"].append(nbtlib.Compound({"Name": nbtlib.String("hk3gtl:industrial_port_casing")}))
            industrial_index = len(structure["palette"]) - 1
        port_positions = {tuple(int(v) for v in port["pos"]) for port in metadata["ports"]}
        for block in structure["blocks"]:
            if tuple(int(v) for v in block["pos"]) in port_positions:
                block["state"] = nbtlib.Int(industrial_index)
        structure.save(delivery_nbt, gzipped=True)
        metadata["delivery_nbt_sha256"] = sha(delivery_nbt)
        files = {path.relative_to(snapshot).as_posix(): sha(path)
                 for path in target.rglob("*") if path.is_file()}
        manifest_entries.append({
            "id": machine_id,
            "status": "approved",
            "source": str(source),
            "archive": str(target),
            "metadata": metadata,
            "files_sha256": files,
        })
    manifest = {
        "batch": batch,
        "created_at": dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat(),
        "rule": "每明确批准五台后立即按确认版本独立接入；本快照不可被后续预览静默替换。",
        "entries": manifest_entries,
        "integration_target": r"C:\Users\OWNER\AppData\Roaming\PrismLauncher\instances\GTL十一周目",
        "integration_note": "I08-I12 为本批次已批准几何；Pattern、控制器、接口映射和配方运行能力另行校验。",
    }
    manifest_path = snapshot / "确认与校验清单.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    bundle = OUT / f"{stamp}_{batch}.zip"
    with zipfile.ZipFile(bundle, "x", zipfile.ZIP_DEFLATED) as archive:
        for path in snapshot.rglob("*"):
            if path.is_file():
                archive.write(path, path.relative_to(snapshot).as_posix())
    with zipfile.ZipFile(bundle) as archive:
        if archive.testzip() is not None:
            raise RuntimeError(f"corrupt archive {bundle}")
        for entry in manifest_entries:
            for name, expected in entry["files_sha256"].items():
                if hashlib.sha256(archive.read(name)).hexdigest() != expected:
                    raise RuntimeError(f"archive hash mismatch: {name}")
    result = {
        "batch": batch,
        "snapshot": str(snapshot),
        "zip": str(bundle),
        "zip_sha256": sha(bundle),
        "entries": [{"id": e["id"], "size": e["metadata"]["size"],
                     "nbt_sha256": e["metadata"]["nbt_sha256"]} for e in manifest_entries],
    }
    (snapshot / "批次结果.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).strftime("%Y%m%d_%H%M%S_%f")
    results = [archive_batch(batch, entries, stamp) for batch, entries in BATCHES.items()]
    index = {
        "created_at": stamp,
        "rule": "每五台明确批准的多方块结构独立归档并接入。",
        "batches": results,
    }
    (OUT / f"{stamp}_批次索引.json").write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(index, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
