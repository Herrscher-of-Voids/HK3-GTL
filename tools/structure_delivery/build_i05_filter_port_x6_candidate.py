"""从 I05 V4 派生滤芯接口移位候选。"""
import base64
import collections
import datetime
import gzip
import hashlib
import json
import re
import shutil
from urllib.parse import quote

from build_i03_centrifuge_preview import TEST_INSTANCE
from build_redesign69 import export, render
from material_resources import Resources
from redesign69_geometry import ROOT
from structure_size_baseline import require


SOURCE = ROOT / 'deliveries/I05_稳定介质再生塔_HBV塔冠内置反应段_主控X20试验_V4_20261026/blueprint.json'
SOURCE_REVIEW = SOURCE.parent / '三维评审.html'
OUT = ROOT / 'deliveries/I05_稳定介质再生塔_HBV塔冠内置反应段_滤芯接口移至X6_V5_20261026'
INDUSTRIAL_PORT = 'hk3gtl:industrial_port_casing'
DESTINATION_CASING = 'gtceu:stainless_evaporation_casing'
DESTINATION = (6, 3, 16)
OLD_POSITION = (14, 3, 16)
ARCHIVE_NAME = '2026-10-26_00-11-21_好嘛，现在才置中了_3fff333a4b.html'


def build():
    source_bytes = SOURCE.read_bytes()
    data = json.loads(source_bytes)
    assert data['key'] == 'i05' and data['controller'] == [20, 3, 16]
    original = {(tuple(block['pos']), block['state']) for block in data['blocks']}
    source_blocks = {tuple(block['pos']): block['state'] for block in data['blocks']}
    filter_port = next(port for port in data['ports'] if port['id'] == 'FILTER')
    assert tuple(filter_port['pos']) == OLD_POSITION
    filter_port['group'] = 'item_input'
    surface = next(row for row in data['integration_revision']['surfaces'] if row['id'] == 'FILTER')
    restored_state = surface['replaced_surface_state']
    destination_state = source_blocks[DESTINATION]
    backing = (6, 3, 17)
    front = (6, 3, 15)
    assert source_blocks[OLD_POSITION] == INDUSTRIAL_PORT
    assert restored_state == 'hk3gtl:voltage_machine_casing_hbv'
    assert destination_state == DESTINATION_CASING
    assert source_blocks[backing] == DESTINATION_CASING and front not in source_blocks

    for block in data['blocks']:
        pos = tuple(block['pos'])
        if pos == OLD_POSITION:
            block['state'] = restored_state
        elif pos == DESTINATION:
            block['state'] = INDUSTRIAL_PORT
    filter_port['pos'] = list(DESTINATION)
    surface.update({
        'pos': list(DESTINATION), 'backing': list(backing), 'front_air': list(front),
        'replaced_surface_state': destination_state,
        'relation': '替换滤材或屏蔽试件由塔脚进入内部滤芯提升路线；本候选按负责人要求迁至[6,3,16]'
    })

    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
    source_path = str(SOURCE.relative_to(ROOT)).replace('\\', '/')
    source_hash = hashlib.sha256(source_bytes).hexdigest()
    previous_revision = data.get('candidate_revision', {})
    data.setdefault('candidate_revision_history', []).append(previous_revision)
    data['candidate_revision'] = {
        'revision': 'hbv-filter-port-x6-v5',
        'status': '独立修订候选，待负责人审阅；未替换 V4、已确认 V2 或实例',
        'source_blueprint': source_path,
        'source_blueprint_sha256': source_hash,
        'reason': '负责人指出 FILTER 位于主控同高行造成左右布局不协调，并指定迁至[6,3,16]。',
        'changes': '仅迁移 FILTER 接口：旧位[14,3,16]恢复HBV机壳，新位[6,3,16]以工业接口占位块替换不锈钢蒸发机壳；主控[20,3,16]和其他五个接口保持原位。',
        'new_blocks': 0,
        'preserved_old_blocks': len(data['blocks']) - 2,
        'overwritten_old_blocks': 2,
        'removed_old_blocks': 0,
        'controller_unchanged': True,
        'controller': data['controller'],
        'port_count_unchanged': len(data['ports'])
    }
    data['filter_port_relocation'] = {
        'port_id': 'FILTER', 'purpose': filter_port['purpose'],
        'old_position': list(OLD_POSITION), 'new_position': list(DESTINATION),
        'group': filter_port['group'],
        'old_position_restored_state': restored_state,
        'new_position_replaced_state': destination_state,
        'backing': list(backing), 'face': filter_port['face'],
        'front_air': list(front), 'port_count_unchanged': True
    }
    data['controller_centering']['status'] = '负责人确认[20,3,16]为塔芯视觉中线位置；相对整机宽向几何中心x=21的偏移仍如实记录。'
    data['controller_centering']['ports_unchanged'] = False
    data['controller_centering']['ports_moved'] = ['FILTER']
    data['approval_status'] = '候选待负责人审阅'
    data['candidate_version'] = 'I05-HBV-H49-V5'
    data['name'] = 'i05-regeneration-hbv-crown-v5'
    data['description'] = (
        '保留V4确认的塔芯视觉中线主控[20,3,16]、塔冠再生段、三层侧抽滤芯盒与其余五个接口；'
        '仅将FILTER占位接口由[14,3,16]迁至[6,3,16]，旧位恢复HBV机壳。'
        '该接口表示替换滤材或屏蔽试件输入候选，不代表实际功能已经接通。'
    )
    revision = data['integration_revision']
    revision.update({
        'version': 'V5 FILTER接口迁位候选', 'time': now,
        'status': '独立候选；只改接口位置，未更新正式Pattern或实例。',
        'source': source_path,
        'changed_positions': [
            {'pos': list(OLD_POSITION), 'before': INDUSTRIAL_PORT, 'after': restored_state},
            {'pos': list(DESTINATION), 'before': destination_state, 'after': INDUSTRIAL_PORT}
        ],
        'deleted_positions': [], 'added_positions': [],
        'counts': {'before': len(original), 'after': len(data['blocks']), 'deleted': 0, 'changed': 2, 'added': 0},
        'not_verified': ['正式Pattern坐标、能力绑定与游戏内成型未核验。']
    })

    after = {(tuple(block['pos']), block['state']) for block in data['blocks']}
    assert len(after) == len(original) == len(data['blocks'])
    assert (OLD_POSITION, restored_state) in after and (DESTINATION, INDUSTRIAL_PORT) in after
    assert data['controller'] == [20, 3, 16]
    assert len(data['ports']) == 6 and tuple(filter_port['pos']) == DESTINATION
    assert all(entry in after for entry in original if entry[0] not in {OLD_POSITION, DESTINATION})
    return data, original, source_hash


