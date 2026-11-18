import json
import re
import shutil
from datetime import datetime
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "logs/beta5-completion-audit-20261030"
LOG = ROOT / "logs/industrial-datagen-r269-20261113"
RECEIPT = "logs/industrial-datagen-r269-20261113/completion.json"
LINK = "../industrial-datagen-r269-20261113/completion.json"
SYSTEM_IDS = ("ae_optimization", "components", "industrial_lines")


def element_span(page, tag, element_id):
    opening = re.search(rf'<{tag}\b[^>]*\bid="{re.escape(element_id)}"[^>]*>', page)
    depth = 0
    for token in re.finditer(rf'</?{tag}\b[^>]*>', page[opening.start():]):
        depth += -1 if token.group().startswith("</") else 1
        if depth == 0:
            return opening.start(), opening.start() + token.end()


def replace_element(page, tag, element_id, replacement):
    start, end = element_span(page, tag, element_id)
    return page[:start] + replacement + page[end:]


def main():
    completion = json.loads((ROOT / RECEIPT).read_text("utf-8"))
    now = datetime.now().astimezone()
    stamp = now.isoformat()
    backup = LOG / ("audit-before-" + now.strftime("%Y%m%d-%H%M%S-%f"))
    backup.mkdir(parents=True)
    for name in ("index.html", "current-summary.json"):
        shutil.copy2(AUDIT / name, backup / name)
    summary = json.loads((backup / "current-summary.json").read_text("utf-8"))
    page = (backup / "index.html").read_text("utf-8")

    for system in summary["systems"]:
        system_id = system["id"]
        if system_id in SYSTEM_IDS:
            review = completion["reviews"][system_id]
            system["industrial_datagen_r269_review"] = {
                "updated_at": stamp,
                "implemented": review["implemented"],
                "remaining": review["remaining"],
                "evidence": RECEIPT,
                "development_score_unchanged": True,
                "original_acceptance_score_unchanged": True,
                "runtime_pass_claim_added": False,
            }
            system["development_metric"].update(
                remaining_development=review["remaining"],
                evidence_updated_at=stamp,
                evidence_review_receipt=RECEIPT,
            )
            system["updated_at"] = stamp

    summary["industrial_datagen_r269_receipt"] = RECEIPT
    summary["industrial_datagen_r269_completion"] = completion
    summary["industrial_datagen_r269_review"] = {
        "updated_at": stamp,
        "reviewed_domains": list(SYSTEM_IDS),
        "previous_audit": (backup / "current-summary.json").relative_to(ROOT).as_posix(),
        "development_score_unchanged": True,
        "original_acceptance_score_unchanged": True,
        "runtime_pass_claim_added": False,
    }
    summary["report_updated_at"] = summary["updated_at"] = stamp

    page = page.replace(
        "<h2>当前工业链与研究补齐 · R268</h2>",
        "<h2>历史工业链与研究补齐 · R268（当前数据生成状态见R269）</h2>",
        1,
    )
    page = page.replace(
        "R268实现增量及既有证据复核；仅研发口径变动，原验收记录保持。",
        "历史R268实现增量及既有证据复核；分数保留，当前数据生成状态见R269。",
        1,
    )
    backup_link = "../" + backup.relative_to(ROOT / "logs").as_posix() + "/index.html"
    notice = (
        '<section class="notice" id="industrial-datagen-r269-current"><h2>当前配方生成、客户端兼容与最终注册复核 · R269–R271</h2>'
        f'<p>{escape(completion["status"])}</p>'
        '<p>本次更新实现、进档及最终配方注册证据；37域原验收、研发分值、各能力分母及23项移交保持。'
        'R268受阻的运行记录保留为历史，不将离线数据生成等同于游戏成型、实际生产或性能验收。</p>'
        f'<p>更新：{stamp} · <a href="{LINK}">当前运行、输出及剩余差距</a> · '
        f'<a href="{backup_link}">修改前真实页面</a></p></section>'
    )
    if 'id="industrial-datagen-r269-current"' in page:
        page = replace_element(page, "section", "industrial-datagen-r269-current", notice)
    else:
        start, _ = element_span(page, "section", "industrial-finish-r268-current")
        page = page[:start] + notice + page[start:]

    for system_id in SYSTEM_IDS:
        review = completion["reviews"][system_id]
        start, end = element_span(page, "details", "system-" + system_id)
        card = page[start:end]
        current_review = (
            f'<section class="notice" id="industrial-datagen-r269-{system_id}"><h3>当前实现、兼容与导出证据 · R269–R271</h3>'
            f'<p>{escape(review["implemented"])}</p>'
            f'<p><b>当前研发缺口：</b>{escape(review["remaining"])}</p>'
            f'<p>更新：{stamp} · 分数及分母保持 · <a href="{LINK}">当前回执</a></p></section>'
        )
        if f'id="industrial-datagen-r269-{system_id}"' in card:
            card = replace_element(card, "section", "industrial-datagen-r269-" + system_id, current_review)
        else:
            card = card.replace("</summary>", "</summary>" + current_review, 1)
        card = card.replace("<h3>当前研发复核 · R268</h3>", "<h3>历史研发复核 · R268（当前证据见R269）</h3>", 1)
        page = page[:start] + card + page[end:]

    payload = json.dumps(summary, ensure_ascii=False, indent=2).replace("<", "\\u003c")
    page = replace_element(page, "script", "audit-data", '<script type="application/json" id="audit-data">' + payload + "</script>")
    (AUDIT / "current-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", "utf-8")
    (AUDIT / "index.html").write_text(page, "utf-8")
    publication = {
        "updated_at": stamp,
        "completion_receipt": RECEIPT,
        "backup": backup.relative_to(ROOT).as_posix(),
        "reviewed_domains": list(SYSTEM_IDS),
        "development_percent": summary["development_metric"]["overall_percent"],
        "acceptance_percent": summary["overall_percent"],
        "domain_count": summary["domain_count"],
        "excluded_capability_count": summary["development_metric"]["excluded_capability_count"],
        "score_changed": False,
        "runtime_pass_claim_added": False,
    }
    (LOG / "audit-publication.json").write_text(json.dumps(publication, ensure_ascii=False, indent=2) + "\n", "utf-8")
    print(json.dumps(publication, ensure_ascii=False))


if __name__ == "__main__":
    main()
