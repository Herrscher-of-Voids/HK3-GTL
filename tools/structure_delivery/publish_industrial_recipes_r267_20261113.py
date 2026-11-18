import json
import re
import shutil
from collections import defaultdict
from datetime import datetime
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "logs/beta5-completion-audit-20261030"
LOG = ROOT / "logs/industrial-recipes-r267-20261113"
RECEIPT = "logs/industrial-recipes-r267-20261113/completion.json"
FINDINGS = ROOT / "logs/recipe-source-review-20261113/findings.json"
LINK = "../industrial-recipes-r267-20261113/completion.json"

REVIEWS = {
    "voltage_progression": (
        "HRV／HDV／CIV结构壳新增HBV／MAX档与RN-LES前级制造入口，解除I09–I16及S02默认机壳首建环；"
        "QSV门槛、工业主材配方和实际运行电压保持。I16魂钢HDV首建研发能力由0分记为1分。",
        "16阶各5台与最低15项目的完整范围、MAX至CEV全链自然推进仍未完成；原验收不变。",
    ),
    "industrial_lines": (
        "292条普通工业计划与17条奇观／舰载计划合计309条；70个主控具有正常制造来源，"
        "其中新增44个；补齐45条功能来源（工业计划3条、Java制造42条），另加13条载体消费工艺。"
        "三档探测器接入对应采集工艺，虚空万藏接入本队第五次真实采掘奖励。"
        "I40四种复材、I42预制件、能源燃料及高阶支线接入正式工艺；"
        "修复I12／I16默认首建的机壳主材自依赖。配方数量不作为完成比例。",
        "I37已有完整候选蓝图，外观未批准且未接入正式结构；W06–W15十座完整蓝图及休伯利安跨界能力仍未完成；"
        "309条计划不等于全部机器均可成型或全链实际运行通过。",
    ),
    "energy_production": (
        "能源燃料和发电计划接入正式执行，I38整流工艺实际结算HW网络注入；"
        "保留真实扣料、GT供能、输出结算与重复结算守卫。",
        "本轮记录源码与构建交付，不新增客户端燃烧、故障恢复或性能验收；原分数保持。",
    ),
    "research": (
        "侵蚀研究模块及研究功能件补正常来源；奇观主控、专项研究、二审、"
        "真实产出回执与工程事实接通。W13真实主控身份及研究服务已注册，"
        "其完整建筑尚缺，不能凭主控运行。",
        "不以持有产物、创造巡检或预览授予工程事实；"
        "缺蓝图、样本解析／重构合同和跨系统执行边界继续保留，原分数保持。",
    ),
    "multiblocks": (
        "W01–W15及H01接入真实主控生产身份；W01–W03沿用完整结构与W03特效，"
        "W04／W05接入完整候选蓝图，外观仍待批准。"
        "I37候选未批准、未接入正式结构，W06–W15缺蓝图，当前均明确拒绝成型和终端搭建；"
        "休伯利安仅按真实舰体实体位置撤销完整性，成型后空域落雪不再中断生产。",
        "70个主控的合成来源不代表70台结构已完成；自由接口规则保留，"
        "原几何批准、成型、运行及性能验收记录分别保留，原分数保持。",
    ),
}

CAPABILITY_REASONS = [
    "液态崩坏能采集、精炼、稳定、回收、供给与自然首建来源接入正式工艺；保留运行验收边界。",
    "固态、气态及能态采集正式工艺与输入来源接通，不再以暂定计划代替生产入口。",
    "魂钢制造与前级机壳主材入口接通，I12／I16默认首建不再依赖自身首批产物。",
    "燃料生产、反应堆、相变及整流供能工艺正式开放，HW注入走实际批次结算。",
    "仿制核心加工、配套材料及主控制器的正常制造来源已接通，研究条件保持。",
    "神之键加工、装配与配套材料工艺接入正式执行，研究与主控来源保持真实前置。",
    "真实世界泡路线的容器、正式加工及相关设备来源接通；不将模拟世界泡产物当作真实捕获事实。",
    "模拟世界泡模型、稳定及终止工艺与物料循环接通，保持模拟和真实世界泡身份分离。",
    "虚数空间、坐标及锚定配套工艺接入正式执行，研究、材料及主控入口接通。",
    "世界维系工艺与主控来源已接；I37已有完整候选蓝图，外观未批准且未接入正式结构，明确拒绝成型，保留半分。",
    "十五座奇观正式身份、产物、研究及真实输出工程回执接通；W06–W15十座完整几何尚缺，保留半分。",
    "休伯利安完整舰体、主控来源与正式舰载工程工艺接通；跨界能力尚缺，保留半分。",
]

