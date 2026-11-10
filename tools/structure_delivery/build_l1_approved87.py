# -*- coding: utf-8 -*-
"""修订87：根据负责人批准方案生成I04/I05蓝图、正式NBT及Sponge投影；不写游戏实例。

输入：已批准尺寸、工艺形体、指定实例材质。输出：同源逐格资源和端口清单。
生成时核验边界、连通、检修通路、完整立方体；不把这些检查称作游戏成型。
"""
from pathlib import Path
from datetime import datetime
from collections import Counter, deque
import json
import hashlib
import shutil
import nbtlib as n
from material_resources import Resources
import package_i03_review as sponge

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'doc/HK3GTL-内测5/03_机器结构/L1稳定与再生_修订87'
LOG = ROOT / 'logs/revision87'
STAMP = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
C = 'gtceu:max_machine_casing'
H = 'gtceu:high_power_casing'
G = 'gtceu:fusion_glass'
K = 'gtceu:superconducting_coil[active=false]'
M = 'gtlcore:molecular_casing'
P = 'kubejs:neutronium_pipe_casing'
D = 'gtceu:computer_casing'
L = 'gtceu:laminated_glass'

def write(rel, value):
    path = ROOT / rel
    if path.exists():
        backup = LOG / 'backup' / rel
        if not backup.exists():
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, backup)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

class Building:
    def __init__(self, key, size, title):
        self.key, self.size, self.title = key, size, title
        self.cells, self.ports = {}, []
        self.controller = [8, 2, 2]
        self.mid = size[0] // 2
    def put(self, x, y, z, material):
        assert all(0 <= a < b for a, b in zip((x,y,z), self.size)), (x,y,z)
        self.cells[x,y,z] = material
    def box(self, lo, hi, material):
        for x in range(lo[0],hi[0]+1):
            for y in range(lo[1],hi[1]+1):
                for z in range(lo[2],hi[2]+1):
                    self.put(x,y,z,material)
    def vessel(self, cx,cz,r,bottom,top,glass,band):
        for y in range(bottom,top+1):
            for x in range(cx-r,cx+r+1):
                for z in range(cz-r,cz+r+1):
                    distance=(x-cx)**2+(z-cz)**2
                    if distance>r*r: continue
                    if y in (bottom,top): self.put(x,y,z,C)
                    elif distance>=(r-1)**2: self.put(x,y,z,band if (y-bottom)%4==0 else glass)
        for x in (cx-r+1,cx+r-1):
            self.box((x,1,cz),(x,bottom-1,cz),band)
    def ring(self,cx,cz,r,y,material):
        for x in range(cx-r,cx+r+1):
            for z in range(cz-r,cz+r+1):
                if (r-2)**2 <= (x-cx)**2+(z-cz)**2 <= r*r:
                    self.put(x,y,z,material)
    def base(self):
        w,h,d=self.size
        self.box((0,0,0),(w-1,0,d-1),C)
        # 底板的管道带和控制走廊具有明确的设备连接作用。
        accent=H if self.key=='i04' else D
        for z in range(d):
            self.put(self.mid-2,0,z,accent)
            self.put(self.mid+2,0,z,accent)
        for x in range(w):
            for z in (4,d-5): self.put(x,0,z,accent)
    def finish(self):
        w,h,d=self.size
        for x in range(self.mid-1,self.mid+2):
            for z in range(d):
                for y in range(1,4): self.cells.pop((x,y,z),None)
        # 前侧控制台与外圈服务口，所有端口面朝可步行到达的外围。
        self.box((7,1,2),(9,3,2),H if self.key=='i04' else D)
        self.put(*self.controller,'minecraft:diamond_block')
        def port(pid,x,z,face,group,purpose):
            self.box((x,1,z),(x,3,z),C)
            self.put(x,2,z,'minecraft:diamond_ore')
            self.ports.append({'id':pid,'pos':[x,2,z],'face':face,'group':group,'purpose':purpose})
        for i,x in enumerate((3,6,w-7,w-4),1):
            port('M'+str(i),x,1,'north','物品接口','默认物品'+('输入' if i<=2 else '输出')+'；同类槽可互换')
        for i,z in enumerate((5,9,14,18),1):
            port('F'+str(i),1,z,'west','流体接口','默认流体输入；同类槽可互换')
            port('F'+str(i+4),w-2,z,'east','流体接口','默认流体输出；同类槽可互换')
        port('P1',w-2,1,'north','扩展接口','可选并行仓，最多1个；不用时为MAX机壳')
        return {'name':'hk3gtl-'+self.key+'-approved-r87','title':self.title,'key':self.key,
            'size':self.size,'controller':self.controller,'entrance':[self.mid,0],
            'blocks':[{'pos':list(pos),'state':state} for pos,state in sorted(self.cells.items())],
            'ports':self.ports,'paths':[{'name':'三格宽底层检修通道','min':[self.mid-1,1,0],'max':[self.mid+1,3,d-1]}],
            '_comment':f'变更记录 #1 {STAMP}（修订87）：新增负责人批准的{self.title}；旧建筑不删除，同源用于Pattern和模板；未游戏验收。'}

