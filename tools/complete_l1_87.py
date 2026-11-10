# -*- coding: utf-8 -*-
"""修订87交付收尾：追加审批落实状态、模板元数据及文件指纹；不启动或部署游戏。"""
from pathlib import Path
from datetime import datetime
import json
import hashlib
import shutil

ROOT=Path(__file__).resolve().parents[1]
LOG=ROOT/'logs/revision87'
STAMP=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
changed=[]

def save(rel,text):
    p=ROOT/rel;backup=LOG/'backup'/rel
    if p.exists() and not backup.exists():
        backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,backup)
    p.write_text(text,encoding='utf-8');changed.append(rel)

rel='src/main/resources/data/hk3gtl/structures/approved/i03.json'
data=json.loads((ROOT/rel).read_text(encoding='utf-8'))
data['_comment_revision87']=f'变更记录 #1 {STAMP}（修订87）：保留修订70蓝图来源；修改正式NBT的F3为流体输出，默认2进4出以容纳净化四流体；坐标、外形及Pattern同类互换不变。'
data['template_revision']=87
data['template_sha256']=hashlib.sha256((ROOT/'src/main/resources/data/hk3gtl/structures/approved/i03.nbt').read_bytes()).hexdigest()
data['default_fluid_inputs']=['F1','F2']
data['default_fluid_outputs']=['F3','F4','F5','F6']
save(rel,json.dumps(data,ensure_ascii=False,indent=2)+'\n')

rel='doc/崩坏三-GTL/00_项目总览/模组全面系统性分析报告_v5.md'
s=(ROOT/rel).read_text(encoding='utf-8')
if '修订87批准结构落地' not in s:
    s+=f'''\n\n### 修订87批准结构落地\n\n【变更记录 #3】{STAMP}（内测5修订87）\n\n- 审批：负责人已明确批准I04 23×27×23中央稳定腔、三层约束环、两侧冷却柱，以及I05 27×19×23前低后高双塔、侧面换热模块；本记录更新上文待审批状态，保留历史过程。\n- 新增：I04/I05批准蓝图、正式NBT、标记与真实仓室Sponge v2、材料和端口清单；两座分别2260/1524个实体方块。\n- 修改：正式Pattern、放置命令及诊断夹具从同一资源读取尺寸、坐标；两座均4物品槽、8流体槽、1可选并行槽，同类共享计数且各至少一进一出。主控外观切换到现有内测5外壳。旧布局数据保留，但I04/I05正式入口不再使用。\n- 修改：I03默认NBT的F3为输出，形成2流体进4出；Pattern允许同类互换，原几何保持不变。旧修订70外部投影保留为历史文件，不代表当前默认端口分配。\n- 用途：关闭L1两台设备的旧海渊建材和新工艺端口不一致问题，不改研究费用及实验结算方式。\n- 核验：两座JSON/NBT/Sponge已独立逐格比对，通道、连通性、端口访问面及完整立方体材质通过；数量检查通过零回收库存启动及60组回流宏批次。报告分别为logs/revision87/structure-verification.json与material-balance.json。\n- 边界：产线供需核算不等于化学元素守恒；GT耗材需持续供给，研究前副产物需暂存。构建以clean-build-structures.log为准；未启动游戏、未部署，机器实际成型、研究推进及长时间自动化由用户验收。\n'''
save(rel,s)

rel='doc/HK3GTL-内测5/02_工业计划/HK3GTL工业计划树状图_v5.html'
s=(ROOT/rel).read_text(encoding='utf-8')
if 'id="revision87-structures"' not in s:
    section=f'''\n<section id="revision87-structures"><h2>L1 批准结构落实 · 修订87</h2>
<p>变更记录 #2 {STAMP}：负责人已批准两座新结构；本段更新前文待审批状态，保留历史提案。</p>
<p>I04为23×27×23、2260实体方块；I05为27×19×23、1524实体方块。两台均使用已核对的GT/GTL及整包完整方块，正式入口不再依赖旧海渊建材。每台4个物品槽、8个流体槽和1个可选并行槽，同类方向可互换但输入与输出各至少一个。</p>
<p>批准JSON、正式NBT、标记与真实仓室Sponge文件已逐格核对；I03默认模板同步为2流体进4出。结构及材料清单位于本项目03_机器结构/L1稳定与再生_修订87。尚未部署或做游戏验收，不能据静态结果宣称L1实际运行完成。</p></section>\n'''
    assert '</body>' in s;s=s.replace('</body>',section+'</body>',1)
save(rel,s)

record=json.loads((LOG/'application.json').read_text(encoding='utf-8'))
paths=set(changed)
for key in ['i04','i05']:
    paths.add(f'src/main/resources/data/hk3gtl/approved_architecture/{key}.json')
    paths.update(f'src/main/resources/data/hk3gtl/structures/approved/{key}.{ext}' for ext in ['json','nbt'])
    paths.update(str(p.relative_to(ROOT)).replace('\\','/') for p in (ROOT/f'doc/HK3GTL-内测5/03_机器结构/L1稳定与再生_修订87/{key}').iterdir() if p.is_file())
for rel in sorted(paths):
    if not any(e['path']==rel for e in record['files']):
        backup=LOG/'backup'/rel
        record['files'].append({'path':rel,'before':hashlib.sha256(backup.read_bytes()).hexdigest() if backup.exists() else None})
for e in record['files']:e['after']=hashlib.sha256((ROOT/e['path']).read_bytes()).hexdigest()
record['completed_source_at']=STAMP
(LOG/'application.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'recorded_files':len(record['files']),'time':STAMP},ensure_ascii=False))
