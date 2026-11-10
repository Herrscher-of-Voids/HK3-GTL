"""【变更记录 #1】2026-10-17 14:03:30（内测5修订160）。
删除：无；新增：仅向已核实的增强版2.8目录部署本次HK3构建并保存回滚副本。
修改：不沿用已消失的2.7目录；用途：核验JAR身份、修订、关键类及资源，拒绝运行中替换。
不调整整包配置，不处理第三方模组，不读写玩家存档；机器收据仅记录部署，不算游戏验收。
变更记录 #2：2026-10-17 14:13:45（修订161）。
删除：固定修订160的运行前提；新增：按构建内修订保存独立部署收据与回滚目录。
修改：工艺业务数据路径和长期部署脚本名；用途：整批命名迁移后继续核验最终JAR。
变更记录 #3：2026-10-17 14:24:10（修订161）。
删除：仅识别旧启动器入口的停机判据；新增：当前Prism入口匹配。
修改：运行中的目标实例必须阻止替换；用途：防止新启动器主类漏检，不输出启动参数或账号数据。
"""
# 【变更记录 · 修订162】2026-10-17 14:40:05：仅部署完成退役清理的修订162，单独保存收据；沿用停机与第三方JAR不变保护。
# 【变更记录 · 修订163】2026-10-17 15:12:00：增加现行研究权限策略与旧节点入口退出的构建身份核对，部署收据独立归档。
# 【变更记录 · 修订164】2026-10-17 15:28:56：核对JEI研究名称模板与换行控件，部署收据独立保存，沿用停机保护。
# 【变更记录 #4】2026-10-17 17:12:52（修订165）：删除仅允许修订164的限制；新增本轮231项批准资源与最终重构包的只读核验；修改收据到主材系统目录；用途为停机、回滚与第三方JAR不变保护下部署，静态核验不冒充游戏验收。
# 【变更记录 #5】2026-10-17 19:17:12（修订165）：删除把物品数231误记为纹理数的口径；新增231物品与586纹理层的分列；修改V2部署收据，沿用严格包核验、停机备份及第三方不变保护；用途是准确记录已批准的完整分层资源。
# 【变更记录 #6】2026-10-17 21:54:10（修订166）：删除部署固定165的限制；新增显式修订与独立证据目录；修改核验调用和收据路径按参数冻结，保留默认165及原批准资料；用途：同一停机备份保护下交付高度包，不覆盖165历史或改第三方。
# 【变更记录 #7】2026-10-19 02:08:05（修订171）：删除新包沿用2.8版本条件；新增171及增强版2.9显式合同；修改部署收据按实际版本记录，保留停机、原包备份、批准资源核验和第三方JAR不变保护；用途为机器总览整批交付，不作为启动验收。
# 【变更记录 #8】2026-10-20 00:47:44（修订172，香港时间）：删除本轮把其他启动器实例一律当作目标实例的停机误判；新增172独立绝对路径分类及无法定位时拒绝的保护；修改172继承2.9包核验并保存不含启动参数的停机证据。165/166/171仍用原停机合同；用途为获批21形态交付，禁止干预其他实例。
# 【变更记录 #9】2026-10-20 03:58:51（修订174，香港时间）：删除174不受完整部署入口支持的限制；新增载体白名单验证计数与独立收据；修改2.9目标停机门禁沿用精确路径分类；用途为部署仅包含13项获批载体模型/29层贴图的整包，同时保留2.9回滚和第三方JAR不变保护。
# 【变更记录 #10】2026-10-23 13:34:18（部署守卫修正，不增加模组修订号）：删除把已证其他Prism实例仍归入未知入口的误拒；新增实际cwd、创建时间、完整natives及实例元数据交叉核验；修改仅对证据一致的其他实例解除阻塞，目标路径或身份不明仍拒绝；用途为获批V2的安全部署准备，不启动、停止或改写其他实例。
import argparse
import ctypes
from datetime import datetime, timezone, timedelta
from pathlib import Path
import hashlib
import json
import ntpath
import os
import re
import shutil
import subprocess
import zipfile
from verify_main_material_package import verify
from prism_process_identity import verified_other_prism

ROOT = Path(__file__).resolve().parents[1]
INSTANCE = Path(os.environ["APPDATA"]) / "PrismLauncher/instances/GregTech Leisure-增强版"
SOURCE = ROOT / "build/libs/hk3gtl-0.5.0.jar"
TARGET = INSTANCE / "minecraft/mods/HK3GTL-内测5.jar"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized_absolute_path(value):
    """只接受有盘符或UNC根的绝对路径；不靠局部字符串或目录名判定实例。"""
    if not isinstance(value, str) or not value or any(char in value for char in ('\x00', '\r', '\n')):
        return None
    drive, tail = ntpath.splitdrive(value)
    if not drive or not tail.startswith(('\\', '/')):
        return None
    return ntpath.normcase(ntpath.normpath(value))


