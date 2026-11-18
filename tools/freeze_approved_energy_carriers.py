# -*- coding: utf-8 -*-
"""冻结已批准的13项能源载体贴图；只复制交付资源，不触碰正式资产。
【变更记录 #1】2026-10-20 01:12:21（香港时间，贴图审批记录；采用文件首次写入时间）
删除：无；新增：按carrier筛选13项模型、全部图层、原图和合成预览的批准快照。
修改：以外部批准清单覆盖本次载体的候选状态，源V1及其旧状态原字节保留。
用途：保存用户“燃料，乏料(原图，候选)重画；载体采用”的部分批准边界；
后续接入载体无需重复审批，燃料和乏料仍须重画后另行提交。失败即报错，不覆盖旧目录。
"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
from copy import deepcopy
from PIL import Image, ImageDraw, ImageFont
import hashlib
import html
import json
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'deliveries/能源燃料工艺_39项贴图候选_R172_20261019'
SOURCE_MANIFEST = SOURCE / '39项候选与完整图层清单.json'
FORMAL = ROOT / 'src/main/resources/assets/hk3gtl'
RULES = ['rules.md', '系统角色设定.md', '崩坏三-gtl (hk3gtl) 项目规则.md',
         'hk3gtl java文件变更备注规范.md', '当前多方块设计规则.md', '巨构提示词.txt']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(folder):
    return {p.relative_to(folder).as_posix(): sha(p)
            for p in sorted(folder.rglob('*')) if p.is_file()}


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    now = datetime.now(timezone(timedelta(hours=8)))
    timestamp = now.isoformat(timespec='seconds')
    out = ROOT / 'deliveries' / ('能源载体_13项已采用_' + now.strftime('%Y%m%d_%H%M%S_%f'))
    out.mkdir()
    source_before = inventory(SOURCE)
    formal_before = inventory(FORMAL)
    source_zip = SOURCE.with_suffix('.zip')
    source_zip_sha = sha(source_zip)
    manifest = json.loads(SOURCE_MANIFEST.read_text(encoding='utf-8'))
    selected = [row for row in manifest['items'] if row['form'] == 'carrier']
    assert len(selected) == 13 and len({row['id'] for row in selected}) == 13
    copied = {}

    def copy(source_relative, target_relative, expected=None):
        source = SOURCE / source_relative
        source_sha = sha(source)
        if expected:
            assert source_sha == expected, source_relative
        target = out / target_relative
        if target.exists():
            assert sha(target) == source_sha
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        assert sha(target) == source_sha
        copied[target_relative] = {'source_relative': source_relative, 'sha256': source_sha}
        return target_relative

    rows = []
    layer_count = 0
    for old in selected:
        row = deepcopy(old)
        row['source_status_preserved'] = old['status']
        row['status'] = '贴图方案已采用并冻结；未写正式资源、未注册新物品、未部署'
        row['source_model_relative'] = old['model_relative']
        row['model_relative'] = copy(old['model_relative'], old['model_relative'].replace('候选资源/', '已采用资源/', 1), old['model_sha256'])
        for layer in row['layers']:
            old_relative = layer['candidate_relative']
            layer['source_candidate_relative'] = old_relative
            layer['approved_relative'] = copy(old_relative, old_relative.replace('候选资源/', '已采用资源/', 1), layer['candidate_sha256'])
            del layer['candidate_relative']
            copy(layer['source_relative'], layer['source_relative'], layer['source_sha256'])
            layer_count += 1
        copy(old['original'], old['original'])
        copy(old['preview'], old['preview'])
        rows.append(row)
    assert layer_count == 29
    approved = {
        'recorded_at': timestamp, 'timezone': 'Asia/Hong_Kong（UTC+08:00）',
        'source_message_exact_time': '未知；本清单时间为实际记录时间，不冒充原消息发送时间',
        'user_quote': '燃料，乏料(原图，候选)重画\n载体采用',
        'status': '仅13项载体贴图已采用并冻结，未注册物品、未写正式资源、未构建或部署',
        'approval_scope': '13个carrier模型及其29层原候选贴图；后续接入这些原字节无需重复审批',
        'excluded_scope': '13燃料和13乏料的原图及候选须重画；旧26项未获采用，不能接入正式资源',
        'source_manifest': str(SOURCE_MANIFEST), 'source_manifest_sha256': sha(SOURCE_MANIFEST),
        'source_zip': str(source_zip), 'source_zip_sha256': source_zip_sha,
        'item_count': len(rows), 'model_count': len(rows), 'texture_layer_count': layer_count,
        'source_jar': manifest['source_jar'], 'source_jar_sha256': manifest['source_jar_sha256'],
        'rule_read_receipt': [{'path': str(ROOT / 'rule' / r), 'sha256': sha(ROOT / 'rule' / r)} for r in RULES],
        'items': rows, 'copied_files': copied,
        'source_v1_all_files_before': source_before,
        '_record': f'【记录 #1】{timestamp}：删除无；新增13载体批准冻结及完整来源；修改仅外部审批状态；用途为后续按批准原件接入，不代表物品或能源工艺实现。'
    }
    write_json(out / '13项载体采用与冻结清单.json', approved)
    cards = []
    for row in rows:
        cards.append(f'<article><h2>{html.escape(row["name_zh"])}</h2><code>{html.escape(row["id"])}</code><div class="pair"><figure><img src="{row["original"]}" alt="完整原图"><figcaption>完整原图</figcaption></figure><figure><img src="{row["preview"]}" alt="已采用载体"><figcaption>已采用 · {len(row["layers"])}图层</figcaption></figure></div></article>')
    page = '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>13项能源载体 · 已采用</title><style>body{margin:0;background:#edf4f3;color:#173c45;font:16px/1.7 system-ui,"Microsoft YaHei",sans-serif}main{max-width:1150px;margin:auto;padding:28px}header{background:#183f48;color:white;padding:24px;border-radius:14px}a{color:#087689}.notice{background:#fff1dc;padding:18px;border-left:5px solid #b76e2b;margin:22px 0}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:16px}article{background:white;border:1px solid #cbdcde;padding:18px;border-radius:12px}h1{font-size:29px}h2{font-size:18px}.pair{display:flex;justify-content:space-around}figure{margin:16px 0;text-align:center}img{width:112px;height:112px;image-rendering:pixelated;background:repeating-conic-gradient(#dae0e1 0% 25%,#f6f8f8 0% 50%) 50%/16px 16px}figcaption{font-size:13px}code{font-size:11px;overflow-wrap:anywhere}footer{font-size:13px;margin-top:24px}</style></head><body><main><header><h1>13项能源载体 · 已采用</h1><p>' + html.escape(timestamp) + ' · 香港时间</p><p>保留已选载体全部模型、图层、轮廓与颜色；原V1归档保持原字节。</p></header><p class="notice">本页13项载体贴图已采用并冻结，后续按此原件接入无需重复审批。燃料与乏料共26项须重画后另行提交；本页没有批准它们。尚未注册新物品、未写正式资源、未部署到游戏。</p><p><a href="13项载体采用与冻结清单.json">来源、逐文件SHA与部分批准边界</a> · <a href="13项载体采用联系表.png">全部13项对照图</a></p><div class="grid">' + ''.join(cards) + '</div><footer>' + html.escape(approved['_record']) + '</footer></main></body></html>'
    (out / '13项载体采用总览.html').write_text(page, encoding='utf-8')
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 20)
    small = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 15)
    sheet = Image.new('RGB', (920, 50 + 13 * 128), '#edf4f3')
    draw = ImageDraw.Draw(sheet)
    draw.text((22, 12), '13项能源载体已采用：完整原图 → 已采用候选（原字节冻结）', font=font, fill='#173c45')
    for i, row in enumerate(rows):
        y = 50 + i * 128
        draw.rectangle((10, y + 3, 910, y + 123), fill='white')
        draw.text((24, y + 20), row['name_zh'], font=font, fill='#173c45')
        draw.text((24, y + 61), row['id'], font=small, fill='#47646b')
        for j, key in enumerate(('original', 'preview')):
            picture = Image.open(out / row[key]).convert('RGBA').resize((96, 96), Image.Resampling.NEAREST)
            sheet.paste(picture, (566 + j * 170, y + 16), picture)
        draw.text((681, y + 47), '→', font=font, fill='#173c45')
    sheet.save(out / '13项载体采用联系表.png')
    assert inventory(SOURCE) == source_before
    assert sha(source_zip) == source_zip_sha
    assert inventory(FORMAL) == formal_before
    model_count = 0
    for path in (out / '已采用资源/assets/hk3gtl/models/item').glob('*.json'):
        model_count += 1
        model = json.loads(path.read_text(encoding='utf-8'))
        for texture in model['textures'].values():
            namespace, relative = texture.split(':', 1)
            assert (out / f'已采用资源/assets/{namespace}/textures/{relative}.png').is_file(), texture
    assert model_count == 13
    verification = {'recorded_at': timestamp, 'passed': True, 'models': 13, 'texture_layers': 29,
                    'copied_file_count': len(copied), 'copied_bytes_identical': True,
                    'v1_source_files_unchanged': len(source_before), 'v1_zip_unchanged': True,
                    'formal_assets_unchanged': len(formal_before), 'model_texture_references_resolved': True,
                    'new_items_registered': False, 'deployed': False, 'game_verified': False,
                    'approved_manifest_sha256': sha(out / '13项载体采用与冻结清单.json'),
                    '_record': f'【核验记录 #1】{timestamp}：新增本次冻结核验；用途为确认源文件与正式资产不变，不代表游戏验收。'}
    write_json(out / '冻结核验.json', verification)
    zip_path = out.with_suffix('.zip')
    with zipfile.ZipFile(zip_path, 'x', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(out.rglob('*')):
            if path.is_file():
                archive.write(path, path.relative_to(out).as_posix())
    with zipfile.ZipFile(zip_path) as archive:
        assert archive.testzip() is None
        assert len(archive.namelist()) == len(inventory(out))
        for name in archive.namelist():
            assert hashlib.sha256(archive.read(name)).hexdigest() == sha(out / name)
    receipt = {'recorded_at': timestamp, 'directory': str(out), 'zip': str(zip_path),
               'zip_sha256': sha(zip_path), 'manifest_sha256': verification['approved_manifest_sha256'],
               'file_count': len(inventory(out)), 'files': inventory(out), 'verification': verification}
    write_json(ROOT / 'logs/energy-production-r172/13项载体采用冻结回执.json', receipt)
    print(json.dumps({k: v for k, v in receipt.items() if k != 'files'}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
