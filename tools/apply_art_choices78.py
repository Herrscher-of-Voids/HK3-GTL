"""内测5修订78：按负责人要求重绘十组正式物品贴图。"""
from pathlib import Path
from io import BytesIO
import colorsys
import hashlib
import json
import shutil
import zipfile
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / "src/main/resources/assets/hk3gtl/textures/item"
LOG = ROOT / "logs/revision78"
BACKUP = LOG / "backup/src/main/resources/assets/hk3gtl/textures/item"
REV77 = ROOT / "logs/revision77/backup/src/main/resources/assets/hk3gtl/textures/item"
INSTANCE = Path("C:/Users/OWNER/AppData/Roaming/PrismLauncher/instances/GregTech-Leisure-1.4.5.2/minecraft")

def rgba(hex_color):
    return tuple(int(hex_color[i:i + 2], 16) for i in (1, 3, 5)) + (255,)

def source(name):
    archived = REV77 / f"{name}.png"
    # 仿制理核心未在修订77范围内，直接使用未改动的正式参照图。
    return Image.open(archived if archived.exists() else TEX / f"{name}.png").convert("RGBA")

def backup(name):
    current = TEX / f"{name}.png"
    target = BACKUP / f"{name}.png"
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        shutil.copy2(current, target)

def save(name, image):
    backup(name)
    image.save(TEX / f"{name}.png", format="PNG")

def tint_with_material(image, color):
    """整体染色但保留GT像素明暗与金属边缘。"""
    hue, saturation, _ = colorsys.rgb_to_hsv(*(v / 255 for v in rgba(color)[:3]))
    result = image.copy(); pixels = []
    for red, green, blue, alpha in image.getdata():
        if alpha == 0:
            pixels.append((red, green, blue, alpha)); continue
        _, _, value = colorsys.rgb_to_hsv(red / 255, green / 255, blue / 255)
        local_saturation = min(0.92, max(saturation, 0.42) + (0.10 if value < 0.30 else 0.0))
        r2, g2, b2 = colorsys.hsv_to_rgb(hue, local_saturation, value)
        pixels.append((round(r2 * 255), round(g2 * 255), round(b2 * 255), alpha))
    result.putdata(pixels)
    return result

def gt_texture(name):
    jar = INSTANCE / "mods/gtceu-1.20.1-1.4.4.jar"
    with zipfile.ZipFile(jar) as file:
        return Image.open(BytesIO(file.read(f"assets/gtceu/textures/item/{name}.png"))).convert("RGBA")

def recolor_blue(image):
    out = image.copy(); pixels = []
    for r, g, b, a in image.getdata():
        if a and b > r * 1.10 and b > g * 1.04:
            _, _, value = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            nr, ng, nb = colorsys.hsv_to_rgb(0.77, 0.72, value)
            pixels.append((round(nr * 255), round(ng * 255), round(nb * 255), a))
        else:
            pixels.append((r, g, b, a))
    out.putdata(pixels)
    return out

def fuel_casing():
    im = Image.new("RGBA", (16, 16)); d = ImageDraw.Draw(im)
    outline=rgba("#21152F"); shadow=rgba("#442065"); body=rgba("#7136A0"); mid=rgba("#9953D0"); light=rgba("#D1A3F0"); steel=rgba("#7A8298")
    d.rectangle((4, 1, 11, 14), fill=outline)
    d.rectangle((5, 2, 10, 13), fill=body)
    d.rectangle((5, 3, 5, 12), fill=light); d.rectangle((10, 3, 10, 12), fill=shadow)
    for y in (3, 6, 9, 12):
        d.rectangle((4, y, 11, y + 1), fill=outline); d.rectangle((5, y, 10, y), fill=mid)
    d.rectangle((3, 1, 12, 2), fill=steel); d.rectangle((4, 1, 11, 1), fill=light)
    d.rectangle((3, 13, 12, 14), fill=steel); d.rectangle((4, 13, 11, 13), fill=shadow)
    d.point((6, 4), fill=rgba("#F0D8FF")); d.point((6, 10), fill=rgba("#E6C5FF"))
    return im