def windows_arguments(command_line):
    """由Windows解析引号与反斜线，启动参数只在本进程内使用，禁止输出。"""
    count = ctypes.c_int()
    parse = ctypes.windll.shell32.CommandLineToArgvW
    parse.argtypes = (ctypes.c_wchar_p, ctypes.POINTER(ctypes.c_int))
    parse.restype = ctypes.POINTER(ctypes.c_wchar_p)
    arguments = parse(command_line, ctypes.byref(count))
    if not arguments:
        raise RuntimeError("无法解析Java进程身份，拒绝替换目标实例")
    try:
        return [arguments[index] for index in range(count.value)]
    finally:
        free = ctypes.windll.kernel32.LocalFree
        free.argtypes = (ctypes.c_void_p,)
        free.restype = ctypes.c_void_p
        free(ctypes.cast(arguments, ctypes.c_void_p))


def classify_java_process(process):
    """仅返回PID和分类；明确的其他gameDir可忽略，未知游戏身份仍拒绝。"""
    pid = process.get("ProcessId")
    if not isinstance(pid, int) or isinstance(pid, bool):
        raise RuntimeError("Java进程清单身份无效，拒绝替换目标实例")
    command_line = process.get("CommandLine")
    if not isinstance(command_line, str) or not command_line.strip():
        return {"pid": pid, "classification": "unresolved_java_identity", "blocks_target_replace": True}
    arguments = windows_arguments(command_line)
    entrypoint = any(re.fullmatch(r"org\.(?:multimc|prismlauncher)\.EntryPoint", value, re.IGNORECASE)
                     for value in arguments)
    game_client = entrypoint or any(value.casefold() == "forgeclient" or
                                   value.casefold().startswith("cpw.mods.modlauncher.") for value in arguments)
    game_dirs, referenced_paths = [], []
    for index, value in enumerate(arguments):
        folded = value.casefold()
        if folded in ("--gamedir", "--game-dir"):
            game_dirs.append(normalized_absolute_path(arguments[index + 1]) if index + 1 < len(arguments) else None)
        elif folded.startswith(("--gamedir=", "--game-dir=")):
            game_dirs.append(normalized_absolute_path(value.split("=", 1)[1]))
        # classpath、-D属性和独立路径按完整路径分解，绝不做路径子串匹配。
        for candidate in (value, value.split("=", 1)[1] if "=" in value else ""):
            for part in candidate.split(";"):
                absolute = normalized_absolute_path(part)
                if absolute:
                    referenced_paths.append(absolute)
    target_instance = normalized_absolute_path(str(INSTANCE))
    target_game = normalized_absolute_path(str(INSTANCE / "minecraft"))
    local_hk_jar = normalized_absolute_path(str(SOURCE))
    target_hk_jar = normalized_absolute_path(str(TARGET))
    require_paths = (target_instance, target_game, local_hk_jar, target_hk_jar)
    if not all(require_paths):
        raise RuntimeError("目标实例或构建JAR不是可确认的绝对路径，拒绝部署")
    references_target = any(path == target_instance or path.startswith(target_instance + "\\") or
                            path in (local_hk_jar, target_hk_jar) for path in referenced_paths)
    if references_target:
        return {"pid": pid, "classification": "target_instance_or_hk_jar", "blocks_target_replace": True}
    if game_client:
        # 仅明确另一个绝对gameDir才允许忽略；不以Java位置或PCL/Prism名称推断。
        if game_dirs and all(path is not None and path not in (target_instance, target_game) for path in game_dirs):
            return {"pid": pid, "classification": "explicit_other_game_dir", "blocks_target_replace": False}
        if entrypoint:
            evidence = verified_other_prism(process, arguments, INSTANCE)
            if evidence.get("target_cwd"):
                return {"pid": pid, "classification": "target_instance_actual_cwd", "blocks_target_replace": True,
                        "identity_evidence": evidence}
            if evidence["verified"]:
                return {"pid": pid, "classification": "verified_other_prism_actual_cwd", "blocks_target_replace": False,
                        "identity_evidence": evidence}
            return {"pid": pid, "classification": "unresolved_prism_entrypoint", "blocks_target_replace": True,
                    "identity_evidence": evidence}
        return {"pid": pid, "classification": "unresolved_prism_entrypoint" if entrypoint else "unresolved_game_client",
                "blocks_target_replace": True}
    return {"pid": pid, "classification": "other_java_process", "blocks_target_replace": False}


