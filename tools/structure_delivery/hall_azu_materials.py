"""按真实 blockstate/model 分类礼堂材料；视觉形体不等同碰撞或遮光。"""
from __future__ import annotations

import io
import itertools
import json
import math
import zipfile
from pathlib import Path

from PIL import Image

from material_resources import Resources

ROOT = Path(__file__).resolve().parents[2]
INSTANCE = Path('C:/Users/OWNER/AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版/minecraft')
PRISM = INSTANCE.parents[2]
CLIENT = PRISM / 'libraries/com/mojang/minecraft/1.20.1/minecraft-1.20.1-client.jar'
SOURCES = Path.home() / '.gradle/caches/forge_gradle/minecraft_user_repo/net/minecraftforge/forge/1.20.1-47.4.16_mapped_official_1.20.1/forge-1.20.1-47.4.16_mapped_official_1.20.1-sources.jar'
OUT = ROOT / 'output/hall-azu-analysis'
AIR = {'minecraft:air', 'minecraft:cave_air', 'minecraft:void_air'}
FLUIDS = {'minecraft:water', 'minecraft:lava'}
FACES = {'east', 'west', 'up', 'down', 'south', 'north'}


def split_state(state):
    name, _, tail = state.partition('[')
    return name, dict(p.split('=', 1) for p in tail.rstrip(']').split(',') if '=' in p)


def condition_matches(condition, props):
    if not condition:
        return True
    if 'OR' in condition:
        return any(condition_matches(c, props) for c in condition['OR'])
    if 'AND' in condition:
        return all(condition_matches(c, props) for c in condition['AND'])
    return all(props.get(k) in str(v).split('|') for k, v in condition.items())


def model_sets(blockstate, props):
    """返回随机模型的每种可能组合；multipart各命中项必须同时考虑。"""
    if 'variants' in blockstate:
        matches = [value for key, value in blockstate['variants'].items()
                   if condition_matches(dict(p.split('=', 1) for p in key.split(',') if '=' in p), props)]
        if len(matches) != 1:
            raise ValueError(f'实际属性不能唯一匹配 variants：{len(matches)}项')
        return [[v] for v in (matches[0] if isinstance(matches[0], list) else [matches[0]])]
    if 'multipart' in blockstate:
        parts = [p['apply'] if isinstance(p['apply'], list) else [p['apply']]
                 for p in blockstate['multipart'] if condition_matches(p.get('when'), props)]
        if not parts:
            raise ValueError('multipart没有命中的实际部件')
        count = math.prod(len(p) for p in parts)
        if count > 512:
            raise ValueError(f'随机multipart组合过多，未穷举：{count}')
        return list(itertools.product(*parts))
    raise ValueError('没有静态variants或multipart')


def rotate_point(point, axis, angle, origin=(8, 8, 8), rescale=False):
    a, b = {'x': (1, 2), 'y': (2, 0), 'z': (0, 1)}[axis]
    p = [point[i] - origin[i] for i in range(3)]
    c, s = math.cos(math.radians(angle)), math.sin(math.radians(angle))
    p[a], p[b] = c * p[a] - s * p[b], s * p[a] + c * p[b]
    if rescale and angle:
        scale = 1 / abs(c)
        p[a] *= scale
        p[b] *= scale
    return tuple(round(p[i] + origin[i], 7) for i in range(3))


def boxes_cover_cube(boxes):
    """坐标分割精确检查轴对齐元素并集，不用碰撞箱或近似体素。"""
    if any(any(low[i] < 0 or high[i] > 16 for i in range(3)) for low, high in boxes):
        return False
    cuts = [sorted({0., 16., *(v[i] for box in boxes for v in box)}) for i in range(3)]
    for xyz in itertools.product(*(list(zip(c, c[1:])) for c in cuts)):
        point = [(a + b) / 2 for a, b in xyz]
        if not any(all(low[i] <= point[i] <= high[i] for i in range(3)) for low, high in boxes):
            return False
    return True


