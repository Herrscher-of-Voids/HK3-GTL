import json
import re
import shutil
from collections import defaultdict
from datetime import datetime
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "logs/beta5-completion-audit-20261030"
LOG = ROOT / "logs/industrial-finish-r268-20261113"
RECEIPT = "logs/industrial-finish-r268-20261113/completion.json"
LINK = "../industrial-finish-r268-20261113/completion.json"

REVIEWS = {
    "ae_optimization": (
        "R268补齐世界泡资源与奖励对普通ME样板总成、超级样板总成及绑定代理的输出、标脏和ticker唤醒。"
        "另修正GTL成功开工后未清除失败状态的生命周期缺口；只在WORKING清理，真实失败分支保留。",
        "ME真实网络回流、缓冲重载及历史IDLE红字仍待负责人客户端回归；新增Mixin实际应用尚未验证，"
        "本轮不增加AE原验收或研发分，不把构建成功当作客户端通过。",
    ),
    "research": (
        "R268新增15档I02电路样本解析和15档I08固定白名单重构工艺。解析要求RN-RCA及本档正常制造技术，"
        "仅在真实成功输出后登记解析事实；重构读取派生许可、保留非消耗仿制理之核心。"
        "现有OPR三类实际回收回执与LAB-OPR付费复核不是本轮首次实现，本轮补齐其依赖图。"
        "W13注册身份和研究服务已有，完整建筑仍缺。",
        "W13完整建筑蓝图、其余高阶工程与世界泡资源目录事实仍未全部闭合；"
        "实际加载、成型、运行与对照验证移交负责人，原验收保持。",
    ),
    "N02": (
        "R267已有I25–I31任务托管、真实结算、发现奖励及同队事实提供者，本轮补记已有实现证据；"
        "R268补齐ME输出与执行唤醒，不能据此把整条世界泡执行链称为首次实现。"
        "任务、奖励与研究事实按真实作业结算连接，未用持有物品代替生产回执。",
        "批准资源roots与当前生效注册／配方目录实证仍缺；外部库存和SavedData的跨文件原子提交仍只部分实现。"
        "资源目录能力维持0分、跨文件原子能力维持半分，真实运行与恢复验收移交负责人。",
    ),
    "N16": (
        "R267已有真实舰图交付来源、舰载供能工程与工程事实提供者，本轮核对后补计研发分；"
        "完整舰体检查与工程运行保持分离，只有真实工程结算才能提供工程事实。"
        "R268接口输出／唤醒补齐不代表舰体、舰图和工程体系本轮首次实现。",
        "舰载移动与跨界能力仍未实现；各朝向完整搭建、供能、工艺运行和长期性能仍由负责人实测。"
        "完整舰体成型不能替代移动、跨界或最终工程验收。",
    ),
    "experiments": (
        "现有OPR三类不同生产Batch回执、LAB-OPR托管付费复核及RN-OPR实验事实本轮核对纠正，"
        "不再列作没有合同；正式研究仍须另付费执行工单，不擅自增加节料倍率。"
        "R267世界泡／舰载／奇观真实生产回执及工程事实提供者已有，本轮补记；"
        "R268另新增RCA样本解析与重构，侵蚀模块正常制造来源沿用R267。",
        "W06–W15十座完整奇观蓝图仍缺，W13完整建筑未接；其余高阶真实工况、"
        "逐槽实际来源追踪与物料／资金跨系统原子提交仍有缺口，不能以源码或批次规格冒充实机证据。",
    ),
    "industrial_lines": (
        "当前322条普通工业计划加17条奇观／舰载计划，合计339条；70个主控具有正常制造来源。"
        "R267的309条计划和主控／功能件来源保持历史；R268新增30条RCA解析／重构计划，"
        "并补齐执行输出与唤醒链路。工艺数量不作为完成率。",
        "I37已有完整候选，待外观批准及正式结构接入；W06–W15十座完整蓝图仍缺；"
        "休伯利安移动及跨界未完成。339条计划不等于全部机器均可成型或全部工业链已实际运行通过。",
    ),
    "components": (
        "MAX复杂度配方源码已经存在，不能继续列作尚未编写；本轮核对源码事实，不因此补完成分。",
        "仍缺当前生效payload的完整导出和逐条复杂度对比、全部终局消费者与自然供料闭环。"
        "数据生成当前执行情况以R268回执为准，不把源代码当作有效payload已经生成。",
    ),
    "casings": (
        "R267已解除当前默认结构所用HRV／HDV／CIV机壳的首建自依赖；"
        "批准资源的原建筑形体与配色没有因此被静默替换。",
        "全链自然供料、旧结构配色批准及专用结构材料消费者仍有缺口；"
        "本轮只纠正陈旧首建环文案，保持3.5/5研发分。",
    ),
    "tier_main_materials": (
        "当前默认结构机壳的首建回环已由R267前级制造入口解除，不能继续断言这条旧回环仍阻断所有主材。",
        "首个HBV及后继主材的全链自然供料、批准设备和高阶研究覆盖仍待完整核对；保持56/64研发分。",
    ),
}

