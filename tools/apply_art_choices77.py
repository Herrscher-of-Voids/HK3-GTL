"""内测5修订77：按负责人确认重构十组（含复合材料平台）的物品贴图。

变更记录 #1：保留旧资源备份；新增像素级候选与正式贴图；修改范围仅限负责人点名的物品贴图。
用途：维持16×16透明像素风，使用GT/GTL原图换色或按确认要求重绘，不改变模型、注册ID和配方。
"""
from pathlib import Path
from datetime import datetime
from io import BytesIO
import colorsys
import hashlib
import json
import shutil
import zipfile
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / 'src/main/resources/assets/hk3gtl/textures/item'
LOG = ROOT / 'logs/revision77'
BACKUP = LOG / 'backup'
INSTANCE = Path('C:/Users/OWNER/AppData/Roaming/PrismLauncher/instances/GregTech-Leisure-1.4.5.2/minecraft')

def read(name):
    return Image.open(TEX / f'{name}.png').convert('RGBA')

def save(name, image):
    path = TEX / f'{name}.png'
    target = BACKUP / path.relative_to(ROOT)
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        shutil.copy2(path, target)
    image.save(path, format='PNG')

def tint(image, hex_color, preserve_alpha=True):
    rgb = tuple(int(hex_color[i:i+2], 16) / 255 for i in (1, 3, 5))
    hue, saturation, _ = colorsys.rgb_to_hsv(*rgb)
    out = image.copy()
    pixels = []
    for r, g, b, a in image.getdata():
        if a == 0:
            pixels.append((r, g, b, a)); continue
        _, _, value = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        nr, ng, nb = colorsys.hsv_to_rgb(hue, max(saturation, 0.5), value)
        pixels.append((round(nr * 255), round(ng * 255), round(nb * 255), a if preserve_alpha else 255))
    out.putdata(pixels)
    return out

def recolor_blue_to_purple(image):
    out = image.copy(); pixels=[]
    for r,g,b,a in image.getdata():
        if a and b > r * 1.08 and b > g * 1.03:
            # 保留原明度，只把蓝色相位转为紫色。
            value=max(r,g,b)/255
            nr,ng,nb=colorsys.hsv_to_rgb(0.77,0.68,value)
            pixels.append((round(nr*255),round(ng*255),round(nb*255),a))
        else: pixels.append((r,g,b,a))
    out.putdata(pixels); return out

def original_gt(path):
    jar = INSTANCE / 'mods/gtceu-1.20.1-1.4.4.jar'
    with zipfile.ZipFile(jar) as z:
        return Image.open(BytesIO(z.read(f'assets/gtceu/textures/item/{path}.png'))).convert('RGBA')

def draw_resource_probe():
    im=Image.new('RGBA',(16,16),(0,0,0,0));d=ImageDraw.Draw(im)
    steel=(144,158,180,255); dark=(19,25,42,255); glow=(186,111,235,255); cyan=(92,218,240,255)
    d.rectangle((5,5,10,10),fill=dark,outline=steel);d.rectangle((6,6,9,9),fill=(45,57,84,255),outline=glow)
    d.point((7,7),fill=cyan);d.point((8,8),fill=glow);d.rectangle((7,2,8,5),fill=steel);d.point((8,2),fill=glow)
    for points in [[(5,6),(3,3),(1,3)],[(10,6),(12,3),(14,3)],[(5,9),(3,12),(1,12)],[(10,9),(12,12),(14,12)]]:
        d.line(points,fill=steel,width=1); d.rectangle((points[-1][0]-1,points[-1][1]-1,points[-1][0]+1,points[-1][1]),fill=glow)
    d.rectangle((4,11,11,12),fill=dark,outline=steel);d.point((8,11),fill=cyan)
    return im

def draw_cosmic_bubble():
    im=Image.new('RGBA',(16,16),(0,0,0,0));d=ImageDraw.Draw(im)
    metal=(140,154,174,255); edge=(31,38,54,255); black=(3,5,14,255); purple=(137,78,209,255); star=(238,226,255,255)
    d.rectangle((4,1,11,14),fill=edge,outline=metal);d.rectangle((3,3,12,12),fill=edge,outline=metal)
    d.rectangle((5,4,10,11),fill=black,outline=purple);d.rectangle((6,5,9,10),fill=(5,7,18,255))
    for x,y in ((7,6),(9,7),(6,8),(8,9),(9,5)):
        d.point((x,y),fill=star)
    d.point((7,8),fill=(178,140,255,255));d.rectangle((2,6,3,9),fill=metal);d.rectangle((12,6,13,9),fill=metal)
    d.rectangle((5,1,10,2),fill=metal);d.rectangle((5,13,10,14),fill=metal)
    return im

def draw_beaker():
    im=Image.new('RGBA',(16,16),(0,0,0,0));d=ImageDraw.Draw(im)
    glass=(159,184,211,255); edge=(52,68,89,255); liquid=(151,54,220,255); light=(218,147,255,255)
    d.rectangle((6,1,9,4),fill=glass);d.line((5,4,10,4),fill=edge,width=1)
    d.line([(5,5),(4,12),(6,14),(10,14),(12,12),(11,5)],fill=glass,width=1)
    d.polygon([(5,9),(11,9),(11,12),(9,14),(6,13),(5,12)],fill=liquid)
    d.line((6,10,10,10),fill=light);d.point((8,11),fill=(244,204,255,255));d.point((7,12),fill=light)
    return im

