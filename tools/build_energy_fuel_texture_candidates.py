# -*- coding: utf-8 -*-
"""能源载体、燃料与乏料的完整图层候选；只写交付目录，不接入正式资源。
【变更记录 #1】2026-10-19 13:47:35（香港时间，文档候选批次172）
删除：无；新增：13个载体族共39项候选、完整GT图层来源与原像素核对。
修改：燃料沿用现有HK棒形像素，仅替换紫色活性区域；GT载体保留全部图层与原色覆盖。
用途：提供用户逐项审批的新贴图，不因工艺范围获批而自动写入正式资产或配方。
"""
# 【追加记录 #2】2026-10-19 13:53:53：新增完整联系表进入ZIP；修改工艺页链接为实际文件名；用途为可直接审阅与一致打包，未改正式资源。
from pathlib import Path
from datetime import datetime, timezone, timedelta
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import colorsys
import hashlib
import html
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
INSTANCE = Path('C:/Users/OWNER/AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版/minecraft')
JAR = INSTANCE/'mods/gtceu-1.20.1-1.4.4.jar'
OUT = ROOT/'deliveries/能源燃料工艺_39项贴图候选_R172_20261019'
ASSETS = ROOT/'src/main/resources/assets/hk3gtl'
FAMILIES = [
    ('carbon', '吸附碳芯', '#746A86', 'carbon_fiber_mesh'),
    ('zeolite', '分子筛', '#BEAA79', 'material_sets/dull/dust'),
    ('silica_gel', '硅胶凝固', '#8ACBC6', 'material_sets/dull/gem'),
    ('silicon_carbide', '碳化硅多孔陶瓷', '#6F9C89', 'material_sets/dull/gem'),
    ('boron_carbide', '碳化硼梯度颗粒', '#785E95', 'material_sets/dull/round'),
    ('zirconia', '氧化锆梯度陶瓷', '#D5CCB9', 'material_sets/dull/round'),
    ('diamond_copper', '金刚石铜骨架', '#D69C62', 'material_sets/dull/ingot'),
    ('graphene', '石墨烯层间', '#657F9B', 'carbon_fiber_plate'),
    ('titanium_carbide', '碳化钛金属陶瓷', '#8A96AB', 'material_sets/dull/plate'),
    ('alumina', '氧化铝绝缘微珠', '#D1C2CA', 'material_sets/dull/round'),
    ('tungsten', '钨微通道', '#9396B7', 'material_sets/dull/rod'),
    ('ptfe_membrane', 'PTFE冷端膜匣', '#7ABAB7', 'material_sets/dull/foil'),
    ('pbi_microcapsule', 'PBI冷端微胶囊', '#C5A66A', 'material_sets/dull/round'),
]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def tint(source, color, active_only=False, depleted=False):
    result = source.copy()
    target = tuple(int(color[i:i+2], 16)/255 for i in (1, 3, 5))
    for y in range(source.height):
        for x in range(source.width):
            r, g, b, a = source.getpixel((x, y))
            if not a:
                continue
            h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
            if active_only and not (.62 <= h <= .91 and s > .28):
                continue
            strength = .66 if depleted else 1
            result.putpixel((x, y), tuple(round(255*c*v*strength) for c in target)+(a,))
    assert result.getchannel('A').tobytes() == source.getchannel('A').tobytes()
    return result


