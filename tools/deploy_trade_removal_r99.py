"""修订99：校验贸易已移除，备份并更新两个指定实例；不改存档或依赖。"""
from pathlib import Path
from datetime import datetime
import hashlib
import json
import shutil
import subprocess
import zipfile
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'build/libs/hk3gtl-0.5.0.jar'
PRISM=Path('C:/Users/OWNER/AppData/Roaming/PrismLauncher/instances')
INSTANCES={'base':PRISM/'GregTech-Leisure-1.4.5.2/minecraft','enhanced':PRISM/'GregTech Leisure-增强版「巨构时代」 2.1/minecraft'}
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
with zipfile.ZipFile(SOURCE) as jar:
    names=jar.namelist()
    assert not [n for n in names if '/common/trade/' in n or '/client/trade/' in n or 'trade_fulfillment_terminal' in n or n.startswith('data/hk3gtl/trade/')]
    assert any(n.endswith('/client/phone/Hk3PhoneScreen.class') for n in names)
    assert json.loads(jar.read('assets/hk3gtl/changelog.json'))['entries'][0]['revision']==99
    prose=json.loads(jar.read('assets/hk3gtl/narrative/approved.json'))
    assert len(prose['entries'])==644 and all(e['system']!='trade' for e in prose['entries'])
    for lang in ('zh_cn','en_us'):
        packed=jar.read(f'assets/hk3gtl/lang/{lang}.json')
        assert packed==(ROOT/f'src/main/resources/assets/hk3gtl/lang/{lang}.json').read_bytes(), 'Stale packaged resources'
    for n in names:
        if n.endswith('.class') and n.startswith('com/sirin/hk3gtl/'):
            data=jar.read(n)
            assert b'Hk3Trade' not in data and b'hk3trade' not in data,n
cmd="Get-CimInstance Win32_Process -Filter \"Name='javaw.exe' OR Name='java.exe'\" | ForEach-Object { $p = Get-Process -Id $_.ProcessId -ErrorAction SilentlyContinue; [PSCustomObject]@{id=$_.ProcessId; command=$_.CommandLine; title=$p.MainWindowTitle} } | ConvertTo-Json -Compress"
# 由PowerShell作为单一shell读取状态，不停止任何进程。
cmd=cmd.replace('\\"','\"')
raw=subprocess.run(['powershell','-NoProfile','-Command',cmd],capture_output=True,text=True,check=True).stdout
processes=json.loads(raw) if raw.strip() else []
if isinstance(processes,dict): processes=[processes]
for process in processes:
    command=(process.get('command') or '').lower()
    title=process.get('title') or ''
    for instance in INSTANCES.values():
        assert str(instance.parent).lower() not in command and instance.parent.name.lower() not in command, 'Target instance running'
    if 'net.minecraft.client.main.main' in command or 'bootstraplauncher' in command:
        assert title=='Infinity Legacy II', 'Unidentified Minecraft process: stop deployment'
for instance in INSTANCES.values():
    assert instance.is_dir() and (instance/'mods/hk3gtl-0.5.0.jar').is_file()
    assert len(list((instance/'mods').glob('hk3gtl*.jar')))==1
now=datetime.now()
report={'revision':99,'time':now.isoformat(),'source_sha256':sha(SOURCE),'artifact_checks':'passed','instances':{}}
for profile,instance in INSTANCES.items():
    target=instance/'mods/hk3gtl-0.5.0.jar'
    config=instance/'config/hk3gtl/trade-offers.json'
    backup=instance/f'hk3gtl-backups/{now:%Y%m%d-%H%M%S}-before-r99-removal'
    backup.mkdir(parents=True,exist_ok=False)
    shutil.copy2(target,backup/target.name)
    assert sha(target)==sha(backup/target.name)
    if config.exists():
        shutil.copy2(config,backup/'trade-offers.json')
        assert sha(config)==sha(backup/'trade-offers.json')
    shutil.copy2(SOURCE,target)
    assert sha(target)==sha(SOURCE)
    if config.exists(): config.unlink()
    assert not config.exists()
    report['instances'][profile]={'path':str(instance),'backup':str(backup),'sha256':sha(target),'trade_config_removed':True}
log=ROOT/'logs/trade-removal-r99'
(log/'delivery.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
source=json.loads((log/'source-removal.json').read_text(encoding='utf-8'))
record=Path(source['discussion'])
s=record.read_text(encoding='utf-8')
s=s.replace('</body>',f'<h2>验证与部署结果 · {now:%Y-%m-%d %H:%M:%S}</h2><p>clean build及回归检查通过。最终JAR已确认无五方贸易类、命令、T02资源和报价。原版与增强版两个指定实例已备份替换，并移除活动报价配置；文件哈希一致。未更换任何定制依赖，未改玩家存档。未进行游戏内启动或FCL验证。</p></body>')
record.write_text(s,encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
