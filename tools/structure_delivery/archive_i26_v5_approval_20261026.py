# -*- coding: utf-8 -*-
"""I26 V5 外观确认及真实材质完整全景；保留体积规则冲突，不接入实例。"""
from __future__ import annotations

import base64
import copy
import datetime as dt
import gzip
import hashlib
import io
import json
import re
import shutil
import zipfile
from collections import Counter
from pathlib import Path

import nbtlib
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageEnhance

import archive_i23_v8_approval_20261025 as common
import build_i26_kwaichung_terminal_v2_20261026 as render_tools

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'deliveries/I26_葵涌码头_疏散货柜与随机集卡运营场景_V5_20261026'
ARCHIVES = ROOT / 'deliveries/多方块确认归档'
INDEX = ARCHIVES / '当前归档索引.json'
QUOTE = '很好很好，I26就用这个\n你给我渲染一个能完整看到整座I26的图片\n然后接下来咱们去I27'
APPROVED_AT = '2026-10-26T16:39:15.933+08:00'
DIALOGUE = ROOT / 'doc/HK3GTL-内测5/完整对话归档/2026-10-26_16-39-15_I26V5确认全景渲染与I27启动_2a95a0cbf8.html'
DISCUSSION = ROOT / 'doc/HK3GTL-内测5/讨论记录/2026-10-26_16-39-15_I26V5确认全景渲染与I27启动.html'
SCOPE = 'I26 V5 葵涌码头疏散货柜与随机集卡运营场景的建筑外观及对应结构文件。用户明确选用该版；体积递增项仍未达标，不据此宣称规则全通过、正式Pattern或游戏运行验收，也不接入实例。'


def read_and_verify():
    manifest = json.loads((SOURCE / 'manifest.json').read_text(encoding='utf-8'))
    check = json.loads((SOURCE / 'verification.json').read_text(encoding='utf-8'))
    nbt_path, = (SOURCE / 'i26').glob('*.nbt')
    schem_path, = (SOURCE / 'i26').glob('*.schem')
    assert common.digest(nbt_path) == check['nbt_schem_sha256']['nbt']
    assert common.digest(schem_path) == check['nbt_schem_sha256']['schem']
    nbt = nbtlib.load(nbt_path)
    states = [common.state_name(p) for p in nbt['palette']]
    cells = {}
    for block in nbt['blocks']:
        pos = tuple(map(int, block['pos']))
        assert pos not in cells
        cells[pos] = states[int(block['state'])]
    size = list(map(int, nbt['size']))
    del nbt
    assert size == manifest['size'] == [333, 110, 301]
    assert len(cells) == manifest['blocks'] == 606452
    assert len(set(cells.values())) == manifest['unique_materials'] == 34
    assert [min(p[i] for p in cells) for i in range(3)] == [0, 0, 0]
    assert [max(p[i] for p in cells) + 1 for i in range(3)] == size
    assert Counter(cells.values()) == check['palette']
    assert cells[tuple(manifest['controller'])] == 'minecraft:diamond_block'
    assert manifest['controller'] == [166, 76, 119]
    assert sum(s == 'minecraft:diamond_block' for s in cells.values()) == 1
    assert {p for p, s in cells.items() if s == 'hk3gtl:industrial_port_casing'} == {tuple(p['pos']) for p in manifest['ports']}
    assert len(manifest['ports']) == 8
    schematic = nbtlib.load(schem_path)
    assert [int(schematic[k]) for k in ('Width', 'Height', 'Length')] == size
    palette = {str(k): int(v) for k, v in schematic['Palette'].items()}
    dense = np.zeros(np.prod(size), dtype=np.uint8)
    for (x, y, z), state in cells.items():
        dense[(y * size[2] + z) * size[0] + x] = palette[state]
    assert np.array_equal(dense, np.asarray(schematic['BlockData']).view(np.uint8))
    del schematic, dense
    encoded, = re.findall(r'window\.HK3_PAYLOAD\s*=\s*"([^"]+)"', (SOURCE / 'i26/data.js').read_text(encoding='utf-8'))
    payload = json.loads(gzip.decompress(base64.b64decode(encoded, validate=True)))
    assert payload['blockCount'] == len(cells)
    data = dict(payload['data'], blocks=[{'pos': list(p), 'state': s} for p, s in cells.items()])
    assert payload['palette'] == states
    assert payload['surfaceGroups'] == render_tools.build_surface_groups(data, states)
    assert check['instance_proof']['instance_version'] == '2.9.2'
    assert check['rule_conflicts'] == ['volume'] and not check['passed']
    assert check['rule_exceptions']['height']['actual'] == 110
    return manifest, check, data, payload['materials']


