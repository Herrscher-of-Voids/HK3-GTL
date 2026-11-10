# -*- coding: utf-8 -*-
"""保留指定舰体数据，为新版评审界面准备原版模型和稀疏表面。"""
from pathlib import Path
import argparse
import base64
import gzip
import hashlib
import io
import json
import shutil
import sys
import zipfile
import nbtlib
import numpy as np
from PIL import Image
from material_resources import Resources
from i37_surface_runs_20261027 import merge_surface_runs

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools'))
from hyperion_litematic_preflight import unpack_batches

OLD = ROOT/'doc/HK3GTL-内测5/03_机器结构/休伯利安_原投影预览_20260929'
SOURCE = ROOT/'deliveries/休伯利安_用户指定新舰体_20261001/休伯利安.litematic'
OUT = ROOT/'deliveries/休伯利安_1145格原稿_新版预览_20261108'
LOG = ROOT/'logs/hyperion-modern-preview-20261108'
INSTANCE = Path.home()/'AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版/minecraft'
EXPECTED = '2238856e3358f88802eb71f59a8d7765a50397fa6bf111d63e992bef2723b91c'


def read(p):
    return json.loads(p.read_text(encoding='utf-8'))


def save(p, data):
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def resources():
    r = Resources(instance=INSTANCE)
    entries = next(line.partition(':')[2] for line in (INSTANCE/'options.txt').read_text(encoding='utf-8').splitlines() if line.startswith('resourcePacks:'))
    packs = []
    for name in json.loads(entries):
        p = INSTANCE/'resourcepacks'/name[5:] if name.startswith('file/') else None
        if p and p.is_file():
            z = zipfile.ZipFile(p); r.archives.append((p, z)); packs.append(name)
            for key in z.namelist():
                if key.startswith('assets/'): r.index[key] = (p, z)
    return r, packs


def prepare():
    OUT.mkdir(exist_ok=True); LOG.mkdir(exist_ok=True)
    before = LOG/'immutable-inputs.json'
    if not before.exists():
        save(before, {str(p): digest(p) for p in [SOURCE, *sorted(OLD.rglob('*'))] if p.is_file()})
    assert digest(SOURCE) == EXPECTED == digest(OLD/'休伯利安.litematic')
    meta = read(OLD/'preview.json'); cells = np.fromfile(OLD/'cells.bin', '<u4'); states = np.fromfile(OLD/'states.bin', np.uint8)
    assert meta['size'] == [1145, 240, 549] and len(cells) == len(states) == 1469258
    assert np.all(cells[1:] > cells[:-1])
    source = nbtlib.load(SOURCE); region = next(iter(source['Regions'].values()))
    palette = region['BlockStatePalette']
    assert [{'name': str(s['Name']), 'properties': {str(k): str(v) for k,v in s.get('Properties',{}).items()}} for s in palette] == meta['palette']
    cursor = 0
    words = np.asarray(region['BlockStates'], np.int64).view(np.uint64)
    for start, values in unpack_batches(words, 1145*240*549, 7, 1000000):
        keep = np.flatnonzero(values); n = len(keep)
        assert np.array_equal(cells[cursor:cursor+n], keep+start)
        assert np.array_equal(states[cursor:cursor+n], values[keep])
        cursor += n
    assert cursor == len(cells)
    tiles = nbtlib.load(OLD/'tiles.nbt')['tiles']; original = region['TileEntities']
    assert len(tiles) == len(original) == 3402
    for tile, original_tile in zip(tiles, original):
        assert tile['nbt'].snbt() == original_tile.snbt()
        x,y,z = (int(original_tile[k]) for k in 'xyz')
        assert int(tile['index']) == (y*549+z)*1145+x
    for name in ['休伯利安.litematic', 'hyperion-full.nbt', 'preview.json', 'cells.bin', 'states.bin', 'tiles.nbt']:
        shutil.copy2(OLD/name, OUT/name)
    r,packs = resources(); models = {}; definitions = {}
    def model(name):
        if name in models: return models[name]
        ns,key = name.split(':',1) if ':' in name else ('minecraft',name)
        raw = json.loads(r.read(f'assets/{ns}/models/{key}.json'))
        parent = raw.get('parent','')
        base = model(parent) if parent and 'builtin/' not in parent else {}
        models[name] = {**base, **raw, 'textures': {**base.get('textures',{}), **raw.get('textures',{})}}
        return models[name]
    for state in meta['palette'][1:]:
        name = state['name']
        if name in definitions: continue
        ns,key = name.split(':',1)
        definition = json.loads(r.read(f'assets/{ns}/blockstates/{key}.json')); definitions[name] = definition
        variants = list(definition.get('variants',{}).values())+[p['apply'] for p in definition.get('multipart',[])]
        for group in variants:
            for variant in group if isinstance(group,list) else [group]: model(variant['model'])
    save(LOG/'model-inputs.json', dict(palette=meta['palette'], definitions=definitions, models=models))
    save(LOG/'source-verification.json', dict(passed=True, source_sha256=EXPECTED, all_non_air_cells_and_states_equal=True,
        source_block_entities_equal=True, blocks=cursor, block_entities=3402, palette_including_air=114,
        source_files_unchanged=True, enabled_resource_packs=packs))
    r.close()
    print(json.dumps(dict(stage='prepare', blocks=cursor, models=len(models)), ensure_ascii=False))


