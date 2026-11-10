"""导出I40批准与I41制作本轮真实可见文字。"""
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
from archive_i40_turn_20261028 import ARCHIVES, ROOT, THREAD, load_current_window

USER_ID = "msg_01a181e9-9b45-7430-96c8-cc20b37b3de3"
TITLE = "I40V1批准归档并制作I41"
SUMMARY = ROOT / "doc/HK3GTL-内测5/讨论记录/2026-10-28_17-48-52_I40V1批准归档并制作I41.html"
PREVIOUS = ARCHIVES / "2026-10-28_16-56-56_I37延后至最后并启动I40_bcc0fac8fa.html"
LOG = ROOT / "logs/i41-dialogue-archive-20261028/status.json"
DELIVERY = "deliveries/I41_文明能源调度中枢_弧幕母线与扇形负载港_V1_20261028"


def local_deliveries(messages):
    found = []
    for message in messages:
        candidates = re.findall(r"https?://127\.0\.0\.1:\d+/[^\s)<>]+", message["text"])
        candidates.extend(re.findall(r"\]\(<?([A-Za-z]:/[^\n>]+?)(?:>|\))", message["text"]))
        for value in candidates:
            if value.startswith("http"):
                path = ROOT / unquote(urlsplit(value).path).lstrip("/")
            else:
                path = Path(unquote(value))
            try:
                relative = path.resolve().relative_to(ROOT.resolve()).as_posix()
            except ValueError:
                continue
            if relative.startswith(("deliveries/I40_", "deliveries/I41_")) and path.exists() and relative not in found:
                found.append(relative)
    return found


