# -*- coding: utf-8 -*-
"""修订177：核验完整构建与36份正式资源，停机备份后仅替换唯一增强版2.9.2的HK3包。

【变更记录 #1】2026-10-26 21:11:05
删除：无；新增：本轮构建/资源身份门禁、原子部署与回滚收据。
修改：复用实际gameDir进程判定，不改第三方包、实例配置或玩家存档。
用途：正式控制器接入的可审计交付；不把文件部署冒充游戏成型验收。

【变更记录 #2】2026-10-26 22:01:47（修订178）
删除：新修订只能写177收据的固定限制；新增修订与日志参数及完整预览数据核验。
修改：每次沿用同一源码指纹、停机、备份与原子替换门禁；用途：可审计交付控制器修复包。
"""
from __future__ import annotations

import configparser
import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
from structure_delivery.project_paths import project_path
import shutil
import zipfile
import deploy_industrial_build as base

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "logs/formal-controller-install-20261026"
GAME = base.INSTANCE / "minecraft"
KEYS = ["i01", "i01_2", "i01_3", "i01_4"] + [f"i{n:02d}" for n in range(2, 29)] + [f"s{n:02d}" for n in range(1, 6)]


def sha(path):
    digest = hashlib.sha256()
    with project_path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read(path):
    return json.loads(project_path(path).read_text(encoding="utf-8-sig"))


