# -*- coding: utf-8 -*-
"""变更记录 #1 · 2026-09-24 00:04:00 · 修订63。
独立逐格核对源蓝图、占地表、实际Java字符串和NBT，接口以外禁止增减方块。
Independently compare approved sources, atlas, Java aisles and NBT; only explicit ports may differ.
"""
from pathlib import Path
import json,re,hashlib
import nbtlib

root=Path(__file__).resolve().parents[1]
base=root/'src/main/resources/data/hk3gtl/structures/approved'
page=next((root/'doc').rglob('*69*v2.html')).read_text(encoding='utf8')
atlas={r['id']:r for r in json.JSONDecoder().raw_decode(page.split('const machines=')[1])[0]}
for key,cls,aid,axes in [('i01','Hk3I01CollectionPatternImpl','I01-1','LEFT, UP, FRONT'),('i02','Hk3I02SpectrumPatternImpl','I02','RIGHT, UP, BACK')]:
    m=json.loads((base/(key+'.json')).read_text(encoding='utf8'))
    raw=(root/m['source']).read_bytes();assert hashlib.sha256(raw).hexdigest()==m['sha256']
    src=json.loads(raw);original={tuple(b['pos']):b['block'] for b in src['blocks']}
    pattern=(root/'src/main/java/com/sirin/hk3gtl/common/multiblock/pattern'/(cls+'.java')).read_text(encoding='utf8')
    assert f'FactoryBlockPattern.start({axes})' in pattern
    aisles=[re.findall(r'"([#A-Za-z]+)"',v) for v in re.findall(r'\.aisle\((.*?)\)',pattern,re.S)]
    assert aisles==m['aisles']
    legend=dict(re.findall(r"\.where\('([A-Z])', Predicates.blocks\(Hk3StructureBlocks.require\(\"([^\"]+)\"\)\)\)",pattern))
    assert legend==m['legend']
    ports={tuple(p['pos']):p['symbol'] for p in m['ports']};ports[tuple(m['controller'])]='S'
    template=nbtlib.load(base/(key+'.nbt'))
    actual={tuple(map(int,b['pos'])):template['palette'][int(b['state'])] for b in template['blocks']}
    w,h,d=m['size'];assert [w,d,h]==atlas[aid]['size'] and len(actual)==w*h*d
    for z in range(d):
        for y in range(h):
            for x in range(w):
                pos=(x,y,z);symbol=aisles[z][y][x];state=actual[pos]
                if pos in ports:
                    assert symbol==ports[pos] and state['Name']!='minecraft:air'
                    if symbol=='S':
                        assert state['Name']=='hk3gtl:'+m['machine'] and state['Properties']['facing']==m['front']
                else:
                    block,_,props=original.get(pos,'minecraft:air').partition('[')
                    assert ('minecraft:air' if symbol=='#' else legend[symbol])==block==state['Name'],pos
                    if props:
                        assert dict(state['Properties'])==dict(p.split('=') for p in props.rstrip(']').split(',')),pos
    assert sum(r.count('S') for a in aisles for r in a)==1
    print(key,'PASS',w*h*d,'cells: approved blueprint, atlas, Java Pattern, NBT states, controller and ports')
