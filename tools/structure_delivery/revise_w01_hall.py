"""W01负责人六项修订的数据源；原始ZIP与分析数据只读，修订单独导出。

变更记录#1：2026-10-30 00:05:13，内测5修订183。
删除指定植物及圈定的14格样件；粉末改混凝土、含水状态改干燥；主控移至西入口。
输出完整稀疏场景、逐项审计及钻石标记预览源，供生产蓝图和真实模型预览共用。
"""
import json
import hashlib
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'output/hall-azu-analysis'
SCENE = ROOT / 'output/w01-dry-layout-20261030'
DELIVERY = ROOT / 'deliveries/W01_永恒礼堂_干燥建材与入口主控修订_V2_20261030'
CONTROLLER_WORLD = [-55, -34, 7]
REMOVED = {'minecraft:warped_roots', 'minecraft:nether_sprouts',
           'minecraft:rose_bush', 'minecraft:lilac', 'minecraft:pink_petals'}


def prohibited(state):
    block = state.split('[')[0]
    return block in REMOVED or 'coral' in block or block in {'minecraft:water', 'minecraft:bubble_column'}


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def main():
    SCENE.mkdir(parents=True, exist_ok=True)
    DELIVERY.mkdir(parents=True, exist_ok=True)
    src = np.load(SOURCE / 'scene-main.npz')
    pos, states, parts = (src[k] for k in ['positions', 'states', 'part_ids'])
    palette = json.loads((SOURCE / 'palette.json').read_text(encoding='utf-8'))
    old_counts = np.bincount(states, minlength=len(palette))
    forbidden = np.array([prohibited(s) for s in palette])
    sample = ((pos >= [-269, 0, 5]) & (pos <= [-267, 1, 8])).all(axis=1)
    assert int(sample.sum()) == 14 and not forbidden[states[sample]].any()
    keep = ~forbidden[states] & ~sample
    changed = [s.replace('minecraft:white_concrete_powder', 'minecraft:white_concrete')
               .replace('waterlogged=true', 'waterlogged=false') for s in palette]
    new_palette = list(dict.fromkeys(changed[int(i)] for i in np.unique(states[keep])))
    remap = np.array([new_palette.index(s) if s in new_palette else 0 for s in changed], dtype=np.uint16)
    new_pos, new_states, new_parts = pos[keep], remap[states[keep]], parts[keep]
    assert len(new_pos) == 1932713
    assert not any(prohibited(s) or 'waterlogged=true' in s or 'white_concrete_powder' in s for s in new_palette)
    low, high = new_pos.min(0), new_pos.max(0)
    assert low.tolist() == [-286, -63, -376] and high.tolist() == [393, 319, 390]
    controller = np.all(new_pos == CONTROLLER_WORLD, axis=1)
    assert controller.sum() == 1 and new_palette[int(new_states[controller][0])] == 'minecraft:chiseled_quartz_block'
    leaves_before = sum(int(n) for s, n in zip(palette, old_counts) if '_leaves[' in s)
    leaves_after = sum(1 for s in new_states if '_leaves[' in new_palette[int(s)])
    assert leaves_before == leaves_after == 1995
    np.savez_compressed(SCENE / 'scene-main.npz', positions=new_pos, states=new_states, part_ids=new_parts)
    write_json(SCENE / 'palette.json', new_palette)
    # HTML只把新主控那一格显示成钻石；生产资源保留被替换石英，由GT机器替换。
    preview = SCENE / 'preview'
    preview.mkdir(exist_ok=True)
    preview_states = new_states.copy()
    preview_states[controller] = len(new_palette)
    np.savez_compressed(preview / 'scene-main.npz', positions=new_pos, states=preview_states, part_ids=new_parts)
    write_json(preview / 'palette.json', new_palette + ['minecraft:diamond_block'])
    classification = {r['state']: r for r in json.loads((SOURCE / 'classification.json').read_text(encoding='utf-8'))}
    counts = np.bincount(new_states, minlength=len(new_palette))
    materials = {}
    for state, count in zip(new_palette, counts):
        record = classification.get(state)
        assert record is not None, '缺少真实模型分类：' + state
        block = state.split('[')[0]
        row = materials.setdefault(block, {'block': block, 'name': record['zh_name'], 'count': 0,
            'full_visual_cube': record['full_visual_cube'], 'category': record['category'], 'states': []})
        row['count'] += int(count)
        row['states'].append({'state': state, 'count': int(count)})
    materials['minecraft:chiseled_quartz_block']['count'] -= 1
    materials['minecraft:chiseled_quartz_block']['states'][0]['count'] -= 1
    materials['hk3gtl:w01_origin_stellar_concert_court'] = {'block': 'hk3gtl:w01_origin_stellar_concert_court',
        'name': 'W01始源星穹协奏庭控制器', 'count': 1, 'full_visual_cube': True,
        'category': 'GT控制器（HTML用钻石标记）', 'states': []}
    assert sum(r['count'] for r in materials.values()) == len(new_pos)
    audit = {
        'revision': 183, 'created_at': datetime.now(timezone(timedelta(hours=8), 'Asia/Hong_Kong')).isoformat(),
        'source': str(SOURCE / 'scene-main.npz'), 'source_sha256': hashlib.sha256((SOURCE / 'scene-main.npz').read_bytes()).hexdigest(),
        'original_count': len(pos), 'revised_count': len(new_pos), 'size_xyz': (high-low+1).tolist(),
        'origin_xyz': low.tolist(), 'bounds': [low.tolist(), high.tolist()], 'runtime_states': len(new_palette),
        'powder_replaced': int(sum(n for s, n in zip(palette, old_counts) if s == 'minecraft:white_concrete_powder')),
        'original_waterlogged': int(sum(n for s, n in zip(palette, old_counts) if 'waterlogged=true' in s)),
        'waterlogged_dried_retained': int(sum(n for s, n, f in zip(palette, old_counts, forbidden) if 'waterlogged=true' in s and not f)),
        'remaining_waterlogged': 0, 'remaining_standalone_water': 0,
        'plants_removed': {s.split('[')[0]: 0 for s, n, f in zip(palette, old_counts, forbidden) if f and n},
        'plants_removed_total': int(forbidden[states].sum()), 'leaves_retained': leaves_after,
        'sample_removed': 14, 'sample_bounds': [[-269, 0, 5], [-267, 1, 8]],
        'sample_blocks': dict(Counter(palette[int(s)].split('[')[0] for s in states[sample])),
        'controller': {'old_source': [7, -16, -17], 'old_local': [293, 47, 359],
            'old_restored': 'minecraft:smooth_quartz', 'source': CONTROLLER_WORLD,
            'local': (np.array(CONTROLLER_WORLD)-low).tolist(), 'front': 'WEST',
            'replaced': 'minecraft:chiseled_quartz_block', 'entrance_midline_z': 6.5,
            'centering': '入口宽14格，中轴Z=6.5；采用中央相邻格Z=7，外侧朝西暴露，低于走道5格。'},
        'materials': sorted(materials.values(), key=lambda r: -r['count']),
        'implementation': {'builder': 'W01专用分批搭建系统，由终极终端调用；保留原生GT成型检查和JEI完整预览。',
            'preparation_steps_per_tick': 65536, 'placement_steps_per_tick': 8192,
            'budget_ms': [2, 12], 'fallback_budget_ms': 4,
            'placement_passes_before': 3, 'placement_passes_after': 1,
            'performance_measured': False, 'mode': '创造测试；生存取料/AE未接入',
            'deployment': '离线制作与构建；未接管用户游戏、未热替换运行JAR、未重写已有存档。'},
        'scope': '当前W01目标区域：主体+13外塔；原ZIP和原始分析数据不改；本轮实体删除1054格，其余仅指定状态和主控位置变化。'
    }
    for s, n, f in zip(palette, old_counts, forbidden):
        if f and n: audit['plants_removed'][s.split('[')[0]] += int(n)
    write_json(DELIVERY / 'revision-audit.json', audit)
    (DELIVERY / 'audit-data.js').write_text('window.W01_AUDIT='+json.dumps(audit, ensure_ascii=False)+';', encoding='utf-8')
    write_json(SCENE / 'revision-audit.json', audit)
    print(json.dumps({k: v for k, v in audit.items() if k not in ['materials', 'implementation']}, ensure_ascii=False))


