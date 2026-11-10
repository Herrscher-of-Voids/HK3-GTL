"""从已审核页面提取原文，生成游戏目录与翻译键；保留原文，不生成剧情或奖励。
变更记录 #1：2026-09-29，实际生成时间写入清单；新增批量提取与来源校验，无旧正文删除。
"""
from pathlib import Path
from html import unescape
import json, re, hashlib, sys
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / 'doc/HK3GTL-内测5'
OUT = ROOT / 'src/main/resources/assets/hk3gtl/narrative/approved.json'
LOG = ROOT / 'logs/approved-prose-20260929'

def plain(value):
    value = re.sub(r'<br\s*/?>', '\n', value)
    return unescape(re.sub('<[^>]+>', '', value)).strip()

def paragraphs(value):
    return [plain(x) for x in re.findall(r'<p[^>]*>(.*?)</p>', value, re.S) if plain(x)]

def embedded(path):
    return json.loads(re.search(r'<script[^>]*type="application/json"[^>]*>(.*?)</script>', path.read_text(encoding='utf-8'), re.S)[1])

def generate():
    entries = []
    sources = {}
    def source(p):
        relative = p.relative_to(ROOT).as_posix()
        sources[relative] = hashlib.sha256(p.read_bytes()).hexdigest()
        return relative
    def add(id, system, title, speaker, lines, path, **extra):
        assert lines and all(isinstance(x, str) and x.strip() for x in lines), id
        entries.append(dict(id=id, system=system, title=title, speaker=speaker, lines=lines, source=source(path), **extra))
    p = DOC / '11_系统专项/交流与外交系统/通知与交流整批审核_v1/review-data.json'
    comm = json.loads(p.read_text(encoding='utf-8'))
    for e in comm['entries']:
        add('communication.'+e['id'], 'communication', e['title'], e['speaker'], paragraphs(e['html']), p)
    p=DOC / '05_叙事事件/一审召入与茧的三问_正文草案v1.html'
    first=p.read_text(encoding='utf-8')
    arrival=re.search(r'<section id="arrival">(.*?)</section>',first,re.S)[1]
    add('first_review.open','first_review','召入与开场','终焉之茧',paragraphs(re.search(r'<blockquote>(.*?)</blockquote>',arrival,re.S)[1]),p)
    for i,m in enumerate(re.finditer(r'<h3>(.*?)</h3><blockquote>(.*?)</blockquote>',first,re.S),1):
        add('first_review.question.'+str(i),'first_review',plain(m[1]),'终焉之茧',paragraphs(m[2]),p)
    closing=re.search(r'<section id="closing">(.*?)</section>',first,re.S)[1]
    add('first_review.closing','first_review','三问之后的收束','终焉之茧',[line for m in re.finditer(r'<blockquote>(.*?)</blockquote>',closing,re.S) for line in paragraphs(m[1])],p)
    p=DOC / '05_叙事事件/首次量子异常_观测记录正文草案v1.html'
    add('observation.QOM','observation','校准之外的回响','信标观测记录',paragraphs(re.search(r'<article id="record">(.*?)</article>',p.read_text(encoding='utf-8'),re.S)[1]),p)
    p = DOC / '11_系统专项/贸易系统/贸易系统正文整批审核_v2.html'
    for m in re.finditer(r'<details class="entry" id="([^"]+)".*?</details>', p.read_text(encoding='utf-8'), re.S):
        block=m[0]; title=plain(re.search('<summary>(.*?)<small>',block,re.S)[1]); article=re.search('<article>(.*?)</article>',block,re.S)
        if article:
            speaker=plain(re.search('<p class="meta">(.*?)</p>',block,re.S)[1]).split(' / ')[0]
            add('trade.'+m[1], 'trade', title, speaker, paragraphs(article[1]), p)
    p = DOC / '11_系统专项/NPC系统/NPC家园访客与正文整批审核_v2.html'
    for m in re.finditer(r'<details class="visitor" id="([^"]+)".*?</details>',p.read_text(encoding='utf-8'),re.S):
        block=m[0]; speaker=plain(re.search('<summary>(.*?)<small>',block,re.S)[1]).split(' · ',1)[1]
        for part in re.finditer(r'<h4 id="([^"]+)">(.*?)</h4>.*?<article>(.*?)</article>',block,re.S):
            add('npc.'+part[1], 'npc', speaker+' · '+plain(part[2]).split(' · ')[0], speaker, paragraphs(part[3]), p)
    p=DOC / '11_系统专项/更新详情页面/进入游戏更新详情正文整批审核_v1.html'
    for e in embedded(p).values():
        add('update.'+e['id'],'update',e['title'],'系统',e['text'].splitlines(),p)
    p=DOC / '06_终局系统/二审与终审对话整批审核_v5_IF逐句阅读.html'
    for e in embedded(p).values():
        add(e['id'],'review' if e['id'].startswith('S') else 'finale',e['title'],e['speaker'],e['text'].splitlines(),p,next=e.get('next'),choices=e.get('choices',[]))
    assert len({e['id'] for e in entries})==len(entries)
    assert len([e for e in entries if e['system']=='npc'])==480
    lang={}
    for e in entries:
        base='hk3gtl.approved.'+e['id']
        lang[base+'.title']=e['title']; lang[base+'.speaker']=e['speaker']
        for i,line in enumerate(e.pop('lines')): lang[base+'.line.'+str(i)]=line
        e['lineCount']=i+1
        for i,c in enumerate(e.get('choices',[])): lang[base+'.choice.'+str(i)]=c['text']
    lang.update({
        'hk3gtl.prose.system.communication':'交流来信', 'hk3gtl.prose.system.trade':'五方贸易',
        'hk3gtl.prose.system.npc':'家园访客', 'hk3gtl.prose.system.update':'更新详情',
        'hk3gtl.prose.system.review':'二审会面', 'hk3gtl.prose.system.finale':'终审与IF',
        'hk3gtl.prose.system.first_review':'一审三问', 'hk3gtl.prose.system.observation':'实验观测记录',
        'hk3gtl.prose.back':'返回目录', 'hk3gtl.prose.previous':'上一页', 'hk3gtl.prose.next':'下一页',
        'hk3gtl.prose.home':'系统目录', 'hk3gtl.prose.continue':'继续', 'hk3gtl.prose.return_finale':'回到终审会面',
        'hk3gtl.prose.readonly':'已审核正文校对 · 只读；不会产生研究、外交、贸易或审查结果',
        'hk3gtl.prose.attachment':'随信观测资料', 'hk3gtl.prose.otto_followup':'查看奥托的后续来信',
        'hk3gtl.prose.update_ack':'我已了解，返回游戏', 'hk3gtl.prose.update_later':'稍后阅读',
        'hk3gtl.prose.preview':'正文校对 · 无进度及奖励结算',
        'hk3gtl.prose.if_count':'已选 %s / 5 · 已选条目可重读',
        'hk3gtl.prose.message_center':'消息中心', 'hk3gtl.prose.message_empty':'暂无消息。',
        'hk3gtl.prose.message_hint':'按 N 打开消息中心；来信可用 /hk3letter 重读',
        'hk3gtl.prose.new_letter':'收到来信', 'hk3gtl.prose.research_done':'研究完成',
        'hk3gtl.prose.archive_unlocked':'新的档案记录'
    })
    payload={'schema':1,'entries':entries}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    LOG.mkdir(parents=True,exist_ok=True)
    for locale in ['zh_cn','en_us']:
        p=ROOT / f'src/main/resources/assets/hk3gtl/lang/{locale}.json'
        backup=LOG / ('before-'+locale+'.json')
        if not backup.exists(): backup.write_bytes(p.read_bytes())
        existing=json.loads(p.read_text(encoding='utf-8')); existing.update(lang)
        p.write_text(json.dumps(existing,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    manifest={'generated':datetime.now().astimezone().isoformat(),'sources':sources,'counts':{s:sum(e['system']==s for e in entries) for s in dict.fromkeys(e['system'] for e in entries)},'languagePolicy':'已确认中文原文作为两种语言环境共同回退；未冒称英译完成。','entries':[{k:e[k] for k in ['id','system','source','lineCount']} for e in entries]}
    (LOG/'import-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return manifest

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    print(json.dumps(generate()['counts'],ensure_ascii=False))
