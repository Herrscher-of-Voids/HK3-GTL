"""Small synthetic fixtures; no real session text is written or printed."""

import importlib.util
import json
from pathlib import Path
import tempfile
import threading
import time
import unittest


MODULE_PATH = Path(__file__).with_name("archive_dialogue.py")
SPEC = importlib.util.spec_from_file_location("archive_dialogue", MODULE_PATH)
archive = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(archive)


def record(kind, payload, second=0):
    return {"type": kind, "timestamp": "2026-10-24T10:00:%02dZ" % second, "payload": payload}


def meta(branch=None, cutoff=None, identity="thread-1"):
    payload = {"session_id": identity, "id": identity, "cwd": "C:/old-project"}
    if branch:
        payload["history_base"] = {"thread_id": branch, "end_byte_offset": cutoff}
    return record("session_meta", payload)


def response(role, text, identity=None, phase=None, second=1, content=None):
    payload = {"type": "message", "role": role, "content": content if content is not None else [{"type": "input_text" if role == "user" else "output_text", "text": text}]}
    if identity is not None:
        payload["id"] = identity
    if phase is not None:
        payload["phase"] = phase
    return record("response_item", payload, second)


def event(role, text, identity=None, phase=None, second=1, turn_id="turn-1"):
    item = {"type": "UserMessage" if role == "user" else "AgentMessage", "content": [{"type": "text" if role == "user" else "Text", "text": text}]}
    if identity is not None:
        item["id"] = identity
    if phase is not None:
        item["phase"] = phase
    return record("event_msg", {"type": "item_completed", "turn_id": turn_id, "item": item, "started_at_ms": 1234, "completed_at_ms": 2345}, second)


def as_bytes(records):
    return b"".join((json.dumps(item, ensure_ascii=False) + "\n").encode("utf-8") for item in records)


