#!/usr/bin/env python3
"""Export visible, text-only Codex dialogue from one exact JSONL history branch.

Only the Python standard library is required (Python 3.9+). This module never
prints transcript content. It deliberately does not infer approval or decisions.
"""

# 【变更记录 #1】2026-10-25（实际导出秒数见档案archived_at）
# 删除：无。新增：人工核对的关联成果路径元数据及本地HTML链接。
# 修改：每段原文与讨论摘要互链，不向原文正文混入工具或自动摘要。
# 用途：压缩后可由完整对话直接找回本次决策与成果；不改变历史消息。

import argparse
import datetime as dt
import hashlib
import html
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import time
from urllib.parse import quote


HONG_KONG = dt.timezone(dt.timedelta(hours=8), "Asia/Hong_Kong")
UNKNOWN = "未提供/未知"
VISIBLE_PHASES = {None, "commentary", "final", "final_answer"}
FINAL_PHASES = {"final", "final_answer"}
METADATA_ID = "archive-metadata"
ENVIRONMENT_TAGS = (
    "in-app-browser-context", "environment_context", "environment-context",
    "environment_details", "environment-details", "app-context",
)
KEYWORD_GROUPS = (
    ("规则", ("规则", "归档", "对话记录", "上下文")),
    ("结构", ("结构", "多方块", "厂房", "建筑")),
    ("控制器接口", ("控制器", "接口", "主控")),
    ("预览", ("预览", "审阅", "审查", "审计")),
    ("电压", ("电压", "qcv", "wsv", "v06")),
    ("实装", ("实装", "部署", "实例", "运行")),
    ("设计", ("设计", "美观", "风格", "贴图", "材质")),
)
MACHINE_RE = re.compile(r"(?<![A-Za-z0-9])I\d{1,3}(?![A-Za-z0-9])", re.I)
META_RE = re.compile(
    r'<script\b(?=[^>]*\bid=[\"\']archive-metadata[\"\'])[^>]*>(.*?)</script\s*>',
    re.I | re.S,
)
TITLE_RE = re.compile(r"<title\b[^>]*>(.*?)</title\s*>", re.I | re.S)


class ArchiveError(Exception):
    """A safe, actionable error that contains no transcript text."""


def parse_timestamp(value):
    if not isinstance(value, str):
        return None
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
        # A timestamp without a UTC offset is not a verifiable wall-clock time.
        return parsed if parsed.tzinfo is not None else None
    except ValueError:
        return None


def local_timestamp(value):
    parsed = parse_timestamp(value)
    return parsed.astimezone(HONG_KONG).isoformat(timespec="seconds") if parsed else None


def session_identity(meta):
    return meta.get("session_id") or meta.get("id")


def read_records(path, limit=None, active=False):
    """Read exact bytes, tolerating only an actively-written final partial line."""
    try:
        with path.open("rb") as stream:
            data = stream.read() if limit is None else stream.read(limit)
    except OSError as exc:
        raise ArchiveError("Cannot read session source: " + path.name) from exc
    if limit is not None and len(data) != limit:
        raise ArchiveError("Parent history cutoff exceeds source length: " + path.name)
    records = []
    lines = data.splitlines(keepends=True)
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line.decode("utf-8-sig" if number == 1 else "utf-8"))
        except (UnicodeError, json.JSONDecodeError) as exc:
            if active and number == len(lines) and not line.endswith((b"\n", b"\r")):
                break
            raise ArchiveError("Invalid JSONL record at %s:%s" % (path.name, number)) from exc
        if not isinstance(record, dict):
            raise ArchiveError("Non-object JSONL record at %s:%s" % (path.name, number))
        records.append(record)
    return records


def get_meta(records, filename):
    for record in records:
        if record.get("type") == "session_meta" and isinstance(record.get("payload"), dict):
            meta = record["payload"]
            if not session_identity(meta):
                break
            return meta
    raise ArchiveError("Missing session identity: " + filename)


def find_sessions_root(path):
    for ancestor in path.parents:
        if ancestor.name.lower() == "sessions":
            return ancestor
    raise ArchiveError("Session must be located below a sessions directory.")