def export():
    records, thread_meta, sources = load_current_window()
    segments = a.segment_dialogue(records, THREAD)
    segment = next(s for s in segments if s["messages"][0]["id"] == USER_ID)
    previous = next(s for s in segments if s["segment_id"] == a.read_page_metadata(PREVIOUS)["segment_id"])
    assert previous["messages"][-1]["phase"] in a.FINAL_PHASES, "上一段缺真实结束回复"
    old = a.existing_pages(ARCHIVES).get(segment["segment_id"])
    deliveries = local_deliveries(segment["messages"])
    for relative in [DELIVERY + "/index.html", DELIVERY + "/i41/三维评审.html", DELIVERY + "/verification.json",
                     "logs/i41-fan-dispatch-20261028/browser-verification.json", "logs/i41-fan-dispatch-20261028/package-status.json"]:
        if (ROOT / relative).exists() and relative not in deliveries:
            deliveries.append(relative)
    verification = json.loads((ROOT / DELIVERY / "verification.json").read_text(encoding="utf-8"))
    assert verification["passed"] and verification["blocks"] == 12358790
    override = {
        "title": TITLE, "kind": "多方块批准、归档与后续制作",
        "keywords": ["I40", "V1", "I41", "batch-10", "1/5", "I37留最后"],
        "tags": ["明确批准", "多方块设计", "完整对话归档"], "machines": ["I37", "I40", "I41"],
        "confirmed_decisions": ["负责人明确采用I40 V1，并要求继续下一台I41。", "I37继续留到最后；本轮不重启其设计。"],
        "pending": ["I41文明能源调度中枢·弧幕母线与扇形负载港V1已完成，等待负责人审批；尚未实装或通过游戏/FCL性能验收。", "I40已确认并计入batch-10第1/5台；I41尚未计入。按累计五台明确批准后接入，FCL与电脑版三场景内存测试仍待全部结构完成后进行。"],
        "related_paths": [str(SUMMARY.relative_to(ROOT)), str(PREVIOUS.relative_to(ROOT)), "rule/当前多方块设计规则.md", "rule/崩坏三-gtl (hk3gtl) 项目规则.md"] + deliveries,
    }
    topic_map_path = ROOT / "tools/conversation_archive/topic_overrides.json"
    topic_map = a.load_overrides(topic_map_path)
    override["related_paths"] = list(dict.fromkeys(override["related_paths"]
        + (old[1].get("related_paths", []) if old else [])
        + topic_map.get(USER_ID, {}).get("related_paths", [])))
    topic_map[USER_ID] = override
    a.write_if_changed(topic_map_path, json.dumps(topic_map, ensure_ascii=False, indent=2) + "\n")
    md = a.build_metadata(segment, thread_meta, sources, old[1] if old else None, override)
    md["transcript_scope"] = "按当前JSONL页及后续分支真实字节边界导出本段用户/助手可见文字；不含工具、隐藏思考、系统注入、环境状态或代理通信。"
    md["completeness"] = "本轮已落盘可见文字已完整纳入；进行中时尚无结束回复，结束后自动补齐。早期祖先页缺失，本轮不重导全项目历史。"
    if segment["closed_reason"] in ("final", "task_complete") and any(m["phase"] in a.FINAL_PHASES for m in segment["messages"]):
        md["completeness"] = "本轮真实用户消息、已落盘可见进度及实际结束回复已纳入；早期祖先页缺失，不能据此宣称全项目历史完整。"
    elif segment["closed_reason"]:
        md["completeness"] = "本段可见文字已纳入，后续用户消息另分新段；本段无可核验结束回复，不用后续文字或摘要重建。"
    old_messages = old[1].get("messages", []) if old else []
    unchanged = (len(old_messages) == len(segment["messages"]) and old_messages
                 and old_messages[-1]["id"] == segment["messages"][-1]["id"]
                 and old[1].get("closed_reason") == segment["closed_reason"])
    updated_at = old[1].get("custom_metadata", {}).get("最后补录时间") if unchanged else None
    md["custom_metadata"].update({"最后补录时间": updated_at or dt.datetime.now(a.HONG_KONG).isoformat(timespec="seconds"), "上一段核对": "上一段I40真实final已归档；其正文保持原文。"})
    md["custom_metadata"]["I41候选交付核对"] = {
        "尺寸口径": "宽×长×高", "尺寸": verification["size_wdh"], "实体方块数": verification["blocks"],
        "普通材料种类": verification["ordinary_materials"], "含主控及接口标记总材料种类": verification["unique_materials"],
        "主控原始坐标XYZ": verification["controller"]["position"], "端口数": 6,
        "更低电压比较形态数": verification["voltage_progression"]["lower_form_count"],
        "绘制面片": verification["viewer_rendered_quads"], "状态": "候选待审；未实装，游戏/FCL未验收。",
        "来源": DELIVERY + "/verification.json"
    }
    path = old[0] if old else ARCHIVES / a.filename_for(md)
    changed = a.write_if_changed(path, a.render_page(segment, md, PREVIOUS, None))
    prior_html = PREVIOUS.read_text(encoding="utf-8")
    if path.name not in prior_html:
        prior_html = prior_html.replace("</nav>", ' · <a href="' + escape(path.name, quote=True) + '">后一段：I40批准并制作I41</a></nav>')
        a.write_if_changed(PREVIOUS, prior_html)
    if changed:
        a.write_if_changed(ARCHIVES / "index.html", a.render_index(ARCHIVES))
    evidence = deliveries + [p for p in override["related_paths"]
        if p.startswith(("logs/", "deliveries/多方块确认归档/")) and (ROOT / p).exists()]
    links = "".join('<p><a href="' + escape((ROOT / p).as_uri(), quote=True) + '">' + escape(p) + '</a></p>' for p in dict.fromkeys(evidence))
    summary = f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>{TITLE}</title><style>body{{max-width:980px;margin:40px auto;padding:0 24px;font:17px/1.8 system-ui;background:#101926;color:#e1ebf7}}a{{color:#7cd6ea}}code{{overflow-wrap:anywhere}}</style>
<h1>{TITLE}</h1>
<p>本页是人工决策摘要，不代替逐字原文。</p>
<p>负责人明确采用I40 V1并要求继续下一台I41。I40计入新批次第1/5台；I41候选须另行审阅，尚未因本轮制作请求获得批准。I37继续留到最后。</p>
<h2>I41本轮实际交付</h2>
<p>I41「文明能源调度中枢·弧幕母线与扇形负载港」V1已完成。实际宽×长×高为591×471×285，共12,358,790个实体方块；普通材料41种，含主控与接口标记共43种。主控原始XYZ坐标为[295,27,0]，6处接口嵌入主体；IWV本级机械机壳为最大单项。</p>
<p>已通过42个更低电压已批准形态比较、NBT/Sponge逐格回读、43种真实纹理、HTTP与file离线HTML检查，以及图层与玻璃切换。预览绘制面片738,392。依据实际交付verification.json及浏览器验证记录核对，本段为交付摘要，不作为用户原话。</p>
<p>I41等待用户审批，未实装；游戏运行、正式调度能力及FCL性能尚未验收。I40归档与batch-10第1/5台状态保持。</p>
<p>累计五台明确批准后先接入的规则继续有效；FCL与电脑版三场景内存测试待全部结构完成后进行。本摘要不声称游戏运行验收已通过。</p>
<p>真实首条用户消息：{escape(md['start_time'])}；最后可见文字：{escape(md['end_time'])}；状态：{escape(md['status'])}。本段墙钟跨度{md['duration_seconds']:.3f}秒，不代表计算时长。</p>
<p><a href="../完整对话归档/{escape(path.name, quote=True)}">本轮完整对话原文</a> · <a href="../完整对话归档/{escape(PREVIOUS.name, quote=True)}">上一段I40制作与真实结束回复</a></p>{links}<p>变更记录 #1：依据实际用户消息建立I40批准与I41制作决定。变更记录 #2：根据实际交付文件补齐I41候选数据、核验范围和待审边界；原文仍只按真实可见消息落盘补录。</p></html>'''
    a.write_if_changed(SUMMARY, summary)
    result = {"thread_id": THREAD, "segment_id": segment["segment_id"], "archive": str(path), "summary": str(SUMMARY), "message_count": len(segment["messages"]), "last_message_id": segment["messages"][-1]["id"], "last_message_time": md["end_time"], "status": md["status"], "prior_i40_final_verified": previous["messages"][-1]["timestamp"], "source_files": sources, "scope": md["completeness"]}
    LOG.parent.mkdir(parents=True, exist_ok=True)
    a.write_if_changed(LOG, json.dumps(result, ensure_ascii=False, indent=2))
    return result, bool(segment["closed_reason"])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--watch", action="store_true")
    args = parser.parse_args()
    last = None
    while True:
        result, closed = export()
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