CREDITS = {
    "research": {
        6: (1, "new_implementation", "R268新增15档I02真实样本解析和15档I08正式白名单重构，接通正常技术、成功输出事实与派生许可。"),
    },
    "N02": {
        4: (1, "existing_implementation_review", "R267已有I25–I31真实工艺输入、任务托管与结算执行，本轮按源码及回执补计；R268另补ME输出和唤醒。"),
        6: (1, "existing_implementation_review", "R267已有首次发现奖励与图鉴升级的真实作业／产物回执提供者，本轮补计已有实现。"),
        7: (1, "existing_implementation_review", "R267已将同队真实结算、模拟及终止事实接入研究门槛，本轮补计已有实现；不授予未执行事实。"),
    },
    "N16": {
        1: (1, "existing_implementation_review", "R267已有真实舰图交付来源，本轮补计已有实现；不把预览或持有舰图当作工程运行。"),
        4: (0.5, "existing_implementation_review", "R267已有舰载供能与工程工艺执行，移动及跨界仍缺，本项仅记半分。"),
        5: (1, "existing_implementation_review", "R267已有真实舰载工程输出的工程事实提供者，本轮补计已有实现；最终实机验收保持未通过。"),
    },
    "experiments": {
        5: (0.5, "existing_implementation_review", "R267已有世界泡／正式工程真实生产回执与事实提供者；W06–W15完整蓝图仍缺，保留半分。"),
    },
}


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
    previous_development = summary["development_metric"]["overall_percent"]
    changes = []

    for system in summary["systems"]:
        system_id = system["id"]
        development = system["development_metric"]
        if system_id in CREDITS:
            before = {key: development[key] for key in ("earned", "possible", "percent")}
            credits = {credit["capability_index"]: credit for credit in development["capability_credits"]}
            for index, (earned, basis, reason) in CREDITS[system_id].items():
                credits[index] = {
                    "capability_index": index,
                    "earned": earned,
                    "basis": basis,
                    "reason": reason,
                    "evidence": RECEIPT,
                }
            excluded = set(development["excluded_capability_indices"])
            development["capability_credits"] = [credits[index] for index in sorted(credits)]
            development["earned"] = sum(
                credits[index]["earned"] if index in credits else capability["earned"]
                for index, capability in enumerate(system["capabilities"])
                if index not in excluded
            )
            development["percent"] = development["earned"] / development["possible"] * 100
            changes.append({
                "system_id": system_id,
                "before": before,
                "after": {key: development[key] for key in ("earned", "possible", "percent")},
                "credits": [credits[index] for index in CREDITS[system_id]],
            })
        if system_id in REVIEWS:
            implemented, remaining = REVIEWS[system_id]
            system["industrial_finish_r268_review"] = {
                "updated_at": stamp,
                "implemented": implemented,
                "remaining": remaining,
                "evidence": RECEIPT,
                "original_acceptance_score_unchanged": True,
                "runtime_pass_claim_added": False,
            }
            system["updated_at"] = stamp
            development.update(
                remaining_development=remaining,
                implementation_receipt=RECEIPT,
                updated_at=stamp,
                original_acceptance_score_unchanged=True,
            )

    research = next(system for system in summary["systems"] if system["id"] == "research")
    for credit in research["development_metric"]["capability_credits"]:
        if credit["capability_index"] == 5:
            credit["reason"] = (
                "研究所与W13扣电统一走Hk3PortPayment／Hk3PowerPorts／Hk3RefundJournal，"
                "按实际接受量退款并限制同tick预算。W13真实主控身份和研究服务已注册，"
                "完整建筑蓝图仍缺，本项继续半分；不把注册或构建记作成型。"
            )

    summary["systems"].sort(key=lambda system: system["percent"])
    group_values = defaultdict(list)
    for system in summary["systems"]:
        group_values[system["group"]].append(system["development_metric"]["percent"])
    current = sum(system["development_metric"]["percent"] for system in summary["systems"]) / summary["domain_count"]
    delta = current - previous_development
    completed = sum(system["development_metric"]["percent"] == 100 for system in summary["systems"])
    overall = summary["development_metric"]
    overall.update(
        overall_percent=current,
        completed_domains=completed,
        incomplete_domains=summary["domain_count"] - completed,
        group_summary={group: sum(values) / len(values) for group, values in group_values.items()},
        updated_at=stamp,
        previous_development_percent=previous_development,
        changed_domains=list(CREDITS),
        delta_percentage_points=current - summary["overall_percent"],
        implementation_delta_percentage_points=delta,
        implementation_receipt=RECEIPT,
        delta_components_percentage_points={
            "new_implementation": (0.5 / 9 * 100) / summary["domain_count"],
            "existing_implementation_review": delta - (0.5 / 9 * 100) / summary["domain_count"],
        },
    )
    summary["industrial_finish_r268_receipt"] = RECEIPT
    summary["industrial_finish_r268_completion"] = completion
    summary["industrial_finish_r268_review"] = {
        "reviewed_domains": list(REVIEWS),
        "scored_domains": list(CREDITS),
        "previous_audit": (backup / "current-summary.json").relative_to(ROOT).as_posix(),
        "unchanged_acceptance": True,
        "unchanged_excluded_capability_count": overall["excluded_capability_count"],
        "runtime_pass_claim_added": False,
        "score_changes": changes,
    }
    summary["report_updated_at"] = summary["updated_at"] = stamp

    page = page.replace(
        "<h2>工业链正式工艺与来源补齐 · R267</h2>",
        "<h2>历史实现记录 · R267（当前计划数量以R268为准）</h2>",
        1,
    )
    source_notice = (
        '<section class="notice" id="industrial-finish-r268-current"><h2>当前工业链与研究补齐 · R268</h2>'
        f'<p>{escape(REVIEWS["industrial_lines"][0])}</p>'
        '<p>本轮新增RCA解析／重构，补齐执行输出与唤醒；世界泡任务、舰图、舰载工程及OPR部分属于已有实现的证据校正。'
        '构建、数据生成与候选状态以回执逐项记录为准；未安装、未新增实机验收。</p>'
        f'<p>{escape(REVIEWS["industrial_lines"][1])}</p>'
        f'<p><a href="{LINK}">当前实现、构建／数据生成状态与剩余边界</a></p></section>'
    )
    source_start, _ = element_span(page, "section", "recipe-source-review-20261113")
    page = page[:source_start] + source_notice + page[source_start:]
    groups_html = "".join(f'<div>{escape(group)}<b>{value:.2f}%</b></div>' for group, value in overall["group_summary"].items())
    backup_link = "../" + backup.relative_to(ROOT / "logs").as_posix() + "/index.html"
    current_notice = (
        '<section id="offline-maximize-current">'
        f'<p class="notice">{stamp} · R268实现增量及既有证据复核；仅研发口径变动，原验收记录保持。</p>'
        '<section class="metrics">'
        f'<div>研发完成度 · 37域等权<b>{current:.2f}%</b></div>'
        f'<div>本轮研发变动<b>{delta:+.2f}个百分点</b></div>'
        f'<div>研发满分系统<b>{completed} / 37</b></div>'
        f'<div>原验收完成度 · 保留<b>{summary["overall_percent"]:.2f}%</b></div></section>'
        f'<section class="metrics">{groups_html}</section>'
        '<ul><li><b>研究</b>：RCA正式解析／重构接通，8/9＝88.89%。</li>'
        '<li><b>世界泡执行</b>：既有任务、奖励与事实提供者补计，6/8＝75.00%；资源目录0分、跨文件原子半分保持。</li>'
        '<li><b>休伯利安工程</b>：既有舰图、供能工程与事实提供者补计，5/6＝83.33%；移动及跨界仍缺。</li>'
        '<li><b>实验</b>：既有正式工程／世界泡生产回执补计，5/6＝83.33%；完整奇观几何仍缺。</li>'
        '<li><b>工业链</b>：339条计划、70个主控正常来源，维持10.5/12＝87.50%。</li></ul>'
        '<p>37域原验收分值、能力表、分母及23项移交验收保持。MAX复杂度源码已有、默认机壳首建环已解除，'
        '有效payload导出／对比及全链自然供料仍缺；I37候选待批准与正式接入，W06–W15十座完整蓝图仍缺。</p>'
        f'<p><a href="{LINK}">当前实现与构建回执</a> · '
        f'<a href="{backup_link}">修改前真实页面</a> · <a href="current-summary.json">当前机器可读摘要</a></p></section>'
    )
    page = replace_element(page, "section", "offline-maximize-current", current_notice)
    page = page.replace(
        "<h2>当前25个未完成系统 · 正式1.0共37域</h2>",
        f'<h2>当前{overall["incomplete_domains"]}个研发未满分系统 · 正式1.0共37域</h2>',
        1,
    )
    page = page.replace(
        "<h2>当前37个系统 · 研发完成度从低到高</h2>",
        "<h2>当前37个系统 · 原验收完成度从低到高，同分保留原序</h2>",
        1,
    )

    cards = {}
    for system in summary["systems"]:
        system_id = system["id"]
        start, end = element_span(page, "details", "system-" + system_id)
        card = page[start:end]
        development = system["development_metric"]
        card = re.sub(
            r"(<summary>.*?<strong>).*?(</strong>)",
            lambda match: match[1] + f'研发 {development["percent"]:.2f}% · 原验收 {system["percent"]:.2f}%' + match[2],
            card, count=1, flags=re.S,
        )
        scope = (
            '<p class="notice development-scope">'
            f'当前研发：{development["earned"]:g}/{development["possible"]:g}（{development["percent"]:.2f}%）；'
            f'原验收历史：{system["earned"]:g}/{system["possible"]:g}（{system["percent"]:.2f}%）。'
            '下方原能力表保留历史；当前缺口以本卡研发复核为准，现场验证移交负责人。</p>'
        )
        card = re.sub(r'<p class="notice development-scope">.*?</p>', lambda match: scope, card, count=1, flags=re.S)
        card = re.sub(
            r'(<div class="bar"><i style="width:)[^%]+(%")',
            lambda match: match[1] + str(development["percent"]) + match[2], card, count=1,
        )
        if system_id in REVIEWS:
            implemented, remaining = REVIEWS[system_id]
            detail = f'<p>{escape(implemented)}</p><p><b>当前研发缺口：</b>{escape(remaining)}</p>'
        else:
            detail = '<p>本轮未重新核验该域，实现判断与研发分值沿用原记录；原验收表和历史说明不作为新增通过证据。</p>'
        notice = (
            f'<section class="notice" id="industrial-finish-r268-{system_id}"><h3>当前研发复核 · R268</h3>'
            f'{detail}<p>更新：{stamp} · <a href="{LINK}">本轮回执与复核范围</a></p></section>'
        )
        card = card.replace("</summary>", "</summary>" + notice, 1)
        card = card.replace('<div class="table-wrap"><table', '<h3>原验收历史能力表（保留原分与依据）</h3><div class="table-wrap"><table', 1)
        cards[system_id] = (start, end, card)
    first = min(value[0] for value in cards.values())
    last = max(value[1] for value in cards.values())
    page = page[:first] + "".join(cards[system["id"]][2] for system in summary["systems"]) + page[last:]
    payload = json.dumps(summary, ensure_ascii=False, indent=2).replace("<", "\\u003c")
    page = replace_element(page, "script", "audit-data", '<script type="application/json" id="audit-data">' + payload + "</script>")
    (AUDIT / "current-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", "utf-8")
    (AUDIT / "index.html").write_text(page, "utf-8")
    publication = {
        "updated_at": stamp,
        "completion_receipt": RECEIPT,
        "backup": backup.relative_to(ROOT).as_posix(),
        "development_percent": current,
        "previous_development_percent": previous_development,
        "acceptance_percent": summary["overall_percent"],
        "domain_count": summary["domain_count"],
        "excluded_capability_count": overall["excluded_capability_count"],
        "score_changes": changes,
        "client_tested": False,
        "installed": False,
    }
    (LOG / "audit-publication.json").write_text(json.dumps(publication, ensure_ascii=False, indent=2) + "\n", "utf-8")
    print(json.dumps(publication, ensure_ascii=False))


if __name__ == "__main__":
    main()
