"""修订99：撤销贸易后同步更新页说明，保留历史审核页面。"""
from pathlib import Path
import json
import re
ROOT = Path(__file__).resolve().parents[1]
p = ROOT/'src/main/resources/assets/hk3gtl/narrative/approved.json'
d = json.loads(p.read_text(encoding='utf-8'))
next(e for e in d['entries'] if e['id']=='update.U16')['title']='贸易功能撤下'
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for locale in ('zh_cn','en_us'):
    p=ROOT/f'src/main/resources/assets/hk3gtl/lang/{locale}.json'
    d=json.loads(p.read_text(encoding='utf-8'))
    d.pop('hk3gtl.prose.system.trade',None)
    wording=('贸易功能撤下','本次版本已移除五方贸易、报价和订单功能。','手机继续提供通知、信件、更新详情和IF档案入口。') if locale=='zh_cn' else ('Trade removed','Faction trade, quotations and orders have been removed in this revision.','The phone still provides notifications, letters, update details and IF archives.')
    for suffix,value in zip(('title','line.0','line.1'),wording):
        key='hk3gtl.approved.update.U16.'+suffix
        assert key in d,key
        d[key]=value
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=ROOT/'doc/HK3GTL-内测5/11_系统专项/贸易系统/多模组贸易候选_v2/index.html'
s=p.read_text(encoding='utf-8')
archive=ROOT/'archive/trade-removed-r99-20260929-195020'/p.relative_to(ROOT)
archive.parent.mkdir(parents=True,exist_ok=True)
assert not archive.exists()
archive.write_bytes(p.read_bytes())
banner='<section style="padding:20px;background:#612829;color:white;font-size:20px"><strong>已撤销 · 2026-09-29</strong><p>负责人已决定删除贸易系统。本页只保留历史讨论，不再作为实施或报价依据。</p></section>'
s,n=re.subn(r'(<body[^>]*>)',lambda m:m.group(0)+banner,s,count=1)
assert n==1
p.write_text(s,encoding='utf-8')
print('Updated withdrawal text in both languages and historical page.')