def save_item(z, slug, name, form, color, carrier_model):
    prefix = 'depleted_honkai_' if form == 'depleted' else 'honkai_'
    suffix = '_carrier' if form == 'carrier' else '_fuel'
    item = prefix+slug+suffix
    role = {'carrier': '载体', 'fuel': '燃料', 'depleted': '乏料'}[form]
    originals = []
    if form == 'carrier':
        model_path = f'assets/gtceu/models/item/{carrier_model}.json'
        model_raw = z.read(model_path)
        model = json.loads(model_raw)
        assert model.get('parent') in ('item/generated', 'minecraft:item/generated', 'item/handheld')
        (OUT/'原始来源'/model_path).parent.mkdir(parents=True, exist_ok=True)
        (OUT/'原始来源'/model_path).write_bytes(model_raw)
        for layer, texture in model['textures'].items():
            ns, local = texture.split(':')
            path = f'assets/{ns}/textures/{local}.png'
            originals.append((layer, path, z.read(path), not path.endswith('_overlay.png')))
    else:
        base = 'depleted_honkai_fuel_rod' if form == 'depleted' else 'honkai_fuel_rod'
        path = 'assets/hk3gtl/textures/item/'+base+'.png'
        originals.append(('layer0', path, (ASSETS/'textures/item'/f'{base}.png').read_bytes(), True))
    merged = Image.new('RGBA', (16, 16))
    original_merged = Image.new('RGBA', (16, 16))
    layers = []
    for layer, path, raw, tinted in originals:
        image = Image.open(BytesIO(raw)).convert('RGBA')
        assert image.size == (16, 16), (path, image.size)
        original = OUT/'原始来源'/path
        original.parent.mkdir(parents=True, exist_ok=True)
        original.write_bytes(raw)
        variant = tint(image, color, form != 'carrier', form == 'depleted') if tinted else image.copy()
        dest = OUT/'候选资源/assets/hk3gtl/textures/item/energy_fuel'/item/(layer+'.png')
        dest.parent.mkdir(parents=True, exist_ok=True)
        if tinted:
            variant.save(dest)
        else:
            dest.write_bytes(raw)
        original_merged.alpha_composite(image)
        merged.alpha_composite(variant)
        layers.append({'layer':layer, 'source':path, 'source_sha256':sha(raw),
                       'source_relative':original.relative_to(OUT).as_posix(),
                       'candidate_relative':dest.relative_to(OUT).as_posix(),
                       'candidate_sha256':sha(dest.read_bytes()), 'tinted':tinted,
                       'alpha_identical':variant.getchannel('A').tobytes()==image.getchannel('A').tobytes(),
                       'unchanged_overlay_bytes':not tinted and raw == dest.read_bytes(),
                       'dimensions':[16,16]})
    (OUT/'合成预览').mkdir(exist_ok=True)
    (OUT/'完整原图').mkdir(exist_ok=True)
    merged.save(OUT/'合成预览'/f'{item}.png')
    original_merged.save(OUT/'完整原图'/f'{item}.png')
    model = {'parent':'minecraft:item/generated', 'textures':{l['layer']:f'hk3gtl:item/energy_fuel/{item}/{l["layer"]}' for l in layers}}
    model_path = OUT/'候选资源/assets/hk3gtl/models/item'/f'{item}.json'
    write_json(model_path, model)
    return {'id':'hk3gtl:'+item,'slug':slug,'name_zh':name+role,'form':form,
            'color':color,'status':'待贴图审批，未接正式资源，未注册新物品',
            'layers':layers,'model_relative':model_path.relative_to(OUT).as_posix(),
            'model_sha256':sha(model_path.read_bytes()),'preview':'合成预览/'+item+'.png',
            'original':'完整原图/'+item+'.png','source_pixels_redrawn':0}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')
    protected = {str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in ASSETS.rglob('*') if p.is_file()}
    with zipfile.ZipFile(JAR) as z:
        items = [save_item(z, slug, name, form, color, model)
                 for slug,name,color,model in FAMILIES for form in ('carrier','fuel','depleted')]
    assert len(items) == len({v['id'] for v in items}) == 39
    assert protected == {str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in ASSETS.rglob('*') if p.is_file()}
    manifest = {'created_at':now,'status':'候选待审，不是正式资源','item_count':39,
                'family_count':13,'existing_families_preserved':2,'items':items,
                'source_jar':str(JAR),'source_jar_sha256':sha(JAR.read_bytes()),
                'checks':{'all_source_layers_preserved':True,'all_alpha_identical':True,
                          'all_gt_overlays_original_bytes':True,'formal_assets_unchanged':True},
                '_record':f'【变更记录 #1】{now}：删除无；新增39项完整分层候选；修改原图色域不重画像素；用途为审批，未接正式。'}
    write_json(OUT/'39项候选与完整图层清单.json', manifest)
    cards = []
    for slug,name,color,_ in FAMILIES:
        row = [i for i in items if i['slug']==slug]
        cells = ''.join(f'<div class="pair"><b>{html.escape(i["name_zh"])}</b><div class="pixels"><figure><img src="{i["original"]}"><figcaption>完整原图</figcaption></figure><figure><img src="{i["preview"]}"><figcaption>候选</figcaption></figure></div><code>{i["id"]}</code><small>{len(i["layers"])}层 · 透明轮廓保留</small></div>' for i in row)
        cards.append(f'<article data-name="{name} {slug}" style="--family:{color}"><h2>{name}</h2><div class="family">{cells}</div></article>')
    page = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>能源燃料39项贴图候选</title><style>*{{box-sizing:border-box}}body{{margin:0;background:#edf3f2;color:#193943;font:16px/1.7 system-ui,"Microsoft YaHei",sans-serif}}main{{max-width:1460px;margin:auto;padding:34px 28px}}header{{padding:26px;background:#183e48;color:white;border-radius:12px}}h1{{margin:0;font-size:30px}}p{{max-width:1100px}}.note{{padding:18px 22px;border-left:5px solid #bb7a3e;background:#fff0e1;margin:20px 0}}article{{background:white;border:1px solid #c8d8dc;border-top:5px solid var(--family);margin:22px 0;padding:18px 22px;border-radius:9px}}h2{{margin:0 0 18px;font-size:23px}}.family{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px}}.pair{{min-width:0}}.pixels{{display:flex;gap:10px;margin:12px 0}}figure{{margin:0;text-align:center;flex:1}}img{{width:100%;max-width:160px;aspect-ratio:1;image-rendering:pixelated;padding:10px;background:repeating-conic-gradient(#293943 0% 25%,#31434d 0% 50%) 0/20px 20px;border-radius:5px}}figcaption,small{{font-size:13px;color:#557078}}code{{font-size:12px;overflow-wrap:anywhere;display:block}}small{{display:block}}a{{color:#126979}}header a{{color:#c4e4e5}}input{{width:100%;padding:14px;font-size:17px;border:1px solid #bbd0d4;border-radius:5px}}@media(max-width:850px){{.family{{grid-template-columns:1fr}}main{{padding:16px}}}}</style></head><body><main><header><h1>13条新燃料载体 · 39项贴图候选</h1><p>{now} · 等待贴图审批 · 正式资源未变</p><p>普通与浓缩燃料沿用现有资源。这一批展示新增13族的载体、燃料及乏料，名称、工艺与贴图审批分别记账。</p><p><a href="../../logs/energy-production-r172/燃料工艺与60工况候选_r172.html">查看燃料工艺与回收合同</a> · <a href="39项候选与完整图层清单.json">完整图层与来源</a></p></header><div class="note">每项左侧是完整原图，右侧是候选。GT载体取实际2.9的完整模型层栈，原色覆盖层保留；燃料棒只替换紫色活性区域，银灰外壳不重画。配色是待审方案，未注册新物品、未替换正式贴图、未更改反应堆结构。</div><input id="search" aria-label="筛选燃料族" placeholder="搜索：陶瓷、冷端、carbon、PTFE…">{''.join(cards)}<footer>【记录 #1】{now}：保留完整像素、透明轮廓及覆盖层；原图来源和SHA逐层记录。39项候选数量不等于39条已注册配方，更不代表能源系统已完成。</footer></main><script>document.querySelector('#search').addEventListener('input',e=>{{let q=e.target.value.toLowerCase();document.querySelectorAll('article').forEach(v=>v.hidden=!v.dataset.name.toLowerCase().includes(q));}});</script></body></html>'''
    (OUT/'39项燃料贴图对照.html').write_text(page, encoding='utf-8')
    sheet = Image.new('RGB', (960, 13*190+60), '#23333e')
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 18)
    for j, title in enumerate(['载体', '燃料', '乏料']):
        draw.text((j*320+100, 10), title, font=font, fill='white')
    for i, entry in enumerate(items):
        x, y = (i % 3)*320, (i//3)*190+52
        picture = Image.open(OUT/entry['preview']).convert('RGBA').resize((112,112), Image.Resampling.NEAREST)
        sheet.paste(picture, (x+100,y), picture)
        draw.text((x+12,y+120), entry['name_zh'], font=font, fill='#dce9ed')
    sheet.save(OUT/'39项候选联系表.png')
    archive = OUT.parent/(OUT.name+'.zip')
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for path in sorted(OUT.rglob('*')):
            if path.is_file(): z.write(path,path.relative_to(OUT))
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
    write_json(ROOT/'logs/energy-production-r172/贴图候选验证.json',
               {'created_at':now,'items':39,'textures':sum(len(v['layers']) for v in items),
                'zip':str(archive),'zip_sha256':sha(archive.read_bytes()),'source_formal_assets_sha256':protected,
                'checks':manifest['checks'],'not_verified':['用户贴图审批','游戏内渲染','注册与配方']})
    print(json.dumps({'out':str(OUT),'items':39,'textures':sum(len(v['layers']) for v in items)},ensure_ascii=False))


if __name__ == '__main__':
    main()