class ArchiveFixtures(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.sessions = self.root / "sessions" / "2026" / "10" / "24"
        self.sessions.mkdir(parents=True)
        self.current = self.sessions / "rollout-thread-1_child.jsonl"
        self.out = self.root / "archive"

    def tearDown(self):
        self.temporary.cleanup()

    def write(self, records, path=None):
        (path or self.current).write_bytes(as_bytes(records))

    def test_visible_text_boundaries_and_environment_only_user(self):
        records = [
            meta(),
            response("user", '<environment_context>automatic</environment_context>', "environment"),
            response("user", '<in-app-browser-context source="ambient">automatic UI</in-app-browser-context>\n## My request:\n真实要求 <b>原文</b>', "u1"),
            response("developer", "must not leak", "dev"),
            response("assistant", "analysis secret", "analysis", "analysis"),
            record("compacted", {"message": "compacted secret", "replacement_history": [response("user", "fake user", "fake")]}),
            record("response_item", {"type": "reasoning", "summary": [{"text": "reasoning secret"}]}),
            record("response_item", {"type": "agent_message", "content": [{"type": "input_text", "text": "subagent secret"}]}),
            record("response_item", {"type": "function_call_output", "output": "tool secret"}),
            response("assistant", "旧版可见文字", "old", second=2),
            response("assistant", "最后回复", "a1", "final_answer", second=3),
        ]
        segments = archive.segment_dialogue(records, "thread-1")
        self.assertEqual(len(segments), 1)
        self.assertEqual([item["text"] for item in segments[0]["messages"]], ["真实要求 <b>原文</b>", "旧版可见文字", "最后回复"])
        self.assertEqual(segments[0]["closed_reason"], "final")

    def test_parent_cutoff_recursive_identity_and_discarded_sibling(self):
        grand = self.sessions / "rollout-thread-1_grand.jsonl"
        parent = self.sessions / "rollout-thread-1_parent.jsonl"
        grand_good = as_bytes([meta(), response("user", "第一段", "u0")])
        grand.write_bytes(grand_good + as_bytes([response("user", "废弃的祖父后续", "discarded-grand")]))
        parent_good = as_bytes([meta("grand", len(grand_good)), response("assistant", "父分支保留", "a0", "commentary", 2)])
        parent.write_bytes(parent_good + as_bytes([response("user", "废弃的父后续", "discarded-parent")]))
        # Same thread, unrelated sibling must never be merged.
        self.write([meta(), response("user", "废弃兄弟", "discarded-sibling")], self.sessions / "rollout-thread-1_sibling.jsonl")
        self.write([meta("parent", len(parent_good)), response("assistant", "现分支结尾", "a1", "final_answer", 3)])
        records, source_meta, chain = archive.load_branch(self.current)
        segments = archive.segment_dialogue(records, archive.session_identity(source_meta))
        self.assertEqual(len(chain), 3)
        self.assertEqual([item["text"] for item in segments[0]["messages"]], ["第一段", "父分支保留", "现分支结尾"])
        parent.write_bytes(as_bytes([meta(identity="wrong-thread")]) + parent_good)
        with self.assertRaises(archive.ArchiveError):
            archive.load_branch(self.current)

    def test_dedup_ids_not_text_and_event_is_primary(self):
        records = [meta(), response("user", "重复源用户", "event-u"), event("user", "真实用户", "event-u"),
                   response("assistant", "重复源助手", "a1", "final_answer"),
                   event("assistant", "同样回答", "a1", "commentary", 2),
                   event("assistant", "同样回答", "a1", "commentary", 2),
                   event("assistant", "同样回答", None, "commentary", 3),
                   event("assistant", "同样回答", None, "final_answer", 4)]
        segments = archive.segment_dialogue(records, "thread-1")
        self.assertEqual(len(segments), 1)
        self.assertEqual(segments[0]["messages"][0]["id"], "event-u")
        self.assertEqual(len(segments[0]["messages"]), 4)
        self.assertEqual(len({message["id"] for message in segments[0]["messages"]}), 4)

    def test_event_on_same_source_page_does_not_drop_other_response_messages(self):
        records = [
            meta(),
            response("user", "用户原文", "u1", second=1),
            response("assistant", "重复来源", "a1", "commentary", second=2),
            event("assistant", "事件来源", "a1", "commentary", second=2),
            event("assistant", "最终可见回复", "a2", "final_answer", second=3),
        ]
        for item in records:
            item["__archive_source_page"] = "same-page.jsonl"

        segments = archive.segment_dialogue(records, "thread-1")

        self.assertEqual(len(segments), 1)
        self.assertEqual(
            [(message["role"], message["text"]) for message in segments[0]["messages"]],
            [("user", "用户原文"), ("assistant", "事件来源"), ("assistant", "最终可见回复")],
        )

    def test_different_user_ids_in_adjacent_dual_source_records_are_one_message(self):
        first = response("user", "同一用户原文", "response-u", second=1)
        twin = event("user", "同一用户原文", "event-u", second=1)
        twin["timestamp"] = "2026-10-24T10:00:01.002Z"
        later = response("user", "同一用户原文", "later-u", second=2)
        later_twin = event("user", "同一用户原文", "later-event", second=2)
        later_twin["timestamp"] = "2026-10-24T10:00:02.002Z"
        segments = archive.segment_dialogue([meta(), first, twin, later, later_twin], "thread-1")
        self.assertEqual([segment["messages"][0]["id"] for segment in segments], ["response-u", "later-u"])
        # 相同文本的独立消息仍须保留，不能按文本永久去重。
        distant_event = event("user", "同一用户原文", "independent-event", second=3)
        segments = archive.segment_dialogue([meta(), first, distant_event], "thread-1")
        self.assertEqual(len(segments), 2)

    def test_attachment_wrapper_difference_keeps_one_original_user_message(self):
        text = '附件路径 C:/Temp/reference.webp\n按原作黑色车体设计'
        original = text + '\n\n<image name="reference" path="C:/Temp/reference.webp">\n</image>'
        first = response("user", original, "response-u")
        twin = event("user", text, "event-u")
        twin["timestamp"] = "2026-10-24T10:00:01.004Z"
        reply = event("assistant", "收到", "a1", "commentary", second=2)
        segments = archive.segment_dialogue([meta(), first, twin, reply], "thread-1")
        self.assertEqual(len(segments), 1)
        self.assertEqual([m["id"] for m in segments[0]["messages"]], ["response-u", "a1"])
        self.assertEqual(segments[0]["messages"][0]["text"], original)

    def test_escape_metadata_preservation_overrides_and_idempotence(self):
        text = 'I23 结构 <script>alert("x")</script> & </script>'
        self.write([meta(), event("user", text, "u1"), event("assistant", "最终可见答复", "a1", "final_answer", 5)])
        self.out.mkdir()
        manual = self.out / "人工旧档.html"
        manual.write_text("<title>旧档保留</title>手工原文", encoding="utf-8")
        overrides = {"u1": {"title": "人工标题", "kind": "结构讨论", "keywords": ["结构"], "tags": ["#结构"], "machines": ["I23"], "confirmed_decisions": ["仅建议；待用户确认"], "pending": ["继续设计"]}}
        result = archive.export_archive(self.current, self.out, overrides)
        self.assertEqual(result["segments"], 1)
        pages = archive.existing_pages(self.out)
        page, metadata = next(iter(pages.values()))
        content = page.read_text(encoding="utf-8")
        self.assertIn("&lt;script&gt;", content)
        self.assertNotIn('<script>alert("x")</script>', content)
        self.assertIn("最终可见答复", content)
        self.assertIn("继续设计", content)
        self.assertNotIn(text, json.dumps(metadata, ensure_ascii=False))
        self.assertEqual(metadata["title"], "人工标题")
        self.assertEqual(metadata["start_time"], "2026-10-24T18:00:01+08:00")
        self.assertEqual(metadata["duration_seconds"], 4)
        self.assertEqual(metadata["messages"][0]["id"], "u1")
        metadata["title"] = "保留的自定义标题"
        metadata["custom_metadata"] = {"人工标签": "保留"}
        updated = archive.META_RE.sub(lambda match: '<script id="archive-metadata" type="application/json">' + archive.safe_json(metadata) + "</script>", content)
        page.write_text(updated, encoding="utf-8")
        archive.export_archive(self.current, self.out)
        saved = archive.read_page_metadata(page)
        self.assertEqual(saved["title"], "保留的自定义标题")
        self.assertEqual(saved["custom_metadata"], {"人工标签": "保留"})
        self.assertEqual(archive.export_archive(self.current, self.out)["files_changed"], 0)
        self.assertEqual(manual.read_text(encoding="utf-8"), "<title>旧档保留</title>手工原文")
        self.assertEqual(len(list(self.out.glob("*.html"))), 3)

    def test_model_changes_resume_paths_turns_and_unknown_model(self):
        records = [meta(), event("user", "旧轮", "u1"),
                   event("assistant", "首轮未知模型", "a1", "final_answer", 2),
                   record("turn_context", {"model": "gpt-6-astra", "effort": "medium", "cwd": "C:/HK3GTL", "turn_id": "resumed-turn"}, 3),
                   event("assistant", "续跑不丢", "a2", "commentary", 4, "resumed-turn"),
                   record("turn_context", {"model": "gpt-6.1-sol", "effort": "ultra", "cwd": "C:/HK3GTL", "turn_id": "new-turn"}, 5),
                   event("user", "新轮", "u2", second=6, turn_id="new-turn"),
                   event("assistant", "最终", "a3", "final_answer", 7, "new-turn")]
        segments = archive.segment_dialogue(records, "thread-1")
        self.assertEqual(len(segments), 2)
        self.assertEqual([item["model"] for item in segments[0]["model_settings"]], [archive.UNKNOWN, "gpt-6-astra"])
        self.assertIn("resumed-turn", segments[0]["turn_ids"])
        metadata = archive.build_metadata(segments[1], {"id": "thread-1", "cwd": "C:/old-project"}, [])
        self.assertEqual(metadata["project_path"], "C:/HK3GTL")
        self.assertEqual(metadata["source_session_project_path"], "C:/old-project")
        self.assertEqual(metadata["model_settings"][0]["effort"], "ultra")

    def test_question_wrapper_image_no_base64_and_credential_redaction(self):
        wrapper = '<send_user_message_question_reply>' + json.dumps([{"questionItemId": "internal", "question": "怎么处理？", "answer": "下一台"}], ensure_ascii=False) + '</send_user_message_question_reply>'
        reply = archive.extract_message(response("user", wrapper, "u1"))
        self.assertEqual(reply["text"], "问题：怎么处理？\n回答：下一台")
        self.assertTrue(reply["presentation_note"])
        message = archive.extract_message(response("user", "", "u2", content=[{"type": "input_image", "image_url": "data:image/png;base64,SECRET"}, {"type": "input_text", "text": "附件路径 C:/Temp/image.png\napi_key=sk-abcdefghijklmnopqrstuvwxyz123456"}]))
        self.assertNotIn("SECRET", message["text"])
        self.assertNotIn("sk-", message["text"])
        self.assertIn("C:/Temp/image.png", message["text"])
        self.assertGreater(message["redactions"], 0)

    def test_async_question_is_visible_but_does_not_close_segment(self):
        question = event("assistant", "目标手机型号是什么？", "q1", "final_answer", 2)
        question["payload"]["item"]["delivery"] = "async"
        records = [meta(), event("user", "请优化", "u1"), question]
        segments = archive.segment_dialogue(records, "thread-1")
        self.assertEqual([item["text"] for item in segments[0]["messages"]], ["请优化", "目标手机型号是什么？"])
        self.assertIsNone(segments[0]["closed_reason"])
        self.assertEqual(segments[0]["messages"][-1]["delivery"], "async")
        self.assertFalse(archive.is_terminal_record(question))
        final = event("assistant", "最终回复", "a1", "final_answer", 3)
        self.assertTrue(archive.is_terminal_record(final))
        self.assertEqual(archive.segment_dialogue(records + [final], "thread-1")[0]["closed_reason"], "final")

    def test_watch_ignores_old_final_and_async_question_then_captures_new_final(self):
        self.write([meta(), event("user", "当前用户", "u1"), event("assistant", "旧final", "a0", "final_answer", 2)])
        finished = []

        def watch():
            finished.append(archive.watch_until_complete(self.current, 3))

        worker = threading.Thread(target=watch)
        worker.start()
        time.sleep(0.15)
        self.assertTrue(worker.is_alive(), "Historical final must not end a new watcher")
        question = event("assistant", "目标手机型号是什么？", "q1", "final_answer", 3)
        question["payload"]["item"]["delivery"] = "async"
        with self.current.open("ab") as stream:
            stream.write(as_bytes([question]))
        time.sleep(0.15)
        self.assertTrue(worker.is_alive(), "异步提问不得使归档监听提前结束")
        with self.current.open("ab") as stream:
            stream.write(as_bytes([event("assistant", "新的最终回复", "a1", "final_answer", 4)]))
        worker.join(4)
        self.assertEqual(finished, [True])
        archive.export_archive(self.current, self.out)
        page = next(iter(archive.existing_pages(self.out).values()))[0]
        self.assertIn("新的最终回复", page.read_text(encoding="utf-8"))

    def test_parent_cutoff_must_be_valid_json_boundary(self):
        parent = self.sessions / "rollout-thread-1_parent.jsonl"
        data = as_bytes([meta(), response("user", "祖父保留文字", "u1")])
        parent.write_bytes(data)
        self.write([meta("parent", len(data) - 3)])
        with self.assertRaises(archive.ArchiveError):
            archive.load_branch(self.current)


if __name__ == "__main__":
    unittest.main()
