"""从已确认 I05 蓝图派生 HBV 高度局部修订候选。"""
import base64
import collections
import datetime
import gzip
import hashlib
import json
import shutil
from urllib.parse import quote

from build_i03_centrifuge_preview import TEST_INSTANCE
from build_redesign69 import export, render
from material_resources import Resources
from redesign69_geometry import ROOT
from structure_size_baseline import require


SOURCE = ROOT / 'deliveries/多方块确认归档/20261023_133546_133059_I01-I18_主控居中融合V2_已确认/confirmed_v2/i05/blueprint.json'
REVIEW_TEMPLATE = ROOT / 'deliveries/I01-I18_控制器居中融合修订_V2_20261023/i05/三维评审.html'
OUT = ROOT / 'deliveries/I05_稳定介质再生塔_HBV塔冠内置反应段_主控X20试验_V4_20261026'
HBV = 'hk3gtl:voltage_machine_casing_hbv'
STAINLESS = 'gtceu:stainless_evaporation_casing'
CORROSION = 'gtceu:corrosion_proof_casing'
FILTER = 'gtceu:sterilizing_filter_casing'
GLASS = 'gtceu:laminated_glass'
GRATING = 'gtceu:assembly_line_grating'
PIPE = 'gtceu:ptfe_pipe_casing'
VENT = 'gtceu:computer_heat_vent'


