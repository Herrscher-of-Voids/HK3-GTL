# -*- coding: utf-8 -*-
"""已确认21形态的电压主色修订候选，同源导出与逐格继承核验。

【变更记录 #1】2026-10-19 12:27:19（香港时间 · 修订172候选交付）
删除：无，不修改确认归档、正式资源、实例与业务代码。
新增：显式2.9资源读取、原状态一次映射、21形态对照、双格式回读和候选HTML。
修改：普通机器统一电压壳，扩建系列保留前阶壳并只改新增层的对应电压。
用途：供负责人整批审美审批；候选不等于正式Pattern、生存首通或游戏验收。

【变更记录 #2】2026-10-19 12:33:11（香港时间 · 修订172候选校正）
删除：错误的I01基项别名；新增：无。修改：沿用总表原有I01-1至I01-4编号。
用途：四个扩建形态分别核对各自尺寸下限，不借用不存在的I01行。

【变更记录 #3】2026-10-19 13:47:03（香港时间 · 修订172交付接续）
删除：无。新增：已完成形态的源哈希、逐格数据及导出哈希核对后复用。
修改：I02–I08归档缺少查看器文件时复用同布局的I01批准查看器。
用途：中断后只补齐未完成产物，保留已经完成的四阶采集塔候选。

【变更记录 #4】2026-10-19 13:57:14（香港时间 · 修订172候选立面增强）
删除：把目标壳占比提示当作主体识别色修复的做法；不删除历史交付凭证。
新增：I08及研究所新增区域的连续灰钢竖肋改色、全部改色位置和前阶继承核验。
修改：先继承前阶候选，再仅将本阶建筑外皮的中性固壳换成本阶现有机壳。
用途：使电压色落实到可见建筑立面；底座、白框、玻璃、穹顶和功能材料保留。
"""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone, timedelta
import base64, copy, gzip, hashlib, html, json, re, shutil, zipfile
import nbtlib
import numpy as np
from build_redesign69 import export, render
from material_resources import Resources
from structure_size_baseline import require

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/21形态_电压主色修订候选_R172_20261019'
LOG = ROOT / 'logs/voltage-architecture-r172'
INSTANCE = Path('C:/Users/OWNER/AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版/minecraft')
ARCHIVE = ROOT / 'deliveries/多方块确认归档'
SOURCES = [
    ARCHIVE / '20261014_212031_239262_I01_V8/confirmed_v8',
    ARCHIVE / '20261015_010334_108818_I02-I08_V7/confirmed_v7',
    ARCHIVE / '20261014_161427_984989_batch-04_I09-I13_V6/confirmed_v6',
    ARCHIVE / '20261015_005918_795325_batch-05_S01-S05_V1/confirmed_v1']
TIERS = 'HBV HCV HRV HDV QSV QCV QEV QAV IMV ICV IRV IWV WFV WSV CIV CEV'.split()
TARGETS = [('i01-1','HBV'),('i01-2','QSV'),('i01-3','QCV'),('i01-4','IWV'),
    ('i02','MAX'),('i03','MAX'),('i04','MAX'),('i05','HBV'),('i06','HBV'),
    ('i07','HBV'),('i08','QSV'),('i09','HRV'),('i10','HRV'),('i11','HRV'),
    ('i12','HRV'),('i13','HDV'),('s01','MAX'),('s02','HDV'),('s03','QEV'),
    ('s04','IRV'),('s05','CIV')]
TIME = lambda: datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')
ESC = html.escape


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def casing(tier):
    return 'gtceu:max_machine_casing' if tier == 'MAX' else 'hk3gtl:voltage_machine_casing_' + tier.lower()


def mapping(key, tier):
    # 对原始状态只查一次表，避免QCV先变成IWV后又被二次替换。
    if key.startswith('i01-'):
        pairs = [('HBV','HBV'),('HDV','QSV'),('CIV','QCV'),('QCV','IWV')]
    elif key.startswith('s'):
        pairs = [('HBV','MAX'),('HDV','HDV'),('CIV','QEV'),('QSV','IRV'),('WSV','CIV')]
    else:
        pairs = [(old, tier) for old in TIERS]
    return {casing(old): casing(new) for old, new in pairs}


