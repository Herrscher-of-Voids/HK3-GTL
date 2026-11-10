# -*- coding: utf-8 -*-
"""生成内测5多方块结构的材料与依赖审计报告。

本脚本只读取指定整合包、项目结构预览和 KubeJS 脚本，不修改模组、存档或配方。
审计结果故意区分“已确认”和“待运行时核验”，避免把模型名称当成完整碰撞箱或把脚本
中的静态配方当成最终运行时配方。所有注释使用中文，脚本和报告均以 UTF-8 写入。
"""

from __future__ import annotations

import html
import json
import re
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


INSTANCE = Path(r"C:\Users\OWNER\AppData\Roaming\PrismLauncher\instances\GregTech-Leisure-1.4.5.2\minecraft")
PROJECT = Path(__file__).resolve().parents[2]
MODS = INSTANCE / "mods"
KUBEJS = INSTANCE / "kubejs"


def find_industrial_docs() -> Path:
    """通过 ASCII 前缀寻找内测5文档目录，避免脚本源文件路径编码影响读取。"""
    for path in (PROJECT / "doc").iterdir():
        if path.is_dir() and path.name.startswith("HK3GTL-") and "格式迁移" not in path.name:
            return path
    raise FileNotFoundError("找不到 HK3GTL-内测5 文档目录")


BETA5 = find_industrial_docs()
STRUCTURE_DIR = BETA5 / "03_机器结构"
REPORT_DIR = STRUCTURE_DIR


def read_json(data: bytes) -> Any | None:
    try:
        return json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None


def parent_chain(zf: zipfile.ZipFile, namespace: str, model_path: str) -> tuple[list[str], bool]:
    """解析模型父链，并判断是否能从元素范围确认完整立方体。"""
    chain: list[str] = []
    visited: set[str] = set()
    full_cube = False
    current = f"{namespace}:{model_path}"
    while current and current not in visited:
        visited.add(current)
        ns, rel = current.split(":", 1) if ":" in current else (namespace, current)
        resource = f"assets/{ns}/models/{rel}.json"
        if resource not in zf.namelist():
            break
        model = read_json(zf.read(resource))
        if not isinstance(model, dict):
            break
        parent = str(model.get("parent", ""))
        chain.append(parent or f"{ns}:{rel}")
        elements = model.get("elements")
        if isinstance(elements, list):
            for element in elements:
                if not isinstance(element, dict):
                    continue
                if element.get("from") == [0, 0, 0] and element.get("to") == [16, 16, 16]:
                    full_cube = True
        if not parent:
            break
        if ":" not in parent:
            current = f"{ns}:{parent}"
        else:
            current = parent
    # 常见父模型是完整立方体，但仍把“可推断”与运行时碰撞核验分开。
    if any(x.endswith("/cube_all") or x in {"block/cube_all", "minecraft:block/cube_all", "block/block"} for x in chain):
        full_cube = True
    return chain, full_cube


def jar_block_rows() -> list[dict[str, Any]]:
    """读取 GTCEu、GTLCore、GTLAdditions 与 GTLsupb 的静态方块资源。"""
    wanted = {
        "gtceu": "gtceu-1.20.1-1.4.4.jar",
        "gtlcore": "gtlcore-1.2.3.2-fix2.jar",
        "gtladditions": "gtladditions-3.3.jar",
        "gtlsupb": "GTLsupb-3.5.jar",
    }
    rows: list[dict[str, Any]] = []
    for namespace, filename in wanted.items():
        jar = MODS / filename
        if not jar.is_file():
            rows.append({"id": f"{namespace}:*", "source": filename, "status": "缺失"})
            continue
        with zipfile.ZipFile(jar) as zf:
            names = set(zf.namelist())
            for resource in sorted(names):
                match = re.fullmatch(r"assets/([^/]+)/blockstates/([^/]+)\.json", resource)
                if not match:
                    continue
                ns, block_id = match.groups()
                if ns != namespace:
                    continue
                state = read_json(zf.read(resource))
                if not isinstance(state, dict):
                    continue
                models: set[str] = set()

                def visit(value: Any) -> None:
                    if isinstance(value, dict):
                        model = value.get("model")
                        if isinstance(model, str):
                            models.add(model)
                        for nested in value.values():
                            visit(nested)
                    elif isinstance(value, list):
                        for nested in value:
                            visit(nested)

                visit(state)
                chains: list[str] = []
                full = False
                for model in sorted(models):
                    model_ns, model_path = model.split(":", 1) if ":" in model else (namespace, model)
                    chain, is_full = parent_chain(zf, model_ns, model_path)
                    chains.extend(chain)
                    full |= is_full
                rows.append({
                    "id": f"{namespace}:{block_id}",
                    "source": filename,
                    "models": sorted(models),
                    "parents": sorted(set(chains)),
                    "full_model": full,
                    "status": "模型可推断完整立方体，仍需运行时碰撞核验" if full else "模型不足以确认完整立方体",
                })
    return rows


