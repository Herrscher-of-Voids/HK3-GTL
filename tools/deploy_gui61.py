# -*- coding: utf-8 -*-
"""Change #1 2026-09-23: deploy only verified HK3GTL revision61.
仅备份替换目标实例HK3GTL；检测游戏运行时拒绝，其他模组/存档不变。
"""
from pathlib import Path
from datetime import datetime
import subprocess, json, zipfile, hashlib, shutil, re

root=Path(__file__).resolve().parents[1]
processes=subprocess.check_output(['powershell','-NoProfile','-Command',
    "Get-CimInstance Win32_Process -Filter \"name = 'javaw.exe'\" | Select-Object ProcessId,CommandLine | ConvertTo-Json -Compress"],text=True).strip()
if processes and processes!='null':
    raise SystemExit('Game/javaw is running; close normally before replacing its loaded JAR.')
source=root/'build/libs/hk3gtl-0.5.0.jar'
with zipfile.ZipFile(source) as z:
    assert json.loads(z.read('assets/hk3gtl/changelog.json'))['entries'][0]['revision']==61
    assert 'com/sirin/hk3gtl/client/gui/Hk3FittedScreen.class' in z.namelist()
mods=Path(r'C:\Users\OWNER\AppData\Roaming\PrismLauncher\instances\GregTech-Leisure-1.4.5.2\minecraft\mods')
assert mods.is_dir()
old=[]
for p in mods.glob('*.jar'):
    try:
        with zipfile.ZipFile(p) as z: meta=z.read('META-INF/mods.toml').decode()
        if re.search(r'modId\s*=\s*[\"\x27]hk3gtl[\"\x27]',meta): old.append(p)
    except (KeyError,zipfile.BadZipFile): pass
assert len(old)==1, f'Expected one installed HK3GTL, found {old}'
backup=mods.parent/'hk3gtl-mod-backups'/('gui61-'+datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
backup.mkdir(parents=True)
digest=lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
shutil.copy2(old[0],backup/old[0].name)
assert digest(old[0])==digest(backup/old[0].name)
stage=mods/(old[0].name+'.pending')
shutil.copy2(source,stage)
assert digest(source)==digest(stage)
stage.replace(old[0])
assert digest(source)==digest(old[0])
print('Installed:',old[0])
print('SHA256:',digest(old[0]))
print('Backup:',backup)
(backup/'deployment.txt').write_text(f'Revision61\n{old[0]}\nSHA256 {digest(old[0])}\nBuild and coordinate tests passed; in-game UI acceptance pending.\n',encoding='utf-8')
