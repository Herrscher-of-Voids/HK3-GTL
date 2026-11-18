"""根据10月25日基线与30日只读复核数据生成内测5完成度HTML。"""
from __future__ import annotations

import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "logs/beta5-completion-audit-20261030"
BASELINE = ROOT / "logs/beta5-audit-20261025/percentage-audit.json"
PROGRESSION = OUT_DIR / "progression-evidence.json"
RUNTIME = OUT_DIR / "runtime-evidence.json"
INDUSTRY = OUT_DIR / "industry-evidence.json"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def esc(value):
    return html.escape(str(value), quote=True)


def file_link(value):
    value = str(value)
    path, marker, line = value.partition(":")
    target = "../../" + path.replace("\\", "/")
    if marker and line.isdigit():
        target += "#L" + line
    return f'<a href="{esc(target)}">{esc(value)}</a>'


def evidence_links(values):
    links = []
    for value in values or []:
        if isinstance(value, dict):
            path = value.get("path")
            line = value.get("line")
            if path:
                links.append(file_link(f"{path}:{line}" if line else path))
        elif isinstance(value, str):
            path = value.split("#", 1)[0]
            links.append(file_link(path))
    return " · ".join(links)


def build():
    baseline = read_json(BASELINE)
    progression = read_json(PROGRESSION)
    runtime = read_json(RUNTIME)
    industry = read_json(INDUSTRY)

    progression_by_id = {item["id"]: item for item in progression["legacy_domain_review"]}
    industry_by_id = {item["id"]: item for item in industry["domains"]}
    runtime_by_id = {item["id"]: item for item in runtime["nine_domains"]}
    updates = {
        ("energy_production", 2): (
            "complete",
            "I19–I22控制器注册、正式Pattern及52形态架构白名单均已接入源码；本项只评结构代码，游戏验收另计。",
        ),
        ("energy_production", 7): (
            "partial",
            "I23、I38、I41的控制器与正式Pattern已进入源码；相变释能及跨机能源工艺仍受provisional守卫，未证明可生产。",
        ),
        ("multiblocks", 2): (
            "unknown",
            "10月25日的29台批准/3台待批记录没有新台账复核，不能沿用为当前审批数量；52份正式架构资源不等于52台均获批准。",
        ),
        ("multiblocks", 3): (
            "partial",
            "旧‘余下43台/88台席位’已过时。当前确认范围为70台具名结构+4台MAX复制系统；14个工业候选席位暂停且不计分母。52份正式架构资源覆盖当前74项的70.3%，尚缺22项正式架构资源。",
        ),
    }

    systems = []
    for system in baseline["systems"]:
        current_caps = []
        changed = False
        for index, cap in enumerate(system["capabilities"]):
            current_status = cap["status"]
            reason = cap.get("reason", "")
            update = updates.get((system["id"], index))
            if update:
                current_status, reason = update
                changed = True
            earned = {"complete": 1.0, "partial": 0.5}.get(current_status, 0.0)
            current_caps.append({
                "claim": cap["claim"],
                "old_status": cap["status"],
                "status": current_status,
                "reason": reason,
                "old_reason": cap.get("reason", ""),
                "earned": earned,
                "possible": 1.0,
                "updated": bool(update),
            })
        if changed:
            earned = sum(cap["earned"] for cap in current_caps)
            possible = len(current_caps)
            percent = earned / possible * 100 if possible else 0.0
        else:
            earned = system["earned"]
            possible = system["possible"]
            percent = earned / possible * 100 if possible else 0.0
        review = industry_by_id.get(system["id"])
        progression_review = progression_by_id.get(system["id"])
        runtime_review = runtime_by_id.get(system["id"])
        coverage = "10月30日重点复核" if review or progression_review or runtime_review else "沿用10月25日评分"
        systems.append({
            "id": system["id"],
            "name": system["name"],
            "group": system["group"],
            "baseline_percent": system["percent"],
            "earned": earned,
            "possible": possible,
            "percent": percent,
            "changed": changed,
            "coverage": coverage,
            "capabilities": current_caps,
            "baseline_gaps": system.get("gaps", []),
            "industry_review": review,
            "progression_review": progression_review,
            "runtime_review": runtime_review,
        })

    overall = sum(system["percent"] for system in systems) / len(systems)
    groups = {}
    for system in systems:
        groups.setdefault(system["group"], []).append(system["percent"])
    group_summary = {name: sum(values) / len(values) for name, values in groups.items()}
    runtime_status_counts = {}
    for item in runtime["supplemental_requirements"]:
        runtime_status_counts[item["status"]] = runtime_status_counts.get(item["status"], 0) + 1

    summary = {
        "audit_date": "2026-10-30",
        "baseline_date": "2026-10-25",
        "method": "36个系统域等权算术平均；系统内部能力项等权，complete=1、partial=0.5、missing/unknown=0。未改分域沿用10月25日原始精确分数。",
        "overall_percent": overall,
        "baseline_percent": baseline["overall"]["earned"],
        "domain_count": len(systems),
        "systems": systems,
        "group_summary": group_summary,
        "multiblock_scope": {"formal_architecture_resources": 52, "agreed_scope": 74, "coverage_percent": 52 / 74 * 100,
                             "named_existing": 70, "max_copy_arrays": 4, "paused_industry_candidates": 14,
                             "missing_architecture_resources": 22},
        "target_instance": {"revision": 186, "version": "GTL增强版2.9.2", "installed": True, "game_verified": False,
                            "runtime_memory_acceptance": False, "terminal_dismantle_acceptance": False},
        "runtime_supplement_status_counts": runtime_status_counts,
    }

    data_json = json.dumps(summary, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    status_names = {"complete": "完成", "partial": "部分完成", "missing": "未完成", "unknown": "未知"}
    cards = []
    for system in systems:
        cap_rows = []
        for cap in system["capabilities"]:
            status_class = cap["status"]
            status_label = status_names[status_class]
            delta = " · 本次调整" if cap["updated"] else ""
            cap_rows.append(
                f'<tr><td>{esc(cap["claim"])}</td><td><span class="status {status_class}">{status_label}</span>{delta}</td>'
                f'<td>{esc(cap["reason"])}</td></tr>'
            )
        review = system["industry_review"]
        if review:
            review_rows = []
            for item in review.get("items", []):
                change_html = f'<span class="muted">{esc(item["change"])}</span>' if item.get("change") else ""
                item_evidence = evidence_links(item.get("evidence", []))
                evidence_html = f'<span class="evidence">{item_evidence}</span>' if item_evidence else ""
                review_rows.append(
                    f'<li><b>{esc(item.get("claim", ""))}</b>：{esc(item.get("fact", ""))}'
                    f' {change_html} {evidence_html}</li>'
                )
            review_html = "<ul>" + "".join(review_rows) + "</ul>"
        else:
            review_html = ""
        progression_review = system["progression_review"]
        if progression_review:
            snippets = progression_review.get("changed_findings", []) + progression_review.get("retained_findings", [])
            if snippets:
                review_html += "<ul>" + "".join(f"<li>{esc(text)}</li>" for text in snippets) + "</ul>"
            review_html += f'<p class="evidence">{evidence_links(progression_review.get("evidence", []))}</p>'
        runtime_review = system["runtime_review"]
        if runtime_review:
            review_html += f'<p><b>部署/验收状态：</b>{esc(runtime_review.get("status", ""))}。{esc(runtime_review.get("gap", ""))}</p>'
            refs = runtime_review.get("code", []) + runtime_review.get("test", []) + runtime_review.get("runtime", []) + runtime_review.get("deploy", [])
            review_html += f'<p class="evidence">{evidence_links(refs)}</p>'
        if not review_html:
            review_html = '<p class="muted">10月30日的定向证据未覆盖此域；分数沿用10月25日，不代表本轮逐项重新验收。</p>'
        gaps = system["baseline_gaps"]
        gap_html = "<ul>" + "".join(f"<li>{esc(item)}</li>" for item in gaps) + "</ul>" if gaps else ""
        cards.append(
            f'<article class="system" data-id="{esc(system["id"])}" data-group="{esc(system["group"])}" data-search="{esc(system["id"] + " " + system["name"] + " " + system["group"])}">'
            f'<button class="system-head" type="button" aria-expanded="false">'
            f'<span class="sys-name"><small>{esc(system["id"])}</small>{esc(system["name"])}</span>'
            f'<span class="score"><b>{system["percent"]:.1f}%</b><small>基线 {system["baseline_percent"]:.1f}%</small></span>'
            f'<span class="chevron" aria-hidden="true">＋</span></button>'
            f'<div class="bar"><i style="width:{system["percent"]:.3f}%"></i></div>'
            f'<div class="system-detail" hidden><p class="coverage">{esc(system["coverage"])} · 当前缺口</p>{review_html}{gap_html}'
            f'<h4>能力项与评分依据</h4><div class="table-wrap"><table><thead><tr><th>能力项</th><th>状态</th><th>当前证据与差距</th></tr></thead><tbody>{"".join(cap_rows)}</tbody></table></div></div></article>'
        )

    group_options = "".join(f'<option value="{esc(name)}">{esc(name)}</option>' for name in group_summary)
    group_cards = "".join(
        f'<div class="group-stat"><span>{esc(name)}</span><b>{percent:.1f}%</b><small>{sum(1 for s in systems if s["group"] == name)}个域</small></div>'
        for name, percent in group_summary.items()
    )
    delta = overall - baseline["overall"]["earned"]
    delta_text = f"{delta:+.1f} 个百分点"
    if abs(delta) < 0.05:
        delta_text = "基本持平"

    html_page = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>内测5全系统完成度复审 · 2026-10-30</title>
<style>
:root{{color-scheme:dark;--bg:#101820;--surface:#17232c;--line:#31434c;--text:#e5edf0;--muted:#9eb1b7;--cyan:#5bd1c8;--lime:#b7d86b;--amber:#e8bf64;--red:#ef7e70;--blue:#72b9e5}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.55 system-ui,'Microsoft YaHei',sans-serif}}
main{{max-width:1320px;margin:auto;padding:28px 22px 60px}}h1{{font-size:25px;margin:0 0 6px}}h2{{font-size:18px;margin:30px 0 12px}}h3{{font-size:16px}}h4{{margin:22px 0 8px;color:#bdd1d5}}p{{margin:8px 0}}a{{color:var(--cyan)}}small,.muted,.sub{{color:var(--muted)}}
.eyebrow{{color:var(--cyan);font-size:12px;font-weight:700;letter-spacing:.06em}}.lede{{color:#b9c8cd;max-width:960px;margin:0 0 18px}}
.metrics{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin:18px 0}}.metric,.group-stat,.notice{{background:var(--surface);border:1px solid var(--line);border-radius:5px;padding:14px}}
.metric span,.metric small{{display:block;color:var(--muted)}}.metric strong{{font-size:26px;line-height:1.3;display:block;margin:3px 0}}.metric .accent{{color:var(--cyan)}}.metric .alert{{color:var(--amber)}}
.notice{{border-left:3px solid var(--amber);margin:10px 0 20px}}.notice b{{color:#f3d994}}
.group-grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}}.group-stat span,.group-stat small{{display:block;color:var(--muted)}}.group-stat b{{display:block;color:var(--lime);font-size:21px}}
.controls{{display:flex;gap:8px;flex-wrap:wrap;margin:14px 0;position:sticky;top:0;background:var(--bg);padding:8px 0;z-index:2}}input,select,button{{font:inherit;color:var(--text);background:#192831;border:1px solid #40545e;border-radius:4px;padding:9px 11px}}input{{flex:1;min-width:240px}}button{{cursor:pointer}}button:hover{{border-color:var(--cyan)}}.count{{color:var(--muted);align-self:center;font-size:13px}}
.system-list{{display:grid;grid-template-columns:1fr 1fr;gap:9px;align-items:start}}.system{{border:1px solid var(--line);background:#141f27;border-radius:5px;overflow:hidden}}.system[hidden]{{display:none}}.system-head{{width:100%;display:grid;grid-template-columns:1fr auto 22px;gap:12px;align-items:center;text-align:left;background:transparent;border:0;border-radius:0;padding:12px 13px 9px}}.sys-name{{font-weight:650}}.sys-name small{{display:inline-block;color:var(--cyan);width:74px;font:12px ui-monospace,monospace}}.score{{text-align:right}}.score b{{display:block;color:var(--lime);font-size:18px}}.score small{{font-size:11px}}.chevron{{color:var(--cyan);font-size:18px}}.bar{{height:3px;background:#293a42}}.bar i{{height:100%;display:block;background:var(--cyan)}}.system-detail{{padding:10px 13px 15px;border-top:1px solid var(--line)}}.system-detail[hidden]{{display:none}}.coverage{{font-size:12px;color:var(--amber);margin:0 0 8px}}
.system-detail ul{{padding-left:20px;margin:7px 0}}.system-detail li{{margin:6px 0}}.evidence{{font-size:12px;overflow-wrap:anywhere}}.evidence a{{display:inline-block;margin:2px 5px 2px 0}}.status{{font-size:11px;padding:2px 6px;border-radius:3px;border:1px solid currentColor;white-space:nowrap}}.status.complete{{color:var(--lime)}}.status.partial{{color:var(--amber)}}.status.missing{{color:var(--red)}}.status.unknown{{color:var(--blue)}}
.table-wrap{{overflow:auto}}table{{border-collapse:collapse;width:100%;min-width:620px;font-size:12px}}th,td{{border-bottom:1px solid #30424a;text-align:left;vertical-align:top;padding:7px}}th{{color:var(--muted);font-weight:600}}td:first-child{{width:24%}}td:nth-child(2){{width:14%;white-space:nowrap}}
.foot{{border-top:1px solid var(--line);margin-top:28px;padding-top:14px;color:var(--muted);font-size:13px}}.sources{{display:flex;gap:12px;flex-wrap:wrap}}
@media(max-width:850px){{.metrics{{grid-template-columns:repeat(2,minmax(0,1fr))}}.system-list{{grid-template-columns:1fr}}.group-grid{{grid-template-columns:1fr}}}}
@media(max-width:480px){{main{{padding:20px 12px 40px}}.metrics{{gap:7px}}.metric{{padding:10px}}.metric strong{{font-size:21px}}.system-head{{grid-template-columns:1fr auto 16px;gap:6px}}.sys-name small{{width:50px}}input{{min-width:100%}}}}
</style></head><body><main>
<div class="eyebrow">HK3GTL · 内测5 · 只读复审 · 2026-10-30</div>
<h1>全系统完成度与内测5讨论差距</h1>
<p class="lede">另一个我，按10月25日的36域等权方法重算，并把新增部署证据与旧设计要求逐项对照。分数是源码/工程能力估算；不等于游戏实机通过率、自然毕业率或1.0发布批准。</p>
<section class="metrics" aria-label="总体指标">
<div class="metric"><span>当前工程完成度</span><strong class="accent">{overall:.1f}%</strong><small>36个系统域等权</small></div>
<div class="metric"><span>10月25日审计基线</span><strong>68.9%</strong><small>本次变化：{delta_text}</small></div>
<div class="metric"><span>正式架构资源覆盖</span><strong class="accent">52 / 74</strong><small>70.3%；资源存在不代表游戏验收</small></div>
<div class="metric"><span>当前部署版本</span><strong>2.9.2 · r186</strong><small class="alert">已安装；game_verified=false</small></div>
</section>
<div class="notice"><b>口径提醒：</b>原规划88项中，14个工业候选席位现已冻结且暂不新增；当前确认范围是70台具名结构+4台MAX复制阵列=74项。现有52份I/S正式架构资源覆盖70.3%，仍缺22项；W01有独立源码/蓝图，但本次版本的整楼成型、控制器及拆除未实机验收。FCL/电脑版最终三工况与全结构运行内存目标尚未测试，不能把旧样本或部署包写成达标。</div>
<h2>分组平均</h2><section class="group-grid">{group_cards}</section>
<h2>逐系统评分</h2>
<div class="controls"><input id="search" type="search" placeholder="搜索系统名称、编号或差距" aria-label="搜索系统"><select id="group"><option value="">所有分组</option>{group_options}</select><select id="order"><option value="score-asc">完成度由低到高</option><option value="score-desc">完成度由高到低</option><option value="name">按编号</option></select><button id="openAll" type="button">展开全部</button><span class="count" id="count"></span></div>
<div class="system-list" id="systems">{"".join(cards)}</div>
<h2>本次复核与旧讨论的主要差距</h2><div class="notice"><ul>
<li><b>结构包：</b>正式架构从旧审计26项推进到52项；当前74项范围内覆盖率70.3%。其中14个候选席位暂停，不计当前分母。</li>
<li><b>能源结构：</b>I19–I22的控制器与正式Pattern已补入源码评分；I23/I38/I41的控制器也在，但工艺守卫仍禁止把它们当作可执行能源闭环。</li>
<li><b>批准状态：</b>旧29项批准、3项待批数字没有新台账佐证，当前标为未知；这会降低多方块审查域的评分，不代表已完成结构减少。</li>
<li><b>13位律者奇观：</b>W01–W15中13座成型后生成对应律者并可对话的规则已确定；逐座映射、W02–W15正式结构，以及西琳触发绑定尚未实现或验收。W03对应西琳，不是凌虛晴。</li>
<li><b>兼容与性能：</b>目标包安装在GTL增强版2.9.2，构建/资源校验有记录；游戏验收、终极终端拆除、AE联动、8GB全结构部署测试及FCL测试仍未通过验收。</li>
</ul></div>
<p class="muted">运行与部署复核列出20项补充要求；“源码/测试存在”“旧修订曾验证”“已部署未实机验证”保持区别，详情见下方原始清单。</p>
<details><summary>查看20项新增验收要求与证据状态</summary><div class="table-wrap"><table><thead><tr><th>要求</th><th>状态</th><th>当前差距</th></tr></thead><tbody>{"".join(f'<tr><td>{esc(item["id"])}</td><td>{esc(item["status"])}</td><td>{esc(item.get("gap", item.get("requirement", "")) or item.get("requirement", ""))}</td></tr>' for item in runtime["supplemental_requirements"])}</tbody></table></div>
<ul>{"".join(f'<li><b>{esc(item["id"])}</b>：{esc(item["state"])}</li>' for item in industry["supplemental_requirements"])}</ul></details>
<footer class="foot"><p><b>计分法：</b>36个审查域百分比算术平均、每域等权；域内每项等权，完成=1、部分=0.5、缺失/未知=0。未发生有证据状态变化的领域沿用10月25日精确分值。本轮改分仅限能源生产与多方块域。unknown表示证据不足，不表示已证明不存在。</p>
<p><b>复核范围：</b>对照内测5设计/讨论摘要、36域旧审计、10个工业域、17个进度域、9个运行/部署域，交叉覆盖全部36域。部分域缺少本轮运行证据，分数按旧源码审计保留并标注来源。本轮只读复核，未运行Gradle、未启动或操控游戏。</p>
<p class="sources"><a href="../../logs/beta5-audit-20261025/percentage-audit.json">10月25日原始分项</a><a href="progression-evidence.json">进度证据</a><a href="industry-evidence.json">工业与结构证据</a><a href="runtime-evidence.json">部署与运行证据</a><a href="../../doc/HK3GTL-内测5/09_测试发布/内测5全库完成度与正式版准备审计_20261025.html">10月25日原报告</a></p>
<p>总体分数不作为正式版发布建议。当前已知阻断仍包括实际工业配方可达性、W02–W15/休伯利安/4台MAX复制机、网络注入器重构、完整实机成型与拆除、主世界全结构运行及内存验收等。</p></footer>
<script id="audit-data" type="application/json">{data_json}</script>
<script>
const cards=[...document.querySelectorAll('.system')],search=document.getElementById('search'),group=document.getElementById('group'),order=document.getElementById('order');
function apply(){{const q=search.value.trim().toLowerCase(),g=group.value;let visible=0;for(const c of cards){{const d=c.querySelector('.system-detail').textContent.toLowerCase();const ok=(!q||(c.dataset.search+' '+d).toLowerCase().includes(q))&&(!g||c.dataset.group===g);c.hidden=!ok;if(ok)visible++;}}const list=document.getElementById('systems');const sorted=cards.filter(c=>!c.hidden).sort((a,b)=>{{const av=Number(a.querySelector('.score b').textContent.replace('%','')),bv=Number(b.querySelector('.score b').textContent.replace('%',''));return order.value==='score-desc'?bv-av:order.value==='name'?a.dataset.id.localeCompare(b.dataset.id):av-bv;}});sorted.forEach(c=>list.append(c));document.getElementById('count').textContent=visible+' / '+cards.length+' 个系统';}}
for(const c of cards){{const b=c.querySelector('.system-head'),d=c.querySelector('.system-detail'),ch=c.querySelector('.chevron');b.addEventListener('click',()=>{{const open=d.hidden;d.hidden=!open;b.setAttribute('aria-expanded',String(open));ch.textContent=open?'－':'＋';}});}}
search.addEventListener('input',apply);group.addEventListener('change',apply);order.addEventListener('change',apply);document.getElementById('openAll').addEventListener('click',e=>{{const open=e.currentTarget.dataset.open!=='1';for(const c of cards){{if(c.hidden)continue;const d=c.querySelector('.system-detail'),b=c.querySelector('.system-head');d.hidden=!open;b.setAttribute('aria-expanded',String(open));c.querySelector('.chevron').textContent=open?'－':'＋';}}e.currentTarget.dataset.open=open?'1':'0';e.currentTarget.textContent=open?'收起全部':'展开全部';}});apply();
</script></main></body></html>'''
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "current-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT_DIR / "index.html").write_text(html_page, encoding="utf-8")
    print(json.dumps({"overall_percent": overall, "baseline_percent": baseline["overall"]["earned"],
                      "domains": len(systems), "revised_domains": [s["id"] for s in systems if s["changed"]],
                      "formal_architecture_coverage": summary["multiblock_scope"]["coverage_percent"],
                      "output": str(OUT_DIR / "index.html")}, ensure_ascii=False))


if __name__ == "__main__":
    build()