def find_parent(root, branch_id, expected_session_id):
    if not isinstance(branch_id, str) or not re.fullmatch(r"[A-Za-z0-9-]+", branch_id):
        raise ArchiveError("Invalid parent branch ID in history_base.")
    suffix = re.compile(r"(?:_|-)" + re.escape(branch_id) + r"\.jsonl$", re.I)
    matches = []
    for candidate in root.rglob("*" + branch_id + ".jsonl"):
        if not suffix.search(candidate.name):
            continue
        # Read only the header to identify a candidate; never combine namesakes.
        try:
            with candidate.open("rb") as stream:
                header = stream.readline()
            record = json.loads(header.decode("utf-8-sig"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            continue
        meta = record.get("payload", {}) if record.get("type") == "session_meta" else {}
        if session_identity(meta) == expected_session_id:
            matches.append(candidate.resolve())
    if len(matches) != 1:
        raise ArchiveError("Expected one matching parent branch; found %s for %s." % (len(matches), branch_id))
    return matches[0]


def load_branch(path):
    """Follow history_base recursively, respecting each parent's byte cutoff."""
    path = Path(path).resolve()
    root = find_sessions_root(path)
    current_records = read_records(path, active=True)
    current_meta = get_meta(current_records, path.name)
    identity = session_identity(current_meta)
    visited = set()
    sources = []

    def visit(source, records, cutoff):
        source = source.resolve()
        if source in visited:
            raise ArchiveError("Cycle in session history_base.")
        visited.add(source)
        meta = get_meta(records, source.name)
        if session_identity(meta) != identity:
            raise ArchiveError("Parent session identity differs from current session.")
        combined = []
        base = meta.get("history_base")
        if base:
            if not isinstance(base, dict):
                raise ArchiveError("Invalid history_base metadata.")
            offset = base.get("end_byte_offset")
            if isinstance(offset, bool) or not isinstance(offset, int) or offset <= 0:
                raise ArchiveError("Missing or invalid parent end_byte_offset.")
            parent = find_parent(root, base.get("thread_id"), identity)
            parent_records = read_records(parent, limit=offset)
            combined.extend(visit(parent, parent_records, offset))
        sources.append({"filename": source.name, "end_byte_offset": cutoff})
        for record in records:
            record["__archive_source_page"] = source.name
        combined.extend(records)
        return combined

    records = visit(path, current_records, None)
    return records, current_meta, sources


def clean_user_text(text):
    for tag in ENVIRONMENT_TAGS:
        text = re.sub(
            r"<" + re.escape(tag) + r"\b[^>]*>.*?</" + re.escape(tag) + r"\s*>",
            "", text, flags=re.I | re.S,
        )
        text = re.sub(r"<" + re.escape(tag) + r"\b[^>]*/\s*>", "", text, flags=re.I)
    text = re.sub(r"(?im)^\s*##\s*My request\s*:\s*\n?", "", text)
    return text.strip()


def present_question_reply(text):
    match = re.fullmatch(r"\s*<send_user_message_question_reply>\s*(.*?)\s*</send_user_message_question_reply>\s*", text, re.S)
    if not match:
        return text, None
    try:
        values = json.loads(match.group(1))
    except json.JSONDecodeError:
        return text, "用户界面问答包装保留原文（无法解析）"
    if not isinstance(values, list) or not all(isinstance(item, dict) and isinstance(item.get("question"), str) and isinstance(item.get("answer"), str) for item in values):
        return text, "用户界面问答包装保留原文（格式无法核验）"
    return "\n\n".join("问题：%s\n回答：%s" % (item["question"], item["answer"]) for item in values), "用户界面问答JSON按原有question/answer文字呈现；省略包装及内部问题ID"


def redact_credentials(text):
    """Redact recognizable credentials, not arbitrary long words or paths."""
    count = 0

    def replace_secret(match):
        nonlocal count
        count += 1
        return "[凭证已遮盖]"

    patterns = (
        r"\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{16,}\b",
        r"\bgh[pousr]_[A-Za-z0-9]{20,}\b",
        r"\bgithub_pat_[A-Za-z0-9_]{20,}\b",
        r"\bAKIA[A-Z0-9]{16}\b",
        r"(?i)\bBearer\s+[A-Za-z0-9._~+/-]{16,}=*",
    )
    for pattern in patterns:
        text = re.sub(pattern, replace_secret, text)
    credential_name = r"(?:api[_ -]?key|access[_ -]?token|auth[_ -]?token|client[_ -]?secret|password|passwd|密钥|密码)"
    assignment = re.compile(
        r"(?i)(\b" + credential_name + r"\b\s*[:=：]\s*)(?:([\"'])([^\r\n]*?)\2|([^\s,;<>]+))"
    )

    def replace_assignment(match):
        nonlocal count
        # Do not count a secret twice after the explicit token patterns above.
        if "[凭证已遮盖]" in (match.group(3) or match.group(4) or ""):
            return match.group(0)
        count += 1
        marker = "[凭证已遮盖]"
        return match.group(1) + ((match.group(2) or "") + marker + (match.group(2) or ""))

    return assignment.sub(replace_assignment, text), count


def extract_message(record):
    payload = record.get("payload")
    if not isinstance(payload, dict):
        return None
    source = "response_item"
    timestamp = record.get("timestamp")
    timestamp_source = "JSONL record timestamp"
    if record.get("type") == "event_msg" and payload.get("type") == "item_completed":
        item = payload.get("item", {})
        if item.get("type") not in ("UserMessage", "AgentMessage"):
            return None
        role = "user" if item["type"] == "UserMessage" else "assistant"
        phase = item.get("phase")
        content_types = {"Text", "text"}
        source = "event_msg.item_completed"
        # Record timestamp is preserved. started/completed times are supplemental
        # provenance rather than substitutes for the source message timestamp.
        started = payload.get("started_at_ms")
        completed = payload.get("completed_at_ms")
        payload = item
    elif record.get("type") == "response_item" and payload.get("type") == "message":
        role = payload.get("role")
        phase = payload.get("phase")
        content_types = {"input_text", "output_text"}
        started = completed = None
    else:
        return None
    if role not in {"user", "assistant"}:
        return None
    if payload.get("recipient") not in (None, "all"):
        return None
    if role == "assistant" and phase not in VISIBLE_PHASES:
        return None
    parts = []
    for part in payload.get("content", []):
        if isinstance(part, dict) and part.get("type") in content_types:
            if isinstance(part.get("text"), str):
                parts.append(part["text"])
    text = "\n".join(parts)
    presentation_note = None
    if role == "user":
        text = clean_user_text(text)
        text, presentation_note = present_question_reply(text)
    if not text.strip():
        return None
    identity = payload.get("id")
    if not isinstance(identity, str) or not identity:
        fallback = json.dumps([timestamp, role, text], ensure_ascii=False, separators=(",", ":"))
        identity = "fallback-" + hashlib.sha256(fallback.encode("utf-8")).hexdigest()
    safe_text, redactions = redact_credentials(text)
    return {
        "id": identity, "role": role, "phase": phase,
        "timestamp": timestamp, "text": safe_text, "redactions": redactions,
        "source_kind": source, "timestamp_source": timestamp_source,
        "source_page": record.get("__archive_source_page"),
        "started_at_ms": started, "completed_at_ms": completed,
        "delivery": payload.get("delivery"),
        "presentation_note": presentation_note,
    }


def setting_at(record, previous):
    payload = record.get("payload", {})
    setting = dict(previous)
    for key in ("model", "effort"):
        if key in payload:
            setting[key] = payload[key] if payload[key] is not None else UNKNOWN
    return setting


def append_setting(segment, setting, timestamp):
    item = {"timestamp": timestamp, "model": setting["model"], "effort": setting["effort"]}
    changes = segment["model_settings"]
    if not changes or any(changes[-1][key] != item[key] for key in ("model", "effort")):
        changes.append(item)


def user_comparison_text(text):
    # 双通道的空附件包装不同；仅用于去重，正文与路径保持原样。
    return re.sub(r"<image\b[^>]*>\s*</image\s*>", "", text, flags=re.I).strip()


def segment_dialogue(records, thread_id):
    segments = []
    active = None
    seen = set()
    setting = {"model": UNKNOWN, "effort": UNKNOWN}
    project_path = UNKNOWN
    turn_id = None
    event_message_ids = set()
    duplicate_user_events = set()
    preceding = None
    for record in records:
        message = extract_message(record)
        if message is None:
            continue
        if record.get("type") == "event_msg":
            event_message_ids.add(message["id"])
            if preceding and preceding["role"] == message["role"] == "user" and preceding["source_kind"] == "response_item" and preceding["id"] != message["id"] and user_comparison_text(preceding["text"]) == user_comparison_text(message["text"]):
                before = parse_timestamp(preceding["timestamp"])
                after = parse_timestamp(message["timestamp"])
                # 同一用户消息可被双通道赋予不同ID；仅配对连续同文且50毫秒内的记录，保留既有档案身份。
                if before and after and 0 <= (after - before).total_seconds() <= 0.05:
                    duplicate_user_events.add(message["id"])
        preceding = message
    for record in records:
        if record.get("type") == "turn_context":
            setting = setting_at(record, setting)
            if record.get("payload", {}).get("cwd"):
                project_path = record["payload"]["cwd"]
            if record.get("payload", {}).get("turn_id"):
                turn_id = record["payload"]["turn_id"]
            continue
        payload = record.get("payload", {})
        if record.get("type") == "event_msg" and isinstance(payload, dict) and payload.get("type") == "task_started":
            turn_id = payload.get("turn_id") or turn_id
            continue
        if record.get("type") == "event_msg" and isinstance(payload, dict) and payload.get("type") == "task_complete":
            if active is not None:
                active["closed_reason"] = "task_complete"
            continue
        message = extract_message(record)
        if message is not None and message["source_kind"] == "event_msg.item_completed" and message["id"] in duplicate_user_events:
            continue
        if message is not None and message["source_kind"] == "response_item" and message["id"] in event_message_ids:
            continue
        if message is None or message["id"] in seen:
            continue
        seen.add(message["id"])
        if message["role"] == "user":
            if active is not None and not active["closed_reason"]:
                active["closed_reason"] = "next_user"
            digest = hashlib.sha256((str(thread_id) + "\0" + message["id"]).encode("utf-8")).hexdigest()
            active = {
                "segment_id": digest[:24], "messages": [message],
                "model_settings": [], "closed_reason": None, "project_paths": [], "turn_ids": [],
            }
            append_setting(active, setting, message["timestamp"])
            segments.append(active)
        elif active is not None:
            append_setting(active, setting, message["timestamp"])
            active["messages"].append(message)
            if is_terminal_record(record):
                active["closed_reason"] = "final"
        if active is not None:
            effective_turn_id = record.get("payload", {}).get("turn_id") or turn_id
            if effective_turn_id and effective_turn_id not in active["turn_ids"]:
                active["turn_ids"].append(effective_turn_id)
            paths = active["project_paths"]
            if not paths or paths[-1]["path"] != project_path:
                paths.append({"timestamp": message["timestamp"], "path": project_path})
    return segments


def infer_search_fields(messages):
    text = "\n".join(message["text"] for message in messages)
    lowered = text.lower()
    keywords = [label for label, needles in KEYWORD_GROUPS if any(needle in lowered for needle in needles)]
    machines = sorted(set(match.upper() for match in MACHINE_RE.findall(text)), key=lambda value: int(value[1:]))
    keywords.extend(machines)
    conversation_type = "项目讨论"
    if "规则" in keywords:
        conversation_type = "规则与记录"
    elif "设计" in keywords or "结构" in keywords:
        conversation_type = "结构设计与修订"
    elif "实装" in keywords:
        conversation_type = "实装与验证"
    title = next((line.strip().lstrip("#").strip() for line in messages[0]["text"].splitlines() if line.strip()), "项目对话")
    title = title[:72] + ("…" if len(title) > 72 else "")
    return title, conversation_type, keywords, ["#" + item for item in keywords], machines


def read_page_metadata(path):
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return None
    match = META_RE.search(content)
    if not match:
        return None
    try:
        result = json.loads(match.group(1))
        return result if isinstance(result, dict) else None
    except json.JSONDecodeError:
        raise ArchiveError("Invalid archive metadata: " + path.name)


def existing_pages(out_dir):
    by_id = {}
    for path in sorted(out_dir.glob("*.html")):
        if path.name == "index.html":
            continue
        metadata = read_page_metadata(path)
        if metadata and metadata.get("segment_id"):
            segment_id = metadata["segment_id"]
            if segment_id in by_id:
                raise ArchiveError("Duplicate existing segment_id; resolve pages before exporting.")
            by_id[segment_id] = (path, metadata)
    return by_id


def build_metadata(segment, thread_meta, sources, previous=None, override=None):
    previous = previous or {}
    override = override or {}
    messages = segment["messages"]
    title, kind, keywords, tags, machines = infer_search_fields(messages)
    start = parse_timestamp(messages[0]["timestamp"])
    end = parse_timestamp(messages[-1]["timestamp"])
    duration = (end - start).total_seconds() if start and end and end >= start else None
    now = dt.datetime.now(HONG_KONG).isoformat(timespec="seconds")
    paths = segment["project_paths"]
    project_path = paths[-1]["path"] if paths else UNKNOWN
    if project_path == UNKNOWN:
        project_path = thread_meta.get("cwd") or UNKNOWN
    metadata = {
        "schema_version": 1, "segment_id": segment["segment_id"],
        "thread_id": session_identity(thread_meta),
        "turn_ids": segment["turn_ids"],
        "project_path": project_path,
        "project_path_source": "该段消息所在turn_context.cwd；缺失时回退session_meta.cwd",
        "project_path_changes": paths,
        "source_session_project_path": thread_meta.get("cwd") or UNKNOWN,
        "title": previous.get("title", title), "conversation_type": kind,
        "start_time": local_timestamp(messages[0]["timestamp"]),
        "end_time": local_timestamp(messages[-1]["timestamp"]),
        "duration_seconds": duration,
        "duration_basis": "首条真实用户消息至最后一条可见文字消息的墙钟跨度；不代表模型计算时长",
        "status": "已结束" if segment["closed_reason"] else "进行中",
        "closed_reason": segment["closed_reason"],
        "timezone": "Asia/Hong_Kong (UTC+08:00)",
        "filename_time_basis": "首条用户消息时间" if start else "首次归档时间（消息时间未提供）",
        "keywords": keywords, "tags": tags, "machines": machines,
        "model_settings": segment["model_settings"],
        "confirmed_decisions": "未自动推定，请见原文",
        "pending_items": "未自动推定，请见原文",
        "related_paths": previous.get("related_paths", []),
        "transcript_scope": "指定JSONL分支及history_base字节边界内可见用户/助手文字；不含工具、思考、摘要和图像数据",
        "completeness": "该源分支可获取的文字记录；无法证明平台未提供的历史是否完整",
        "redaction_count": sum(message["redactions"] for message in messages),
        "custom_metadata": previous.get("custom_metadata", {}),
        "archived_at": previous.get("archived_at", now),
        "source_chain": sources,
        "messages": [
            {key: message[key] for key in ("id", "role", "phase", "timestamp", "redactions", "source_kind", "source_page", "timestamp_source", "started_at_ms", "completed_at_ms", "presentation_note")}
            for message in messages
        ],
    }
    # Existing hand-edited titles take precedence, unless an explicit override
    # is now supplied by the human-reviewed topic map. custom_metadata is never
    # replaced by automatic fields or override values.
    mapping = {"title": "title", "kind": "conversation_type", "keywords": "keywords",
               "tags": "tags", "machines": "machines", "confirmed_decisions": "confirmed_decisions",
               "pending": "pending_items", "related_paths": "related_paths"}
    for source_key, target_key in mapping.items():
        if source_key in override:
            metadata[target_key] = override[source_key]
    return metadata


def safe_json(value):
    return (json.dumps(value, ensure_ascii=False, indent=2)
            .replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e")
            .replace("\u2028", "\\u2028").replace("\u2029", "\\u2029"))


def escape(value):
    return html.escape(str(value), quote=True)


def display_values(value):
    return "\n".join(str(item) for item in value) if isinstance(value, list) else str(value)


def page_link(path, label):
    return '<a href="%s">%s</a>' % (escape(quote(path.name)), escape(label))


CSS = """
:root{color-scheme:light dark}body{max-width:1050px;margin:30px auto;padding:0 22px;font:16px/1.65 system-ui,'Microsoft YaHei',sans-serif}
h1{font-size:1.7rem;line-height:1.3}nav{display:flex;gap:20px;flex-wrap:wrap;margin:20px 0}a{color:#3687be}
.meta{padding:18px;background:rgba(100,130,160,.1);border-left:4px solid #5286a6}dt{font-weight:700}dd{margin:0 0 10px;overflow-wrap:anywhere}
.message{border-top:1px solid #8886;padding:18px 0}.role{font-weight:700}.time{font-size:.85rem;opacity:.7;margin-left:12px}
.text{white-space:pre-wrap;overflow-wrap:anywhere}.note{font-size:.9rem;opacity:.8}.search{width:100%;box-sizing:border-box;font:inherit;padding:12px;margin:12px 0}
.entry{border-bottom:1px solid #8886;padding:16px 0}.entry small{display:block;opacity:.75}[hidden]{display:none!important}
"""


def navigation(previous_page, next_page):
    links = ['<a href="index.html">目录与搜索</a>']
    if previous_page:
        links.append(page_link(previous_page, "上一段"))
    if next_page:
        links.append(page_link(next_page, "下一段"))
    return "<nav>" + "".join(links) + "</nav>"


def render_page(segment, metadata, previous_page=None, next_page=None):
    model_text = "\n".join(
        "%s | %s | 思考等级：%s" % (local_timestamp(item["timestamp"]) or UNKNOWN, item["model"], item["effort"])
        for item in metadata["model_settings"]
    )
    duration = "%g 秒" % metadata["duration_seconds"] if metadata["duration_seconds"] is not None else UNKNOWN
    fields = [
        ("种类", metadata["conversation_type"]), ("线程ID", metadata["thread_id"]),
        ("项目路径", metadata["project_path"]),
        ("开始时间", metadata["start_time"] or UNKNOWN),
        ("最后可见消息时间", metadata["end_time"] or UNKNOWN),
        ("状态与持续时间", metadata["status"] + "；" + duration),
        ("时长口径", metadata["duration_basis"]),
        ("关键词与标签", "、".join(metadata["keywords"]) + "  " + " ".join(metadata["tags"])),
        ("AI Agent / 模型 / 思考等级（设置变化）", model_text),
        ("已确认决定（人工整理；未自动推定）", display_values(metadata["confirmed_decisions"])),
        ("待办（人工整理；未自动推定）", display_values(metadata["pending_items"])),
        ("转录范围", metadata["transcript_scope"]), ("完整度", metadata["completeness"]),
        ("凭证遮盖", "%s 处" % metadata["redaction_count"]),
    ]
    if metadata["custom_metadata"]:
        fields.append(("人工补充元数据", json.dumps(metadata["custom_metadata"], ensure_ascii=False, indent=2)))
    meta_html = "".join("<dt>%s</dt><dd class=\"text\">%s</dd>" % (escape(key), escape(value)) for key, value in fields)
    related = []
    for value in metadata.get("related_paths", []):
        target = Path(value)
        if not target.is_absolute():
            target = Path(metadata["project_path"]) / target
        if target.is_absolute():
            related.append('<a href="%s">%s</a>' % (escape(target.as_uri()), escape(value)))
    if related:
        meta_html += '<dt>关联讨论与成果（人工核对）</dt><dd>' + '<br>'.join(related) + '</dd>'
    messages_html = []
    for message in segment["messages"]:
        messages_html.append(
            '<section class="message"><span class="role">%s</span><span class="time">%s</span><div class="text">%s</div></section>'
            % ("用户" if message["role"] == "user" else "助手", escape(local_timestamp(message["timestamp"]) or UNKNOWN), escape(message["text"])))
        if message["presentation_note"]:
            messages_html.append('<p class="note">呈现说明：%s</p>' % escape(message["presentation_note"]))
    nav = navigation(previous_page, next_page)
    return ('<!doctype html>\n<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>%s</title><style>%s</style><script id="%s" type="application/json">%s</script></head><body>'
            '<h1>%s</h1>%s<dl class="meta">%s</dl><h2>对话原文</h2>%s%s</body></html>\n') % (
                escape(metadata["title"]), CSS, METADATA_ID, safe_json(metadata), escape(metadata["title"]),
                nav, meta_html, "".join(messages_html), nav,
            )


def filename_for(metadata):
    start = parse_timestamp(metadata["start_time"]) or parse_timestamp(metadata["archived_at"])
    stamp = start.astimezone(HONG_KONG).strftime("%Y-%m-%d_%H-%M-%S")
    title = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", metadata["title"]).strip(" .")[:45] or "项目对话"
    return "%s_%s_%s.html" % (stamp, title, metadata["segment_id"][:10])


def write_if_changed(path, content):
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    temporary = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="\n", dir=str(path.parent), delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(content)
        os.replace(str(temporary), str(path))
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()
    return True


def render_index(out_dir):
    entries = []
    for path in out_dir.glob("*.html"):
        if path.name == "index.html":
            continue
        metadata = read_page_metadata(path)
        if metadata is None:
            # Leave manual archives intact, and keep them discoverable.
            title_match = TITLE_RE.search(path.read_text(encoding="utf-8"))
            title = html.unescape(title_match.group(1)) if title_match else path.stem
            metadata = {"title": title, "tags": ["#人工旧档"], "keywords": [], "machines": [], "status": "人工档案；未自动改写", "start_time": None}
        entries.append((path, metadata))
    entries.sort(key=lambda item: (item[1].get("start_time") or item[0].name, item[0].name))
    cards = []
    for path, metadata in entries:
        title = metadata.get("title") or path.stem
        date = metadata.get("start_time") or path.name[:19]
        tags = " ".join(metadata.get("tags", []))
        machines = " ".join(metadata.get("machines", []))
        search = " ".join([str(date), title, tags, machines, " ".join(metadata.get("keywords", []))]).lower()
        cards.append('<article class="entry" data-search="%s">%s<small>%s · %s · %s</small><small>%s</small></article>' % (
            escape(search), page_link(path, title), escape(date), escape(metadata.get("status", UNKNOWN)), escape(machines), escape(tags)))
    return ('<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>完整对话归档 · 检索</title><style>%s</style></head><body><h1>完整对话归档</h1>'
            '<p>按日期、标题、标签、机器编号检索。原文和模型设置以各段档案为准。</p>'
            '<input class="search" id="search" type="search" placeholder="例如：2026-10-24 I23 控制器" aria-label="搜索对话归档">'
            '<p class="note" id="count"></p><main>%s</main>'
            '<script>const q=document.getElementById("search"),rows=[...document.querySelectorAll(".entry")];'
            'function filter(){const terms=q.value.toLowerCase().trim().split(/\\s+/).filter(Boolean);let n=0;'
            'for(const row of rows){row.hidden=!terms.every(t=>row.dataset.search.includes(t));if(!row.hidden)n++;}'
            'document.getElementById("count").textContent=n+" / "+rows.length+" 段对话";}q.addEventListener("input",filter);filter();</script>'
            '</body></html>\n') % (CSS, "".join(cards))


def load_overrides(path):
    if path is None:
        return {}
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ArchiveError("Cannot read topic override JSON.") from exc
    if not isinstance(value, dict) or not all(isinstance(key, str) and isinstance(item, dict) for key, item in value.items()):
        raise ArchiveError("Topic override JSON must map message IDs to metadata objects.")
    for item in value.values():
        for key in ("title", "kind"):
            if key in item and not isinstance(item[key], str):
                raise ArchiveError("Topic override title/kind must be strings.")
        for key in ("keywords", "tags", "machines", "confirmed_decisions", "pending", "related_paths"):
            if key in item and not (isinstance(item[key], list) and all(isinstance(part, str) for part in item[key])):
                raise ArchiveError("Topic override list fields must contain strings.")
    return value


def export_archive(session, out_dir, overrides=None):
    records, thread_meta, sources = load_branch(session)
    segments = segment_dialogue(records, session_identity(thread_meta))
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    existing = existing_pages(out_dir)
    pages = []
    overrides = overrides or {}
    for segment in segments:
        old = existing.get(segment["segment_id"])
        metadata = build_metadata(segment, thread_meta, sources, old[1] if old else None, overrides.get(segment["messages"][0]["id"]))
        path = old[0] if old else out_dir / filename_for(metadata)
        if not old and path.exists():
            raise ArchiveError("Generated filename already belongs to another archive: " + path.name)
        pages.append((segment, metadata, path))
    changed = 0
    for index, (segment, metadata, path) in enumerate(pages):
        previous_page = pages[index - 1][2] if index else None
        next_page = pages[index + 1][2] if index + 1 < len(pages) else None
        changed += write_if_changed(path, render_page(segment, metadata, previous_page, next_page))
    changed += write_if_changed(out_dir / "index.html", render_index(out_dir))
    return {"thread_id": session_identity(thread_meta), "segments": len(segments), "files_changed": changed,
            "source_files": len(sources), "latest_status": "已结束" if segments and segments[-1]["closed_reason"] else "进行中"}


def is_terminal_record(record):
    payload = record.get("payload", {})
    if not isinstance(payload, dict):
        return False
    if record.get("type") == "event_msg" and payload.get("type") == "task_complete":
        return True
    if record.get("type") == "event_msg" and payload.get("type") == "item_completed":
        item = payload.get("item", {})
        # 异步提问是可见文字，但即使标为final_answer也不代表本轮结束。
        return (item.get("type") == "AgentMessage" and item.get("phase") in FINAL_PHASES
                and item.get("delivery") != "async")
    return (record.get("type") == "response_item" and payload.get("type") == "message"
            and payload.get("role") == "assistant" and payload.get("phase") in FINAL_PHASES
            and payload.get("delivery") != "async")


def watch_until_complete(session, timeout):
    # Only new terminal events after startup count. Historical finals must not
    # make a watcher exit before the current reply has been fully written.
    offset = session.stat().st_size
    pending = b""
    if offset:
        # A process may have just written half a JSONL line at startup. Retain
        # that tail so the later continuation can be parsed as one record.
        with session.open("rb") as stream:
            initial_tail = stream.read(offset).rsplit(b"\n", 1)[-1]
        pending = initial_tail
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        size = session.stat().st_size
        if size < offset:
            raise ArchiveError("Session was truncated while watching; refusing to switch histories.")
        if size > offset:
            with session.open("rb") as stream:
                stream.seek(offset)
                chunk = stream.read()
            offset += len(chunk)
            pending += chunk
            lines = pending.split(b"\n")
            pending = lines.pop()
            for line in lines:
                if not line.strip():
                    continue
                try:
                    record = json.loads(line.decode("utf-8"))
                except (UnicodeError, json.JSONDecodeError) as exc:
                    raise ArchiveError("Invalid appended JSONL record while watching.") from exc
                if is_terminal_record(record):
                    return True
        time.sleep(min(0.5, max(0.0, deadline - time.monotonic())))
    return False


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session", required=True, type=Path, help="Absolute path of the exact active JSONL session file")
    parser.add_argument("--out-dir", required=True, type=Path, help="HTML archive directory")
    parser.add_argument("--watch", action="store_true", help="Wait for the current round's final/task_complete, then export")
    parser.add_argument("--overrides", type=Path, help="Reviewed topic metadata JSON keyed by real user message ID")
    parser.add_argument("--timeout", type=float, default=1800, help="Watch timeout in seconds, 0 < timeout <= 1800")
    args = parser.parse_args(argv)
    if not args.session.is_absolute():
        parser.error("--session must be an absolute path")
    if not 0 < args.timeout <= 1800:
        parser.error("--timeout must be greater than zero and at most 1800")
    try:
        completed = watch_until_complete(args.session, args.timeout) if args.watch else None
        result = export_archive(args.session, args.out_dir, load_overrides(args.overrides))
        if args.watch:
            result["watch_completed"] = completed
        print(json.dumps(result, ensure_ascii=True))
        return 2 if args.watch and not completed else 0
    except (ArchiveError, OSError) as exc:
        # These diagnostics include paths/record positions, never record content.
        print("Archive error: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
