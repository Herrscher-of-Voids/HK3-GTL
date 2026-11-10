"""按指定真实消息ID归档当前可获取分支中的单段对话。"""
import argparse
import datetime as dt
import json
import sys
import time
from html import escape
from pathlib import Path

import archive_dialogue as a
from archive_i40_turn_20261028 import ARCHIVES, ROOT, THREAD, load_current_window


def export(profile):
    records, thread_meta, sources = load_current_window()
    segments = a.segment_dialogue(records, THREAD)
    segment = next(s for s in segments if s["messages"][0]["id"] == profile["user_id"])
    previous_path = ROOT / profile["previous"]
    previous_metadata = a.read_page_metadata(previous_path)
    previous = next(s for s in segments if s["segment_id"] == previous_metadata["segment_id"])
    previous_has_final = (previous["messages"][-1]["phase"] in a.FINAL_PHASES
        and previous["messages"][-1].get("delivery") != "async")
    assert previous_has_final or profile.get("allow_previous_without_final", False)
    assert previous_metadata["messages"][-1]["id"] == previous["messages"][-1]["id"]
    old = a.existing_pages(ARCHIVES).get(segment["segment_id"])
    summary_path = ROOT / profile["summary"]
    override = dict(profile["metadata"])
    override["related_paths"] = list(dict.fromkeys([profile["summary"], profile["previous"],
        "rule/当前多方块设计规则.md", "rule/崩坏三-gtl (hk3gtl) 项目规则.md"]
        + override.get("related_paths", []) + (old[1].get("related_paths", []) if old else [])))
    topic_path = ROOT / "tools/conversation_archive/topic_overrides.json"
    topics = a.load_overrides(topic_path)
    override["related_paths"] = list(dict.fromkeys(override["related_paths"]
        + topics.get(profile["user_id"], {}).get("related_paths", [])))
    topics[profile["user_id"]] = override
    a.write_if_changed(topic_path, json.dumps(topics, ensure_ascii=False, indent=2) + "\n")
    metadata = a.build_metadata(segment, thread_meta, sources, old[1] if old else None, override)
    old_messages = old[1].get("messages", []) if old else []
    unchanged = (len(old_messages) == len(segment["messages"]) and old_messages
        and old_messages[-1]["id"] == segment["messages"][-1]["id"]
        and old[1].get("closed_reason") == segment["closed_reason"])
    supplemented = old[1].get("custom_metadata", {}).get("最后补录时间") if unchanged else None
    metadata["custom_metadata"]["最后补录时间"] = supplemented or dt.datetime.now(a.HONG_KONG).isoformat(timespec="seconds")
    metadata["custom_metadata"].update(profile.get("custom_metadata", {}))
    metadata["transcript_scope"] = "从当前可获取JSONL分支按真实消息ID取单段可见用户/助手文字；不含工具、隐藏思考、系统注入、环境状态、摘要或代理通信。"
    metadata["completeness"] = "本段已落盘可见文字已纳入；结束回复尚未落盘时持续补录。早期历史祖先页缺失，不能据此宣称全项目历史完整。"
    if segment["closed_reason"] and any(m["phase"] in a.FINAL_PHASES and m.get("delivery") != "async" for m in segment["messages"]):
        metadata["completeness"] = "本段真实用户消息、可见进度及真实结束回复已纳入；早期历史祖先页缺失，不能据此宣称全项目历史完整。"
    elif segment["closed_reason"]:
        metadata["completeness"] = "本段已落盘可见文字已纳入；本段未产生真实结束回复，后续用户消息与其助手回复另分新段。早期历史祖先页缺失，不能据此宣称全项目历史完整。"
    path = old[0] if old else ARCHIVES / a.filename_for(metadata)
    changed = a.write_if_changed(path, a.render_page(segment, metadata, previous_path, None))
    previous_html = previous_path.read_text(encoding="utf-8")
    if path.name not in previous_html:
        previous_html = previous_html.replace("</nav>", ' · <a href="' + escape(path.name, quote=True)
            + '">后一段：' + escape(override["title"]) + '</a></nav>')
        a.write_if_changed(previous_path, previous_html)
    if changed:
        a.write_if_changed(ARCHIVES / "index.html", a.render_index(ARCHIVES))
    paragraphs = "".join("<p>" + escape(p) + "</p>" for p in profile["summary_paragraphs"])
    evidence = "".join('<p><a href="' + escape((ROOT / relative).as_uri(), quote=True) + '">'
        + escape(relative) + '</a></p>' for relative in override["related_paths"]
        if relative != profile["summary"] and relative != profile["previous"]
        and (ROOT / relative).exists())
    summary = f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>{escape(override['title'])}</title>
<style>body{{max-width:980px;margin:40px auto;padding:0 24px;font:17px/1.8 system-ui;background:#101926;color:#e1ebf7}}a{{color:#7cd6ea}}</style>
<h1>{escape(override['title'])}</h1><p>本页为人工整理的简要索引，不代替逐字原文。</p>{paragraphs}
<p>实际用户消息：{escape(metadata['start_time'])}；最后可见文字：{escape(metadata['end_time'])}；{escape(metadata['status'])}，墙钟跨度{metadata['duration_seconds']:.3f}秒，不代表计算时长。</p>
<p><a href="../完整对话归档/{escape(path.name, quote=True)}">本轮对话原文</a> · <a href="../完整对话归档/{escape(previous_path.name, quote=True)}">{escape(profile.get('previous_label', '上一段及其真实结束回复'))}</a></p>
{evidence}
<p>变更记录 #1：按真实用户消息建立独立单段，持续补录可见文字；不保存隐藏思考或工具记录。</p></html>'''
    a.write_if_changed(summary_path, summary)
    result = {"thread_id": THREAD, "segment_id": segment["segment_id"], "archive": str(path), "summary": str(summary_path),
        "message_count": len(segment["messages"]), "last_message_id": segment["messages"][-1]["id"],
        "last_message_time": metadata["end_time"], "status": metadata["status"],
        "previous_final_verified": previous["messages"][-1]["timestamp"] if previous_has_final else None,
        "previous_latest_verified": previous["messages"][-1]["timestamp"], "scope": metadata["completeness"]}
    log = ROOT / profile["status"]
    log.parent.mkdir(parents=True, exist_ok=True)
    a.write_if_changed(log, json.dumps(result, ensure_ascii=False, indent=2))
    return result, bool(segment["closed_reason"])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--watch", action="store_true")
    args = parser.parse_args()
    last = None
    while True:
        result, closed = export(json.loads(args.profile.read_text(encoding="utf-8-sig")))
        signature = (result["message_count"], result["last_message_id"], result["status"])
        if signature != last:
            print(json.dumps(result, ensure_ascii=False), flush=True)
            last = signature
        if closed or not args.watch:
            return
        time.sleep(20)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
