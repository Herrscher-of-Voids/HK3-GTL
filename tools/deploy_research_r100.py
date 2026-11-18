"""研究修订100交付：要求clean build通过且指定实例关闭，校验JAR后备份替换。
只改两处HK3GTL JAR；失败回滚已替换目标，不修改存档、配置或其他模组。
"""
from pathlib import Path
from datetime import datetime
import hashlib,json,zipfile,subprocess,shutil,os,re,html
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'logs/research-mainline-r100'
SOURCE=ROOT/'build/libs/hk3gtl-0.5.0.jar'
PRISM=Path('C:/Users/OWNER/AppData/Roaming/PrismLauncher/instances')
INSTANCES={'base':PRISM/'GregTech-Leisure-1.4.5.2/minecraft','enhanced':PRISM/'GregTech Leisure-增强版「巨构时代」 2.1/minecraft'}
# Python3.10没有file_digest，流式读取避免JAR整体驻留内存。
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for part in iter(lambda:f.read(1024*1024),b''):h.update(part)
 return h.hexdigest()

build=(OUT/'final-build.log').read_text(encoding='utf-8',errors='replace')
assert 'BUILD SUCCESSFUL' in build and 'BUILD FAILED' not in build
tests=re.findall(r'^> Task :(run\w+Test)\s*$',build,re.M)
assert 'runResearchTeamTest' in tests and 'runLabExperimentTest' in tests
manifest=json.loads((OUT/'source-manifest.json').read_text(encoding='utf-8'))
for item in manifest['files']:assert sha(ROOT/item['path'])==item['sha256'],f"Source changed since clean build: {item['path']}"
with zipfile.ZipFile(SOURCE) as jar:
 names=set(jar.namelist())
 for suffix in ['common/research/Hk3ResearchTeams.class','common/research/Hk3LabExperimentService.class','common/command/Hk3ResearchAccountCommands.class']:
  assert 'com/sirin/hk3gtl/'+suffix in names,suffix
 assert not any('/common/trade/' in n or '/client/trade/' in n or n.startswith('data/hk3gtl/trade/') for n in names)
 assert not any(n.startswith('dev/ftb/mods/ftbteams/') for n in names),'Optional dependency must not be bundled'
 costs=json.loads(jar.read('data/hk3gtl/research/research_costs.json'))['topics']
 assert len(costs)==100 and sum(t['points'] for t in costs)==255750
 assert json.loads(jar.read('assets/hk3gtl/changelog.json'))['entries'][0]['revision']==100
 for resource in ['assets/hk3gtl/lang/zh_cn.json','assets/hk3gtl/lang/en_us.json','data/hk3gtl/research/research_costs.json']:
  assert jar.read(resource)==(ROOT/'src/main/resources'/resource).read_bytes(),resource
 assert b'Hk3ResearchTeams' in jar.read('com/sirin/hk3gtl/Hk3Gtl.class')

command="Get-CimInstance Win32_Process -Filter \"Name='javaw.exe' OR Name='java.exe'\" | ForEach-Object { $taskProcess=Get-Process -Id $_.ProcessId -ErrorAction SilentlyContinue; [PSCustomObject]@{id=$_.ProcessId; command=$_.CommandLine; title=$taskProcess.MainWindowTitle} } | ConvertTo-Json -Compress"
raw=subprocess.run(['powershell','-NoProfile','-Command',command],capture_output=True,text=True,check=True).stdout
processes=json.loads(raw) if raw.strip() else []
if isinstance(processes,dict):processes=[processes]
for proc in processes:
 cmd=(proc.get('command') or '').lower();title=proc.get('title') or ''
 for instance in INSTANCES.values():
  assert str(instance.parent).lower() not in cmd and instance.parent.name.lower() not in cmd,'Target instance running; no deployment'
 if 'net.minecraft.client.main.main' in cmd or 'bootstraplauncher' in cmd:
  assert title=='Infinity Legacy II','Unidentified running Minecraft; no deployment'

now=datetime.now().astimezone();report={'revision':100,'time':now.isoformat(),'source_sha256':sha(SOURCE),'build':'clean build passed','checks':tests,'gameplay_verified':False,'instances':{}}
prepared=[]
for profile,instance in INSTANCES.items():
 target=instance/'mods/hk3gtl-0.5.0.jar'
 assert target.is_file() and len(list((instance/'mods').glob('hk3gtl*.jar')))==1
 backup=instance/f'hk3gtl-backups/{now:%Y%m%d-%H%M%S}-before-r100-research'
 backup.mkdir(parents=True,exist_ok=False)
 shutil.copy2(target,backup/target.name)
 old_hash=sha(target);assert old_hash==sha(backup/target.name)
 staging=backup/'verified-new-r100.jar';shutil.copy2(SOURCE,staging);assert sha(staging)==report['source_sha256']
 others={p.name:(p.stat().st_size,p.stat().st_mtime_ns) for p in (instance/'mods').iterdir() if p.is_file() and p!=target}
 prepared.append((profile,instance,target,backup,staging,old_hash,others))

replaced=[]
try:
 for profile,instance,target,backup,staging,old_hash,others in prepared:
  os.replace(staging,target);replaced.append((target,backup/target.name))
  assert sha(target)==report['source_sha256']
  current={p.name:(p.stat().st_size,p.stat().st_mtime_ns) for p in (instance/'mods').iterdir() if p.is_file() and p!=target}
  assert current==others,'Unrelated mod files changed during delivery'
  report['instances'][profile]={'path':str(instance),'backup':str(backup),'old_sha256':old_hash,'sha256':sha(target),'other_mod_files_unchanged':True,
      'ftb_team_jars':[n for n in others if 'ftb-teams' in n.lower() or 'ftbteams' in n.lower()]}
except Exception:
 for target,backup in replaced:shutil.copy2(backup,target)
 raise
(OUT/'delivery.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
record=Path(manifest['discussion']);text=record.read_text(encoding='utf-8')
summary=f'<h2>最终验证与实例交付 · {now:%Y-%m-%d %H:%M:%S}</h2><p>clean build通过，执行{len(tests)}个自定义验证任务（并执行Gradle构建任务）。JAR中的100课题成本、语言资源、新账本与实验类已经核验；没有打回贸易代码，也没有打包FTB依赖副本。</p><p>两个指定GTL实例均已备份并替换为修订100，其他mods文件大小和修改时间未变。源包与两实例SHA-256：<code>{report["source_sha256"]}</code>。客户端／服务端协议14。</p><p class="warn">没有启动整合包；GUI、FTB真实联机事件、实际物品标签和生存链路仍须游戏验收。测试中的构造状态不代表玩家已能取得全部实验材料或进入S02。</p><p>验证任务：{html.escape(", ".join(tests))}。详细部署回执：<code>logs/research-mainline-r100/delivery.json</code>。</p>'
text=text.replace('</html>',summary+'</html>');record.write_text(text,encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
