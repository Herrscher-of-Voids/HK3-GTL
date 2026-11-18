# -*- coding: utf-8 -*-
"""修整既有燃料底稿：在原生16像素网格内约束平行长边及配对共用外壳。

【变更记录 #1】2026-10-20 02:14:08（香港时间，长边平行修正候选）
删除：当前候选中自由缩图导致的歪斜外轮廓与两套不同壳体；不删除旧文件。
新增：整数对角坐标、同模板端盖、独立窗口掩码、PNG与几何检查清单。
修改：从既有API底稿提取近似色板，按用户明确要求逐像素重整轮廓；无API调用。
用途：产出待审批视觉修正版，不写正式资源，不修改游戏或13项已采用载体。
边界：16为编辑原稿；32及放大展示只用最近邻整数倍，不冒称API原生输出。
"""
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from pathlib import Path
import json

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "output/imagegen/energy-fuel-pilot-20261020"
OUT = ROOT / "output/imagegen/energy-fuel-parallel-v3-20261020"
NEAREST = Image.Resampling.NEAREST if hasattr(Image, "Resampling") else Image.NEAREST
FONT = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 22)
SMALL = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 17)


def build_palette():
    with Image.open(SOURCE / "pixel-review-v2/fresh-fuel-transparent.png") as image:
        image.load()
        colors = set(pixel[:3] for pixel in image.getdata() if pixel[3] == 255)
    hints = {"outline": "1b2022", "dark": "303637", "rim": "626c6c", "steel": "9ca6a5",
             "light": "d3d9d5", "shine": "edf1ed", "shadow": "475051",
             "fuel_light": "72e4e5", "fuel": "1dc5cb", "fuel_dark": "07969d",
             "empty": "121a1c", "empty_light": "273233", "residue": "296566"}
    palette = {}
    for label, value in hints.items():
        target = tuple(bytes.fromhex(value))
        nearest = min(colors, key=lambda pixel: (sum((a-b)**2 for a, b in zip(pixel, target)), pixel))
        palette[label] = nearest + (255,)
    return palette


def make_pair(palette):
    shell = Image.new("RGBA", (16, 16))
    window = []
    for y in range(16):
        for x in range(16):
            normal, axis = x + y, x - y
            absolute = abs(axis)
            key = None
            if absolute <= 7 and 11 <= normal <= 19:
                keys = {11: "outline", 12: "rim", 13: "dark", 14: "fuel_light",
                        15: "fuel", 16: "fuel_dark", 17: "dark", 18: "shadow", 19: "outline"}
                key = keys[normal]
                if 14 <= normal <= 16:
                    window.append((x, y, normal, axis))
            elif 8 <= absolute <= 11:
                limits = {8: (10, 20), 9: (10, 20), 10: (11, 19), 11: (13, 17)}
                low, high = limits[absolute]
                if low <= normal <= high:
                    if absolute == 11 or normal in (low, high):
                        key = "outline"
                    elif absolute == 8:
                        key = "shine" if normal <= 14 else "steel" if normal <= 17 else "shadow"
                    elif absolute == 9:
                        key = "light" if normal <= 13 else "steel" if normal <= 17 else "dark"
                    else:
                        key = "light" if normal <= 13 else "dark" if normal <= 16 else "shadow"
            if key:
                shell.putpixel((x, y), palette[key])
    fresh = shell.copy()
    spent = shell.copy()
    window_mask = Image.new("L", (16, 16))
    for x, y, normal, axis in window:
        window_mask.putpixel((x, y), 255)
        key = "empty_light" if normal == 14 else "empty"
        if -5 <= axis <= -3:
            key = "residue"
        spent.putpixel((x, y), palette[key])
    return fresh, spent, window_mask