def kubejs_block_rows() -> list[dict[str, Any]]:
    """读取 KubeJS 启动脚本中的方块声明，排除明确的非完整方块类型。"""
    source = KUBEJS / "startup_scripts" / "block.js"
    if not source.is_file():
        return []
    text = source.read_text(encoding="utf-8", errors="replace")
    rows: list[dict[str, Any]] = []
    for match in re.finditer(r'event\.create\("([^"]+)"(?:,\s*"([^"]+)")?', text):
        block_id, kind = match.groups()
        if block_id in {"gelid_cryotheum"}:
            continue
        non_full = kind in {"stairs", "slab", "fence", "fence_gate", "pressure_plate", "button"}
        rows.append({
            "id": f"kubejs:{block_id}",
            "source": "kubejs/startup_scripts/block.js",
            "kind": kind or "basic",
            "full_model": not non_full,
            "status": "禁止：脚本声明为非完整方块" if non_full else "basic 声明；需运行时碰撞核验",
        })
    return rows


def recipe_evidence(ids: list[str]) -> dict[str, list[dict[str, Any]]]:
    """收集脚本中直接出现的输出/输入证据，不把它标记为最终配方确认。"""
    evidence: dict[str, list[dict[str, Any]]] = defaultdict(list)
    files = sorted(KUBEJS.rglob("*.js"))
    for path in files:
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for line_no, line in enumerate(lines, 1):
            for block_id in ids:
                if block_id in line:
                    evidence[block_id].append({"file": str(path.relative_to(INSTANCE)), "line": line_no, "text": line.strip()[:240]})
    return dict(evidence)


def load_old_palettes() -> list[dict[str, Any]]:
    """读取现有预览 NBT 的调色板，作为旧资产违规提示，不作为新结构基线。"""
    try:
        import nbtlib
    except ImportError:
        return []
    rows: list[dict[str, Any]] = []
    for path in sorted(STRUCTURE_DIR.rglob("*.nbt")):
        try:
            root = nbtlib.load(path)
        except Exception:
            continue
        palette = root.get("palette", [])
        ids = [str(entry.get("Name")) for entry in palette if hasattr(entry, "get")]
        old = [block for block in ids if block.startswith("hk3gtl:")]
        forbidden = [block for block in ids if block in {
            "minecraft:iron_bars", "minecraft:quartz_stairs", "minecraft:smooth_quartz_slab",
            "minecraft:magma_block", "minecraft:crying_obsidian", "minecraft:light_blue_stained_glass",
            "minecraft:cyan_stained_glass", "minecraft:purpur_block", "minecraft:sea_lantern",
        }]
        if old or forbidden:
            rows.append({"file": str(path.relative_to(PROJECT)), "palette": ids, "old_hk3gtl": old, "forbidden_shapes_or_legacy": forbidden})
    return rows


