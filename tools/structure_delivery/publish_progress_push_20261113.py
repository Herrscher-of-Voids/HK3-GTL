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
OUT = ROOT / "logs/progress-push-20261113"
RECEIPT = "logs/progress-push-20261113/completion.json"
LINK = "../progress-push-20261113/completion.json"


def main(OUT=OUT, RECEIPT=RECEIPT, LINK=LINK,
         publication_key="progress_push_20261113_completion", review_key="progress_push_20261113_review",
         work_name="能源工况、双能源与彩蛋接线", extra_links=""):
    completion = json.loads((ROOT / RECEIPT).read_text("utf8"))
    now = datetime.now(ZoneInfo("Asia/Hong_Kong"))
    stamp = now.isoformat()
    backup = OUT / ("audit-before-" + now.strftime("%Y%m%d-%H%M%S-%f"))
    backup.mkdir(parents=True)
    for name in ("index.html", "current-summary.json"):
        shutil.copy2(AUDIT / name, backup / name)
    summary = json.loads((backup / "current-summary.json").read_text("utf8"))
    page = (backup / "index.html").read_text("utf8")
    previous = summary["development_metric"]["overall_percent"]
    for system in summary["systems"]:
        review = completion["reviews"].get(system["id"])
        if review is None:
            continue
        metric = system["development_metric"]
        credits = {row["capability_index"]: row for row in metric.get("capability_credits", [])}
        for credit in review.get("credits", []):
            credits[credit["capability_index"]] = dict(credit, evidence=RECEIPT)
        metric["capability_credits"] = list(credits.values())
        metric["earned"] = sum(credits[i]["earned"] if i in credits else capability["earned"]
            for i, capability in enumerate(system["capabilities"])
            if i not in metric["excluded_capability_indices"])
        metric.update(percent=metric["earned"] / metric["possible"] * 100,
            remaining_development=review["remaining"], updated_at=stamp,
            evidence_updated_at=stamp, evidence_review_receipt=RECEIPT)
        system[review_key] = dict(review, updated_at=stamp, evidence=RECEIPT)
        system["updated_at"] = stamp
        start, end = element_span(page, "details", "system-" + system["id"])
        card = page[start:end]
        card = re.sub(r"(<summary>.*?<strong>).*?(</strong>)",
            lambda m: m[1] + f'研发 {metric["percent"]:.2f}% · 原验收 {system["percent"]:.2f}%' + m[2], card, count=1, flags=re.S)
        scope = (f'<p class="notice development-scope">研发：{metric["earned"]:g}/{metric["possible"]:g}'
            f'（{metric["percent"]:.2f}%）；原验收：{system["earned"]:g}/{system["possible"]:g}'
            f'（{system["percent"]:.2f}%）。原能力表保留历史，本轮实现见当前复核。</p>')
        card = re.sub(r'<p class="notice development-scope">.*?</p>', lambda m: scope, card, count=1, flags=re.S)
        card = re.sub(r'(<div class="bar"><i style="width:)[^%]+(%")',
            lambda m: m[1] + str(metric["percent"]) + m[2], card, count=1)
        note = (f'<section class="notice"><h3>2026-11-13 · 仓库研发推进</h3>'
            f'<p>{escape(review["implemented"])}</p><p><b>剩余：</b>{escape(review["remaining"])}</p>'
            f'<p><a href="{LINK}">实现与构建回执</a> · {stamp}</p></section>')
        card = card.replace("</summary>", "</summary>" + note, 1)
        page = page[:start] + card + page[end:]
    summary["systems"].sort(key=lambda s: s["development_metric"]["percent"])
    groups = defaultdict(list)
    for system in summary["systems"]:
        groups[system["group"]].append(system["development_metric"]["percent"])
    current = sum(s["development_metric"]["percent"] for s in summary["systems"]) / summary["domain_count"]
    completed = sum(s["development_metric"]["percent"] == 100 for s in summary["systems"])
    summary["development_metric"].update(overall_percent=current, completed_domains=completed,
        incomplete_domains=summary["domain_count"] - completed,
        group_summary={k: sum(v) / len(v) for k, v in groups.items()},
        previous_development_percent=previous, implementation_delta_percentage_points=current - previous,
        delta_percentage_points=current - summary["overall_percent"], updated_at=stamp,
        changed_domains=list(completion["reviews"]), implementation_receipt=RECEIPT)
    summary["primary_metric"]["percent"] = current
    summary[publication_key] = completion
    summary["repository_candidate"] = completion["artifact"]
    summary["current_work"] = dict(system=work_name, state=completion["status"],
        scope="仓库开发、构建与隔离数据生成；未操作游戏、桌面、活动实例或存档，未安装候选。",
        remaining=completion["remaining_project_gaps"], evidence=RECEIPT)
    summary["report_updated_at"] = summary["updated_at"] = stamp
    rows = "".join(f'<li>{escape(s["name"])}：{s["development_metric"]["percent"]:.2f}%</li>'
        for s in summary["systems"] if s["development_metric"]["percent"] < 100)
    history = "../" + backup.relative_to(ROOT / "logs").as_posix() + "/index.html"
    notice = (f'<section id="offline-maximize-current"><h2>仓库研发推进 · 2026-11-13</h2>'
        f'<section class="metrics"><div>研发完成度 · 37域等权<b>{current:.2f}%</b></div>'
        f'<div>本轮增量<b>{current - previous:+.2f}个百分点</b></div>'
        f'<div>研发满分系统<b>{completed} / 37</b></div>'
        f'<div>原验收完成度 · 保留<b>{summary["overall_percent"]:.2f}%</b></div></section>'
        f'<p>{escape(completion["status"])}</p><p>固定37域、原能力分母及23项历史计分排除记录保持；发布前实机、联机与性能测试已取消，研发完成后由负责人发布，问题按玩家反馈修复。'
        '未安装，隔离配方生成与构建不计实机成型、运行或性能通过。</p>'
        f'<p><a href="{LINK}">本轮实现与剩余缺项</a> · <a href="{history}">修改前历史</a> · {stamp}</p>{extra_links}'
        f'<details><summary>当前{summary["domain_count"] - completed}个研发未满分系统</summary><ol>{rows}</ol></details></section>')
    page = replace_element(page, "section", "offline-maximize-current", notice)
    spans = {s["id"]: element_span(page, "details", "system-" + s["id"]) for s in summary["systems"]}
    cards = {key: page[start:end] for key, (start, end) in spans.items()}
    start = min(a for a, _ in spans.values())
    end = max(b for _, b in spans.values())
    page = page[:start] + "".join(cards[s["id"]] for s in summary["systems"]) + page[end:]
    payload = json.dumps(summary, ensure_ascii=False, indent=2).replace("<", "\\u003c")
    page = replace_element(page, "script", "audit-data", '<script type="application/json" id="audit-data">' + payload + '</script>')
    (AUDIT / "current-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", "utf8")
    (AUDIT / "index.html").write_text(page, "utf8")
    publication = dict(updated_at=stamp, backup=backup.relative_to(ROOT).as_posix(),
        development_percent=current, previous_development_percent=previous, completed_domains=completed,
        acceptance_percent=summary["overall_percent"], domain_count=summary["domain_count"],
        excluded_runtime_items=summary["development_metric"]["excluded_capability_count"])
    (OUT / "audit-publication.json").write_text(json.dumps(publication, ensure_ascii=False, indent=2) + "\n", "utf8")
    print(json.dumps(publication, ensure_ascii=False))


if __name__ == "__main__":
    main()
