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
    return result

if __name__ == '__main__':
    topics=extract()
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps({'schema':1,'_comment':'Beta5 dependency catalog; costs, evidence collection and machine execution are separate. / 内测5前置目录，不代表研究已完成。','topics':topics},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Exported and validated {len(topics)} research topics.')

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
