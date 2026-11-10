"""从实际会话页导出I40本轮；不依赖已经不可获取的早期祖先页。"""
import argparse
import datetime as dt
import json
import re
import sys
import time
from html import escape
from pathlib import Path
from urllib.parse import unquote, urlsplit

import archive_dialogue as a

ROOT = Path(__file__).resolve().parents[2]
ARCHIVES = ROOT / "doc/HK3GTL-内测5/完整对话归档"
SUMMARY = ROOT / "doc/HK3GTL-内测5/讨论记录/2026-10-28_16-56-56_I37延后至最后并启动I40.html"
USER_ID = "msg_01a181ba-0bdb-7bf2-9e9e-69dab51d4978"
START = Path("C:/Users/OWNER/.codex/sessions/2026/10/28/rollout-2026-10-28T16-54-50-01a158c2-319f-7ad2-b0ce-2e04979e5e4e_01a181b8-21b4-7a21-b0ca-9eb31b2ea291.jsonl")
THREAD = "01a158c2-319f-7ad2-b0ce-2e04979e5e4e"
PREVIOUS = ARCHIVES / "2026-10-28_13-40-11_I37白纸重设计V5目标与范围_57c3fd4ecb.html"
LOG = ROOT / "logs/i40-dialogue-archive-20261028/status.json"


def load_current_window():
    sessions = a.find_sessions_root(START)
    choices = list(sessions.rglob("*" + THREAD + "*.jsonl"))
    active = max(choices, key=lambda p: p.stat().st_mtime)
    sources = []

    def visit(path, limit=None):
        records = a.read_records(path, limit=limit, active=limit is None)
        meta = a.get_meta(records, path.name)
        assert a.session_identity(meta) == THREAD
        combined = []
        if path.resolve() != START.resolve():
            base = meta.get("history_base") or {}
            parent = a.find_parent(sessions, base.get("thread_id"), THREAD)
            combined.extend(visit(parent, base.get("end_byte_offset"))[0])
        sources.append({"filename": path.name, "end_byte_offset": limit})
        for record in records:
            record["__archive_source_page"] = path.name
        return combined + records, meta

    records, meta = visit(active)
    return records, meta, sources


