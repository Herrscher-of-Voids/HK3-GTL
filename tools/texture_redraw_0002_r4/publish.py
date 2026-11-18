import hashlib
import json
import math
import runpy
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
DELIVERY = ROOT / 'deliveries/0002贴图材质_审定重绘_R4_20261114'
REVIEW = ROOT / 'logs/textures-redraw-0002-r3-20261114/art-review.json'
CHAT_ID = '01a1d68a-a994-7ac0-a48a-54c0f98fd54e'


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def collect_designs():
    records = {}
    for name, category in (('process', '魂钢与纳米工艺'), ('world', '空间作业与装备')):
        source = DELIVERY / f'design-{name}.json'
        for item in read_json(source)['items']:
            records[item['id']] = {
                'name': item['name'], 'category': category,
                'code_facts': [item['function_process_facts']], 'project_contract': [],
                'art_interpretation': [{'label': '形制与材质推导', 'text': item['new_visual_interpretation']}],
                'evidence': [{'path': p, 'locator': item['text_evidence_locator']} for p in item['text_evidence_paths']],
                'design_source': source.relative_to(ROOT).as_posix(),
            }
    return records


def contact_sheet(items):
    cell_w, cell_h, columns, header = 184, 184, 8, 78
    sheet = Image.new('RGB', (cell_w * columns, header + cell_h * math.ceil(len(items) / columns)), '#17232b')
    draw = ImageDraw.Draw(sheet)
    title = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 23)
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 14)
    small = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 12)
    draw.text((20, 10), '0002 · 贴图材质 R4 · 26张认可保留，2张待重做', font=title, fill='#f1e7cb')
    draw.text((20, 47), f'64×64 原生像素 | 累计66张锁定 · 未打包 · 未安装 | 对话 ID {CHAT_ID}', font=small, fill='#bac8cc')
    for n, item in enumerate(items):
        x, y = (n % columns) * cell_w, header + (n // columns) * cell_h
        for cy in range(8):
            for cx in range(8):
                color = '#42535b' if (cx + cy) % 2 else '#35464e'
                draw.rectangle((x + 28 + cx * 16, y + cy * 16, x + 43 + cx * 16, y + 15 + cy * 16), fill=color)
        with Image.open(DELIVERY / item['image']) as im:
            tile = im.resize((128, 128), Image.Resampling.NEAREST)
            sheet.paste(tile, (x + 28, y), tile)
        lines = [item['name'][i:i + 11] for i in range(0, len(item['name']), 11)]
        draw.text((x + 10, y + 131), item['review_status'], font=small,
                  fill='#a9d4b9' if item['art_approved'] else '#efb58b')
        draw.multiline_text((x + 10, y + 151), f'{n + 1:02d} ' + '\n   '.join(lines), font=font, fill='#edf0e8', spacing=3)
    sheet.save(DELIVERY / 'contact-sheet.png')


PAGE = runpy.run_path(str(ROOT / 'tools/texture_redraw_0002_r3/publish.py'))['PAGE']
for old, new in (
    ('R3贴图工艺重构 · 59张新图', 'R4贴图审定重绘 · 28张非燃料候选'),
    ('R3 · 从工艺重构实物', 'R4 · 按工艺审定重绘'),
    ('59张新图，以名称、实际用途与当前工艺为设计起点。', '28张非燃料重绘候选，只依据名称、实际用途与工艺设计。'),
    ('<strong>59</strong><span>本轮新图</span>', '<strong>28</strong><span>非燃料候选</span>'),
    ('<strong>20</strong><span>认可项文字保留</span>', '<strong>40</strong><span>锁定项文字保留</span>'),
    ('查看59张总览图', '查看28张总览图'),
    ('59张本轮新图', '28张本轮非燃料候选'),
    ('已认可20项：沿用原文件，仅列文字保留说明', '已认可40项：锁定原文件，仅列文字保留说明'),
    ('这20项不参与本轮重绘，本页不读取或展示其图片。', '这40项不参与本轮重绘，本页不读取或展示其图片。'),
    ('0002 · R3 · 2026-11-14。', '0002 · R4 · 2026-11-14。'),
    ('未构建', '未打包'),
):
    PAGE = PAGE.replace(old, new)
for old, new in (
    ('R4 · 按工艺审定重绘', 'R4 · 26张保留，2张待重做'),
    ('28张非燃料重绘候选，只依据名称、实际用途与工艺设计。', '本轮26张认可锁定；仿制的伊甸之星与仿制的犹大的誓约两张待重做。'),
    ('候选未批准 · 未打包 · 未安装', '26张认可 · 2张待重做 · 未打包 · 未安装'),
    ('<strong>40</strong><span>锁定项文字保留</span>', '<strong>66</strong><span>累计认可锁定</span>'),
    ('${esc(x.category)} · 点击查看设计', '${esc(x.review_status)} · ${esc(x.category)}'),
    ('外观等待负责人评审', '26张认可保留，2张待重做'),
):
    PAGE = PAGE.replace(old, new)
PAGE = PAGE.replace('<section class="tools"', '<p class="sub">燃料棒R5的181张贴图单独待审：<a href="../0002贴图材质_燃料棒_R5_20261114/index.html">查看燃料棒材质</a>。</p><section class="tools"')


def publish():
    review = read_json(REVIEW)
    ids = review['r4_reviewed_ids']
    designs = collect_designs()
    items = []
    for ident in ids:
        path = DELIVERY / f'textures/item/{ident}.png'
        with Image.open(path) as im:
            size = list(im.size)
        items.append({'id': ident, **designs[ident], 'image': path.relative_to(DELIVERY).as_posix(),
                      'native_size': size, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                      'art_approved': ident in review['r4_accepted_ids'],
                      'review_status': '认可保留' if ident in review['r4_accepted_ids'] else '待重做',
                      'change_kind': 'R4非燃料评审记录'})
    manifest = {
        'revision': 'R4', 'date': '2026-11-14', 'conversation_number': '0002', 'conversation_id': CHAT_ID,
        'art_approved': False, 'jar_built': False, 'installed': False, 'game_tested': False,
        'reviewed': True, 'approved_count': 26, 'redraw_count': 2, 'accepted_total': review['accepted_count'],
        'accepted_ids': review['r4_accepted_ids'], 'pending_redraw_ids': review['r4_redo_ids'],
        'reference_policy': 'R4共28张非燃料贴图：26张获负责人认可并锁定原图，两张待重做；此前40项继续锁定。燃料R5独立待审。',
        'review_source': REVIEW.relative_to(ROOT).as_posix(), 'new_image_count': len(items),
        'paused_fuel_count': len(review['paused_fuel_ids']),
        'paused_fuel_ids': review['paused_fuel_ids'], 'fuel_reference_status': review['fuel_reference_status'],
        'fuel_status_text': 'R5燃料母型已确认，181张候选独立待审', 'excluded_item_ids': review['excluded_item_ids'],
        'retained_items': [{'id': x['id'], 'name': x['name'], 'note': '已认可，锁定原文件；本页不读取原图。'}
                           for x in review['accepted_assets'] if x['id'] not in ids],
        'items': items,
    }
    (DELIVERY / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    payload = json.dumps(manifest, ensure_ascii=False).replace('</', '<\\/')
    (DELIVERY / 'index.html').write_text(PAGE.replace('__DATA__', payload), encoding='utf-8')
    contact_sheet(items)
    return {'candidate_images': len(items), 'approved': 26, 'redraw': manifest['redraw_count'], 'paused_fuel': manifest['paused_fuel_count'],
            'retained_text_entries': len(manifest['retained_items']), 'page': str(DELIVERY / 'index.html')}


if __name__ == '__main__':
    print(json.dumps(publish(), ensure_ascii=False))
