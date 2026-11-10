"""2026-09-29：只读扫描内测5资料与源码，生成完成度审计的覆盖索引。"""
from pathlib import Path
from html.parser import HTMLParser
from collections import Counter
from datetime import datetime
import json,re,hashlib
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'logs/beta5-completion-audit-20260929'
OUT.mkdir(parents=True,exist_ok=True)
class Text(HTMLParser):
    def __init__(self): super().__init__();self.parts=[];self.skip=0
    def handle_starttag(self,t,a):
        if t in ('script','style'):self.skip+=1
    def handle_endtag(self,t):
        if t in ('script','style'):self.skip=max(0,self.skip-1)
    def handle_data(self,s):
        if not self.skip and s.strip():self.parts.append(s.strip())
docs=[];sources=[]
allfiles=[p for p in (ROOT/'doc/HK3GTL-内测5').rglob('*') if p.is_file()]
for p in allfiles:
    if p.suffix not in ('.html','.md','.txt'):continue
    raw=p.read_text(encoding='utf-8-sig',errors='replace')
    parser=Text()
    if p.suffix=='.html':parser.feed(raw);text='\n'.join(parser.parts)
    else:text=raw
    docs.append({'path':p.relative_to(ROOT).as_posix(),'historical':'10_历史对照' in p.parts,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'text':text})
for p in (ROOT/'src').rglob('*.java'):
    raw=p.read_text(encoding='utf-8-sig',errors='replace')
    sources.append({'path':p.relative_to(ROOT).as_posix(),'lines':len(raw.splitlines()),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'markers':[{'line':i,'text':s.strip()[:240]} for i,s in enumerate(raw.splitlines(),1) if re.search(r'TODO|FIXME|暂未|未接|占位|stub|placeholder|待实现|待接|后续|return false;',s,re.I)]})
summary={'time':datetime.now().astimezone().isoformat(),'all_doc_files':len(allfiles),'doc_extensions':dict(Counter(p.suffix for p in allfiles)),'text_documents':len(docs),'nonhistorical_text_documents':sum(not d['historical'] for d in docs),'main_java':sum('/main/' in s['path'] for s in sources),'test_java':sum('/test/' in s['path'] for s in sources),'java_lines':sum(s['lines'] for s in sources),'coverage':'全部路径索引、全文提取与标记扫描；系统主路径人工对照；不代表逐行语义证明或实机验收。'}
for name,data in [('documents',docs),('source-index',sources),('inventory',summary)]:
    (OUT/(name+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False))
for d in docs:
    if not d['historical'] and ('讨论记录' not in d['path']) and len(d['path'].split('/'))<=5:print(d['path'])

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