def preview():
    import hall_azu_preview as renderer
    renderer.SOURCE, renderer.OUT = SCENE / 'preview', DELIVERY
    renderer.main()
    data_path = DELIVERY / 'hall-data.js'
    data = json.loads(data_path.read_text(encoding='utf-8')[len('window.HALL_DATA='):-1])
    data['controller'] = {'source': CONTROLLER_WORLD, 'front': 'WEST', 'preview': 'minecraft:diamond_block'}
    data['notes'] = ['W01修订V2：粉末换白色混凝土、含水全清、指定植物和14格样件删除；主体及13外塔保留。',
        '西入口钻石仅标记GT主控；正式游戏及JEI使用实际控制器，旧礼台恢复石英。',
        '使用MC1.20.1真实模型/贴图，树叶近似色调，动画取首帧；招牌文字及光源方块不绘制。']
    data_path.write_text('window.HALL_DATA='+json.dumps(data, ensure_ascii=False, separators=(',', ':'))+';', encoding='utf-8')
    path = DELIVERY / 'preview-verification.json'
    report = json.loads(path.read_text(encoding='utf-8'))
    report.update(source_geometry_modified=True, revision=183, controller=data['controller'],
                  source_original_preserved=True, preview_placeholder_only=True)
    write_json(path, report)


if __name__ == '__main__':
    main()
    if '--preview' in sys.argv:
        preview()