class InstanceResources(Resources):
    """复用既有模型解析器；额外按选项顺序读取已启用外部资源包。"""
    def __init__(self):
        super().__init__(instance=INSTANCE)
        self.overrides, self.pack_status = {}, []
        options = (INSTANCE / 'options.txt').read_text(encoding='utf-8')
        packs = json.loads(next(line.split(':', 1)[1] for line in options.splitlines()
                                if line.startswith('resourcePacks:')))
        for name in packs:
            if not name.startswith('file/'):
                self.pack_status.append({'name': name, 'status': '内建或动态资源，沿用JAR静态资源；动态逻辑未模拟'})
                continue
            path = INSTANCE / 'resourcepacks' / name[5:]
            if not path.is_file():
                raise FileNotFoundError('选项中启用的资源包不存在：' + str(path))
            archive = zipfile.ZipFile(path)
            self.archives.append((path, archive))
            count = 0
            for entry in archive.namelist():
                if entry.startswith('assets/'):
                    self.overrides[entry] = (path, archive, entry)
                    count += 1
            self.pack_status.append({'name': name, 'sha256': sha(path), 'root_assets': count,
                                     'status': '按启用顺序覆盖根assets；包内嵌套资源规则未执行'})

    def read(self, rel):
        if rel in getattr(self, 'overrides', {}):
            path, archive, entry = self.overrides[rel]
            self.sources[rel] = str(path) + '!/' + entry
            return archive.read(entry)
        return super().read(rel)


def immutable_snapshot():
    files = [p for source in SOURCES for p in source.rglob('*') if p.is_file()]
    for path in ['src/main/resources/data/hk3gtl/approved_architecture',
                 'src/main/resources/data/hk3gtl/structures/approved']:
        files.extend(p for p in (ROOT / path).rglob('*') if p.is_file())
    return {str(p.relative_to(ROOT)).replace('\\', '/'): sha(p) for p in sorted(set(files))}


def origin(key):
    source = SOURCES[0 if key.startswith('i01-') else 3 if key.startswith('s')
                     else 1 if int(key[1:]) <= 8 else 2]
    return source / key / 'blueprint.json'


def relative_blocks(data):
    anchor = data.get('paste_anchor', data['controller'])
    return {tuple(b['pos'][i] - anchor[i] for i in range(3)): b['state']
            for b in data['blocks'] if b['pos'] != data['controller']}


