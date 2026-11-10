# -*- coding: utf-8 -*-
"""电压任务横向布局：本页前置严格由左到右，研究最多两行，跨页前置和辅助说明各成横排。"""
# 【变更记录 #1】2026-10-01 15:45:32（修订132）：新增双行横向布局与单行外页前置；只计算坐标，不改变任务语义。
def apply_horizontal(chapters, manifest, topics, ident, primary):
    by_topic = {t['id']: t for t in topics}
    entries = {e['key']: e for e in manifest}
    by_quest = {e['quest']: e for e in manifest}
    def depth(key):
        t = by_topic[key]
        return 1 + max((depth(p) for p in t['prerequisites'] if by_topic[p]['tier'] == t['tier']), default=-1)
    for tier, chapter in enumerate(chapters):
        quests = {q['id']: q for q in chapter['quests']}
        stage = [t for t in topics if t['tier'] == tier]
        positions = {}
        column = 0
        for level in sorted({depth(t['id']) for t in stage}):
            batch = [t for t in stage if depth(t['id']) == level]
            # 优先使依赖相同一侧的分支相邻，避免字母排序将相连节点拆散。
            def order(t):
                parents = [positions[p] for p in t['prerequisites'] if p in positions]
                return (sum(y for x,y in parents)/len(parents) if parents else 0, t['id'])
            batch.sort(key=order)
            for i,t in enumerate(batch):
                x = (column + i//2)*3.5
                y = (i%2)*4.0
                positions[t['id']] = (x,y)
                quests[entries[t['id']]['quest']].update(x=x,y=y)
            column += (len(batch)+1)//2
        bottom = max((y for x,y in positions.values()), default=0) + 4.0
        auxiliary = 0
        for q in chapter['quests']:
            e=by_quest[q['id']];key=e['key']
            if e['kind']=='research':continue
            if key=='guide-start' or key.startswith('voltage-intro-'):
                q.update(x=-8.0,y=0.0,size=2.0,shape='rsquare',icon=primary.get(tier,'gtlcore:max_electric_motor'))
            elif key.startswith('voltage-parts-'):
                q.update(x=-4.0,y=0.0)
            else:
                q.update(x=auxiliary*3.5,y=bottom);auxiliary+=1
        external={p for t in stage for p in t['prerequisites'] if by_topic[p]['tier']!=tier}
        def external_order(p):
            children=[positions[t['id']][0] for t in stage if p in t['prerequisites']]
            return (sum(children)/len(children),p)
        chapter['quest_links']=[{'id':ident('link:'+chapter['filename']+':'+p),'linked_quest':entries[p]['quest'],'x':i*3.5,'y':-4.0} for i,p in enumerate(sorted(external,key=external_order))]

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
