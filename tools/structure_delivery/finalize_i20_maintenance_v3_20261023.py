# -*- coding: utf-8 -*-
"""封装I20原位主控修订，逐格核对差异并如实记录空区仍待处理。

【文件职责】读取V1/V2/I19和导出文件，验证唯一墙面改动、主控继承及保护文件身份。
【变更记录 #1】2026-10-23 19:44:05（独立候选封装，不增加模组修订号）
删除：无。新增：逐格差异、原位主控及空区A核对、文件清单、ZIP和讨论记录。
修改：候选明确说明空区尚未改动，不把用户询问解释为新增设施批准。
用途：保证页面、三维载荷和结构文件一致，保留前阶段和V1原件。
【变更记录 #2】2026-10-23 20:03:04（检修厂房与外围路V3核对）
删除：V2单块差异和空区不改填的当前断言。新增：厂房设备、内部工位可达、南路与墙外维护带检查。
修改：保留I19和V2源文件，按本轮授权核对厂房及道路；用途：封装完整V3候选，不写正式资源或实例。
"""
import base64
import collections
import datetime as dt
import gzip
import hashlib
import html
import json
import re
import shutil
import zipfile
from pathlib import Path

import nbtlib
import numpy as np

from build_i20_qsv_maintenance_v3 import OUT, LOG, ROOT, NAME, BASE
from build_integration_revision_20261023 import access


def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p, value): p.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def mapping(data): return {tuple(b['pos']): b['state'] for b in data['blocks']}