def geometry(variants, resources):
    boxes, model_details, textures = [], [], set()
    nonorthogonal = False
    partial_faces = False
    builtin = False
    for variant in variants:
        ref = variant['model']
        model = resources.model(ref)
        elements = model.get('elements', [])
        builtin |= model.get('parent', '').startswith('builtin/')
        model_details.append({'model': ref, 'x': variant.get('x', 0), 'y': variant.get('y', 0),
                              'elements': len(elements), 'source': resources.sources['assets/' + ref.replace(':', '/models/') + '.json']})
        for element in elements:
            corners = list(itertools.product(*zip(element['from'], element['to'])))
            rotation = element.get('rotation')
            if rotation:
                nonorthogonal |= rotation['angle'] % 90 != 0
                corners = [rotate_point(p, rotation['axis'], rotation['angle'], rotation.get('origin', [8, 8, 8]), rotation.get('rescale', False)) for p in corners]
            for axis in ('x', 'y'):
                if variant.get(axis):
                    corners = [rotate_point(p, axis, variant[axis]) for p in corners]
            low = tuple(min(p[i] for p in corners) for i in range(3))
            high = tuple(max(p[i] for p in corners) for i in range(3))
            boxes.append((low, high))
            partial_faces |= set(element.get('faces', {})) != FACES
            for face in element.get('faces', {}).values():
                texture = face.get('texture', '')
                seen = set()
                while texture.startswith('#'):
                    if texture in seen:
                        raise ValueError('纹理引用循环')
                    seen.add(texture)
                    texture = model.get('textures', {})[texture[1:]]
                if texture:
                    textures.add(texture)
    if not boxes:
        return None, '模型没有静态元素，可能由内置或方块实体渲染；未据名称猜形体', model_details, textures
    bounds = [[min(b[0][i] for b in boxes) for i in range(3)], [max(b[1][i] for b in boxes) for i in range(3)]]
    if bounds != [[0., 0., 0.], [16., 16., 16.]]:
        return False, '真实模型几何边界不是完整16×16×16：' + str(bounds), model_details, textures
    if nonorthogonal:
        return None, '含非直角旋转元素，未用轴对齐包围盒冒充完整实体', model_details, textures
    complete = boxes_cover_cube(boxes)
    if complete and (partial_faces or builtin):
        return None, '元素体积覆盖完整立方体，但有缺面或内置渲染；外表完整性待单独核验', model_details, textures
    return complete, '模型全部元素并集' + ('恰好覆盖完整16³立方体，六面齐全' if complete else '未填满16³立方体'), model_details, textures


def language(resources):
    translations, evidence = {}, []
    try:
        path = 'assets/minecraft/lang/zh_cn.json'
        translations.update(json.loads(resources.read(path)))
        evidence.append(resources.sources[path])
    except FileNotFoundError:
        pass
    # 1.20.1使用的asset index 5；其他版本语言不替代目标实例。
    index = PRISM / 'assets/indexes/5.json'
    if index.is_file():
        obj = json.loads(index.read_text(encoding='utf-8'))['objects'].get('minecraft/lang/zh_cn.json')
        if obj:
            hashed = PRISM / 'assets/objects' / obj['hash'][:2] / obj['hash']
            if hashed.is_file():
                translations.update(json.loads(hashed.read_text(encoding='utf-8')))
                evidence.append(str(hashed))
    return translations, evidence


def builtin_evidence(block):
    """只为已查到真实客户端实现的具体ID补核，不按名字后缀猜形体。"""
    if not SOURCES.is_file():
        return None
    with zipfile.ZipFile(SOURCES) as archive:
        if block in {'minecraft:birch_sign', 'minecraft:birch_wall_sign'}:
            path = 'net/minecraft/client/renderer/blockentity/SignRenderer.java'
            source = archive.read(path).decode('utf-8')
            registry = archive.read('net/minecraft/world/level/block/Blocks.java').decode('utf-8')
            name = block.split(':')[1]
            cls = 'StandingSignBlock' if name == 'birch_sign' else 'WallSignBlock'
            assert f'register("{name}", new {cls}(' in registry
            assert 'addBox(-12.0F, -14.0F, -1.0F, 24.0F, 12.0F, 2.0F)' in source
            assert 'addBox(-1.0F, -2.0F, -1.0F, 2.0F, 14.0F, 2.0F)' in source
            assert 'return 0.6666667F;' in source and '.scale(f, -f, -f);' in source
            return dict(full_visual_cube=False, category='非完整方块（方块实体告示牌）',
                        reason='真实SignRenderer：牌面24×12×2模型单位，缩放2/3后为16×8×4/3；立式另有2×14×2支杆，墙牌隐藏支杆；均非完整16³立方体',
                        models=[{'model': 'SignRenderer.createSignLayer / SignModel', 'source': str(SOURCES) + '!/' + path,
                                 'lines': '60–70,86–101,195–200'}],
                        sources=[str(SOURCES) + '!/' + path, str(SOURCES) + '!/net/minecraft/world/level/block/Blocks.java'])
        if block == 'minecraft:light':
            path = 'net/minecraft/world/level/block/LightBlock.java'
            source = archive.read(path).decode('utf-8')
            assert 'return RenderShape.INVISIBLE;' in source
            return dict(full_visual_cube=False, category='特殊无形光源',
                        reason='真实LightBlock.getRenderShape返回INVISIBLE；游戏世界中没有可见建筑实体，不能按物品图标计为完整立方体',
                        models=[{'model': 'LightBlock.getRenderShape', 'source': str(SOURCES) + '!/' + path, 'lines': '62–64'}],
                        sources=[str(SOURCES) + '!/' + path])
    return None


