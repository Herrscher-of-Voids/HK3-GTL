# -*- coding: utf-8 -*-
"""只读核对主材料系统正式交付包，失败仍保存证据，不修改实例。
【变更记录 #1】2026-10-17 17:12:07（修订165）
删除：无；新增：已批准231项资源、双语、退役类、功率Mixin及建筑原字节核对。
修改：核验必须读取本轮正式JAR和完整构建日志；用途：阻止旧包、漏资源或未批准替换被记为新交付。
【变更记录 #2】2026-10-17 17:12:52（修订165）
删除：把初次资源复制日志当最终证据的可能；新增：专门读取最终重构日志。
修改：构建入口使用build-final.log；用途：第一次资源复制早于变更记录落盘，最终核验须等待重构完成。
【变更记录 #3】2026-10-17 17:14:49（修订165）
删除：无；新增：机壳、电路、电子和实际运行导出入口打包核验与源码身份。
修改：把消费者入口纳入交付类清单；用途：避免只包含材料目录而漏掉正式消费者或总入口。
【变更记录 #4】2026-10-17 17:16:12（修订165）
删除：Mixin配置必须与源码字节相同的过严判据；新增：仅允许Loom添加已存在的hk3gtl-refmap.json引用。
修改：去除该一个构建字段后精确比较完整JSON；用途：接受已核实的正常映射处理，其他配置差异仍拒绝。
【变更记录 #5】2026-10-17 17:53:15（修订165）
删除：无；新增：十条光刻副本包装类的交付核验；修改：当前消费者类清单；用途：确保实机修复进入重构包。
【变更记录 #6】2026-10-17 18:06:37（修订165）
删除：无；新增：自建规划器判别类打包核验；修改：功率类清单；用途：防止漏打拒绝未知执行器的实机修复。
【变更记录 #7】2026-10-17 19:13:39（修订165，香港时间UTC+08:00）
删除：当前包仍按旧231单层PNG验收的失效判据，旧批准文件与工具快照保留历史。
新增：V2冻结清单、明确批准、精确231模型和586纹理白名单、逐层四方SHA、GT原色覆盖层、
191旧单层及231旧模型归档核对；源码静态模式不读取旧包冒充新包。
修改：正式包必须等于V2完整模型层栈，40项继续保持旧PNG及模型字节；原代码、双语、
建筑、Mixin及clean/check/build判据继续生效。用途：阻止漏层、混入旧平图或批准身份漂移。
【变更记录 #8】2026-10-17 21:51:05（修订166）
删除：完整核验只能用于固定165修订的限制；新增：显式166修订及独立日志目录参数。
修改：165批准资料仍从原冻结目录读取，166额外核对高度类、映射和双语；用途：继承原资源和建筑严格判据，避免覆盖历史收据或放宽包身份。
【变更记录 #9】2026-10-19 02:08:05（修订171，香港时间）
删除：新修订仍固定使用2.8清单的失效条件；新增：171机器总览类与Mixin打包核验。
修改：171显式核对增强版2.9并保留高度、主材批准字节与正式建筑全部判据。
用途：在独立构建证据目录核验本轮交付，不把静态检查写成游戏验收。
【变更记录 #10】2026-10-20 00:47:44（修订172，香港时间）
删除：本轮获批改色仍须等于上一安装建筑JSON的失效限制，历史165/166/171分支原样保留。
新增：172批准冻结清单、63项正式JSON/NBT资源与归档原字节核验；修改：172继承2.9及总览、
高度、主材231模型/586层和全部Mixin判据；用途：只接受本批明确获批21形态，不放松其他交付身份。
【变更记录 #11】2026-10-20 03:58:51（修订174，香港时间）
删除：无；保留165/166/171/172历史合同。新增：13项已批准载体、13模型、29贴图层的冻结清单与JAR原字节核验。
修改：174继承21形态建筑审批合同并单独统计载体资源；用途：只接入明确批准的载体贴图，不将燃料/乏料候选或配方误记为已批准。
"""
import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path, PurePosixPath
import hashlib
import json
import os
import struct
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "logs/main-materials-r165"
SOURCE = ROOT / "build/libs/hk3gtl-0.5.0.jar"
INSTANCE = Path(os.environ["APPDATA"]) / "PrismLauncher/instances/GregTech Leisure-增强版"
TARGET = INSTANCE / "minecraft/mods/HK3GTL-内测5.jar"
DELIVERY = ROOT / "deliveries/16阶主材料贴图修正候选_V2_20261017"
OLD_DELIVERY = ROOT / "deliveries/16阶主材料贴图候选_R165_20261017"
V2_MANIFEST_SHA = "984b70758f387248b029d22bcf65c6e66ad9a01220c6e662b4f16a39ac272070"
OLD_MANIFEST_SHA = "d24548448fe9848fafa42f5c61c614d77092532fc3b0b1e4794b8729b51a7e0b"
OLD_APPROVAL_SHA = "61a96536be5a731d77f9dc35d2b9797de4367c8348b345455b9c58d223051f7a"
RESOURCES = ROOT / "src/main/resources"
VOLTAGE_ARCHIVE = ROOT / "deliveries/多方块确认归档/20261020_005209_151059_21形态_电压主色修订_已确认"
VOLTAGE_MANIFEST_SHA = "cbec17435908b7e9a6c93efa0f333d0051fc8ef9a9bd7aa46f92a523c2bf8762"
VOLTAGE_ARCHIVE_ZIP_SHA = "218502218f518604b24e6f696a10913ad7a6cf3f30a2c0c3e1138878b1bc5641"
VOLTAGE_CANDIDATE = ROOT / "deliveries/21形态_电压主色修订候选_R172_20261019"
VOLTAGE_KEYS = frozenset(["i01", "i01_2", "i01_3", "i01_4"] +
                         [f"i{number:02d}" for number in range(2, 14)] +
                         [f"s{number:02d}" for number in range(1, 6)])