def build():
    original_bytes = SOURCE.read_bytes()
    data = json.loads(original_bytes)
    assert data['key'] == 'i05' and data['size'] == [43, 39, 37]
    original = {(tuple(block['pos']), block['state']) for block in data['blocks']}
    source_controller = tuple(data['controller'])
    target_controller = (20, 3, 16)
    source_states = {tuple(block['pos']): block['state'] for block in data['blocks']}
    target_surface_state = source_states[target_controller]
    source_centering_record = data.get('controller_centering', {})
    source_backings = [tuple(item['pos']) for item in source_centering_record.get('internal_backing_added', [])]
    assert source_backings == [(21, 3, 17)]
    source_backing = source_backings[0]
    assert source_controller == (21, 3, 16)
    assert source_states[source_controller] == 'minecraft:diamond_block'
    assert target_surface_state == HBV
    assert source_states[source_backing] == HBV
    assert source_states[(20, 3, 17)] == HBV
    moved_blocks = []
    for block in data['blocks']:
        pos = tuple(block['pos'])
        if pos == source_backing:
            continue
        if pos == source_controller:
            block['state'] = target_surface_state
        elif pos == target_controller:
            block['state'] = 'minecraft:diamond_block'
        moved_blocks.append(block)
    data['blocks'] = moved_blocks
    data['controller'] = list(target_controller)
    data['controller_centering'] = {
        'version': 'V4坐标试验',
        'status': '按负责人指定坐标试用；相对几何中心向左一格，尚未批准',
        'width': data['size'][0],
        'center_x_0based': (data['size'][0] - 1) // 2,
        'center_column_1based': (data['size'][0] + 1) // 2,
        'old_controller': list(source_controller),
        'new_controller': list(target_controller),
        'offset_from_geometric_center_x': target_controller[0] - ((data['size'][0] - 1) // 2),
        'target_backing_reused': {'pos': [20, 3, 17], 'state': source_states[(20, 3, 17)]},
        'source_backing_removed': {'pos': list(source_backing), 'state': source_states[source_backing]},
        'ports_unchanged': True
    }
    occupied = {tuple(block['pos']) for block in data['blocks']}
    additions = []

    def put(x, y, z, state):
        pos = (x, y, z)
        if pos in occupied:
            raise ValueError(f'新增结构覆盖了已确认方块：{pos}')
        occupied.add(pos)
        additions.append({'pos': [x, y, z], 'state': state})

    # 新反应段沿原塔芯收肩延伸，回路立管留在壳体内部。
    for x in range(17, 24):
        for z in range(20, 27):
            if x in (17, 23) or z in (20, 26):
                put(x, 39, z, CORROSION if (x + z) % 3 else STAINLESS)

    for y in range(40, 46):
        for x in range(17, 24):
            for z in range(20, 27):
                edge = x in (17, 23) or z in (20, 26)
                if not edge:
                    continue
                corner = x in (17, 23) and z in (20, 26)
                if z == 20 and x in (19, 20, 21) and y in (42, 43, 44):
                    state = GLASS
                elif z == 26 and x in (19, 20, 21) and y in (42, 43, 44):
                    state = GLASS
                elif corner:
                    state = STAINLESS
                elif y in (40, 43, 45):
                    state = CORROSION
                else:
                    state = HBV
                put(x, y, z, state)

    for y in range(39, 45):
        put(19, y, 23, PIPE)
        put(20, y, 23, STAINLESS)
        put(21, y, 23, PIPE)
    put(20, 45, 23, STAINLESS)
    for x in (19, 21):
        put(x, 45, 23, PIPE)

    # 两层过滤构件位于内腔，玻璃窗与主塔正面观察线对齐。
    for y in (42, 44):
        for x in range(18, 23):
            for z in range(21, 26):
                if (x in (18, 22) or z in (21, 25)) and (x, z) not in ((19, 23), (21, 23)):
                    put(x, y, z, FILTER)

    # 检修环贴合反应段外肩，排气帽由壳体中央向上收束。
    for x in range(16, 25):
        for z in range(19, 28):
            if x in (16, 24) or z in (19, 27):
                put(x, 46, z, GRATING)
    for x in range(18, 23):
        for z in range(21, 26):
            state = STAINLESS if x in (18, 22) or z in (21, 25) else VENT
            if (x, z) == (20, 23):
                state = HBV
            put(x, 47, z, state)
    for x in range(19, 22):
        for z in range(22, 25):
            state = STAINLESS if abs(x - 20) + abs(z - 23) == 2 else VENT
            if (x, z) == (20, 23):
                state = HBV
            put(x, 48, z, state)

    data['blocks'].extend(additions)
    data['size'] = [43, 49, 37]
    data['brief']['minimum_wdh'] = [43, 37, 49]
    data['brief']['flow'] = '保留原有滤芯、冷凝及屏蔽回收流程；待再生介质沿既有塔芯上升至新增真空脱附段，经内置双立管和分级过滤后回流。'
    data['zones'].append({
        'name': '塔芯真空再生与排气段', 'kind': 'integrated_vacuum_regeneration',
        'min': [16, 39, 19], 'max': [24, 48, 27], 'pos': [20, 44, 23],
        'role': '沿既有塔芯内置双路立管、分级过滤层、贴壳检修环与顶部排气',
        'service_face': '贴合塔冠的环形检修层，南北观察窗'
    })
    data['links'].extend([
        {'from': '既有再生塔芯', 'to': '塔芯真空脱附段',
         'route': [[19, 38, 23], [19, 39, 23], [19, 44, 23]]},
        {'from': '塔芯真空脱附段', 'to': '既有稳定介质回流',
         'route': [[21, 44, 23], [21, 39, 23], [21, 38, 23]]}
    ])
    data['description'] = (
        '保留已确认V2收肩主塔、三层侧抽滤芯盒、回热冷凝器、屏蔽回收坞及六个接口；按负责人指示试将主控移至[20,3,16]，使用该处既有HBV机壳背衬。'
        '新增段从原主塔中央承压芯向上延续，不在外侧另立托柱或管架；两根介质立管收在塔冠壳体内部，'
        '通过分级过滤层、南北观察窗和贴壳检修环完成真空脱附与介质回流，顶部排气帽沿主轴收束。'
    )
    data['candidate_revision'] = {
        'revision': 'hbv-height-v4-controller-x20-trial',
        'status': '独立修订候选，待负责人审阅；未替换已确认V2或接入实例',
        'source_blueprint': str(SOURCE.relative_to(ROOT)).replace('\\', '/'),
        'source_blueprint_sha256': hashlib.sha256(original_bytes).hexdigest(),
        'source_controller_centering_record': source_centering_record,
        'reason': 'HBV结构需严格超过MAX结构的实际高度H43；V2原高度H39。',
        'changes': '新增沿主塔中轴内置的真空再生段、双路立管、过滤层、排气帽与贴壳检修环；按负责人指示将钻石主控由[21,3,16]移至[20,3,16]，旧位恢复为HBV机壳，并移除仅服务旧位的背衬[21,3,17]。',
        'new_blocks': len(additions),
        'preserved_old_blocks': len(original) - 3,
        'overwritten_old_blocks': 2,
        'removed_old_blocks': 1
    }
    data['candidate_revision']['controller_inheritance'] = {
        'source_revision': '已确认的I01-I18 V2',
        'source_blueprint': str(SOURCE.relative_to(ROOT)).replace('\\', '/'),
        'source_blueprint_sha256': hashlib.sha256(original_bytes).hexdigest(),
        'source_v2_controller': list(source_controller),
        'source_controller_backing_removed': list(source_backing),
        'target_controller_backing': [20, 3, 17],
        'controller': data['controller'],
        'width': data['size'][0],
        'center_x_0based': (data['size'][0] - 1) // 2,
        'center_column_1based': (data['size'][0] + 1) // 2,
        'offset_from_geometric_center_x': data['controller'][0] - ((data['size'][0] - 1) // 2),
        'moved_in_candidate': True,
        'placement_reason': '负责人要求试用蓝图坐标[20,3,16]；当前候选相对宽向几何中心列x=21向左一格。',
        'restored_old_position_state': target_surface_state,
        'replaced_target_position_state': target_surface_state
    }
    data['approval_status'] = '候选待负责人审阅'
    data['candidate_version'] = 'I05-HBV-H49-V4'
    data['name'] = 'i05-regeneration-hbv-crown-v4'
    after = {(tuple(block['pos']), block['state']) for block in data['blocks']}
    unchanged_source = {entry for entry in original if entry[0] not in {source_controller, target_controller, source_backing}}
    assert unchanged_source <= after
    assert (source_controller, target_surface_state) in after
    assert (target_controller, 'minecraft:diamond_block') in after
    assert not any(pos == source_backing for pos, _ in after)
    assert len(after) == len(original) - 1 + len(additions)
    assert all(state in {block['state'] for block in json.loads(original_bytes)['blocks']}
               for state in {block['state'] for block in additions})
    return data, original, additions, hashlib.sha256(original_bytes).hexdigest()


def main():
    data, original, additions, source_sha = build()
    size_audit = require(data)
    OUT.mkdir(parents=True, exist_ok=True)
    states, groups, hashes = export(data, OUT)
    counts = collections.Counter(block['state'] for block in data['blocks'])
    resources = Resources(instance=TEST_INSTANCE, project_resources=ROOT / 'src/main/resources')
    try:
        materials = [resources.material(state) for state in states]
        asset_sources = dict(resources.sources)
    finally:
        resources.close()
    OUT.mkdir(parents=True, exist_ok=True)
    render(data, materials, OUT)

    source_map = {(tuple(block['pos']), block['state']) for block in data['blocks'][:len(original) - 1]}
    moved_positions = {tuple(data['candidate_revision']['controller_inheritance']['source_v2_controller']),
                       tuple(data['controller']),
                       tuple(data['candidate_revision']['controller_inheritance']['source_controller_backing_removed'])}
    unchanged_source = {entry for entry in original if entry[0] not in moved_positions}
    assert unchanged_source <= source_map
    assert len(source_map) == len(original) - 1
    assert len(data['blocks']) == len({tuple(block['pos']) for block in data['blocks']})
    assert size_audit['actual_xyz'] == [43, 49, 37]
    assert data['controller'] == [20, 3, 16]
    assert (tuple(data['controller']), 'minecraft:diamond_block') in source_map
    assert not any(pos == (21, 3, 17) for pos, _ in source_map)
    assert data['ports'] == json.loads(SOURCE.read_text(encoding='utf-8'))['ports']

    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
    audit = {
        'recorded_at': now,
        'source_blueprint': str(SOURCE.relative_to(ROOT)).replace('\\', '/'),
        'source_blueprint_sha256': source_sha,
        'approved_geometry_preserved_blocks': len(unchanged_source),
        'overwritten_positions': 2,
        'removed_positions': 1,
        'added_blocks': len(additions),
        'block_count': len(data['blocks']),
        'unique_material_count': len(counts),
        'entity_bbox_xyz': size_audit['actual_xyz'],
        'entity_bbox_volume': size_audit['actual_xyz'][0] * size_audit['actual_xyz'][1] * size_audit['actual_xyz'][2],
        'target_voltage': 'HBV',
        'resource_instance': str(TEST_INSTANCE),
        'asset_sources': asset_sources,
        'max_baseline': {'block_count': 4179, 'materials': 11, 'bbox_volume': 52675, 'height': 43},
        'max_comparison': {'block_count': len(data['blocks']) > 4179,
                           'materials': len(counts) > 11,
                           'bbox_volume': 43 * 49 * 37 > 52675,
                           'height': size_audit['actual_xyz'][1] > 43},
        'controller': data['controller'],
        'ports': data['ports'],
        'material_counts': dict(counts),
        'size_baseline': size_audit,
        'hashes': hashes,
        'checks': [
            '来源哈希指向已确认V2；按负责人要求将主控试移至[20,3,16]，其余7,230个源方块坐标和状态不变',
            '旧主控位[21,3,16]恢复为HBV机壳；目标主控位[20,3,16]为钻石块',
            '目标位已有HBV机壳背衬；移除仅服务旧主控的[21,3,17]背衬',
            '新增部分仅使用原V2既有材料ID',
            '六个接口坐标和用途不变；主控相对宽向几何中心x=21偏移为-1',
            '实体边界按实际方块坐标统计，达到H49并超过MAX的H43',
            'NBT及Sponge导出执行逐格回读校验'
        ],
        'not_verified': [
            '本候选外观待负责人审阅，不代表已批准或替换正式结构',
            '本候选的测试位置相对宽向几何中心x=21偏左一格；严格居中时应使用原V2位置[21,3,16]',
            'Pattern、真实仓室能力、配方、生存可达性及游戏内成型未验收',
            '建筑工艺路线只表达设计意图，不证明机器运行逻辑已接通'
        ]
    }
    meta = {key: value for key, value in data.items() if key != 'blocks'}
    (OUT / 'blueprint.json').write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    (OUT / '设计与检查.json').write_text(json.dumps({'data': meta, 'audit': audit}, ensure_ascii=False, indent=2), encoding='utf-8')
    payload = {'data': meta, 'palette': states, 'groups': groups, 'materials': materials, 'audit': audit, 'names': {}}
    encoded = base64.b64encode(gzip.compress(json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), 9)).decode('ascii')
    (OUT / 'data.js').write_text('window.HK3_PAYLOAD=' + json.dumps(encoded) + ';', encoding='utf-8')
    viewer_path = OUT / 'viewer.bundle.js'
    shutil.copy2(REVIEW_TEMPLATE.parent / 'viewer.bundle.js', viewer_path)
    viewer = viewer_path.read_text(encoding='utf-8')
    missing_count_lookup = '${o.palette[e.state]}'
    assert viewer.count(missing_count_lookup) == 1
    viewer = viewer.replace(missing_count_lookup, '${o.material_counts[e.state]}')
    raw_controller_label = 'te(`主控 [`+r.controller.join(`, `)+`]`'
    assert viewer.count(raw_controller_label) == 1
    viewer = viewer.replace(raw_controller_label, 'te(`主控蓝图 [`+r.controller.join(`, `)+`]`')
    raw_controller_row = '<span>钻石块标记<small>(${r.controller.join(`, `)}) · 朝 -Z</small></span>'
    assert viewer.count(raw_controller_row) == 1
    viewer = viewer.replace(raw_controller_row,
                            '<span>钻石块标记<small>蓝图坐标 [${r.controller.join(`, `)}]（0起算）· 负责人指定试验位置 · 朝 -Z</small></span>')
    default_view = 'get(`view`)??`front`'
    assert viewer.count(default_view) == 1
    viewer_path.write_text(viewer.replace(default_view, 'get(`view`)??`orthofront`'), encoding='utf-8')
    page = REVIEW_TEMPLATE.read_text(encoding='utf-8')
    page = page.replace('href="../index.html#i05">← 全部21形态', 'href="设计与检查.json">← 候选数据')
    page = page.replace('I05 · 稳定介质再生塔 · 主控置中融合修订V2', 'I05 · 稳定介质再生塔 · 主控X20试验候选V4')
    page = page.replace('43×37×39（宽深高） · 7,233方块',
                        f"43×37×49（宽深高） · {len(data['blocks']):,}方块")
    page = page.replace('id="layerValue">38', 'id="layerValue">48')
    page = page.replace('id="layer" type="range" min="0" max="38" value="38"',
                        'id="layer" type="range" min="0" max="48" value="48"')
    page = page.replace('<b>主控 [21, 3, 16]</b>',
                        '<b>主控蓝图坐标 [20, 3, 16]（0起算）</b>')
    page = page.replace('宽43格的第22格，X=21。',
                        '按负责人要求试用蓝图坐标[20,3,16]；该格及其正后方已有HBV机壳。宽向几何中心是x=21，本候选主控向左偏一格；已确认V2和先前V3均保持不变。')
    archive_dir = ROOT / 'doc/HK3GTL-内测5/完整对话归档'
    trial_archive = next((path for path in archive_dir.glob('2026-10-26_*.html')
                          if '"segment_id": "f712b6374858362adb603848"' in path.read_text(encoding='utf-8')),
                         None)
    archive_link = quote(trial_archive.name) if trial_archive else 'index.html'
    page = page.replace('<details><summary>结构文件与边界</summary>',
                        '<details><summary>结构文件与边界</summary><p><a href="../I05_稳定介质再生塔_HBV塔冠内置反应段_主控红点修订_V3_20261025/三维评审.html">保留的V3候选</a> · <a href="../I05_稳定介质再生塔_HBV塔冠内置反应段_V2_20261025/三维评审.html">保留的V2候选</a> · <a href="../../doc/HK3GTL-内测5/完整对话归档/' + archive_link + '">本轮坐标试验原文</a></p>')
    page = page.replace('主控置中融合修订V2</h1>', '主控X20试验候选V4</h1>')
    page = page.replace('<details open><summary>本次结构修改</summary><p>主控沿原再生塔裙座向右一格，落在整机宽度中心列；塔脚进料与冷凝、回收分区保持。</p></details>',
                        '<details open><summary>本次结构修改</summary><p>' + data['description'] +
                        '</p><p>V2来源中7,230个其余方块逐格保留；2个主控格状态变更，并移除1个旧位专用背衬。本候选新增' + str(len(additions)) +
                        '块，仅用于待审阅的独立版本。</p></details>')
    page = page.replace('i05-controller-centered-v2.nbt', data['name'] + '.nbt')
    page = page.replace('i05-controller-centered-v2.schem', data['name'] + '.schem')
    page = page.replace('新候选外观待负责人批准；正式控制器/Pattern、真实仓室、配方、生存研究与游戏运行未验收；I14/I15历史电压映射缺口本轮未处理；离线纹理投影；静态步行检查假设外围平地',
                        '本候选尚未批准或接入实例；Pattern、真实仓室、配方、生存可达性与游戏内成型未验收。')
    page = page.replace('<title>I05 · 稳定介质再生塔 · 主控置中融合修订V2</title>',
                        '<title>I05 · 稳定介质再生塔 · 主控X20试验候选V4</title>')
    (OUT / '三维评审.html').write_text(page, encoding='utf-8')
    print(json.dumps({'out': str(OUT), 'blocks': len(data['blocks']), 'added': len(additions),
                      'materials': len(counts), 'size': size_audit['actual_xyz'],
                      'sha256_source': source_sha, 'hashes': hashes}, ensure_ascii=False))


if __name__ == '__main__':
    main()