def i04():
    b=Building('i04',[23,27,23],'I04 崩坏能稳定化塔')
    b.base()
    b.vessel(11,12,5,5,24,G,H)
    # 三层约束环由四条纵向立柱承托，环内横向连接中央稳定腔。
    for x,z in ((3,12),(19,12),(11,4),(11,20)):
        b.box((x,1,z),(x,24,z),H)
    for y in (9,16,23):
        b.ring(11,12,8,y,K)
        b.ring(11,12,8,y+1,H)
        b.box((3,y,12),(19,y,12),K)
        b.box((11,y,4),(11,y,20),K)
    for x in (3,19):
        b.vessel(x,12,1,4,22,G,M)
        for y in (6,12,18): b.box((x-1,y,11),(x+1,y,13),M)
        b.box((x,1,5),(x,4,12),H)
    b.box((10,25,11),(12,25,13),M)
    b.put(11,26,12,H)
    return b.finish()

def i05():
    b=Building('i05',[27,19,23],'I05 稳定介质再生中心')
    b.base()
    b.vessel(8,7,4,4,12,L,D)
    b.vessel(18,15,4,4,17,L,D)
    b.box((7,13,6),(9,13,8),D)
    b.box((17,18,14),(19,18,16),D)
    b.box((8,10,7),(18,10,7),P)
    b.box((18,10,7),(18,10,15),P)
    b.box((8,5,7),(8,5,18),P)
    b.box((5,5,18),(18,5,18),P)
    # 侧面层叠换热模块与两塔管路连通，内部留出间隙而非实心填充。
    for x in (3,5): b.box((x,1,14),(x,10,18),C)
    for y in (4,6,8,10): b.box((3,y,14),(5,y,18),P)
    b.box((3,11,14),(5,11,18),D)
    b.box((5,6,10),(8,6,10),P)
    b.box((5,6,10),(5,6,14),P)
    return b.finish()

def connected(data):
    cells={tuple(c['pos']) for c in data['blocks']}
    reached={next(iter(cells))}; queue=deque(reached)
    while queue:
        p=queue.popleft()
        for axis in range(3):
            for sign in (-1,1):
                q=list(p);q[axis]+=sign;q=tuple(q)
                if q in cells and q not in reached: reached.add(q);queue.append(q)
    assert reached==cells, ('悬空实体',list(cells-reached)[:10])

def state(value):
    name,_,props=value.partition('[')
    obj=n.Compound({'Name':n.String(name)})
    if props: obj['Properties']=n.Compound({k:n.String(v) for k,v in (p.split('=') for p in props.rstrip(']').split(','))})
    return obj

