"""修订106部署：核对已暂存修复包，保存旧包后更新两个已授权实例。
变更记录 #1 · 2026-09-30 01:44:01 · 修订106。
删除：无；新增：游戏进程优先于Gradle识别的安全检查；修改：仅两个实例的HK3GTL包。
用途：游戏命令行也可能含Gradle缓存路径，不能仅用“不含Gradle”来判断游戏退出。
"""
from pathlib import Path
import datetime, hashlib, json, shutil, subprocess, zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'logs/research-audit-r106'
SOURCE = OUT / 'hk3gtl-0.5.0.jar'
BASE = Path('C:/Users/OWNER/AppData/Roaming/PrismLauncher/instances')
NAMES = ['GregTech-Leisure-1.4.5.2', 'GregTech Leisure-增强版「巨构时代」 2.1']

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def active_games():
    # 只输出游戏进程ID，绝不输出可能含令牌的启动参数。
    command = "@(Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^java(w)?[.]exe$' -and $_.CommandLine -match 'org.prismlauncher|BootstrapLauncher|net.minecraft.client.main.Main|cpw.mods.modlauncher.Launcher' } | Select-Object -ExpandProperty ProcessId) | ConvertTo-Json -Compress"
    result = subprocess.run(['powershell','-NoProfile','-Command',command],capture_output=True,text=True,check=True)
    return json.loads(result.stdout) if result.stdout.strip() else []

def save(status):
    (OUT/'delivery-status.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf-8')

def main():
    status=json.loads((OUT/'delivery-status.json').read_text(encoding='utf-8'))
    assert sha(SOURCE)==status['jar_sha256'], '暂存包哈希变化，停止部署'
    with zipfile.ZipFile(SOURCE) as z:
        assert json.loads(z.read('assets/hk3gtl/changelog.json'))['entries'][0]['revision']==106
    status['last_checked_at']=datetime.datetime.now().astimezone().isoformat()
    for i,name in enumerate(NAMES,1):
        running=active_games()
        if running:
            status.update(status='WAITING_FOR_GAME_EXIT',active_game_pids=running,deployed=False)
            save(status);print(json.dumps(status,ensure_ascii=False,indent=2));return 2
        target=BASE/name/'minecraft/mods/hk3gtl-0.5.0.jar'
        assert target.is_file()
        if sha(target)==sha(SOURCE): continue
        backup=OUT/'instance-backups'/str(i)/target.name
        assert not backup.exists(), '备份已存在，须人工核对而非覆盖'
        backup.parent.mkdir(parents=True,exist_ok=True)
        previous=sha(target);shutil.copy2(target,backup);assert sha(backup)==previous
        if active_games():
            status.update(status='WAITING_FOR_GAME_EXIT',deployed=False);save(status);return 2
        shutil.copy2(SOURCE,target);assert sha(target)==sha(SOURCE)
        status.setdefault('instances',[]).append(dict(instance=name,target=str(target),backup=str(backup),previous_sha256=previous,sha256=sha(target)))
        save(status)
    status.update(status='DEPLOYED_WAITING_FOR_GAME_ACCEPTANCE',deployed=True,active_game_pids=[])
    save(status);print(json.dumps(status,ensure_ascii=False,indent=2));return 0

if __name__=='__main__':
    raise SystemExit(main())
