# -*- coding: utf-8 -*-
"""按现行电压映射核验 I01–I25 的四项建筑规模递增指标。"""

from collections import Counter
from datetime import datetime, timezone, timedelta
from hashlib import sha256
from html import unescape
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "logs/i01-i25-voltage-progression-20261025"
ARCHIVE = "deliveries/多方块确认归档"
CONFIRMED = f"{ARCHIVE}/20261023_133546_133059_I01-I18_主控居中融合V2_已确认"
MAPPING = "doc/HK3GTL-内测5/02_工业计划/多方块结构电压映射提案_v1.html"
DELIVERIES = {
    19: "I19_小型崩坏能反应堆_单塔蓝湾独立候选_V3_20261023",
    20: "I20_中型崩坏能反应堆_检修厂房与外围路修订_V3_20261023",
    21: "I21_大型崩坏能反应堆_闭式三回路联合厂区候选_V1_20261023",
    22: "I22_究极崩坏能反应堆_四堆隔离外场候选_V1_20261023",
    23: "I23_崩坏能相变释能机_双瓣相界锻炉_V8_20261024",
    24: "I24_量子异常观测阵列_三碟长基线天文庭院_V2_20261025",
    25: "I25_世界泡坐标解析中心_量子天球研究院_重制首版_20261025",
}
RECEIPTS = {
    22: "20261024_010011_626135_batch-07_01of05_I22_WSV_已确认",
    23: "20261025_001407_313968_batch-07_02of05_I23_V8_QCV_已确认",
    24: "20261025_004459_948658_batch-07_03of05_I24_V2_QEV_已确认",
}
VOLTAGES = "MAX HBV HCV HRV HDV QSV QCV QEV QAV IMV ICV IRV IWV WFV WSV CIV CEV".split()
TIERS = {name: 14 + i for i, name in enumerate(VOLTAGES)}
METRICS = {
    "blocks": "实际方块数", "materials": "唯一材料数",
    "volume": "实际包围盒体积", "height": "实际高度",
}
SOURCES = {}


def read(path, kind):
    raw = (ROOT / path).read_bytes()
    SOURCES[path] = {"path": path, "kind": kind, "sha256": sha256(raw).hexdigest()}
    return json.loads(raw.decode("utf-8-sig"))


def voltage_mapping():
    raw = (ROOT / MAPPING).read_bytes()
    SOURCES[MAPPING] = {"path": MAPPING, "kind": "负责人指定的结构制作电压映射提案", "sha256": sha256(raw).hexdigest()}
    result = {}
    for row in re.findall(r"<tr\b[^>]*>(.*?)</tr>", raw.decode("utf-8-sig"), re.S | re.I):
        cells = re.findall(r"<td\b[^>]*>(.*?)</td>", row, re.S | re.I)
        if len(cells) < 3:
            continue
        first = unescape(re.sub(r"<[^>]+>", " ", cells[0])).strip().split()
        if first and first[0] in TIERS:
            for key in re.findall(r"\bI\d{2}(?:-[1-4])?\b", cells[2]):
                assert key not in result, f"映射表重复：{key}"
                result[key] = first[0]
    assert result["I01-4"] == "IWV" and result["I25"] == "QEV"
    assert TIERS["MAX"] == 14 and TIERS["HBV"] == 15
    return result


def approval_old(receipt, index_entry):
    return {
        "state": "approved", "label": "已确认归档／已接入，游戏未验收",
        "evidence_kind": "独立确认清单与当前归档索引；覆盖候选文件保留的待审字段",
        "quote": receipt["approval_quote"], "scope": receipt["approval_scope"],
        "path": f"{CONFIRMED}/确认与校验清单.json",
        "index_status": index_entry["status"], "game_verified": index_entry.get("game_verified", False),
    }