def resource_probe():
    im=Image.new("RGBA",(16,16)); d=ImageDraw.Draw(im)
    edge=rgba("#182030"); shade=rgba("#344158"); steel=rgba("#8998B2"); high=rgba("#D3DDEC"); violet=rgba("#A95CED"); glow=rgba("#E7C7FF"); cyan=rgba("#57D5EC"); gold=rgba("#BB8C42")
    d.polygon([(5,3),(10,3),(13,6),(12,11),(9,13),(4,12),(2,9),(3,5)], fill=edge)
    d.polygon([(5,4),(10,4),(12,6),(11,10),(8,12),(4,11),(3,9),(4,5)], fill=shade)
    d.line([(5,4),(10,4),(12,6)],fill=high); d.line([(3,9),(4,11),(8,12)],fill=steel)
    d.rectangle((5,6,10,10),fill=edge,outline=steel);d.rectangle((6,7,9,9),fill=violet);d.point((7,7),fill=glow);d.point((8,8),fill=cyan)
    d.line([(7,5),(6,1)],fill=steel); d.line([(8,5),(10,1)],fill=steel); d.point((6,1),fill=violet); d.point((10,1),fill=violet)
    d.line([(4,7),(1,5)],fill=steel); d.line([(11,7),(14,5)],fill=steel);d.rectangle((0,4,2,6),fill=edge,outline=violet);d.rectangle((13,4,15,6),fill=edge,outline=violet)
    d.line([(5,10),(2,12)],fill=steel);d.line([(10,10),(13,12)],fill=steel);d.point((2,12),fill=glow);d.point((13,12),fill=glow)
    d.rectangle((7,13,8,14),fill=gold);d.point((7,14),fill=high)
    return im

def world_bubble():
    im=Image.new("RGBA",(16,16));d=ImageDraw.Draw(im)
    edge=rgba("#1B2434");shadow=rgba("#465168");steel=rgba("#9EABC0");high=rgba("#DFE8F5");ring=rgba("#9250D1");space=rgba("#050814");nebula=rgba("#263B72");star=rgba("#F0E7FF")
    d.rectangle((3,2,12,13),fill=edge);d.rectangle((4,3,11,12),fill=shadow);d.rectangle((4,2,11,3),fill=steel);d.rectangle((5,2,10,2),fill=high);d.rectangle((4,12,11,13),fill=steel);d.rectangle((5,13,10,13),fill=edge)
    d.rectangle((2,5,3,10),fill=steel);d.rectangle((12,5,13,10),fill=steel);d.point((2,5),fill=high);d.point((13,10),fill=edge)
    d.rectangle((3,5,12,5),fill=ring);d.rectangle((3,10,12,10),fill=ring)
    d.ellipse((5,4,10,11),fill=rgba("#121A36"),outline=rgba("#6C3AA2"));d.ellipse((6,5,9,10),fill=space)
    d.arc((6,6,10,10),190,320,fill=nebula);d.point((7,6),fill=star);d.point((9,6),fill=rgba("#9FC7FF"));d.point((8,8),fill=star);d.point((7,9),fill=rgba("#C79AFF"));d.point((9,10),fill=star)
    return im

def flame_core():
    im=source("imitation_reason_core"); d=ImageDraw.Draw(im)
    dark=rgba("#421522");red=rgba("#B53929");orange=rgba("#F07A2E");gold=rgba("#FFD269");white=rgba("#FFF0C4")
    d.polygon([(7,4),(9,5),(10,8),(8,11),(6,9),(6,6)],fill=dark)
    d.polygon([(8,4),(9,7),(8,10),(7,9),(7,6)],fill=red)
    d.polygon([(8,5),(9,8),(8,9),(7,8)],fill=orange);d.point((8,6),fill=gold);d.point((8,7),fill=white)
    return im