def panorama(data, materials):
    source = (ROOT / 'tools/structure_delivery/package_l1_review89.py').read_text(encoding='utf-8')
    source = 'def render_iso(data,materials,out):' + source.split('def render_iso(data,materials,out):', 1)[1].split('\ndef main(', 1)[0]
    source = source.replace('scale=16;sy=8;sz=16', 'scale=7;sy=3.5;sz=7')
    source = source.replace("image.convert('RGB').save(out/'等轴预览.png')", '')
    scope = dict(Image=Image, ImageDraw=ImageDraw, ImageEnhance=ImageEnhance, io=io, base64=base64)
    exec(source, scope)
    image = scope['render_iso'](data, materials, SOURCE)
    background = Image.new('RGB', image.size, (19, 26, 40))
    bounds = ImageChops.difference(image, background).getbbox()
    assert bounds
    # 按实际像素裁掉空白，不裁建筑；统一补足120像素四边留白。
    picture = image.crop(bounds)
    canvas = Image.new('RGB', (picture.width + 240, picture.height + 240), (19, 26, 40))
    canvas.paste(picture, (120, 120))
    path = SOURCE / '整座I26完整全景.png'
    canvas.save(path)
    assert canvas.width > 4500 and canvas.height > 2500
    return {'path': str(path), 'pixels': list(canvas.size), 'sha256': common.digest(path),
            'source': '与确认结构逐格一致的真实贴图等轴投影；未裁建筑，无文字水印。',
            'whole_structure_included': True, 'margin_pixels': 120}