def main():
    now = dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))
    folder = OUT/'i20'
    source = ROOT/'deliveries/I20_中型崩坏能反应堆_原位主控修订_V2_20261023'
    data = read(folder/'blueprint.json')
    prior = read(source/'i20/blueprint.json')
    old = read(BASE)
    current, previous, inherited = mapping(data), mapping(prior), mapping(old)
    assert len(current) == len(data['blocks']) == 522531
    assert data['size'] == [271,155,233]
    assert data['controller'] == old['controller'] == [95,3,20] and data['controller_face'] == 'north'
    assert all(current[p] == state for p,state in inherited.items())
    assert data['ports'] == prior['ports'] and len(data['ports']) == 16
    assert set(current.values()) <= set(previous.values())
    added = [p for p in current if p not in previous]
    removed = [p for p in previous if p not in current]
    replacements = [p for p,state in current.items() if p in previous and state != previous[p]]
    assert all(p[0] == 108 and 2 <= p[1] <= 8 and 201 <= p[2] <= 204 for p in removed)
    assert all(p[1] == 0 for p in replacements)
    differences = {'added':len(added),'removed':len(removed),'replaced':len(replacements),
                   'removed_positions':[list(p) for p in removed],
                   'replaced_bounds':{'min':[min(p[i] for p in replacements) for i in range(3)],
                                      'max':[max(p[i] for p in replacements) for i in range(3)]}}
    assert current[(135,3,184)] == 'hk3gtl:voltage_machine_casing_qsv'
    equipment_checks = {
        (50,27,203):'gtceu:titanium_gearbox',
        (50,20,203):'gtceu:titanium_pipe_casing',
        (40,12,188):'hk3gtl:voltage_machine_casing_qsv',
        (40,24,191):'gtceu:steel_machine_casing',
        (49,5,200):'gtceu:stainless_steel_turbine_casing',
        (24,5,198):'gtceu:stainless_steel_turbine_casing',
        (64,5,198):'gtceu:stainless_steel_turbine_casing',
        (82,5,198):'gtceu:stainless_steel_turbine_casing',
        (24,5,217):'gtceu:steel_machine_casing'}
    assert all(current.get(p) == state for p,state in equipment_checks.items())
    for x in range(271):
        for z in range(228,233):
            assert current.get((x,0,z)) == 'gtceu:steel_machine_casing'
            assert all((x,y,z) not in current for y in range(1,5))
    for x in range(6,266):
        for z in range(223,228):
            assert current.get((x,0,z)) == 'gtceu:assembly_line_grating'
            assert all((x,y,z) not in current for y in range(1,5))
    for lo,hi in ((0,5),(266,270)):
        for x in range(lo,hi+1):
            for z in range(223,233): assert current.get((x,0,z)) == 'gtceu:steel_machine_casing'
    probes=[{'id':'西侧泵转子检修位','pos':[20,3,203],'face':'west'},
            {'id':'中央拆装床','pos':[42,4,203],'face':'west'},
            {'id':'东侧泵转子检修位','pos':[88,3,203],'face':'east'},
            {'id':'后墙备件架','pos':[24,5,217],'face':'north'}]
    workstation_access=access({**data,'ports':probes})[1:]
    assert all(p['front_clear'] and p['backing_solid'] and p['walk_access'] for p in workstation_access),workstation_access
    save(LOG/'workstation-access.json',workstation_access)
    # NBT按坐标与状态全量回读；Sponge包含整个包围盒内的空气一起比较。
    nbt = nbtlib.load(folder/(NAME+'.nbt'))
    assert list(map(int, nbt['size'])) == data['size']
    palette = []
    for b in nbt['palette']:
        state = str(b['Name'])
        props = b.get('Properties', {})
        if props: state += '['+','.join(str(k)+'='+str(v) for k, v in sorted(props.items()))+']'
        palette.append(state)
    saved = {tuple(map(int, b['pos'])): palette[int(b['state'])] for b in nbt['blocks']}
    assert saved == current
    del nbt, saved
    schem = nbtlib.load(folder/(NAME+'.schem'))
    w, h, d = data['size']
    assert int(schem['Version']) == 2 and int(schem['DataVersion']) == 3465
    assert [int(schem[k]) for k in ('Width', 'Height', 'Length')] == [w, h, d]
    ids = {str(k): int(v) for k, v in schem['Palette'].items()}
    assert ids['minecraft:air'] == 0 and max(ids.values()) < 128
    dense = np.zeros(w*h*d, dtype=np.uint8)
    for (x, y, z), state in current.items(): dense[(y*d+z)*w+x] = ids[state]
    assert np.array_equal(dense, np.asarray(schem['BlockData']).view(np.uint8))
    assert list(map(int, schem['Offset'])) == [0, 0, 0]
    del schem, dense
    payload = json.loads(gzip.decompress(base64.b64decode(re.search(
        r'window.HK3_PAYLOAD\s*=\s*"([^"\n]+)"', (folder/'data.js').read_text(encoding='utf-8'))[1])))
    assert payload['data']['controller'] == data['controller']
    assert payload['data']['ports'] == data['ports']
    expected = [set() for _ in payload['palette']]
    for (x, y, z), state in current.items(): expected[payload['palette'].index(state)].add((y*d+z)*w+x)
    assert all(set(g) == e for g, e in zip(payload['groups'], expected))
    assert len(payload['groups']) == len(expected)
    protected = read(LOG/'protected-before.json')
    changed = [p for p, identity in protected['files'].items()
               if not Path(p).is_file() or sha(Path(p)) != identity]
    assert not changed, changed
    verification = read(OUT/'verification.json')
    assert all(p['front_clear'] and p['backing_solid'] and p['walk_access'] for p in verification['access'])
    review = {'time': now.isoformat(), 'reviewer': '主任务直接复核；子代理工具请求失败，未声称完成独立人工复核',
              'visual_review': '主任务已查看检修厂房近景、内部剖切与全厂俯视图，设备和吊车有支撑连接，后退道路及两侧转角位于全部后墙之外。',
              'blueprint_sha256': sha(folder/'blueprint.json'), 'nbt_sha256': sha(folder/(NAME+'.nbt')),
              'schem_sha256': sha(folder/(NAME+'.schem')), 'controller': data['controller'],
              'controller_face': data['controller_face'], 'changes_from_v2': differences,
              'inherited_i19_blocks': len(inherited), 'i19_removed_or_changed': 0,
              'unchanged_ports': len(data['ports']), 'maintenance_workshop': data['layout_gap'], 'perimeter':data['perimeter_revision'], 'workstation_access':workstation_access,
              'all_nbt_blocks_match': True, 'all_schem_blocks_and_air_match': True,
              'all_viewer_blocks_match': True, 'protected_files_unchanged': len(protected['files']),
              'open_design_issues': [], 'not_verified': ['用户对V3整版的外观批准','游戏内成型、检修或能源功能、材料生存首建及2.9.2兼容性'],
              'boundary': '静态文件与几何核对；不等于用户批准、游戏成型、能源功能或生存可达性通过'}
    save(LOG/'final-review.json', review)
    verification.update(revision_review=review, layout_gap=data['layout_gap'])
    save(OUT/'verification.json', verification)
    record = read(folder/'设计与检查.json'); record['audit'] = verification
    save(folder/'设计与检查.json', record)
    payload['audit'] = verification
    packed = base64.b64encode(gzip.compress(json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), 9)).decode('ascii')
    (folder/'data.js').write_text('/* I20检修厂房与外围路V3；建筑表达不代表真实检修功能。 */\nwindow.HK3_PAYLOAD='+json.dumps(packed)+';', encoding='utf-8')
    evidence = OUT/'评审依据'; evidence.mkdir(exist_ok=True)
    for name in ('rules-read.json', 'final-review.json', 'workstation-access.json'):
        shutil.copy2(LOG/name, evidence/name)
    shutil.copy2(ROOT/'logs/i20-next-candidate-20261023/material-tooling-audit.json', evidence/'material-tooling-audit.json')
    save(evidence/'保护文件复核.json', {'time': now.isoformat(), 'checked': len(protected['files']), 'changed': changed})
    for name in ('build_i20_qsv_second_unit_v1.py', 'build_i20_qsv_inherited_controller_v2.py',
                 'build_i20_qsv_maintenance_v3.py', 'package_i20_qsv_candidate_v3_20261023.py', 'finalize_i20_maintenance_v3_20261023.py'):
        shutil.copy2(ROOT/'tools/structure_delivery'/name, OUT/'生成脚本'/name)
    shutil.copy2(ROOT/'tools/structure_delivery/package_integration_review.mjs', OUT/'生成脚本/package_integration_review.mjs')
    obsolete = OUT/'生成脚本/package_i20_qsv_candidate_20261023.py'
    if obsolete.is_file(): obsolete.unlink()
    page = folder/'三维评审.html'
    page.write_text(page.read_text(encoding='utf-8').replace('全部21形态', 'I20交付总览').replace(
        'href="../index.html#i20"', 'href="../index.html"'), encoding='utf-8')
    assert 'undefined' not in page.read_text(encoding='utf-8')
    manifest = read(OUT/'manifest.json'); manifest.update(finalized_at=now.isoformat(), revision_review=review)
    save(OUT/'manifest.json', manifest)
    broken = []
    for page in OUT.rglob('*.html'):
        for link in re.findall(r'(?:href|src)="([^"]+)"', page.read_text(encoding='utf-8')):
            relative = link.split('#')[0].split('?')[0]
            if relative and '://' not in relative and not relative.endswith('.zip') and not (page.parent/relative).resolve().is_file():
                broken.append([str(page), link])
    assert not broken, broken
    identities = {p.relative_to(OUT).as_posix(): {'bytes': p.stat().st_size, 'sha256': sha(p)}
                  for p in sorted(OUT.rglob('*')) if p.is_file() and p.name != '交付文件清单.json'}
    save(OUT/'交付文件清单.json', {'time': now.isoformat(), 'approval': '待用户审批',
        'deployment_eligible': False, 'open_design_issues': review['open_design_issues'], 'files': identities})
    archive = OUT.with_suffix('.zip')
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
        for p in sorted(OUT.rglob('*')):
            if p.is_file(): bundle.write(p, p.relative_to(OUT))
    with zipfile.ZipFile(archive) as bundle:
        assert bundle.testzip() is None
        assert all(bundle.read(n) == (OUT/n).read_bytes() for n in bundle.namelist())
    quote = '那要不你补一个检修厂房进去，刚好这个位置也没啥东西放，然后还有就是这个位置可能要拖后几个，我发个图给你，然后用红色圈圈给你看；这玩意应该是将厂房包进去的'
    topic = 'I20补建检修厂房与南侧外围路后退'
    discussion = ROOT/'doc/HK3GTL-内测5/讨论记录'/(now.strftime('%Y-%m-%d_%H-%M-%S')+'_'+topic+'.html')
    assert not discussion.exists()
    discussion.write_text(f"""<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>{topic}</title><style>body{{max-width:1050px;margin:35px auto;font:16px/1.9 'Microsoft YaHei';color:#243c48}}code{{overflow-wrap:anywhere}}</style><h1>{topic}</h1><p>记录时间：{now.isoformat()}，Asia/Hong_Kong；用户消息精确时间未知。</p>
<h2>用户明确要求</h2><blockquote>{html.escape(quote)}</blockquote><p>附图红圈位于最南侧灰色外围道路，要求向后退几格以将厂房包进去；同意在V2的西南空区补建检修厂房。覆盖上一轮该空区用途待定、暂不改填的当前状态。原位主控及系列继承决定继续有效。</p>
<h2>本轮实际完成</h2><p>新建I20 V3候选，XYZ271×155×233，实体{len(current):,}块。QSV检修厂房X12–103/Z186–220，最高屋顶Y37；增加门式框架、低拱屋顶及天窗、连续轨梁和桥式吊车、中央拆装床、三组泵转子检修工位、备件架和东侧仪控连廊。</p><p>南侧道路从Z218–222向后退10格至Z228–232，西/东两侧接长闭合；全部厂房最大后墙Z222，墙外Z223–227留5格连续净空维护带。扩展尺寸来自有用途的道路和维护空间。主控仍[95,3,20]朝北，I19全部256,075块原位原状态、16个接口不变。</p><p>与I20 V2相比，新增{len(added):,}、删除{len(removed):,}、替换{len(replacements):,}块；删除仅为开启I20新增仪控厅西墙连廊门洞，替换仅涉及原南路和新增厂房周边地面的用途重排，不触动I19。</p>
<h2>验证与未验收</h2><p>NBT/Sponge含空气、三维载荷全量逐格一致；单一六面连通、13条通道净空、17个原主控/接口操作位及4个检修工位静态步行可达，后墙维护带/南路/转角地面与净空核对。已直接查看检修厅内外及全厂俯视图。子代理工具请求失败，未声称独立人工复核。{len(protected['files'])}份前版交付/正式资源/实例文件身份保持。</p><p>本轮是用户明确授权修改，并非对修改后V3整版外观的最终批准；候选未计入新批准批次、未正式接入，未增加模组修订号或改动实例。建筑设备无真实检修能力；真实控制器/Pattern、能源及材料生存首建、游戏运行与2.9.2兼容性尚未验收。满五台先实装2.9、负责人升级后验2.9.2的决定持续有效。</p>
<h2>相关记录</h2><p><a href="../../../deliveries/{OUT.name}/index.html">V3交付</a> · <a href="../../../logs/i20-maintenance-v3-20261023/final-review.json">实际验证</a> · <a href="2026-10-23_19-44-46_I20继承I19主控位置与新增空区原因核对.html">V2讨论及本轮覆盖关系</a></p><p>变更#1：新增检修厂房、内部设备、外围后路和连廊；删除西墙门洞位置；修改道路布局；用途为落实附图要求。ZIP SHA256：<code>{sha(archive)}</code>。</p></html>""",encoding='utf-8')
    result = {'time': now.isoformat(), 'out': str(OUT), 'blueprint_sha256': review['blueprint_sha256'],
              'controller': data['controller'], 'blocks': len(current), 'ports': len(data['ports']),
              'changes_from_v2': differences, 'protected_files_unchanged': len(protected['files']),
              'zip': str(archive), 'zip_sha256': sha(archive), 'zip_all_bytes_verified': True,
              'instance_changed': False, 'formal_resources_changed': False, 'candidate_approved': False,
              'empty_area_modified': True, 'discussion': str(discussion)}
    save(LOG/'final-verification.json', result)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__': main()
