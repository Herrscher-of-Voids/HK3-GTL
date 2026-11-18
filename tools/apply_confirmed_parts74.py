"""按负责人确认轮用基板/RAM原图并整体染色，不修改待定电路板。

变更记录 #1：实时时间写入清单；四平台依次采用候选B1至B4、R1至R4。
删除：无。新增：明确授权范围和覆盖前备份。修改：只处理基板与成对RAM。
用途：保留原图像素、透明度、HSV明度和动画；其他资源通过指纹校验。
"""
from datetime import datetime
from pathlib import Path
from io import BytesIO
import colorsys
import hashlib
import json
import shutil
import zipfile
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / 'src/main/resources'
INSTANCE = Path('C:/Users/OWNER/AppData/Roaming/PrismLauncher/instances/GregTech-Leisure-1.4.5.2/minecraft')
OUT = ROOT / 'logs/revision74/confirmed-parts'
PLATFORMS = ['honkai_lattice', 'quantum_coherence', 'imaginary_topology', 'civilization_endurance']
LABELS = ['崩坏晶格', '量子相干', '虚数拓扑', '文明存续']
COLORS = ['#A45BDA', '#22BCD2', '#EBA630', '#DC456F']
FAMILIES = ['wetware', 'optical', 'exotic', 'cosmic']
STAMP = datetime.now().astimezone().isoformat(timespec='seconds')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def write(path, data):
    if isinstance(data, str):
        data = data.encode('utf-8')
    if path.exists():
        if path.read_bytes() == data:
            return
        backup = OUT / 'before' / path.relative_to(ROOT)
        if not backup.exists():
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, backup)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def save_json(path, data):
    write(path, json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def whole_tint(original, color, ram):
    """采用已展示B算法：所有不透明区域染色，保持原图逐像素HSV明度。"""
    hue, saturation, _ = colorsys.rgb_to_hsv(*(int(color[i:i+2], 16) / 255 for i in (1, 3, 5)))
    result = original.copy()
    for y in range(original.height):
        for x in range(original.width):
            r, g, b, a = original.getpixel((x, y))
            if not a:
                continue
            h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            functional = ((max(r, g, b) - min(r, g, b) > 3 and v > .25) if ram
                          else (s > .12 and not .035 <= h <= .20))
            ns = max(s, saturation * .85) if functional else saturation * .55
            rgb = colorsys.hsv_to_rgb(hue, ns, v)
            result.putpixel((x, y), tuple(round(c * 255) for c in rgb) + (a,))
    return result


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    before = {p: digest(p.read_bytes()) for p in RES.rglob('*') if p.is_file()}
    allowed, entries, prepared = set(), [], []
    jar = INSTANCE / 'mods/gtceu-1.20.1-1.4.4.jar'
    # 先验证全部来源，避免中途发现缺图才留下半套轮换。
    with zipfile.ZipFile(jar) as archive:
        for i, platform in enumerate(PLATFORMS):
            for part in ['circuit_substrate', 'ram_wafer', 'ram_chip']:
                ns = 'gtceu' if i == 0 else 'kubejs'
                source_name = FAMILIES[i] + '_circuit_board' if part == 'circuit_substrate' else (
                    part if i == 0 else FAMILIES[i] + '_' + part)
                resource = f'assets/{ns}/textures/item/{source_name}.png'
                if i == 0:
                    data = archive.read(resource)
                    metadata = archive.read(resource + '.mcmeta') if resource + '.mcmeta' in archive.namelist() else None
                    source_path = str(jar) + '!/' + resource
                else:
                    path = INSTANCE / 'kubejs' / resource
                    data = path.read_bytes()
                    metadata = path.with_suffix('.png.mcmeta').read_bytes() if path.with_suffix('.png.mcmeta').exists() else None
                    source_path = str(path)
                item_id = platform + '_' + part
                model_path = RES / f'assets/hk3gtl/models/item/{item_id}.json'
                model = json.loads(model_path.read_text('utf-8'))
                path = RES / ('assets/hk3gtl/textures/' + model['textures']['layer0'].split(':')[1] + '.png')
                original = Image.open(BytesIO(data)).convert('RGBA')
                im = whole_tint(original, COLORS[i], part.startswith('ram_'))
                assert im.size == original.size
                assert im.getchannel('A').tobytes() == original.getchannel('A').tobytes()
                assert [max(p[:3]) for p in im.getdata()] == [max(p[:3]) for p in original.getdata()]
                assert im.tobytes() != original.tobytes(), item_id
                prepared.append((i, part, item_id, model_path, model, path, im, metadata, source_path, digest(data)))

    sheet = Image.new('RGB', (880, 530), '#181b22')
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 20)
    draw.text((20, 10), '已确认：基板 / RAM 原图轮用 · B 整体染色', fill='white', font=font)
    for i, label in enumerate(LABELS):
        draw.text((155 + i * 178, 55), label, fill='white', font=font)
    for row, label in enumerate(['基板', 'RAM 晶圆', 'RAM 晶片']):
        draw.text((15, 125 + row * 135), label, fill='white', font=font)
    for i, part, item_id, model_path, model, path, im, metadata, provenance, source_hash in prepared:
        buffer = BytesIO()
        im.save(buffer, format='PNG')
        write(path, buffer.getvalue())
        allowed.add(path)
        meta_path = path.with_suffix('.png.mcmeta')
        if metadata is not None:
            write(meta_path, metadata)
            allowed.add(meta_path)
        elif meta_path.exists():
            save_json(meta_path, {'animation': {'frames': [0], 'frametime': 20},
                                 '_comment': f'变更记录 {STAMP}：静态来源仅显示零帧，保留历史元数据文件。'})
            allowed.add(meta_path)
        history = model.setdefault('_history', [])
        record = f'变更记录 #5 {STAMP}：负责人确认基板和RAM候选顺序轮用，采用B整体染色；晶圆与切片成对，电路板方案保留。'
        if not any('候选顺序轮用' in h for h in history):
            history.append(record)
            save_json(model_path, model)
            allowed.add(model_path)
        # 落盘回读，逐像素验证最终文件而非只检查内存图像。
        actual = Image.open(path).convert('RGBA')
        assert actual.tobytes() == im.tobytes() and actual.size == im.size
        entries.append({'id': item_id, 'source': provenance, 'source_sha256': source_hash,
                        'destination': path.relative_to(RES).as_posix(), 'sha256': digest(path.read_bytes()),
                        'color': COLORS[i], 'size': list(im.size), 'tint_scope': 'whole',
                        'alpha_preserved': True, 'hsv_value_preserved': True,
                        'animation_metadata_copied': metadata is not None})
        row = ['circuit_substrate', 'ram_wafer', 'ram_chip'].index(part)
        preview = im.crop((0, 0, im.width, im.width)).resize((112, 112), Image.Resampling.NEAREST)
        sheet.paste(preview, (175 + i * 178, 95 + row * 135), preview)
    sheet.save(OUT / 'confirmed-parts.png')
    for name in ['electronic_art74.json', 'gt_circuit_assets.json']:
        path = RES / 'data/hk3gtl/catalog' / name
        catalog = json.loads(path.read_text('utf-8'))
        ids = {e['id'] for e in entries}
        prior = [e for e in catalog['entries'] if e['id'] in ids]
        catalog.setdefault('history', []).append({'generated_at': STAMP, 'reason': '基板与RAM轮用原图并整体染色', 'entries': prior})
        replacements = {e['id']: e for e in entries}
        catalog['entries'] = [replacements.get(e['id'], e) for e in catalog['entries']]
        catalog['confirmed_parts_at'] = STAMP
        catalog['pending_circuit_art'] = '负责人另有电路板选择，保持当前文件，不继续替换；印刷电路板与完整电路均暂缓。'
        save_json(path, catalog)
        allowed.add(path)
    path = RES / 'assets/hk3gtl/changelog.json'
    changelog = json.loads(path.read_text('utf-8'))
    revision = next((e for e in changelog['entries'] if e.get('revision') == 74), None)
    if revision is None:
        now = datetime.now().astimezone()
        revision = {'version': '0.5.0', 'revision': 74, 'codename': 'HK3GTL-内测5',
                    'date': now.strftime('%Y-%m-%d'), 'time': now.strftime('%H:%M:%S'),
                    'summary': '基板与RAM原图轮用、整体染色确认',
                    'reason': '负责人确认基板和RAM轮用候选，电路板另有选择暂缓。', 'changes': []}
        changelog['entries'].insert(0, revision)
    revision['changes'].append(f'{STAMP}：四平台基板按B1/B2/B3/B4轮用，RAM按R1/R2/R3/R4成对轮用；12张贴图采用B整体染色，保留像素与透明度、HSV明度。印刷电路板与完整电路未改。本条不补记未经核验的历史修订或代表游戏验收。')
    save_json(path, changelog)
    allowed.add(path)
    after = {p: digest(p.read_bytes()) for p in RES.rglob('*') if p.is_file()}
    unexpected = [str(p) for p in before.keys() | after.keys() if before.get(p) != after.get(p) and p not in allowed]
    assert not unexpected, unexpected
    assert len({e['sha256'] for e in entries if '_ram_' in e['id']}) == 8
    save_json(OUT / 'verification.json', {'generated_at': STAMP, 'entries': entries,
        'source_layout_alpha_hsv_verified': 12, 'other_resources_unchanged': True,
        'checked_resource_files': len(before), 'build_status': '本报告仅验证资源，构建另看日志',
        'applied_order': 'B1/R1、B2/R2、B3/R3、B4/R4；B5/R5保留为后续轮换候选'})
    print(json.dumps({'textures_verified': len(entries), 'other_resources_unchanged': True}))


if __name__ == '__main__':
    main()