CARRIER_ARCHIVE = ROOT / "deliveries/能源载体_13项已采用_20261020_011231_794351"
CARRIER_MANIFEST_SHA = "916ba326dbfce839d84053050c3f8097a8b487d45144fa6a46e8ebfa6011e3d8"
CARRIER_SOURCE_ZIP_SHA = "cc3ea4a47a2b687dbab9e28b2faeb53ebfa59e167b848197a01e4eff286c158c"
CARRIER_NAMES_ZH = {
    "honkai_carbon_carrier": "吸附碳芯载体",
    "honkai_zeolite_carrier": "分子筛载体",
    "honkai_silica_gel_carrier": "硅胶凝固载体",
    "honkai_silicon_carbide_carrier": "碳化硅多孔陶瓷载体",
    "honkai_boron_carbide_carrier": "碳化硼梯度颗粒载体",
    "honkai_zirconia_carrier": "氧化锆梯度陶瓷载体",
    "honkai_diamond_copper_carrier": "金刚石铜骨架载体",
    "honkai_graphene_carrier": "石墨烯层间载体",
    "honkai_titanium_carbide_carrier": "碳化钛金属陶瓷载体",
    "honkai_alumina_carrier": "氧化铝绝缘微珠载体",
    "honkai_tungsten_carrier": "钨微通道载体",
    "honkai_ptfe_membrane_carrier": "PTFE冷端膜匣载体",
    "honkai_pbi_microcapsule_carrier": "PBI冷端微胶囊载体",
}
POWER_MIXINS = ("Hk3PowerRecipeMixin", "Hk3PowerModifierMixin", "Hk3PowerLogicMixin", "gtlcore.Hk3PowerBatchMixin")
REQUIRED_CLASSES = (
    "common/material/main/Hk3MainMaterialCatalog", "common/item/main/Hk3MainMaterialItems",
    "common/recipe/main/Hk3MainMaterialRecipes", "common/recipe/main/Hk3MainMaterialAccess",
    "common/recipe/main/Hk3MainMaterialProductionLower", "common/recipe/main/Hk3MainMaterialProductionUpper",
    "common/recipe/main/Hk3MainMaterialFormRecipes", "common/recipe/main/Hk3MainMaterialRecoveryRecipes",
    "common/recipe/main/Hk3MainMaterialUnits", "common/recipe/main/Hk3MainComponentRecipes",
    "common/recipe/power/Hk3PowerBudget", "common/recipe/power/Hk3PowerPorts",
    "common/recipe/power/Hk3PowerWork", "common/recipe/power/Hk3RecipePower", "common/recipe/power/Hk3PowerPlanner",
    "common/recipe/Hk3CircuitManufacturing", "common/recipe/Hk3ElectronicRecipes", "common/recipe/Hk3ElectronicRecipeCopies",
    "common/recipe/machine/Hk3VoltageCasingRecipes", "common/recipe/Hk3RecipeAdderImpl",
    "common/registration/Hk3ResearchRuntimeAudit",
)
RETIRED_CLASSES = (
    "common/recipe/Hk3RecipeTypesImaginary", "common/recipe/Hk3RecipeTypesQuantum",
    "common/recipe/Hk3RecipeTypesFinality", "common/recipe/Hk3RecipeTypesWonder",
    "common/recipe/Hk3CircuitSeriesRecipes", "common/recipe/max/MaxStageRecipes",
    "common/recipe/abyss/AbyssMachineRecipes", "common/recipe/imaginary/ImaginaryChainRecipes",
    "common/recipe/imaginary/ImaginaryMachineRecipes", "common/recipe/imaginary/ImaginaryCircuitRecipes",
    "common/recipe/quantum/QuantumStageRecipes", "common/recipe/finality/FinalityStageRecipes",
    "common/machine/imaginary/Hk3ImaginaryAnchor", "common/recipe/abyss/AbyssComponentRecipes",
    "common/recipe/imaginary/ImaginaryComponentRecipes", "common/recipe/quantum/QuantumComponentRecipes",
)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def approved_voltage_architecture(archive=None):
    """172独立批准合同：冻结清单和ZIP授权，收据自述及上一安装包不作为新配色授权。"""
    if archive is not None:
        require(len(archive.namelist()) == len(set(archive.namelist())), "172 JAR包含重复资源路径")
    manifest_path = VOLTAGE_ARCHIVE / "确认与校验清单.json"
    manifest_bytes = manifest_path.read_bytes()
    require(digest(manifest_bytes) == VOLTAGE_MANIFEST_SHA, "172建筑批准冻结清单被改写")
    manifest = json.loads(manifest_bytes)
    require(manifest["approval_quote"] == "采用整批21形态新配色" and manifest["shape_count"] == 21,
            "172缺少本批21形态明确批准")
    rows = manifest["structures"]
    require(len(rows) == 21 and {row["key"] for row in rows} == VOLTAGE_KEYS,
            "172批准建筑身份不是精确21项")
    inheritance = manifest["inheritance_checks"]
    required_links = {("i01-1", "i01-2"), ("i01-2", "i01-3"), ("i01-3", "i01-4")} | {
        (f"s{number:02d}", f"s{number+1:02d}") for number in range(1, 5)}
    require(len(inheritance) == 7 and {(row["from"], row["to"]) for row in inheritance} == required_links
            and all(row["passed"] is True for row in inheritance), "172扩建继承批准证据不完整")

    def contained_file(base, value):
        require(isinstance(value, str) and value, "172资源路径为空或类型错误")
        path = (ROOT / value).resolve(strict=True)
        require(path.is_file() and path.is_relative_to(base.resolve()), "172资源或归档路径越界")
        return path

    archive_zip = VOLTAGE_ARCHIVE.with_suffix(".zip")
    require(digest(archive_zip.read_bytes()) == VOLTAGE_ARCHIVE_ZIP_SHA, "172批准冻结ZIP被改写")
    frozen_formal = VOLTAGE_ARCHIVE / "formal_resources"
    frozen_candidate = VOLTAGE_ARCHIVE / "confirmed_voltage_r172"
    with zipfile.ZipFile(archive_zip) as frozen_zip:
        require(frozen_zip.testzip() is None, "172批准冻结ZIP的CRC无效")
        all_zip_names = frozen_zip.namelist()
        require(len(all_zip_names) == len(set(all_zip_names)), "172冻结ZIP存在重复路径")
        frozen_names = {name for name in all_zip_names if not name.endswith("/")}
        for name in all_zip_names:
            value = PurePosixPath(name)
            require(not value.is_absolute() and ".." not in value.parts and "\\" not in name,
                    "172冻结ZIP包含越界路径")
        frozen_files = {path.relative_to(VOLTAGE_ARCHIVE).as_posix(): path
                        for path in VOLTAGE_ARCHIVE.rglob("*") if path.is_file()}
        require(set(frozen_files) == frozen_names, "172冻结归档文件集合与批准ZIP不同")
        for name, path in frozen_files.items():
            require(path.resolve().is_relative_to(VOLTAGE_ARCHIVE.resolve()), "172冻结归档链接越界")
            require(path.read_bytes() == frozen_zip.read(name), "172冻结归档不是批准ZIP原字节：" + name)

    candidate_zip_name = "21形态_电压主色修订候选_R172_结构与预览.zip"
    for candidate_root in (VOLTAGE_CANDIDATE, frozen_candidate):
        require(digest((candidate_root / candidate_zip_name).read_bytes()) == manifest["candidate_zip_sha256"],
                "172候选原ZIP或冻结复制发生变化")
        require(digest((candidate_root / "manifest.json").read_bytes()) == manifest["candidate_manifest_sha256"],
                "172候选身份清单或冻结复制发生变化")
    candidate_identity = json.loads((VOLTAGE_ARCHIVE / "evidence/候选原件身份.json").read_text(encoding="utf-8"))
    current_candidate_files = {path.relative_to(ROOT).as_posix() for path in VOLTAGE_CANDIDATE.rglob("*") if path.is_file()}
    require(current_candidate_files == set(candidate_identity), "172候选原件集合发生变化")
    for relative, expected_sha in candidate_identity.items():
        path = contained_file(VOLTAGE_CANDIDATE, relative)
        require(digest(path.read_bytes()) == expected_sha, "172候选原件字节发生变化：" + relative)

    architecture, expected_resources = [], set()
    for row in rows:
        key = row["key"]
        require(row["controller_and_six_port_positions_unchanged"] is True and row["other_cells_exact_candidate"] is True,
                key + "缺少控制器/六仓及候选几何保持证据")
        candidate_key = {"i01": "i01-1", "i01_2": "i01-2", "i01_3": "i01-3", "i01_4": "i01-4"}.get(key, key)
        require(row["candidate_key"] == candidate_key, key + "候选身份对应错误")
        for field, extension in (("source_blueprint", ".json"), ("source_nbt", ".nbt"), ("source_schem", ".schem")):
            source = contained_file(frozen_candidate, row[field])
            expected_name = "blueprint.json" if field == "source_blueprint" else candidate_key + "-voltage-r172" + extension
            require(source == (frozen_candidate / candidate_key / expected_name).resolve(), key + "批准候选路径错误")
            require(digest(source.read_bytes()) == row[field + "_sha256"], key + "批准候选原字节发生变化")
        expected_row_paths = {f"approved_architecture/{key}.json", f"structures/approved/{key}.nbt",
                              f"structures/approved/{key}.json"}
        require(set(row["formal_sha256"]) == expected_row_paths == set(row["previous_formal_sha256"]),
                key + "正式或旧正式三类资源路径不符")
        for relative, expected_sha in row["formal_sha256"].items():
            resource = "data/hk3gtl/" + relative
            formal_path = contained_file(RESOURCES / "data/hk3gtl", str(RESOURCES / resource))
            frozen_path = contained_file(frozen_formal, str(frozen_formal / relative))
            formal_bytes = formal_path.read_bytes()
            require(digest(formal_bytes) == expected_sha and formal_bytes == frozen_path.read_bytes(),
                    resource + "不是172批准冻结正式原字节")
            if archive is not None:
                require(archive.read(resource) == formal_bytes, resource + "JAR与源码及批准冻结正式资源不同")
            previous_path = contained_file(VOLTAGE_ARCHIVE / "evidence/previous_formal_resources",
                                           str(VOLTAGE_ARCHIVE / "evidence/previous_formal_resources" / relative))
            require(digest(previous_path.read_bytes()) == row["previous_formal_sha256"][relative],
                    resource + "旧正式资源归档SHA不同")
            expected_resources.add(resource)
            architecture.append({"key": key, "path": resource, "sha256": expected_sha,
                                 "matches_source_and_frozen_approval": True,
                                 "jar_matches_source": archive is not None})
        current = json.loads((RESOURCES / "data/hk3gtl/approved_architecture" / (key + ".json")).read_text(encoding="utf-8"))
        previous = json.loads((VOLTAGE_ARCHIVE / "evidence/previous_formal_resources/approved_architecture" / (key + ".json")).read_text(encoding="utf-8"))
        require(current["key"] == key and current["size"] == row["size_xyz"] and current["target_voltage"] == row["voltage"]
                and current["target_casing"] == row["casing"], key + "正式建筑身份或电压偏离批准")
        require(all(current[field] == previous[field] for field in ("controller", "ports"))
                and ("runtime_contract" in current) == ("runtime_contract" in previous)
                and current.get("runtime_contract") == previous.get("runtime_contract"),
                key + "控制器/仓位或能力合同被擅改")
        old_source = row["previous_approved_source"]
        if "blueprint" in old_source:
            old_blueprint = contained_file(ROOT / "deliveries/多方块确认归档", old_source["blueprint"])
            require(digest(old_blueprint.read_bytes()) == old_source["sha256"], key + "旧批准蓝图归档发生变化")
        else:
            # 研究所原批准合同保存的是归档目录与原NBT身份，不能臆造其不存在的blueprint字段。
            old_snapshot = (ROOT / old_source["snapshot"]).resolve(strict=True)
            require(old_snapshot.is_dir() and old_snapshot.is_relative_to((ROOT / "deliveries/多方块确认归档").resolve()),
                    key + "旧研究所批准归档目录越界")
            require(any(path.resolve().is_relative_to(old_snapshot) and digest(path.read_bytes()) == old_source["nbt_sha256"]
                        for path in old_snapshot.rglob("*.nbt")), key + "旧批准研究所NBT归档缺失或改变")
    prefixes = ("data/hk3gtl/approved_architecture/", "data/hk3gtl/structures/approved/")
    formal_files = {path.relative_to(RESOURCES).as_posix() for prefix in prefixes
                    for path in (RESOURCES / prefix).rglob("*") if path.is_file()}
    require(len(expected_resources) == 63 and formal_files == expected_resources, "172正式资源不是精确21形态/63文件")
    if archive is not None:
        packed_files = {name for name in archive.namelist() if name.startswith(prefixes) and not name.endswith("/")}
        require(packed_files == expected_resources, "172 JAR三类批准建筑资源集合不同")
    return {"architecture": architecture, "manifest_path": str(manifest_path), "manifest_sha256": VOLTAGE_MANIFEST_SHA,
            "archive_zip_sha256": VOLTAGE_ARCHIVE_ZIP_SHA, "formal_file_count": 63, "shape_count": 21,
            "candidate_original_files_checked": len(candidate_identity), "frozen_archive_files_checked": len(frozen_files),
            "checks": {"approved_21_architecture_frozen_manifest": True, "approved_63_architecture_original_bytes": True,
                       "approved_architecture_controller_ports_contract_unchanged": True,
                       "approved_architecture_candidates_and_previous_sources_unchanged": True}}


