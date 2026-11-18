"""修订74电子像素资产生成器：RAM晶圆与切片共享阵列；覆盖前保存原文件。

输入：现有模型与目录；输出：16像素贴图、可追溯清单及检视图。
只修改列入清单的电子资产；不清理旧文件，不生成游戏验收结论。
"""
from datetime import datetime
from pathlib import Path
import hashlib
import json
import shutil
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / 'src/main/resources'
LOG = ROOT / 'logs/revision74'
STAMP = datetime.now().astimezone().isoformat(timespec='seconds')
PLATFORMS = ['honkai_lattice', 'quantum_coherence', 'imaginary_topology', 'civilization_endurance']
COLORS = [(164, 91, 218), (34, 188, 210), (235, 166, 48), (220, 69, 111)]
PATTERNS = [
    ['110', '110', '001'],
    ['101', '010', '101'],
    ['111', '010', '010'],
    ['111', '101', '111'],
]


def backup(path):
    if path.exists():
        dest = LOG / 'backup' / path.relative_to(ROOT)
        if not dest.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, dest)


def save_json(path, data):
    backup(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def shade(color, factor):
    return tuple(min(255, round(c * factor)) for c in color)


def die(index):
    """三像素存储单元同时用于晶圆阵列与切片中心，颜色之外也有拓扑区别。"""
    im = Image.new('RGBA', (3, 3), shade(COLORS[index], .24))
    for y, row in enumerate(PATTERNS[index]):
        for x, value in enumerate(row):
            if value == '1':
                im.putpixel((x, y), (*COLORS[index], 255))
    return im


def ram(index, wafer):
    im = Image.new('RGBA', (16, 16))
    d = ImageDraw.Draw(im)
    color = COLORS[index]
    if wafer:
        d.polygon([(5, 0), (10, 0), (14, 4), (15, 8), (13, 12), (9, 15), (5, 15), (1, 11), (0, 6), (2, 3)], fill=(29, 34, 48), outline=shade(color, .8))
        d.line([(4, 2), (10, 2), (13, 5)], fill=shade(color, 1.5))
        for y in (4, 8):
            for x in (3, 7, 11):
                if x == 11 and y == 8:
                    continue
                im.paste(die(index), (x, y))
        im.paste(die(index), (6, 12))
        d.rectangle((7, 0, 8, 1), fill=(0, 0, 0, 0))
    else:
        for x in (3, 5, 7, 9, 11):
            d.line((x, 1, x, 14), fill=(175, 177, 184))
        d.rectangle((1, 4, 14, 11), fill=(31, 35, 48), outline=shade(color, .65))
        d.line((2, 4, 13, 4), fill=shade(color, 1.4))
        d.rectangle((4, 5, 11, 10), fill=shade(color, .32))
        im.paste(die(index).resize((6, 6), Image.Resampling.NEAREST), (5, 5))
        d.point((2, 10), fill=(236, 224, 179))
    return im


def write_texture(item_id, im):
    model_path = RES / f'assets/hk3gtl/models/item/{item_id}.json'
    model = json.loads(model_path.read_text('utf-8'))
    resource = model['textures']['layer0'].split(':')[1]
    path = RES / f'assets/hk3gtl/textures/{resource}.png'
    backup(path)
    im.save(path)
    history = model.setdefault('_history', [])
    if not any('修订74' in h for h in history):
        history.append(f'变更记录 #3 {STAMP} 内测5修订74：保留注册及模型路径；对应贴图改为平台专用配色和独立几何，晶圆与芯片共享单元图案。')
    save_json(model_path, model)
    meta = path.with_suffix('.png.mcmeta')
    if meta.exists():
        # 保留文件但改为单帧；旧动画索引不可用于新的16×16静态图。
        data = json.loads(meta.read_text('utf-8'))
        data['animation'] = {'frametime': 20, 'frames': [0]}
        data['_comment_revision74'] = f'变更记录 #1 {STAMP}：新图使用完整16像素单帧；取消旧动画索引，保留文件。'
        save_json(meta, data)
    return {'id': item_id, 'destination': path.relative_to(RES).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'size': list(im.size)}


def circuit(family, form):
    """七种封装拓扑×四种形态；底板轮廓、芯片数与主机结构分别演进。"""
    palette = [COLORS[0], (204, 104, 241), COLORS[1], (71, 132, 234), COLORS[2], (191, 213, 126), COLORS[3]]
    c = palette[family]
    dark, board, edge = shade(c, .23), shade(c, .48), shade(c, 1.3)
    im = Image.new('RGBA', (16, 16))
    d = ImageDraw.Draw(im)
    metal, pin, core = (99, 113, 130), (222, 200, 134), (27, 31, 44)

    def chip(x, y, size=3):
        d.rectangle((x, y, x + size - 1, y + size - 1), fill=core, outline=metal)
        d.point((x + 1, y + 1), fill=edge)

    def emblem(x, y):
        motifs = [[(0, 0), (1, 0), (0, 1)], [(1, 0), (0, 1), (2, 1), (1, 2)],
                  [(0, 0), (2, 0), (1, 1), (0, 2), (2, 2)], [(0, 0), (1, 0), (2, 0), (0, 2), (2, 2)],
                  [(0, 0), (1, 1), (2, 2), (2, 0), (0, 2)], [(0, 1), (1, 0), (1, 1), (1, 2), (2, 1)],
                  [(0, 0), (1, 0), (2, 0), (0, 1), (2, 1), (0, 2), (1, 2), (2, 2)]]
        for dx, dy in motifs[family]:
            d.point((x + dx, y + dy), fill=edge)

    if form == 0:
        for k in range(4, 13, 2):
            d.line((k, 1, k, 14), fill=pin)
            d.line((1, k, 14, k), fill=pin)
        outlines = [[(3, 3), (12, 3), (12, 12), (3, 12)], [(7, 1), (14, 7), (8, 14), (1, 8)],
                    [(2, 4), (13, 4), (13, 11), (2, 11)], [(5, 2), (10, 2), (13, 5), (13, 10), (10, 13), (5, 13), (2, 10), (2, 5)],
                    [(4, 2), (11, 2), (14, 7), (11, 12), (4, 12), (1, 7)], [(6, 1), (9, 1), (9, 5), (14, 5), (14, 10), (9, 10), (9, 14), (6, 14), (6, 10), (1, 10), (1, 5), (6, 5)],
                    [(4, 1), (11, 1), (14, 4), (14, 11), (11, 14), (4, 14), (1, 11), (1, 4)]]
        d.polygon(outlines[family], fill=board, outline=metal)
        if family == 2:
            chip(3, 5, 4); chip(9, 5, 4)
        else:
            d.rectangle((5, 5, 10, 10), fill=core, outline=c)
        emblem(6, 6)
    elif form == 1:
        y0 = 3 if family % 2 == 0 else 2
        d.rectangle((1, y0, 14, 12), fill=board, outline=metal)
        for x in range(2, 14, 2):
            d.line((x, 13, x, 15), fill=pin)
        d.line((3, 10, 12, 10), fill=c)
        layouts = [[(3, 5), (9, 5)], [(3, 4), (7, 6), (11, 4)], [(2, 4), (6, 4), (10, 4)],
                   [(2, 3), (10, 3), (6, 7)], [(3, 3), (9, 7)], [(2, 6), (6, 3), (10, 6)], [(2, 3), (10, 3), (2, 8), (10, 8)]]
        for x, y in layouts[family]:
            chip(x, y)
        d.line((2, y0 + 1, 13, y0 + 1), fill=edge)
        emblem(6, 9 if family in (0, 2) else 6)
    elif form == 2:
        d.polygon([(1, 4), (11, 1), (15, 4), (15, 12), (5, 15), (1, 11)], fill=dark, outline=metal)
        d.polygon([(1, 4), (11, 1), (15, 4), (5, 7)], fill=board, outline=edge)
        d.line((5, 7, 5, 14), fill=c)
        chip(2, 6, 3)
        for n in range(2 + family % 3):
            y = 6 + n * 2
            d.line((7, y, 13, y - 1), fill=c if n % 2 else metal)
        if family in (1, 3, 5):
            d.line((11, 4, 11, 12), fill=edge)
        emblem(7, 3)
        d.point((14, 11 - family % 3), fill=pin)
    else:
        silhouettes = [(2, 1, 12, 14), (1, 2, 14, 13), (3, 0, 12, 15), (1, 1, 14, 14),
                       (2, 0, 13, 15), (0, 2, 15, 13), (2, 1, 13, 14)]
        x0, y0, x1, y1 = silhouettes[family]
        d.rectangle((x0, y0, x1, y1), fill=core, outline=metal)
        d.line((x0 + 1, y0 + 1, x1 - 1, y0 + 1), fill=edge)
        if family in (0, 2, 4):
            for y in range(y0 + 3, y1 - 1, 3):
                d.rectangle((x0 + 2, y, x1 - 2, y + 1), fill=board, outline=c)
                d.point((x1 - 1, y), fill=pin)
        elif family in (1, 3):
            d.ellipse((x0 + 2, y0 + 2, x1 - 2, y1 - 2), outline=edge, width=2)
            d.line((7, y0 + 3, 7, y1 - 3), fill=c)
            if family == 3:
                d.line((x0 + 2, 7, x1 - 2, 7), fill=pin)
        elif family == 5:
            for x, y in [(2, 4), (10, 4), (2, 9), (10, 9)]:
                chip(x, y)
            d.line((6, 4, 9, 11), fill=c)
        else:
            d.polygon([(7, 3), (11, 7), (7, 12), (4, 7)], fill=board, outline=edge)
            d.rectangle((6, 5, 9, 10), outline=c)
        emblem(6, 6)
    return im


def main():
    LOG.mkdir(parents=True, exist_ok=True)
    entries = []
    sheet = Image.new('RGB', (512, 256), (22, 26, 35))
    for i, platform in enumerate(PLATFORMS):
        for j, part in enumerate(('ram_wafer', 'ram_chip')):
            im = ram(i, j == 0)
            entries.append(write_texture(platform + '_' + part, im))
            preview = im.resize((112, 112), Image.Resampling.NEAREST)
            sheet.paste(preview, (i * 128 + 8, j * 128 + 8), preview)
    sheet.save(LOG / 'ram-after.png')
    circuits = json.loads((RES / 'data/hk3gtl/catalog/circuit_series.json').read_text('utf-8'))['entries']
    families = list(dict.fromkeys(e['family'] for e in circuits))
    sheet = Image.new('RGB', (512, 896), (22, 26, 35))
    for e in circuits:
        i = families.index(e['family'])
        im = circuit(i, e['form'])
        entries.append(write_texture(e['id'], im))
        preview = im.resize((112, 112), Image.Resampling.NEAREST)
        sheet.paste(preview, (e['form'] * 128 + 8, i * 128 + 8), preview)
    sheet.save(LOG / 'circuits-after.png')
    save_json(RES / 'data/hk3gtl/catalog/electronic_art74.json', {
        'revision': 74, 'generated_at': STAMP,
        'changes': '变更记录 #1：替换四档相同RAM原图；新增紫色双阵列、青色交叉、金色树状及绯色闭环存储单元，晶圆和切片保持对应。',
        'platforms': [{'id': p, 'color': COLORS[i], 'die_pattern': PATTERNS[i]} for i, p in enumerate(PLATFORMS)],
        'entries': entries,
    })
    print(json.dumps({'written': len(entries), 'distinct_sha256': len(set(e['sha256'] for e in entries))}))


if __name__ == '__main__':
    # 变更记录 #2：负责人明确要求原图换色；默认入口已改用原资产，重绘函数不再执行。
    from recolor_electronics74 import main as recolor_originals
    recolor_originals()