def main():
    data, original, source_hash = build()
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
    render(data, materials, OUT)

    source_map = {(tuple(block['pos']), block['state']) for block in json.loads(SOURCE.read_text(encoding='utf-8'))['blocks']}
    changed = {OLD_POSITION, DESTINATION}
    assert len(source_map) == len(original)
    unchanged = {entry for entry in original if entry[0] not in changed}
    assert unchanged <= source_map
    assert len(unchanged) == len(original) - 2
    assert data['controller'] == [20, 3, 16]

    audit = {
        'recorded_at': datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
        'source_blueprint': str(SOURCE.relative_to(ROOT)).replace('\\', '/'),
        'source_blueprint_sha256': source_hash,
        'unchanged_source_blocks': len(unchanged),
        'changed_positions': [list(OLD_POSITION), list(DESTINATION)],
        'added_blocks': 0, 'removed_blocks': 0, 'block_count': len(data['blocks']),
        'unique_material_count': len(counts), 'entity_bbox_xyz': size_audit['actual_xyz'],
        'target_voltage': 'HBV', 'resource_instance': str(TEST_INSTANCE),
        'asset_sources': asset_sources, 'controller': data['controller'],
        'ports': data['ports'], 'material_counts': dict(counts),
        'size_baseline': size_audit, 'hashes': hashes,
        'checks': [
            'FILTER用途为替换滤材或屏蔽试件输入候选；本次只迁移占位位置，不宣称能力已接通',
            'FILTER从[14,3,16]移至[6,3,16]，六接口总数不变',
            '旧位恢复原HBV机壳；新位不锈钢机壳替换为工业接口占位块',
            '主控[20,3,16]及其余五个接口坐标保持不变',
            '除两个接口表面位置外，V4其余方块坐标与状态逐格一致',
            'NBT和Sponge导出执行逐格回读校验'
        ],
        'not_verified': ['正式Pattern能力绑定、配方和游戏内成型未验收；V5尚未批准或接入实例。']
    }
    meta = {key: value for key, value in data.items() if key != 'blocks'}
    (OUT / 'blueprint.json').write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    (OUT / '设计与检查.json').write_text(json.dumps({'data': meta, 'audit': audit}, ensure_ascii=False, indent=2), encoding='utf-8')
    encoded = base64.b64encode(gzip.compress(json.dumps(
        {'data': meta, 'palette': states, 'groups': groups, 'materials': materials, 'audit': audit, 'names': {}},
        ensure_ascii=False, separators=(',', ':')).encode('utf-8'), 9)).decode('ascii')
    (OUT / 'data.js').write_text('window.HK3_PAYLOAD=' + json.dumps(encoded) + ';', encoding='utf-8')
    shutil.copy2(SOURCE.parent / 'viewer.bundle.js', OUT / 'viewer.bundle.js')

    page = SOURCE_REVIEW.read_text(encoding='utf-8')
    page = page.replace('主控X20试验候选V4', '滤芯接口移位候选V5')
    page = page.replace('按负责人要求试用蓝图坐标[20,3,16]；该格及其正后方已有HBV机壳。宽向几何中心是x=21，本候选主控向左偏一格；已确认V2和先前V3均保持不变。',
                        '按负责人确认保留塔芯视觉中线主控蓝图坐标[20,3,16]；整机包围盒几何中心为x=21。')
    page = page.replace('<details open><summary>本次结构修改</summary>',
                        '<details open><summary>本次结构修改</summary><p>V4塔冠、塔芯和主控位置全部保留。FILTER接口原位[14,3,16]恢复HBV机壳，移至[6,3,16]并复用该处既有不锈钢机壳背衬；其他五个接口不动。FILTER分组为item_input，对应物品输入能力；工业接口块仍只是位置占位，不代表Pattern已经接入。</p></details><details><summary>V4继承说明</summary>')
    link_anchor = '<p><a href="../I05_稳定介质再生塔_HBV塔冠内置反应段_主控红点修订_V3_20261025/三维评审.html">保留的V3候选</a>'
    assert page.count(link_anchor) == 1
    page = page.replace(link_anchor,
                        '<p><a href="../I05_稳定介质再生塔_HBV塔冠内置反应段_主控X20试验_V4_20261026/三维评审.html">保留的V4候选</a> · '
                        '<a href="../I05_稳定介质再生塔_HBV塔冠内置反应段_主控红点修订_V3_20261025/三维评审.html">保留的V3候选</a>')
    page, archive_replacements = re.subn(
        r'2026-10-26_00-00-12_[^\"]+_f712b63748\.html', quote(ARCHIVE_NAME), page)
    assert archive_replacements == 1
    page = page.replace('i05-regeneration-hbv-crown-v4.nbt', data['name'] + '.nbt')
    page = page.replace('i05-regeneration-hbv-crown-v4.schem', data['name'] + '.schem')
    page = re.sub(r'候选尚未批准或接入实例；Pattern、真实仓室、配方、生存可达性与游戏内成型未验收。',
                  'V5待负责人审阅，未接入实例；正式Pattern能力绑定与游戏内成型未验收。', page)
    (OUT / '三维评审.html').write_text(page, encoding='utf-8')
    print(json.dumps({'out': str(OUT), 'blocks': len(data['blocks']), 'materials': len(counts),
                      'size': size_audit['actual_xyz'], 'filter_port': [6, 3, 16],
                      'source_sha256': source_hash, 'hashes': hashes}, ensure_ascii=False))


if __name__ == '__main__':
    main()