def record(key, title, declared, actual, count, palette, paths, approval, mapping, evidence, source_status):
    palette = {state: int(n) for state, n in palette.items() if n > 0}
    assert not any(s.split("[")[0] in {"minecraft:air", "minecraft:cave_air", "minecraft:void_air"} for s in palette)
    assert sum(palette.values()) == count, f"{key} 调色板用量与方块总数不符"
    assert len(actual) == 3 and all(0 < n <= d for n, d in zip(actual, declared))
    # 不把朝向等状态差异计成额外材料；现有样本材料状态与方块种类数量一致。
    materials = len({s.split("[")[0] for s in palette})
    code = mapping[key]
    return {
        "id": key, "family": key.split("-")[0], "title": title,
        "voltage": code, "tier": TIERS[code],
        "voltage_label": "MAX / tier14" if code == "MAX" else f"{code} / V{TIERS[code]-14:02d} / tier{TIERS[code]}",
        "declared_xyz": declared, "actual_xyz": actual,
        "size_wdh": [actual[0], actual[2], actual[1]],
        "dimensions_differ": declared != actual,
        "metrics": {"blocks": count, "materials": materials, "volume": actual[0]*actual[1]*actual[2], "height": actual[1]},
        "palette": palette, "material_state_count": len(palette),
        "sources": paths, "measurement_evidence": evidence,
        "approval": approval, "source_candidate_metadata": source_status,
    }


def load_forms(mapping):
    manifest_path = f"{CONFIRMED}/confirmed_v2/manifest.json"
    manifest = read(manifest_path, "I01–I18 已确认归档总清单")
    receipt = read(f"{CONFIRMED}/确认与校验清单.json", "I01–I18 独立批准证据")
    index = read(f"{ARCHIVE}/当前归档索引.json", "当前归档与实装状态索引")
    entries = {entry["id"]: entry for entry in index["entries"]}
    forms = []
    for item in manifest["items"]:
        key = item["key"].upper()
        blueprint_path = f"{CONFIRMED}/confirmed_v2/{item['key']}/blueprint.json"
        bp = read(blueprint_path, f"{key} 已确认归档逐格蓝图")
        blocks = bp["blocks"]
        positions = {tuple(b["pos"]) for b in blocks}
        assert len(positions) == len(blocks) == item["blocks"], key
        actual = [max(p[a] for p in positions)-min(p[a] for p in positions)+1 for a in range(3)]
        forms.append(record(key, item["title"], item["size"], actual, len(blocks),
                            Counter(b["state"] for b in blocks), [manifest_path, blueprint_path],
                            approval_old(receipt, entries[key]), mapping,
                            "本次从确认归档 blueprint.json 逐格重算方块数、材料与实际占用范围。",
                            {"manifest_status": manifest.get("status"), "blueprint_approval_status": bp.get("approval_status")}))
    assert len(forms) == 21
    for number, directory in DELIVERIES.items():
        key = f"I{number}"
        manifest_path = f"deliveries/{directory}/manifest.json"
        verification_path = f"deliveries/{directory}/verification.json"
        m = read(manifest_path, f"{key} 当前指定版本清单")
        v = read(verification_path, f"{key} 当前版本几何与材料检查")
        declared = m.get("size_xyz", m.get("size"))
        check = v.get("size_check") or v.get("geometry", {}).get("size_check")
        assert check and check["declared_xyz"] == declared, key
        actual = check["actual_xyz"]
        palette = m.get("palette", v["palette"])
        assert palette == v["palette"], f"{key} 清单和检查调色板不一致"
        count = m["block_count"]
        assert v.get("blocks", count) == count, key
        source_status = {k: m[k] for k in ("status", "candidate_approved", "approval", "candidate_version") if k in m}
        approval = {"state": "candidate", "label": "当前候选／本审计未见该版本明确批准凭据",
                    "evidence_kind": "源清单的候选状态；不把继续制作当成批准",
                    "quote": "", "scope": "本报告仅检查建筑规模；候选不代表已批准或已实装。", "path": manifest_path}
        if number in RECEIPTS:
            receipt_path = f"{ARCHIVE}/{RECEIPTS[number]}/确认与校验清单.json"
            receipt = read(receipt_path, f"{key} 独立批准清单")
            approved = next(e for e in receipt["entries"] if e["id"] == key)
            approved_check = approved["structure_checks"]
            assert approved.get("block_count", approved_check.get("block_count")) == count, key
            assert approved.get("size_xyz", approved_check.get("declared_xyz")) == declared, key
            expected_manifest = approved.get("source_files_sha256", {}).get("manifest.json")
            if expected_manifest:
                assert SOURCES[manifest_path]["sha256"] == expected_manifest, f"{key} 当前清单已偏离批准快照"
            approval = {"state": "approved", "label": "外观已确认归档／待批次接入",
                        "evidence_kind": "独立确认清单；源文件 candidate_approved=false 为历史候选元数据",
                        "quote": approved["approval_quote"], "scope": approved["approval_scope"],
                        "path": receipt_path, "index_status": approved["status"],
                        "game_verified": approved.get("game_verified", False)}
        forms.append(record(key, m["title"], declared, actual, count, palette,
                            [manifest_path, verification_path], approval, mapping,
                            "本次核对当前 manifest 与 verification 材料统计、实际范围；未重新回读全部 NBT 方块。", source_status))
    return forms