def approved_assets(archive=None):
    """使用同一获批白名单核验源码与可选JAR；归档只读，绝不由当前正式文件反推旧身份。"""
    candidate_path = DELIVERY / "修正候选与完整图层清单.json"
    require(digest(candidate_path.read_bytes()) == V2_MANIFEST_SHA, "V2冻结候选清单被改写")
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    approval_path = LOG / "asset-approval-and-installation-v2.json"
    approval = json.loads(approval_path.read_text(encoding="utf-8"))
    old_approval_path = LOG / "asset-approval-and-installation.json"
    old_manifest_path = OLD_DELIVERY / "候选资源与来源清单.json"
    old_approval = json.loads(old_approval_path.read_text(encoding="utf-8"))
    old_candidate = json.loads(old_manifest_path.read_text(encoding="utf-8"))
    require(approval["schema"] == 2 and approval["revision"] == 165, "V2批准记录版本不符")
    require(approval["user_answer"] == "采用V2，整批接入正式资源", "缺少本批V2明确批准")
    require(approval["candidate_manifest_sha256"] == V2_MANIFEST_SHA, "安装依据不是已批准冻结V2")
    require(approval["installed_count"] == approval["model_count"] == 231 and approval["texture_count"] == 586,
            "安装记录不是精确231模型/586层")
    require(digest(old_approval_path.read_bytes()) == approval["previous_approval_sha256"] == OLD_APPROVAL_SHA,
            "旧批准历史被改写")
    require(digest(old_manifest_path.read_bytes()) == approval["previous_candidate_manifest_sha256"] == OLD_MANIFEST_SHA,
            "旧候选清单历史被改写")
    manifest = json.loads((LOG / "item-manifest.json").read_text(encoding="utf-8"))
    expected = {row["id"]: row for row in manifest["items"]}
    candidates = {row["id"]: row for row in candidate["items"]}
    installed = {row["id"]: row for row in approval["installed"]}
    prior = {row["id"]: row for row in old_candidate["items"]}
    prior_installed = {row["id"]: row for row in old_approval["installed"]}
    require(len(expected) == len(candidates) == len(installed) == 231, "V2身份数量或重复项不符")
    require(len(approval["installed"]) == len(candidate["items"]) == len(manifest["items"]) == 231,
            "V2身份记录含重复或多余条目")
    require(expected.keys() == candidates.keys() == installed.keys() == prior.keys() == prior_installed.keys(),
            "V2与物品注册、旧批准身份集合不同")
    review = json.loads((LOG / "texture-v2-independent-review.json").read_text(encoding="utf-8"))
    require(review["result"] == "PASS" and review["manifest_sha256"] == V2_MANIFEST_SHA,
            "缺少冻结V2完整图层独立审查")
    require(review["item_count"] == 231 and review["checks"]["all_layers"] == 586 and not review["issues"],
            "完整图层独立审查范围不符")
    protected = {str(Path(path).resolve()).casefold(): value for path, value in candidate["preserved_files_sha256"].items()}
    for path in OLD_DELIVERY.rglob("*"):
        if path.is_file():
            require(digest(path.read_bytes()) == protected[str(path.resolve()).casefold()], "旧候选历史发生变化：" + str(path))
    changed_ids = {key for key, row in candidates.items() if row["model_layers_restored"]}
    require(len(changed_ids) == 191, "V2漏层修正身份不是精确191项")
    archives = {row["id"]: row for row in approval["old_single_layer_archive"]}
    model_history = {row["id"]: row for row in approval["model_history_archive"]}
    require(len(approval["old_single_layer_archive"]) == len(archives) == 191 and archives.keys() == changed_ids,
            "旧单层归档身份不是精确191项")
    require(len(approval["model_history_archive"]) == len(model_history) == 231 and model_history.keys() == expected.keys(),
            "旧模型归档身份不是精确231项")
    for key, row in model_history.items():
        path = "assets/hk3gtl/models/item/" + key.split(":", 1)[1] + ".json"
        require(row["path"] == path, key + "旧模型归档资源路径错误")
        saved = ROOT / row["archive_path"]
        require(saved.resolve().is_relative_to((ROOT / "logs").resolve()), "旧模型归档路径越界")
        require(digest(saved.read_bytes()) == row["sha256"] == protected[str((RESOURCES / path).resolve()).casefold()],
                key + "旧模型归档SHA不符")
    for key, row in archives.items():
        path = "assets/hk3gtl/textures/item/main_material/" + key.split(":", 1)[1] + ".png"
        require(row["path"] == path, key + "旧单层归档资源路径错误")
        saved = ROOT / row["archive_path"]
        require(saved.resolve().is_relative_to((ROOT / "logs").resolve()), "旧单层归档路径越界")
        require(digest(saved.read_bytes()) == row["sha256"] == prior[key]["candidate_sha256"]
                == prior_installed[key]["texture_sha256"], key + "旧单层归档身份或SHA不符")
        require(not (RESOURCES / path).exists(), key + "旧单层贴图残留正式资源")
    zh = json.loads((RESOURCES / "assets/hk3gtl/lang/zh_cn.json").read_text(encoding="utf-8"))
    en = json.loads((RESOURCES / "assets/hk3gtl/lang/en_us.json").read_text(encoding="utf-8"))
    expected_png, expected_models, items = set(), set(), []
    gt_path = Path(candidate["source_jar"]["path"])
    require(digest(gt_path.read_bytes()) == candidate["source_jar"]["sha256"], "原GT模型来源JAR已改变")
    with zipfile.ZipFile(gt_path) as gt:
        for key, item in expected.items():
            approved = candidates[key]
            receipt = installed[key]
            ident = key.split(":", 1)[1]
            model_path = "assets/hk3gtl/models/item/" + ident + ".json"
            model_bytes = (RESOURCES / model_path).read_bytes()
            candidate_model = (DELIVERY / approved["model_relative"]).read_bytes()
            require(receipt["model_path"] == model_path, key + "安装模型路径错误")
            require(digest(model_bytes) == receipt["model_sha256"] == approved["model_sha256"], key + "模型SHA偏离批准")
            require(model_bytes == candidate_model, key + "源码模型不是批准候选原字节")
            if archive is not None:
                require(archive.read(model_path) == model_bytes, key + "JAR模型不是源码原字节")
            model = json.loads(model_bytes)
            require(model["parent"] in ("minecraft:item/generated", "item/generated"), key + "模型父级错误")
            require(len(receipt["layers"]) == len(approved["layers"]), key + "安装层数错误")
            require(len({layer["layer"] for layer in receipt["layers"]}) == len(receipt["layers"]), key + "安装层编号重复")
            require(set(model["textures"]) == {layer["layer"] for layer in approved["layers"]}, key + "模型层集合缺失或增加")
            installed_layers = {layer["layer"]: layer for layer in receipt["layers"]}
            layers = []
            for layer in approved["layers"]:
                number = layer["layer"]
                candidate_layer = DELIVERY / layer["candidate_relative"]
                texture_path = str(candidate_layer.relative_to(DELIVERY / "候选分层资源")).replace("\\", "/")
                require(texture_path.startswith("assets/hk3gtl/textures/item/main_material/"), key + "纹理路径越界")
                require(texture_path not in expected_png, key + "不同候选共享了未经批准的层文件")
                installed_layer = installed_layers[number]
                require(installed_layer["path"] == texture_path and installed_layer["candidate_relative"] == layer["candidate_relative"],
                        key + "安装纹理映射与候选不同")
                source_layer = (RESOURCES / texture_path).read_bytes()
                require(digest(source_layer) == layer["candidate_sha256"] == installed_layer["sha256"], key + "分层SHA偏离批准")
                require(source_layer == candidate_layer.read_bytes(), key + "源码分层不是候选原字节")
                require(source_layer[:8] == b"\x89PNG\r\n\x1a\n" and struct.unpack(">II", source_layer[16:24]) == (16, 16),
                        key + "候选层不是16x16 PNG")
                texture_id = "hk3gtl:" + texture_path.removeprefix("assets/hk3gtl/textures/").removesuffix(".png")
                require(model["textures"][number] == texture_id, key + "模型引用不对应批准纹理层")
                if archive is not None:
                    require(archive.read(texture_path) == source_layer, key + "JAR分层不是源码原字节")
                if int(number.removeprefix("layer")) >= 2:
                    require(source_layer == gt.read(layer["archive_path"]), key + "覆盖层不是GT原色PNG原字节")
                    require(not layer["tinted"] and layer["raw_bytes_identical"], key + "覆盖层染色语义错误")
                expected_png.add(texture_path)
                layers.append({"layer": number, "path": texture_path, "sha256": digest(source_layer)})
            if key not in changed_ids:
                require(len(layers) == 1 and layers[0]["sha256"] == prior[key]["candidate_sha256"], key + "40单层项未保留旧PNG字节")
                require(digest(model_bytes) == model_history[key]["sha256"], key + "40单层项未保留旧模型字节")
            require(zh.get(item["translation_key"]) == item["name_zh"] and en.get(item["translation_key"]) == item["name_en"],
                    key + "双语显示不符")
            expected_models.add(model_path)
            items.append({"id": key, "model_sha256": digest(model_bytes), "parent": model["parent"], "layers": layers,
                          "translations_match": True, "old_single_layer_archived": key in changed_ids})
    require(len(expected_png) == 586 and len(expected_models) == 231, "批准资源白名单不是精确586层/231模型")
    source_png = {str(path.relative_to(RESOURCES)).replace("\\", "/") for path in (RESOURCES / "assets/hk3gtl/textures/item/main_material").rglob("*") if path.is_file()}
    require(source_png == expected_png, "正式主材纹理目录与批准586层白名单不同")
    material_keys = {row["material_key"] for row in candidates.values()}
    def belongs(path):
        return any(Path(path).stem.startswith(name + "_") for name in material_keys)
    source_models = {str(path.relative_to(RESOURCES)).replace("\\", "/") for path in (RESOURCES / "assets/hk3gtl/models/item").glob("*.json") if belongs(path)}
    require(source_models == expected_models, "正式主材模型目录与批准231模型白名单不同")
    if archive is not None:
        names = archive.namelist()
        require(len(names) == len(set(names)), "JAR包含重复资源路径")
        packed_png = {path for path in names if path.startswith("assets/hk3gtl/textures/item/main_material/") and not path.endswith("/")}
        packed_models = {path for path in names if path.startswith("assets/hk3gtl/models/item/") and path.endswith(".json") and belongs(path)}
        require(packed_png == expected_png and packed_models == expected_models, "JAR不是精确批准586层/231模型集合")
    return {"items": items, "material_count": 16, "texture_count": 586, "model_count": 231, "translated_item_count": 231,
            "approval_path": str(approval_path), "approval_sha256": digest(approval_path.read_bytes()),
            "candidate_manifest_sha256": V2_MANIFEST_SHA, "archived_old_single_count": 191, "unchanged_single_layer_count": 40,
            "checks": {"approved_v2_586_png_sha": True, "approved_231_models_sha": True, "valid_generated_models": True,
                       "both_languages_231": True, "approval_manifest_unchanged": True, "old_approval_history_unchanged": True,
                       "exact_586_layer_whitelist": True, "gt_original_overlay_bytes": True, "old_191_single_layers_archived": True,
                       "old_231_models_archived": True, "old_40_single_layer_bytes_unchanged": True}}


