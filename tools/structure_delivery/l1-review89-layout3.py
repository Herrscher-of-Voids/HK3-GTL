# -*- coding: utf-8 -*-
"""候选89第三版：统一灰色地板与无机壳边框的接口面板。
【变更记录 #1】2026-09-27 03:42:11
删除：本候选取消面板顶框，地板不再按检修路线换色；历史候选保留。
新增：面板空余位置标为可选接口，必要接口与并行上限沿用原规则。
修改：全部Y=0地板统一模块基座，正面两层面板除主控外全部为接口标记。
用途：生成审核候选，不修改正式Pattern和游戏实例。
【变更记录 #2】2026-09-27 03:45:00
删除：取消把白色外框误改为接口的处理。新增：保留原有顶部与左右计算机机壳边框。
修改：仅框内两层空间除主控外全部标为接口；灰色地板不变。用途：落实负责人明确纠正。
"""
from pathlib import Path
from datetime import datetime
import importlib.util,json

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'doc/HK3GTL-内测5/03_机器结构/L1五机重设计_候选89_统一地板'
spec=importlib.util.spec_from_file_location('layout2',Path(__file__).with_name('l1-review89-layout2.py'))
previous=importlib.util.module_from_spec(spec);spec.loader.exec_module(previous)


class Building(previous.Building):
    def finish(self):
        data=super().finish()
        cells={tuple(b['pos']):b['state'] for b in data['blocks']}
        c=self.cx;half=max(2,(len(data['ports'])+3)//4)
        for p in list(cells):
            if p[1]==0:cells[p]='kubejs:module_base'
        occupied_ports={tuple(p['pos']) for p in data['ports']}
        extra=0
        for x in range(c-half,c+half+1):
            # 原有白色顶部与左右外框直接保留；只修改框内两层位置。
            for y in (1,2):
                p=(x,y,3)
                if p==tuple(data['controller']):continue
                cells[p]='minecraft:diamond_ore'
                if p not in occupied_ports:
                    extra+=1
                    data['ports'].append({'id':'E'+str(extra),'pos':list(p),'face':'north','group':'可选接口',
                        'purpose':'新增可选物品／流体接口位；不用时以工业接口机械方块封闭，不新增必装要求或并行仓名额'})
        data['name']='hk3gtl-'+self.key+'-review89-layout3'
        data['blocks']=[{'pos':list(p),'state':s} for p,s in sorted(cells.items())]
        data['status']='统一灰色地板、白色外框与框内全接口候选，未接入正式机器'
        data['generated_at']=datetime.now().astimezone().isoformat()
        data['layout_checks'].update(uniform_floor='kubejs:module_base',panel_only_controller_and_ports=True,white_frame_preserved=True,
            optional_ports_added=extra,panel_rows=2,original_port_requirements=self.meta['ports'])
        return data


if __name__=='__main__':
    proposal=json.loads((ROOT/'logs/revision89/design-proposal.json').read_text(encoding='utf-8'))
    for m in proposal['machines']:
        b=Building(m);getattr(previous.original,m['id'])(b);previous.original.enrich(b)
        data=b.finish();audit=previous.original.validate(data);audit.update(data['layout_checks'])
        out=OUT/m['id'];out.mkdir(parents=True,exist_ok=True)
        for name,value in [('blueprint.json',data),('geometry-audit.json',audit)]:
            (out/name).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
        print(m['id'],len(data['blocks']),'方块',len(data['ports']),'接口位；灰色地板、两层全接口面板')
