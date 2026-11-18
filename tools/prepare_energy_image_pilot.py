#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成燃料接口试图的透明化与像素尺寸对照，不读取密钥、不调用网络。

【变更记录 #1】2026-10-20 01:49:59（香港时间，API 试图后处理）
删除：无；新增：解码、洋红色键去底、最近邻16/32采样、联系图及逐图核验。
修改：保留API原图，输出独立文件；采样结果不冒称原生16像素美术。
用途：检查用户授权中转站试图能否作为贴图底稿，禁止改写正式游戏资源。
输入输出：仅使用固定output目录中的两张PNG，重复执行时拒绝覆盖派生文件。
【变更记录 #2】2026-10-20 01:51:46（香港时间，目视发现紫边后修正）
删除：严阈值遗漏暗紫色边缘的当前处理；新增：宽色键边界洪泛及主体等比紧裁。
修改：新结果只写pixel-review-v2；16/32保留1/2像素边距，原图和V1过程保留。
用途：清除底色污染并提高小尺寸可读性，仍不宣称原生16网格或最终配对完成。
"""

from datetime import datetime, timedelta, timezone
from hashlib import sha256
from pathlib import Path
import json

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "output/imagegen/energy-fuel-pilot-20261020"
OUT = BASE / "pixel-review-v2"
NEAREST = Image.Resampling.NEAREST if hasattr(Image, "Resampling") else Image.NEAREST
FONT = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 21)
SMALL = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 16)


def identity(path):
    with Image.open(path) as source:
        source.load()
        alpha = source.getchannel("A") if "A" in source.getbands() else None
        return {
            "path": path.relative_to(ROOT).as_posix(),
            "sha256": sha256(path.read_bytes()).hexdigest(),
            "size": list(source.size),
            "mode": source.mode,
            "alpha_values": sorted(set(alpha.getdata())) if alpha else None,
            "visible_bounds": list(alpha.getbbox()) if alpha and alpha.getbbox() else None,
        }


def transparent(source):
    # 提示词明确只允许背景为洋红，主体中不得使用该色；不去除青色燃料窗。
    rgb = source.convert("RGB")
    mask = Image.new("L", source.size)
    mask.putdata([255 if r - g >= 20 and b - g >= 20 else 0 for r, g, b in rgb.getdata()])
    if mask.getpixel((0, 0)) != 255:
        raise ValueError("角点不是预期色键背景，拒绝自动抠底")
    ImageDraw.floodfill(mask, (0, 0), 128)
    data = [(0, 0, 0, 0) if keyed == 128 else (*pixel, 255)
            for pixel, keyed in zip(rgb.getdata(), mask.getdata())]
    removed = sum(keyed == 128 for keyed in mask.getdata())
    result = Image.new("RGBA", source.size)
    result.putdata(data)
    if not removed or not result.getchannel("A").getbbox():
        raise ValueError("未得到同时含主体与透明背景的图像，拒绝继续")
    return result, removed


def compact(clear, size):
    bounds = clear.getchannel("A").getbbox()
    cropped = clear.crop(bounds)
    margin = size // 16
    scale = min((size - 2 * margin) / cropped.width, (size - 2 * margin) / cropped.height)
    dimensions = (max(1, round(cropped.width * scale)), max(1, round(cropped.height * scale)))
    fitted = cropped.resize(dimensions, NEAREST)
    result = Image.new("RGBA", (size, size))
    result.paste(fitted, ((size - fitted.width) // 2, (size - fitted.height) // 2))
    return result


def backdrop(size, color=None):
    tile = Image.new("RGB", size, color or "#e2e7eb")
    if color is None:
        draw = ImageDraw.Draw(tile)
        for y in range(0, size[1], 16):
            for x in range(0, size[0], 16):
                if (x // 16 + y // 16) % 2:
                    draw.rectangle((x, y, x + 15, y + 15), fill="#bcc8d2")
    return tile


def main():
    OUT.mkdir(exist_ok=False)
    names = ("fresh-fuel", "spent-fuel")
    targets = [OUT / (name + suffix + ".png") for name in names
               for suffix in ("-transparent", "-16", "-32")]
    targets += [OUT / "pixel-comparison.png", OUT / "postprocess-receipt.json"]
    if any(path.exists() for path in targets):
        raise FileExistsError("已有派生结果；请建立新版本目录，不能覆盖")
    records, prepared = [], {}
    for name in names:
        raw = BASE / (name + "-master-api.png")
        with Image.open(raw) as source:
            source.load()
            clear, removed = transparent(source)
        outputs = []
        for suffix, image in (("-transparent", clear),
                              ("-16", compact(clear, 16)),
                              ("-32", compact(clear, 32))):
            path = OUT / (name + suffix + ".png")
            image.save(path)
            info = identity(path)
            bounds = info["visible_bounds"]
            width, height = info["size"]
            if info["alpha_values"] != [0, 255] or not bounds:
                raise ValueError("透明度不满足二值主体与背景")
            if not (0 < bounds[0] < bounds[2] < width and 0 < bounds[1] < bounds[3] < height):
                raise ValueError("主体触边或可见范围异常")
            outputs.append(info)
            prepared[(name, suffix)] = image
        records.append({"raw": identity(raw), "removed_backdrop_pixels": removed,
                        "derived": outputs})

    sheet = Image.new("RGB", (1160, 812), "#edf2f6")
    draw = ImageDraw.Draw(sheet)
    draw.text((28, 20), "US 接口试图 · 燃料 / 乏料像素对照", font=FONT, fill="#163442")
    labels = ("16×16 紧裁采样放大", "32×32 紧裁采样放大", "16×16 深色背景")
    for row, name in enumerate(names):
        y = 72 + row * 357
        draw.text((28, y), "燃料：完整填充" if row == 0 else "乏料：暗色空腔与残留", font=FONT, fill="#163442")
        for column, label in enumerate(labels):
            x = 28 + column * 375
            draw.text((x, y + 35), label, font=SMALL, fill="#385567")
            tile = backdrop((272, 272), "#17242c" if column == 2 else None)
            sprite = prepared[(name, "-32" if column == 1 else "-16")].resize((272, 272), NEAREST)
            tile.paste(sprite, (0, 0), sprite)
            sheet.paste(tile, (x, y + 65))
            native = prepared[(name, "-16")]
            sheet.paste(native, (x + 291, y + 96), native)
            draw.text((x + 285, y + 125), "原大小", font=SMALL, fill="#385567")
    draw.text((28, 785), "API原图为1254×1254 RGB；此处为去底与采样试稿，未审批、未写正式资源。", font=SMALL, fill="#385567")
    sheet.save(OUT / "pixel-comparison.png")
    now = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")
    report = {
        "created_at": now, "mode": "CLI fallback via unmodified bundled image_gen.py",
        "reference_images_uploaded": 0, "requested_size": [1024, 1024],
        "actual_size_honored": False, "actual_native_16_grid_confirmed": False,
        "processing": "宽色键边界洪泛去底；主体紧裁后等比最近邻采样；16/32留1/2像素边距；未重画、未平滑插值",
        "caveat": "API像素风原图包含细节与非网格色差；16/32图为采样试稿，需人工视觉审批",
        "records": records, "contact_sheet": identity(OUT / "pixel-comparison.png"),
        "formal_resource_writes": 0, "game_deployed": False,
        "_record": "【记录 #1】" + now + "：新增V2宽色键去底与紧裁采样；保留API原图及V1过程。用途为实际缩放质量检查，尚需视觉审批。",
    }
    (OUT / "postprocess-receipt.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"images": len(records), "derived": 6, "formal_resource_writes": 0}, ensure_ascii=False))


if __name__ == "__main__":
    main()
