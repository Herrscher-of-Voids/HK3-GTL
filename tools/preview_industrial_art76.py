"""内测5修订76：审计新增物品原图来源并生成待确认的整体染色候选。

变更记录 #1：实际运行时间写入 manifest；新增只读资源审计和候选图。
删除：无。修改：无正式贴图。用途：排除旧物品、电子部件及理核心后供用户选择。
生成器函数仅通过 AST 提取纯绘图函数，不执行历史生成脚本的注册、写入或删除操作。
"""
from pathlib import Path
from datetime import datetime
from io import BytesIO
import ast
import colorsys
import hashlib
import json
import zipfile
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'logs/revision76/art-candidates'
ASSETS = ROOT / 'src/main/resources/assets/hk3gtl'
INSTANCE = Path('C:/Users/OWNER/AppData/Roaming/PrismLauncher/instances/GregTech-Leisure-1.4.5.2/minecraft')
ROWS = [
    ('A 探测器', 'prototype_honkai_detector', 'gtceu', 'uv_sensor', '#AF7FDF'),
    ('B 分析样本', 'honkai_analysis_sample', 'gtceu', 'petri_dish', '#C288E8'),
    ('C 分离滤芯', 'separation_filter', 'gtlcore', 'protonated_fullerene_sieving_matrix', '#7DCBB3'),
    ('D 纳米构建单元', 'nano_building_unit', 'kubejs', 'precision_circuit_assembly_robot_mk1', '#B38CE0'),
    ('E 重构规则载体', 'reconstruction_rule_carrier', 'gtceu', 'data_stick', '#81BACD'),
    ('F 复合材料', 'conducting_composite', 'gtceu', 'carbon_fiber_plate', '#8DCDB4'),
    ('G 燃料棒壳体', 'honkai_fuel_rod_casing', 'kubejs', 'reactor_fuel_rod', '#A9B4C8'),
    ('H 资源探测器', 'unmanned_resource_probe', 'kubejs', 'space_probe_mk1', '#829DD9'),
    ('I 世界泡容器', 'sealed_real_world_bubble', 'kubejs', 'contained_exotic_matter', '#917BD9'),
    ('J 舰船推进组件', 'hyperion_thruster_assembly', 'gtceu', 'gravitation_engine_unit', '#9DADCE'),
    ('K 仿制炎核心', 'imitation_flame_core', 'gtlcore', 'miracle_crystal', '#ED9158'),
    ('L 废料与残渣', 'soulium_swarf', 'gtceu', 'material_sets/metallic/dust', '#9D87AF'),
]

def sha(data):
    return hashlib.sha256(data).hexdigest()

def current(ident):
    model = json.loads((ASSETS / f'models/item/{ident}.json').read_text('utf-8'))
    key = model['textures']['layer0']
    ns, rel = key.split(':')
    p = ROOT / f'src/main/resources/assets/{ns}/textures/{rel}.png'
    return p, Image.open(p).convert('RGBA')

def original(ns, name):
    rel = f'assets/{ns}/textures/item/{name}.png'
    if ns == 'kubejs':
        p = INSTANCE / 'kubejs' / rel
        raw = p.read_bytes()
        source = str(p)
    else:
        p = INSTANCE / 'mods' / ('gtceu-1.20.1-1.4.4.jar' if ns == 'gtceu' else 'gtlcore-1.2.3.2-fix2.jar')
        with zipfile.ZipFile(p) as z:
            raw = z.read(rel)
        source = str(p) + '!/' + rel
    return Image.open(BytesIO(raw)).convert('RGBA'), source, sha(raw)

