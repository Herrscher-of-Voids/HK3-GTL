"""内测5批次3：从已接受的研究目录提取结构化前置，不推测数值或完成证据。
Beta5 batch 3: extract the research dependency catalog without inventing costs or completion evidence.
变更记录 #1：2026-09-22 14:48；新增导出与一致性检查，无旧内容删除。
Output is bundled metadata, not an automatically completed research tree.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/'doc/HK3GTL-内测5/04_研究系统/研究课题目录与前置树_v1.html'
OUTPUT = ROOT/'src/main/resources/data/hk3gtl/research/research_catalog.json'
PLAYER_TEXT = json.loads((ROOT/'tools/research_player_text.json').read_text(encoding='utf-8'))

# 2026-09-28已批准的职责合并只校准元数据，不改历史目录、前置或生产配方。
MERGED_MACHINES = {'I46':['I05'], 'I47':['I05'], 'I48':['I12'], 'I49':['I16'],
                   'I50':['I16'], 'I51':['I11'], 'I52':['I05'], 'I53':['I16','I33']}
MERGED_RESULTS = {
    'RN-HLC':'解锁I05反应堆热循环与换热工况；原介质再生路线保留。',
    'RN-SFR':'解锁I05屏蔽拆解、有限材料回收与残渣处置工况；不恢复原燃料全部能量。',
    'RN-CBS':'解锁I12基础基板生长与沉积工况；不要求下一阶段才产出的魂钢载体。',
    'RN-MCE':'解锁I16多层电路蚀刻工况；首次封装先用前级可达GTL工艺，不等待CPT正式封装。',
    'RN-OPR':'解锁I05可验证的节料回收改良工况，具体收益后定。',
    'RN-CPT':'解锁I16精密封装与电气终检工况，各步分别配方；首套工况使用前级电路。',
    'RN-GPR':'解锁I05分气种净化与过滤介质回用工况；与液态介质再生分别配方。',
    'RN-CQS':'解锁I12基板及I16蚀刻、封装的高阶工况；逐级种子配方仍必须在前一电压可制造。',
    'RN-UAA':'解锁I11探针与无人作业装置装配工况，I16供应精密件；返修由UPR单独开放，任务执行仍归I26。',
    'RN-HCC':'解锁I16舰体件与I11施工装置配方；不要求后续虚数材料。',
    'RN-BCC':'解锁I16空壳与接口制造、I33装配密封与场校准工况，产出正式空世界泡收容容器；不要求先捕获世界泡。',
    'RN-UPR':'解锁I11无人装置返修工况；同一装置不能同时返还新件与旧件。',
}

def apply_confirmed_merges(topics):
    for topic in topics:
        topic['machines'] = list(dict.fromkeys(machine for old in topic['machines']
            for machine in MERGED_MACHINES.get(old, [old])))
        if topic['id'] in MERGED_RESULTS:
            topic['result'] = MERGED_RESULTS[topic['id']]

def extract():
    """读取const nodes的JSON并返回有序课题数组；重复/缺失/成环立即失败。
    Read the JSON nodes array, returning ordered topics; reject duplicates, missing parents and cycles.
    """
    text = SOURCE.read_text(encoding='utf-8')
    nodes, _ = json.JSONDecoder().raw_decode(text.split('const nodes=',1)[1].lstrip())
    result = []
    def visit(items):
        for item in items:
            if item['id'].startswith('RN-'):
                result.append({k:item[k] for k in ('id','title','english','lab','tier','prerequisites','machines','evidence','result')})
            visit(item.get('children',[]))
    visit(nodes)
    by_id = {n['id']:n for n in result}
    assert len(by_id) == len(result) == 100
    done, active = set(), set()
    def check(key):
        assert key in by_id, key
        assert key not in active, key
        if key in done:return
        active.add(key)
        for parent in by_id[key]['prerequisites']:check(parent)
        active.remove(key);done.add(key)
    for key in by_id:check(key)
    apply_confirmed_merges(result)
    for topic in result:
        topic.update({key:PLAYER_TEXT[topic['id']][key] for key in ('evidence','result')})
    return result

if __name__ == '__main__':
    topics=extract()
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps({'schema':1,'topics':topics},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Exported and validated {len(topics)} research topics.')

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
