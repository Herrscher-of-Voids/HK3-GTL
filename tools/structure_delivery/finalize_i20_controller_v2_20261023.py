# -*- coding: utf-8 -*-
"""封装I20原位主控修订，逐格核对差异并如实记录空区仍待处理。

【文件职责】读取V1/V2/I19和导出文件，验证唯一墙面改动、主控继承及保护文件身份。
【变更记录 #1】2026-10-23 19:44:05（独立候选封装，不增加模组修订号）
删除：无。新增：逐格差异、原位主控及空区A核对、文件清单、ZIP和讨论记录。
修改：候选明确说明空区尚未改动，不把用户询问解释为新增设施批准。
用途：保证页面、三维载荷和结构文件一致，保留前阶段和V1原件。
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

from build_i20_qsv_inherited_controller_v2 import OUT, LOG, ROOT, NAME, BASE


def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p, value): p.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def mapping(data): return {tuple(b['pos']): b['state'] for b in data['blocks']}


def main():
    now = dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))
    folder = OUT/'i20'
    source = ROOT/'deliveries/I20_中型崩坏能反应堆_双岛复合厂区扩建候选_V1_20261023'
    data = read(folder/'blueprint.json')
    prior = read(source/'i20/blueprint.json')
    old = read(BASE)
    current, previous, inherited = mapping(data), mapping(prior), mapping(old)
    assert len(current) == len(data['blocks']) == 490655
    assert current.keys() == previous.keys()
    differences = [{'pos': list(p), 'before': previous[p], 'after': s}
                   for p, s in current.items() if previous[p] != s]
    assert differences == [{'pos': [135, 3, 184], 'before': 'minecraft:diamond_block',
                             'after': 'hk3gtl:voltage_machine_casing_qsv'}], differences
    assert all(current[p] == s for p, s in inherited.items())
    assert data['controller'] == old['controller'] == [95, 3, 20]
    assert data['controller_face'] == 'north'
    assert data['controller_centering']['source_controller'] == old['controller']
    assert current[(95, 3, 20)] == 'minecraft:diamond_block'
    assert data['ports'] == prior['ports'] and len(data['ports']) == 16
    empty = [p for p in current if 6 <= p[0] <= 107 and 184 <= p[2] <= 217]
    assert not empty
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
              'visual_review': '主任务已查看实际主控近景及标注俯视图：原北墙钻石标记清楚，橙框A对应新增西南空区。',
              'blueprint_sha256': sha(folder/'blueprint.json'), 'nbt_sha256': sha(folder/(NAME+'.nbt')),
              'schem_sha256': sha(folder/(NAME+'.schem')), 'controller': data['controller'],
              'controller_face': data['controller_face'], 'changed_blocks_from_v1': differences,
              'inherited_i19_blocks': len(inherited), 'i19_removed_or_changed': 0,
              'unchanged_ports': len(data['ports']), 'empty_area_a': data['layout_gap'],
              'all_nbt_blocks_match': True, 'all_schem_blocks_and_air_match': True,
              'all_viewer_blocks_match': True, 'protected_files_unchanged': len(protected['files']),
              'open_design_issues': ['空区A尚无明确用途，本轮标注并回答原因，没有改填设施'],
              'boundary': '静态文件与几何核对；不等于用户批准、游戏成型、能源功能或生存可达性通过'}
    save(LOG/'final-review.json', review)
    verification.update(revision_review=review, layout_gap=data['layout_gap'])
    save(OUT/'verification.json', verification)
    record = read(folder/'设计与检查.json'); record['audit'] = verification
    save(folder/'设计与检查.json', record)
    payload['audit'] = verification
    packed = base64.b64encode(gzip.compress(json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), 9)).decode('ascii')
    (folder/'data.js').write_text('/* I20原位主控V2；空区A只标注未改填。 */\nwindow.HK3_PAYLOAD='+json.dumps(packed)+';', encoding='utf-8')
    evidence = OUT/'评审依据'; evidence.mkdir(exist_ok=True)
    for name in ('rules-read.json', 'final-review.json'):
        shutil.copy2(LOG/name, evidence/name)
    shutil.copy2(ROOT/'logs/i20-next-candidate-20261023/material-tooling-audit.json', evidence/'material-tooling-audit.json')
    save(evidence/'保护文件复核.json', {'time': now.isoformat(), 'checked': len(protected['files']), 'changed': changed})
    for name in ('build_i20_qsv_second_unit_v1.py', 'build_i20_qsv_inherited_controller_v2.py',
                 'package_i20_qsv_candidate_v2_20261023.py', 'finalize_i20_controller_v2_20261023.py'):
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
    quote = 'I20有两个问题，多方块控制器我希望保留在I19的对应位置，毕竟他们基本上是同一个系列的多方块结构，也就是崩坏能反应堆，然后就是我看到这个新区域里有一个空的位置，为什么要留下那一个空位置？'
    topic = 'I20继承I19主控位置与新增空区原因核对'
    discussion = ROOT/'doc/HK3GTL-内测5/讨论记录'/(now.strftime('%Y-%m-%d_%H-%M-%S')+'_'+topic+'.html')
    assert not discussion.exists()
    discussion.write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>{topic}</title><style>body{{max-width:1050px;margin:35px auto;font:16px/1.9 'Microsoft YaHei';color:#243c48}}code{{overflow-wrap:anywhere}}</style><h1>{topic}</h1><p>记录时间：{now.isoformat()}，Asia/Hong_Kong；用户消息精确时间未知。</p>
<h2>用户要求及已确认</h2><blockquote>{html.escape(quote)}</blockquote><p>I20主控保留在I19的对应位置，因属于同一反应堆系列。覆盖上一轮按I20全宽居中将主控移至[135,3,184]的方案；系列后续扩建沿用原锚点，其他独立机器要求不变。</p>
<h2>实际完成</h2><p>新建V2候选：主控恢复[95,3,20]朝北，I19原宽第96格、原主厂房北墙。新增仪控厅重复钻石标记恢复QSV墙面。相比V1只有1块状态改变，无新增或删除方块；I19全部256,075块原位原状态、16接口不变。NBT、Sponge含空气及三维载荷全量核对，232份原件/正式资源/实例文件身份未改。</p>
<h2>新增空区原因与未决事项</h2><p>最明显的是新增区域西南角A：X6–107、Z184–217，102×34=3,468格；此范围实体为0。V1南侧仪控厅从X108开始，而道路围至西端，留下无明确用途的布局空档；没有依据称为必需检修区、安全间距或I21预留。这是已识别的布局缺口，未声称合理或已修复。用户当前询问原因，未明确要求填入何种设施；本轮标注并解释，保留该区几何，后续改填或边界调整待定。若用户所指为其他孔位，需按其定位另查，不把本推定冒充用户确认。</p>
<h2>边界与相关记录</h2><p>本轮没有批准归档、正式接入、模组构建、实例写入或游戏运行验证；不计入新批准批次。满五台先装2.9、负责人升级后再验2.9.2的决定持续有效。子代理工具请求失败，本轮使用主任务直接复核，不宣称独立人工审查。</p><p><a href="../../../deliveries/{OUT.name}/index.html">V2交付与空区标注</a> · <a href="../../../logs/i20-controller-inheritance-v2-20261023/final-review.json">当前静态核对</a> · <a href="2026-10-23_18-16-56_五台批次实装复核与I20双岛扩建候选.html">被部分覆盖的V1主控决定及继续有效的批次规则</a></p><p>变更记录#1：新增V2与规则#12；删除新增厅重复主控钻石，恢复原墙；修改主控锚点；用途为同系列原位扩建；空区仅解释未改填。ZIP SHA256：<code>{sha(archive)}</code>。</p></html>''',encoding='utf-8')
    result = {'time': now.isoformat(), 'out': str(OUT), 'blueprint_sha256': review['blueprint_sha256'],
              'controller': data['controller'], 'blocks': len(current), 'ports': len(data['ports']),
              'changed_blocks_from_v1': differences, 'protected_files_unchanged': len(protected['files']),
              'zip': str(archive), 'zip_sha256': sha(archive), 'zip_all_bytes_verified': True,
              'instance_changed': False, 'formal_resources_changed': False, 'candidate_approved': False,
              'empty_area_modified': False, 'discussion': str(discussion)}
    save(LOG/'final-verification.json', result)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__': main()