def analysis_beaker():
    im=Image.new("RGBA",(16,16));d=ImageDraw.Draw(im)
    edge=rgba("#263447");glass=rgba("#91A9C5");light=rgba("#D8F3FF");shade=rgba("#5C718D");liquid=rgba("#842BC1");bright=rgba("#DA8DFF");deep=rgba("#4A176F")
    d.rectangle((6,1,9,4),fill=edge);d.rectangle((7,1,8,4),fill=glass);d.line((5,4,10,4),fill=light)
    d.line([(5,5),(4,11),(5,13),(7,14),(10,14),(12,12),(11,5)],fill=edge,width=1)
    d.line([(6,5),(5,11)],fill=light);d.line([(10,5),(11,11)],fill=shade)
    d.polygon([(5,9),(11,9),(11,12),(9,13),(6,13),(5,11)],fill=deep);d.polygon([(5,10),(11,10),(10,12),(6,12)],fill=liquid);d.line((5,10,11,10),fill=bright)
    d.point((8,11),fill=light);d.point((9,12),fill=bright);d.point((9,7),fill=bright);d.point((10,8),fill=light)
    return im

def separation_filter():
    im=source("separation_filter"); d=ImageDraw.Draw(im)
    edge=rgba("#30174D");dark=rgba("#54237D");mid=rgba("#8743B9");light=rgba("#C28BE8");metal=rgba("#93A1B8")
    d.rectangle((3,2,12,13),fill=edge);d.rectangle((4,3,11,12),fill=dark)
    d.rectangle((4,3,11,4),fill=light);d.rectangle((4,11,11,12),fill=rgba("#3B205A"))
    for y in (5,7,9):
        d.rectangle((5,y,10,y),fill=metal);d.point((5,y),fill=light);d.point((10,y),fill=edge)
    d.rectangle((2,4,3,11),fill=mid);d.rectangle((12,4,13,11),fill=mid);d.point((2,4),fill=light);d.point((13,11),fill=edge)
    return im

def nano_robot():
    im=Image.new("RGBA",(16,16));d=ImageDraw.Draw(im)
    edge=rgba("#1B2030");steel=rgba("#7888A2");high=rgba("#C8D6EA");violet=rgba("#9B4DDA");glow=rgba("#E8CCFF");cyan=rgba("#69DDE8")
    d.polygon([(6,5),(9,5),(11,7),(10,10),(8,11),(5,9),(5,7)],fill=edge);d.rectangle((6,6,9,9),fill=rgba("#3A4058"));d.rectangle((7,7,8,8),fill=violet);d.point((7,7),fill=cyan);d.point((8,8),fill=glow)
    for line in [[(5,6),(3,4),(1,4)],[(10,6),(12,4),(14,4)],[(5,9),(3,11),(1,11)],[(10,9),(12,11),(14,11)],[(6,10),(5,13),(3,14)],[(9,10),(10,13),(12,14)]]:
        d.line(line,fill=steel);d.point(line[1],fill=violet);d.point(line[-1],fill=high)
    d.line([(7,5),(7,2)],fill=steel);d.point((7,2),fill=glow);d.point((6,3),fill=cyan);d.point((8,3),fill=cyan)
    return im

