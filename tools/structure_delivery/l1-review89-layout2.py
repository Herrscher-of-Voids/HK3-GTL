# -*- coding: utf-8 -*-
"""候选89第二版：集中接口、中轴主控、无破坏检修路径。
【变更记录 #1】2026-09-27 03:37:00
删除：新候选不生成散布的装饰承台，不执行贯穿切除。
新增：正面集中接口面板、完整中轴地面、利用天然空隙的三格宽四格高通道。
修改：复用第一版五机主体和材料，不覆盖第一版或正式游戏资源。
用途：落实负责人本轮确认；几何核验不等于游戏成型。
"""
from pathlib import Path
from datetime import datetime
from collections import deque
import importlib.util,json

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'doc/HK3GTL-内测5/03_机器结构/L1五机重设计_候选89_接口调整'
spec=importlib.util.spec_from_file_location('original',Path(__file__).with_name('l1-review89-buildings.py'))
original=importlib.util.module_from_spec(spec);spec.loader.exec_module(original)


class Building(original.Building):
    def base(self):
        # 只生成承重地面；不再无目的地散布2×2装饰墩。
        for x in range(self.w):
            for z in range(self.d):
                if min(x,self.w-1-x)+min(z,self.d-1-z)<3:continue
                edge=min(x,self.w-1-x,z,self.d-1-z)
                self.put(x,0,z,'D' if edge in (0,3) or x==self.cx else 'C')

    def finish(self):
        equipment=dict(self.cells)
        c=self.cx
        # 中轴位于地面，贯通前后；不将中轴误当作必须清空的走道。
        for z in range(self.d):self.put(c,0,z,'D')
        counts=self.meta['ports']
        specs=[]
        for i in range(counts['item']):specs.append(('M'+str(i+1),'物品接口','物品输入／输出；同类互换，空余可封闭'))
        for i in range(counts['fluid']):specs.append(('F'+str(i+1),'流体接口','采集液体输出，必须保留' if counts['fluid']==1 else '流体输入／输出；同类互换，空余可封闭'))
        if counts['parallel']:specs.append(('P1','扩展接口','可选并行仓，最多1；空余用接口机械方块'))
        half=max(2,(len(specs)+3)//4)
        # 接口面板四周有连续边框，端口由近及远排列，主控固定在中轴。
        for x in range(c-half-1,c+half+2):
            for y in range(1,4):
                assert (x,y,3) not in equipment,('面板不得覆盖设备',self.key,x,y)
                self.put(x,y,3,'D' if y==3 or abs(x-c)==half+1 else 'C')
        self.controller=[c,2,3];self.put(*self.controller,'minecraft:diamond_block')
        self.put(c,1,3,'H')
        # 物品优先在左侧，流体延续到右侧；每侧上下两层，端口数量不变。
        positions=[(c-d,y,3) for y in (2,1) for d in range(1,half+1)]+[(c+d,y,3) for y in (2,1) for d in range(1,half+1)]
        for (pid,group,purpose),pos in zip(specs,positions):
            self.put(*pos,'minecraft:diamond_ore')
            self.ports.append({'id':pid,'pos':list(pos),'face':'north','group':group,'purpose':purpose})
        assert len(self.ports)==len(specs)
        # 前方操作带及主体之间的自然间隙；只标识和铺地，不清除任何实体。
        free=set()
        for x in range(1,self.w-1):
            for z in range(1,self.d-1):
                if all((xx,0,zz) in self.cells and all((xx,y,zz) not in self.cells for y in range(1,5)) for xx in range(x-1,x+2) for zz in range(z-1,z+2)):
                    free.add((x,z))
        start=(c,1);assert start in free
        parent={start:None};distance={start:0};queue=deque([start])
        while queue:
            x,z=queue.popleft()
            for p in ((x-1,z),(x+1,z),(x,z-1),(x,z+1)):
                if p in free and p not in parent:parent[p]=(x,z);distance[p]=distance[x,z]+1;queue.append(p)
        chosen=set()
        for side in (-1,1):
            candidates=[p for p in parent if (p[0]-c)*side>half+1]
            assert candidates,('缺少侧向通道',self.key,side)
            endpoint=max(candidates,key=lambda p:(p[1],distance[p]))
            assert endpoint[1]>=self.d//2,('侧向通道未进入主体',self.key,endpoint)
            p=endpoint
            while p is not None:chosen.add(p);p=parent[p]
        # 前操作带覆盖整个面板；通道净空检查适用于叠加显示的全部格子。
        tiles={(xx,zz) for x,z in chosen for xx in range(x-1,x+2) for zz in range(z-1,z+2)}
        tiles.update((x,z) for x in range(c-half-2,c+half+3) for z in range(3))
        for z in sorted({p[1] for p in tiles}):
            xs=sorted(x for x,zz in tiles if zz==z);startx=prev=xs[0]
            for x in xs[1:]+[self.w+10]:
                if x!=prev+1:
                    self.paths.append({'name':'沿设备间隙的检修操作带','min':[startx,1,z],'max':[prev,4,z]});startx=x
                prev=x
        for x,z in tiles:
            assert all((x,y,z) not in self.cells for y in range(1,5)),('通道占用',x,z)
            if x!=c:self.put(x,0,z,'S')
        preserved=all(self.cells.get(p)==s for p,s in equipment.items() if p[1]>0)
        assert preserved,'主体必须逐格保留'
        self.zone('中央主控与集中接口',[c,4,3])
        return {'key':self.key,'name':'hk3gtl-'+self.key+'-review89-layout2','title':self.key.upper()+' '+self.meta['design_name'],
                'description':self.meta['composition'],'details':self.meta['details'],'size':self.size,'controller':self.controller,
                'entrance':[c,1],'blocks':[{'pos':list(p),'state':s} for p,s in sorted(self.cells.items())],
                'ports':self.ports,'paths':self.paths,'zones':self.zones,'status':'接口布局第二版候选，未接入正式机器',
                'generated_at':datetime.now().astimezone().isoformat(),'layout_checks':{'equipment_above_floor_preserved':preserved,
                'removed_equipment_blocks':0,'controller_on_center_axis':True,'all_ports_front_panel':True,
                'decorative_pads_generated':False,'natural_corridor_centers_reached':len(parent)}}


if __name__=='__main__':
    proposal=json.loads((ROOT/'logs/revision89/design-proposal.json').read_text(encoding='utf-8'))
    for m in proposal['machines']:
        b=Building(m);getattr(original,m['id'])(b);original.enrich(b);data=b.finish();audit=original.validate(data)
        audit.update(data['layout_checks'])
        out=OUT/m['id'];out.mkdir(parents=True,exist_ok=True)
        for name,obj in [('blueprint.json',data),('geometry-audit.json',audit)]:
            (out/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
        print(m['id'],len(data['blocks']),'方块，主体零切除，主控居中，接口集中，通道核验通过')