def rate(passed, total):
    return {"passed": passed, "total": total, "percent": round(100*passed/total, 2) if total else None}


def evaluate(forms):
    pairs = []
    for higher in forms:
        lower_forms = [f for f in forms if f["tier"] < higher["tier"]]
        tests = {}
        for metric in METRICS:
            maximum = max((f["metrics"][metric] for f in lower_forms), default=None)
            tests[metric] = {"passed": higher["metrics"][metric] > maximum if maximum is not None else None,
                             "lower_max": maximum,
                             "lower_max_ids": [f["id"] for f in lower_forms if f["metrics"][metric] == maximum],
                             "counterexample_ids": [f["id"] for f in lower_forms if f["metrics"][metric] >= higher["metrics"][metric]]}
        higher["lower_form_count"] = len(lower_forms)
        higher["checks"] = tests
        higher["quantitative"] = rate(sum(t["passed"] is True for t in tests.values()), len(METRICS) if lower_forms else 0)
        higher["all_quantitative_passed"] = all(t["passed"] for t in tests.values()) if lower_forms else None
        for lower in lower_forms:
            failed = [metric for metric in METRICS if higher["metrics"][metric] <= lower["metrics"][metric]]
            pairs.append({"higher": higher["id"], "lower": lower["id"], "failed_metrics": failed,
                          "passed_metrics": len(METRICS)-len(failed), "all_passed": not failed})
    families = []
    for number in range(1, 26):
        group = [f for f in forms if f["family"] == f"I{number:02d}"]
        eligible = [f for f in group if f["lower_form_count"]]
        families.append({"id": f"I{number:02d}", "title": "崩坏能采集塔（四阶段）" if number == 1 else group[0]["title"],
                         "form_ids": [f["id"] for f in group],
                         "quantitative": rate(sum(f["quantitative"]["passed"] for f in eligible), 4*len(eligible)),
                         "all_quantitative_passed": all(f["all_quantitative_passed"] for f in eligible) if eligible else None})
    eligible = [f for f in forms if f["lower_form_count"]]
    eligible_families = [f for f in families if f["quantitative"]["total"]]
    summary = {
        "forms": len(forms), "families": len(families), "eligible_forms": len(eligible),
        "quantitative_metric_checks": rate(sum(f["quantitative"]["passed"] for f in eligible), 4*len(eligible)),
        "all_quantitative_forms": rate(sum(f["all_quantitative_passed"] for f in eligible), len(eligible)),
        "all_quantitative_families": rate(sum(f["all_quantitative_passed"] for f in eligible_families), len(eligible_families)),
        "ordered_voltage_pairs": len(pairs), "counterexample_pairs": sum(not p["all_passed"] for p in pairs),
        "pair_metric_checks": rate(sum(p["passed_metrics"] for p in pairs), 4*len(pairs)),
        "per_metric": {metric: rate(sum(f["checks"][metric]["passed"] for f in eligible), len(eligible)) for metric in METRICS},
        "approved_forms": sum(f["approval"]["state"] == "approved" for f in forms),
        "candidate_forms": sum(f["approval"]["state"] == "candidate" for f in forms),
    }
    i25 = next(f for f in forms if f["id"] == "I25")
    higher = [f for f in forms if f["tier"] > i25["tier"]]
    special = {"id": "I25", "metrics": i25["metrics"], "size_wdh": i25["size_wdh"], "checks": i25["checks"],
               "higher_tier_minima": {metric: {"value": min(f["metrics"][metric] for f in higher),
                    "ids": [f["id"] for f in higher if f["metrics"][metric] == min(x["metrics"][metric] for x in higher)]} for metric in METRICS},
               "higher_forms_compared": [f["id"] for f in higher],
               "higher_tier_counterexamples": [p for p in pairs if p["lower"] == "I25" and not p["all_passed"]]}
    assert len(forms) == 28 and len(families) == 25 and len(eligible) == 25
    assert next(f for f in forms if f["id"] == "I01-4")["tier"] == 26
    assert "I01-4" in special["higher_forms_compared"]
    assert sum(f["quantitative"]["total"] for f in forms) == 100
    if i25["metrics"]["materials"] >= 15:
        assert any(p["higher"] == "I01-4" and "materials" in p["failed_metrics"] for p in special["higher_tier_counterexamples"])
    return families, pairs, summary, special