def checker(size, dark=False):
    result = Image.new("RGB", (size, size), "#142229" if dark else "#dbe3e7")
    if not dark:
        draw = ImageDraw.Draw(result)
        for y in range(0, size, 16):
            for x in range(0, size, 16):
                if (x // 16 + y // 16) % 2:
                    draw.rectangle((x, y, x+15, y+15), fill="#b6c4cc")
    return result


def compare(fresh, spent):
    image = Image.new("RGB", (1160, 775), "#edf2f5")
    draw = ImageDraw.Draw(image)
    draw.text((26, 18), "V3 · 平行长边 / 同一外壳", font=FONT, fill="#193845")
    labels = ("旧版16像素取样", "修正后16像素", "修正后深色背景")
    for row, (name, new_image) in enumerate((("fresh-fuel", fresh), ("spent-fuel", spent))):
        y = 64 + row * 340
        draw.text((26, y), "燃料" if row == 0 else "乏料", font=FONT, fill="#193845")
        for column, label in enumerate(labels):
            x = 26 + column * 375
            draw.text((x, y+31), label, font=SMALL, fill="#45606c")
            old = SOURCE / "pixel-review-v2" / (name + "-16.png")
            with Image.open(old) as before:
                sprite = before.convert("RGBA") if column == 0 else new_image
                enlarged = sprite.resize((256, 256), NEAREST)
            tile = checker(256, column == 2)
            tile.paste(enlarged, (0, 0), enlarged)
            image.paste(tile, (x, y+60))
            image.paste(sprite, (x+281, y+91), sprite)
            draw.text((x+272, y+122), "原大小", font=SMALL, fill="#45606c")
    draw.text((26, 750), "原生16×16网格修整 · 长边阶梯同步 · 两状态只改变窗内像素 · 待审批候选", font=SMALL, fill="#45606c")
    image.save(OUT / "parallel-comparison.png")


def main():
    OUT.mkdir(exist_ok=False)
    palette = build_palette()
    fresh, spent, window_mask = make_pair(palette)
    for name, sprite in (("fresh-fuel", fresh), ("spent-fuel", spent)):
        sprite.save(OUT / (name + "-16.png"))
        sprite.resize((32, 32), NEAREST).save(OUT / (name + "-32-preview.png"))
    window_mask.save(OUT / "window-mask.png")
    compare(fresh, spent)
    sides = [[[x, 11-x] for x in range(2, 10)], [[x+4, 15-x] for x in range(2, 10)]]
    assert all(fresh.getpixel(tuple(p))[3] == 255 for side in sides for p in side)
    assert all(b[0]-a[0] == 1 and b[1]-a[1] == -1 for side in sides for a, b in zip(side, side[1:]))
    assert all((q[0]-p[0], q[1]-p[1]) == (4, 4) for p, q in zip(*sides))
    differences = [(x, y) for y in range(16) for x in range(16) if fresh.getpixel((x,y)) != spent.getpixel((x,y))]
    assert differences and all(window_mask.getpixel(p) == 255 for p in differences)
    assert fresh.getchannel("A").tobytes() == spent.getchannel("A").tobytes()
    bounds = fresh.getchannel("A").getbbox()
    assert bounds and 0 < bounds[0] < bounds[2] < 16 and 0 < bounds[1] < bounds[3] < 16
    assert set(fresh.getchannel("A").getdata()) == {0, 255}
    now = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")
    report = {
        "created_at": now, "status": "待审批的长边几何修正候选",
        "source": "既有API燃料底稿的色板与胶囊造型，本地16像素几何修整；本轮无API生成",
        "native_edit_size": [16, 16], "preview_32": "原稿最近邻2倍，不增加细节",
        "long_edges": sides, "equations": ["x+y=11", "x+y=19"],
        "step": [1, -1], "translation": [4, 4], "parallel": True,
        "silhouette_equal": True, "shell_equal_outside_window": True,
        "changed_pixels": len(differences), "visible_bounds": list(bounds),
        "palette": {k: '#'+''.join(f'{v:02x}' for v in rgb[:3]) for k, rgb in palette.items()},
        "files": {p.name: sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.iterdir()) if p.is_file()},
        "formal_resource_writes": 0, "api_calls": 0,
        "_record": "【记录 #1】"+now+"：新增平行长边、共用外壳与16原稿；保留旧候选；用途为负责人纠正后的复审。",
    }
    (OUT / "geometry-verification.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"parallel": True, "shell_equal": True, "changed_pixels": len(differences)}))


if __name__ == "__main__":
    main()
