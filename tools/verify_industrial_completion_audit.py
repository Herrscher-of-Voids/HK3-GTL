"""2026-09-29：检查审计产物和来源完整性，不运行或修改游戏。"""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse,unquote
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'logs/beta5-completion-audit-20260929'
def load(p):return json.loads(p.read_text(encoding='utf-8'))
class Page(HTMLParser):
    def __init__(self):super().__init__();self.hrefs=[];self.ids=[];self.script=False;self.scripts=[]
    def handle_starttag(self,t,a):
        attrs=dict(a)
        if t=='a' and 'href' in attrs:self.hrefs.append(attrs['href'])
        if 'id' in attrs:self.ids.append(attrs['id'])
        if t=='script':self.script=True
    def handle_endtag(self,t):
        if t=='script':self.script=False
    def handle_data(self,d):
        if self.script:self.scripts.append(d)
meta=load(OUT/'report-meta.json');data=load(OUT/'system-audit.json')
p=Page();p.feed(Path(meta['report']).read_text(encoding='utf-8'))
assert len(p.ids)==len(set(p.ids)),'duplicate HTML ids'
bad=[]
for href in p.hrefs:
    if href.startswith('#'):
        if href[1:] not in p.ids:bad.append(href)
    elif href.startswith('file:'):
        path=unquote(urlparse(href).path).lstrip('/')
        if not Path(path).is_file():bad.append(href)
assert not bad,bad
changed=[]
for record in load(OUT/'source-index.json'):
    path=ROOT/record['path']
    if hashlib.sha256(path.read_bytes()).hexdigest()!=record['sha256']:changed.append(record['path'])
assert not changed,changed
for row in data['systems']:
    for ref in row['refs']:
        path=Path(ref['absolute'])
        assert hashlib.sha256(path.read_bytes()).hexdigest()==ref['sha256'],str(path)
        assert ref['line']<=len(path.read_text(encoding='utf-8-sig').splitlines())
js=OUT/'report-filter-check.js';js.write_text('\n'.join(p.scripts),encoding='utf-8')
run=subprocess.run(['node','--check',str(js)],capture_output=True,text=True)
assert run.returncode==0,run.stderr
canvas=Path(meta['canvas']).read_text(encoding='utf-8')
assert 'from "cursor/canvas"' in canvas and 'export default' in canvas
assert 'fetch(' not in canvas and 'linear-gradient' not in canvas and 'boxShadow' not in canvas
result={'systems':len(data['systems']),'evidence_references':sum(len(r['refs']) for r in data['systems']),'html_links_checked':len(p.hrefs),'invalid_links':bad,'source_files_changed_during_audit':changed,'html_filter_javascript':'node --check passed','canvas':'source generated; not host-render acceptance','runtime_change':'none','game_started':False}
(OUT/'artifact-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