def draw_nano_robot():
    im=Image.new('RGBA',(16,16),(0,0,0,0));d=ImageDraw.Draw(im)
    dark=(25,28,45,255); metal=(140,160,186,255); purple=(182,94,235,255); cyan=(97,226,225,255)
    d.rectangle((6,5,9,10),fill=dark,outline=metal);d.rectangle((7,6,8,7),fill=purple);d.point((8,8),fill=cyan)
    d.line([(6,6),(3,3),(2,4)],fill=metal);d.line([(9,6),(12,3),(13,4)],fill=metal)
    d.line([(6,9),(3,12),(2,11)],fill=metal);d.line([(9,9),(12,12),(13,11)],fill=metal)
    for x,y in ((2,4),(13,4),(2,11),(13,11)): d.rectangle((x-1,y-1,x+1,y),fill=purple)
    d.point((7,3),fill=cyan);d.line((7,4,7,2),fill=metal)
    return im

def draw_rule_carrier():
    im=Image.new('RGBA',(16,16),(0,0,0,0));d=ImageDraw.Draw(im)
    shell=(55,65,88,255); edge=(153,177,207,255); glyph=(187,104,245,255); bright=(235,210,255,255)
    d.polygon([(3,2),(12,2),(14,4),(14,12),(12,14),(4,14),(2,12),(2,4)],fill=shell,outline=edge)
    d.rectangle((4,4,12,12),fill=(26,31,53,255),outline=(91,111,145,255))
    d.line([(5,9),(7,9),(7,6),(10,6),(10,8),(8,8),(8,11),(5,11),(5,9)],fill=glyph,width=1)
    d.point((10,10),fill=bright);d.point((6,5),fill=bright);d.rectangle((6,13,9,13),fill=glyph)
    return im

def main():
    LOG.mkdir(exist_ok=True); before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in TEX.glob('*.png')}
    # 1. 燃料棒壳体：整体紫色染色。
    save('honkai_fuel_rod_casing',tint(read('honkai_fuel_rod_casing'),'#8b45c6'))
    # 2. 资源探测器：以GT探测器识别逻辑为参考，重绘更强的四臂探测器。
    save('unmanned_resource_probe',draw_resource_probe())
    # 3. 世界泡容器：扩大外壳，中心替换为黑色星空宇宙。
    save('sealed_real_world_bubble',draw_cosmic_bubble())
    # 4. 休伯利安推进组件：只把原图蓝色功能区变成紫色，金属保留。
    save('hyperion_thruster_assembly',recolor_blue_to_purple(original_gt('gravitation_engine_unit')))
    # 5. 仿制炎核心：沿用仿制理核心轮廓，只改变中心核色。
    reason=read('imitation_reason_core'); flame=read('imitation_flame_core'); out=reason.copy();pix=[]
    for y in range(16):
        for x in range(16):
            r,g,b,a=reason.getpixel((x,y));
            if a and 5<=x<=10 and 4<=y<=11:
                v=max(r,g,b)/255; nr,ng,nb=colorsys.hsv_to_rgb(0.07,0.76,v);pix.append((round(nr*255),round(ng*255),round(nb*255),a))
            else: pix.append((r,g,b,a))
    out.putdata(pix);save('imitation_flame_core',out)
    # 6. 废料残渣：整体染色为更深紫色。
    save('soulium_swarf',tint(read('soulium_swarf'),'#4e267d'))
    # 7. 试作型探测器：负责人确认保留当前版本，明确不写入。
    # 8. 分析样本：重绘为装有紫色液态崩坏能的烧杯。
    save('honkai_analysis_sample',draw_beaker())
    # 9. 分离滤芯：整体染色，并把外框加深为紫色。
    filt=tint(read('separation_filter'),'#8c48cf');dp=ImageDraw.Draw(filt);purple=(139,61,203,255)
    for x in range(2,14):
        for y in range(2,14):
            if x in (2,3,12,13) or y in (2,3,12,13):
                r,g,b,a=filt.getpixel((x,y));
                if a: dp.point((x,y),fill=purple)
    save('separation_filter',filt)
    # 10. 纳米构建单元：改为纳米机器人形态。
    save('nano_building_unit',draw_nano_robot())
    # 11. 重构规则载体：完全按HK3规则载体重绘，不引用GT原图。
    save('reconstruction_rule_carrier',draw_rule_carrier())
    # 12. 四类复合材料：整体染色，按平台/电压主题色区分。
    for name,color in {'conducting_composite':'#b45fe2','confining_composite':'#7c55d6','reconstructing_composite':'#693db0','cognitive_composite':'#a43bc8','composite_offcut':'#51216f'}.items():
        save(name,tint(read(name),color))
    after={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in TEX.glob('*.png')}
    changed=[p for p in after if before.get(p)!=after[p]]
    report={'revision':77,'generated_at':datetime.now().astimezone().isoformat(),'changed':changed,'unchanged':['prototype_honkai_detector'],'formal_assets_only':True,'count_changed':len(changed)}
    (LOG/'texture-change.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False))

if __name__=='__main__': main()
