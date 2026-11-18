# -*- coding: utf-8 -*-
"""从九台现行完整蓝图生成64像素三态控制器面板。"""
from pathlib import Path
import gzip
import hashlib
import html
import json
import shutil
import struct

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import build_controller_texture_candidates_20261026 as faces

ROOT = Path(__file__).resolve().parents[2]
LOG = ROOT / 'logs/controller-front-redraw-0002-r7-20261114'
OUT = ROOT / 'deliveries/0002贴图材质_控制器整机图_R7_20261114'
OVERLAYS = ROOT / 'src/main/resources/assets/hk3gtl/textures/block/overlay'
DATA = ROOT / 'src/main/resources/data/hk3gtl'
SOURCES = {
    'I01': ('i01', DATA / 'approved_architecture/i01.json', '现行一阶采集塔完整蓝图'),
    'I02': ('i02', DATA / 'approved_architecture/i02.json', '现行光谱阵列完整蓝图'),
    'I03': ('i03', DATA / 'approved_architecture/i03.json', '现行离心分离中心完整蓝图'),
    'S01': ('s01', DATA / 'approved_architecture/s01.json', '现行一阶研究所完整蓝图'),
    'W01': ('w01', DATA / 'structures/w01_hall.bin.gz', '现行干燥修订完整礼堂'),
    'W02': ('w02', DATA / 'structures/w02_19c_a2.bin.gz', '19C自律构造船坞完整组合A2；外观待批准'),
    'W03': ('w03', DATA / 'structures/w03_c9.bin.gz', '已批准C9完整建筑；静态蓝图轮廓'),
    'W04': ('w04', DATA / 'structures/w04_candidate.bin.gz', '已批准七雷取能天枢A3完整建筑'),
    'AUX-NETWORK': ('network_injector', ROOT / 'logs/network-injector-rebuild-20261111/blueprint.json', '网络注入器自身三段谐振结构；不绘旧固定接口'),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def binary_points(path):
    with gzip.open(path, 'rb') as stream:
        magic, version, w, h, d, cx, cy, cz, count, palettes = struct.unpack('>9iH', stream.read(38))
        for _ in range(palettes):
            stream.read(struct.unpack('>H', stream.read(2))[0])
        raw = stream.read()
    if version == 1:
        positions = np.frombuffer(raw, dtype='>u8') >> 16
        points = np.column_stack((positions >> 20, (positions >> 10) & 1023, positions & 1023)).astype(np.int16)
    else:
        runs = np.frombuffer(raw, dtype=[('start', '>i4'), ('step', '>i4'), ('length', '>i4'), ('state', '>u2'), ('extra', '>i4')])
        lengths = runs['length'].astype(np.int64)
        offsets = np.arange(count, dtype=np.int64) - np.repeat(np.cumsum(lengths) - lengths, lengths)
        indices = np.repeat(runs['start'], lengths) + offsets * np.repeat(runs['step'], lengths)
        points = np.column_stack((indices // (h * d), (indices // d) % h, indices % d)).astype(np.int16)
    return points, [cx, cy, cz], [w, h, d]


def load_points(path):
    if path.name.endswith('.bin.gz'):
        return binary_points(path)
    layout = json.loads(path.read_text('utf-8'))
    return np.asarray([b['pos'] for b in layout['blocks']], dtype=np.int16), layout['controller'], layout['size']


def small_geometry_image(points, path):
    image = Image.new('RGB', (600, 420), '#091421')
    draw = ImageDraw.Draw(image)
    uv = faces.projection(points)
    corners = faces.projection(np.asarray([[0, 0, 0], [1, 0, 0], [0, 0, 1], [1, 0, 1],
                                          [0, 1, 0], [1, 1, 0], [0, 1, 1], [1, 1, 1]]))[:, :2]
    low = uv[:, :2].min(axis=0) + corners.min(axis=0)
    extent = uv[:, :2].max(axis=0) + corners.max(axis=0) - low
    scale = min(570 / extent[0], 390 / extent[1])
    offset = (np.asarray([600, 420]) - extent * scale) / 2
    polygons = [([2, 3, 7, 6], '#305469'), ([1, 3, 7, 5], '#397184'), ([4, 5, 7, 6], '#6095a6')]
    for index in np.argsort(uv[:, 2]):
        vertices = ((uv[index, :2] + corners - low) * scale + offset).tolist()
        for indices, color in polygons:
            draw.polygon([tuple(vertices[i]) for i in indices], fill=color)
    image.save(path)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    baseline = json.loads((LOG / 'baseline.json').read_text('utf-8'))
    registry = {c['role']: c for c in baseline['selected']}
    projection = faces.projected_geometry
    entries = []
    for role, (key, source, note) in SOURCES.items():
        current = registry[role]
        folder = OUT / key
        folder.mkdir(exist_ok=True)
        target = OVERLAYS / (key + '_appearance_0002_r7')
        target.mkdir(exist_ok=True)
        points, controller, size = load_points(source)
        if role in ('I01', 'I02', 'I03', 'S01', 'AUX-NETWORK'):
            small_geometry_image(points, folder / 'whole-machine.png')
        else:
            faces.geometry_image(points, folder / 'whole-machine.png')
        projected = projection(points, 44, 37)
        faces.projected_geometry = lambda value, width, height, margin=1: projected
        textures, previous = {}, {}
        for state, suffix in faces.STATE_SUFFIX.items():
            old = ROOT / current['renderer']['state_png_paths']['overlay_front' + suffix]
            shutil.copy2(old, folder / ('before' + suffix + '.png'))
            previous[state] = {'path': (key + '/before' + suffix + '.png'), 'sha256': sha(old), 'source': old.relative_to(ROOT).as_posix()}
            picture, pattern = faces.candidate_face(points, [], controller, state)
            destination = target / ('overlay_front' + suffix + '.png')
            picture.save(destination)
            shutil.copy2(destination, folder / destination.name)
            textures[state] = {'path': key + '/' + destination.name, 'resource': destination.relative_to(ROOT).as_posix(), 'sha256': sha(destination)}
        faces.projected_geometry = projection
        entries.append({'role': role, 'key': key, 'machine': current['id'], 'name': current['name_zh'],
                        'source': source.relative_to(ROOT).as_posix(), 'source_sha256': sha(source), 'source_status': note,
                        'size_xyz': size, 'blocks': len(points), 'controller_xyz': controller, 'ports_drawn': [],
                        'overlay': 'hk3gtl:block/overlay/' + target.name, 'geometry': key + '/whole-machine.png',
                        'geometry_pattern_sha256': pattern, 'textures': textures, 'previous': previous})
        print(json.dumps({'role': role, 'blocks': len(points), 'size_xyz': size, 'states': 3}), flush=True)
        del points
    manifest = {'date': '2026-11-14', 'thread': '0002贴图材质', 'thread_id': '01a1d68a-a994-7ac0-a48a-54c0f98fd54e',
                'method': '完整现行结构坐标直接生成原生64×64轮廓与深度棱线投影；复用现有金属面板及三态显示，不裁掉整机，不复用工艺符号。',
                'entries': entries, 'source_resource_changes': 27, 'art_status': '待负责人评审', 'game_verified': False,
                'held': 'W05–W15、H01和I37本轮保持；其他已采用控制器保持。'}
    (OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    draw_sheet(entries)
    write_html(manifest)


def draw_sheet(entries):
    sheet = Image.new('RGB', (1530, 1280), '#121d28')
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 20)
    small = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 16)
    draw.text((20, 12), '0002 · 九台控制器整机图 R7 · 空闲／运行／暂停', font=font, fill='#e6eef4')
    for i, entry in enumerate(entries):
        x = 15 + (i % 3) * 505
        y = 58 + (i // 3) * 404
        draw.rectangle((x, y, x + 490, y + 389), fill='#20303e', outline='#3a4f60')
        draw.text((x + 12, y + 9), entry['role'] + ' · ' + entry['name'], font=small, fill='#e6eef4')
        for j, state in enumerate(faces.STATE_SUFFIX):
            image = Image.open(OUT / entry['textures'][state]['path'])
            sheet.paste(image.resize((144, 144), Image.Resampling.NEAREST), (x + 13 + j * 158, y + 48))
            draw.text((x + 64 + j * 158, y + 199), faces.STATE_CN[state], font=small, fill='#a7c7d5')
        image = Image.open(OUT / entry['geometry']).resize((225, 158))
        sheet.paste(image, (x + 13, y + 228))
        draw.text((x + 250, y + 238), '对应完整结构', font=small, fill='#a7c7d5')
        draw.text((x + 250, y + 269), '×'.join(map(str, entry['size_xyz'])), font=small, fill='#a7c7d5')
        draw.text((x + 250, y + 300), format(entry['blocks'], ',') + ' 方块', font=small, fill='#a7c7d5')
        draw.text((x + 250, y + 339), '原生64×64 · 待评审', font=small, fill='#e7c583')
    sheet.save(OUT / 'overview.png')


def write_html(manifest):
    cards = []
    for e in manifest['entries']:
        pairs = '<figure><img src="' + e['previous']['idle']['path'] + '"><figcaption>原空闲图</figcaption></figure>'
        for state, suffix in faces.STATE_SUFFIX.items():
            pairs += '<figure><img src="' + e['textures'][state]['path'] + '"><figcaption>' + faces.STATE_CN[state] + '</figcaption></figure>'
        cards.append('<article><h2>' + html.escape(e['role'] + ' · ' + e['name']) + '</h2><p>' + html.escape(e['source_status']) + '</p><img class="geometry" src="' + e['geometry'] + '"><div class="states">' + pairs + '</div><small>' + ' × '.join(map(str, e['size_xyz'])) + '（X/Y/Z） · ' + format(e['blocks'], ',') + '方块<br>' + html.escape(e['source']) + '<br>' + html.escape(e['overlay']) + '</small></article>')
    page = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>0002控制器整机图R7</title><style>body{margin:0;background:#101923;color:#e6eef4;font:15px/1.6 system-ui,"Microsoft YaHei",sans-serif}main{max-width:1480px;margin:auto;padding:25px}a{color:#85d8e6}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(410px,1fr));gap:16px}article{background:#1b2a37;border:1px solid #3c5062;padding:18px}h1{font-size:27px}h2{font-size:19px;margin:0}p{color:#b7ccd8}.geometry{width:100%;aspect-ratio:10/7;object-fit:contain;background:#091421;image-rendering:pixelated}.states{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}figure{margin:8px 0;text-align:center}figure img{width:100%;image-rendering:pixelated}figcaption{font-size:13px;color:#b7ccd8}small{display:block;overflow-wrap:anywhere;color:#97adbd}footer{margin:24px 0;color:#97adbd}</style><main><h1>0002 · 九台控制器整机图 R7</h1><p>九台控制器均从各自完整现行结构生成64×64三态面板；统一沿用原金属边框和青色投影风格。上方显示完整结构依据，下方对照原图与空闲、运行、暂停新图。全部为美术候选。</p><p>W02使用当前完整船坞A2，外观仍待批准；W03使用已批准C9；W04使用已批准七雷A3。W05–W15、休伯利安和I37按负责人决定暂时保留。源码已接入，不代表游戏验收。</p><p><a href="overview.png">九台总览图</a> · <a href="manifest.json">来源与贴图清单</a></p><div class="grid">'''
    page += ''.join(cards) + '</div><footer>2026-11-14 · 对话0002 · 01a1d68a-a994-7ac0-a48a-54c0f98fd54e</footer></main></html>'
    (OUT / 'index.html').write_text(page, 'utf-8')


if __name__ == '__main__':
    main()