def save(name, data):
    (LOG / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def source_inputs():
    paths = [p for p in (ROOT / "src").rglob("*") if p.is_file()]
    paths += [ROOT / "build.gradle", ROOT / "gradle.properties"]
    return {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(paths)}


def main(revision=177, log_dir=None):
    """修订178：复用同一停机门禁，按本轮修订和独立收据目录部署；历史177默认行为保留。"""
    global LOG
    if log_dir is not None:
        candidate = project_path(log_dir).resolve()
        require(candidate.is_relative_to((ROOT / "logs").resolve()), "部署收据必须位于项目logs目录")
        LOG = candidate
    LOG.mkdir(parents=True, exist_ok=True)
    build = read(LOG / "clean-build.json")
    require(build["status"] == "passed" and build["revision"] == revision, "缺少本轮完整构建成功收据")
    require(read(LOG / "build-source-inputs.json") == source_inputs(), "构建后源码发生变化，拒绝部署")
    pack_path = base.INSTANCE / "mrpack/modrinth.index.json"
    mmc_path = base.INSTANCE / "mmc-pack.json"
    cfg_path = base.INSTANCE / "instance.cfg"
    pack = read(pack_path)
    cfg = configparser.ConfigParser(interpolation=None)
    cfg.read(cfg_path, encoding="utf-8-sig")
    require(pack["versionId"] == "2.9.2" and pack["name"] == "GregTech Leisure-增强版", "唯一目标实例版本/名称改变")
    require(cfg.get("General", "name") == pack["name"], "Prism实例身份不一致")
    require(pack["dependencies"] == {"minecraft": "1.20.1", "forge": "47.4.16"}, "MC或Forge版本改变")
    components = {c["uid"]: c["version"] for c in read(mmc_path)["components"]}
    require(components.get("net.minecraft") == "1.20.1" and components.get("net.minecraftforge") == "47.4.16", "Prism组件身份不一致")
    metadata = {str(p): sha(p) for p in (pack_path, mmc_path, cfg_path)}
    guard_before = base.target_process_guard()
    require(base.SOURCE.is_file() and base.TARGET.is_file(), "构建产物或预期目标JAR不存在")
    expected = sha(base.SOURCE)
    require(build["jar_sha256"] == expected, "构建产物身份已变化")
    resources = []
    with zipfile.ZipFile(base.SOURCE) as archive:
        require(archive.testzip() is None, "JAR压缩校验失败")
        changelog = json.loads(archive.read("assets/hk3gtl/changelog.json"))
        require(changelog["entries"][0]["revision"] == revision, "构建修订不匹配")
        machine_class = archive.read("com/sirin/hk3gtl/common/machine/Hk3LateIndustrialMachines.class")
        init_class = archive.read("com/sirin/hk3gtl/common/machine/Hk3MachinesImpl.class")
        require(b"Hk3LateIndustrialMachines" in init_class, "实际初始化链未调用新控制器注册")
        mixins = json.loads(archive.read("hk3gtl.mixins.json"))
        for name in ("gtceu.Hk3MultiblockStateAccess", "gtceu.Hk3LargeStructureStateMixin"):
            require(name in mixins["mixins"], "紧凑巨构状态桥未登记")
        for name in ("common/multiblock/pattern/Hk3LargeStructurePattern", "common/multiblock/pattern/Hk3LateIndustrialPatterns",
                     "common/machine/research/Hk3LateIndustrialMachine", "mixin/gtceu/Hk3MultiblockStateAccess",
                     "mixin/gtceu/Hk3LargeStructureStateMixin"):
            archive.getinfo("com/sirin/hk3gtl/" + name + ".class")
        for key in KEYS:
            for path in (f"data/hk3gtl/approved_architecture/{key}.json", f"data/hk3gtl/structures/approved/{key}.json", f"data/hk3gtl/structures/approved/{key}.nbt"):
                digest = hashlib.sha256(archive.read(path)).hexdigest()
                require(digest == sha(ROOT / "src/main/resources" / path), "打包资源与已核验源码不同：" + path)
                resources.append({"path": path, "sha256": digest})
            manifest = json.loads(archive.read(f"data/hk3gtl/structures/approved/{key}.json"))
            if key in {f"i{n}" for n in range(19, 29)}:
                require(manifest["machine"].split(":", 1)[1].encode() in machine_class, "控制器未实际注册：" + key)
                require(manifest["game_verified"] is False, "不能预记游戏验收成功")
        if revision >= 178:
            require(b"Hk3LargeArchitectureShapes" in machine_class, "巨构注册未接入完整预览")
            archive.getinfo("com/sirin/hk3gtl/common/multiblock/pattern/Hk3LargeArchitectureShapes.class")
            for key in (f"i{number}" for number in range(19, 29)):
                path = f"data/hk3gtl/structures/approved_preview/{key}.bin.gz"
                require(hashlib.sha256(archive.read(path)).hexdigest() == sha(ROOT / "src/main/resources" / path),
                        "巨构完整预览打包缺失或不一致：" + key)
                resources.append({"path": path, "sha256": hashlib.sha256(archive.read(path)).hexdigest()})
            for language in ("zh_cn", "en_us"):
                path = f"assets/hk3gtl/lang/{language}.json"
                values = json.loads(archive.read(path))
                for key in KEYS:
                    manifest = json.loads(archive.read(f"data/hk3gtl/structures/approved/{key}.json"))
                    name = "block." + manifest["machine"].replace(":", ".")
                    require(bool(values.get(name)), "包内控制器缺少名称：" + name)
            applied = read(ROOT / "logs/controller-texture-candidates-20261026/application-r178.json")
            require(applied["status"] == "applied" and applied["unique_controller_fronts"] == 36,
                    "独立控制器材质尚未完成应用核验")
            texture_files = {row["target"]: row["sha256"] for row in applied["copied_files"]}
            texture_files.update(applied["preserved_sha256"])
            for target, digest in texture_files.items():
                path = project_path(target).relative_to(ROOT / "src/main/resources").as_posix()
                require(hashlib.sha256(archive.read(path)).hexdigest() == digest,
                        "批准控制器材质打包不一致：" + path)
        verification = {"status": "passed", "revision": revision, "sha256": expected,
                        "formal_shapes": len(KEYS), "formal_resource_files": resources,
                        "game_verified": False}
        save("package-verification.json", verification)
    before = {p.name: sha(p) for p in sorted(base.TARGET.parent.glob("*.jar"))}
    stamp = datetime.now(timezone(timedelta(hours=8))).strftime("%Y%m%d_%H%M%S")
    backup = GAME / "hk3gtl-mod-backups" / (stamp + f"_formal_controllers_r{revision}")
    backup.mkdir(parents=True, exist_ok=False)
    shutil.copy2(base.TARGET, backup / base.TARGET.name)
    require(sha(backup / base.TARGET.name) == before[base.TARGET.name], "旧包备份验证失败")
    pending = base.TARGET.with_suffix(f".r{revision}-pending")
    require(not pending.exists(), "上次暂存仍存在，拒绝覆盖")
    try:
        shutil.copy2(base.SOURCE, pending)
        require(sha(pending) == expected and sha(base.SOURCE) == expected, "复制期间构建产物变化")
        guard_replace = base.target_process_guard()
        require({str(p): sha(p) for p in (pack_path, mmc_path, cfg_path)} == metadata, "替换前实例身份变化")
        require(sha(base.TARGET) == before[base.TARGET.name], "旧包被并发更改")
        os.replace(pending, base.TARGET)
    finally:
        if pending.exists():
            pending.unlink()
    after = {p.name: sha(p) for p in sorted(base.TARGET.parent.glob("*.jar"))}
    require(before.keys() == after.keys(), "模组文件集合发生额外变化")
    require(all(after[name] == digest for name, digest in before.items() if name != base.TARGET.name), "第三方JAR变化")
    require(sha(base.TARGET) == expected, "目标JAR最终回读失败")
    receipt = {"status": "installed", "revision": revision, "pack_version": "2.9.2", "target": str(base.TARGET),
               "installed_at_hong_kong": datetime.now(timezone(timedelta(hours=8))).isoformat(),
               "sha256": expected, "bytes": base.TARGET.stat().st_size, "backup": str(backup / base.TARGET.name),
               "old_sha256": before[base.TARGET.name], "formal_shapes": len(KEYS), "new_formal_controllers": 10 if revision == 177 else 0,
               "i05_revision": "V5", "third_party_jars_unchanged": True, "instance_metadata_unchanged": True,
               "worlds_written": False, "game_verified": False, "provisional_processes_unlocked": 0,
               "process_guards": {"before_verification": guard_before, "before_atomic_replace": guard_replace}}
    save("deployment.json", receipt)
    save("rollback.json", {"target": str(base.TARGET), "backup": str(backup / base.TARGET.name),
                           "expected_current_sha256": expected, "restore_sha256": before[base.TARGET.name],
                           "requires_target_instance_stopped": True})
    print(json.dumps({k: receipt[k] for k in ("status", "revision", "pack_version", "formal_shapes", "bytes", "sha256")}, ensure_ascii=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--revision", type=int, default=177)
    parser.add_argument("--log-dir", type=Path)
    args = parser.parse_args()
    main(args.revision, args.log_dir)
