# -*- coding: utf-8 -*-
"""保留生图API原尺寸，只去色键背景并生成R4评审材料。"""

from hashlib import sha256
from html import escape
from pathlib import Path
import json
import shutil

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
R4 = ROOT / "deliveries/0002贴图材质_审定重绘_R4_20261114"
R4_OUTPUT = ROOT / "output/imagegen/r4-redraw-0002-r9"
R4_DELIVERY = ROOT / "deliveries/0002贴图材质_R4全量重绘_R9_20261115"
R8 = ROOT / "output/imagegen/industrial-ecosystem-0002-r8"
R8_DELIVERY = ROOT / "deliveries/0002贴图材质_工业生态_R8原图版_R8r1_20261115"
FONT = "C:/Windows/Fonts/msyh.ttc"


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def transparent(raw, output, magenta_key=False):
    source = Image.open(raw).convert("RGB")
    pixels = list(source.getdata())
    alpha = Image.new("L", source.size)
    if magenta_key:
        alpha.putdata([0 if min(r, b) > g + 4 and min(r, b) > g * 1.06 and min(r, b) > max(r, b) * 0.72 else 255
                       for r, g, b in pixels])
    else:
        alpha.putdata([0 if g > max(r, b) + 4 and g > max(r, b) * 1.06 else 255
                       for r, g, b in pixels])
    image = source.convert("RGBA")
    image.putalpha(alpha)
    image.save(output)
    return image


