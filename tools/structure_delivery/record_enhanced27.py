# -*- coding: utf-8 -*-
"""
【文件职责】按实际部署回执、分轮结构结果与内存摘要生成增强版实例纠正讨论记录。
【变更记录 #1】2026-10-15 03:06:10（香港时间 UTC+08:00 · 内测5修订159）
- 删除：无；不改历史HTML、分析报告、游戏文件或原始证据。
- 新增：自动选择目标实例最新部署回执、对应修订的结构解析JSON、现有内存摘要，
  并核对当前JAR及结构输入日志哈希；输出UTF-8中文HTML及输入证据摘要。
- 修改：只有显式 --write 才落盘正式讨论记录；默认只打印预览摘要，避免把脚本
  创建、构建或历史部分通过当作已生成记录或当前完整实机通过。
- 用途：补记本轮用户将唯一测试目标纠正为增强版2.7的决定；文件名使用实际记录
  时间且拒绝覆盖，原讨论精确时刻未知时明确写未知，实测范围与未验证事项分开。
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[2]
LOG = ROOT / "logs/enhanced27-memory-20261015"
RECORDS = ROOT / "doc/HK3GTL-内测5/讨论记录"
PREVIOUS = RECORDS / "2026-10-15_01-32-43_四包最新结构正式实装与下一座I14候选.html"
REPORT = ROOT / "doc/崩坏三-GTL/00_项目总览/模组全面系统性分析报告_v5.md"
HONG_KONG = timezone(timedelta(hours=8))
TARGET_INSTANCE = Path(os.environ.get("APPDATA", "C:/Users/OWNER/AppData/Roaming")) / (
    "PrismLauncher/instances/GregTech Leisure-增强版 2.7"
)
USER_QUOTE = (
    r"不对，我们应该用以下实例C:\Users\OWNER\AppData\Roaming\PrismLauncher\instances\GregTech Leisure-增强版 2.7"
    "作为模组的测试，因为我之后会将内测5加到这个整合包里，和我的朋友们一起试玩，"
    "我们优先将模组弄到这里面，然后测试并且优化整个整合包的内存占用"
)
TOPIC = "增强版2.7唯一测试实例纠正与实装验收内存优化"


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"需要JSON对象：{path}")
    return data


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def latest(paths: list[Path]) -> Path | None:
    return max(paths, key=lambda p: (p.stat().st_mtime_ns, p.name)) if paths else None


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def local_link(path: Path, label: str) -> str:
    relative = os.path.relpath(path.resolve(), RECORDS.resolve()).replace("\\", "/")
    return f'<a href="{esc(quote(relative, safe="/.:"))}">{esc(label)}</a>'


def code(value: Any) -> str:
    return f"<code>{esc(value)}</code>"


def list_html(values: list[str]) -> str:
    return "<ul>" + "".join(f"<li>{value}</li>" for value in values) + "</ul>"


def round_status(round_data: dict[str, Any]) -> str:
    status = {"passed": "本轮范围通过", "failed": "失败", "incomplete": "尚未完成",
              "ended_without_pass": "结束但未通过"}.get(round_data.get("status"), "状态待核对")
    return (
        f"第{esc(round_data.get('round'))}轮，目标{esc(round_data.get('scope'))}个方向："
        f"放置{esc(round_data.get('placed_count'))}、阶段{esc(round_data.get('stage_count'))}、"
        f"完整七阶段夹具{esc(round_data.get('complete_fixture_count'))}、"
        f"清理{esc(round_data.get('clean_count'))}、"
        f"FAILED {esc(round_data.get('failed_count'))}、"
        f"外部保留{esc(round_data.get('preserved_external_blocks'))}；{status}。"
        f"时间{esc(round_data.get('start_time'))}至{esc(round_data.get('end_time'))}，"
        f"耗时{esc(round_data.get('duration_seconds'))}秒。"
    )


def strict_full_pass(result: dict[str, Any], source_matches: bool) -> bool:
    # 不单凭一个all84passed布尔值宣布通过；最新轮计数和终态必须同时吻合。
    rounds = result.get("rounds", [])
    if not rounds or not source_matches or result.get("source_decode_replacement_count", 0):
        return False
    r = rounds[-1]
    return bool(
        result.get("schema") == "hk3gtl.structure70-runtime-result.v1"
        and result.get("all84passed") is True and r.get("all84passed") is True
        and r.get("scope") == 84 and r.get("placed_count") == 84
        and r.get("unique_placed_count") == 84 and r.get("stage_count") == 588
        and r.get("complete_fixture_count") == 84 and r.get("clean_count") == 84
        and r.get("unique_cleaned_count") == 84 and r.get("failed_count") == 0
        and not r.get("failed") and not r.get("timeouts") and not r.get("anomalies")
        and r.get("cleanup_failed_count", 0) == 0 and r.get("preserved_external_blocks") == 0
        and r.get("final_success_scope") == 84 and r.get("final_success_message")
        and r.get("stage_coverage_full_no_duplicates") is True
        and not r.get("scope_coverage_missing") and not r.get("scope_coverage_unexpected")
    )


def build_record(args: argparse.Namespace) -> tuple[str, dict[str, Any], Path]:
    receipt_path = args.receipt or latest(list(LOG.glob("deployment-r*-*.json")))
    if receipt_path is None:
        raise ValueError("未找到增强版部署回执；不能编造已部署记录")
    receipt_path = receipt_path.resolve()
    receipt = read_json(receipt_path)
    if Path(receipt.get("instance", "")).resolve() != TARGET_INSTANCE.resolve():
        raise ValueError("部署回执不是负责人指定增强版2.7实例")
    revision = int(receipt["revision"])
    installed = Path(receipt["installed_jar"])
    current_jar_matches = installed.is_file() and digest(installed) == receipt["sha256"]
    result_path = args.structure or latest(list(LOG.glob(f"structure-result-r{revision}*.json")))
    result: dict[str, Any] | None = None
    source_matches = False
    if result_path is not None:
        result_path = result_path.resolve()
        if not re.search(rf"r{revision}(?:\D|$)", result_path.name):
            raise ValueError("结构结果文件名修订号与最新部署不一致，禁止用旧修订通过代替当前结果")
        result = read_json(result_path)
        if result.get("schema") != "hk3gtl.structure70-runtime-result.v1":
            raise ValueError("结构结果不是正式分轮解析器格式")
        source_log = Path(result.get("source_log", ""))
        source_matches = source_log.is_file() and digest(source_log) == result.get("source_sha256")
    fully_passed = current_jar_matches and result is not None and strict_full_pass(result, source_matches)
    memory_paths = args.memory or sorted(LOG.glob("memory-*.json"), key=lambda p: p.stat().st_mtime_ns)
    memory_inputs = [(path.resolve(), read_json(path)) for path in memory_paths]
    memory_inputs = [(path, data) for path, data in memory_inputs if isinstance(data.get("metrics"), dict)]
    now = datetime.now(HONG_KONG)
    output_path = RECORDS / f"{now:%Y-%m-%d_%H-%M-%S}_{TOPIC}.html"
    if output_path.exists():
        raise ValueError(f"讨论记录同名已存在，拒绝覆盖：{output_path}")
    changelog = read_json(ROOT / "src/main/resources/assets/hk3gtl/changelog.json")
    source_entry = changelog.get("entries", [{}])[0]
    source_revision = source_entry.get("revision", "未知")
    build_log = LOG / f"clean-build-r{revision}.log"
    build_passed = build_log.is_file() and "BUILD SUCCESSFUL" in build_log.read_text(encoding="utf-8", errors="replace")
    references = [receipt_path, REPORT, PREVIOUS]
    if result_path is not None:
        references.append(result_path)
    if result is not None:
        references.append(Path(result["source_log"]))
    if build_log.is_file():
        references.append(build_log)
    references.extend(path for path, _ in memory_inputs)
    for name in ["config-restore-packs-20261015_020932.json", "modernfix-dynamic-resources-audit.json",
                 "r158-pattern-race-diagnosis.json", "r158-blockpattern-race-audit.json"]:
        path = LOG / name
        if path.is_file():
            references.append(path)
    structures = [
        f"当前部署修订{revision}，当前活动JAR与回执SHA-256{'一致' if current_jar_matches else '不一致或无法读取，部署状态需重新核对'}。",
        f"完整84朝向：{'当前修订最新轮已严格通过' if fully_passed else '尚未取得当前修订最新轮完整通过证据'}。",
    ]
    if result is not None:
        structures += [
            f"结构解析输入：{local_link(result_path, result_path.name)}；原始日志哈希{'一致' if source_matches else '不一致或缺失，不能据此认定当前通过'}。",
            *[round_status(r) for r in result.get("rounds", [])],
            "各轮互不合并；某轮范围通过只覆盖其scope。取消、失败或未完成不会借用旧轮结果。",
            "forced最大值只表示日志记录的放置足迹，票据释放没有独立的日志计数断言。",
        ]
    else:
        structures.append(f"尚未发现修订{revision}的分轮结构解析JSON；旧修订结果只可作为历史，未自动沿用。")
    memories: list[str] = []
    metric_names = {"rss": "工作集", "private": "私有字节", "heap_used": "已用堆", "heap_committed": "已提交堆"}
    for path, data in memory_inputs:
        fragments: list[str] = []
        for key, label in metric_names.items():
            metric = data["metrics"].get(key, {})
            value = metric.get("median")
            if isinstance(value, (int, float)) and metric.get("unit") == "bytes":
                fragments.append(f"{label}中位数{value/(1024**3):.3f}GiB（{metric.get('sample_count', '未知')}样本）")
        interval = data.get("requested_interval", {})
        memories.append(
            f"{local_link(path, path.name)}：{esc(data.get('label', '未标记'))}，"
            f"{esc(interval.get('start', '起点未记录'))}至{esc(interval.get('end', '终点未记录'))}；"
            + "，".join(fragments) + "。"
        )
        for limit in data.get("comparison_limits", []) + data.get("notes", []):
            memories.append(f"该摘要边界：{esc(limit)}")
    if not memories:
        memories.append("当前没有含metrics的内存摘要，内存占用与收益尚未实测。")
    memories.append("以上为各文件实际采样值；测试位置、夹具阶段、GC和后台裁剪可能不同，不能自动等同受控A/B或存活堆下降。进程工作集不等于GPU显存，本生成器不自动宣布内存优化验收通过。")
    fixes = [
        "增强版现有Enhancedcore与GTLAdditions含major65类，实例运行Java21；HK3GTL仍保持Java17字节码兼容。",
        "按原整合包清单保留JECharacters4.6.11，重复4.6.3-fix备份移出；来源不是“用户后加”。",
        "HK3模型来源记录迁出models，修复TextureScaler误读标量texture_size造成资源加载回退与重复初始化；TextureScaler继续启用。",
        "正式21种批准结构保留几何、严格空气与接口，稀疏预览和逐夹具清理只改变对象/票据管理。",
        "原始10项资源包及顺序已恢复，未裁剪第三方内容冒充通过；ModernFix dynamic_resources仍为false。",
        f"源码当前修订{esc(source_revision)}，最新部署回执修订{revision}；源码说明不能自动视为已部署或实机通过。",
    ]
    fixes += ["源码当前修订说明：" + esc(change) for change in source_entry.get("changes", [])]
    awaiting = [
        "实际生产配方、研究推进、LIQUID66可达性专项适配与多人长时稳定性仍需单独验收；结构成型通过不等于这些系统通过。",
        "I14曲冠重设计V3仍为下一座候选，用户尚未批准，不进入本次正式结构清单。",
        "已批准结构尺寸、材料、层级扩建和四个ZIP决定持续有效，性能调整不授权缩小或重新设计。",
    ]
    if not fully_passed:
        awaiting.insert(0, "先完成当前修订S05四向与全84朝向成型、破坏、恢复和安全清理复验，再按真实结果继续优化。")
    awaiting += ["主任务补充的当前执行说明：" + esc(note) for note in args.note]
    sections = [
        ("用户要求与已确认决定", f"<blockquote>{esc(USER_QUOTE)}</blockquote>" +
         list_html([
             "本轮唯一部署与实机目标：" + code(TARGET_INSTANCE / "minecraft") + "；用于内测5与朋友联机试玩。",
             "优先实装最新定稿结构，再测试并优化整个实际整合包；后续游戏测试继续限定专用创造、允许作弊、超平坦世界。",
             "原用户讨论精确时刻无法从消息核实，记为未知；本文件为实际生成时刻的补记，不伪造当时已写入。",
         ])),
        ("被覆盖决定与历史追溯", "<p>" + local_link(PREVIOUS, "此前四包正式实装与I14候选记录") +
         "保留；其中GTL十一周目作为当前测试目标的决定被本轮增强版2.7纠正覆盖，旧GregTech-Leisure-1.4.5.2亦不再是当前目标。四包批准结构和I14候选状态仍延续。</p>"),
        ("实际部署与备份", list_html([
             f"最新回执：{local_link(receipt_path, receipt_path.name)}，回执时间{esc(receipt.get('time', '未记录'))}。",
             "安装JAR：" + code(installed) + "；SHA-256：" + code(receipt["sha256"]) +
             f"；{esc(receipt.get('bytes'))} bytes。",
             "备份：" + code(receipt.get("backup", "未记录")) + "。",
             "无关第三方JAR哈希：" + ("部署回执确认不变。" if receipt.get("unrelated_jars_unchanged") is True else "回执未确认，待核对。"),
             f"该部署修订构建日志：{'记录BUILD SUCCESSFUL' if build_passed else '尚无成功构建日志'}；构建不等于实机通过。",
         ])),
        ("结构实机执行与验收范围", list_html(structures)),
        ("已实施修复与兼容边界", list_html(fixes)),
        ("内存采样与结论边界", list_html(memories)),
        ("助手提案、待定事项与下一步", list_html(awaiting)),
        ("相关文档与本次输入", list_html([
            local_link(path, str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path))
            for path in references if path.exists()
        ])),
    ]
    content = (
        '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>{esc(TOPIC)}</title><style>'
        'body{max-width:1120px;margin:auto;padding:30px;background:#101722;color:#e9eef5;'
        'font:16px/1.8 system-ui,"Microsoft YaHei",sans-serif}h1,h2{color:#9fe7d4}'
        'section{background:#172234;border:1px solid #32445e;border-radius:10px;padding:18px;margin:16px 0}'
        'code{color:#ffd590;overflow-wrap:anywhere}a{color:#9fe7d4}li{margin:8px 0;overflow-wrap:anywhere}'
        'blockquote{border-left:3px solid #9fe7d4;padding:12px;white-space:pre-wrap}</style></head><body>'
        f'<h1>{esc(TOPIC)}</h1><p>记录时间：{now:%Y-%m-%d %H:%M:%S} '
        'Asia/Hong_Kong（UTC+08:00）；主题：本轮增强版实例纠正。</p>'
        + "".join(f"<section><h2>{esc(title)}</h2>{body}</section>" for title, body in sections)
        + f'<footer>变更记录 #1 · {now:%Y-%m-%d %H:%M:%S} 香港时间 · '
        '新增本轮决定与真实状态快照，保留历史；无已确认决定被自动扩大为未完成的验收。</footer></body></html>\n'
    )
    summary = {
        "record_time": now.isoformat(), "html_path": str(output_path), "written": False,
        "receipt": str(receipt_path), "deployed_revision": revision,
        "installed_jar_matches_receipt": current_jar_matches,
        "structure_result": str(result_path) if result_path else None,
        "structure_source_matches_sha256": source_matches, "all84passed": fully_passed,
        "source_revision": source_revision, "build_passed_for_deployed_revision": build_passed,
        "memory_summaries": [str(path) for path, _ in memory_inputs],
        "memory_gain_automatically_validated": False,
        "inputs": [{"path": str(path), "sha256": digest(path)} for path in references if path.is_file()],
    }
    return content, summary, output_path


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="生成增强版2.7讨论记录；默认预览，--write正式落盘")
    parser.add_argument("--write", action="store_true", help="写入新的中文UTF-8 HTML，已有文件不覆盖")
    parser.add_argument("--receipt", type=Path, help="指定增强版部署回执；默认选择最新回执")
    parser.add_argument("--structure", type=Path, help="对应部署修订的结构分轮结果；默认选择最新匹配文件")
    parser.add_argument("--memory", type=Path, action="append", help="内存摘要，可重复；默认读取现有memory-*.json")
    parser.add_argument("--note", action="append", default=[], help="主任务追加的当前执行说明，保留为明确补充说明")
    args = parser.parse_args()
    try:
        content, summary, output_path = build_record(args)
        if args.write:
            RECORDS.mkdir(parents=True, exist_ok=True)
            # x模式保护同名历史文件；不存在时才创建，文件确实落盘后才报告written。
            with output_path.open("x", encoding="utf-8", newline="") as stream:
                stream.write(content)
            summary["written"] = True
            summary["html_sha256"] = digest(output_path)
        json.dump(summary, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return 0
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as error:
        parser.error(str(error))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
