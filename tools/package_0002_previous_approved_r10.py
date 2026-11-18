# -*- coding: utf-8 -*-
"""整理39张独立重绘候选，保留API原尺寸及既有游戏资源。"""

from html import escape
from pathlib import Path
import json
import shutil

from PIL import Image, ImageDraw, ImageFont

from package_0002_fullsize_texture_candidates_r9 import checker, digest, transparent


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output/imagegen/previous-approved-0002-r10"
DELIVERY = ROOT / "deliveries/0002贴图材质_R2R3全量试画_R10_20261115"
LOG = ROOT / "logs/textures-previous-approved-0002-r10-20261115"
FONT = "C:/Windows/Fonts/msyh.ttc"
REVIEW_ATTENTION = [
    "五种探测器更偏精细工业插画，Minecraft像素块面感需要负责人重点评审。",
    "不合格电路层与正常层的线路、焊盘版式不同；不合格封装的引脚样式也有变化。它们是同族独立生图，不是严格复用同一母图。",
    "稳定模拟世界泡采用第二次文本生图，修正额外锚块及重复世界核；首稿在工作目录discarded中保留。",
]


def overview(records, output, title):
    columns, cell, row_height = 7, 224, 262
    rows = (len(records) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * cell, 74 + rows * row_height), "#eff3f7")
    draw = ImageDraw.Draw(sheet)
    draw.text((18, 14), title, font=ImageFont.truetype(FONT, 25), fill="#24394a")
    font = ImageFont.truetype(FONT, 13)
    for index, record in enumerate(records):
        image = Image.open(DELIVERY / record["image"]).convert("RGBA")
        image.thumbnail((cell - 16, cell - 16), Image.Resampling.LANCZOS)
        tile = checker((cell - 12, cell - 12))
        tile.paste(image, ((tile.width - image.width) // 2, (tile.height - image.height) // 2), image)
        x, y = index % columns * cell + 4, 68 + index // columns * row_height
        sheet.paste(tile, (x, y))
        draw.text((x, y + cell - 10), record["name"], font=font, fill="#26394a")
    sheet.save(output)


def main():
    scope = json.loads((OUTPUT / "scope.json").read_text(encoding="utf-8"))
    baseline = json.loads((LOG / "baseline.json").read_text(encoding="utf-8"))
    originals = {item["id"]: item for item in baseline["originals"]}
    prompts = []
    for group in ("instruments", "circuits-materials", "world-samples"):
        prompts.extend(json.loads((OUTPUT / f"{group}-prompts.json").read_text(encoding="utf-8")))
    by_id = {item["id"]: item for item in prompts}
    fullsize = OUTPUT / "fullsize"
    fullsize.mkdir(exist_ok=True)
    DELIVERY.mkdir(parents=True, exist_ok=True)
    records, cards = [], []
    for index, item in enumerate(scope):
        identity = item["id"]
        prompt = by_id[identity]
        raw = OUTPUT / f"{identity}.png"
        png = fullsize / raw.name
        image = transparent(raw, png)
        target = DELIVERY / identity
        target.mkdir(exist_ok=True)
        shutil.copy2(png, target / "texture.png")
        shutil.copy2(raw, target / "api-original-rgb.png")
        (target / "prompt.txt").write_text(prompt["promptEn"], encoding="utf-8")
        record = {**prompt, "previousReviewGroup": "R2" if index < 19 else "R3",
                  "image": f"{identity}/texture.png", "rawImage": f"{identity}/api-original-rgb.png",
                  "size": list(image.size), "mode": image.mode,
                  "sha256": digest(png), "sourceSha256": digest(raw),
                  "apiSource": raw.relative_to(ROOT).as_posix(),
                  "originalResource": originals[identity]["path"],
                  "originalSha256": originals[identity]["sha256"],
                  "originalApprovalStillValid": True, "gameResourceChanged": False,
                  "artApproved": False, "status": "R10独立试稿，待负责人评审"}
        records.append(record)
        facts = "；".join(prompt["code_facts"])
        cards.append(f'<article id="{identity}"><h2>{index + 1:02d} · {escape(item["name"])}</h2>'
                     f'<code>{identity}</code><p><b>用途与工艺事实：</b>{escape(facts)}</p>'
                     f'<p><b>本轮造型推导：</b>{escape(prompt["designZh"])}</p>'
                     f'<img class="texture" src="{identity}/texture.png">'
                     f'<p>实际尺寸：{image.width}×{image.height} RGBA；原画布未缩放。</p>'
                     f'<p><a href="{identity}/texture.png">透明PNG</a> · '
                     f'<a href="{identity}/api-original-rgb.png">API原图</a> · '
                     f'<a href="{identity}/prompt.txt">提示词</a></p>'
                     f'<details><summary>设计依据与提示词</summary><p>{escape(prompt["basis"])}</p>'
                     f'<pre>{escape(prompt["promptEn"])}</pre></details></article>')
    sizes = sorted({tuple(item["size"]) for item in records})
    counts = {f"{w}×{h}": sum(item["size"] == [w, h] for item in records) for w, h in sizes}
    data = {"revision": "R10", "conversation": "0002",
            "conversationId": "01a1d68a-a994-7ac0-a48a-54c0f98fd54e",
            "sourceReviewGroups": {"R2": 19, "R3": 20}, "itemCount": len(records),
            "apiModelAlias": "gpt-image-2.6-sunburst", "actualApiSizes": sizes, "apiSizeCounts": counts,
            "originalCanvasPreserved": True, "originalRgbPreserved": True, "resized": False,
            "referenceImagesUploaded": 0, "oldImagesUsedAsVisualReference": False,
            "excludedId": "world_mining_legacy_record", "sourceResourcesChanged": 0,
            "previousApprovalsRevoked": False, "artApproved": False,
            "jarBuilt": False, "installed": False, "gameTested": False,
            "reviewAttention": REVIEW_ATTENTION, "records": records}
    (DELIVERY / "manifest.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUTPUT / "prompts.json").write_text(json.dumps(prompts, ensure_ascii=False, indent=2), encoding="utf-8")
    overview(records, DELIVERY / "overview.png", "0002 · R2/R3全部39张独立试画 · R10")
    overview(records[:19], DELIVERY / "overview-r2.png", "0002 · R2的19张新试稿 · R10")
    overview(records[19:], DELIVERY / "overview-r3.png", "0002 · R3的20张新试稿 · R10")
    size_text = "、".join(f"{count}张{size}" for size, count in counts.items())
    page = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>0002 · R2/R3全量试画 R10</title><style>
body{font:16px/1.6 "Microsoft YaHei",sans-serif;color:#24394a;background:#edf2f7;max-width:1160px;margin:24px auto;padding:0 20px}
article{background:#fff;padding:20px;margin:18px 0;border:1px solid #d2dce5;border-radius:6px}
img{max-width:100%;height:auto}.texture{display:block;max-height:512px;background:repeating-conic-gradient(#cbd5df 0 25%,#e8edf2 0 50%) 0/32px 32px}
code,pre{overflow-wrap:anywhere;white-space:pre-wrap}a{color:#126895}nav a{display:inline-block;margin:4px 12px 4px 0}
</style><h1>0002 · R2/R3全量试画 R10</h1>
<p>R2的19张与R3的20张，共39张独立新候选。依据物品用途与工艺重新设计，未上传或参考旧图。
原认可及游戏资源保持；真实采掘遗留资料不在本轮范围。新稿尚待美术评审，未构建或安装JAR。</p>
<p>保留API实际原尺寸：SIZE_TEXT。仅增加透明通道，RGB与画布不变，不缩64。</p>
<p>对话ID：01a1d68a-a994-7ac0-a48a-54c0f98fd54e</p>
<nav><a href="#r2">R2 · 19张</a><a href="#r3">R3 · 20张</a><a href="manifest.json">完整事实与资源清单</a></nav>
<img src="overview.png"><h2 id="r2">R2 · 19张重新试画</h2>'''.replace("SIZE_TEXT", size_text)
    review = '<aside><b>评审关注</b><ul>' + "".join(f"<li>{escape(note)}</li>" for note in REVIEW_ATTENTION) + "</ul></aside>"
    page = page.replace("</nav>", "</nav>" + review, 1)
    page += "".join(cards[:19]) + '<h2 id="r3">R3 · 20张重新试画</h2>' + "".join(cards[19:]) + "</html>"
    (DELIVERY / "index.html").write_text(page, encoding="utf-8")
    print(json.dumps({"itemCount": len(records), "apiSizeCounts": counts,
                      "gallery": (DELIVERY / "index.html").relative_to(ROOT).as_posix()}, ensure_ascii=False))


if __name__ == "__main__":
    main()