HTML = r'''<!doctype html>
<html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>I01–I25 电压与建筑规模递增审计</title>
<style>
:root{color-scheme:dark;--bg:#07131d;--card:#102431;--line:#284553;--muted:#9ab2c1;--cyan:#71e4d4;--red:#ff9a9a;--amber:#f3cf83}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:#e4edf1;font:15px/1.65 system-ui,"Microsoft YaHei",sans-serif}main{max-width:1560px;margin:auto;padding:36px 24px 80px}h1{font-size:30px;line-height:1.3;margin:8px 0 12px}h2{font-size:21px;margin:0 0 14px}p{margin:8px 0}a{color:var(--cyan);overflow-wrap:anywhere}small,.muted{color:var(--muted)}.eyebrow{color:var(--cyan);letter-spacing:.14em}.cards{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:24px 0}.card,section{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:20px}section{margin:20px 0}.card strong{font-size:32px;display:block;color:var(--cyan)}.good{color:var(--cyan)}.bad{color:var(--red)}.na{color:var(--muted)}.warning{border-left:4px solid var(--amber);padding:10px 16px;background:#302a1b;color:#fae6bb;margin:16px 0}.controls{display:flex;gap:12px;flex-wrap:wrap;margin:16px 0}input,select,button{background:#0a1a26;border:1px solid #426171;color:#e4edf1;border-radius:8px;padding:10px;font:inherit}input{flex:1;min-width:210px}button{cursor:pointer}table{width:100%;border-collapse:collapse;text-align:left;font-variant-numeric:tabular-nums}th,td{border-bottom:1px solid var(--line);padding:12px 10px;vertical-align:top}th{color:#b6ced9;white-space:nowrap;background:#102431;position:sticky;top:0}td.num{text-align:right;white-space:nowrap}.scroll{overflow:auto;max-height:720px}.pill{display:inline-block;border:1px solid currentColor;padding:1px 8px;border-radius:20px;white-space:nowrap;font-size:12px}details{margin:8px 0}summary{cursor:pointer;color:var(--cyan)}.detail{background:#091b27;border-radius:8px;padding:14px;min-width:440px}.detail table{font-size:13px}.metric{display:inline-block;margin-right:14px}code{font-family:Consolas,monospace;overflow-wrap:anywhere}.sources li{margin:8px 0}.legend{display:flex;gap:24px;flex-wrap:wrap}.grid2{display:grid;grid-template-columns:1fr 1fr;gap:20px}.empty{padding:25px;color:var(--muted)}@media(max-width:900px){.cards,.grid2{grid-template-columns:1fr 1fr}h1{font-size:25px}}@media(max-width:600px){.cards,.grid2{grid-template-columns:1fr}main{padding:20px 12px}.card strong{font-size:27px}}
</style><main>
<div class="eyebrow">HK3GTL · 建筑设计规则核验</div><h1>I01–I25：高电压是否严格高于所有低电压结构</h1>
<p>按负责人指定电压映射，对全部不同电压的结构逐对比较。I01 四阶段展开为 28 个形态，并另按 25 台机器汇总；同电压不比较。</p>
<p class="muted" id="stamp"></p><div class="cards" id="summary"></div>
<div class="warning">百分比只覆盖「实际方块数、唯一材料数、实际包围盒体积、实际高度」四项。华丽度、复杂度、细致度、现实风格需逐图评审，本报告未赋分；量化四项全部通过也不等于整条规则通过。MAX 是 tier14，V01 是 tier15。</div>
<section><h2>统计口径与证据</h2><p>严格递增要求较高电压的每个形态在每项指标上，都大于全部较低电压形态；相等也算反例。最低电压 MAX 三台没有本次范围内的低阶比较对象，显示「无比较对象」并从通过率分母排除。</p><p>材料数按非空气方块 ID 去重，包含主控占位与工业接口；朝向等状态差异不增加材料数。体积是实际占用包围盒 W×D×H，包含内部空腔，不能代表实体材料量；同时单列真实方块总数。I01–I18 本次逐格读取确认归档蓝图；I19–I25 本次核对指定版本 manifest 与 verification 的统计，未重新读取全部 NBT。</p><p>外观批准以独立确认清单为证；源候选文件中的待审字段保留作历史元数据。建筑批准、文件实装、游戏运行验收各自独立。本审计不评估配方、功能或内测五整体完成度。</p><div id="metrics" class="legend"></div></section>
<section><h2>I25 当前快照与上下电压边界</h2><div id="i25"></div></section>
<section><h2>28 个结构形态</h2><div class="controls"><input id="search" placeholder="搜索编号、名称、电压、批准状态"><select id="tier"><option value="">全部电压</option></select><select id="status"><option value="">全部量化状态</option><option value="fail">存在反例</option><option value="pass">四项全部通过</option><option value="na">无比较对象</option></select><select id="approval"><option value="">全部批准状态</option><option value="approved">已确认归档</option><option value="candidate">当前候选</option></select></div><p id="formcount" class="muted"></p><div class="scroll"><table><thead><tr><th>形态 / 名称</th><th>目标电压</th><th>实际 W×D×H</th><th>方块数</th><th>材料数</th><th>包围盒体积</th><th>量化通过率</th><th>批准证据 / 详情</th></tr></thead><tbody id="forms"></tbody></table></div></section>
<section><h2>25 台机器汇总</h2><p class="muted">I01 汇总其四个阶段的 16 个量化判定；机器「四项全通过」要求所属全部可比较阶段通过。百分比按各阶段实际可比较项累计，不对四阶段取平均后掩盖反例。</p><div class="scroll"><table><thead><tr><th>机器</th><th>包含形态</th><th>通过项 / 可比较项</th><th>量化通过率</th></tr></thead><tbody id="families"></tbody></table></div></section>
<section><h2>严格比较反例</h2><p class="muted">每行是一对较高 / 较低电压结构；列出所有不严格大于的指标。反例可搜索，高低阶均保留原始 ID；完整判定存于 audit.json。</p><div class="controls"><input id="pairsearch" placeholder="搜索 I25、I01-4、材料数…"><select id="pairmetric"><option value="">全部反例指标</option></select></div><p id="paircount" class="muted"></p><div class="scroll"><table><thead><tr><th>较高电压</th><th>较低电压</th><th>不满足严格递增的指标（高阶 ≤ 低阶）</th></tr></thead><tbody id="pairs"></tbody></table></div></section>
<section><h2>来源文件与快照校验</h2><p class="muted">以下路径相对于项目根目录；链接可直接打开本地原文件。SHA-256 对应本次读取的文件内容。候选变化后应重跑生成器；此页是静态快照。</p><p><a href="audit.json">下载 / 查看完整审计 JSON</a></p><details><summary>展开全部来源文件与 SHA-256</summary><ul id="sources" class="sources"></ul></details></section>
</main><script id="auditdata" type="application/json">__AUDIT_DATA__</script><script>
const D=JSON.parse(document.getElementById('auditdata').textContent),F=Object.fromEntries(D.forms.map(f=>[f.id,f]));
const $=id=>document.getElementById(id),esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])),num=n=>Number(n).toLocaleString('zh-CN'),pct=r=>r.percent===null?'无比较对象':`${r.percent.toFixed(2)}%`,cls=f=>f.all_quantitative_passed===null?'na':f.all_quantitative_passed?'good':'bad',link=(p,label)=>`<a href="../../${encodeURI(p).replace(/#/g,'%23')}" target="_blank">${esc(label||p)}</a>`;
$('stamp').textContent=`快照：${D.generated_at} · ${D.summary.approved_forms} 个形态有独立批准证据，${D.summary.candidate_forms} 个为当前候选 · 映射来源：${D.mapping_source}`;
const S=D.summary;$('summary').innerHTML=[['量化判定通过率',S.quantitative_metric_checks,'每形态 × 4 项；全体低阶极值核验'],['四项全通过形态',S.all_quantitative_forms,'28 形态中 25 个存在低阶比较对象'],['四项全通过机器',S.all_quantitative_families,'25 台中 22 台存在低阶比较对象'],['逐对指标通过率',S.pair_metric_checks,`${S.ordered_voltage_pairs} 对比较，${S.counterexample_pairs} 对含反例`]].map(([t,r,n])=>`<div class="card"><span>${t}</span><strong>${pct(r)}</strong><span>${r.passed} / ${r.total}</span><br><small>${n}</small></div>`).join('');
$('metrics').innerHTML=Object.entries(S.per_metric).map(([k,r])=>`<span>${D.metric_labels[k]}：<b>${pct(r)}</b> <small>(${r.passed}/${r.total})</small></span>`).join('');
function details(f){return `<details><summary>低阶极值、反例与原始证据</summary><div class="detail"><table><thead><tr><th>指标</th><th>本形态</th><th>全部低阶最大值 / 来源</th><th>结果</th></tr></thead><tbody>${Object.entries(f.checks).map(([k,t])=>`<tr><td>${D.metric_labels[k]}</td><td>${num(f.metrics[k])}</td><td>${t.lower_max===null?'无比较对象':`${num(t.lower_max)} · ${t.lower_max_ids.map(esc).join('、')}`}</td><td class="${t.passed===null?'na':t.passed?'good':'bad'}">${t.passed===null?'—':t.passed?'通过':`不通过<br>反例：${t.counterexample_ids.map(esc).join('、')}`}</td></tr>`).join('')}</tbody></table><p>声明 XYZ：${f.declared_xyz.join('×')}；实际 XYZ：${f.actual_xyz.join('×')}${f.dimensions_differ?' · <b class="bad">声明空边界已剔除</b>':''}</p><p>${esc(f.measurement_evidence)}</p><p>批准证据性质：${esc(f.approval.evidence_kind)}<br>负责人原话：${esc(f.approval.quote||'本审计未检出该版本明确批准凭据')}<br>范围：${esc(f.approval.scope)}</p><p>${link(f.approval.path,'批准 / 候选状态来源')}</p><p>${f.sources.map(p=>link(p)).join('<br>')}</p><details><summary>源候选历史状态字段</summary><pre>${esc(JSON.stringify(f.source_candidate_metadata,null,2))}</pre></details><details><summary>材料用量（${f.metrics.materials} 种方块 ID）</summary>${Object.entries(f.palette).sort((a,b)=>b[1]-a[1]).map(([s,n])=>`<p><code>${esc(s)}</code> · ${num(n)}</p>`).join('')}</details></div></details>`}
function renderForms(){const query=$('search').value.trim().toLowerCase(),tier=$('tier').value,status=$('status').value,approval=$('approval').value;const forms=D.forms.filter(f=>(!tier||f.voltage===tier)&&(!approval||f.approval.state===approval)&&(!status||(status==='na'?f.all_quantitative_passed===null:status==='pass'?f.all_quantitative_passed===true:f.all_quantitative_passed===false))&&`${f.id} ${f.title} ${f.voltage_label} ${f.approval.label}`.toLowerCase().includes(query));$('formcount').textContent=`显示 ${forms.length} / ${D.forms.length} 个形态；列表通过率按全体低阶判定，筛选不会改变比较对象。`;$('forms').innerHTML=forms.map(f=>`<tr><td><b>${f.id}</b><br>${esc(f.title)}</td><td>${esc(f.voltage_label)}</td><td>${f.size_wdh.join('×')}${f.dimensions_differ?'<br><small>已剔除声明空边界</small>':''}</td><td class="num">${num(f.metrics.blocks)}</td><td class="num">${f.metrics.materials}</td><td class="num">${num(f.metrics.volume)}</td><td class="${cls(f)}"><b>${pct(f.quantitative)}</b><br><small>${f.quantitative.passed}/${f.quantitative.total}</small></td><td><span class="pill ${f.approval.state==='approved'?'good':'na'}">${esc(f.approval.label)}</span>${details(f)}</td></tr>`).join('')||'<tr><td colspan="8" class="empty">没有匹配项。</td></tr>'}
const tiers=[...new Set(D.forms.map(f=>f.voltage))].sort((a,b)=>D.tiers[a]-D.tiers[b]);$('tier').innerHTML+=tiers.map(v=>`<option value="${v}">${v} / tier${D.tiers[v]}</option>`).join('');for(const id of ['search','tier','status','approval'])$(id).addEventListener('input',renderForms);renderForms();
$('families').innerHTML=D.families.map(f=>`<tr><td><b>${f.id}</b> ${esc(f.title)}</td><td>${f.form_ids.join('、')}</td><td>${f.quantitative.passed} / ${f.quantitative.total}</td><td class="${cls(f)}">${pct(f.quantitative)}</td></tr>`).join('');
const I=D.i25_snapshot;$('i25').innerHTML=`<p><b>${I.size_wdh.join('×')}</b> W×D×H · <b>${num(I.metrics.blocks)}</b> 块 · <b>${I.metrics.materials}</b> 种材料 · 实际包围盒 <b>${num(I.metrics.volume)}</b> 格³。${link(F.I25.sources[0],'当前 I25 manifest')}</p><div class="grid2"><div><h3>全部低阶极值</h3>${Object.entries(I.checks).map(([k,t])=>`<p>${D.metric_labels[k]}：${num(t.lower_max)}（${t.lower_max_ids.join('、')}） · <b class="${t.passed?'good':'bad'}">I25 ${t.passed?'通过':'不通过'}</b></p>`).join('')}</div><div><h3>全部高阶最小值</h3><p class="muted">本次高阶对象：${I.higher_forms_compared.join('、')}，包含 I01-4 / IWV / V12。</p>${Object.entries(I.higher_tier_minima).map(([k,t])=>`<p>${D.metric_labels[k]}：${num(t.value)}（${t.ids.join('、')}）</p>`).join('')}</div></div><p>${I.higher_tier_counterexamples.length?'<b class="bad">更高阶相对 I25 仍存在反例：</b>'+I.higher_tier_counterexamples.map(p=>`${p.higher} 的 ${p.failed_metrics.map(k=>D.metric_labels[k]).join('、')}`).join('；'):'全部现有高阶均在四项量化指标上严格大于 I25。'}</p>`;
const failedPairs=D.comparisons.filter(p=>!p.all_passed);$('pairmetric').innerHTML+=Object.entries(D.metric_labels).map(([k,v])=>`<option value="${k}">${v}</option>`).join('');function renderPairs(){const query=$('pairsearch').value.trim().toLowerCase(),metric=$('pairmetric').value;const pairs=failedPairs.filter(p=>(!metric||p.failed_metrics.includes(metric))&&`${p.higher} ${F[p.higher].title} ${p.lower} ${F[p.lower].title} ${p.failed_metrics.map(k=>D.metric_labels[k]).join(' ')}`.toLowerCase().includes(query));$('paircount').textContent=`显示 ${pairs.length} / ${failedPairs.length} 对反例；全体不同电压比较共 ${D.comparisons.length} 对。`;$('pairs').innerHTML=pairs.map(p=>`<tr><td><b>${p.higher}</b><br><small>${F[p.higher].voltage_label}</small></td><td><b>${p.lower}</b><br><small>${F[p.lower].voltage_label}</small></td><td>${p.failed_metrics.map(k=>`<span class="metric bad">${D.metric_labels[k]} ${num(F[p.higher].metrics[k])} ≤ ${num(F[p.lower].metrics[k])}</span>`).join('')}</td></tr>`).join('')||'<tr><td colspan="3" class="empty">没有匹配的反例。</td></tr>'}for(const id of ['pairsearch','pairmetric'])$(id).addEventListener('input',renderPairs);renderPairs();
$('sources').innerHTML=D.sources.map(s=>`<li>${link(s.path)}<br><small>${esc(s.kind)} · <code>${s.sha256}</code></small></li>`).join('');
</script></html>'''