def strengthen_facades(key, tier, old, data, predecessor):
    """只替换有实际外露侧面的连续固壳竖肋；整列处理，不随机撒点。"""
    eligible = key == 'i08' or key.startswith('s')
    anchor = data.get('paste_anchor', data['controller'])
    inherited = relative_blocks(predecessor) if predecessor else {}
    grid = {tuple(b['pos']): b['state'] for b in old['blocks']}
    allowed = {'laboratory','research_wing','seminar','administration','supercomputer',
               'archive','research_core','research_lab','shared_research',
               'knowledge_library','campus_entrance','shared_library'}
    excluded = {'stairs','cooling','cognitive_dome','courtyard'}
    columns, selected, zones = {}, set(), Counter()
    for p, state in grid.items():
        relative = tuple(p[i] - anchor[i] for i in range(3))
        if not eligible or state != 'gtceu:solid_machine_casing' or p[1] < 2 or relative in inherited:
            continue
        memberships = [z for z in old['zones'] if all(z['min'][i] <= p[i] <= z['max'][i] for i in range(3))]
        if key.startswith('s') and (any(z['kind'] in excluded for z in memberships)
                                   or not any(z['kind'] in allowed for z in memberships)):
            continue
        columns.setdefault((p[0], p[2]), []).append(p[1])
    for (x, z), heights in columns.items():
        runs = []
        for y in sorted(heights):
            if runs and runs[-1][-1] == y-1:
                runs[-1].append(y)
            else:
                runs.append([y])
        for run in runs:
            if len(run) >= 4 and any((x+dx,y,z+dz) not in grid for y in run
                                    for dx,dz in ((1,0),(-1,0),(0,1),(0,-1))):
                selected.update((x,y,z) for y in run)
    for block in data['blocks']:
        p = tuple(block['pos'])
        relative = tuple(p[i] - anchor[i] for i in range(3))
        if relative in inherited:
            block['state'] = inherited[relative]
        elif p in selected:
            block['state'] = casing(tier)
            zone = next((z['name'] for z in old['zones'] if z['kind'] in allowed
                         and all(z['min'][i] <= p[i] <= z['max'][i] for i in range(3))), '主设备外侧竖向固壳')
            zones[zone] += 1
    changes = {}
    for before, after in zip(old['blocks'], data['blocks']):
        if before['state'] == 'gtceu:solid_machine_casing' and before['state'] != after['state']:
            p = tuple(after['pos'])
            label = '本阶新增立面' if p in selected else '前阶原位继承'
            changes.setdefault((label, after['state']), []).append(after['pos'])
    detail = {'time': TIME(), 'key': key, 'new_facade_blocks': len(selected), 'new_facade_zone_counts': dict(zones),
        'rule': '原固壳、局部Y至少2、至少4格连续竖列且存在外露侧面；研究所仅建筑分区并排除楼梯/冷却/庭院/穹顶；前阶位置冻结',
        'groups': [{'scope': label, 'from': 'gtceu:solid_machine_casing', 'to': state,
                    'count': len(positions), 'local_positions': sorted(positions)}
                   for (label,state), positions in sorted(changes.items())]}
    assert all(p[1] >= 2 for group in detail['groups'] for p in group['local_positions'])
    return detail


def namespace_counts(counts):
    groups = Counter()
    for state, count in counts.items():
        groups['指定主控标记' if state == 'minecraft:diamond_block' else
               '指定接口占位' if state == 'hk3gtl:industrial_port_casing' else
               state.split(':')[0]] += count
    total = sum(counts.values())
    return {key: {'blocks': count, 'percent_all_blocks': round(count / total * 100, 3)}
            for key, count in sorted(groups.items())}


def patch_and_verify_sponge(data, path):
    # Offset是相对主控锚点，绝不是世界坐标；公共导出器原先写零偏移。
    loaded = nbtlib.load(path)
    expected_offset = [-v for v in data.get('paste_anchor', data['controller'])]
    loaded['Offset'] = nbtlib.IntArray(expected_offset)
    loaded.save(path, gzipped=True)
    loaded = nbtlib.load(path)
    assert list(map(int, loaded['Offset'])) == expected_offset
    w, h, d = data['size']
    assert [int(loaded[k]) for k in ('Width','Height','Length')] == [w,h,d]
    assert str(loaded.root_name) == 'Schematic'
    assert int(loaded['Palette']['minecraft:air']) == 0
    palette = {str(k): int(v) for k, v in loaded['Palette'].items()}
    dense = np.asarray(loaded['BlockData']).view(np.uint8)
    assert dense.size == w*h*d and max(palette.values()) < 128
    expected = np.zeros(w*h*d, dtype=np.uint8)
    for block in data['blocks']:
        x,y,z = block['pos']
        expected[(y*d+z)*w+x] = palette[block['state']]
    assert np.array_equal(dense, expected)
    return expected_offset


