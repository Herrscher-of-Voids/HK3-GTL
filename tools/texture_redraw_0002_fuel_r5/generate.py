import colorsys
import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw

from bundles import bundle


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/0002贴图材质_燃料棒_R5_20261114'
ASSETS = ROOT / 'src/main/resources/assets/hk3gtl'
LOG = ROOT / 'logs/textures-fuel-0002-r5-20261114'
MOTHER = OUT / 'references/honkai_fuel_rod_original.png'
CHAT = '01a1d68a-a994-7ac0-a48a-54c0f98fd54e'


def recolor(color):
    im = Image.open(MOTHER).convert('RGBA')
    target = tuple(int(color[n:n + 2], 16) / 255 for n in (1, 3, 5))
    for y in range(10, 54):
        for x in range(27, 37):
            r, g, b, a = im.getpixel((x, y))
            if a and g > r + 15 and b > r + 15:
                brightness = max(r, g, b) / 208
                rgb = tuple(min(255, round(c * brightness * 255)) for c in target)
                im.putpixel((x, y), rgb + (a,))
    return im


def depleted(active):
    im = active.copy()
    source = Image.open(MOTHER).convert('RGBA')
    for y in range(10, 54):
        for x in range(27, 37):
            r, g, b, a = source.getpixel((x, y))
            if a and g > r + 15 and b > r + 15:
                rgb = im.getpixel((x, y))[:3]
                h, s, v = colorsys.rgb_to_hsv(*(c / 255 for c in rgb))
                muted = colorsys.hsv_to_rgb(h, s * .42, v * .39 + .10)
                im.putpixel((x, y), tuple(round(c * 255) for c in muted) + (a,))
    return im


def broken(spent):
    im = Image.new('RGBA', (64, 64))
    im.alpha_composite(spent.crop((0, 0, 64, 31)), (0, 0))
    im.alpha_composite(spent.crop((0, 33, 63, 62)), (1, 34))
    d = ImageDraw.Draw(im)
    d.line([(27, 30), (29, 31), (31, 30), (34, 31), (36, 30)], fill='#b3bab6')
    d.line([(29, 34), (31, 33), (34, 35), (36, 34)], fill='#646d6a')
    d.line((30, 32, 31, 34), fill='#323638')
    d.line((34, 31, 34, 33), fill='#888c86')
    return im


def rejected():
    source = recolor('#9D8954')
    im = source.copy()
    ImageDraw.Draw(im).rectangle((26, 3, 39, 10), fill=(0, 0, 0, 0))
    im.alpha_composite(source.crop((27, 4, 37, 10)), (29, 4))
    d = ImageDraw.Draw(im)
    d.rectangle((27, 22, 36, 25), fill='#c3a246')
    d.line((27, 24, 29, 22), fill='#303434', width=2)
    d.line((32, 25, 35, 22), fill='#303434', width=2)
    d.line((34, 37, 32, 41, 34, 44), fill='#242c2a')
    return im


