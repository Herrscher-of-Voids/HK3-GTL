# -*- coding: utf-8 -*-
"""核对审计离线交付的链接、证据行号、主源码身份和脚本语法。

【变更记录 #1】2026-10-25（实际秒数见核验输出）
删除：无。新增：报告与来源JSON的一致性及可打开路径检查。
修改：不运行游戏，不修改源码，不把文档核验视为产品验收。
用途：拒绝失效链接/越界行号；证据语义由逐份人工审查负责。
"""
from pathlib import Path
from structure_delivery.project_paths import project_path
from html.parser import HTMLParser
from urllib.parse import urlparse, unquote
import datetime as dt
import hashlib
import json
import re
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
LOG=ROOT/'logs/beta5-audit-20261025'


def main():
    summary=json.loads((LOG/'audit-summary.json').read_text(encoding='utf-8'))
    report=ROOT/summary['report_path']
    missing=[]; bad_lines=[]; refs=set(); scripts=[]; ids=set(); anchors=[]
    class Page(HTMLParser):
        def __init__(self):
            super().__init__();self.script=False;self.parts=[]
        def handle_starttag(self,tag,attrs):
            a=dict(attrs)
            if 'id' in a:ids.add(a['id'])
            if tag in ('a','img','script'):
                link=a.get('href') or a.get('src')
                if link:
                    u=urlparse(link)
                    if not u.scheme and not u.netloc:
                        if u.path:
                            p=(report.parent/unquote(u.path)).resolve();refs.add(str(p))
                            if not p.is_file():missing.append(str(p))
                        elif u.fragment:anchors.append(u.fragment)
            if tag=='script' and 'src' not in a:self.script=True;self.parts=[]
        def handle_endtag(self,tag):
            if tag=='script' and self.script:
                scripts.append(''.join(self.parts));self.script=False
        def handle_data(self,data):
            if self.script:self.parts.append(data)
    text=report.read_text(encoding='utf-8');Page().feed(text)
    assert not [a for a in anchors if a not in ids]
    def walk(v):
        if isinstance(v,dict):
            if isinstance(v.get('path'),str):
                p=project_path(v['path'])
                if not p.is_absolute():p=ROOT/p
                if p.is_file():
                    refs.add(str(p.resolve()))
                    line=v.get('line')
                    if line and p.suffix in ('.java','.html','.json','.gradle','.py'):
                        n=len(p.read_text(encoding='utf-8-sig').splitlines())
                        if not isinstance(line,int) or not 1<=line<=n:bad_lines.append([str(p),line,n])
                else:missing.append(str(p))
            for x in v.values():walk(x)
        elif isinstance(v,list):
            for x in v:walk(x)
    for n in ['audit-summary','industry-audit','progression-audit','general-audit','client-audit','test-audit']:
        walk(json.loads((LOG/(n+'.json')).read_text(encoding='utf-8')))
    js_results=[]
    for script in scripts:
        with tempfile.NamedTemporaryFile('w',suffix='.js',encoding='utf-8',delete=False) as stream:
            stream.write(script);p=project_path(stream.name)
        result=subprocess.run(['node','--check',str(p)],capture_output=True,text=True)
        p.unlink()
        js_results.append({'exit_code':result.returncode,'output':result.stderr.strip()})
    result={'checked_at':dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat(timespec='seconds'),
            'html':report.relative_to(ROOT).as_posix(),'html_sha256':hashlib.sha256(report.read_bytes()).hexdigest(),
            'systems':len(summary['systems']),'capability_clauses':sum(len(s['capabilities']) for s in summary['systems']),
            'unique_source_or_link_paths':len(refs),'missing_paths':sorted(set(missing)),
            'out_of_range_evidence_lines':bad_lines,'inline_js_checks':js_results,
            'scope':'静态文档/来源核验；未实际渲染浏览器，不代表游戏或界面端到端验收。'}
    result['passed']=not missing and not bad_lines and all(v['exit_code']==0 for v in js_results)
    (LOG/'report-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if not result['passed']:raise SystemExit(1)


if __name__=='__main__':main()