def load_legacy_references() -> dict[str, Any]:
    """扫描项目 Pattern 和 HK3GTL 包中的旧注册引用，供迁移清单使用。"""
    references: list[dict[str, Any]] = []
    pattern_root = PROJECT / "src" / "main" / "java" / "com" / "sirin" / "hk3gtl" / "common" / "multiblock"
    if pattern_root.is_dir():
        for path in sorted(pattern_root.rglob("*.java")):
            try:
                lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
            except OSError:
                continue
            for line_no, line in enumerate(lines, 1):
                if "hk3gtl:" in line:
                    references.append({"file": str(path.relative_to(PROJECT)), "line": line_no, "text": line.strip()[:240]})
    jar_ids: list[str] = []
    hk3jar = MODS / "hk3gtl-0.5.0.jar"
    if hk3jar.is_file():
        with zipfile.ZipFile(hk3jar) as zf:
            for resource in zf.namelist():
                match = re.fullmatch(r"assets/hk3gtl/blockstates/([^/]+)\.json", resource)
                if match:
                    jar_ids.append(f"hk3gtl:{match.group(1)}")
    return {"pattern_references": references, "jar_blockstates": sorted(jar_ids)}


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def make_report() -> None:
    jar_rows = jar_block_rows()
    kube_rows = kubejs_block_rows()
    all_rows = jar_rows + kube_rows
    candidates = [row for row in all_rows if row.get("full_model") and not row["id"].startswith("hk3gtl:")]
    evidence = recipe_evidence([row["id"] for row in candidates])
    old_palettes = load_old_palettes()
    legacy = load_legacy_references()
    report = {
        "generated_at": "2026-09-24",
        "instance": str(INSTANCE),
        "jar_blocks": jar_rows,
        "kubejs_blocks": kube_rows,
        "candidate_count": len(candidates),
        "recipe_evidence": evidence,
        "old_preview_violations": old_palettes,
        "legacy_references": legacy,
        "hard_rules": [
            "禁止使用旧版 HK3GTL 海渊方块、物品和其他旧注册内容",
            "只允许完整 1×1×1 方块；钻石块为核心标记，普通钻石矿为接口占位",
            "每次实机测试必须创建全新存档，且只能使用指定 Prism 实例",
            "结构文件与 Pattern/机器功能分开验收；静态模型不能替代运行时碰撞核验",
        ],
    }
    (REPORT_DIR / "材料审核数据_v1.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    source_counts = Counter(row["source"] for row in all_rows)
    rows_html = []
    for row in all_rows:
        status = row.get("status", "")
        if row["id"].startswith("hk3gtl:"):
            status = "禁止：旧版 HK3GTL 注册内容"
        rows_html.append(
            "<tr>"
            f"<td><code>{esc(row['id'])}</code></td>"
            f"<td>{esc(row.get('source', ''))}</td>"
            f"<td>{esc(row.get('kind', 'JAR 静态资源'))}</td>"
            f"<td>{esc(row.get('parents', row.get('models', '')))}</td>"
            f"<td>{esc(status)}</td>"
            "</tr>"
        )
    violations_html = []
    for item in old_palettes:
        violations_html.append(
            f"<li><code>{esc(item['file'])}</code>：旧注册 {esc(', '.join(item['old_hk3gtl']) or '无')}；"
            f"禁止形体/旧预览 {esc(', '.join(item['forbidden_shapes_or_legacy']) or '无')}。</li>"
        )
    recipe_html = []
    for block_id, refs in sorted(evidence.items()):
        locations = "; ".join(f"{item['file']}:{item['line']}" for item in refs[:5])
        recipe_html.append(f"<tr><td><code>{esc(block_id)}</code></td><td>{len(refs)}</td><td>{esc(locations)}</td></tr>")
    legacy_html = []
    for item in legacy["pattern_references"]:
        legacy_html.append(f"<li><code>{esc(item['file'])}:{item['line']}</code>：{esc(item['text'])}</li>")
    html_text = f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><title>内测5多方块材料与依赖审核 v1</title>
<style>body{{font-family:system-ui,'Microsoft YaHei',sans-serif;background:#0b1020;color:#edf3ff;line-height:1.65;margin:0 auto;max-width:1500px;padding:24px}}h1,h2{{color:#78e7de}}section{{background:#141e32;border:1px solid #405270;border-radius:10px;padding:16px;margin:16px 0}}code{{color:#ffd392}}table{{border-collapse:collapse;width:100%;font-size:13px}}th,td{{border-bottom:1px solid #405270;padding:7px;text-align:left;vertical-align:top}}th{{color:#78e7de;position:sticky;top:0;background:#182943}}.warn{{border-left:4px solid #ff9f7a;padding-left:12px}}.ok{{border-left:4px solid #78e7de;padding-left:12px}}</style></head><body>
<h1>内测5多方块材料与依赖审核 v1</h1>
<p>生成日期：2026-09-24。此页是只读审计结果，不是结构成型或配方可运行证明。</p>
<section class="warn"><h2>本轮硬边界</h2><ul>{''.join(f'<li>{esc(x)}</li>' for x in report['hard_rules'])}</ul></section>
<section><h2>调查范围与结论</h2><p>目标实例：<code>{esc(INSTANCE)}</code></p><p>读取 GTCEu、GTLCore、GTLAdditions、GTLsupb 的静态方块资源以及指定实例的 KubeJS 启动/服务脚本。资源行数：{len(all_rows)}；模型或脚本可初步视为完整方块的候选：{len(candidates)}。JAR 模型的完整立方体判断仍需游戏内碰撞箱核验；KubeJS <code>basic</code> 只代表注册类型，不代表已经通过实机验收。</p><p>来源计数：{esc(dict(source_counts))}</p></section>
<section><h2>旧预览违规提示</h2><p>现有预览资产只作为清理线索，不能直接迁移为新结构。</p><ul>{''.join(violations_html) or '<li>未读取到明显违规调色板。</li>'}</ul></section>
<section><h2>旧版 HK3GTL 依赖引用</h2><p>以下引用必须在新结构迁移前清理或转入归档；本报告不自动改写 Pattern。</p><p>目标实例 HK3GTL JAR 中静态 blockstates：{esc(', '.join(legacy['jar_blockstates']) or '未发现')}</p><ul>{''.join(legacy_html) or '<li>多方块源码中未发现 hk3gtl: 引用。</li>'}</ul></section>
<section><h2>候选材料与形体证据</h2><div style="max-height:680px;overflow:auto"><table><thead><tr><th>方块 ID</th><th>来源</th><th>声明类型</th><th>模型/父链</th><th>状态</th></tr></thead><tbody>{''.join(rows_html)}</tbody></table></div></section>
<section><h2>KubeJS 配方出现位置（非最终配方证明）</h2><p>以下仅记录脚本中出现的行；动态加载、移除、覆盖和研究门槛仍需运行时导出核对。</p><table><thead><tr><th>方块 ID</th><th>出现次数</th><th>最多列出五处位置</th></tr></thead><tbody>{''.join(recipe_html) or '<tr><td colspan="3">没有静态脚本证据</td></tr>'}</tbody></table></section>
<section><h2>未决事项</h2><ol><li>为 16 个电压等级逐级选定材料，补齐每种材料的真实配方、研究/维度前置和最早可达阶段。</li><li>重新设计并导出 16 个独立 Sponge Schematic v2；每个结构必须包含钻石块核心和钻石矿接口占位，且不含旧版 HK3GTL 方块。</li><li>确认 I01、I02 保留几何的重新材料映射，并单独核对 Pattern 端口能力；结构文件验收不能代替机器成型验收。</li><li>每次实机测试新建空存档，核对实例不是 “Infinity Legacy II”，并分别记录结构解析、粘贴、成型和运行结果。</li></ol></section>
<footer>本报告由 tools/structure_audit/material_audit.py 生成；脚本只读，不修改模组、配方或存档。</footer>
</body></html>"""
    (REPORT_DIR / "多方块材料与依赖审核_v1.html").write_text(html_text, encoding="utf-8")


if __name__ == "__main__":
    make_report()
    print("已生成多方块材料与依赖审核报告")

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
