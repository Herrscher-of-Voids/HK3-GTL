# -*- coding: utf-8 -*-
"""归档并安装用户确认的 S01-S05 研究所五阶结构文件。

只复制已确认交付中的原始压缩字节；正式 Pattern 与研究机器由源码构建阶段接入。
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
SOURCE = ROOT / "deliveries/S01-S05_研究所五阶_原地扩建_V1_20261014"
ARCHIVES = ROOT / "deliveries/多方块确认归档"
INSTANCE = Path(r"C:\Users\OWNER\AppData\Roaming\PrismLauncher\instances\GTL十一周目\minecraft")
LOG = ROOT / "logs/research-campus-additive-v1"
KEYS = ("s01", "s02", "s03", "s04", "s05")
APPROVAL = "很好，先把现在这些多方块结构实装到游戏里，然后继续进行下一个多方块结构的设计"

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def state_text(raw):
    props = raw.get("Properties", {})
    suffix = "[" + ",".join(f"{k}={v}" for k, v in sorted(props.items())) + "]" if props else ""
    return str(raw["Name"]) + suffix

def inspect(key: str):
    folder = SOURCE / key
    nbt_files = list(folder.glob("*.nbt"))
    schem_files = list(folder.glob("*.schem"))
    assert len(nbt_files) == len(schem_files) == 1, folder
    nbt_path, schem_path = nbt_files[0], schem_files[0]
    record = json.loads((folder / "设计与检查.json").read_text(encoding="utf-8"))
    data = record["data"]
    root = nbtlib.load(nbt_path)
    assert int(root["DataVersion"]) == 3465
    size = [int(v) for v in root["size"]]
    assert size == data["size"]
    palette = [state_text(v) for v in root["palette"]]
    states = {tuple(int(v) for v in block["pos"]): palette[int(block["state"])]
              for block in root["blocks"]}
    assert len(states) == len(root["blocks"])
    assert states[tuple(data["controller"])] == "minecraft:diamond_block"
    assert sum(v == "minecraft:diamond_block" for v in states.values()) == 1
    assert sum(v == "hk3gtl:industrial_port_casing" for v in states.values()) == 6
    assert len(data["ports"]) == 6
    schem = nbtlib.load(schem_path)
    assert schem.root_name == "Schematic"
    assert int(schem["Version"]) == 2 and int(schem["DataVersion"]) == 3465
    assert [int(schem[name]) for name in ("Width", "Height", "Length")] == size
    assert [int(v) for v in schem["Offset"]] == [-int(v) for v in data["controller"]]
    assert sha(nbt_path) == record["audit"]["hashes"]["nbt"]
    assert sha(schem_path) == record["audit"]["hashes"]["schem"]
    return {
        "id": key.upper(), "title": data["title"], "size": size,
        "blocks": len(states), "controller": data["controller"],
        "ports": data["ports"], "nbt": nbt_path.name, "schem": schem_path.name,
        "nbt_sha256": sha(nbt_path), "schem_sha256": sha(schem_path),
        "source": str(folder),
    }

def copy_verified(source: Path, target: Path):
    assert source.is_file(), source
    assert not target.exists(), target
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    assert sha(source) == sha(target), target

def main():
    assert SOURCE.is_dir() and INSTANCE.is_dir(), "源交付或目标实例不存在"
    assert not any(p.name.endswith((".pending", ".tmp")) for p in (INSTANCE / "mods").glob("*")), "目标实例有未完成替换"
    entries = [inspect(key) for key in KEYS]
    now = dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))
    stamp = now.strftime("%Y%m%d_%H%M%S_%f")
    snapshot = ARCHIVES / f"{stamp}_batch-05_S01-S05_V1"
    snapshot.mkdir(parents=True, exist_ok=False)
    copied = snapshot / "confirmed_v1"
    shutil.copytree(SOURCE, copied)
    source_hashes = {p.relative_to(SOURCE).as_posix(): sha(p) for p in sorted(SOURCE.rglob("*")) if p.is_file()}
    assert source_hashes == {p.relative_to(copied).as_posix(): sha(p) for p in sorted(copied.rglob("*")) if p.is_file()}
    dependencies = snapshot / "evidence"
    dependencies.mkdir()
    for name in ("final-verification.json", "independent-review.json", "browser-review.json", "reference-supplement.json"):
        source = LOG / name
        if source.is_file():
            copy_verified(source, dependencies / name)
    instance_identity = []
    for jar in sorted((INSTANCE / "mods").glob("*.jar")):
        instance_identity.append({"file": str(jar), "sha256": sha(jar), "bytes": jar.stat().st_size})
    schem_root = INSTANCE / "config/worldedit/schematics"
    nbt_root = INSTANCE / "config/hk3gtl/approved_structures" / snapshot.name
    installed = []
    for entry in entries:
        key = entry["id"].lower()
        schem_target = schem_root / f"hk3gtl_{key}_v1_{stamp}.schem"
        nbt_target = nbt_root / key / entry["nbt"]
        copy_verified(copied / key / entry["schem"], schem_target)
        copy_verified(copied / key / entry["nbt"], nbt_target)
        installed += [
            {"id": entry["id"], "kind": "schem", "path": str(schem_target), "sha256": entry["schem_sha256"]},
            {"id": entry["id"], "kind": "nbt", "path": str(nbt_target), "sha256": entry["nbt_sha256"]},
        ]
        assert sha(schem_target) == entry["schem_sha256"]
        assert sha(nbt_target) == entry["nbt_sha256"]
    manifest = {
        "batch": "batch-05", "created_at": now.isoformat(), "timezone": "Asia/Hong_Kong",
        "approval_quote": APPROVAL,
        "confirmation_scope": "S01-S05 研究所五阶原地扩建 V1 建筑外观与结构文件",
        "status": "approved_archived_structure_files_installed",
        "source_delivery": str(SOURCE), "archive": str(snapshot), "instance": str(INSTANCE),
        "entries": entries, "installed_files": installed, "instance_identity": instance_identity,
        "source_sha256": source_hashes,
        "copy_rule": "复制确认版本原始压缩字节并逐文件核对 SHA256，未重新导出或重压缩。",
        "formal_pattern_integrated": False, "game_verified": False,
        "not_verified": ["正式 Pattern 与研究机器定义（等待源码构建）", "Minecraft 成型与运行", "生存材料完整可达性"],
        "unchanged_scope": ["源交付", "玩家存档/world", "KubeJS", "原有 mods 文件"],
    }
    manifest_path = snapshot / "确认与校验清单.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    copy_verified(manifest_path, nbt_root / "确认与校验清单.json")
    bundle = snapshot.with_suffix(".zip")
    archived_hashes = {p.relative_to(snapshot).as_posix(): sha(p) for p in sorted(snapshot.rglob("*")) if p.is_file()}
    with zipfile.ZipFile(bundle, "x", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for rel in archived_hashes:
            archive.write(snapshot / rel, rel)
    with zipfile.ZipFile(bundle) as archive:
        assert archive.testzip() is None and set(archive.namelist()) == set(archived_hashes)
        for rel, expected in archived_hashes.items():
            assert hashlib.sha256(archive.read(rel)).hexdigest() == expected
    result = {
        "time": now.isoformat(), "batch": "batch-05", "snapshot": str(snapshot),
        "zip": str(bundle), "zip_sha256": sha(bundle), "zip_bytes": bundle.stat().st_size,
        "instance": str(INSTANCE), "structures": 5, "installed_structure_files": 10,
        "installed_files": installed, "all_hashes_verified": True,
        "source_delivery_unchanged": True, "formal_pattern_integrated": False,
        "game_verified": False,
    }
    (LOG / f"approval-{stamp}.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    (LOG / f"install-{stamp}.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    (ARCHIVES / f"{stamp}_batch-05_批次索引.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    discussion = ROOT / "doc/HK3GTL-内测5/讨论记录" / f"{now:%Y-%m-%d_%H-%M-%S}_S01-S05确认归档与结构文件实装.html"
    discussion.write_text(f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>S01-S05确认归档与结构文件实装</title></head><body>
<h1>S01-S05确认归档与结构文件实装</h1>
<p>记录时间：{now.isoformat()}，Asia/Hong_Kong。</p>
<p>用户已确认原话：「{APPROVAL}」。本记录覆盖 S01–S05 研究所五阶 V1 的待确认外观状态，允许将该确认版本归档并接入目标实例。</p>
<p>已实施：五座结构交付复制到 {snapshot}，并将五个 Sponge Schematic 复制到 GTL十一周目实例的 config/worldedit/schematics；原始 NBT 与清单复制到 {nbt_root}。归档 ZIP：{bundle}。</p>
<p>已验证：NBT/Sponge 版本、尺寸、主控、六工业接口、结构文件哈希与归档 ZIP 逐文件一致；S01–S05 源交付未修改。此次结构文件实装仍不等同于 Pattern、研究机器运行或 Minecraft 成型验收。</p>
<p>下一步：源码构建接入 S01–S05 的正式研究 Pattern 与研究控制器；用户随后可以在游戏中进行外观粘贴与成型测试。</p>
</body></html>""", encoding="utf-8")
    result["discussion"] = str(discussion)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()