def build_materials(palette: list[str]) -> list[dict]:
    assert INSTANCE.is_dir() and CLIENT.is_file(), '目标增强版实例或1.20.1真实client资源缺失'
    resources = Resources(instance=INSTANCE, client=CLIENT)
    zh, lang_sources = language(resources)
    results = []
    try:
        for state in palette:
            block, props = split_state(state)
            ns, key = block.split(':', 1)
            item = dict(state=state, block=block, properties=props,
                        zh_name=zh.get(f'block.{ns}.{key}', '中文名未核实'),
                        full_visual_cube=None, category='未核实', reason='', models=[], sources=[],
                        texture_has_alpha=None, transparent=None, alpha_mode='未核实', language_sources=lang_sources,
                        resource_version='目标增强版Minecraft 1.20.1真实资源；原世界1.20.4兼容另验',
                        collision_or_occlusion_verified=False)
            if block in AIR:
                item.update(full_visual_cube=False, category='空气', reason='空气不是建筑实体，不计完整或非完整建筑材料')
            elif block in FLUIDS:
                item.update(category='特殊流体', reason='流体由相邻状态决定液面与侧面，非静态建筑模型；不并入完整实体立方体')
            else:
                try:
                    path = f'assets/{ns}/blockstates/{key}.json'
                    bs = json.loads(resources.read(path))
                    sets = model_sets(bs, props)
                    outcomes = [geometry(v, resources) for v in sets]
                    flags = {result[0] for result in outcomes}
                    complete = flags.pop() if len(flags) == 1 else None
                    reasons = list(dict.fromkeys(result[1] for result in outcomes))
                    if len(outcomes) > 1:
                        reasons.insert(0, f'核验全部{len(outcomes)}种随机/部件组合')
                    textures = set().union(*(result[3] for result in outcomes))
                    alphas, alpha_modes, texture_sources = [], [], []
                    for ref in sorted(textures):
                        tns, tkey = ref.split(':', 1) if ':' in ref else ('minecraft', ref)
                        texpath = f'assets/{tns}/textures/{tkey}.png'
                        picture = Image.open(io.BytesIO(resources.read(texpath))).convert('RGBA')
                        alphas.append(picture.getchannel('A').getextrema()[0] < 255)
                        histogram = picture.getchannel('A').histogram()
                        alpha_modes.append('半透明' if any(histogram[1:255]) else '镂空' if histogram[0] else '不透明')
                        texture_sources.append(resources.sources[texpath])
                    alpha = any(alphas) if alphas else None
                    category = ('完整立方体（透明或镂空贴图）' if alpha else '完整立方体') if complete is True else '非完整方块' if complete is False else '未核实特殊形体'
                    if complete is True and props.get('type') == 'double':
                        category = '完整立方体（双层台阶状态）'
                    if props.get('waterlogged') == 'true':
                        reasons.append('含水状态的流体效果另计；本项按建筑固体模型分类')
                    item.update(full_visual_cube=complete, category=category,
                                reason='；'.join(reasons), texture_has_alpha=alpha, transparent=alpha,
                                alpha_mode='、'.join(sorted(set(alpha_modes))) or '未核实',
                                models=[d for result in outcomes for d in result[2]],
                                sources=sorted(set([resources.sources[path], *texture_sources, *(d['source'] for result in outcomes for d in result[2])])))
                except (FileNotFoundError, ValueError, KeyError, TypeError) as e:
                    item.update(reason='真实资源未完整核实：' + str(e))
                if item['full_visual_cube'] is None:
                    proof = builtin_evidence(block)
                    if proof:
                        item.update(proof)
            results.append(item)
    finally:
        resources.close()
    return results


if __name__ == '__main__':
    raw = json.loads((OUT / 'palette.json').read_text(encoding='utf-8'))
    palette = raw.get('palette', raw.get('states')) if isinstance(raw, dict) else raw
    if palette and isinstance(palette[0], dict):
        palette = [r['state'] for r in palette]
    classified = build_materials(palette)
    (OUT / 'classification.json').write_text(json.dumps(classified, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'states': len(classified), 'full': sum(r['full_visual_cube'] is True for r in classified),
                      'nonfull': sum(r['full_visual_cube'] is False for r in classified),
                      'unverified_or_special': sum(r['full_visual_cube'] is None for r in classified)}, ensure_ascii=False))
