import base64
from datetime import datetime
import gzip
import json
from pathlib import Path
import shutil

import numpy as np

import package_0005_w05_author_blueprint_20261115 as original


ROOT = original.ROOT
SOURCE = ROOT / 'deliveries/0005_W05_作者蓝图原案_20261115'
OUT = ROOT / 'deliveries/0005_W05_移除双翼后掠主梁_R1_20261115'
LOG = ROOT / 'logs/0005-w05-remove-wing-beams-r1-20261115'
REMOVED = {f'wing_{side}_beam_{i}' for side in ('left', 'right') for i in range(1, 7)}
NOTE = '负责人R1修改：删除左右翼全部12根后掠空心主梁，其余73个构件的几何、坐标、材质与动态参数保持原案。'


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8')


def main():
    OUT.mkdir(exist_ok=True)
    LOG.mkdir(exist_ok=True)
    shutil.copytree(SOURCE / 'materials', OUT / 'materials', dirs_exist_ok=True)
    shutil.copytree(SOURCE / '生成脚本', OUT / '生成脚本', dirs_exist_ok=True)
    for name in ('作者原文.md', 'Three许可.txt'):
        shutil.copy2(SOURCE / name, OUT / name)
    packed = json.loads((SOURCE / 'data.js').read_text('utf8').split('=', 1)[1].removesuffix(';'))
    payload = json.loads(gzip.decompress(base64.b64decode(packed)))
    parts = [p for p in payload['parts'] if p['id'] not in REMOVED]
    removed = [p for p in payload['parts'] if p['id'] in REMOVED]
    data = payload['data']
    now = datetime.now().astimezone().isoformat(timespec='seconds')
    revision = dict(id='R1', created_at=now, user_quote='第一步，先将左翼、右翼的后掠空心主梁全删掉',
                    source_delivery=str(SOURCE.relative_to(ROOT)), note=NOTE,
                    removed_components=[dict(id=p['id'], label=p['label'], blocks=p['blocks']) for p in removed])
    interpretations = [p for p in data['interpretations'] if p.get('section') != '二·3 双翼骨架']
    interpretations = [dict(p, preview_sampling='保留管网、副塔等构件的原案坐标与既有连接；仅按负责人要求删除12根后掠空心主梁。')
                       if p.get('section') == '二·3 构件相交' else p for p in interpretations]
    data.update(revision=revision, interpretations=interpretations)
    materials = json.loads((SOURCE / 'materials/materials.json').read_text('utf8'))
    manifest = json.loads((SOURCE / 'manifest.json').read_text('utf8'))
    archive = np.load(SOURCE / '原始构件数据.npz')
    kept = {p['id'] + suffix: archive[p['id'] + suffix] for p in parts for suffix in ('_xyz', '_materials')}
    np.savez_compressed(OUT / '原始构件数据.npz', **kept)
    low = np.min([kept[p['id'] + '_xyz'].min(0) for p in parts], axis=0)
    high = np.max([kept[p['id'] + '_xyz'].max(0) for p in parts], axis=0)
    w, h, d = map(int, high - low + 1)
    owner = np.zeros(w * h * d, np.uint8)
    counts = np.zeros(8, np.int64)
    overlaps = []
    for i, p in enumerate(parts, 1):
        q = kept[p['id'] + '_xyz'] - low
        keys = (q[:, 1] * d + q[:, 2]) * w + q[:, 0]
        previous = owner[keys]
        hit = previous > 0
        ids, amounts = np.unique(previous[hit], return_counts=True)
        overlaps.extend(dict(first_component=parts[int(j) - 1]['id'], later_component=p['id'], coincident_voxels=int(n))
                        for j, n in zip(ids, amounts))
        owner[keys[~hit]] = i
        counts += np.bincount(kept[p['id'] + '_materials'], minlength=8)
    unique = int(np.count_nonzero(owner))
    del owner
    data['bounds'] = dict(min=low.tolist(), max=high.tolist())
    original.OUT = OUT
    packed_bytes = original.write_payload(data, parts, materials)
    components = [{k: v for k, v in p.items() if k not in ('starts', 'lengths')} for p in parts]
    manifest.update(candidate='负责人R1：移除双翼后掠空心主梁', created_at=now, revision=revision,
                    size_wdh=[w, d, h], occupied_bounds_xyz=data['bounds'], components=components,
                    source_component_voxels=int(counts.sum()), unique_occupied_voxels=unique,
                    overlap_extra_memberships=int(counts.sum()) - unique,
                    material_counts={str(i): int(counts[i]) for i in range(1, 8)},
                    geometry_constraints='按负责人指示删除12梁；其他构件完整保留原坐标与形状，不裁切、不移位。')
    manifest['preview'].update(payload_gzip_bytes=packed_bytes,
        rendered_surface_faces=sum(sum(sum(face) for face in material) for p in parts for material in p['lengths']),
        merged_quads=sum(sum(len(face) for face in material) for p in parts for material in p['starts']))
    constraints = json.loads((SOURCE / 'constraints.json').read_text('utf8'))
    constraints['revision_override'] = revision
    mapping = json.loads((SOURCE / '原文落实记录.json').read_text('utf8'))
    mapping.update(components=components, interpretations=interpretations, revision=revision)
    overlap_record = dict(note='保留原案首占构件归因方法；包含正常连接，不等于全部成对交集或动态穿模验证。',
                          unique_occupied_voxels=unique, extra_component_memberships=int(counts.sum()) - unique, pairs=overlaps)
    for name, value in [('manifest.json', manifest), ('constraints.json', constraints),
                        ('原文落实记录.json', mapping), ('构件重合记录.json', overlap_record), ('修订记录.json', revision)]:
        save(OUT / name, value)
    original.html_pages(data, parts, manifest, constraints, interpretations, materials)
    replacements = {
        '作者蓝图预览': 'R1 · 移除双翼后掠主梁',
        '作者原案独立预览': 'R1 · 负责人修改版',
        '作者蓝图原案 · 独立预览': 'R1 · 移除双翼后掠主梁',
        '加载完整作者蓝图…': '加载R1修订构图…',
        '按原文保留双翼莫比乌斯风洞、中轴风暴炉、480×680底座及指定主控坐标。原文没给出的曲线、角度与叶数属于预览取样，已逐项公开。': NOTE,
        '原文自身的尺寸差异与构件重合照实保留，未通过移位、删件或裁切处理。独立分组可逐一隐藏。重合记录包含正常连接，不能直接当作全部碰撞错误。': '本次只删除12根后掠空心主梁。保留构件间的原有连接与重合未另行调整；重合记录包含正常连接，不宣称整机零穿模。',
        '原文坐标、数量、外观分区与七种材料身份保留。未明确给出的逐格曲线和倾角为可追溯预览取样；原文冲突未私自修正。没有覆盖既有W05 A4，也未进行游戏实装。': NOTE + ' 原作者版本完整保留；本次为网页预览，未替换游戏资源。',
        '作者蓝图原案前左完整预览': 'R1删除12根后掠空心主梁后完整预览',
        '完整构图 · 待机状态': 'R1 · 双翼后掠空心主梁已全部删除 · 待机状态',
        '<h1>原文冻结与实现边界</h1>': '<h1>作者原文与R1修改范围</h1><div class="notice">' + NOTE + ' 作者原文在下方原样保留。</div>',
    }
    for name in ('三维评审.html', 'index.html', '原文与取样.html'):
        text = (OUT / name).read_text('utf8')
        for old, new in replacements.items():
            text = text.replace(old, new)
        (OUT / name).write_text(text, 'utf8')
    capture = (ROOT / 'tools/structure_delivery/capture_0005_w05_author_blueprint_20261115.mjs').read_text('utf8')
    capture = capture.replace("'../..');", "'../../..');")
    capture = capture.replace(str(SOURCE.relative_to(ROOT)).replace('\\', '/'), str(OUT.relative_to(ROOT)).replace('\\', '/'))
    capture = capture.replace('logs/0005-w05-author-blueprint-20261115', str(LOG.relative_to(ROOT)).replace('\\', '/'))
    capture = capture.replace("await fs.copyFile(fileURLToPath(import.meta.url),path.join(out,'生成脚本',path.basename(fileURLToPath(import.meta.url))));", '')
    (OUT / '生成脚本/capture_r1.mjs').write_text(capture, 'utf8')
    shutil.copy2(Path(__file__), OUT / '生成脚本' / Path(__file__).name)
    save(LOG / 'generation.json', manifest)
    print(json.dumps(dict(output=str(OUT), removed=len(removed), parts=len(parts), size_wdh=[w, d, h],
                          component_voxels=int(counts.sum()), unique=unique, quads=manifest['preview']['merged_quads']), ensure_ascii=False))


if __name__ == '__main__':
    main()