def texture(r, name):
    ns,key = name.split(':',1); rel = f'assets/{ns}/textures/{key}.png'
    image = Image.open(io.BytesIO(r.read(rel))).convert('RGBA')
    try: animation = json.loads(r.read(rel+'.mcmeta')).get('animation')
    except FileNotFoundError: animation = None
    if animation is not None:
        w = animation.get('width', image.width if 'height' in animation else min(image.size))
        h = animation.get('height', image.height if 'width' in animation else min(image.size))
        frame = animation.get('frames',[0])[0]; frame = frame.get('index',0) if isinstance(frame,dict) else frame
        x,y = frame%(image.width//w)*w,frame//(image.width//w)*h
        image = image.crop((x,y,x+w,y+h))
    target = io.BytesIO(); image.save(target,format='PNG')
    return dict(url='data:image/png;base64,'+base64.b64encode(target.getvalue()).decode(), alpha=image.getchannel('A').getextrema()[0]<255)


def finish():
    meta = read(OUT/'preview.json'); templates = read(LOG/'model-templates.json')
    cells = np.fromfile(OUT/'cells.bin','<u4').astype(np.int64); states = np.fromfile(OUT/'states.bin',np.uint8)
    w,h,d = meta['size']; y = cells//(w*d); z = cells//w%d; x = cells%w
    r,packs = resources()
    textures = {name: texture(r,name) for name in sorted({q['texture'] for t in templates[1:] for q in t['quads']})}
    groups = [[[] for _ in range(6)] for _ in templates[1:]]
    opaque = np.array([bool(t.get('cube')) and 'glass' not in t.get('name','') for t in templates])
    for face,(stride,edge) in enumerate([(1,x==w-1),(-1,x==0),(w,z==d-1),(-w,z==0),(-w*d,y==0),(w*d,y==h-1)]):
        target = cells+stride; at = np.searchsorted(cells,target); safe = np.minimum(at,len(cells)-1)
        occupied = (~edge)&(at<len(cells))&(cells[safe]==target)
        hidden = occupied & (opaque[states[safe]] | ((states[safe]==states)&np.array(['glass' in t.get('name','') for t in templates])[states]))
        for state in range(1,len(templates)):
            if templates[state]['cube']: groups[state-1][face] = cells[(states==state)&~hidden].tolist()
    merged,lengths,merge_check = merge_surface_runs(groups,meta['size'])
    data = []
    for i,t in enumerate(templates[1:],1):
        indices = cells[states==i]; assert len(indices)>0 and t['quads'], t['state']
        bounds = [np.stack((indices%w,indices//(w*d),indices//w%d),axis=1).min(axis=0).tolist(),
                  np.stack((indices%w,indices//(w*d),indices//w%d),axis=1).max(axis=0).tolist()]
        data.append(dict(t,count=len(indices),indices=[] if t['cube'] else indices.tolist(),
            groups=merged[i-1],runs=lengths[i-1],layer_counts=np.bincount(y[states==i],minlength=h).tolist(),cell_bounds=bounds))
    lang = {}
    assets = INSTANCE.parents[2]/'assets'
    for index in sorted((assets/'indexes').glob('*.json')):
        entry = read(index).get('objects',{}).get('minecraft/lang/zh_cn.json')
        if entry:
            file = assets/'objects'/entry['hash'][:2]/entry['hash']
            if file.is_file():
                lang = read(file); r.sources['原版中文语言'] = str(file); break
    assert lang, '未找到原版中文语言资产，不采用资源包的不完整界面语言覆盖'
    for s in data: s['label'] = lang.get(s['name'].replace('minecraft:','block.minecraft.'),s['name'])
    sources = dict(r.sources); r.close()
    verification = dict(read(LOG/'source-verification.json'), source_instance=str(INSTANCE), instance_version='3.0',
        materials=len(data), blocks=sum(s['count'] for s in data), size_xyz=meta['size'], resource_sources=sources,
        resource_file_sha256={p:digest(Path(p)) for p in sorted({s.split('!/',1)[0] for s in sources.values()})},
        surface_merge=merge_check, non_cube_states=sum(not s['cube'] for s in data),
        non_cube_blocks=sum(s['count'] for s in data if not s['cube']), source_models_used=True,
        model_notes=['使用目标实例原版模型和启用资源包的静态首帧；状态旋转及非完整方块保留。',
                     '单块告示牌保留板体模型；文字随原始方块实体文件保留，未绘制为世界文字。',
                     '材质筛选及剖切仅隐藏现有表面，不补画切口。原稿没有已定主控或接口，不自动识别钻石块。'],
        approved=False,installed=False,game_verified=False)
    assert verification['blocks']==1469258
    for path,old_hash in read(LOG/'immutable-inputs.json').items(): assert digest(Path(path))==old_hash,path
    payload = dict(title='仿制 · 休伯利安｜1145格原稿',size=meta['size'],blocks=meta['blocks'],states=data,textures=textures,
                   author=meta['author_from_file'],block_entities=3402,audit=verification)
    encoded = base64.b64encode(gzip.compress(json.dumps(payload,ensure_ascii=False,separators=(',',':')).encode(),6)).decode()
    (OUT/'data.js').write_text('window.HYPERION_PAYLOAD='+json.dumps(encoded)+';',encoding='utf-8')
    save(OUT/'verification.json',verification)
    save(OUT/'材料清单.json',[dict(state=s['state'],count=s['count'],name=s['label']) for s in data])
    save(OUT/'manifest.json',dict(title=payload['title'],size_xyz=meta['size'],blocks=1469258,materials=len(data),block_entities=3402,
        source_sha256=EXPECTED,preview='三维评审.html',preview_updated_at='2026-11-08',approved=False,installed=False,game_verified=False))
    print(json.dumps(dict(stage='finish',blocks=verification['blocks'],materials=len(data),non_cube_blocks=verification['non_cube_blocks'],merged_quads=merge_check['rendered_quads']),ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('stage',choices=['prepare','finish']); args=parser.parse_args()
    prepare() if args.stage=='prepare' else finish()
