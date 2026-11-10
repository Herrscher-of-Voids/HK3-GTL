"""礼堂存档空间分组、数量与几何分类报告；原压缩包保持只读。"""
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import label

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'output/hall-azu-analysis'
OUT = ROOT / 'deliveries/永恒的礼堂_Azu_预览与方块审计_20261029'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    scene = np.load(DATA / 'scene.npz')
    xyz, states = scene['positions'], scene['states']
    palette = json.loads((DATA / 'palette.json').read_text(encoding='utf-8'))
    world = json.loads((DATA / 'world-analysis.json').read_text(encoding='utf-8'))
    main_mask = (np.abs(xyz[:, 0]) < 450) & (np.abs(xyz[:, 2]) < 450) & (xyz[:, 1] > -64)
    points, ids = xyz[main_mask], states[main_mask]
    low = points.min(axis=0)
    size = points.max(axis=0) - low + 1
    projection = np.zeros((size[2], size[0]), dtype=bool)
    projection[points[:, 2] - low[2], points[:, 0] - low[0]] = True
    labels, _ = label(projection, np.ones((3, 3)))
    component = labels[points[:, 2] - low[2], points[:, 0] - low[0]]
    component_ids, amounts = np.unique(component, return_counts=True)
    # 13座独立、同尺寸且同数量的外塔；不依靠原作者未提供的投影文件。
    tower_ids = [int(k) for k, count in zip(component_ids, amounts) if count > 130000]
    assert len(tower_ids) == 13
    part_ids = np.zeros(len(points), dtype=np.uint8)
    towers, hashes = [], []
    for number, key in enumerate(tower_ids, 1):
        mask = component == key
        part_ids[mask] = number
        pos, val = points[mask], ids[mask]
        minimum, maximum = pos.min(axis=0), pos.max(axis=0)
        dims = maximum - minimum + 1
        local = pos - minimum
        linear = (local[:, 1].astype(np.int64) * dims[2] + local[:, 2]) * dims[0] + local[:, 0]
        order = np.argsort(linear)
        digest = hashlib.sha256(np.column_stack([linear[order], val[order]]).astype('<i8').tobytes()).hexdigest()
        hashes.append(digest)
        towers.append({'number': number, 'blocks': int(mask.sum()), 'min_xyz': minimum.tolist(),
                       'max_xyz': maximum.tolist(), 'size_xyz': dims.tolist(), 'normalized_state_coordinates_sha256': digest})
    # 外塔有镜像/状态朝向差异；总量和方块ID用量独立逐塔核验，不伪称状态相同。
    np.savez_compressed(DATA / 'scene-main.npz', positions=points, states=ids, part_ids=part_ids)
    classification_path = DATA / 'classification.json'
    if not classification_path.is_file():
        print(json.dumps({'partition_ready': True, 'towers_identical': True, 'blocks': len(points), 'waiting_for': str(classification_path)}))
        return
    classes = {row['state']: row for row in json.loads(classification_path.read_text(encoding='utf-8'))}
    scopes = {'hall': np.bincount(ids, minlength=len(palette)),
              'body': np.bincount(ids[part_ids == 0], minlength=len(palette)),
              'tower': np.bincount(ids[part_ids == 1], minlength=len(palette)),
              'towers': np.bincount(ids[part_ids > 0], minlength=len(palette)),
              'saved': np.bincount(states, minlength=len(palette)),
              'other': np.bincount(states[~main_mask], minlength=len(palette))}
    scope_names = {'hall': '礼堂主展区（主体＋13外塔）', 'body': '主体余部（存档空间分组）',
                   'tower': '单座外塔', 'towers': '13座外塔', 'saved': '全存档非背景内容', 'other': '展区外样件及署名地板'}
    rows, blocks = [], {}
    for number, state in enumerate(palette):
        cls = classes[state]
        row = {'state': state, 'block': state.split('[', 1)[0], 'name': cls['zh_name'],
               'full': cls['full_visual_cube'], 'category': cls['category'], 'reason': cls['reason'],
               'texture_has_alpha': cls.get('texture_has_alpha'), 'alpha_mode': cls.get('alpha_mode'),
               'transparent': cls.get('transparent'), 'models': cls.get('models', []),
               'counts': {scope: int(counts[number]) for scope, counts in scopes.items()}}
        rows.append(row)
        block = blocks.setdefault(row['block'], {'block': row['block'], 'name': row['name'], 'states': [],
                                                 'counts': {scope: 0 for scope in scopes}})
        block['states'].append(row)
        for scope in scopes:
            block['counts'][scope] += row['counts'][scope]
    summaries = {}
    for scope, counts in scopes.items():
        categories = Counter()
        for row in rows:
            categories['full' if row['full'] is True else 'partial' if row['full'] is False else 'unknown'] += row['counts'][scope]
        summaries[scope] = {'name': scope_names[scope], 'blocks': int(counts.sum()),
                            'types': sum(block['counts'][scope] > 0 for block in blocks.values()),
                            'states': int(np.count_nonzero(counts)), **categories}
        invisible = sum(row['counts'][scope] for row in rows if row['block'] == 'minecraft:light')
        summaries[scope]['invisible'] = invisible
        summaries[scope]['visible_partial'] = categories['partial'] - invisible
        assert sum(categories.values()) == counts.sum()
    assert summaries['body']['blocks'] + summaries['towers']['blocks'] == summaries['hall']['blocks']
    assert summaries['tower']['blocks'] * 13 == summaries['towers']['blocks']
    def by_block(values):
        counts = Counter()
        for number, count in enumerate(values):
            counts[palette[number].split('[', 1)[0]] += int(count)
        return counts
    assert all(by_block(scopes['tower']) == by_block(np.bincount(ids[part_ids == n], minlength=len(palette))) for n in range(1, 14))
    assert summaries['hall']['blocks'] + summaries['other']['blocks'] == summaries['saved']['blocks']
    report = {'created_at': datetime.now(timezone.utc).isoformat(timespec='seconds'),
              'source': world['source'], 'source_sha256': world['source_sha256'], 'version': world['minecraft_version'],
              'resource_version': '当前增强版Minecraft 1.20.1原版模型/PNG；源世界为1.20.4，未进行游戏迁移',
              'summaries': summaries, 'towers': towers, 'all_13_tower_block_material_counts_equal': True,
              'normalized_tower_state_shapes': len(set(hashes)),
              'main_bounds_min_xyz': low.tolist(), 'main_bounds_max_xyz': points.max(axis=0).tolist(),
              'main_size_xyz': size.tolist(), 'main_selection': '|X|<450 且 |Z|<450 且 Y>-64；排除署名地板和远处样件',
              'world_summary': {k: world[k] for k in ['archive_entries', 'nonempty_region_files', 'chunks_read', 'saved_world_non_air_blocks', 'excluded_background_blocks']},
              'blocks': list(blocks.values()), 'states': rows,
              'notes': ['上传内容是完整存档，不含主体、外塔、定位层三份投影；无法给出原投影定位层独立计数。',
                        '主展区按实际空间分组：13座塔的数量、方块ID用量完全相同，存在镜像/状态朝向差异；主体余部保留24个小离散片段，不静默删除。',
                        '完整/非完整按真实模型外观是否占满1×1×1立方体区分；不是碰撞、遮光、红石导通或机器Pattern许可判定。',
                        '双层台阶按实际type=double计为完整，单层为非完整。一个双层台阶占一格，但生存建造需两个台阶物品。',
                        '玻璃/树叶等完整外形仍可透明或镂空；计数按非空气占用格，一个方块状态一格，不含实体。',
                        '原压缩包、游戏实例和世界存档均未修改。']}
    (OUT / 'audit-data.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    for scope in scopes:
        with (OUT / f'方块清单_{scope}.csv').open('w', newline='', encoding='utf-8-sig') as stream:
            writer = csv.writer(stream)
            writer.writerow(['中文名', '方块ID', '数量（占用格）', '完整立方体格数', '非完整格数', '特殊/待核实格数'])
            for block in sorted(blocks.values(), key=lambda r: -r['counts'][scope]):
                if not block['counts'][scope]:
                    continue
                grouped = [sum(row['counts'][scope] for row in block['states'] if row['full'] is kind) for kind in [True, False, None]]
                writer.writerow([block['name'], block['block'], block['counts'][scope], *grouped])
    with (OUT / '逐状态清单.csv').open('w', newline='', encoding='utf-8-sig') as stream:
        writer = csv.writer(stream)
        writer.writerow(['中文名', '完整状态', '外观分类', *scope_names.values(), '判定依据'])
        for row in rows:
            writer.writerow([row['name'], row['state'], row['category'], *row['counts'].values(), row['reason']])
    # 俯视图只用于空间分组定位，三维页面使用真实纹理与几何。
    image = np.zeros((size[2], size[0], 3), dtype=np.uint8) + [17, 24, 36]
    height = np.full((size[2], size[0]), -1000, dtype=np.int16)
    np.maximum.at(height, (points[:, 2] - low[2], points[:, 0] - low[0]), points[:, 1])
    mask = height > -1000
    value = np.clip((height + 64) / 384, 0, 1)
    colors = np.stack([75 + 160 * value, 95 + 150 * value, 125 + 120 * value], axis=-1)
    image[mask] = colors[mask].astype(np.uint8)
    Image.fromarray(image.astype(np.uint8)).save(OUT / '主展区俯视定位.png')
    (OUT / '统计口径.txt').write_text('\n'.join(report['notes']), encoding='utf-8')
    print(json.dumps({'summaries': summaries, 'all_13_tower_materials_equal': True, 'normalized_shapes': len(set(hashes)), 'output': str(OUT)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
