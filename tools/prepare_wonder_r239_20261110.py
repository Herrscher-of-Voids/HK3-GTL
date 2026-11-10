"""同步W01/W02验收文案及修订，不改生产或毕业规则。"""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
for lang in ['zh_cn','en_us']:
    p=ROOT/f'src/main/resources/assets/hk3gtl/lang/{lang}.json'
    data=json.loads(p.read_text('utf8'))
    data['block.hk3gtl.omnia_autonomous_industrial_matrix']='理之律者 · 万象·自律工业矩阵' if lang=='zh_cn' else 'Herrscher of Reason · Omnia Autonomous Industrial Matrix'
    data['hk3gtl.w01.structure_only']='完整实体成型与创造巡检调试；正式工艺和毕业规则另定。'
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf8')
p=ROOT/'src/main/resources/assets/hk3gtl/changelog.json'
data=json.loads(p.read_text('utf8'))
if data['entries'][0]['revision']==238:
    data['entries'].insert(0,dict(revision=239,date='2026-11-10',timezone='Asia/Hong_Kong',reason='W01/W02真实控制器与分批完整核验、创造巡检',changes=[
        'W02接入19C船坞A2完整实体、真实GT主控和八通用接口，保持静态。',
        'W01/W02复用逐实体分批实读及滑动区块票；创造启停执行已加载实体巡检，不能授予生产或毕业资格。',
        '新增W01–W03创造验收入口，复用真实搭建、核验与启停操作；W03保留C9场特效。',
        '负责人明确本轮先验控制器、完整搭建、成型与运行，正式工艺另定；客户端验收另行记录。']))
else:
    assert data['entries'][0]['revision']==239
p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf8')