def revised_html(original, data, comparison):
    text = original.read_text(encoding='utf-8')
    text = text.replace(comparison['original_name'], data['name'])
    text = re.sub(r'<title>.*?</title>', '<title>' + ESC(data['title']) + ' · R172电压配色候选</title>', text)
    text = text.replace('待审预览', 'R172电压配色候选 · 未批准')
    text = text.replace('← 采集塔四阶', '← 21形态总览').replace('← 五阶研究所', '← 21形态总览')
    text = text.replace('← 八台新设计', '← 21形态总览').replace('← 五台新设计', '← 21形态总览')
    marker = '<details open><summary>本机建筑概念</summary>'
    note = '<details open><summary>本轮电压与审批状态</summary><p>' + ESC(data['description'])
    note += '</p><p>全部几何、端口和功能材料保留；中性承重立面按电压改色，扩建系列的前阶立面与机壳保留。'
    note += '目标电压壳占实体' + str(comparison['target_share_percent']) + '%，该比例不是外表面积或视觉覆盖率。'
    note += '</p><p><a href="材料计数对照.html">原配色与候选材料对照</a></p></details>'
    text = text.replace(marker, note + marker)
    text = text.replace('三维操作已检查；游戏成型与运行待验收。', '本轮三维交互及游戏验收待完成。')
    text = text.replace('三维载入与剖切检查通过；游戏成型与运行仍待验收。', '本轮三维交互及游戏验收待完成。')
    text = text.replace(comparison['original_description'], ESC(data['description']))
    return text.replace('</html>', '<!-- 变更记录 #1 ' + TIME() + '：复用原评审布局，新增电压候选状态，更新当前材质说明；不沿用旧浏览器验收。 --></html>')


STYLE = '''body{margin:0;background:#101b2b;color:#e7eff8;font:15px/1.75 "Microsoft YaHei",sans-serif}main{max-width:1500px;margin:auto;padding:28px}a{color:#9de6f2}h1{font-size:29px}.notice{background:#2c3545;border-left:4px solid #e7bb79;padding:16px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:18px}.card{border:1px solid #435571;padding:17px;border-radius:9px;background:#162337}.card img{width:100%;height:300px;object-fit:contain}.muted{color:#acbdd1}table{width:100%;border-collapse:collapse}th,td{padding:9px;border:1px solid #435571;text-align:left;overflow-wrap:anywhere}code{font-size:12px}.swatch{image-rendering:pixelated;width:48px;height:48px;vertical-align:middle}section{margin:24px 0}.pair{display:grid;grid-template-columns:1fr 1fr;gap:16px}.pair img{width:100%}@media(max-width:700px){.pair{grid-template-columns:1fr}main{padding:16px}}'''


def page(title, content):
    return '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>' + ESC(title) + '</title><style>' + STYLE + '</style></head><body><main><h1>' + ESC(title) + '</h1>' + content + '<footer class="muted">变更记录 #1 · ' + TIME() + ' 香港时间：新增只读评审交付；正式资源、批准归档与实例均未修改。</footer></main></body></html>'