def target_process_guard():
    """只读查询；原始命令行不进入工具输出、异常或部署收据。"""
    command = ("[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false); "
               "@(Get-CimInstance Win32_Process -Filter \"Name='java.exe' OR Name='javaw.exe'\" "
               "-ErrorAction Stop | Select-Object ProcessId,CommandLine,"
               "@{Name='CreationTimeUtc';Expression={$_.CreationDate.ToUniversalTime().ToString('o')}}) "
               "| ConvertTo-Json -Compress -Depth 3")
    query = subprocess.run(["powershell.exe", "-NoProfile", "-Command", command], capture_output=True,
                           encoding="utf-8", errors="strict", check=False)
    if query.returncode != 0:
        raise RuntimeError("无法只读核实Java进程身份，拒绝替换目标实例")
    try:
        processes = json.loads(query.stdout.lstrip("\ufeff").strip() or "[]")
    except (TypeError, ValueError):
        raise RuntimeError("Java进程身份查询格式无效，拒绝替换目标实例") from None
    if isinstance(processes, dict):
        processes = [processes]
    if not isinstance(processes, list) or not all(isinstance(process, dict) for process in processes):
        raise RuntimeError("Java进程清单无效，拒绝替换目标实例")
    decisions = [classify_java_process(process) for process in processes]
    blocking = [decision for decision in decisions if decision["blocks_target_replace"]]
    if blocking:
        safe_ids = ", ".join(str(decision["pid"]) + ":" + decision["classification"] for decision in blocking)
        raise RuntimeError("目标实例运行中或游戏身份无法确认，保留原JAR；进程分类：" + safe_ids)
    return {"policy": "exact_target_paths_explicit_game_dir_or_verified_prism_actual_cwd",
            "checked_at": datetime.now(timezone(timedelta(hours=8))).isoformat(),
            "decisions": decisions, "raw_command_lines_recorded": False, "target_replace_allowed": True}


def stopped(expected_revision=165):
    if expected_revision >= 172:
        return target_process_guard()
    command = "@(Get-CimInstance Win32_Process -Filter \"Name='java.exe' OR Name='javaw.exe'\" | Where-Object { $_.CommandLine -match 'forgeclient|org\\.(?:multimc|prismlauncher)\\.EntryPoint|cpw\\.mods\\.modlauncher' }).Count"
    count = subprocess.check_output(["powershell.exe", "-NoProfile", "-Command", command], text=True).strip()
    if count != "0":
        raise RuntimeError("游戏尚在运行，保留已构建产物，不替换实例JAR")


