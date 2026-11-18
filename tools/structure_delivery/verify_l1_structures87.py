# -*- coding: utf-8 -*-
"""修订87：独立核对正式JSON、NBT和Sponge文件的逐格内容、端口与空腔，不写入游戏实例。"""
from pathlib import Path
from datetime import datetime
from collections import Counter
import hashlib
import json
import nbtlib as n
from build_l1_approved87 import connected
from package_i03_review import validate_paths

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / 'src/main/resources/data/hk3gtl'
OUT = ROOT / 'doc/HK3GTL-内测5/03_机器结构/L1稳定与再生_修订87'

def state(obj):
    properties = obj.get('Properties', {})
    return str(obj['Name']) + ('[' + ','.join(str(k)+'='+str(v) for k,v in sorted(properties.items())) + ']' if properties else '')

def sponge_cells(path):
    data = n.load(path)
    assert data.root_name == 'Schematic' and int(data['Version']) == 2 and int(data['DataVersion']) == 3465
    w,h,d = [int(data[key]) for key in ('Width','Height','Length')]
    palette = {int(v):str(k) for k,v in data['Palette'].items()}
    assert palette[0] == 'minecraft:air'
    values=[]; value=shift=0
    for signed in data['BlockData']:
        b=int(signed)&255;value|=(b&127)<<shift
        if b&128:shift+=7
        else:values.append(value);value=shift=0
    assert len(values)==w*h*d and shift==0
    cells={}
    for i,v in enumerate(values):
        assert v in palette
        if v: cells[i%w,i//(w*d),i//w%d]=palette[v]
    return [w,h,d],cells

report=[]
for key,expected_size,controller in [('i04',[23,27,23],'liquid_honkai_stabilization_tower'),
        ('i05',[27,19,23],'stabilization_medium_regeneration_tower')]:
    data=json.loads((RES/f'approved_architecture/{key}.json').read_text(encoding='utf-8'))
    assert data['size']==expected_size and data['controller']==[8,2,2]
    cells={tuple(v['pos']):v['state'] for v in data['blocks']}
    assert len(cells)==len(data['blocks'])
    assert all(all(0<=p[i]<expected_size[i] for i in range(3)) for p in cells)
    assert all(not v.startswith('hk3gtl:') for v in cells.values())
    assert Counter(cells.values())['minecraft:diamond_block']==1
    assert Counter(cells.values())['minecraft:diamond_ore']==13
    connected(data);validate_paths(data)
    ports={tuple(p['pos']):p for p in data['ports']}
    assert len(ports)==13 and {p['id'] for p in ports.values()}=={'P1',*[f'M{i}' for i in range(1,5)],*[f'F{i}' for i in range(1,9)]}
    template=n.load(RES/f'structures/approved/{key}.nbt')
    assert list(map(int,template['size']))==expected_size
    actual={tuple(map(int,b['pos'])):state(template['palette'][int(b['state'])]) for b in template['blocks']}
    assert len(actual)==len(template['blocks']) and set(actual)==set(cells)
    expected=dict(cells)
    expected[tuple(data['controller'])]='hk3gtl:'+controller+'[facing=north]'
    for pos,p in ports.items():
        pid=p['id']
        if pid=='P1':expected[pos]='gtceu:max_machine_casing'
        else:
            fluid=pid.startswith('F');output=int(pid[1:])>(4 if fluid else 2)
            expected[pos]='gtceu:max_'+('output' if output else 'input')+('_hatch' if fluid else '_bus')+'[facing='+p['face']+']'
    assert actual==expected, key
    folder=OUT/key
    assert json.loads((folder/'blueprint.json').read_text(encoding='utf-8'))==data
    for suffix,target in [('markers',cells),('production',actual)]:
        size,decoded=sponge_cells(folder/(data['name']+'-'+suffix+'.schem'))
        assert size==expected_size and decoded==target,(key,suffix)
    assert (folder/(data['name']+'.nbt')).read_bytes()==(RES/f'structures/approved/{key}.nbt').read_bytes()
    metadata=json.loads((RES/f'structures/approved/{key}.json').read_text(encoding='utf-8'))
    assert metadata['sha256']==hashlib.sha256((RES/f'approved_architecture/{key}.json').read_bytes()).hexdigest()
    assert all(v['complete_cube'] for v in metadata['material_evidence'].values())
    report.append({'id':key,'size':expected_size,'blocks':len(cells),'ports':len(ports),'exact_json_nbt_sponge_match':True})

# I03默认模板必须能接收净化的四种流体输出，几何与获批资源仍相同。
data=json.loads((RES/'approved_architecture/i03.json').read_text(encoding='utf-8'))
template=n.load(RES/'structures/approved/i03.nbt')
actual={tuple(map(int,b['pos'])):state(template['palette'][int(b['state'])]) for b in template['blocks']}
fluid_counts=Counter(actual[tuple(p['pos'])].split('[')[0] for p in data['ports'] if p['id'].startswith('F'))
assert fluid_counts=={'gtceu:max_input_hatch':2,'gtceu:max_output_hatch':4},fluid_counts
java=ROOT/'src/main/java/com/sirin/hk3gtl/common/multiblock/pattern'
pattern=(java/'Hk3LiquidLinePatterns.java').read_text(encoding='utf-8')
for kind,key in [('STABILIZATION','i04'),('REGENERATION','i05')]:
    assert f'if(kind==Hk3LiquidLineLayout.Kind.{kind})return Hk3ApprovedArchitecturePatterns.create(definition,"{key}");' in pattern
result={'time':datetime.now().isoformat(),'checks':report,'i03_default_fluid_ports':dict(fluid_counts),
    'scope':'逐格资源、NBT与Sponge静态一致性；不代表游戏注册、加载或成型验收','game_tested':False}
(ROOT/'logs/revision87/structure-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