def materials_page(data, audit, mats):
    rows = []
    for row in audit['material_counts']:
        state = row['state']
        image = mats[state]['faces']['north']
        rows.append('<tr><td><img class="swatch" src="' + image + '"><code>' + ESC(state)
                    + '</code></td><td>' + str(row['before']) + '</td><td>' + str(row['after'])
                    + '</td><td>' + str(row['delta']) + '</td></tr>')
    content = '<a href="../index.html">← 整批总览</a> · <a href="三维评审.html">本机三维</a>'
    content += '<p class="notice">目标电压 ' + audit['target_voltage'] + '；目标机壳 ' + ESC(audit['target_casing'])
    content += '。' + ESC(audit['visual_note']) + '</p><div class="pair"><section><h2>原批准配色 · 当前2.9资源</h2><img src="原配色/等轴预览.png"></section>'
    content += '<section><h2>电压修订候选 · 当前2.9资源</h2><img src="等轴预览.png"></section></div>'
    content += '<p>下表按实际实体计数；主控标记与工业接口占位单列统计。贴图使用实际文件首帧；静态投影不模拟光影、动态染色和内建动态资源。</p><table><tr><th>实际方块状态 / 正面纹理</th><th>原数量</th><th>候选数量</th><th>变化</th></tr>'
    content += ''.join(rows) + '</table><p><a href="材料计数对照.json">完整计数、来源及逐格检查</a>'
    if audit.get('facade_recolor'):
        content += ' · <a href="立面改色位置.json">新增立面与继承部分的全部改色坐标</a>'
    content += '</p>'
    return page(data['title'] + ' · 材料与配色对照', content)


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    LOG.mkdir(parents=True, exist_ok=True)
    before_snapshot = immutable_snapshot()
    save(LOG / 'immutable-before.json', {'time': TIME(), 'files': before_snapshot})
    rules = ['rules.md','系统角色设定.md','崩坏三-gtl (hk3gtl) 项目规则.md',
             'hk3gtl java文件变更备注规范.md','当前多方块设计规则.md','巨构提示词.txt']
    save(LOG / 'rules-read.json', {'time': TIME(), 'files': [
        {'path': 'rule/' + name, 'sha256': sha(ROOT / 'rule' / name)} for name in rules],
        'note': '执行前实际完整读取；读取本身不计业务完成。'})
    resource = InstanceResources()
    mats, entries, previous = {}, [], {}
    used_sources = {}
    try:
        for key, tier in TARGETS:
            source = origin(key)
            old = json.loads(source.read_text(encoding='utf-8'))
            data = copy.deepcopy(old)
            state_map = mapping(key, tier)
            unknown = {b['state'] for b in old['blocks'] if b['state'].startswith('hk3gtl:voltage_machine_casing_')} - set(state_map)
            assert not unknown, (key, unknown)
            data['blocks'] = [{**b, 'state': state_map.get(b['state'], b['state'])} for b in old['blocks']]
            family = 'i01' if key.startswith('i01-') else 's' if key.startswith('s') else None
            facade = strengthen_facades(key, tier, old, data, previous.get(family))
            old_counts = Counter(b['state'] for b in old['blocks'])
            counts = Counter(b['state'] for b in data['blocks'])
            for state in sorted(set(old_counts) | set(counts)):
                if state not in mats:
                    mats[state] = resource.material(state)
            assert all(material['complete_cube'] for material in mats.values())
            inheritance = {'previous': None, 'passed': True, 'preserved_non_controller_blocks': 0}
            family = 'i01' if key.startswith('i01-') else 's' if key.startswith('s') else None
            if family and family in previous:
                predecessor = previous[family]
                prev_grid, grid = relative_blocks(predecessor), relative_blocks(data)
                mismatches = [pos for pos, state in prev_grid.items() if grid.get(pos) != state]
                assert not mismatches, (key, mismatches[:10])
                inheritance = {'previous': predecessor['key'], 'passed': True,
                    'preserved_non_controller_blocks': len(prev_grid),
                    'added_non_controller_blocks': len(grid) - len(prev_grid),
                    'basis': '所有前阶非主控方块按局部坐标减主控粘贴锚点逐格比较位置和状态'}
            original_description = old['description']
            data['name'] = key + '-voltage-r172'
            data['description'] = 'R172电压配色候选：' + tier + '；以原批准几何为基础修订机壳与主体识别色。' + ('扩建保留前阶全部非主控方块、立面与机壳，新增层使用本阶机壳。' if family else '全部16阶电压机壳均统一本机目标。')
            if facade['new_facade_blocks']:
                data['description'] += '将新增区域' + str(facade['new_facade_blocks']) + '格外露连续灰钢竖肋换成本阶现有机壳；地面最低两层、白色边框、玻璃与功能材料保留。'
            data['original_description'] = original_description
            data['candidate_revision'] = {'revision': 172, 'time': TIME(), 'status': '未批准，未接入正式资源', 'source_blueprint': str(source.relative_to(ROOT)), 'source_sha256': sha(source), 'target_voltage': tier, 'state_mapping': state_map, 'inheritance': inheritance}
            data['candidate_revision']['facade_recolor'] = {k:v for k,v in facade.items() if k != 'groups'}
            data['role_materials'] = {state: [state] for state in sorted(counts)}
            data['construction_notes'] = {**old.get('construction_notes', {}), 'status': 'R172电压配色候选，待负责人审批；未做本轮三维交互或游戏验收。'}
            if 'material_usage' in data:
                data['material_usage'] = dict(counts)
            if 'upgrade_contract' in data:
                data['upgrade_contract'] = {**data['upgrade_contract'], **inheritance}
                data['upgrade_contract']['signed_non_controller_sha256'] = hashlib.sha256(json.dumps(sorted(relative_blocks(data).items()), separators=(',', ':')).encode()).hexdigest()
            for field in ('size','controller','ports','paths','zones','links'):
                assert data[field] == old[field], (key, field)
            assert [b['pos'] for b in data['blocks']] == [b['pos'] for b in old['blocks']]
            assert len({tuple(b['pos']) for b in data['blocks']}) == len(data['blocks'])
            recolors = {tuple(p): group['to'] for group in facade['groups'] for p in group['local_positions']}
            assert all(b['state'] == recolors.get(tuple(b['pos']), state_map.get(o['state'], o['state']))
                       for o,b in zip(old['blocks'], data['blocks']))
            # 公共总表已逐形态列出I01-1至I01-4，不能折叠成无对应行的I01。
            export_data = data
            size_audit = require(export_data)
            minimum = data['brief'].get('minimum_wdh')
            if minimum:
                assert all(data['size'][i] >= minimum[j] for i,j in enumerate((0,2,1)))
            folder = OUT / key
            folder.mkdir(exist_ok=True)
            if (folder / '材料计数对照.html').is_file() and json.loads((folder / 'blueprint.json').read_text(encoding='utf-8'))['blocks'] == data['blocks']:
                audit = json.loads((folder / '材料计数对照.json').read_text(encoding='utf-8'))
                cached = json.loads((folder / 'blueprint.json').read_text(encoding='utf-8'))
                assert audit['source_sha256'] == sha(source) and audit['target_voltage'] == tier
                assert cached['blocks'] == data['blocks'] and cached['ports'] == data['ports']
                assert audit['inheritance'] == inheritance
                assert all(sha(folder / (cached['name'] + '.' + ext)) == digest
                           for ext, digest in audit['hashes'].items())
                entries.append({**{k:audit[k] for k in ('key','target_voltage','target_casing','target_share_percent','blocks','visual_note','inheritance','hashes')}, 'title': data['title'], 'name': cached['name'], 'size_xyz': data['size'], 'folder': key})
                if family:
                    previous[family] = data
                print(key, '已完成产物核对后复用', flush=True)
                continue
            save(folder / 'blueprint.json', data)
            save(folder / '立面改色位置.json', facade)
            states, groups, hashes = export(export_data, folder)
            offset = patch_and_verify_sponge(data, folder / (data['name'] + '.schem'))
            hashes['schem'] = sha(folder / (data['name'] + '.schem'))
            share = round(counts[casing(tier)] / len(data['blocks']) * 100, 3)
            note = ('本阶机壳仅占实体' + str(share) + '%，主色可能不显著；没有为提高占比擅改功能材料。' if share < 15 else '机壳已按目标电压替换；视觉协调、主体识别和分区仍需负责人审阅。')
            if facade['new_facade_blocks']:
                note = '本阶新增' + str(facade['new_facade_blocks']) + '格外露连续竖肋已改成本阶机壳；颜色落在研究楼立面或设备外皮，底座与功能材料保留。目标壳占实体' + str(share) + '%，不是可见表面积。'
            audit = {'time': TIME(), 'candidate_only': True, 'key': key, 'target_voltage': tier,
                'target_casing': casing(tier), 'target_share_percent': share, 'visual_note': note,
                'source_blueprint': str(source.relative_to(ROOT)), 'source_sha256': sha(source),
                'original_name': old['name'], 'original_description': original_description,
                'size_baseline': size_audit, 'original_stage_minimum_wdh': minimum,
                'geometry_unchanged': True, 'ports_unchanged': True, 'functional_materials_unchanged': True,
                'blocks': len(data['blocks']), 'inheritance': inheritance, 'offset': offset,
                'facade_recolor': {k:v for k,v in facade.items() if k != 'groups'},
                'state_mapping': {s: state_map[s] for s in sorted(old_counts) if s in state_map},
                'material_counts': [{'state': s, 'before': old_counts[s], 'after': counts[s], 'delta': counts[s]-old_counts[s]} for s in sorted(set(old_counts)|set(counts))],
                'namespace_before': namespace_counts(old_counts), 'namespace_after': namespace_counts(counts), 'hashes': hashes,
                'checks': ['原电压机壳一次状态映射；新增立面改色逐格列举；所有几何、控制器、端口、路径、分区不变', 'NBT全部位置/状态回读与Sponge全部体素/相对Offset回读通过', '当前2.9资源完整立方体模型解析通过', '前阶非主控方块按统一主控锚点逐格保留' if family else '本机全部电压机壳统一本机目标'],
                'not_verified': ['本轮浏览器全部视角、剖切与端口近景尚待实测', '候选未获批准，未替换正式Pattern或部署', '未作游戏成型、配方、生存首通或多人验收', '静态首帧不模拟游戏光影、动态染色、内建动态资源与包内嵌套规则', '机壳实体占比不是可见表面积；功能材料的阶段获取未重新验收']}
            save(folder / '材料计数对照.json', audit)
            save(folder / '设计与检查.json', {'data': {k:v for k,v in data.items() if k != 'blocks'}, 'audit': audit})
            payload = {'data': {k:v for k,v in data.items() if k != 'blocks'}, 'palette': states,
                       'groups': groups, 'materials': [mats[s] for s in states], 'audit': audit, 'names': {}}
            encoded = base64.b64encode(gzip.compress(json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode(), compresslevel=9)).decode('ascii')
            (folder / 'data.js').write_text('/* 变更记录 #1 ' + TIME() + '：原蓝图机壳映射候选；全部逐格数据与结构同源。 */\nwindow.HK3_PAYLOAD=' + json.dumps(encoded) + ';', encoding='utf-8')
            viewer = source.parent.parent / 'viewer.bundle.js'
            if not viewer.is_file():
                viewer = SOURCES[0] / 'viewer.bundle.js'
            shutil.copyfile(viewer, folder / 'viewer.bundle.js')
            # 每机保留其原评审页对应查看器，防止不同归档间查看器版本互串。
            review = revised_html(source.parent / '三维评审.html', data, audit).replace('src="../viewer.bundle.js"', 'src="viewer.bundle.js"')
            (folder / '三维评审.html').write_text(review, encoding='utf-8')
            render(data, [mats[s] for s in states], folder)
            original_folder = folder / '原配色'
            original_folder.mkdir(exist_ok=True)
            render(old, [mats[s] for s in sorted(old_counts)], original_folder)
            (folder / '材料计数对照.html').write_text(materials_page(data, audit, mats), encoding='utf-8')
            entries.append({**{k:audit[k] for k in ('key','target_voltage','target_casing','target_share_percent','blocks','visual_note','inheritance','hashes')}, 'title': data['title'], 'name': data['name'], 'size_xyz': data['size'], 'folder': key})
            if family:
                previous[family] = data
            print(key, tier, len(data['blocks']), 'target_share=' + str(share), 'passed', flush=True)
        used_sources = dict(resource.sources)
        pack_status = resource.pack_status
    finally:
        resource.close()
    assert len(entries) == 21
    after_snapshot = immutable_snapshot()
    assert before_snapshot == after_snapshot, '原批准归档或正式资源发生变化，拒绝宣称交付通过'
    verification = {'time': TIME(), 'candidate_only': True, 'shape_count': len(entries), 'passed': True,
        'formal_resources_changed': False, 'approved_archives_changed': False, 'game_instance_changed': False,
        'geometry_and_ports_unchanged': True, 'inheritance_checks': [e for e in entries if e['inheritance']['previous']],
        'instance': str(INSTANCE), 'minecraft': '1.20.1', 'resource_pack_status': pack_status,
        'resource_sources': used_sources, 'immutable_files_checked': len(after_snapshot), 'machines': entries,
        'not_verified': ['候选外观与主体配色审批', '全部三维页面浏览器交互', '游戏Pattern、仓位、供能及生存首通', '动态染色、游戏光影、内建动态资源和包内嵌套规则', '本轮没有执行构建、部署、游戏启动或整包内存优化']}
    save(OUT / 'verification.json', verification)
    save(LOG / 'verification.json', verification)
    save(LOG / 'immutable-after.json', {'time': TIME(), 'files': after_snapshot, 'unchanged': True})
    save(OUT / 'manifest.json', {'time': TIME(), 'status': '21形态整批候选，待负责人审批', 'machines': entries})
    cards = []
    for entry in entries:
        key = entry['folder']
        cards.append('<article class="card"><h2>' + key.upper() + ' · ' + ESC(entry['title']) + '</h2><p>' + entry['target_voltage'] + ' · ' + '×'.join(map(str, [entry['size_xyz'][0],entry['size_xyz'][2],entry['size_xyz'][1]])) + '（宽深高）</p><a href="' + key + '/三维评审.html"><img loading="lazy" src="' + key + '/等轴预览.png"></a><p>' + ESC(entry['visual_note']) + '</p><p><a href="' + key + '/三维评审.html">三维评审</a> · <a href="' + key + '/材料计数对照.html">前后配色与材料对照</a> · <a href="' + key + '/' + entry['name'] + '.nbt">NBT</a> · <a href="' + key + '/' + entry['name'] + '.schem">Schem</a></p></article>')
    content = '<p class="notice">仅供整批审批：21形态全部从不可变确认蓝图产生，电压壳映射后为I08与五阶研究所补齐可见主体识别色：将本阶新增区域的灰钢外露连续竖肋换成对应现有机壳。未新增方块、未改功能材质、几何与端口；未接入正式资源或游戏实例。<br>扩建系列保留前阶立面、机壳与全部非主控方块；不改最低两层地板、白色框架、玻璃及穹顶。改色逐格坐标见各机材料对照，外观仍需负责人审阅。</p>'
    content += '<p>' + TIME() + ' 香港时间 · 资源来源：增强版2.9当前实际JAR与已启用外部包。MAX使用GTCEu原有MAX机械方块。静态首帧不模拟游戏光影、动态染色及内建动态资源。</p><p><a href="21形态_电压主色修订候选_R172_结构与预览.zip">整批ZIP</a> · <a href="verification.json">逐机验证与资源来源</a> · <a href="manifest.json">21形态清单</a></p><div class="grid">' + ''.join(cards) + '</div>'
    (OUT / 'index.html').write_text(page('21形态 · 电压主色修订候选 R172', content), encoding='utf-8')
    shutil.copyfile(Path(__file__), OUT / Path(__file__).name)
    package = OUT / '21形态_电压主色修订候选_R172_结构与预览.zip'
    with zipfile.ZipFile(package, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(OUT.rglob('*')):
            if path.is_file() and path != package:
                archive.write(path, str(path.relative_to(OUT)).replace('\\', '/'))
    with zipfile.ZipFile(package) as archive:
        assert archive.testzip() is None
    save(LOG / 'package.json', {'time': TIME(), 'path': str(package.relative_to(ROOT)), 'bytes': package.stat().st_size, 'sha256': sha(package), 'zip_crc_passed': True})
    print('complete', len(entries), str(package), flush=True)


if __name__ == '__main__':
    run()
