"""内测5修订79：纠正整体染色范围，使用GT/GTL原图而非自绘轮廓。"""
from pathlib import Path
from io import BytesIO
import colorsys
import hashlib
import json
import shutil
import zipfile
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / "src/main/resources/assets/hk3gtl/textures/item"
LOG = ROOT / "logs/revision79"
BACKUP = LOG / "backup/src/main/resources/assets/hk3gtl/textures/item"
INSTANCE = Path("C:/Users/OWNER/AppData/Roaming/PrismLauncher/instances/GregTech-Leisure-1.4.5.2/minecraft")

def archive(name):
    source = TEX / f"{name}.png"; target = BACKUP / f"{name}.png"
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists(): shutil.copy2(source, target)

def read_jar(jar, member):
    with zipfile.ZipFile(jar) as file:
        return Image.open(BytesIO(file.read(member))).convert("RGBA")

def tint(image, color):
    rgb = tuple(int(color[i:i + 2], 16) / 255 for i in (1, 3, 5))
    hue, saturation, _ = colorsys.rgb_to_hsv(*rgb)
    pixels=[]
    for red, green, blue, alpha in image.getdata():
        if alpha == 0:
            pixels.append((red, green, blue, alpha)); continue
        _, _, value = colorsys.rgb_to_hsv(red / 255, green / 255, blue / 255)
        nr, ng, nb = colorsys.hsv_to_rgb(hue, max(0.48, saturation), value)
        pixels.append((round(nr * 255), round(ng * 255), round(nb * 255), alpha))
    result=image.copy(); result.putdata(pixels); return result

def purple_border(image):
    """在不改变原图内部网格的前提下，把最外一圈不透明框架改为紫色。"""
    out=image.copy(); px=out.load(); opaque=[(x,y) for y in range(out.height) for x in range(out.width) if px[x,y][3]]
    left=min(x for x,_ in opaque); right=max(x for x,_ in opaque); top=min(y for _,y in opaque); bottom=max(y for _,y in opaque)
    border=(124,57,184,255)
    for x,y in opaque:
        if x-left<=2 or right-x<=2 or y-top<=2 or bottom-y<=2: px[x,y]=border
    return out

def save(name, image):
    archive(name); image.save(TEX / f"{name}.png", format="PNG")

def main():
    LOG.mkdir(exist_ok=True)
    gtceu=INSTANCE / "mods/gtceu-1.20.1-1.4.4.jar"
    gtlcore=INSTANCE / "mods/gtlcore-1.2.3.2-fix2.jar"
    kubejs=INSTANCE / "kubejs/assets/kubejs/textures/item/reactor_fuel_rod.png"
    names=["honkai_fuel_rod_casing","soulium_swarf","separation_filter","conducting_composite","confining_composite","reconstructing_composite","cognitive_composite","composite_offcut"]
    save("honkai_fuel_rod_casing", tint(Image.open(kubejs).convert("RGBA"), "#8D49C9"))
    save("soulium_swarf", tint(read_jar(gtceu,"assets/gtceu/textures/item/material_sets/metallic/dust.png"), "#4E267D"))
    matrix=read_jar(gtlcore,"assets/gtlcore/textures/item/protonated_fullerene_sieving_matrix.png")
    save("separation_filter", purple_border(tint(matrix,"#7D4BB0")))
    colors={"conducting_composite":"#8A55D1","confining_composite":"#6848BC","reconstructing_composite":"#8346C7","cognitive_composite":"#B13CC8","composite_offcut":"#4D1A75"}
    base=read_jar(gtceu,"assets/gtceu/textures/item/carbon_fiber_plate.png")
    for name,color in colors.items(): save(name,tint(base,color))
    report={"revision":79,"changed":names,"source_policy":"燃料壳、废料、滤芯与复合材料均从明确的GT/GTL/KubeJS原图整体染色；滤芯仅额外将外框改为紫色。","unchanged_custom_assets":["unmanned_resource_probe","sealed_real_world_bubble","hyperion_thruster_assembly","imitation_flame_core","honkai_analysis_sample","nano_building_unit","reconstruction_rule_carrier","prototype_honkai_detector"]}
    (LOG/"texture-change.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False))

if __name__ == "__main__": main()
