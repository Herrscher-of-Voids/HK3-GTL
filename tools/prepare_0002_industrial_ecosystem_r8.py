# -*- coding: utf-8 -*-
"""整理工业生态API底稿、导出64像素候选与评审页。"""

from datetime import datetime, timedelta, timezone
from hashlib import sha256
from html import escape
from pathlib import Path
import json
import shutil
import sys

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/imagegen/industrial-ecosystem-0002-r8"
DELIVERY = ROOT / "deliveries/0002贴图材质_工业生态_R8"
LOG = ROOT / "logs/textures-industrial-ecosystem-0002-r8"
HANDOFF = ROOT / "deliveries/0003工业链_工业生态注册_V3_20261114/registry-manifest.json"
PUBLISH = "--publish" in sys.argv
FONT = "C:/Windows/Fonts/msyh.ttc"


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def sprite(path):
    source = Image.open(path).convert("RGB")
    pixels = list(source.getdata())
    keyed = [g > 110 and g - max(r, b) > 35 and g > r * 1.35 and g > b * 1.35
             for r, g, b in pixels]
    clear = Image.new("RGBA", source.size)
    clear.putdata([(0, 0, 0, 0) if key else (*rgb, 255)
                   for rgb, key in zip(pixels, keyed)])
    bounds = clear.getchannel("A").getbbox()
    cutout = clear.crop(bounds)
    cutout.thumbnail((56, 56), Image.Resampling.NEAREST)
    result = Image.new("RGBA", (64, 64))
    result.paste(cutout, ((64 - cutout.width) // 2, (64 - cutout.height) // 2))
    alpha = result.getchannel("A")
    result = result.convert("RGB").quantize(colors=32, dither=Image.Dither.NONE).convert("RGBA")
    result.putalpha(alpha)
    return result, {"apiSize": list(source.size), "apiMode": source.mode,
                    "backgroundPixelsRemoved": sum(keyed), "sourceBounds": list(bounds)}


def backdrop(size, dark=False):
    image = Image.new("RGB", size, "#202b39" if dark else "#edf1f5")
    draw = ImageDraw.Draw(image)
    for y in range(0, size[1], 16):
        for x in range(0, size[0], 16):
            if (x // 16 + y // 16) % 2:
                draw.rectangle((x, y, x + 15, y + 15), fill="#2d3c4d" if dark else "#d8e0e9")
    return image


def main():
    DELIVERY.mkdir(parents=True, exist_ok=True)
    final = OUT / "final"
    final.mkdir(exist_ok=True)
    handoff = json.loads(HANDOFF.read_text(encoding="utf-8-sig"))
    prompts = {p["id"]: p for p in json.loads((OUT / "prompts.json").read_text(encoding="utf-8"))}
    records = []
    cards = []
    sheet = Image.new("RGB", (1500, 1290), "#f4f7fa")
    draw = ImageDraw.Draw(sheet)
    title_font = ImageFont.truetype(FONT, 28)
    label_font = ImageFont.truetype(FONT, 18)
    tiny_font = ImageFont.truetype(FONT, 14)
    draw.text((24, 16), "0002 · 工业生态 R8 · 15张64×64透明PNG候选", font=title_font, fill="#183248")
    draw.text((24, 56), "绑定API底稿 → 去绿底 → 64像素网格整理；非16像素放大，仍待美术评审", font=label_font, fill="#516678")
    for index, item in enumerate(handoff["items"]):
        identity = item["id"]
        raw = OUT / (identity + ".png")
        image, processing = sprite(raw)
        png = final / (identity + ".png")
        image.save(png)
        folder = DELIVERY / identity
        folder.mkdir(exist_ok=True)
        shutil.copy2(png, folder / "texture.png")
        prompt = prompts[identity]
        (folder / "prompt.txt").write_text(prompt["promptEn"], encoding="utf-8")
        texture = "hk3gtl:" + item["targetPng"].split("/textures/", 1)[1][:-4]
        if PUBLISH:
            target = ROOT / item["targetPng"]
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(png, target)
            model = ROOT / item["model"]
            document = json.loads(model.read_text(encoding="utf-8"))
            document["textures"]["layer0"] = texture
            model.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        alpha = image.getchannel("A")
        record = {**item, **prompt, **processing, "texture": texture,
                  "source": str(raw.relative_to(ROOT)).replace("\\", "/"), "sourceSha256": digest(raw),
                  "png": str(png.relative_to(ROOT)).replace("\\", "/"), "sha256": digest(png),
                  "size": list(image.size), "mode": image.mode, "alphaValues": sorted(set(alpha.getdata())),
                  "visibleBounds": list(alpha.getbbox()), "status": "待负责人美术评审"}
        records.append(record)
        x = 20 + index % 5 * 296
        y = 100 + index // 5 * 392
        tile = backdrop((256, 256), dark=index % 2 == 1)
        enlarged = image.resize((256, 256), Image.Resampling.NEAREST)
        tile.paste(enlarged, (0, 0), enlarged)
        sheet.paste(tile, (x + 10, y))
        draw.text((x + 8, y + 266), item["zh"], font=label_font, fill="#183248")
        native = backdrop((64, 64))
        native.paste(image, (0, 0), image)
        sheet.paste(native, (x + 12, y + 300))
        draw.text((x + 90, y + 312), "原大小 64×64", font=tiny_font, fill="#516678")
        draw.text((x + 90, y + 337), "RGBA · 透明底", font=tiny_font, fill="#516678")
        cards.append(f'''<article id="{identity}"><h2>{escape(item['zh'])}</h2><code>{identity}</code>
<div class="views"><div class="preview"><img src="{identity}/texture.png" width="256" height="256"></div><div class="preview dark"><img src="{identity}/texture.png" width="256" height="256"></div><div class="native"><img src="{identity}/texture.png" width="64" height="64"><span>64×64 原大小</span></div></div>
<p><b>功能事实：</b>{escape(item['role'])}</p><p><b>设计推导：</b>{escape(prompt['designZh'])}</p><p><b>配色依据：</b>{escape(prompt['paletteBasis'])}</p>
<details><summary>资源、API原图与提示词</summary><p><a href="../../{record['source']}">API原图 {processing['apiSize'][0]}×{processing['apiSize'][1]}</a> · <a href="{identity}/texture.png">64×64 PNG</a> · <a href="{identity}/prompt.txt">完整提示词</a></p><p>{escape(item['targetPng'])}</p><p>{escape(item['model'])}</p><p>layer0：{texture}</p><p>SHA256：{record['sha256']}</p></details></article>''')
    sheet.save(DELIVERY / "overview.png")
    manifest = {"conversation": "0002贴图材质", "conversationId": "01a1d68a-a994-7ac0-a48a-54c0f98fd54e",
                "recordedAt": datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds"),
                "mode": "API fallback via existing invoke_image_relay.ps1 -Mode Generate -RelayResponse; bundled CLI not invoked",
                "model": "gpt-image-2.6-sunburst", "requestedApiSize": [1024, 1024], "outputSize": [64, 64],
                "processing": "API像素底稿按色键去底；主体裁切后最近邻落到64网格；32色硬边RGBA；原图保留，不宣称API原生64输出",
                "referenceImagesUploaded": 0, "fluidPngCount": 0, "itemPngCount": len(records),
                "resourcesWritten": PUBLISH, "artApproved": False, "jarBuilt": False, "installed": False,
                "gameRun": False, "automatedTestsRun": False, "items": records}
    (DELIVERY / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    html = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>0002 工业生态贴图 R8</title><style>
body{margin:0;background:#edf2f7;color:#203449;font:16px/1.65 "Microsoft YaHei",sans-serif}main{max-width:1240px;margin:auto;padding:28px}h1{font-size:28px}h2{font-size:20px;margin:0 0 8px}.notice,article{background:white;border:1px solid #d0dce6;border-radius:10px;padding:22px;margin:20px 0}.views{display:flex;flex-wrap:wrap;align-items:center;gap:16px;margin:20px 0}.preview{width:256px;height:256px;background:repeating-conic-gradient(#d8e0e9 0% 25%,#edf1f5 0% 50%) 0/32px 32px}.dark{background:repeating-conic-gradient(#202b39 0% 25%,#2d3c4d 0% 50%) 0/32px 32px}.native{padding:16px;background:#e0e7ef;display:flex;flex-direction:column;align-items:center;gap:12px}img{image-rendering:pixelated}code{font-size:13px;overflow-wrap:anywhere}details{overflow-wrap:anywhere}a{color:#126895}.overview{max-width:100%;height:auto}nav{display:flex;flex-wrap:wrap;gap:8px}nav a{padding:4px 10px;background:#dce7f1;border-radius:4px;text-decoration:none}p{margin:10px 0}
</style><main><h1>0002贴图材质 · 工业生态 R8</h1><div class="notice"><b>15张物品候选 · 每张64×64 RGBA透明PNG · 待美术评审</b><p>依照0003工业生态V3的名称、用途与工艺设计。未上传现有贴图或截图；9种流体无需新增PNG。API原图与完整提示词可逐项查看。</p><p>底稿由项目绑定的 gpt-image-2.6-sunburst 生成，再去底并整理为64像素网格；不是16像素放大，也不将API大图冒称原生64输出。未生成JAR、未安装或运行游戏。</p></div>'''
    html += '<nav>' + ''.join(f'<a href="#{r["id"]}">{escape(r["zh"])}</a>' for r in records) + '</nav>'
    html += '<p><a href="manifest.json">逐项清单与处理记录</a></p><img class="overview" src="overview.png">' + ''.join(cards) + '</main></html>'
    (DELIVERY / "index.html").write_text(html, encoding="utf-8")
    print(json.dumps({"png": len(records), "resourcesWritten": PUBLISH,
                      "delivery": str(DELIVERY.relative_to(ROOT)).replace("\\", "/")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
