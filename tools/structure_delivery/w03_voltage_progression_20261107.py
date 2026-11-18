# -*- coding: utf-8 -*-
"""CIV候选比较全部低阶批准形态；旧I22格式独立流式复核，禁止遗漏WSV。"""
import copy,gzip,json,math,struct
import numpy as np
from w02_voltage_progression_20261107 import ROOT,INDEX,MAPPING,read,resolve,progression as wsv_progression
from i41_voltage_progression_20261028 import TIERS,_mapping
from i34_open_observatory_export_20261027 import digest


def approved_nbt(entry):
    if 'approved_nbt' in entry:return resolve(entry['approved_nbt'])
    files=list(resolve(entry['archive']).rglob('*.nbt'))
    assert len(files)==1,files
    assert digest(files[0])==entry['nbt_sha256']
    return files[0]


def legacy_metrics(entry):
    from build_batch10_approved_resources_20261030 import header,chunks,nbt
    source=approved_nbt(entry);raw=gzip.decompress(source.read_bytes())
    assert digest(source)==entry.get('approved_nbt_sha256',entry['nbt_sha256'])
    fields,start,count=header(raw);size=list(struct.unpack_from('>iii',raw,fields['size'][0]+5))
    states=nbt.palette(raw,fields['palette']);counts=np.zeros(len(states),np.int64)
    seen=np.zeros(math.prod(size),bool);low=np.asarray(size);high=np.zeros(3,int)
    for _,_,_,positions,ids,_ in chunks(raw,start,count):
        assert ((positions>=0)&(positions<size)).all()
        linear=(positions[:,1].astype(np.int64)*size[2]+positions[:,2])*size[0]+positions[:,0]
        assert len(np.unique(linear))==len(linear) and not seen[linear].any();seen[linear]=True
        counts+=np.bincount(ids,minlength=len(states));low=np.minimum(low,positions.min(0));high=np.maximum(high,positions.max(0))
    assert low.tolist()==[0,0,0] and (high+1).tolist()==size==entry['size_xyz']
    assert int(counts.sum())==count==entry['block_count']==int(seen.sum())
    ordinary=sorted({s.split('[',1)[0] for s,n in zip(states,counts) if n and s not in {'minecraft:diamond_block','hk3gtl:industrial_port_casing'}})
    return dict(blocks=count,materials=len(ordinary),volume=math.prod(size),height=size[1]),ordinary,size


def progression(metrics):
    lower=wsv_progression(metrics);rows=copy.deepcopy(lower['lower_forms'])
    index=read(INDEX);entries={e['id']:e for e in index['entries']}
    mapping=_mapping(MAPPING.read_bytes());mapping.update({f'MX-C0{i}':'MAX' for i in range(1,5)})
    assert mapping['W03']=='CIV'
    expected={k for k in entries if TIERS[mapping[k]]<TIERS['CIV']}
    watched={resolve(p):s for p,s in lower['hashed_files'].items()}
    for identity in sorted(expected-{r['id'] for r in rows}):
        e=entries[identity];folder=resolve(e['archive']);nbt=approved_nbt(e)
        for p,sha in [(nbt,e.get('approved_nbt_sha256',e['nbt_sha256'])),(resolve(e['archive_zip']),e['archive_zip_sha256'])]:
            assert digest(p)==sha;watched[p]=sha
        watched[resolve(e['approval_manifest'])]=digest(resolve(e['approval_manifest']))
        if identity=='I22':values,ordinary,size=legacy_metrics(e)
        else:
            verify=read(folder/'verification.json');manifest=read(folder/'manifest.json')
            assert verify['readback']['geometry_nbt_schematic_per_block_equal']
            assert digest(nbt)==verify['nbt_schem_sha256']['nbt']
            size=verify['size_xyz'];assert size==e['size_xyz']==manifest['size']
            ordinary=sorted({s.split('[',1)[0] for s in verify['palette'] if s not in {'minecraft:diamond_block','hk3gtl:industrial_port_casing'}})
            assert sum(verify['palette'].values())==verify['blocks']==e['block_count']
            values=dict(blocks=verify['blocks'],materials=len(ordinary),volume=math.prod(size),height=size[1])
            for p in (folder/'verification.json',folder/'manifest.json'):watched[p]=digest(p)
        rows.append(dict(id=identity,key=e['key'],voltage=mapping[identity],tier=TIERS[mapping[identity]],actual_xyz=size,
            metrics=values,ordinary_states=ordinary,approved_nbt=str(nbt),approved_nbt_sha256=digest(nbt),
            approval_quote=e['approval_quote'],evidence_refreshed=True,independent_nbt_readback=identity=='I22'))
    assert {r['id'] for r in rows}==expected and len(rows)==56
    maxima={k:dict(value=max(r['metrics'][k] for r in rows),ids=[r['id'] for r in rows if r['metrics'][k]==max(p['metrics'][k] for p in rows)]) for k in metrics}
    passes={k:metrics[k]>v['value'] for k,v in maxima.items()};assert all(passes.values()),(metrics,maxima)
    assert all(digest(p)==s for p,s in watched.items())
    return dict(passed=True,target_voltage='CIV',target_tier=TIERS['CIV'],metrics=metrics,passes=passes,
        lower_form_count=len(rows),lower_forms=rows,lower_maxima=maxima,hashed_files={str(p):s for p,s in watched.items()},
        approval_index_sha256=digest(INDEX),voltage_mapping_sha256=digest(MAPPING),
        comparison='按CIV比较全部56个已批准低阶形态，包含新批准W02 V2和WSV I22/I43；同阶S05及未批准候选不混入。',
        material_count_scope='普通方块ID去重，排除主控和接口标记；HCV仅为外观主材，运行仍为CIV。')
