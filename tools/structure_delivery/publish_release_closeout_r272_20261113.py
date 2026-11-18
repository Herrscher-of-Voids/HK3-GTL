import json
import re
import shutil
from collections import defaultdict
from datetime import datetime
from html import escape
from pathlib import Path
from zoneinfo import ZoneInfo

from publish_industrial_datagen_r269_20261113 import element_span, replace_element


ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "logs/beta5-completion-audit-20261030"
OUT = ROOT / "logs/release-closeout-r272-20261113"
RECEIPT = "logs/release-closeout-r272-20261113/completion.json"
LINK = "../release-closeout-r272-20261113/completion.json"


def main():
    completion = json.loads((ROOT / RECEIPT).read_text("utf8"))
    revision = completion["revision"]
    label = "R272–R" + str(revision) if revision != 272 else "R272"
    now = datetime.now(ZoneInfo("America/New_York"))
    stamp = now.isoformat()
    backup = OUT / ("audit-before-" + now.strftime("%Y%m%d-%H%M%S-%f"))
    backup.mkdir(parents=True)
    for name in ("index.html", "current-summary.json"):
        shutil.copy2(AUDIT / name, backup / name)
    summary = json.loads((backup / "current-summary.json").read_text("utf8"))
    page = (backup / "index.html").read_text("utf8")
    previous = summary["development_metric"]["overall_percent"]
    reviews = completion["reviews"]
    for system in summary["systems"]:
        if system["id"] not in reviews:
            continue
        review = reviews[system["id"]]
        metric = system["development_metric"]
        credits = {item["capability_index"]: item for item in metric.get("capability_credits", [])}
        credits.update({item["capability_index"]: item for item in review.get("credits", [])})
        metric["capability_credits"] = list(credits.values())
        metric["earned"] = sum(credits[i]["earned"] if i in credits else capability["earned"]
            for i, capability in enumerate(system["capabilities"])
            if i not in metric["excluded_capability_indices"])
        metric.update(percent=metric["earned"] / metric["possible"] * 100,
            updated_at=stamp, remaining_development=review["remaining"],
            evidence_updated_at=stamp, evidence_review_receipt=RECEIPT)
        system["release_closeout_r272_review"] = dict(review, updated_at=stamp, evidence=RECEIPT)
        system["updated_at"] = stamp
    summary["systems"].sort(key=lambda item: item["development_metric"]["percent"])
    groups = defaultdict(list)
    for system in summary["systems"]:
        groups[system["group"]].append(system["development_metric"]["percent"])
    current = sum(system["development_metric"]["percent"] for system in summary["systems"]) / summary["domain_count"]
    summary["primary_metric"]["percent"] = current
    completed = sum(system["development_metric"]["percent"] == 100 for system in summary["systems"])
    summary["development_metric"].update(overall_percent=current, completed_domains=completed,
        incomplete_domains=summary["domain_count"] - completed,
        group_summary={name: sum(values) / len(values) for name, values in groups.items()},
        previous_development_percent=previous, implementation_delta_percentage_points=current - previous,
        delta_percentage_points=current - summary["overall_percent"], updated_at=stamp,
        changed_domains=list(reviews), implementation_receipt=RECEIPT)
    summary["release_closeout_r272_completion"] = completion
    client = json.loads((ROOT / completion["client_receipt"]).read_text("utf8"))
    summary["current_environment"] = dict(checked_at=stamp, pack_version="3.6", minecraft="1.20.1",
        forge="47.4.16", hk3gtl_revision=revision, runtime_revalidated=True, client_runtime_revalidated=True,
        scope=client["scope"], evidence=completion["client_receipt"],
        history=summary["current_environment"])
    summary["target_instance"] = dict(version="GTL增强版3.6", revision=revision, installed=True,
        game_directory=summary["target_instance"]["game_directory"], updated_at=stamp,
        version_source="负责人确认增强版3.6；本轮实际客户端进档及最终配方注册回读。",
        evidence=completion["installation"]["receipt"], game_verified=False,
        client_compatibility_verified=True, runtime_memory_acceptance=False, terminal_dismantle_acceptance=False,
        game_verification_scope=client["scope"], history=summary["target_instance"])
    summary["report_updated_at"] = summary["updated_at"] = stamp
    backup_link = "../" + backup.relative_to(ROOT / "logs").as_posix() + "/index.html"
    notice = (f'<section id="offline-maximize-current"><h2>发布前接线、能源预算与回收收尾 · {label}</h2>'
        '<section class="metrics">'
        f'<div>研发完成度 · 37域等权<b>{current:.2f}%</b></div>'
        f'<div>本轮研发变动<b>{current - previous:+.2f}个百分点</b></div>'
        f'<div>研发满分系统<b>{completed} / 37</b></div>'
        f'<div>原验收完成度 · 保留<b>{summary["overall_percent"]:.2f}%</b></div></section>'
        f'<p>{escape(completion["status"])}</p>'
        '<p>37域、各能力分母及23项历史计分排除记录保持；发布前实机、联机与性能测试已取消，研发完成后由负责人发布，问题按玩家反馈修复。</p>'
        f'<p>更新：{stamp} · <a href="{LINK}">构建、安装与剩余差距</a> · '
        f'<a href="{backup_link}">修改前真实页面</a></p></section>')
    start, end = element_span(page, "section", "offline-maximize-current")
    page = page[:start] + page[end:]
    page = page.replace("<main>", "<main>" + notice, 1)
    page = page.replace(
        "<h2>当前配方生成、客户端兼容与最终注册复核 · R269–R271</h2>",
        f"<h2>历史配方生成、客户端兼容与最终注册复核 · R269–R271（当前状态见{label}）</h2>", 1)
    start, end = element_span(page, "section", "unfinished-20261111")
    history = page[start:end].replace("当前22个研发未满分系统", "历史未完成系统快照（2026-11-11）", 1)
    history = history.replace("</h2>", f"</h2><p>以下分数与操作安排仅保留当时记录；当前状态见{label}复核。</p>", 1)
    page = page[:start] + history + page[end:]
    for system in summary["systems"]:
        if system["id"] not in reviews:
            continue
        review = reviews[system["id"]]
        metric = system["development_metric"]
        start, end = element_span(page, "details", "system-" + system["id"])
        card = page[start:end]
        card = re.sub(r"(<summary>.*?<strong>).*?(</strong>)",
            lambda match: match[1] + f'研发 {metric["percent"]:.2f}% · 原验收 {system["percent"]:.2f}%' + match[2], card, count=1, flags=re.S)
        scope = ('<p class="notice development-scope">'
            f'研发：{metric["earned"]:g}/{metric["possible"]:g}（{metric["percent"]:.2f}%）；'
            f'原验收：{system["earned"]:g}/{system["possible"]:g}（{system["percent"]:.2f}%）。'
            '原能力表保留验收历史；本轮实现与注册证据见当前复核。</p>')
        card = re.sub(r'<p class="notice development-scope">.*?</p>', lambda match: scope, card, count=1, flags=re.S)
        card = re.sub(r'(<div class="bar"><i style="width:)[^%]+(%")',
            lambda match: match[1] + str(metric["percent"]) + match[2], card, count=1)
        section_id = "release-closeout-r272-" + system["id"]
        note = (f'<section class="notice" id="{section_id}"><h3>当前发布前复核 · {label}</h3>'
            f'<p>{escape(review["implemented"])}</p><p><b>剩余：</b>{escape(review["remaining"])}</p>'
            f'<p><a href="{LINK}">当前证据与回执</a> · {stamp}</p></section>')
        if f'id="{section_id}"' in card:
            card = replace_element(card, "section", section_id, note)
        else:
            card = card.replace("</summary>", "</summary>" + note, 1)
        page = page[:start] + card + page[end:]
    spans = {system["id"]: element_span(page, "details", "system-" + system["id"])
        for system in summary["systems"]}
    cards = {system_id: page[start:end] for system_id, (start, end) in spans.items()}
    start = min(start for start, _ in spans.values())
    end = max(end for _, end in spans.values())
    page = page[:start] + "".join(cards[system["id"]] for system in summary["systems"]) + page[end:]
    page = page.replace("原验收完成度从低到高，同分保留原序", "研发完成度从低到高，同分保留原序", 1)
    payload = json.dumps(summary, ensure_ascii=False, indent=2).replace("<", "\\u003c")
    page = replace_element(page, "script", "audit-data", '<script type="application/json" id="audit-data">' + payload + '</script>')
    (AUDIT / "current-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", "utf8")
    (AUDIT / "index.html").write_text(page, "utf8")
    publication = dict(updated_at=stamp, receipt=RECEIPT, backup=backup.relative_to(ROOT).as_posix(),
        development_percent=current, previous_development_percent=previous,
        acceptance_percent=summary["overall_percent"], domain_count=summary["domain_count"],
        excluded_runtime_items=summary["development_metric"]["excluded_capability_count"])
    (OUT / "audit-publication.json").write_text(json.dumps(publication, ensure_ascii=False, indent=2) + "\n", "utf8")
    print(json.dumps(publication, ensure_ascii=False))


if __name__ == "__main__":
    main()