def generate():
    inventory = json.loads((LOG / 'inventory.json').read_text(encoding='utf-8'))
    items, families = [], []
    for family in inventory['families']:
        families.append({k: family[k] for k in ('id', 'name', 'color')})
        if family['id'] == 'honkai_fuel_rod':
            families[-1]['color'] = '#06CCB3'
        active = Image.open(MOTHER).convert('RGBA') if family['id'] == 'honkai_fuel_rod' else recolor(family['color'])
        spent = depleted(active)
        images = {'active': active, 'depleted': spent, 'broken': broken(spent)}
        for state in family['states']:
            ident, status = state['id'], state['state']
            model_path = ROOT / state['model_path']
            model = json.loads(model_path.read_text(encoding='utf-8'))
            new_texture = 'hk3gtl:item/' + ident
            current = model.setdefault('textures', {})
            changed = current.get('layer0') != new_texture
            current['layer0'] = new_texture
            if changed:
                model_path.write_text(json.dumps(model, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            for count in (1, 4, 8, 16):
                suffix = '' if count == 1 else f'_{count}x'
                local = f'item/{ident}.png' if count == 1 else f'item/fuel_bundles/{ident}{suffix}.png'
                source_path, copy_path = ASSETS / 'textures' / local, OUT / 'textures' / local
                source_path.parent.mkdir(parents=True, exist_ok=True)
                copy_path.parent.mkdir(parents=True, exist_ok=True)
                im = images[status] if count == 1 else bundle(images[status], count)
                if ident == 'honkai_fuel_rod' and count == 1:
                    shutil.copyfile(MOTHER, source_path)
                else:
                    im.save(source_path, optimize=True)
                shutil.copyfile(source_path, copy_path)
                item_id = ident + suffix
                item_model_path = ASSETS / f'models/item/{item_id}.json'
                if count > 1:
                    item_model = json.loads(item_model_path.read_text(encoding='utf-8'))
                    item_model.setdefault('textures', {})['layer0'] = 'hk3gtl:' + local[:-4]
                    item_model_path.write_text(json.dumps(item_model, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
                items.append({'id': ident + suffix, 'family_id': family['id'],
                              'name': state['name'] if count == 1 else f'{count}连{state["name"]}',
                              'state': status, 'rods': count, 'existing_item': True,
                              'existing_model_path': item_model_path.relative_to(ROOT).as_posix(),
                              'image': copy_path.relative_to(OUT).as_posix(),
                              'source_path': source_path.relative_to(ROOT).as_posix(),
                              'texture': 'hk3gtl:' + local[:-4],
                              'sha256': hashlib.sha256(source_path.read_bytes()).hexdigest()})
    ident = inventory['rejected']['id']
    p = ASSETS / f'textures/item/{ident}.png'
    rejected().save(p, optimize=True)
    shutil.copyfile(p, OUT / f'textures/item/{ident}.png')
    items.append({'id': ident, 'family_id': ident, 'name': inventory['rejected']['name'],
                  'state': 'rejected', 'rods': 1, 'existing_item': True,
                  'existing_model_path': inventory['rejected']['model_path'],
                  'image': f'textures/item/{ident}.png', 'source_path': p.relative_to(ROOT).as_posix(),
                  'texture': f'hk3gtl:item/{ident}', 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()})
    manifest = {'revision': 'R5', 'date': '2026-11-14', 'conversation_number': '0002', 'conversation_id': CHAT,
                'native_size': [64, 64], 'mode': 'RGBA', 'art_approved': False,
                'reference': 'references/honkai_fuel_rod_original.png',
                'reference_sha256': hashlib.sha256(MOTHER.read_bytes()).hexdigest(),
                'reference_source': 'R2历史JAR仅提取普通棒PNG，未复用旧代码或旧JAR交付。',
                'reference_policy': '负责人截图指定普通青白细棒；普通棒原样恢复，其余仅换芯色与状态，金属端盖和细长轮廓沿用母图。',
                'bundle_design': '4连2×2、8连4×2、16连4×4错层，可见独立端帽和窄金属绑箍；不使用数字代替棒体。',
                'existing_single_textures': 46, 'new_bundle_textures': 135, 'image_count': len(items),
                'existing_model_texture_overrides': 39, 'new_items_registered': False,
                'bundle_items_registered_by': '0003', 'bundle_model_texture_links': 135,
                'new_models_registered': False, 'recipe_changed': False, 'jar_built': False,
                'installed': False, 'game_tested': False,
                'handoff': '0003已注册135个组合物品及独立模型；0002保留模型继承，补layer0到item/fuel_bundles下的对应PNG。未改注册或配方。',
                'out_of_scope': ['29张energy_fuel载体分层图与39个载体前置物品', '5项燃料工艺中间品重绘', '66张已认可贴图与神之键R6候选'],
                'families': families, 'items': items}
    (OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return {'single': 46, 'bundles': 135, 'images': len(items), 'model_texture_overrides': 39}


if __name__ == '__main__':
    print(json.dumps(generate(), ensure_ascii=False))