def export():
    records, thread_meta, sources = load_current_window()
    segments = a.segment_dialogue(records, THREAD)
    segment = next(s for s in segments if s["messages"][0]["id"] == USER_ID)
    old = a.existing_pages(ARCHIVES).get(segment["segment_id"])
    delivery_paths = []
    for message in segment["messages"]:
        for url in re.findall(r"https?://127\.0\.0\.1:\d+/[^\s)<>]+", message["text"]):
            relative = unquote(urlsplit(url).path).lstrip("/")
            target = ROOT / relative
            if relative.startswith("deliveries/I40_") and target.exists() and relative not in delivery_paths:
                delivery_paths.append(relative)
    override = {
        "title": "I37延后至最后并启动I40",
        "kind": "制作顺序调整与多方块设计",
        "keywords": ["I37", "I39已完成", "I40", "制作顺序", "延后"],
        "tags": ["负责人决定", "多方块设计", "完整对话归档"],
        "machines": ["I37", "I39", "I40"],
        "confirmed_decisions": ["I37暂时跳过，留到最后再制作。", "I39已经存在，本轮改为制作I40。"],
        "pending": ["I40候选须经负责人评审后才能计入批准批次；本轮制作请求不等于批准或实装授权。", "I37仍未批准、未实装。FCL与电脑版三场景内存测试仍待全部结构完成后进行。"],
        "related_paths": [str(SUMMARY.relative_to(ROOT)), "rule/当前多方块设计规则.md", "rule/崩坏三-gtl (hk3gtl) 项目规则.md", str(PREVIOUS.relative_to(ROOT))] + delivery_paths,
    }
    topic_map_path = ROOT / "tools/conversation_archive/topic_overrides.json"
    topic_map = a.load_overrides(topic_map_path)
    topic_map[USER_ID] = override
    a.write_if_changed(topic_map_path, json.dumps(topic_map, ensure_ascii=False, indent=2) + "\n")
    metadata = a.build_metadata(segment, thread_meta, sources, old[1] if old else None, override)
    metadata["transcript_scope"] = "从本轮真实用户消息所在JSONL页起，按实际分支字节边界导出本轮可见用户/助手文字；不含工具、思考、摘要、系统注入、环境状态或代理通信。"
    metadata["completeness"] = "本轮已落盘可见文字已完整纳入；进行中时尚无结束回复，结束后自动补齐。早期历史祖先页已不可获取，本轮不重导全项目历史。"
    if segment["closed_reason"] in ("final", "task_complete"):
        metadata["completeness"] = "本轮真实用户消息、全部已落盘可见进度和结束回复已纳入；早期历史祖先页已不可获取，本轮不据此宣称全项目历史完整。"
    elif segment["closed_reason"]:
        metadata["completeness"] = "本段已落盘可见文字已纳入；下一条用户消息开始了新段。本段并无可核验的结束回复，不能将后续消息或摘要当作本段原文。"
    old_messages = old[1].get("messages", []) if old else []
    unchanged = (len(old_messages) == len(segment["messages"]) and old_messages
                 and old_messages[-1]["id"] == segment["messages"][-1]["id"]
                 and old[1].get("closed_reason") == segment["closed_reason"])
    updated_at = (old[1].get("custom_metadata", {}).get("最后补录时间") if unchanged else None)
    metadata["custom_metadata"].update({"补录口径": "当前单段可完整恢复；未将缺失祖先或压缩摘要重建为原话。", "最后补录时间": updated_at or dt.datetime.now(a.HONG_KONG).isoformat(timespec="seconds")})
    path = old[0] if old else ARCHIVES / a.filename_for(metadata)
    changed = a.write_if_changed(path, a.render_page(segment, metadata, PREVIOUS, None))
    previous_html = PREVIOUS.read_text(encoding="utf-8")
    if path.name not in previous_html:
        old_nav = '<nav><a href="index.html">目录与搜索</a></nav>'
        new_nav = '<nav><a href="index.html">目录与搜索</a> · <a href="' + escape(path.name, quote=True) + '">后一段：I37延后并启动I40</a></nav>'
        assert old_nav in previous_html
        a.write_if_changed(PREVIOUS, previous_html.replace(old_nav, new_nav))
    if changed:
        a.write_if_changed(ARCHIVES / "index.html", a.render_index(ARCHIVES))
    archive_link = "../完整对话归档/" + path.name
    delivery_links = "".join('<p><a href="' + escape((ROOT / path).as_uri(), quote=True) + '">' + escape(path) + '</a></p>' for path in delivery_paths)
    summary = f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>I37延后至最后并启动I40</title><style>body{{max-width:980px;margin:40px auto;padding:0 24px;font:17px/1.8 system-ui;background:#101926;color:#e1ebf7}}a{{color:#7cd6ea}}code{{overflow-wrap:anywhere}}</style><h1>I37延后至最后并启动I40</h1><p>本页为人工决策摘要，不代替逐字原文。</p><p>负责人决定：I37暂时跳过，留到全部其他结构之后；I39已经存在，接着制作I40。此决定不表示批准最新I37候选，也不表示批准尚在制作的I40。</p><p>I37现有候选保持未批准、未实装；I40本轮制作完成后仍须审阅。五台批准后接入及全部结构完成后的FCL/电脑版三场景内存测试规则继续有效。</p><p>真实用户消息时间：{escape(metadata['start_time'])}；最后可见文字：{escape(metadata['end_time'])}；状态：{escape(metadata['status'])}。时长从首条用户消息至最后一条可见文字计算，当前{metadata['duration_seconds']:.3f}秒，不代表计算时长。</p><p><a href="{escape(archive_link, quote=True)}">本轮完整对话原文</a> · <a href="../完整对话归档/{escape(PREVIOUS.name, quote=True)}">上一轮I37原文与实际交付</a></p><p>变更记录 #1：按实际负责人消息建立制作顺序决定及原文互链；随着真实可见回复落盘持续补录。</p></html>'''
    if delivery_links:
        summary = summary.replace("</html>", '<h2>本轮可核对的本地交付链接</h2>' + delivery_links + '</html>')
    a.write_if_changed(SUMMARY, summary)
    result = {"thread_id": THREAD, "segment_id": segment["segment_id"], "archive": str(path), "summary": str(SUMMARY), "message_count": len(segment["messages"]), "last_message_id": segment["messages"][-1]["id"], "last_message_time": metadata["end_time"], "status": metadata["status"], "source_files": sources, "prior_i37_final_verified": "2026-10-28T16:18:47.107+08:00", "scope": metadata["completeness"]}
    LOG.parent.mkdir(parents=True, exist_ok=True)
    a.write_if_changed(LOG, json.dumps(result, ensure_ascii=False, indent=2))
    return result, bool(segment["closed_reason"])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--watch", action="store_true")
    args = parser.parse_args()
    last_signature = None
    while True:
        result, closed = export()
        signature = (result["message_count"], result["last_message_id"], result["status"])
        if signature != last_signature:
            print(json.dumps(result, ensure_ascii=False), flush=True)
            last_signature = signature
        if closed or not args.watch:
            return
        time.sleep(20)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
