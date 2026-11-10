#!/usr/bin/env python3
"""校验配方标题与控制器提示的语言资源；失败时返回非零退出码。

变更记录 #1 · 2026-09-24 14:31:12 · 内测5修订65：
删除仅检查旧配方类型文件、缺键仍成功退出的行为；新增内测5类型扫描、
双语言重复键及自动/手动提示冲突检查。使用GT注册的实际命名空间校验，
防止遗漏Hk3IndustrialRecipeTypes或把hk3gtl翻译键误当成gtceu标题。
本检查不启动游戏，不验证配方可达性或机器成型。

变更记录 #2 · 2026-10-17 14:24:38 · 内测5修订161：
新增动态工业工艺角色展开、端口允许范围与计划角色交叉检查；静态注册必须是
完整字符串参数，不能把 industrial_process_ 拼接前缀误认为完整类型。
缺少标题、内部编号充当标题或动态注册语法变化时检查失败，不声称实机验收。
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def unique_object(pairs):
    """拒绝JSON重复键，避免后一个翻译静默覆盖前一个。"""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"重复语言键：{key}")
        result[key] = value
    return result


def registered_recipe_ids(recipe_root):
    """从真实注册源码展开标题键；动态语法改变时明确失败，防止静默漏扫。"""
    ids = set()
    for source in recipe_root.glob("*RecipeTypes*.java"):
        text = source.read_text(encoding="utf-8")
        # 完整字面量后必须紧接参数分隔/结束，排除字符串拼接的部分前缀。
        ids.update(re.findall(r'GTRecipeTypes\.register\(\s*"([^"]+)"\s*[,)]', text))
        ids.update(re.findall(r'\breg\(\s*"([^"]+)"\s*[,)]', text))

    process_source = (recipe_root / "Hk3ResearchProcessTypes.java").read_text(encoding="utf-8")
    initial = re.search(
        r'List<String>\s+roles\s*=\s*new\s+ArrayList<>\(\s*List\.of\((.*?)\)\s*\)\s*;',
        process_source, re.DOTALL)
    ranges = re.findall(
        r'for\s*\(\s*int\s+(\w+)\s*=\s*(\d+)\s*;\s*\1\s*<=\s*(\d+)\s*;'
        r'\s*\1\+\+\s*\)\s*if\s*\(\s*\1\s*!=\s*(\d+)\s*\)\s*roles\.add\('
        r'\s*String\.format\(\s*Locale\.ROOT\s*,\s*"([^"]+)"\s*,\s*\1\s*\)\s*\)\s*;',
        process_source)
    prefix = re.findall(
        r'GTRecipeTypes\.register\(\s*"([^"]+)"\s*\+\s*role\.toLowerCase\('
        r'\s*Locale\.ROOT\s*\)\.replace\(\s*\'-\'\s*,\s*\'_\'\s*\)\s*,',
        process_source)
    if (initial is None or len(prefix) != 1 or not ranges
            or len(re.findall(r'\broles\.add\(', process_source)) != len(ranges)
            or re.search(r'\broles\.addAll\(', process_source)):
        raise ValueError("无法完整展开动态工艺注册，请同步更新检查器的源码解析规则。")
    roles = re.findall(r'"([^"]+)"', initial.group(1))
    for _, start, end, excluded, pattern in ranges:
        roles.extend(pattern % i for i in range(int(start), int(end) + 1) if i != int(excluded))
    if len(roles) != len(set(roles)) or any(not re.fullmatch(r'I\d{2}(?:-[234])?', r) for r in roles):
        raise ValueError("动态工业角色重复或格式无效。")

    ports_source = (recipe_root / "Hk3ResearchProcessPorts.java").read_text(encoding="utf-8")
    allowed = re.search(r'role\.matches\(\s*"([^"]+)"\s*\)', ports_source)
    special_ports = set(re.findall(r'case\s+"([^"]+)"\s*->', ports_source))
    if allowed is None or any(r not in special_ports and not re.fullmatch(allowed.group(1), r) for r in roles):
        raise ValueError("动态角色未包含在实际端口规则中。")
    aliases = set(re.findall(r'map\.put\(\s*"([^"]+)"\s*,', process_source))
    plans_path = ROOT / "src/main/resources/data/hk3gtl/research/industrial_processes.json"
    plans = json.loads(plans_path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    unknown = {p["role"] for p in plans["recipes"]} - set(roles) - aliases
    if unknown:
        raise ValueError(f"工艺计划角色未注册：{sorted(unknown)}")
    dynamic = {prefix[0] + role.lower().replace("-", "_") for role in roles}
    if ids & dynamic:
        raise ValueError("动态类型与静态类型重复。")
    return ids | dynamic, len(ids), len(dynamic)


def is_internal_title(value, key, recipe_id):
    """有文字职责名才是标题；内部ID或纯角色编号不能掩盖缺少翻译。"""
    if not isinstance(value, str) or not value.strip():
        return True
    plain = re.sub(r'\u00a7.', '', value).strip()
    return (plain in (key, recipe_id) or plain.startswith("gtceu.")
            or re.fullmatch(r'(?:I\d{2}(?:[_-][1-4])?|[\d\s._-]+)', plain, re.IGNORECASE) is not None
            or re.fullmatch(r'industrial_process_[a-z\d_]+', plain, re.IGNORECASE) is not None)


def main():
    recipe_root = ROOT / "src/main/java/com/sirin/hk3gtl/common/recipe"
    ids, static_count, dynamic_count = registered_recipe_ids(recipe_root)
    if not ids or "industrial_honkai_collection" not in ids:
        raise ValueError("未扫描到内测5配方类型，请检查源码路径。")

    failures = []
    catalogs = {}
    for locale in ("zh_cn", "en_us"):
        path = ROOT / f"src/main/resources/assets/hk3gtl/lang/{locale}.json"
        data = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
        catalogs[locale] = data
        for recipe_id in sorted(ids):
            key = f"gtceu.{recipe_id}"
            value = data.get(key)
            if is_internal_title(value, key, recipe_id):
                failures.append(f"{locale} 配方标题缺失或仍为内部标识符：{key}")
        for key, value in data.items():
            if not isinstance(value, str) or "\ufffd" in value:
                failures.append(f"{locale} 翻译值无效或包含替换字符：{key}")
            if key.startswith("hk3gtl.machine.") and key.endswith(".tooltip") and key + ".0" in data:
                failures.append(f"{locale} 控制器同时定义自动提示与编号提示：{key}")
        print(f"{locale}：已检查 {len(data)} 个语言键、{len(ids)} 个配方类型"
              f"（静态 {static_count}、动态工业角色 {dynamic_count}）。")
    if catalogs["zh_cn"].keys() != catalogs["en_us"].keys():
        failures.append("中英文语言键集合不一致。")
    for failure in failures:
        print(failure)
    print(f"检查结果：{len(failures)} 项错误。")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
