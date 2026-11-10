# -*- coding: utf-8 -*-
"""归档本轮获批的 I02-I08 V7，并复制当前全部工业建筑到指定实例。"""
import datetime as dt
import hashlib
import json
import shutil
import zipfile
from pathlib import Path
import nbtlib
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "deliveries/多方块确认归档"
SOURCE = ROOT / "deliveries/I01-I08_重设计_V7_20261014"
INSTANCE = Path(r"C:\Users\OWNER\AppData\Roaming\PrismLauncher\instances\GTL十一周目\minecraft")
KEYS = tuple(f"i{n:02}" for n in range(2, 9))
APPROVAL = "很好，先把现在这些多方块结构实装到游戏里，然后继续进行下一个多方块结构的设计"
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
def copy(source, target):
    assert source.is_file() and not target.exists(), target
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    assert sha(source) == sha(target)
def inspect(folder, key):
    raw = json.loads((folder / "设计与检查.json").read_text(encoding="utf-8"))
    data = raw["data"]
    nbt_path = next(folder.glob("*.nbt"))
    schem_path = next(folder.glob("*.schem"))
    root = nbtlib.load(nbt_path)
    assert list(map(int, root["size"])) == data["size"]
    assert int(root["DataVersion"]) == 3465
    assert sha(nbt_path) == raw["audit"]["hashes"]["nbt"]
    assert sha(schem_path) == raw["audit"]["hashes"]["schem"]
    assert len(data["ports"]) == 6
    return {"id": key.upper(), "title": data["title"], "size": data["size"],
            "controller": data["controller"], "ports": data["ports"],
            "nbt": nbt_path.name, "schem": schem_path.name,
            "nbt_sha256": sha(nbt_path), "schem_sha256": sha(schem_path),
            "blocks": len(root["blocks"])}
def main():
    now = dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))
    stamp = now.strftime("%Y%m%d_%H%M%S_%f")
    snapshot = OUT / f"{stamp}_I02-I08_V7"
    snapshot.mkdir(parents=True, exist_ok=False)
    confirmed = snapshot / "confirmed_v7"
    confirmed.mkdir()
    entries = []
    for key in KEYS:
        source = SOURCE / key
        entry = inspect(source, key)
        shutil.copytree(source, confirmed / key)
        entry["files_sha256"] = {p.relative_to(source).as_posix(): sha(p) for p in sorted(source.rglob("*")) if p.is_file()}
        for rel, expected in entry["files_sha256"].items():
            assert sha(confirmed / key / rel) == expected
        entries.append(entry)
    shared = snapshot / "shared_source_evidence"
    shared.mkdir()
    for path in SOURCE.iterdir():
        if path.is_file():
            copy(path, shared / path.name)
    manifest = {"created_at": now.isoformat(), "timezone": "Asia/Hong_Kong",
                "approval_quote": APPROVAL, "approved_ids": [k.upper() for k in KEYS],
                "source": str(SOURCE), "snapshot": str(snapshot), "entries": entries,
                "scope": "本轮当前工业结构实装授权覆盖 I02-I08 V7；共享原交付证据中的 I01 V7 不作为本次确认版本，I01使用已批准V8。",
                "batch_note": "明确立即实装，七台完整安装；I02-I06为本轮五台组，I07-I08为后续两台组，不重复计数I01或既有I09-I13。",
                "formal_pattern_integrated": False, "game_verified": False}
    write(snapshot / "确认与校验清单.json", manifest)
    bundle = snapshot.with_suffix(".zip")
    with zipfile.ZipFile(bundle, "x", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in sorted(snapshot.rglob("*")):
            if p.is_file():
                z.write(p, p.relative_to(snapshot).as_posix())
    with zipfile.ZipFile(bundle) as z:
        assert z.testzip() is None
        for p in sorted(snapshot.rglob("*")):
            if p.is_file():
                assert z.read(p.relative_to(snapshot).as_posix()) == p.read_bytes()
    sources = [(key, confirmed / key, "v7") for key in KEYS]
    i01 = OUT / "20261014_212031_239262_I01_V8/confirmed_v8"
    sources += [(f"i01-{n}", i01 / f"i01-{n}", "v8") for n in range(1, 5)]
    installed = []
    for key, folder, version in sources:
        entry = inspect(folder, key)
        for kind in ("nbt", "schem"):
            source = folder / entry[kind]
            target = (INSTANCE / "config/worldedit/schematics" / f"hk3gtl_{key}_{version}_{stamp}.schem"
                      if kind == "schem" else INSTANCE / "config/hk3gtl/approved_structures" / snapshot.name / key / entry[kind])
            copy(source, target)
            installed.append({"id": key.upper(), "kind": kind, "path": str(target), "sha256": sha(target)})
    result = {"time": now.isoformat(), "snapshot": str(snapshot), "zip": str(bundle),
              "zip_sha256": sha(bundle), "approved_ids": [k.upper() for k in KEYS],
              "installed_ids": [key.upper() for key, _, _ in sources], "installed_files": installed,
              "all_hashes_verified": True, "formal_pattern_integrated": False, "game_verified": False}
    log = ROOT / "logs/approved-architecture-20261015"
    log.mkdir(parents=True, exist_ok=True)
    write(log / "industrial-approval-install.json", result)
    write(OUT / f"{stamp}_I02-I08_V7_批次索引.json", result)
    print(json.dumps({"snapshot": str(snapshot), "zip_sha256": sha(bundle), "files": len(installed)}, ensure_ascii=True))
if __name__ == "__main__":
    main()