def approved_energy_carriers(archive=None):
    """只核验已批准的13项载体资源；不把燃料/乏料候选、配方或机器视为已批准。"""
    manifest_path = CARRIER_ARCHIVE / "13项载体采用与冻结清单.json"
    manifest_bytes = manifest_path.read_bytes()
    require(digest(manifest_bytes) == CARRIER_MANIFEST_SHA, "能源载体冻结批准清单被改写")
    manifest = json.loads(manifest_bytes)
    require(manifest["user_quote"] == "燃料，乏料(原图，候选)重画\n载体采用" and
            manifest["approval_scope"] == "13个carrier模型及其29层原候选贴图；后续接入这些原字节无需重复审批" and
            (manifest["item_count"], manifest["model_count"], manifest["texture_layer_count"]) == (13, 13, 29),
            "载体冻结批准范围或数量发生变化")
    source_zip = Path(manifest["source_zip"])
    require(source_zip.is_file() and digest(source_zip.read_bytes()) == CARRIER_SOURCE_ZIP_SHA == manifest["source_zip_sha256"],
            "载体原始批准ZIP丢失或哈希变化")
    frozen_root = CARRIER_ARCHIVE / "已采用资源"
    rows = manifest["items"]
    expected_ids = {"hk3gtl:" + key for key in CARRIER_NAMES_ZH}
    require(len(rows) == 13 and {row["id"] for row in rows} == expected_ids,
            "载体批准项不是精确13项")
    expected_models, expected_textures, verified = set(), set(), []
    registrations = (ROOT / "src/main/java/com/sirin/hk3gtl/common/registration/Hk3IndustrialContent.java").read_text(encoding="utf-8")
    zh = json.loads((RESOURCES / "assets/hk3gtl/lang/zh_cn.json").read_text(encoding="utf-8"))
    en = json.loads((RESOURCES / "assets/hk3gtl/lang/en_us.json").read_text(encoding="utf-8"))
    png_signature = b"\x89PNG\r\n\x1a\n"

    for row in rows:
        item_id = row["id"].split(":", 1)[1]
        require(row["form"] == "carrier" and row["name_zh"] == CARRIER_NAMES_ZH[item_id],
                item_id + "批准身份或中文名称不符")
        model_relative = row["model_relative"]
        require(model_relative == "已采用资源/assets/hk3gtl/models/item/" + item_id + ".json",
                item_id + "批准模型路径不符")
        model_path = frozen_root / PurePosixPath(model_relative.removeprefix("已采用资源/"))
        model_bytes = model_path.read_bytes()
        require(digest(model_bytes) == row["model_sha256"], item_id + "批准模型字节变化")
        model = json.loads(model_bytes)
        require(model.get("parent") == "minecraft:item/generated", item_id + "模型父项不符")
        model_resource = "assets/hk3gtl/models/item/" + item_id + ".json"
        expected_models.add(model_resource)
        formal_model = RESOURCES / model_resource
        require(formal_model.read_bytes() == model_bytes, item_id + "正式模型偏离批准原字节")
        if archive is not None:
            require(archive.read(model_resource) == model_bytes, item_id + "JAR模型偏离批准原字节")

        expected_layer_names = {}
        for layer in row["layers"]:
            layer_name = layer["layer"]
            approved_relative = layer["approved_relative"]
            require(approved_relative.startswith("已采用资源/assets/hk3gtl/textures/item/energy_fuel/" + item_id + "/") and
                    approved_relative.endswith("/" + layer_name + ".png"), item_id + "批准贴图路径不符")
            texture_path = frozen_root / PurePosixPath(approved_relative.removeprefix("已采用资源/"))
            texture_bytes = texture_path.read_bytes()
            require(digest(texture_bytes) == layer["candidate_sha256"], item_id + "/" + layer_name + "批准贴图字节变化")
            require(texture_bytes.startswith(png_signature) and len(texture_bytes) >= 24 and
                    struct.unpack(">II", texture_bytes[16:24]) == (16, 16), item_id + "/" + layer_name + "不是批准16×16 PNG")
            relative = "assets/hk3gtl/" + approved_relative.removeprefix("已采用资源/assets/hk3gtl/")
            require((RESOURCES / relative).read_bytes() == texture_bytes, relative + "正式贴图偏离批准原字节")
            if archive is not None:
                require(archive.read(relative) == texture_bytes, relative + "JAR贴图偏离批准原字节")
            expected_textures.add(relative)
            expected_layer_names[layer_name] = "hk3gtl:item/energy_fuel/" + item_id + "/" + layer_name
        require(model.get("textures") == expected_layer_names, item_id + "模型层与批准贴图映射不符")

        require(f'item("{item_id}", 64);' in registrations, item_id + "未在正式注册入口注册")
        translation_key = "item.hk3gtl." + item_id
        require(zh.get(translation_key) == row["name_zh"] and en.get(translation_key), item_id + "双语名称缺失")
        verified.append({"id": row["id"], "name_zh": row["name_zh"], "model": model_resource,
                         "texture_layers": len(row["layers"]), "registered": True, "translated": True})

    formal_models = {path.relative_to(RESOURCES).as_posix() for path in
                     (RESOURCES / "assets/hk3gtl/models/item").glob("*_carrier.json")
                     if path.stem in CARRIER_NAMES_ZH}
    require(formal_models == expected_models, "正式载体模型集合与批准13项不一致")
    if archive is not None:
        packed_models = {name for name in archive.namelist() if name.startswith("assets/hk3gtl/models/item/") and
                         name.endswith("_carrier.json") and PurePosixPath(name).stem in CARRIER_NAMES_ZH}
        packed_textures = {name for name in archive.namelist() if name.startswith("assets/hk3gtl/textures/item/energy_fuel/") and
                           name.endswith(".png") and
                           any("/" + item_id + "/" in name for item_id in CARRIER_NAMES_ZH)}
        require(packed_models == expected_models, "JAR载体模型集合与批准13项不一致")
        require(packed_textures == expected_textures, "JAR载体贴图集合与批准29层不一致")
    return {"energy_carriers": verified, "energy_carrier_items": 13, "energy_carrier_models": len(expected_models),
            "energy_carrier_texture_layers": len(expected_textures), "carrier_manifest_sha256": CARRIER_MANIFEST_SHA,
            "carrier_source_zip_sha256": CARRIER_SOURCE_ZIP_SHA,
            "checks": {"approved_carrier_scope_frozen": True, "approved_13_models_original_bytes": True,
                       "approved_29_texture_layers_original_bytes": True, "carrier_registration_and_bilingual_names": True,
                       "carrier_models_reference_approved_layers": True}}