def tint(im, color):
    rgb = tuple(int(color[i:i+2], 16) / 255 for i in (1, 3, 5))
    hue, saturation, _ = colorsys.rgb_to_hsv(*rgb)
    result = im.copy()
    result.putdata([tuple(round(v * 255) for v in colorsys.hsv_to_rgb(hue, saturation, max(r,g,b)/255)) + (a,)
                    if a else (r,g,b,a) for r,g,b,a in im.getdata()])
    assert result.getchannel('A').tobytes() == im.getchannel('A').tobytes()
    assert [max(p[:3]) for p in result.getdata()] == [max(p[:3]) for p in im.getdata()]
    return result

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    before = {str(p): sha(p.read_bytes()) for p in ASSETS.rglob('*') if p.is_file()}
    catalog = json.loads((ROOT/'src/main/resources/data/hk3gtl/catalog/industrial_content.json').read_text('utf-8'))['entries']
    parsed = ast.parse((ROOT/'tools/generate_industrial_content.py').read_text('utf-8'))
    pure = ast.Module(body=[node for node in parsed.body if isinstance(node, ast.FunctionDef) and node.name in ('palette','texture')], type_ignores=[])
    env = {'Image': Image, 'ImageDraw': ImageDraw, 'hashlib': hashlib}
    exec(compile(pure, '<只读历史绘图函数>', 'exec'), env)
    old_ids = {'honkai_energy_crystal','imitation_reason_core','honkai_fuel_rod','dense_honkai_fuel_rod',
               'soulium_proto_mass','stabilized_soulium_proto_mass','narrative_codex'}
    inventory = []
    for entry in catalog:
        if entry['kind'] != 'item':
            continue
        ident = entry['id']
        excluded = ident in old_ids or entry['family'] == 'circuit' or 'reason_core' in ident
        p, im = current(ident)
        generated = env['texture'](entry).convert('RGBA')
        exact = im.size == generated.size and im.tobytes() == generated.tobytes()
        inventory.append({**entry, 'texture':str(p.relative_to(ROOT)), 'sha256':sha(p.read_bytes()),
                          'status':'排除：旧物品／电子部件／理核心' if excluded else '确认与自绘生成器逐像素一致，待重构候选' if exact else '与历史生成器不一致，来源待核对，暂不改写',
                          'matches_procedural_generator':exact})
    font = lambda size: ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',size)
    manifest=[]
    for page, rows in enumerate((ROWS[:6], ROWS[6:]),1):
        sheet=Image.new('RGB',(1100,1060),'#151C28');d=ImageDraw.Draw(sheet)
        d.text((24,16),f'内测5物品贴图候选 {page}/2 · 未应用',font=font(25),fill='white')
        d.text((24,57),'左：当前物品　中：GT/GTL原图　右：整体染色候选；动画仅展示首帧',font=font(17),fill='#BAC9DE')
        for n,(title,ident,ns,name,color) in enumerate(rows):
            y=100+n*155
            p,old=current(ident);src,source,digest=original(ns,name);recolored=tint(src,color)
            d.rounded_rectangle((18,y,1082,y+145),8,fill='#222E40')
            d.text((30,y+14),title,font=font(20),fill='white')
            d.text((30,y+51),ident,font=font(11),fill='#BAC9DE')
            d.text((30,y+81),ns+':'+name,font=font(11),fill='#BAC9DE')
            for col,(pic,label) in enumerate(((old,'当前'),(src,'原图'),(recolored,'整体染色'))):
                first=pic.crop((0,0,pic.width,min(pic.width,pic.height))).resize((96,96),Image.Resampling.NEAREST)
                x=535+col*180;sheet.paste(first,(x,y+10),first)
                d.text((x,y+112),label,font=font(16),fill='#DBE7F7')
            manifest.append({'id':ident,'source':source,'source_sha256':digest,'color':color,'size':list(src.size),'alpha_and_value_preserved':True})
        sheet.save(OUT/f'candidates-{page}.png')
    after={str(p):sha(p.read_bytes()) for p in ASSETS.rglob('*') if p.is_file()}
    assert before == after
    result={'revision':76,'time':datetime.now().astimezone().isoformat(),'status':'仅候选，未修改正式资源',
            'asset_hashes_unchanged':True,'inventory':inventory,'previews':manifest}
    (OUT/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'items':len(inventory),'excluded':sum(x['status'].startswith('排除') for x in inventory),
                      'confirmed_procedural':sum(x['status'].startswith('确认') for x in inventory),'formal_assets_unchanged':True},ensure_ascii=False))

if __name__ == '__main__':
    main()

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
