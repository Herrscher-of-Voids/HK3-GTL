# -*- coding: utf-8 -*-
"""以现役批准索引复核WSV全部低阶；旧逐格证据必须与当前文件哈希一致。"""
import copy
import json
import math
from pathlib import Path
from project_paths import project_path
from i34_open_observatory_export_20261027 import digest
from i41_voltage_progression_20261028 import TIERS,_mapping

ROOT=Path(__file__).resolve().parents[2]
INDEX=ROOT/'deliveries/多方块确认归档/当前归档索引.json'
MAPPING=ROOT/'doc/HK3GTL-内测5/02_工业计划/多方块结构电压映射提案_v1.html'


def read(p):return json.loads(p.read_text(encoding='utf-8'))


def resolve(s):
    p=project_path(s)
    return p if p.is_absolute() else ROOT/p


def progression(metrics):
    index_sha=digest(INDEX);mapping_sha=digest(MAPPING)
    index=read(INDEX);entries={e['id']:e for e in index['entries']}
    assert len(entries)==len(index['entries'])
    mapping=_mapping(MAPPING.read_bytes())
    mapping.update({f'MX-C0{i}':'MAX' for i in range(1,5)})
    assert mapping['W02']=='WSV'
    expected={k for k in entries if TIERS[mapping[k]]<TIERS['WSV']}
    source=resolve(entries['I43']['archive'])/'verification.json'
    previous=read(source)['voltage_progression'];assert previous['passed']
    # 映射文档允许正文更新；每个低阶身份仍逐项核对当次运行电压。
    rows=copy.deepcopy(previous['lower_forms']);assert len(rows)==len({r['id'] for r in rows})==47
    assert {r['id'] for r in rows}<=expected
    watched={INDEX:index_sha,MAPPING:mapping_sha,source:digest(source)}
    def verify_file(p,sha):
        assert p.is_file(),str(p)
        actual=digest(p);assert actual==sha,('批准证据变化',str(p),actual,sha)
        watched[p]=actual
    for row in rows:
        e=entries[row['id']];assert e['key']==row['key'] and e['approval_quote']==row['approval_quote']
        assert row['voltage']==mapping[e['id']]
        assert row['metrics']['materials']==len({s.split('[',1)[0] for s in row['ordinary_states']})
        assert row['metrics']['volume']==math.prod(row['actual_xyz'])
        assert row['metrics']['height']==row['actual_xyz'][1]
        if e.get('block_count') is not None:assert e['block_count']==row['metrics']['blocks']
        if 'blueprint' in row:
            verify_file(resolve(row['metadata']),row['metadata_sha256'])
            verify_file(resolve(row['blueprint']),row['blueprint_sha256'])
        else:
            verify_file(resolve(row['verification']),row['verification_sha256'])
            verify_file(resolve(row['approved_nbt']),row['approved_nbt_sha256'])
            verify_file(resolve(row['archive_zip']),row['archive_zip_sha256'])
            assert resolve(e['approved_nbt'])==resolve(row['approved_nbt'])
        row['evidence_refreshed']=True
    for identity in sorted(expected-{r['id'] for r in rows}):
        e=entries[identity];archive=resolve(e['archive'])
        verify=read(archive/'verification.json');manifest=read(archive/'manifest.json')
        assert verify.get('passed',verify.get('connected',False)) and verify['readback']['geometry_nbt_schematic_per_block_equal']
        approval=read(resolve(e['approval_manifest']))
        assert (e.get('external_approval_is_authoritative') or e.get('formal_resource_present')
            or approval.get('approved')) and e['approval_quote']
        watched[resolve(e['approval_manifest'])]=digest(resolve(e['approval_manifest']))
        palette=verify['palette'];ordinary=sorted({s.split('[',1)[0] for s in palette if s not in
            {'minecraft:diamond_block','hk3gtl:industrial_port_casing'}})
        size=verify.get('size_xyz',verify.get('actual_size_xyz'));nbt=resolve(e['approved_nbt'])
        verify_file(nbt,e['approved_nbt_sha256']);assert digest(nbt)==verify['nbt_schem_sha256']['nbt']
        verify_file(resolve(e['archive_zip']),e['archive_zip_sha256'])
        watched[archive/'verification.json']=digest(archive/'verification.json')
        watched[archive/'manifest.json']=digest(archive/'manifest.json')
        assert sum(palette.values())==verify['blocks']==e['block_count']
        assert size==e['size_xyz']==manifest['size']
        assert verify['readback']['blocks']==verify['blocks']
        rows.append(dict(id=identity,key=e['key'],voltage=mapping[identity],tier=TIERS[mapping[identity]],
            actual_xyz=size,bounds_xyz=verify.get('bounds_xyz',dict(min=[0,0,0],max=[v-1 for v in size])),
            metrics=dict(blocks=verify['blocks'],materials=len(ordinary),volume=math.prod(size),height=size[1]),
            ordinary_states=ordinary,approved_nbt=str(nbt),approved_nbt_sha256=digest(nbt),
            verification=str(archive/'verification.json'),verification_sha256=digest(archive/'verification.json'),
            approval_quote=e['approval_quote'],evidence_refreshed=True))
    assert {r['id'] for r in rows}==expected and len(rows)==53
    maxima={k:dict(value=max(r['metrics'][k] for r in rows),ids=[r['id'] for r in rows if
        r['metrics'][k]==max(p['metrics'][k] for p in rows)]) for k in metrics}
    passes={k:metrics[k]>maxima[k]['value'] for k in metrics}
    assert all(passes.values()),('WSV四项递增未通过',metrics,maxima)
    assert all(digest(p)==sha for p,sha in watched.items()),'核验期间证据变化'
    return dict(passed=True,target_voltage='WSV',target_tier=28,metrics=metrics,passes=passes,
        lower_form_count=len(rows),lower_forms=rows,lower_maxima=maxima,
        minimum_strict_metrics={k:v['value']+1 for k,v in maxima.items()},
        approval_index_sha256=index_sha,voltage_mapping_sha256=mapping_sha,
        source_audit=str(source),source_audit_sha256=digest(source),
        hashed_files={str(p):sha for p,sha in watched.items()},
        comparison='按WSV运行档位比较全部53个较低电压批准形态；排除同阶I22/I43、更高阶S05和未批准I37；HBV仅为W02外观映射。',
        material_count_scope='普通方块ID去重；排除主控与通用接口标记，不按方块状态重复计数。')