def template(data,controller):
    ports={tuple(p['pos']):p for p in data['ports']}
    palette=[];blocks=[];actual=[]
    for cell in data['blocks']:
        pos=cell['pos'];value=cell['state']
        if pos==data['controller']: value='hk3gtl:'+controller+'[facing=north]'
        elif tuple(pos) in ports:
            port=ports[tuple(pos)];pid=port['id']
            if pid=='P1': value=C
            else:
                isfluid=pid.startswith('F'); output=int(pid[1:])>(4 if isfluid else 2)
                value='gtceu:max_'+('output' if output else 'input')+('_hatch' if isfluid else '_bus')+'[facing='+port['face']+']'
        obj=state(value)
        if obj not in palette: palette.append(obj)
        blocks.append(n.Compound({'pos':n.List[n.Int](pos),'state':n.Int(palette.index(obj))}))
        actual.append({'pos':pos,'state':value})
    return n.File({'DataVersion':n.Int(3465),'size':n.List[n.Int](data['size']),
        'palette':n.List[n.Compound](palette),'blocks':n.List[n.Compound](blocks),'entities':n.List[n.Compound]([])}),actual

def main():
    resources=Resources();report=[]
    for data,controller in [(i04(),'liquid_honkai_stabilization_tower'),(i05(),'stabilization_medium_regeneration_tower')]:
        key=data['key'];folder=OUT/key;folder.mkdir(parents=True,exist_ok=True)
        connected(data);walkable=sponge.validate_paths(data)
        counts=Counter(c['state'] for c in data['blocks'])
        evidence={}
        for material in counts:
            assert not material.startswith('hk3gtl:')
            if material.startswith('minecraft:'): continue
            m=resources.material(material)
            evidence[material]={k:v for k,v in m.items() if k!='faces'}
            assert m['complete_cube']
        write(f'src/main/resources/data/hk3gtl/approved_architecture/{key}.json',data)
        write(str((folder/'blueprint.json').relative_to(ROOT)),data)
        sponge.OUT=folder;sponge.NAME=data['name']+'-markers'
        marker,_,_=sponge.write_sponge(data)
        nbt,actual=template(data,controller)
        target=ROOT/f'src/main/resources/data/hk3gtl/structures/approved/{key}.nbt'
        target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists():
            backup=LOG/'backup'/target.relative_to(ROOT);backup.parent.mkdir(parents=True,exist_ok=True)
            if not backup.exists():shutil.copy2(target,backup)
        nbt.save(target,gzipped=True)
        shutil.copy2(target,folder/(data['name']+'.nbt'))
        sponge.NAME=data['name']+'-production'
        production,_,_=sponge.write_sponge({**data,'blocks':actual})
        metadata={'revision':87,'time':STAMP,'size':data['size'],'controller':data['controller'],
            'machine':'hk3gtl:'+controller,'source':f'data/hk3gtl/approved_architecture/{key}.json',
            'sha256':hashlib.sha256((ROOT/f'src/main/resources/data/hk3gtl/approved_architecture/{key}.json').read_bytes()).hexdigest(),
            'ports':data['ports'],'materials':dict(counts),'placement':{'baseY':-60,'topY':-60+data['size'][1]-1,'origin':[0,0,0]},
            'material_evidence':evidence,'walkable_columns':walkable,'solids':len(data['blocks']),
            'game_tested':False,'deployed':False,'note':'正式NBT使用真实仓室；标记schem仅用于建筑表达；不代表游戏成型验收。'}
        write(f'src/main/resources/data/hk3gtl/structures/approved/{key}.json',metadata)
        write(str((folder/'manifest.json').relative_to(ROOT)),metadata)
        report.append({'id':key,'size':data['size'],'solids':len(data['blocks']),'ports':len(data['ports']),'walkable':walkable,
            'production_schem_sha256':hashlib.sha256(production.read_bytes()).hexdigest()})
    write('logs/revision87/structures.json',{'time':STAMP,'structures':report,'game_tested':False})
    print(json.dumps(report,ensure_ascii=False))

if __name__=='__main__':main()
