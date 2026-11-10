# -*- coding: utf-8 -*-
"""修订70：独立比较批准建筑和正式模板，只有主控／接口可以替换；导出真实仓室投影。"""
from pathlib import Path
import json, hashlib, shutil
import nbtlib as n
import package_i03_review as package

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'doc/HK3GTL-内测5/03_机器结构/初期四机外观重设计_v2'
OUT=BASE/'正式结构_修订70'
OUT.mkdir(exist_ok=True)
INSTANCE=Path.home()/'AppData/Roaming/PrismLauncher/instances/GregTech-Leisure-1.4.5.2/minecraft'
IDS={'i01':'i01_honkai_collection_tower','i02':'i02_spectrum_analysis_array','i03':'liquid_honkai_fractionation_center','s01':'abyss_research_analysis_matrix'}
report=[]
for key,controller in IDS.items():
    approved=json.loads((BASE/key/'blueprint.json').read_text(encoding='utf-8'))
    data=json.loads((ROOT/f'src/main/resources/data/hk3gtl/approved_architecture/{key}.json').read_text(encoding='utf-8'))
    assert data==approved
    template_path=ROOT/f'src/main/resources/data/hk3gtl/structures/approved/{key}.nbt'
    template=n.load(template_path)
    assert list(map(int,template['size']))==data['size']
    cells={tuple(b['pos']):b['state'] for b in data['blocks']};ports={tuple(p['pos']):p for p in data['ports']}
    real=[];seen=set();marker_ids={'minecraft:diamond_block','minecraft:diamond_ore'}
    for block in template['blocks']:
        pos=tuple(map(int,block['pos']));state=template['palette'][int(block['state'])];name=str(state['Name'])
        props={str(k):str(v) for k,v in state.get('Properties',{}).items()}
        value=name+('['+','.join(k+'='+v for k,v in props.items())+']' if props else '')
        assert pos not in seen;seen.add(pos)
        assert name not in marker_ids
        if pos==tuple(data['controller']):assert name=='hk3gtl:'+controller and props['facing']=='north'
        elif pos in ports:
            port=ports[pos];pid=port['id']
            if key=='s01' or pid=='P1' or (key=='i01' and pid=='M2'):assert name=='gtceu:max_machine_casing'
            else:
                assert props['facing']==port['face']
                assert name.startswith('gtceu:max_')
                assert name.endswith('_hatch' if pid.startswith('F') else '_bus')
        else:assert value==cells[pos],(key,pos,value,cells[pos])
        real.append({'pos':list(pos),'state':value})
    assert seen==set(cells)
    actual={**data,'name':f'hk3gtl-{key}-production-r70','blocks':real}
    package.OUT=OUT;package.NAME=actual['name']
    schem,_,_=package.write_sponge(actual)
    shutil.copy2(template_path,OUT/(actual['name']+'.nbt'))
    for directory in ['schematics','config/worldedit/schematics']:
        dest=INSTANCE/directory/schem.name;dest.parent.mkdir(parents=True,exist_ok=True)
        if dest.exists():assert dest.read_bytes()==schem.read_bytes(),'正式投影存在不同内容'
        else:shutil.copy2(schem,dest)
    metadata={'revision':70,'source':str((BASE/key/'blueprint.json').relative_to(ROOT)).replace('\\','/'),
              'sha256':hashlib.sha256((BASE/key/'blueprint.json').read_bytes()).hexdigest(),
              'size':data['size'],'controller':data['controller'],'machine':'hk3gtl:'+controller,'ports':data['ports']}
    (ROOT/f'src/main/resources/data/hk3gtl/structures/approved/{key}.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding='utf-8')
    report.append({'key':key,'size':data['size'],'cells':len(seen),'ports':len(ports),'sha256':hashlib.sha256(schem.read_bytes()).hexdigest(),'file':schem.name})
(OUT/'正式模板逐格核验.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
