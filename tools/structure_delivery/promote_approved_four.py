# -*- coding: utf-8 -*-
"""2026-09-25：将已确认的四台逐格蓝图提升为包内正式资源与真实仓室模板，保留外部评审标记文件。"""
from pathlib import Path
import json, re, nbtlib as n

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'doc/HK3GTL-内测5/03_机器结构/初期四机外观重设计_v2'
RES=ROOT/'src/main/resources/data/hk3gtl'
IDS={'i01':'i01_honkai_collection_tower','i02':'i02_spectrum_analysis_array','i03':'liquid_honkai_fractionation_center','s01':'abyss_research_analysis_matrix'}

def main():
    (RES/'approved_architecture').mkdir(exist_ok=True)
    for key,controller in IDS.items():
        data=json.loads((BASE/key/'blueprint.json').read_text(encoding='utf-8'))
        (RES/'approved_architecture'/f'{key}.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
        template=n.load(BASE/key/(data['name']+'.nbt'))
        def state_index(name,face=None):
            state=n.Compound({'Name':n.String(name)})
            if face:state['Properties']=n.Compound({'facing':n.String(face)})
            for i,s in enumerate(template['palette']):
                if s==state:return i
            template['palette'].append(state);return len(template['palette'])-1
        ports={tuple(p['pos']):p for p in data['ports']}
        for block in template['blocks']:
            pos=tuple(map(int,block['pos']))
            if pos==tuple(data['controller']):
                block['state']=n.Int(state_index('hk3gtl:'+controller,'north'))
            elif pos in ports:
                port=ports[pos];pid=port['id'];face=port['face']
                if key=='s01' or pid=='P1' or (key=='i01' and pid=='M2'):
                    block['state']=n.Int(state_index('gtceu:max_machine_casing'));continue
                output=(key=='i01' and pid=='F1') or (key=='i02' and pid in ('M2','M4')) or (key=='i03' and pid in ('M2','F4','F5','F6'))
                kind='hatch' if pid.startswith('F') else 'bus'
                block['state']=n.Int(state_index(f'gtceu:max_{"output" if output else "input"}_{kind}',face))
        template.save(RES/'structures/approved'/f'{key}.nbt',gzipped=True)
        print(key, data['size'],len(data['blocks']),'正式结构与真实接口模板已生成')
    pattern=ROOT/'src/main/java/com/sirin/hk3gtl/common/multiblock/pattern'
    for file,key in [('Hk3I01CollectionPatternImpl.java','i01'),('Hk3I02SpectrumPatternImpl.java','i02'),('Hk3ResearchMatrixPatternImpl.java','s01')]:
        p=pattern/file;s=p.read_text(encoding='utf-8')
        # 历史备注留在原处，旧方法整体另行归档；当前唯一入口转入正式资源适配器。
        marker='    public static BlockPattern createPattern(MultiblockMachineDefinition definition) {'
        start=s.index(marker);end=s.rfind('}')
        s=s[:start]+marker+'\n        return Hk3ApprovedArchitecturePatterns.create(definition,"'+key+'");\n    }\n'+s[end:]
        note='/**\n * 【变更记录 #3】2026-09-25 02:18:00（内测5修订70）\n * 删除：旧结构退出正式入口，原实现已归档。新增：获批建筑的统一成型资源入口。\n * 修改：使用'+key+'正式逐格结构，去除旧海渊建材依赖；用途：结构与确认预览一致，不更改机器工艺。\n */\n'
        s=s.replace('public class ',note+'public class ',1)
        # 不保留已失去用途的旧材料辅助方法，历史文件已完整备份。
        start=s.find('    /** 新版 MAX 材料')
        if start>=0:s=s[:start]+s[s.index('    public static BlockPattern createPattern',start):]
        # I02采用不同描述，同样只保留构造器与当前入口。
        if key=='i02':
            start=s.index('    private static TraceabilityPredicate') if '    private static TraceabilityPredicate' in s else -1
            if start>=0:s=s[:start]+s[s.index('    public static BlockPattern createPattern',start):]
        p.write_text(s,encoding='utf-8')

if __name__=='__main__':main()