def main(expected_revision=165, output_dir=None):
    assert expected_revision in (165, 166, 171, 172, 174)
    output_dir = Path(output_dir) if output_dir is not None else (
        ROOT / "logs/energy-carriers-r174-20261020" if expected_revision == 174 else
        ROOT / "logs/voltage-architecture-r172" if expected_revision == 172 else ROOT / "logs/main-materials-r165")
    manifest = json.loads((INSTANCE / "mrpack/modrinth.index.json").read_text(encoding="utf-8-sig"))
    expected_instance = "2.9" if expected_revision >= 171 else "2.8"
    assert manifest["versionId"] == expected_instance, "目标包版本变化，须重新核验"
    process_guard_before_verify = stopped(expected_revision)
    if not verify(expected_revision, output_dir):
        raise RuntimeError("最终JAR静态核验未通过，拒绝部署；检查" + str(output_dir / "package-verification.json"))
    verification_path = output_dir / "package-verification.json"
    verification = json.loads(verification_path.read_text(encoding="utf-8"))
    verified_sha = verification["sha256"]
    if verification["status"] != "passed" or verification["revision"] != expected_revision or sha(SOURCE) != verified_sha:
        raise RuntimeError("最终包身份与本轮核验收据不一致，拒绝部署")
    with zipfile.ZipFile(SOURCE) as archive:
        assert archive.testzip() is None
        revision = json.loads(archive.read("assets/hk3gtl/changelog.json"))["entries"][0]["revision"]
        assert revision == expected_revision
        for entry in (
            "com/sirin/hk3gtl/common/recipe/audit/RecipeReachability.class",
            "com/sirin/hk3gtl/common/registration/Hk3IndustrialDependencyAudit.class",
            "com/sirin/hk3gtl/common/registration/Hk3IndustrialAuditReport.class",
            "com/sirin/hk3gtl/common/research/Hk3ResearchRequirementPolicy.class",
            "com/sirin/hk3gtl/common/research/Hk3RecipeAccess.class",
        ):
            assert entry in archive.namelist(), entry
        plans = {p["id"]: p for p in json.loads(archive.read("data/hk3gtl/research/industrial_processes.json"))["recipes"]}
        assert plans["industrial_soulium_polymerization"]["item_outputs"][0]["id"] == "hk3gtl:soulium_proto_mass"
        assert not any("Hk3Beta5" in entry for entry in archive.namelist())
        gate_class = archive.read("com/sirin/hk3gtl/common/research/Hk3RecipeResearchGate.class")
        assert b"LEGACY_NODE_REDIRECT" not in gate_class and b"Hk3ResearchNodes" not in gate_class
        language = json.loads(archive.read("assets/hk3gtl/lang/zh_cn.json"))
        assert language["hk3gtl.jei.research_summary"] == "研究门槛：%s"
        widget = archive.read("com/sirin/hk3gtl/mixin/GTRecipeWidgetMixin.class")
        assert b"TextBoxWidget" in widget and b"research_detail_hint" not in widget
        retired_classes = (
            "common/recipe/Hk3RecipeTypesImaginary", "common/recipe/Hk3RecipeTypesQuantum",
            "common/recipe/Hk3RecipeTypesFinality", "common/recipe/Hk3RecipeTypesWonder",
            "common/recipe/Hk3CircuitSeriesRecipes", "common/recipe/max/MaxStageRecipes",
            "common/recipe/abyss/AbyssMachineRecipes", "common/recipe/imaginary/ImaginaryChainRecipes",
            "common/recipe/imaginary/ImaginaryMachineRecipes", "common/recipe/imaginary/ImaginaryCircuitRecipes",
            "common/recipe/quantum/QuantumStageRecipes", "common/recipe/finality/FinalityStageRecipes",
            "common/machine/imaginary/Hk3ImaginaryAnchor",
        )
        names = set(archive.namelist())
        assert not any("com/sirin/hk3gtl/" + name + ".class" in names for name in retired_classes), "构建混入退役类"
        for description in (ROOT / "src/main/resources/data/hk3gtl/approved_architecture").glob("*.json"):
            assert archive.read("data/hk3gtl/approved_architecture/" + description.name) == description.read_bytes()
    assert TARGET.is_file(), "预期实例JAR不存在，禁止推断其他目标"
    stamp = datetime.now(timezone(timedelta(hours=8))).strftime("%Y%m%d_%H%M%S")
    backup = INSTANCE / "minecraft/hk3gtl-mod-backups" / (stamp + "_industrial_r" + str(revision))
    backup.mkdir(parents=True, exist_ok=False)
    before = {p.name: sha(p) for p in TARGET.parent.glob("*.jar")}
    shutil.copy2(TARGET, backup / TARGET.name)
    assert sha(backup / TARGET.name) == before[TARGET.name]
    pending = TARGET.with_suffix(".industrial-pending")
    assert not pending.exists(), "存在先前未完成部署，须先核验"
    try:
        shutil.copy2(SOURCE, pending)
        if sha(pending) != verified_sha or sha(SOURCE) != verified_sha:
            raise RuntimeError("复制期间构建产物发生变化，保留原实例JAR")
        process_guard_before_replace = stopped(expected_revision)
        os.replace(pending, TARGET)
    finally:
        if pending.exists():
            pending.unlink()
    after = {p.name: sha(p) for p in TARGET.parent.glob("*.jar")}
    assert before.keys() == after.keys()
    assert all(after[name] == digest for name, digest in before.items() if name != TARGET.name)
    assert sha(TARGET) == sha(SOURCE) == verified_sha
    receipt = dict(time=stamp, revision=revision, manifest_version=expected_instance, instance=str(INSTANCE),
                   target=str(TARGET), backup=str(backup), sha256=sha(TARGET),
                   bytes=TARGET.stat().st_size, third_party_jars_unchanged=True,
                   package_verification=str(verification_path), package_verification_sha256=sha(verification_path),
                   main_material_items_verified=231, main_material_textures_verified=586, main_material_models_verified=231,
                   game_acceptance="尚未运行本修订的游戏内验收")
    if expected_revision >= 174:
        receipt.update(energy_carrier_items_verified=verification["energy_carrier_items"],
                       energy_carrier_models_verified=verification["energy_carrier_models"],
                       energy_carrier_texture_layers_verified=verification["energy_carrier_texture_layers"],
                       energy_carrier_manifest_sha256=verification["carrier_manifest_sha256"])
    if expected_revision >= 172:
        receipt["process_guards"] = {"before_verification": process_guard_before_verify,
                                   "before_atomic_replace": process_guard_before_replace}
    path = output_dir / "deployment.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="仅向指定增强版实例停机部署已核验的HK3包")
    parser.add_argument("--expected-revision", type=int, choices=(165, 166, 171, 172, 174), default=165)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    main(args.expected_revision, args.output_dir)