RESOLUTIONS = {
    "missing_acquisition": (
        "侵蚀研究模块补正常制造来源，研究所安装入口保持。",
        ["src/main/java/com/sirin/hk3gtl/common/recipe/machine/Hk3ControllerRecipes.java"],
    ),
    "provisional_locked": (
        "I40四种功能复材和I42预制件改为正式工艺；真实执行仍检查研究、供能、物料与输出结算。",
        ["src/main/resources/data/hk3gtl/research/industrial_processes.json"],
    ),
    "commissioning_only": (
        "W01–W15及H01登记17条正式生产工艺，真实生产与创造巡检分离；W06–W15缺几何仍不得成型。",
        [
            "src/main/resources/data/hk3gtl/research/wonder_processes.json",
            "src/main/java/com/sirin/hk3gtl/common/machine/wonder/Hk3WonderProductionMachine.java",
        ],
    ),
    "default_blueprint_bootstrap_dependency": (
        "I12／I16所需前级机壳主材来源已修复，默认自然首建不再消耗本机首次产物；建筑外观不变。",
        ["src/main/java/com/sirin/hk3gtl/common/recipe/machine/Hk3VoltageCasingRecipes.java"],
    ),
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
    shutil.copy2(FINDINGS, backup / "recipe-source-findings.json")
    summary = json.loads((backup / "current-summary.json").read_text("utf-8"))
    page = (backup / "index.html").read_text("utf-8")
    findings = json.loads((backup / "recipe-source-findings.json").read_text("utf-8"))
    previous_development = summary["development_metric"]["overall_percent"]

    for finding in findings["findings"]:
        detail, sources = RESOLUTIONS[finding["kind"]]
        finding["original_detail"] = finding["detail"]
        finding["historical_sources"] = finding["sources"]
        finding.update(status="resolved_in_source", detail=detail, sources=sources, evidence=RECEIPT)
    findings.update(
        status="原4项缺口已在源码解决；缺失建筑蓝图及跨界能力仍单列",
        scope="R267仓库实现与候选构建；未安装、未进行新的游戏实测。",
        confirmed_missing_acquisition_lower_bound=0,
        score_delta=0,
        client_tested=False,
        updated_at=stamp,
        completion_receipt=RECEIPT,
        previous_findings=(backup / "recipe-source-findings.json").relative_to(ROOT).as_posix(),
    )

    systems = {system["id"]: system for system in summary["systems"]}
    for system_id, (implemented, remaining) in REVIEWS.items():
        systems[system_id]["industrial_production_r267_review"] = {
            "updated_at": stamp,
            "implemented": implemented,
            "remaining": remaining,
            "evidence": RECEIPT,
            "runtime_pass_claim_added": False,
            "original_acceptance_score_unchanged": True,
        }
        systems[system_id]["updated_at"] = stamp
    industrial = systems["industrial_lines"]
    industrial["recipe_source_review"] = {
        "evidence": "logs/recipe-source-review-20261113/findings.json",
        "completion": RECEIPT,
        "status": findings["status"],
        "findings": findings["findings"],
        "updated_at": stamp,
    }
    metric = industrial["development_metric"]
    metric.update(
        earned=10.5,
        percent=87.5,
        updated_at=stamp,
        implementation_receipt=RECEIPT,
        original_acceptance_score_unchanged=True,
        capability_credits=[
            {
                "capability_index": index,
                "earned": 1 if index < 9 else 0.5,
                "basis": "new_implementation",
                "reason": reason,
                "evidence": RECEIPT,
            }
            for index, reason in enumerate(CAPABILITY_REASONS)
        ],
        remaining_development="L10：I37已有完整候选，待外观批准及正式结构接入；L11：W06–W15十座完整几何；L12：休伯利安跨界能力。实际运行验收移交负责人，不计作已通过。",
    )
    voltage = systems["voltage_progression"]["development_metric"]
    voltage.update(
        earned=2.5,
        percent=50,
        updated_at=stamp,
        implementation_receipt=RECEIPT,
        capability_credits=[credit for credit in voltage["capability_credits"] if credit["capability_index"] != 2] + [{
            "capability_index": 2,
            "earned": 1,
            "basis": "new_implementation",
            "reason": "HRV／HDV／CIV结构壳以HBV／MAX档及RN-LES前级制造解除I09–I16／S02默认首建环；QSV门槛、主材和运行电压保持。",
            "evidence": RECEIPT,
        }],
        remaining_development="16阶各5台与最低15项目的扩展设备范围、MAX至CEV全链自然推进仍待完成；本轮完成当前已登记设备的工艺。默认HRV／HDV／CIV首建环已修复；QSV门槛与主材、运行档保持。",
    )
    research = systems["research"]["development_metric"]
    research["remaining_development"] = research["remaining_development"].replace("W13真实注册母机", "W13完整建筑蓝图")
    summary["systems"].sort(key=lambda system: system["percent"])
    group_values = defaultdict(list)
    for system in summary["systems"]:
        group_values[system["group"]].append(system["development_metric"]["percent"])
    current = sum(system["development_metric"]["percent"] for system in summary["systems"]) / summary["domain_count"]
    delta = current - previous_development
    overall = summary["development_metric"]
    completed = sum(system["development_metric"]["percent"] == 100 for system in summary["systems"])
    overall.update(
        overall_percent=current,
        completed_domains=completed,
        incomplete_domains=summary["domain_count"] - completed,
        group_summary={group: sum(values) / len(values) for group, values in group_values.items()},
        updated_at=stamp,
        previous_development_percent=previous_development,
        changed_domains=["industrial_lines", "voltage_progression"],
        delta_percentage_points=current - summary["overall_percent"],
        implementation_delta_percentage_points=delta,
        implementation_receipt=RECEIPT,
        delta_components_percentage_points={"new_implementation": delta},
    )
    summary["industrial_production_r267_receipt"] = RECEIPT
    summary["industrial_production_r267_completion"] = completion
    summary["report_updated_at"] = summary["updated_at"] = stamp

    source_notice = (
        '<section class="notice" id="recipe-source-review-20261113"><h2>工业链正式工艺与来源补齐 · R267</h2>'
        f'<p>{escape(REVIEWS["industrial_lines"][0])}</p>'
        '<p>原核对的侵蚀研究模块来源、I40／I42暂定锁、W01–W03仅巡检及I12／I16首建自依赖四项已在源码解决。'
        'I37候选待批准和正式结构接入，W06–W15完整蓝图、休伯利安跨界能力仍缺；未安装、未新增实机验收。</p>'
        f'<p><a href="{LINK}">实现、构建与剩余边界</a> · '
        '<a href="../recipe-source-review-20261113/findings.json">当前缺口核对</a></p></section>'
    )
    page = replace_element(page, "section", "recipe-source-review-20261113", source_notice)
    groups_html = "".join(f'<div>{escape(group)}<b>{value:.2f}%</b></div>' for group, value in overall["group_summary"].items())
    backup_link = "../" + backup.relative_to(ROOT / "logs").as_posix() + "/index.html"
    current_notice = (
        '<section id="offline-maximize-current">'
        f'<p class="notice">{stamp} · R267工业链研发增量；仅按能力完成计分，原验收记录保持。</p>'
        '<section class="metrics">'
        f'<div>研发完成度 · 37域等权<b>{current:.2f}%</b></div>'
        f'<div>本轮研发变动<b>{delta:+.2f}个百分点</b></div>'
        f'<div>研发满分系统<b>{completed} / 37</b></div>'
        f'<div>原验收完成度 · 保留<b>{summary["overall_percent"]:.2f}%</b></div></section>'
        f'<section class="metrics">{groups_html}</section>'
        '<ul><li><b>工业链正式工艺与来源</b>：309条计划、70个主控来源；L1–L9各1分，L10–L12各0.5分，研发10.5/12＝87.50%。</li>'
        '<li><b>默认机壳首建</b>：I16魂钢HDV首建能力计入1分；该域研发2.5/5＝50.00%，其余四项不改分。</li>'
        '<li><b>保留研发缺口</b>：I37候选的批准与正式结构接入、W06–W15十座完整蓝图、休伯利安跨界能力。</li></ul>'
        '<p>37域及各域原验收分值、分母保持；其余域研发分数保持。配方数量、构建、安装或取消实测均不替代实机验收。</p>'
        f'<p><a href="{LINK}">本轮实现与构建回执</a> · '
        f'<a href="{backup_link}">本轮前真实页面</a> · <a href="current-summary.json">当前机器可读摘要</a></p></section>'
    )
    page = replace_element(page, "section", "offline-maximize-current", current_notice)

    cards = {}
    for system in summary["systems"]:
        system_id = system["id"]
        start, end = element_span(page, "details", "system-" + system_id)
        card = page[start:end]
        if system_id in REVIEWS:
            development = system["development_metric"]
            card = re.sub(r"(<summary>.*?<strong>).*?(</strong>)", lambda match: match[1] + f'研发 {development["percent"]:.2f}% · 原验收 {system["percent"]:.2f}%' + match[2], card, count=1, flags=re.S)
            scope = (
                '<p class="notice development-scope">'
                f'研发：{development["earned"]:g}/{development["possible"]:g}（{development["percent"]:.2f}%）；'
                f'原验收：{system["earned"]:g}/{system["possible"]:g}（{system["percent"]:.2f}%）。'
                '本轮只计实现能力；原能力表沿用验收历史，现场验证移交负责人。</p>'
            )
            card = re.sub(r'<p class="notice development-scope">.*?</p>', lambda match: scope, card, count=1, flags=re.S)
            card = re.sub(r'(<div class="bar"><i style="width:)[^%]+(%")', lambda match: match[1] + str(development["percent"]) + match[2], card, count=1)
            implemented, remaining = REVIEWS[system_id]
            notice = (
                f'<section class="notice" id="industrial-production-r267-{system_id}"><h3>R267当前研发实现</h3>'
                f'<p>{escape(implemented)}</p><p>{escape(remaining)}</p>'
                f'<p><a href="{LINK}">本轮源码、候选构建及剩余差距</a></p></section>'
            )
            card = card.replace("</summary>", "</summary>" + notice, 1)
        cards[system_id] = (start, end, card)
    first = min(value[0] for value in cards.values())
    last = max(value[1] for value in cards.values())
    page = page[:first] + "".join(cards[system["id"]][2] for system in summary["systems"]) + page[last:]
    payload = json.dumps(summary, ensure_ascii=False, indent=2).replace("<", "\\u003c")
    page = replace_element(page, "script", "audit-data", '<script type="application/json" id="audit-data">' + payload + "</script>")
    (AUDIT / "current-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", "utf-8")
    (AUDIT / "index.html").write_text(page, "utf-8")
    FINDINGS.write_text(json.dumps(findings, ensure_ascii=False, indent=2) + "\n", "utf-8")
    print(json.dumps({"development_percent": current, "acceptance_percent": summary["overall_percent"], "backup": str(backup)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