def main():
    before = INDEX.read_bytes()
    index = json.loads(before)
    assert not any(row['id'] == 'I26' for row in index['entries']), '拒绝重复归档 I26'
    assert index['pending_batch']['approved_machine_ids'] == ['I22', 'I23', 'I24']
    hashes_before_render = common.file_hashes(SOURCE)
    manifest, check, data, materials = read_and_verify()
    photo = panorama(data, materials)
    assert all(common.digest(SOURCE / k) == v for k, v in hashes_before_render.items())
    hashes = common.file_hashes(SOURCE)
    now = dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))
    snapshot = ARCHIVES / f'{now:%Y%m%d_%H%M%S_%f}_batch-07_04of05_I26_V5_QAV_外观已确认'
    snapshot.mkdir(exist_ok=False)
    evidence = snapshot / 'evidence'; evidence.mkdir()
    (evidence / 'previous-current-index.json').write_bytes(before)
    shutil.copy2(__file__, evidence / Path(__file__).name)
    for name in ('系统角色设定.md', '崩坏三-gtl (hk3gtl) 项目规则.md', '当前多方块设计规则.md', '巨构提示词.txt'):
        shutil.copy2(ROOT / 'rule' / name, evidence / name)
    target = snapshot / SOURCE.name
    shutil.copytree(SOURCE, target)
    assert common.file_hashes(target) == hashes
    pending = dict(index['pending_batch'], approved_machine_ids=['I22', 'I23', 'I24', 'I26'], count=4,
                   deployment_eligible=False, deployment_blockers=['batch-07当前为4/5，未达到五台接入门槛。',
                   'I26仅记录外观选用，体积递增项仍未满足；未声称整体规则或游戏验收通过。'])
    checks = dict(size_xyz=manifest['size'], actual_bounds_xyz=manifest['size'], block_count=len(data['blocks']),
                  material_count=34, controller=manifest['controller'], ports=8, nbt_schematic_per_block_equal=True,
                  nbt_viewer_surface_equal=True, source_hashes=check['nbt_schem_sha256'], panorama=photo,
                  height_exception=check['rule_exceptions']['height'], unresolved_rules=['volume'],
                  full_rules_passed=False, geometry_passed=True)
    row = dict(id='I26', key='i26', candidate_key='i26', approved_version='V5',
               candidate_version=manifest['candidate_version'], target_voltage_appearance='QAV',
               status='appearance_approved_archived_rule_conflict', approval_quote=QUOTE,
               approval_scope=SCOPE, approved_at=APPROVED_AT, source=str(SOURCE), archive=str(target),
               discussion_record=str(DISCUSSION), dialogue_archive=str(DIALOGUE),
               counts_as_new_machine=True, structure_checks=checks, source_candidate_approved_field=False,
               formal_resource_present=False, game_files_installed=False, game_verified=False,
               size_xyz=manifest['size'], controller=manifest['controller'], port_count=8, block_count=len(data['blocks']))
    approval = dict(record=1, created_at=now.isoformat(), timezone='Asia/Hong_Kong',
                    original_user_message_time=APPROVED_AT, original_time_note='取自主会话本地JSONL用户消息时间；建档时间另记。',
                    entries=[row], accepted_design_scope=SCOPE, source_files_sha256=hashes,
                    rule_conflicts=check['rule_conflicts'], rule_exceptions=check['rule_exceptions'],
                    pending_batch_after_archive=pending, previous_index_sha256=hashlib.sha256(before).hexdigest(),
                    source_metadata_boundary='来源待审及approved=false原字节保留；外观选用另记，不将体积项改判通过。',
                    game_files_installed=False, game_verified=False)
    common.write_json(snapshot / '确认与校验清单.json', approval)
    (snapshot / '确认接入.html').write_text(f'<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>I26 V5外观确认</title><style>body{{max-width:1150px;margin:32px auto;font:16px/1.8 system-ui;background:#131a28;color:#e4edf7}}img{{width:100%}}a{{color:#90d8e0}}</style><h1>I26 V5 外观已确认</h1><p>{SCOPE}</p><p>333×301×110格（宽×长×高），606,452方块、34种材料。主控与8个接口保持；42只堆场货柜、4只车载箱、8台拖头。</p><p>batch-07外观确认计数4/5。高度110格获批逐案例外；实体包围盒体积11,025,630仍低于I25的11,970,190，不把外观选择推定为体积豁免。未实装。</p><p><a href="确认与校验清单.json">确认与校验清单</a> · <a href="{SOURCE.name}/i26/三维评审.html">原版三维</a></p><img src="{SOURCE.name}/整座I26完整全景.png" alt="I26完整全景"></html>', encoding='utf-8')
    bundle = snapshot.with_suffix('.zip')
    archive_hashes = common.file_hashes(snapshot)
    with zipfile.ZipFile(bundle, 'x', zipfile.ZIP_DEFLATED, compresslevel=9) as package:
        for name in archive_hashes:
            package.write(snapshot / name, name)
    zip_check = common.verify_zip(bundle, archive_hashes)
    bundle.with_suffix('.zip.sha256').write_text(zip_check['sha256'] + '\n', encoding='ascii')
    assert common.file_hashes(SOURCE) == hashes and INDEX.read_bytes() == before
    row.update(approval_manifest=str(snapshot / '确认与校验清单.json'), archive_zip=str(bundle),
               archive_zip_sha256=zip_check['sha256'], nbt_sha256=check['nbt_schem_sha256']['nbt'])
    index['entries'].append(row)
    index['approved_structure_forms'] += 1
    index.update(pending_batch=pending, updated_at=now.isoformat(), target_pack_version='2.9.2')
    index['scope'] = '既有正式形态保持；I26 V5外观已确认并归档，体积规则冲突保留，未接入实例。'
    index['batch_rule'] = '每累计5台明确批准后按归档并核定剩余规则接入增强版实例；当前batch-07为4/5。'
    index['latest_approval_snapshot'] = dict(snapshot=str(snapshot), zip=str(bundle), zip_sha256=zip_check['sha256'])
    index.setdefault('historical_previous_indices', []).append(copy.deepcopy(index.get('previous_index', {})))
    index['previous_index'] = dict(preserved_copy=str(evidence / 'previous-current-index.json'), sha256=hashlib.sha256(before).hexdigest())
    index.setdefault('_change_records', []).append(dict(record=len(index['_change_records']) + 1, time=now.isoformat(),
        reason='用户明确选用I26 V5并要求完整全景及继续I27', deleted='无；旧索引及候选原件均保留',
        added='I26 V5外观确认归档与高分辨率全景', modified='外观确认batch-07推进4/5；体积未达标状态保留',
        purpose='保存外观决定并区分规则核定、正式Pattern及游戏验收'))
    common.write_json(INDEX, index)
    print(json.dumps(dict(snapshot=str(snapshot), zip=str(bundle), zip_sha256=zip_check['sha256'], panorama=photo,
                         pending_batch=pending, source_original_files_unchanged=True, verified=True), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
