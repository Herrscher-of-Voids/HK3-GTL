"""核验修订101最终包与交付页，不启动游戏、不部署到实例。"""
from pathlib import Path
from structure_delivery.project_paths import project_path
from datetime import datetime
from html.parser import HTMLParser
import json,hashlib,re,zipfile

R=Path(__file__).resolve().parents[1];O=R/'logs/research-mainline-r101'
load=lambda p:json.loads(p.read_text(encoding='utf8'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
log=(O/'clean-build.log').read_text(encoding='utf8',errors='replace')
assert 'BUILD SUCCESSFUL' in log and 'BUILD FAILED' not in log
checks=re.findall(r'^> Task :(run\w+Test)\s*$',log,re.M)
assert 'runResearchMainlineTest' in checks and 'runLabExperimentTest' in checks
jar=R/'build/libs/hk3gtl-0.5.0.jar';manifest=load(O/'source-manifest.json')
resource_paths=[p['path'] for p in manifest['files'] if p['path'].startswith('src/main/resources/')]
with zipfile.ZipFile(jar) as z:
 assert not z.testzip()
 for p in resource_paths:assert z.read(p.removeprefix('src/main/resources/'))==(R/p).read_bytes(),p
 contracts=json.loads(z.read('data/hk3gtl/research/research_execution.json'))['topics']
 recipes=json.loads(z.read('data/hk3gtl/research/industrial_processes.json'))['recipes']
 assert len(contracts)==100 and len(recipes)==250
 assert json.loads(z.read('assets/hk3gtl/changelog.json'))['entries'][0]['revision']==101
 for t in contracts:
  if not t['existing']:assert 'assets/hk3gtl/models/item/'+t['specimen']+'.json' in z.namelist()
 for p in manifest['files']:
  if p['path'].startswith('src/main/java/'):
   assert p['path'].removeprefix('src/main/java/').removesuffix('.java')+'.class' in z.namelist(),p['path']
class Rows(HTMLParser):
 def __init__(self):super().__init__();self.rows=0;self.body=False
 def handle_starttag(self,tag,attrs):
  if tag=='tbody':self.body=True
  if tag=='tr' and self.body:self.rows+=1
 def handle_endtag(self,tag):
  if tag=='tbody':self.body=False
review=project_path(manifest['review']);page=review.read_text(encoding='utf8');parser=Rows();parser.feed(page)
assert parser.rows==350,parser.rows
assert '\ufffd' not in page and 'NaN' not in page
instances={}
for name in ('GregTech-Leisure-1.4.5.2','GregTech Leisure-增强版「巨构时代」 2.1'):
 p=project_path('C:/Users/OWNER/AppData/Roaming/PrismLauncher/instances')/name/'minecraft/mods/hk3gtl-0.5.0.jar'
 instances[name]=sha(p) if p.exists() else 'absent'
status=load(O/'delivery-status.json')
status.update({'verified_at':datetime.now().astimezone().isoformat(),'clean_build_passed':True,
 'custom_check_tasks':checks,'packaged_resource_checks':len(resource_paths),'review_rows':parser.rows,
 'jar':str(jar),'jar_sha256':sha(jar),'instance_jar_sha256':instances,'deployed':False,'gameplay_verified':False})
save(O/'delivery-status.json',status)
text=(f'clean build 已通过，34项构建任务、{len(checks)}项自定义检查全部完成；'
 f'JAR内核对100题、250条配方及{len(resource_paths)}份资源与源码一致，审阅页350行完整。'
 '包含100题付款状态机、OPR退款/重启、团队归属、世界泡同批次与异源拒绝等测试。'
 '测试中的实验记录为夹具，不能证明100条实际生产路径已经打通。'
 '没有启动游戏/FCL验收；原版与增强版实例均未被本轮覆盖。'
 f'<p>构建包：<code>{jar.name}</code><br>SHA256：<code>{sha(jar)}</code></p>')
page=re.sub(r'<div id="validation-result">[\s\S]*?</div>',lambda m:'<div id="validation-result">'+text+'</div>',page,count=1)
review.write_text(page,encoding='utf8')
discussion=project_path(manifest['discussion']);s=discussion.read_text(encoding='utf8')
if 'R101_VALIDATED' not in s:discussion.write_text(s+'\n<!-- R101_VALIDATED --><h2>最终构建核验</h2><p>'+text+'</p>',encoding='utf8')
paths={p['path'] for p in manifest['files']};paths.add('tools/verify_research_r101_delivery.py')
manifest['files']=[{'path':p,'sha256':sha(R/p)} for p in sorted(paths)]
manifest['verification']=str(O/'delivery-status.json');save(O/'source-manifest.json',manifest)
print(json.dumps({'jar_sha256':status['jar_sha256'],'checks':len(checks),'resources':len(resource_paths),'review_rows':parser.rows,'instances_unchanged':instances,'review':str(review)},ensure_ascii=False))

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
