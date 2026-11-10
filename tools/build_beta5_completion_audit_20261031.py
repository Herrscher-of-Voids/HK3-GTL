# -*- coding: utf-8 -*-
"""基于10月30日快照，仅用两系统完整验收回执刷新完成度审计。"""
from __future__ import annotations

import copy
from datetime import datetime
import hashlib
import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXED_DIR = ROOT / "logs/beta5-completion-audit-20261030"
PREVIOUS = FIXED_DIR / "summary-20261030.json"
HISTORY_HTML = FIXED_DIR / "index-20261030.html"
COMPLETION = ROOT / "logs/two-systems-completion-20261031/completion.json"
OUT_DIR = ROOT / "logs/beta5-completion-audit-20261031"
OUT_JSON = OUT_DIR / "current-summary.json"
OUT_HTML = OUT_DIR / "index.html"

TARGETS = {
    "N11": {
        "capability": 4,
        "claim": "个人补谈四步仅在服务端接受当前全文的完整阅读回执后推进；回执与玩家、团队事件、动作令牌及当前正文绑定，撤权、重放、换队、重登和旧令牌均拒绝。",
        "reason": "首信服务端现以阅读会话消费动作，完整验收收据决定本项是否可记为完成；旧“可绕过末页”缺陷仅保留为历史对照。",
        "pending_gap": "本轮正式服务链、真实客户端和双客户端门禁尚未全部通过；分值保留10月30日快照。",
        "complete_gap": "本轮100%仅覆盖奥托首信与首次接触，不推广为五方后续内容或其他系统。离线专用测试账户的两个真实客户端由临时程序走公开UI回调，不代表真人输入。",
        "evidence": [
            "src/main/java/com/sirin/hk3gtl/common/communication/Hk3TeamContactService.java",
            "src/main/java/com/sirin/hk3gtl/common/easter/Hk3EggReading.java",
            "logs/two-systems-completion-20261031/completion.json",
        ],
    },
    "all_dimension_height": {
        "capability": 4,
        "claim": "全维度新档高度合同的本轮验收覆盖跨进程冻结、真实客户端高空与光影、双客户端在线，以及Y1007原生GT配方和AE网格的重启持久化。",
        "reason": "完整验收收据必须同时满足高度合同、客户端、光影、双客户端和GT/AE门禁；旧包高空兼容缺口仅保留为历史对照。",
        "pending_gap": "本轮高度合同、真实客户端、光影、双客户端及GT/AE门禁尚未全部通过；分值保留10月30日快照。",
        "complete_gap": "本轮100%只覆盖收据记录的既有世界合同冻结、高空场景、光影、双客户端和Y1007 GT/AE；旧初建不冒充当前SHA新世界初建。离线专用账户、真实客户端程序化UI操作不代表真人输入；不推广到所有光影或全维度全机器。",
        "evidence": [
            "src/main/java/com/sirin/hk3gtl/common/dimension/height/Hk3HeightService.java",
            "logs/two-systems-completion-20261031/completion.json",
        ],
    },
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for data in iter(lambda: stream.read(1 << 20), b""):
            digest.update(data)
    return digest.hexdigest()


def verify_current_binding(value: dict) -> dict:
    """只为两目标系统防止旧100%收据在换包或新隔离安装后被重新采纳。"""
    binding = value.get("artifact_binding", {})
    if not isinstance(binding, dict) or binding.get("passed") is not True:
        raise ValueError("completion当前包绑定未通过")
    out = ROOT / "logs/two-systems-completion-20261031"
    deployment = read_json(out / "deployment.json")
    fixture = read_json(out / "final-fixture-artifacts.json")
    if fixture.get("passed") is not True or fixture.get("status") != "installed":
        raise ValueError("当前隔离安装未完成")
    production_sha = sha256(ROOT / "build/libs/hk3gtl-0.5.0.jar")
    addon_sha = sha256(ROOT / "build/hk3acceptance/production/hk3acceptance-0.0.1.jar")
    if not (production_sha == binding.get("production_sha256") == deployment.get("installed_sha256")
            == fixture.get("sourceSHA") == fixture.get("source_sha256")
            == sha256(Path(deployment["target"]))):
        raise ValueError("当前正式构建/部署/隔离回执SHA不一致")
    if not (addon_sha == binding.get("addon_sha256") == fixture.get("addonSHA") == fixture.get("addon_sha256")):
        raise ValueError("当前附属包与completion/隔离回执SHA不一致")
    installed = fixture.get("installed_at")
    if not isinstance(installed, str) or installed != binding.get("fixture_installed_at"):
        raise ValueError("completion来自旧隔离安装epoch")
    generated_at = datetime.fromisoformat(str(value.get("generated_at", "")).replace("Z", "+00:00"))
    installed_at = datetime.fromisoformat(installed.replace("Z", "+00:00"))
    if generated_at.tzinfo is None or installed_at.tzinfo is None or generated_at < installed_at:
        raise ValueError("completion生成时间早于当前隔离安装或缺少时区")
    names = {"two-systems-production-acceptance-20261031", "two-systems-client-acceptance-20261031",
             "two-systems-pair-leader-20261031", "two-systems-pair-member-20261031"}
    entries = fixture.get("fixtures", [])
    if (not isinstance(entries, list) or len(entries) != 4
            or any(not isinstance(e, dict) for e in entries) or {e.get("name") for e in entries} != names):
        raise ValueError("隔离安装未准确覆盖四fixture")
    for entry in entries:
        targets = entry.get("targets", [])
        if not isinstance(targets, list) or any(not isinstance(target, dict) for target in targets):
            raise ValueError("隔离JAR目标回执格式无效")
        for filename, expected in (("HK3GTL-内测5.jar", production_sha), ("hk3acceptance-0.0.1.jar", addon_sha)):
            path = ROOT / "build" / entry["name"] / "mods" / filename
            matching = [target for target in targets if target.get("path")
                        and Path(target["path"]).resolve() == path.resolve()]
            if len(matching) != 1 or not (expected == matching[0].get("sha256")
                                          == matching[0].get("expected_sha256") == sha256(path)):
                raise ValueError("当前fixture文件与安装回执SHA不一致")
    return {"passed": True, "production_sha256": production_sha, "addon_sha256": addon_sha,
            "fixture_installed_at": installed, "actual_jar_files_rehashed": 11}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def preserve_baseline() -> None:
    """首次刷新前保存原始基线；已有历史快照永不覆盖。"""
    for source, snapshot in ((FIXED_DIR / "index.html", HISTORY_HTML),
                             (FIXED_DIR / "current-summary.json", PREVIOUS)):
        if not snapshot.exists():
            with snapshot.open("xb") as stream:
                stream.write(source.read_bytes())


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def relative_link(path: str) -> str:
    normalized = path.replace("\\", "/")
    if normalized.startswith("logs/"):
        return "../" + normalized.removeprefix("logs/")
    return "../../" + normalized


def completion_systems() -> tuple[dict, dict]:
    receipt = {"path": "logs/two-systems-completion-20261031/completion.json", "exists": COMPLETION.is_file()}
    if not receipt["exists"]:
        receipt["state"] = "验收进行中：尚无completion.json"
        return {}, receipt
    try:
        value = read_json(COMPLETION)
        systems = value.get("systems")
        if not isinstance(systems, dict):
            raise ValueError("systems不是对象")
        binding = verify_current_binding(value)
        receipt.update({"state": "当前SHA与隔离安装epoch已核实；仅采纳passed=true且100%的两目标系统",
                        "generated_at": value.get("generated_at"), "current_artifact_binding": binding})
        return systems, receipt
    except (OSError, UnicodeError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        receipt["state"] = "验收进行中：completion或当前包绑定未通过，保留原分"
        receipt["error"] = str(error)
        return {}, receipt


def receipt_percent(receipts: dict, system_id: str) -> float | None:
    value = receipts.get(system_id)
    if not isinstance(value, dict):
        return None
    percent = value.get("percent")
    if type(percent) not in (int, float):
        return None
    if percent == 100 and value.get("passed") is not True:
        return None
    return float(percent)


def preserve_old_capability(capability: dict) -> None:
    capability.setdefault("old_claim", capability.get("claim", ""))
    capability.setdefault("old_status", capability.get("status", "unknown"))
    capability.setdefault("old_reason", capability.get("reason", ""))


def refresh_target(system: dict, definition: dict, receipt_percent_value: float | None, receipt: dict) -> None:
    caps = system.get("capabilities", [])
    cap_index = definition["capability"]
    if not isinstance(caps, list) or cap_index >= len(caps) or not isinstance(caps[cap_index], dict):
        raise ValueError(f"{system.get('id')}缺少能力项{cap_index + 1}")

    system["previous_percent"] = system["percent"]
    system["completion_percent"] = receipt_percent_value
    system["completion_receipt"] = receipt["path"]
    system.setdefault("previous_baseline_gaps", copy.deepcopy(system.get("baseline_gaps", [])))
    system.setdefault("previous_progression_review", copy.deepcopy(system.get("progression_review")))
    system.setdefault("previous_runtime_review", copy.deepcopy(system.get("runtime_review")))
    capability = caps[cap_index]
    preserve_old_capability(capability)
    capability["claim"] = definition["claim"]
    capability["reason"] = definition["reason"]
    capability["evidence"] = definition["evidence"]
    capability["updated"] = True
    system["progression_review"] = {
        "id": system["id"],
        "comparison": "10月31日当前实现与完整验收收据",
        "current_findings": [definition["claim"]],
        "evidence": definition["evidence"],
    }
    system["runtime_review"] = {
        "id": system["id"],
        "status": "complete" if receipt_percent_value == 100.0 else "acceptance_pending",
        "receipt": receipt["path"],
        "receipt_percent": receipt_percent_value,
    }

    if receipt_percent_value == 100.0:
        capability["status"] = "complete"
        capability["earned"] = capability.get("possible", 1.0)
        system["earned"] = system["possible"]
        system["percent"] = receipt_percent_value
        system["changed"] = True
        system["coverage"] = "10月31日两系统完整验收已通过"
        system["acceptance_status"] = "100%验收完成"
        system["baseline_gaps"] = [definition["complete_gap"]]
    else:
        capability["reason"] += " 本轮完整验收尚未以100%收据确认，因此分值沿用10月30日快照。"
        system["changed"] = False
        system["coverage"] = "10月31日两系统验收进行中；分值沿用10月30日"
        system["acceptance_status"] = "验收进行中"
        system["baseline_gaps"] = [definition["pending_gap"]]


def build_summary() -> dict:
    previous = copy.deepcopy(read_json(PREVIOUS))
    systems = previous.get("systems")
    if not isinstance(systems, list) or len(systems) != 36:
        raise ValueError("10月30日快照必须包含36个系统")
    receipt_systems, receipt = completion_systems()
    by_id = {system.get("id"): system for system in systems if isinstance(system, dict)}
    if set(TARGETS) - set(by_id):
        raise ValueError("10月30日快照缺少目标系统")

    for system_id, definition in TARGETS.items():
        refresh_target(by_id[system_id], definition, receipt_percent(receipt_systems, system_id), receipt)

    overall = sum(float(system["percent"]) for system in systems) / len(systems)
    groups: dict[str, list[float]] = {}
    for system in systems:
        groups.setdefault(system["group"], []).append(float(system["percent"]))
    previous_overall = float(previous["overall_percent"])
    previous["audit_date"] = "2026-10-31"
    previous["previous_audit_date"] = "2026-10-30"
    previous["report_updated_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
    previous["previous_overall_percent"] = previous_overall
    previous["method"] = "36个系统域等权算术平均；仅N11与all_dimension_height在当前实际JAR SHA、部署与隔离安装epoch一致，且completion对应passed=true、percent=100时刷新；其余34域深拷贝10月30日快照。"
    previous["overall_percent"] = overall
    previous["group_summary"] = {group: sum(values) / len(values) for group, values in groups.items()}
    systems.sort(key=lambda system: float(system["percent"]))
    previous["group_summary"] = dict(sorted(previous["group_summary"].items(), key=lambda item: item[1]))
    previous["two_systems_receipt"] = receipt
    previous["two_systems_scope"] = {
        "updated_systems": list(TARGETS),
        "other_systems_carried_forward": 34,
        "fixed_entry": "logs/beta5-completion-audit-20261030/index.html",
        "history": "logs/beta5-completion-audit-20261030/index-20261030.html",
        "history_summary": "logs/beta5-completion-audit-20261030/summary-20261030.json",
        "full_acceptance_report": "logs/two-systems-completion-20261031/index.html",
    }
    return previous


def status_label(capability: dict) -> str:
    earned = float(capability.get("earned", 0))
    possible = float(capability.get("possible", 1))
    return f"{earned / possible * 100 if possible else 0:.0f}%"


def render(summary: dict) -> str:
    systems = summary["systems"]
    receipt = summary["two_systems_receipt"]
    cards = []
    for system in systems:
        capability_rows = []
        for capability in system.get("capabilities", []):
            evidence = " · ".join(
                f'<a href="{esc(relative_link(path))}">{esc(path)}</a>' for path in capability.get("evidence", [])
            )
            historical = ""
            if capability.get("updated"):
                historical = (
                    f'<p class="history">10/30历史：{esc(capability.get("old_claim", ""))} '
                    f'[{esc(capability.get("old_status", "unknown"))}]</p>'
                )
            capability_rows.append(
                f'<tr><td>{esc(capability.get("claim", ""))}{historical}</td>'
                f'<td><span class="status {esc(capability.get("status", "unknown"))}">{esc(status_label(capability))}</span></td>'
                f'<td>{esc(capability.get("reason", ""))}<p class="evidence">{evidence}</p></td></tr>'
            )
        acceptance = system.get("acceptance_status", "10月30日分值沿用")
        prior = system.get("previous_percent", system.get("percent"))
        cards.append(
            f'<article class="system" data-id="{esc(system["id"])}" data-group="{esc(system["group"])}" '
            f'data-search="{esc(system["id"] + " " + system["name"] + " " + system["group"])}">'
            f'<button class="system-head" type="button" aria-expanded="false"><span><small>{esc(system["id"])}</small>{esc(system["name"])}</span>'
            f'<b>{float(system["percent"]):.1f}%</b><i>+</i></button><div class="bar"><span style="width:{float(system["percent"]):.3f}%"></span></div>'
            f'<section class="detail" hidden><p class="coverage">{esc(system.get("coverage", ""))} · {esc(acceptance)}</p>'
            f'<p>10/30分值：{float(prior):.1f}%；当前：{float(system["percent"]):.1f}%</p>'
            f'<table><thead><tr><th>能力项</th><th>状态</th><th>当前依据</th></tr></thead><tbody>{"".join(capability_rows)}</tbody></table></section></article>'
        )
    options = "".join(f'<option value="{esc(group)}">{esc(group)}</option>' for group in summary["group_summary"])
    groups = "".join(
        f'<div class="metric"><span>{esc(group)}</span><b>{percent:.1f}%</b><small>{sum(s["group"] == group for s in systems)}个系统</small></div>'
        for group, percent in summary["group_summary"].items()
    )
    data = json.dumps(summary, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>HK3GTL实时完成度 · 低→高 · 固定入口</title><style>
:root{{color-scheme:dark;--bg:#111a20;--panel:#17262d;--line:#38505a;--text:#e6eff1;--muted:#9eafb5;--cyan:#60d4c6;--lime:#c4de77;--amber:#f1c46b;--red:#f08076}}*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.55 system-ui,"Microsoft YaHei",sans-serif}}main{{max-width:1280px;margin:auto;padding:30px 20px 56px}}h1{{font-size:26px;margin:0 0 5px}}h2{{font-size:19px;margin:28px 0 10px}}a{{color:var(--cyan);overflow-wrap:anywhere}}.muted,small{{color:var(--muted)}}.notice{{border-left:3px solid var(--amber);background:#222b2a;padding:12px 15px;margin:16px 0}}.metrics{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}}.metric{{background:var(--panel);border:1px solid var(--line);padding:13px;border-radius:5px}}.metric span,.metric small{{display:block;color:var(--muted)}}.metric b{{display:block;color:var(--lime);font-size:22px}}.controls{{display:flex;gap:8px;flex-wrap:wrap;margin:14px 0;position:sticky;top:0;padding:8px 0;background:var(--bg);z-index:1}}input,select,button{{font:inherit;color:var(--text);background:#192a31;border:1px solid var(--line);border-radius:4px;padding:8px 10px}}input{{flex:1;min-width:240px}}button{{cursor:pointer}}.count{{align-self:center;color:var(--muted)}}.systems{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px;align-items:start}}.system{{background:#152229;border:1px solid var(--line);border-radius:5px;overflow:hidden}}.system[hidden]{{display:none}}.system-head{{display:grid;grid-template-columns:1fr auto 18px;gap:8px;align-items:center;width:100%;border:0;border-radius:0;text-align:left;background:transparent}}.system-head small{{display:inline-block;color:var(--cyan);font:12px ui-monospace,monospace;width:84px}}.system-head b{{color:var(--lime);font-size:18px}}.system-head i{{font-style:normal;color:var(--cyan);font-size:19px}}.bar{{height:3px;background:#293a41}}.bar span{{display:block;height:100%;background:var(--cyan)}}.detail{{padding:10px 12px 14px;border-top:1px solid var(--line)}}.detail[hidden]{{display:none}}.coverage{{color:var(--amber);font-size:12px}}table{{border-collapse:collapse;width:100%;font-size:12px}}th,td{{border-bottom:1px solid #31464e;text-align:left;vertical-align:top;padding:7px}}th{{color:var(--muted)}}td:first-child{{width:30%}}td:nth-child(2){{width:12%;white-space:nowrap}}.status{{border:1px solid currentColor;border-radius:3px;padding:2px 5px}}.status.complete{{color:var(--lime)}}.status.partial{{color:var(--amber)}}.status.missing{{color:var(--red)}}.status.unknown{{color:var(--cyan)}}.history{{color:var(--muted);font-size:11px;margin:5px 0 0}}.evidence{{font-size:11px;margin:6px 0 0}}footer{{border-top:1px solid var(--line);margin-top:30px;padding-top:14px;color:var(--muted);font-size:13px}}@media(max-width:800px){{.metrics,.systems{{grid-template-columns:1fr}}}}@media(max-width:480px){{main{{padding:20px 12px}}input{{min-width:100%}}.system-head small{{width:58px}}}}
</style></head><body><main><p class="muted">HK3GTL · 36系统等权审计 · 当前更新时间：{esc(summary["report_updated_at"])}</p><h1>实时完成度 · 低→高 · 固定入口</h1><p>请持续使用 <a href="../beta5-completion-audit-20261030/index.html">固定实时入口</a>；每次运行生成器刷新，目录日期仅为固定地址。当前验收批次为2026-10-31，历史基线为2026-10-30。本页深拷贝10月30日的36系统快照。除N11与全维度高度外，其余34项的分值、能力与证据均未重审或改写。</p><div class="notice"><b>{esc(receipt["state"])}</b>。只有 <code>completion.json</code> 中对应系统的 <code>percent</code> 严格为100，才允许本页更新该系统分值；否则沿用10月30日原值。</div><section class="metrics"><div class="metric"><span>当前总完成度</span><b>{summary["overall_percent"]:.1f}%</b><small>36系统等权</small></div><div class="metric"><span>10/30基线</span><b>{summary["previous_overall_percent"]:.1f}%</b><small>仅两系统可变化</small></div><div class="metric"><span>本轮系统</span><b>2</b><small>N11与全维度高度</small></div><div class="metric"><span>历史沿用</span><b>34</b><small>未重新验收</small></div></section><h2>分组平均</h2><section class="metrics">{groups}</section><h2>系统列表 · 完成度从低到高</h2><div class="controls"><input id="search" type="search" placeholder="搜索系统、编号、依据" aria-label="搜索"><select id="group"><option value="">全部分组</option>{options}</select><button id="toggle" type="button">展开全部</button><span id="count" class="count"></span></div><section id="systems" class="systems">{"".join(cards)}</section><footer><p><a href="{esc(relative_link(summary["two_systems_scope"]["history"]))}">10/30历史审计快照</a> · <a href="{esc(relative_link(summary["two_systems_scope"]["history_summary"]))}">10/30历史摘要</a> · <a href="../two-systems-completion-20261031/index.html">本轮两系统完整验收报告</a> · <a href="current-summary.json">本页机器可读摘要</a></p><p>本页不把历史漏洞叙述当作当前事实；历史对照仅在两个已刷新能力项展开后显示。完整验收边界以本轮收据为准。</p></footer><script id="audit-data" type="application/json">{data}</script><script>const cards=[...document.querySelectorAll('.system')],search=document.querySelector('#search'),group=document.querySelector('#group'),count=document.querySelector('#count');function apply(){{let shown=0,q=search.value.trim().toLowerCase();for(const card of cards){{let ok=(!q||card.textContent.toLowerCase().includes(q))&&(!group.value||card.dataset.group===group.value);card.hidden=!ok;if(ok)shown++}}count.textContent=`${{shown}} / ${{cards.length}} 个系统`}}for(const card of cards){{let button=card.querySelector('.system-head'),detail=card.querySelector('.detail'),mark=button.querySelector('i');button.onclick=()=>{{let open=detail.hidden;detail.hidden=!open;button.setAttribute('aria-expanded',String(open));mark.textContent=open?'−':'+'}}}}search.oninput=apply;group.onchange=apply;document.querySelector('#toggle').onclick=e=>{{let open=e.currentTarget.dataset.open!=='1';for(const card of cards){{if(card.hidden)continue;let detail=card.querySelector('.detail'),button=card.querySelector('.system-head');detail.hidden=!open;button.setAttribute('aria-expanded',String(open));button.querySelector('i').textContent=open?'−':'+'}}e.currentTarget.dataset.open=open?'1':'0';e.currentTarget.textContent=open?'收起全部':'展开全部'}};apply();</script></main></body></html>'''


def main() -> None:
    # 【变更记录 #4】2026-11-01 00:30:26（报告工具，不增加生产修订）
    # 新增五方交流专项优先路由；严格验收聚合存在后才接管固定页，历史生成器保留回退。
    communication = ROOT / "logs/communication-completion-20261101/build_report.py"
    if communication.is_file() and (communication.parent / "completion.json").is_file():
        import runpy
        import sys
        original_arguments = sys.argv
        try:
            sys.argv = [str(communication), "--publish-fixed"]
            runpy.run_path(str(communication), run_name="__main__")
        finally:
            sys.argv = original_arguments
        return
    # 【变更记录 #3】2026-10-31 22:06:09（内测5修订191）
    # 新增手机专项冻结基线优先路由；保留总览及更早回退，避免旧生成器覆盖本轮报告。
    phone = ROOT / "logs/phone-completion-20261031/build_report.py"
    if phone.is_file() and (phone.parent / "before/current-summary.json").is_file():
        import runpy
        runpy.run_path(str(phone), run_name="__main__")
        return
    # 本轮冻结快照存在时，文明机器总览生成器拥有固定报告入口。
    overview = ROOT / "logs/machine-overview-completion-20261031/build_report.py"
    if overview.is_file() and (overview.parent / "before/current-summary.json").is_file():
        import runpy
        runpy.run_path(str(overview), run_name="__main__")
        return
    # 【变更记录 #2】2026-10-31 17:57:00（内测5修订189）
    # 删除本轮对欢迎旧基线的刷新；新增工具导出冻结快照优先路由，仅其生成器可修改实时报告。
    tools_export = ROOT / "logs/tools-export-completion-20261031/build_report.py"
    if tools_export.is_file() and (tools_export.parent / "before/current-summary.json").is_file():
        import runpy
        runpy.run_path(str(tools_export), run_name="__main__")
        return
    # The two-system receipt remains a historical r187 acceptance.  Once the
    # welcome round has a frozen baseline, its generator owns the live entry.
    welcome = ROOT / "logs/welcome-completion-20261031/build_report.py"
    before = welcome.parent / "before/current-summary.json"
    if welcome.is_file() and before.is_file():
        import runpy
        runpy.run_path(str(welcome), run_name="__main__")
        return
    preserve_baseline()
    summary = build_summary()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summary_text = json.dumps(summary, ensure_ascii=False, indent=2) + "\n"
    page = render(summary)
    for directory in (FIXED_DIR, OUT_DIR):
        (directory / "current-summary.json").write_text(summary_text, encoding="utf-8")
        (directory / "index.html").write_text(page, encoding="utf-8")
    print(json.dumps({"output": str(FIXED_DIR / "index.html"), "dated_output": str(OUT_HTML),
                      "overall_percent": summary["overall_percent"],
                      "receipt": summary["two_systems_receipt"], "updated": list(TARGETS)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
