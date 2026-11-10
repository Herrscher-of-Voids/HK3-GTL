# -*- coding: utf-8 -*-
"""核对结构交付清单中的方块注册、模型父链和旧版依赖。

脚本只读指定 Prism 实例的 JAR 与 KubeJS 文本，不读取或修改存档，不判断机器
Pattern 是否成型。配方和科技门槛必须在游戏运行时另外核验。
"""

from __future__ import annotations

import hashlib
import html
import json
import re
import zipfile
from pathlib import Path
from typing import Any


PROJECT = Path(__file__).resolve().parents[2]
INSTANCE = Path(r"C:\Users\OWNER\AppData\Roaming\PrismLauncher\instances\GregTech-Leisure-1.4.5.2\minecraft")
MODS = INSTANCE / "mods"
DELIVERY = next(path for path in (PROJECT / "doc").rglob("manifest.json") if path.stat().st_size == 59368).parent
SCHEMATICS = INSTANCE / "config" / "worldedit" / "schematics"

JARS = {
    "gtceu": MODS / "gtceu-1.20.1-1.4.4.jar",
    "gtlcore": MODS / "gtlcore-1.2.3.2-fix2.jar",
}


def read_json(zf: zipfile.ZipFile, name: str) -> Any:
    return json.loads(zf.read(name).decode("utf-8"))


def model_chain(zf: zipfile.ZipFile, namespace: str, model: str) -> tuple[list[str], bool]:
    """解析模型父链，并只把明确的完整立方体父模型标为完整。"""

    current_ns, current_path = (model.split(":", 1) if ":" in model else (namespace, model))
    visited: set[tuple[str, str]] = set()
    parents: list[str] = []
    full = False
    while (current_ns, current_path) not in visited:
        visited.add((current_ns, current_path))
        resource = f"assets/{current_ns}/models/{current_path}.json"
        if resource not in zf.namelist():
            break
        data = read_json(zf, resource)
        parent = str(data.get("parent", ""))
        parents.append(parent or f"{current_ns}:{current_path}")
        if any(token in parent for token in ("cube_all", "cube/tinted", "cube_2_layer")):
            full = True
        for element in data.get("elements", []) if isinstance(data.get("elements"), list) else []:
            if element.get("from") == [0, 0, 0] and element.get("to") == [16, 16, 16]:
                full = True
        if not parent:
            break
        current_ns, current_path = (parent.split(":", 1) if ":" in parent else (current_ns, parent))
    return parents, full


def block_evidence(block_id: str) -> dict[str, Any]:
    namespace, block = block_id.split(":", 1)
    jar = JARS.get(namespace)
    if jar is None or not jar.is_file():
        return {"id": block_id, "status": "缺少对应模组 JAR", "registered": False}
    with zipfile.ZipFile(jar) as zf:
        blockstate_name = f"assets/{namespace}/blockstates/{block}.json"
        if blockstate_name not in zf.namelist():
            return {"id": block_id, "status": "JAR 中没有对应 blockstates", "registered": False}
        blockstate = read_json(zf, blockstate_name)
        models: set[str] = set()

        def visit(value: Any) -> None:
            if isinstance(value, dict):
                if isinstance(value.get("model"), str):
                    models.add(value["model"])
                for nested in value.values():
                    visit(nested)
            elif isinstance(value, list):
                for nested in value:
                    visit(nested)

        visit(blockstate)
        chains: dict[str, list[str]] = {}
        full = True
        for model in sorted(models):
            chain, is_full = model_chain(zf, namespace, model)
            chains[model] = chain
            full &= is_full
        return {
            "id": block_id,
            "jar": jar.name,
            "jar_sha256": hashlib.sha256(jar.read_bytes()).hexdigest(),
            "registered": True,
            "blockstate": blockstate_name,
            "models": sorted(models),
            "model_parents": chains,
            "complete_cube_model": full,
            "status": "注册与完整模型父链已核对；碰撞箱和阶段配方仍待运行时核验" if full else "模型父链无法确认完整立方体",
        }


