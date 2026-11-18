import base64
from collections import Counter
from datetime import datetime
import gzip
import hashlib
import io
import json
from pathlib import Path
import shutil
import zipfile

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'deliveries/0005_W05_移除双翼后掠主梁_R1_20261115'
OUT = ROOT / 'deliveries/0005_W05_GTL现有方块近色替换_R2_20261115'
LOG = ROOT / 'logs/0005-w05-existing-materials-r2-20261115'
INSTANCE = Path('C:/Users/OWNER/AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版/minecraft')
CLIENT = Path('C:/Users/OWNER/AppData/Roaming/PrismLauncher/libraries/com/mojang/minecraft/1.20.1/minecraft-1.20.1-client.jar')


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8')


def main():
    OUT.mkdir(exist_ok=True)
    LOG.mkdir(exist_ok=True)
    (OUT / 'materials').mkdir(exist_ok=True)
    shutil.copytree(SOURCE / '生成脚本', OUT / '生成脚本', dirs_exist_ok=True)
    for name in ('作者原文.md', '原始构件数据.npz', '构件重合记录.json', 'Three许可.txt', '原文与取样.html'):
        shutil.copy2(SOURCE / name, OUT / name)
    payload = json.loads(gzip.decompress(base64.b64decode(json.loads((SOURCE / 'data.js').read_text('utf8').split('=', 1)[1].removesuffix(';')))))
    old_materials = json.loads((SOURCE / 'materials/materials.json').read_text('utf8'))
    gt = zipfile.ZipFile(INSTANCE / 'mods/gtceu-1.20.1-1.4.4.jar')
    vanilla = zipfile.ZipFile(CLIENT)
    options = (INSTANCE / 'options.txt').read_text('utf8')
    active = json.loads(next(line.split(':', 1)[1] for line in options.splitlines() if line.startswith('resourcePacks:')))
    packs = [zipfile.ZipFile(INSTANCE / 'resourcepacks' / name.removeprefix('file/')) for name in active if name.startswith('file/')]
    overrides = {name: archive for archive in packs for name in archive.namelist()}
    sources = {}

    def resource(archive, path):
        selected = overrides.get(path, archive)
        raw = selected.read(path)
        sources[path] = dict(archive=selected.filename, sha256=hashlib.sha256(raw).hexdigest())
        return raw

    def texture(archive, path, name, animated=False):
        raw = resource(archive, path)
        target = OUT / 'materials' / name
        if animated:
            (OUT / 'materials' / ('source_' + name)).write_bytes(raw)
            image = Image.open(io.BytesIO(raw)).convert('RGBA')
            image.crop((0, 0, image.width, image.width)).save(target)
        else:
            target.write_bytes(raw)
        if path + '.mcmeta' in overrides or path + '.mcmeta' in archive.namelist():
            (OUT / 'materials' / (('source_' if animated else '') + name + '.mcmeta')).write_bytes(resource(archive, path + '.mcmeta'))
        return 'materials/' + name

    shell = texture(gt, 'assets/gtceu/textures/block/casings/gcym/watertight_casing.png', 'watertight_casing.png')
    armor = texture(gt, 'assets/gtceu/textures/block/casings/cleanroom/plascrete.png', 'plascrete.png')
    lamp = texture(vanilla, 'assets/minecraft/textures/block/sea_lantern.png', 'sea_lantern.png', animated=True)
    primary = Image.open(io.BytesIO(resource(gt, 'assets/gtceu/textures/block/material_sets/dull/frame_gt.png'))).convert('RGBA')
    secondary = Image.open(io.BytesIO(resource(gt, 'assets/gtceu/textures/block/material_sets/dull/frame_gt_secondary.png'))).convert('RGBA')
    side = max(primary.width, secondary.width)
    primary = primary.resize((side, side), Image.Resampling.NEAREST)
    secondary = secondary.resize((side, side), Image.Resampling.NEAREST)
    for name, colors in (('stainless_steel_frame', ([237, 237, 253], [25, 25, 29])),
                         ('iridium_frame', ([153, 254, 222], [108, 209, 207]))):
        layers = []
        for image, color in zip((primary, secondary), colors):
            pixels = np.array(image)
            pixels[:, :, :3] = pixels[:, :, :3].astype(np.uint16) * np.array(color, np.uint16) // 255
            layers.append(Image.fromarray(pixels))
        Image.alpha_composite(*layers).save(OUT / 'materials' / (name + '.png'))
    for state in ('watertight_casing', 'plascrete'):
        for folder in ('blockstates', 'models/block'):
            resource(gt, f'assets/gtceu/{folder}/{state}.json')
    resource(gt, 'assets/gtceu/models/block/material_sets/dull/frame_gt.json')
    resource(vanilla, 'assets/minecraft/blockstates/sea_lantern.json')
    resource(vanilla, 'assets/minecraft/models/block/sea_lantern.json')
    rows = [
        ('gtceu:watertight_casing', '防水机械方块', shell, False, 0, '#000000', '保留深青灰基座与机壳；使用原生贴图，不另行染色。'),
        ('gtceu:plascrete', '塑料混凝土', armor, False, 0, '#000000', '冷白大板替代珍珠白装甲；原翡翠刻痕和紫晶装甲纹样不再新增。'),
        ('gtceu:iridium_frame', '铱框架', 'materials/iridium_frame.png', True, 0, '#000000', '原生薄荷青绿双层镂空框架，主色#99fede、次色#6cd1cf；替代蜂窝玻璃管网，保留青绿方向，花纹与透光方式改变。'),
        ('gtceu:watertight_casing', '防水机械方块', shell, False, 0, '#000000', '叶轮沿用暗青工业色，与机壳复用现有方块。'),
        ('minecraft:sea_lantern', '海晶灯', lamp, False, .75, '#ffffff', '原生薄荷青白发光块；预览取原动画首帧，无新绘绕组纹理。'),
        ('gtceu:watertight_casing', '防水机械方块', shell, False, .7, '#19e796', '核心实体复用深青灰块；碧绿能量与白色工作风眼继续作为机器网页特效，非该块原生发光。'),
        ('gtceu:stainless_steel_frame', '不锈钢框架', 'materials/stainless_steel_frame.png', True, 0, '#000000', '按GT原生主色#ededfd、次色#19191d还原双层镂空框架；合成PNG仅供网页还原，不注册新材质。'),
    ]
    materials = []
    for old, (state, label, path, transparent, intensity, emissive, description) in zip(old_materials, rows):
        materials.append(dict(id=old['id'], key=old['key'], label=label, state=state, original_role=old['label'],
            texture=path, color='#ffffff', emissive=emissive, emissiveIntensity=intensity,
            opacity=1, transparent=transparent, alphaTest=.01, description=description))
    now = datetime.now().astimezone().isoformat(timespec='seconds')
    revision = dict(id='R2', created_at=now, user_request='尽量换成GTL模组包原有方块，尽量确保配色没有变化',
        source_delivery=str(SOURCE.relative_to(ROOT)), new_registered_blocks=0, new_game_textures=0,
        material_slots=7, distinct_existing_blocks=len({r[0] for r in rows}), geometry_unchanged=True,
        palette_scope='增强版3.9已有方块，按当前启用资源包覆盖顺序读取；网页近色预览，不改源码注册或游戏资源。')
    payload['data'].update(revision=revision, material_scope=revision['palette_scope'])
    payload['materials'] = [dict(m, texture='data:image/png;base64,' + base64.b64encode((OUT / m['texture']).read_bytes()).decode()) for m in materials]
    packed = gzip.compress(json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode(), compresslevel=6, mtime=0)
    (OUT / 'data.js').write_text('window.W05_AUTHOR_PAYLOAD=' + json.dumps(base64.b64encode(packed).decode()) + ';', 'utf8')
    manifest = json.loads((SOURCE / 'manifest.json').read_text('utf8'))
    counts = Counter()
    for m in materials:
        counts[m['state']] += manifest['material_counts'][str(m['id'])]
    manifest.update(candidate='R2 · GTL现有方块近色替换', created_at=now, revision=revision,
        distinct_existing_blocks=revision['distinct_existing_blocks'], material_count=5, material_slot_count=7, existing_block_counts=dict(counts),
        native_materials=materials, material_sources=sources, active_resourcepacks=active, geometry_unchanged_from_r1=True,
        native_ctm_previewed=False, native_frame_tints={
            'gtceu:stainless_steel_frame': ['#ededfd', '#19191d'],
            'gtceu:iridium_frame': ['#99fede', '#6cd1cf']})
    manifest['preview']['payload_gzip_bytes'] = len(packed)
    mapping = [dict(slot=m['id'], role=m['original_role'], state=m['state'], name=m['label'],
                    component_voxels=manifest['material_counts'][str(m['id'])], description=m['description']) for m in materials]
    for name, value in [('manifest.json', manifest), ('materials/materials.json', materials),
                        ('现有方块映射.json', mapping), ('修订记录.json', revision), ('材质来源.json', sources)]:
        save(OUT / name, value)
    for name in ('constraints.json', '原文落实记录.json'):
        value = json.loads((SOURCE / name).read_text('utf8'))
        value['material_revision'] = revision
        save(OUT / name, value)
    note = 'R2仅将7个预览材质槽替换为5种整合包已有方块，零新增方块与游戏材质。深青灰、冷白与薄荷青绿为主；青绿管网改用铱框架镂空网面，花纹与透光方式有差异。R1删除12梁后的73构件几何保持；网页尚未模拟CTM。'
    for name in ('index.html', '三维评审.html', '原文与取样.html'):
        page = (SOURCE / name).read_text('utf8')
        page = page.replace('R1 · 移除双翼后掠主梁', 'R2 · GTL现有方块近色替换').replace('R1 · 负责人修改版', 'R2 · 零新增方块')
        page = page.replace('7种预览专用材质', '5种已有方块 · 7个用途槽').replace('七种专用预览材质', '已有方块与原材质用途映射')
        page = page.replace('材质贴图与动态均仅供本网页预览；尚未注册游戏方块或BER。', '使用增强版3.9已有方块的原生贴图；不新增注册方块或游戏材质。流光、风眼仍为独立网页特效。')
        page = page.replace('加载R1修订构图…', '加载R2现有方块构图…')
        page = page.replace('负责人R1修改：删除左右翼全部12根后掠空心主梁，其余73个构件的几何、坐标、材质与动态参数保持原案。', note)
        page = page.replace('本次只删除12根后掠空心主梁。', '几何沿用R1删除12根后掠空心主梁后的版本。')
        page = page.replace('alt="R1删除12根后掠空心主梁后完整预览"', 'alt="R2现有方块近色替换完整预览"')
        for old, new in zip(old_materials, materials):
            page = page.replace(old['texture'], new['texture']).replace(old['label'], new['label'] + ' ← ' + old['label'])
        page = page.replace('R1 · 双翼后掠空心主梁已全部删除 · 待机状态', 'R2 · 原有方块近色替换 · R1删梁几何保持')
        page = page.replace('<a href="manifest.json">', '<a href="../' + SOURCE.name + '/三维评审.html">R1原材质对照</a> · <a href="现有方块映射.json">现有方块映射</a> · <a href="manifest.json">', 1)
        (OUT / name).write_text(page, 'utf8')
    capture = (SOURCE / '生成脚本/capture_r1.mjs').read_text('utf8')
    capture = capture.replace(str(SOURCE.relative_to(ROOT)).replace('\\', '/'), str(OUT.relative_to(ROOT)).replace('\\', '/'))
    capture = capture.replace('logs/0005-w05-remove-wing-beams-r1-20261115', str(LOG.relative_to(ROOT)).replace('\\', '/'))
    (OUT / '生成脚本/capture_r2.mjs').write_text(capture, 'utf8')
    shutil.copy2(Path(__file__), OUT / '生成脚本' / Path(__file__).name)
    save(LOG / 'generation.json', manifest)
    print(json.dumps(dict(parts=len(payload['parts']), distinct_existing_blocks=len(counts), new_blocks=0, output=str(OUT)), ensure_ascii=False))


if __name__ == '__main__':
    main()