def checker(size):
    image = Image.new("RGB", size, "#e8edf2")
    draw = ImageDraw.Draw(image)
    for y in range(0, size[1], 16):
        for x in range(0, size[0], 16):
            if (x // 16 + y // 16) % 2:
                draw.rectangle((x, y, x + 15, y + 15), fill="#cbd5df")
    return image


def prepare_r8():
    prompts = {item["id"]: item for item in json.loads((R8 / "prompts.json").read_text(encoding="utf-8"))}
    handoff = json.loads((ROOT / "deliveries/0003工业链_工业生态注册_V3_20261114/registry-manifest.json").read_text(encoding="utf-8-sig"))
    items = {item["id"]: item for item in handoff["items"]}
    R8_DELIVERY.mkdir(parents=True, exist_ok=True)
    raw_dir = R8 / "api-originals-1254"
    raw_dir.mkdir(exist_ok=True)
    columns, cell = 5, 240
    rows = (len(items) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * cell, 90 + rows * (cell + 52)), "#eff3f7")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype(FONT, 15)
    draw.text((18, 14), "0002 R8r1 · 15张API原尺寸图，原画布加透明通道", font=ImageFont.truetype(FONT, 24), fill="#24394a")
    records = []
    links = []
    for index, identity in enumerate(items):
        prompt = prompts[identity]
        old = items[identity]
        name = old["zh"]
        raw = R8 / (identity + ".png")
        original = raw_dir / raw.name
        if not original.exists():
            shutil.copy2(raw, original)
        png = R8 / "fullsize" / raw.name
        png.parent.mkdir(exist_ok=True)
        image = transparent(original, png)
        item_dir = R8_DELIVERY / identity
        item_dir.mkdir(exist_ok=True)
        previous = R8 / "final" / raw.name
        if previous.exists() and not (item_dir / "texture-64-previous.png").exists():
            shutil.copy2(previous, item_dir / "texture-64-previous.png")
        shutil.copy2(original, item_dir / "api-original-rgb.png")
        shutil.copy2(png, item_dir / "texture.png")
        shutil.copy2(png, ROOT / old["targetPng"])
        x, y = (index % columns) * cell + 8, 72 + (index // columns) * (cell + 52)
        thumb = image.copy()
        thumb.thumbnail((cell - 20, cell - 20), Image.Resampling.LANCZOS)
        tile = checker((cell - 16, cell - 16))
        tile.paste(thumb, ((tile.width - thumb.width) // 2, (tile.height - thumb.height) // 2), thumb)
        sheet.paste(tile, (x, y))
        draw.text((x, y + cell - 10), name, font=font, fill="#26394a")
        texture = old["targetPng"].split("/textures/", 1)[1][:-4]
        layer0 = "hk3gtl:" + texture
        record = {"id": identity, "name": name, "source": str(original.relative_to(ROOT)).replace("\\", "/"),
                  "png": str(png.relative_to(ROOT)).replace("\\", "/"), "size": list(image.size),
                  "mode": image.mode, "sha256": digest(png), "sourceSha256": digest(original),
                  "targetResource": old["targetPng"], "model": old["model"], "layer0": layer0,
                  "designZh": prompt["designZh"], "basis": prompt["paletteBasis"], "prompt": prompt["promptEn"],
                  "alphaValues": sorted(set(image.getchannel("A").getdata())), "status": "待负责人评审；源码已使用原尺寸"}
        records.append(record)
        links.append(f'<article id="{identity}"><h2>{escape(name)}</h2><code>{identity}</code><p>{escape(prompt["designZh"])}</p><p>API原图 {image.width}×{image.height} RGBA；Alpha仅由色键背景生成，RGB与画布尺寸不变。</p><img src="{identity}/texture.png"><p><a href="{identity}/api-original-rgb.png">含背景原始API图</a> · <a href="{identity}/texture-64-previous.png">此前64像素版本</a></p><details><summary>提示词</summary><pre>{escape(prompt["promptEn"])}</pre></details><p>模型：gpt-image-2.6-sunburst · {layer0}</p><p>SHA256：{record["sha256"]}</p></article>')
    sheet.save(R8_DELIVERY / "overview.png")
    data = {"revision": "R8r1", "conversation": "0002", "model": "gpt-image-2.6-sunburst",
            "apiSize": [1254, 1254], "textureCount": len(records), "outputSize": "preserved API canvas; RGBA alpha added",
            "sourceImagesUploaded": 0, "nativeApiImagesPreserved": True, "resized": False,
            "old64PreviewsPreserved": True, "gameResourcesUpdated": True, "gameTested": False,
            "records": records}
    (R8_DELIVERY / "manifest.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    html = '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>0002 R8r1 原尺寸贴图</title><style>body{font:16px/1.6 "Microsoft YaHei",sans-serif;color:#24394a;background:#edf2f7;max-width:1160px;margin:24px auto;padding:0 20px}article{background:#fff;padding:20px;margin:18px 0;border:1px solid #d2dce5;border-radius:6px}article img{display:block;max-width:100%;max-height:512px;height:auto;image-rendering:auto;background:repeating-conic-gradient(#cbd5df 0 25%,#e8edf2 0 50%) 0/32px 32px}code,pre{overflow-wrap:anywhere;white-space:pre-wrap}a{color:#126895}</style><h1>0002 R8r1 · API原尺寸</h1><p>15张游戏资源已改为API原画布加透明通道，1254×1254 RGB未缩放。此前64像素版本单独保留供对照；新图待美术评审。图像浏览器按窗口缩放显示，PNG本身未缩小。</p><img src="overview.png" style="max-width:100%;height:auto">' + ''.join(links) + '<p><a href="manifest.json">完整清单</a></p></html>'
    (R8_DELIVERY / "index.html").write_text(html, encoding="utf-8")
    return records


def prepare_r4():
    handoff = json.loads((R4 / "manifest.json").read_text(encoding="utf-8-sig"))
    prompts = []
    for name in ["world-prompts.json", "process-prompts.json", "nano-keys-prompts.json"]:
        prompts.extend(json.loads((R4_OUTPUT / name).read_text(encoding="utf-8")))
    prompt_map = {item["id"]: item for item in prompts}
    records, cards = [], []
    R4_DELIVERY.mkdir(parents=True, exist_ok=True)
    columns, cell = 7, 224
    rows = (len(handoff["items"]) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * cell, 100 + rows * (cell + 34)), "#eff3f7")
    draw = ImageDraw.Draw(sheet)
    draw.text((18, 15), "0002 · R4全量重绘试稿 · API原尺寸透明PNG", font=ImageFont.truetype(FONT, 26), fill="#24394a")
    small = ImageFont.truetype(FONT, 13)
    for index, old in enumerate(handoff["items"]):
        prompt = prompt_map[old["id"]]
        raw = R4_OUTPUT / (old["id"] + ".png")
        target = R4_DELIVERY / old["id"]
        target.mkdir(exist_ok=True)
        original = R4_OUTPUT / "api-originals" / raw.name
        original.parent.mkdir(exist_ok=True)
        if not original.exists():
            shutil.copy2(raw, original)
        image = transparent(original, raw, magenta_key=old["id"] == "imitation_oath_of_judah")
        shutil.copy2(raw, target / "texture.png")
        shutil.copy2(original, target / "api-original-rgb.png")
        (target / "prompt.txt").write_text(prompt["promptEn"], encoding="utf-8")
        x, y = (index % columns) * cell + 4, 68 + (index // columns) * (cell + 34)
        thumb = image.copy()
        thumb.thumbnail((cell - 16, cell - 16), Image.Resampling.LANCZOS)
        tile = checker((cell - 12, cell - 12))
        tile.paste(thumb, ((tile.width - thumb.width) // 2, (tile.height - thumb.height) // 2), thumb)
        sheet.paste(tile, (x, y))
        draw.text((x, y + cell - 12), old["name"], font=small, fill="#26394a")
        record = {"id": old["id"], "name": old["name"], "category": old["category"],
                  "code_facts": old["code_facts"], "evidence": old["evidence"],
                  "image": old["id"] + "/texture.png", "apiSource": str(original.relative_to(ROOT)).replace("\\", "/"),
                  "candidate": str((target / "texture.png").relative_to(ROOT)).replace("\\", "/"),
                  "size": list(image.size), "mode": image.mode, "sha256": digest(raw),
                  "native_size": list(image.size), "art_approved": False, "review_status": "R9候选待评审",
                  "previousR4Approved": old["art_approved"],
                  "sourceSha256": digest(original), "designZh": prompt["designZh"],
                  "designBasis": prompt["basis"], "prompt": prompt["promptEn"],
                  "alphaValues": sorted(set(image.getchannel("A").getdata())),
                  "gameResourceChanged": False, "status": "候选；待美术评审"}
        records.append(record)
        cards.append(f'<article id="{old["id"]}"><h2>{escape(old["name"])}</h2><code>{old["id"]}</code><p><b>配方/用途事实：</b>{escape("；".join(old["code_facts"]))}</p><p><b>本轮造型：</b>{escape(prompt["designZh"])}</p><p>API画布 {image.width}×{image.height} RGBA；未缩64，未覆盖R4源码资源。</p><img src="{old["id"]}/texture.png"><p><a href="{old["id"]}/api-original-rgb.png">含背景原始API图</a> · <a href="{old["id"]}/prompt.txt">提示词</a></p><p>SHA256：{record["sha256"]}</p></article>')
    sheet.save(R4_DELIVERY / "overview.png")
    sizes = sorted({tuple(record["size"]) for record in records})
    size_counts = {f"{width}×{height}": sum(record["size"] == [width, height] for record in records)
                   for width, height in sizes}
    size_text = "、".join(f"{count}张{size}" for size, count in size_counts.items())
    data = {"revision": "R9", "conversation": "0002", "sourceRevision": "R4", "itemCount": len(records),
            "apiModel": "gpt-image-2.6-sunburst", "actualApiSizes": sizes, "apiSizeCounts": size_counts,
            "artApproved": False, "jarBuilt": False, "installed": False, "gameTested": False,
            "output": "API原尺寸RGBA PNG；保留原画布及RGB，仅以透明通道替换色键背景",
            "referenceImagesUploaded": 0, "acceptedR4SourcesChanged": 0,
            "sourceGameResourcesChanged": 0, "itemIds": [record["id"] for record in records],
            "records": records}
    (R4_DELIVERY / "manifest.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    html = '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>0002 R4全量重绘 R9</title><style>body{font:16px/1.6 "Microsoft YaHei",sans-serif;color:#24394a;background:#edf2f7;max-width:1160px;margin:24px auto;padding:0 20px}article{background:#fff;padding:20px;margin:18px 0;border:1px solid #d2dce5;border-radius:6px}article img{display:block;max-width:100%;max-height:512px;height:auto;background:repeating-conic-gradient(#cbd5df 0 25%,#e8edf2 0 50%) 0/32px 32px}code,pre{overflow-wrap:anywhere}a{color:#126895}.overview{max-width:100%;height:auto}</style><h1>0002 · R4全量重绘试稿 R9</h1><p>28张独立新候选；PNG保留API原尺寸（{size_text}），增加透明Alpha，不缩64。原R4源图、已认可26张及旧游戏资源均保持；候选尚未接入游戏。两神之键按原作构造设计，其余按用途和工艺重新设计。</p><img class="overview" src="overview.png">' .replace("{size_text}", size_text) + ''.join(cards) + '<p><a href="manifest.json">完整清单</a></p></html>'
    (R4_DELIVERY / "index.html").write_text(html, encoding="utf-8")
    return records


def main():
    r8 = prepare_r8()
    r4 = prepare_r4()
    print(json.dumps({"r8OriginalCanvasTextures": len(r8), "r4NewCandidates": len(r4),
                      "r8Gallery": str(R8_DELIVERY.relative_to(ROOT)).replace("\\", "/"),
                      "r4Gallery": str(R4_DELIVERY.relative_to(ROOT)).replace("\\", "/")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