def static_recipe_mentions(block_id: str) -> list[str]:
    """记录 KubeJS 静态文本中的出现位置，不把它当作最终配方证明。"""

    result: list[str] = []
    for path in sorted((INSTANCE / "kubejs").rglob("*")):
        if not path.is_file() or path.suffix not in {".js", ".json", ".json5"}:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if block_id in text:
            result.append(str(path.relative_to(INSTANCE)))
    return result


def main() -> None:
    manifest = json.loads((DELIVERY / "manifest.json").read_text(encoding="utf-8"))
    ids = sorted(
        {
            material["id"]
            for item in manifest
            for material in item["materials"]
            if not material["id"].startswith("minecraft:")
        }
    )
    evidence = []
    for block_id in ids:
        row = block_evidence(block_id)
        row["static_kubejs_mentions"] = static_recipe_mentions(block_id)
        evidence.append(row)
    forbidden = [row["id"] for row in evidence if row.get("id", "").startswith("hk3gtl:")]
    incomplete = [row["id"] for row in evidence if not row.get("complete_cube_model", False)]
    missing = [row["id"] for row in evidence if not row.get("registered", False)]
    report = {
        "generated_at": "2026-09-24",
        "instance": str(INSTANCE),
        "structures": [item["file"] for item in manifest],
        "materials": evidence,
        "forbidden_legacy_ids": forbidden,
        "missing_registration": missing,
        "incomplete_cube_models": incomplete,
        "runtime_recipe_verification": "未执行；静态文本出现位置不等于最终运行时配方或阶段可达性",
    }
    (DELIVERY / "材料基线_v1.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    rows = []
    for row in evidence:
        rows.append(
            "<tr>"
            f"<td><code>{html.escape(row['id'])}</code></td>"
            f"<td>{html.escape(row.get('jar', ''))}</td>"
            f"<td>{'通过' if row.get('registered') else '缺失'}</td>"
            f"<td>{'通过' if row.get('complete_cube_model') else '待核验'}</td>"
            f"<td>{len(row.get('static_kubejs_mentions', []))}</td>"
            f"<td>{html.escape(row.get('status', ''))}</td>"
            "</tr>"
        )
    page = f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><title>内测5结构材料基线 v1</title>
<style>body{{max-width:1500px;margin:auto;padding:24px;background:#0b1020;color:#edf3ff;font:15px/1.7 system-ui,\"Microsoft YaHei\",sans-serif}}h1,h2{{color:#78e7de}}section{{background:#141e32;border:1px solid #405270;border-radius:10px;padding:16px;margin:16px 0}}table{{border-collapse:collapse;width:100%;font-size:13px}}th,td{{border-bottom:1px solid #405270;padding:8px;text-align:left;vertical-align:top}}th{{color:#78e7de;background:#182943}}code{{color:#ffd392}}.warn{{border-left:4px solid #ff9f7a;padding-left:12px}}</style></head>
<body><h1>内测5结构材料基线 v1</h1>
<p>目标实例：<code>{html.escape(str(INSTANCE))}</code></p>
<section class="warn"><h2>核验边界</h2><p>本页只证明当前实例 JAR 中存在对应注册资源，并根据 blockstates 与模型父链判断完整方块。碰撞箱、最终配方、科技门槛和运行时成型仍需游戏内核验。</p></section>
<section><table><thead><tr><th>方块 ID</th><th>来源 JAR</th><th>注册</th><th>完整模型</th><th>KubeJS 静态出现次数</th><th>状态</th></tr></thead><tbody>{''.join(rows)}</tbody></table></section>
<section><p>旧版 ID：{html.escape(', '.join(forbidden) or '无')}；缺少注册：{html.escape(', '.join(missing) or '无')}；无法确认完整模型：{html.escape(', '.join(incomplete) or '无')}。</p><p>下一步必须在指定实例新建存档，先验证粘贴，再迁移 Pattern。</p></section>
</body></html>"""
    (DELIVERY / "材料基线_v1.html").write_text(page, encoding="utf-8")
    print(f"已核对材料 {len(evidence)} 种；旧版引用 {len(forbidden)}，缺少注册 {len(missing)}，模型待核验 {len(incomplete)}")


if __name__ == "__main__":
    main()