def main():
    mapping = voltage_mapping()
    forms = load_forms(mapping)
    families, pairs, summary, special = evaluate(forms)
    report = {
        "schema_version": 1, "generated_at": datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds"),
        "scope": "I01四阶段与I02–I25，共28形态／25台机器；仅建筑规模四项量化规则。",
        "mapping_source": MAPPING, "tiers": TIERS, "metric_labels": METRICS,
        "comparison_rule": "任意较高电压形态 > 全部较低电压形态；同阶排除，相等不通过；无低阶对象不计分母。",
        "qualitative_dimensions": {name: "需逐图评审，未量化，不计入百分比" for name in ("华丽度", "复杂度", "细致度", "现实风格")},
        "qualitative_review": {
            "scope": "针对性预览对照；非全体评分，不生成百分比。未覆盖细项仍为未核实。",
            "findings": [
                {"higher": ["I06", "I07"], "lower": ["I04"], "result": "反例", "dimensions": ["设备密度", "功能分区", "现实工程感"], "evidence": ["deliveries/I01-I18_控制器居中融合修订_V2_20261023/i04/等轴预览.png", "deliveries/I01-I18_控制器居中融合修订_V2_20261023/i06/等轴预览.png", "deliveries/I01-I18_控制器居中融合修订_V2_20261023/i07/等轴预览.png"]},
                {"higher": ["I08"], "lower": ["I11", "I12"], "result": "待复核", "dimensions": ["细节", "功能分区", "现实感"], "evidence": ["deliveries/I01-I18_控制器居中融合修订_V2_20261023/i08/等轴预览.png", "deliveries/I01-I18_控制器居中融合修订_V2_20261023/i11/等轴预览.png", "deliveries/I01-I18_控制器居中融合修订_V2_20261023/i12/等轴预览.png"]},
                {"higher": ["I24"], "lower": ["I23"], "result": "反例", "dimensions": ["视觉复杂度", "工艺细节", "体量感"], "evidence": ["deliveries/I23_崩坏能相变释能机_双瓣相界锻炉_V8_20261024/等轴预览.png", "deliveries/I24_量子异常观测阵列_三碟长基线天文庭院_V2_20261025/等轴预览.png"]},
                {"higher": ["I22"], "lower": ["I21"], "result": "待复核", "dimensions": ["艺术复杂度", "细节"], "evidence": ["deliveries/I21_大型崩坏能反应堆_闭式三回路联合厂区候选_V1_20261023/i21/等轴预览.png", "deliveries/I22_究极崩坏能反应堆_四堆隔离外场候选_V1_20261023/i22/等轴预览.png"]},
                {"higher": ["I01-2", "I01-3", "I01-4"], "lower": ["I01-1"], "result": "局部递增清晰", "dimensions": ["扩建层级", "承重结构", "模块数量"]},
            ],
        },
        "summary": summary, "forms": forms, "families": families, "comparisons": pairs,
        "i25_snapshot": special, "sources": list(SOURCES.values()),
        "self_checks": {"28形态": True, "25机器族": True, "MAX14与V01_15": True,
                        "I01四阶段独立核验": True, "I01_4_V12列入I25高阶比较": True,
                        "清单与调色板总量一致": True, "来源快照SHA256": True},
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    inline = json.dumps(report, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    page = HTML.replace("__AUDIT_DATA__", inline)
    page = page.replace(
        "I21_%E5%A4%A7%E5%9E%8B%E5%B4%A9%E5%9D%8F%E8%83%BD%E5%8F%8D%E5%BA%94%E5%A0%86_%E9%97%AD%E5%BC%8F%E4%B8%89%E5%9B%9E%E8%B7%AF%E8%81%94%E5%90%88%E5%8E%82%E5%8C%BA%E5%80%99%E9%80%89_V1_20261023/%E7%AD%89%E8%BD%B4%E9%A2%84%E8%A7%88.png",
        "I21_%E5%A4%A7%E5%9E%8B%E5%B4%A9%E5%9D%8F%E8%83%BD%E5%8F%8D%E5%BA%94%E5%A0%86_%E9%97%AD%E5%BC%8F%E4%B8%89%E5%9B%9E%E8%B7%AF%E8%81%94%E5%90%88%E5%8E%82%E5%8C%BA%E5%80%99%E9%80%89_V1_20261023/i21/%E7%AD%89%E8%BD%B4%E9%A2%84%E8%A7%88.png",
    )
    page = page.replace(
        "I23_%E5%B4%A9%E5%9D%8F%E8%83%BD%E7%9B%B8%E5%8F%98%E9%87%8A%E8%83%BD%E6%9C%BA_%E5%8F%8C%E7%93%A3%E7%9B%B8%E7%95%8C%E7%82%89_V8_20261024",
        "I23_%E5%B4%A9%E5%9D%8F%E8%83%BD%E7%9B%B8%E5%8F%98%E9%87%8A%E8%83%BD%E6%9C%BA_%E5%8F%8C%E7%93%A3%E7%9B%B8%E7%95%8C%E9%94%BB%E7%82%89_V8_20261024",
    )
    (OUT / "audit.html").write_text(page, encoding="utf-8")
    print(json.dumps({"generated_at": report["generated_at"], "summary": summary, "i25_snapshot": special,
                      "output": str(OUT)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
