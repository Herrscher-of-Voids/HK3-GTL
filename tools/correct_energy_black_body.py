# -*- coding: utf-8 -*-
"""在V3既有位图内只整理中间黑壳，冻结白色端盖、窗口和透明轮廓。

【变更记录 #1】2026-10-20 02:28:06（香港时间，用户澄清黑色主体）
删除：中间两侧黑壳不一致的灰亮边配色；历史文件不删。
新增：两个同宽同色且严格平移的黑色轨面及隔离观察图。
修改：只写中间黑壳46像素允许区，端盖、窗口和alpha逐字节保留V3。
用途：按用户明确的中间黑壳要求制作V4复审候选，不调用API或写正式资源。
边界：16为原稿，32与展示仅最近邻；目录已存在时拒绝覆盖。
"""
from pathlib import Path
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "output/imagegen/energy-fuel-parallel-v3-20261020"
OUT = ROOT / "output/imagegen/energy-fuel-blackbody-v4-20261020"
NEAREST = Image.Resampling.NEAREST if hasattr(Image, "Resampling") else Image.NEAREST
FONT = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 21)
SMALL = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 17)


def rails():
    left = [(x,y) for y in range(16) for x in range(16)
            if -7 <= x-y <= 7 and 11 <= x+y <= 13]
    right = [(x+3,y+3) for x,y in left]
    return left, right


def panel(sprite, dark=False):
    tile = Image.new("RGB", (256,256), "#18252d" if dark else "#dfe7ea")
    if not dark:
        draw = ImageDraw.Draw(tile)
        for y in range(0,256,16):
            for x in range(0,256,16):
                if (x//16+y//16)%2:
                    draw.rectangle((x,y,x+15,y+15), fill="#bccbd1")
    bigger = sprite.resize((256,256), NEAREST)
    tile.paste(bigger,(0,0),bigger)
    return tile


def save_comparison(originals, updated, black):
    sheet = Image.new("RGB", (1000,790), "#edf3f6")
    draw = ImageDraw.Draw(sheet)
    draw.text((24,18), "V4 · 只修中间黑壳，白色端盖保持原样", font=FONT, fill="#183a47")
    for row,name in enumerate(("fresh-fuel", "spent-fuel")):
        y=65+row*347
        draw.text((24,y), "燃料" if row==0 else "乏料", font=FONT, fill="#183a47")
        for column,(label,sprite) in enumerate((("V3 · 上一版",originals[name]),
                                                ("V4 · 黑壳同宽平行",updated[name]),
                                                ("V4 · 中间黑壳单独看",black))):
            x=24+column*328
            draw.text((x,y+31),label,font=SMALL,fill="#405c69")
            sheet.paste(panel(sprite,column==2),(x,y+61))
    draw.text((24,764), "只改中间黑色轨面；白壳、窗内填充和透明轮廓逐像素不变。", font=SMALL, fill="#405c69")
    sheet.save(OUT/"blackbody-comparison.png")


def main():
    OUT.mkdir(exist_ok=False)
    left,right=rails()
    allowed=set(left+right)
    assert len(left)==len(right)==23 and len(allowed)==46
    mask=Image.new("L",(16,16))
    for p in allowed:
        mask.putpixel(p,255)
    mask.save(OUT/"blackbody-edit-mask.png")
    originals,updated={},{}
    changes={}
    for name in ("fresh-fuel","spent-fuel"):
        with Image.open(SOURCE/(name+"-16.png")) as raw:
            original=raw.convert("RGBA")
        new=original.copy()
        # 两侧使用完全相同的三层黑色剖面，杜绝只靠整体外轮廓平行。
        for side in (left,right):
            side_sum=min(x+y for x,y in side)
            for x,y in side:
                color=(39,46,48,255) if x+y==side_sum+1 else (17,22,25,255)
                assert original.getpixel((x,y))[3]==255
                new.putpixel((x,y),color)
        differences=[(x,y) for y in range(16) for x in range(16)
                     if new.getpixel((x,y))!=original.getpixel((x,y))]
        assert set(differences)==allowed
        assert all(new.getpixel(p)==original.getpixel(p) for y in range(16) for x in range(16)
                   for p in [(x,y)] if p not in allowed)
        assert new.getchannel("A").tobytes()==original.getchannel("A").tobytes()
        assert all(new.getpixel(a)==new.getpixel(b) for a,b in zip(left,right))
        new.save(OUT/(name+"-16.png"))
        new.resize((32,32),NEAREST).save(OUT/(name+"-32-preview.png"))
        originals[name],updated[name]=original,new
        changes[name]=len(differences)
    black=Image.new("RGBA",(16,16))
    for p in allowed:
        black.putpixel(p,updated["fresh-fuel"].getpixel(p))
    black.save(OUT/"blackbody-only-16.png")
    with Image.open(SOURCE/"window-mask.png") as w:
        window=w.copy()
    window.save(OUT/"window-mask.png")
    state_changes=[(x,y) for y in range(16) for x in range(16)
                   if updated["fresh-fuel"].getpixel((x,y))!=updated["spent-fuel"].getpixel((x,y))]
    assert len(state_changes)==22 and all(window.getpixel(p)==255 for p in state_changes)
    save_comparison(originals,updated,black)
    now=datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")
    proof={
        "created_at":now,"status":"中间黑壳V4候选，待用户外观审批",
        "user_scope":"除白色端盖外，中间黑色主体的两侧必须平行等宽",
        "native_edit_size":[16,16],"rail_left":left,"rail_right":right,
        "rail_pixels_each":23,"translation":[3,3],"same_rail_cross_section":True,
        "only_allowed_changes":46,"actual_changed_pixels":changes,
        "caps_window_and_alpha_equal_to_v3":True,"state_differences_in_window":22,
        "source_files":{p.name:sha256(p.read_bytes()).hexdigest() for p in SOURCE.glob("*-16.png")},
        "files":{p.name:sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.iterdir()) if p.is_file()},
        "api_calls":0,"formal_resource_writes":0,
        "_record":"【记录 #1】"+now+"：新增两侧黑壳完全相同的平移色带；只改46像素，白端盖及窗口保留；用途为纠正误解后的复审。",
    }
    (OUT/"blackbody-verification.json").write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"black_rail_pixels_each":23,"only_body_changes":changes,"caps_preserved":True}))


if __name__=="__main__":
    main()