def rule_carrier():
    im=Image.new("RGBA",(16,16));d=ImageDraw.Draw(im)
    edge=rgba("#172136");side=rgba("#35445E");steel=rgba("#A3B4CB");violet=rgba("#8E43D0");glow=rgba("#E5C5FF");dark=rgba("#24113E")
    d.polygon([(4,2),(11,2),(14,5),(14,10),(10,14),(4,13),(1,10),(1,5)],fill=edge)
    d.polygon([(4,3),(10,3),(12,5),(12,10),(9,12),(4,11),(3,9),(3,5)],fill=side)
    d.line([(4,3),(10,3),(12,5)],fill=steel);d.line([(3,9),(4,11),(9,12)],fill=rgba("#5F7594"))
    d.polygon([(6,4),(10,5),(10,10),(7,11),(5,9),(5,6)],fill=dark,outline=violet)
    d.line([(6,6),(9,6),(9,7)],fill=glow);d.line([(6,8),(9,8)],fill=violet);d.line([(7,5),(7,10)],fill=glow);d.point((8,9),fill=glow)
    d.rectangle((1,6,3,8),fill=steel);d.rectangle((12,6,14,8),fill=steel);d.point((2,6),fill=glow);d.point((13,8),fill=violet)
    return im

def soulium_swarf():
    im=tint_with_material(source("soulium_swarf"),"#52246E");d=ImageDraw.Draw(im)
    d.point((6,4),fill=rgba("#B47AE1"));d.point((9,6),fill=rgba("#8C52B8"));d.point((5,9),fill=rgba("#281137"));d.point((10,10),fill=rgba("#C693EB"))
    return im

def composites():
    colors={"conducting_composite":"#9156D5","confining_composite":"#5F46B9","reconstructing_composite":"#7B43CE","cognitive_composite":"#B13DC7","composite_offcut":"#4D1B77"}
    for name,color in colors.items():
        im=tint_with_material(source(name),color);d=ImageDraw.Draw(im)
        # 只补一处材质高光，保留原图主体与平台差异。
        for x,y in ((5,4),(6,4),(5,5)):
            if im.getpixel((x,y))[3]: d.point((x,y),fill=rgba("#DFC8FF"))
        save(name,im)

def make_preview(names):
    scale=12; width=5*190; height=((len(names)+4)//5)*220
    out=Image.new("RGBA",(width,height),(20,27,40,255)); d=ImageDraw.Draw(out)
    for index,name in enumerate(names):
        x=(index%5)*190; y=(index//5)*220; image=Image.open(TEX/f"{name}.png").convert("RGBA")
        out.alpha_composite(image.resize((image.width*scale,image.height*scale),Image.Resampling.NEAREST),(x+(190-image.width*scale)//2,y+28))
        d.text((x+8,y+8),name,fill=(240,244,252,255))
    out.save(LOG/"texture-preview.png")

def main():
    LOG.mkdir(exist_ok=True)
    names=["honkai_fuel_rod_casing","unmanned_resource_probe","sealed_real_world_bubble","hyperion_thruster_assembly","imitation_flame_core","soulium_swarf","honkai_analysis_sample","separation_filter","nano_building_unit","reconstruction_rule_carrier","conducting_composite","confining_composite","reconstructing_composite","cognitive_composite","composite_offcut"]
    before={name:hashlib.sha256((TEX/f"{name}.png").read_bytes()).hexdigest() for name in names}
    save("honkai_fuel_rod_casing",fuel_casing())
    save("unmanned_resource_probe",resource_probe())
    save("sealed_real_world_bubble",world_bubble())
    save("hyperion_thruster_assembly",recolor_blue(gt_texture("gravitation_engine_unit")))
    save("imitation_flame_core",flame_core())
    save("soulium_swarf",soulium_swarf())
    save("honkai_analysis_sample",analysis_beaker())
    save("separation_filter",separation_filter())
    save("nano_building_unit",nano_robot())
    save("reconstruction_rule_carrier",rule_carrier())
    composites()
    after={name:hashlib.sha256((TEX/f"{name}.png").read_bytes()).hexdigest() for name in names}
    make_preview(names)
    report={"revision":78,"changed":[name for name in names if after[name] != hashlib.sha256((BACKUP/f"{name}.png").read_bytes()).hexdigest()],"unchanged":["prototype_honkai_detector"],"scope":"十组负责人点名资源重绘，复合材料组含五张平台变体；未修改模型、注册ID或配方。"}
    (LOG/"texture-change.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False))

if __name__ == "__main__":
    main()