def verify_source():
    result = {"revision": 165, "verified_at": datetime.now(timezone(timedelta(hours=8))).isoformat(),
              "status": "failed", "scope": "V2正式源码静态核验，不读取构建包，不等于已构建、部署或游戏通过"}
    try:
        result.update(approved_assets())
        result["status"] = "passed"
    except Exception as error:
        result["error"] = str(error)
    (LOG / "package-source-verification-v2.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "items"}, ensure_ascii=False, indent=2))
    return result["status"] == "passed"


def verify(expected_revision=165, output_dir=None):
    require(expected_revision in (165, 166, 171, 172, 174), "未定义该修订的完整包核验合同")
    output_dir = Path(output_dir) if output_dir is not None else (
        ROOT / "logs/energy-carriers-r174-20261020" if expected_revision == 174 else
        ROOT / "logs/voltage-architecture-r172" if expected_revision == 172 else LOG)
    output_dir.mkdir(parents=True, exist_ok=True)
    result = {"schema": 1, "revision": expected_revision, "verified_at": datetime.now(timezone(timedelta(hours=8))).isoformat(),
              "status": "failed", "source": str(SOURCE), "scope": "最终JAR只读静态核验，不等于启动或生存验收",
              "deployment_executed": False, "checks": {}, "items": [], "architecture": []}
    try:
        require(SOURCE.is_file(), "本轮构建包不存在")
        result.update(sha256=digest(SOURCE.read_bytes()), bytes=SOURCE.stat().st_size)
        build_log = output_dir / "build-final.log"
        build_text = build_log.read_text(encoding="utf-8", errors="replace")
        require("BUILD SUCCESSFUL" in build_text and "BUILD FAILED" not in build_text, "本轮完整构建没有成功证据")
        require("Task :clean" in build_text and "Task :check" in build_text and "Task :build" in build_text,
                "本轮日志未包含clean/check/build")
        result["build_log_sha256"] = digest(build_log.read_bytes())
        result["checks"]["complete_clean_check_build"] = True
        identity = json.loads((INSTANCE / "mrpack/modrinth.index.json").read_text(encoding="utf-8-sig"))
        expected_instance = "2.9" if expected_revision >= 171 else "2.8"
        require(identity["versionId"] == expected_instance, "实例版本与本轮核验合同不符")
        result["instance"] = str(INSTANCE)
        result["instance_version"] = identity["versionId"]
        with zipfile.ZipFile(SOURCE) as archive, zipfile.ZipFile(TARGET) as previous:
            require(archive.testzip() is None, "JAR CRC检查失败")
            names = set(archive.namelist())
            revision = json.loads(archive.read("assets/hk3gtl/changelog.json"))["entries"][0]["revision"]
            require(revision == expected_revision, f"构建内修订为{revision}，预期{expected_revision}，拒绝旧包")
            require(archive.read("assets/hk3gtl/changelog.json") == (RESOURCES / "assets/hk3gtl/changelog.json").read_bytes(),
                    "JAR变更记录不是当前源码原字节")
            result["checks"].update(jar_crc=True, expected_revision=True, current_changelog_bytes=True)
            zh = json.loads(archive.read("assets/hk3gtl/lang/zh_cn.json"))
            en = json.loads(archive.read("assets/hk3gtl/lang/en_us.json"))
            for language_name in ("zh_cn", "en_us"):
                relative = "assets/hk3gtl/lang/" + language_name + ".json"
                require(archive.read(relative) == (RESOURCES / relative).read_bytes(), relative + "不是当前源码")
            asset_result = approved_assets(archive)
            result["checks"].update(asset_result.pop("checks"))
            result.update(asset_result)
            if expected_revision >= 174:
                carrier_result = approved_energy_carriers(archive)
                result["checks"].update(carrier_result.pop("checks"))
                result.update(carrier_result)
            for name in REQUIRED_CLASSES:
                require("com/sirin/hk3gtl/" + name + ".class" in names, "缺少正式类：" + name)
            for name in RETIRED_CLASSES:
                require(not any(entry.startswith("com/sirin/hk3gtl/" + name + suffix) for entry in names for suffix in (".class", "$")),
                        "构建混入退役类：" + name)
            require(not any("Hk3Beta5" in name for name in names), "混入已否决的临时类命名")
            component_classes = sorted(name for name in names if "ComponentRecipes" in name and name.endswith(".class"))
            require(component_classes == ["com/sirin/hk3gtl/common/recipe/main/Hk3MainComponentRecipes.class"], "混入旧组件配方入口")
            mixins = json.loads(archive.read("hk3gtl.mixins.json"))
            source_mixins = json.loads((RESOURCES / "hk3gtl.mixins.json").read_text(encoding="utf-8"))
            comparison_mixins = dict(mixins)
            require(comparison_mixins.pop("refmap", None) == "hk3gtl-refmap.json", "Loom映射引用不是预期值")
            require(comparison_mixins == source_mixins, "除Loom映射引用外，Mixin配置与源码不同")
            require("hk3gtl-refmap.json" in names, "Loom映射引用对应文件未打包")
            json.loads(archive.read("hk3gtl-refmap.json"))
            if expected_revision >= 166:
                height_classes = (
                    "common/dimension/height/Hk3HeightConfig", "common/dimension/height/Hk3HeightWorldState",
                    "common/dimension/height/Hk3HeightBounds", "common/dimension/height/Hk3HeightPolicy",
                    "common/dimension/height/Hk3HeightService", "common/dimension/height/audit/Hk3HeightRuntimeAudit",
                    "client/Hk3HeightClientAudit", "client/Hk3HeightConfigScreen",
                )
                for name in height_classes:
                    require("com/sirin/hk3gtl/" + name + ".class" in names, "缺少高度正式类：" + name)
                height_mixins = ("height.Hk3DimensionTypeHeightAccessor", "height.Hk3PrimaryLevelHeightMixin", "height.Hk3MinecraftServerHeightMixin")
                for name in height_mixins:
                    require(name in mixins["mixins"], "高度Mixin未登记：" + name)
                    require("com/sirin/hk3gtl/mixin/" + name.replace(".", "/") + ".class" in names, "高度Mixin未打包：" + name)
                for language_name, language in (("zh_cn", zh), ("en_us", en)):
                    require(all(key in language for key in (
                        "hk3gtl.height.config.title", "hk3gtl.height.config.scope",
                    )), "高度界面语言缺失：" + language_name)
                result["checks"]["height_classes_mixins_and_languages"] = True
            if expected_revision >= 171:
                for name in (
                    "common/overview/Hk3MachineOverviewData", "common/overview/Hk3MachineOverviewService",
                    "common/overview/Hk3MachineOverviewAdapter", "client/phone/Hk3MachineOverviewPane",
                ):
                    require("com/sirin/hk3gtl/" + name + ".class" in names, "缺少机器总览正式类：" + name)
                overview_mixins = [name for name in source_mixins["mixins"] if "Overview" in name]
                require(len(overview_mixins) >= 2, "机器总览生命周期Mixin未登记")
                for name in overview_mixins:
                    require("com/sirin/hk3gtl/mixin/" + name.replace(".", "/") + ".class" in names,
                            "机器总览Mixin未打包：" + name)
                result["checks"]["overview_classes_and_lifecycle_mixins"] = True
            result["mixin_build_transformation"] = {"only_added_field": "refmap", "value": mixins["refmap"],
                                                     "refmap_sha256": digest(archive.read("hk3gtl-refmap.json")),
                                                     "remaining_configuration_matches_source": True}
            for mixin in POWER_MIXINS:
                require(mixin in mixins["mixins"], "功率Mixin未登记：" + mixin)
                require("com/sirin/hk3gtl/mixin/" + mixin.replace(".", "/") + ".class" in names,
                        "功率Mixin未打包：" + mixin)
            result["power_mixins"] = list(POWER_MIXINS)
            result["checks"].update(required_main_classes=True, retired_classes_absent=True, only_new_component_recipes=True,
                                    four_power_mixins_registered_and_packaged=True)
            if expected_revision >= 172:
                architecture_result = approved_voltage_architecture(archive)
                result["architecture"] = architecture_result.pop("architecture")
                result["checks"].update(architecture_result.pop("checks"))
                result["architecture_approval"] = architecture_result
            else:
                architecture_dir = RESOURCES / "data/hk3gtl/approved_architecture"
                source_architecture = sorted(architecture_dir.glob("*.json"))
                previous_names = {name for name in previous.namelist() if name.startswith("data/hk3gtl/approved_architecture/") and name.endswith(".json")}
                packed_architecture = {name for name in names if name.startswith("data/hk3gtl/approved_architecture/") and name.endswith(".json")}
                require(len(source_architecture) == 21 and previous_names == packed_architecture, "正式批准建筑集合被改变")
                for path in source_architecture:
                    relative = "data/hk3gtl/approved_architecture/" + path.name
                    data = archive.read(relative)
                    require(data == path.read_bytes() == previous.read(relative), relative + "偏离已安装正式建筑原字节")
                    result["architecture"].append({"path": relative, "sha256": digest(data), "matches_source_and_previous_install": True})
                result["checks"]["approved_21_architecture_original_bytes"] = True
            require(b"${mod_id}" not in archive.read("META-INF/mods.toml"), "模组元数据占位符未展开")
        sources = [ROOT / "src/main/java/com/sirin/hk3gtl" / (name + ".java") for name in REQUIRED_CLASSES]
        sources += [ROOT / "src/main/java/com/sirin/hk3gtl/mixin" / (name.replace(".", "/") + ".java") for name in POWER_MIXINS]
        result["source_snapshot"] = {str(path.relative_to(ROOT)).replace("\\", "/"): digest(path.read_bytes()) for path in sources}
        result.update(status="passed", material_count=16, texture_count=586, model_count=231, translated_item_count=231,
                      approved_architecture_count=21, installed_previous_sha256=digest(TARGET.read_bytes()))
    except Exception as error:
        result["error"] = str(error)
    (output_dir / "package-verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key not in ("items", "architecture", "source_snapshot")}, ensure_ascii=False, indent=2))
    return result["status"] == "passed"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="只读核验指定修订的正式构建包")
    parser.add_argument("--source-only", action="store_true")
    parser.add_argument("--expected-revision", type=int, choices=(165, 166, 171, 172, 174), default=165)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    require(not args.source_only or (args.expected_revision == 165 and args.output_dir is None), "源码模式保留原165冻结入口，不覆盖其他修订")
    raise SystemExit(0 if (verify_source() if args.source_only else verify(args.expected_revision, args.output_dir)) else 1)
