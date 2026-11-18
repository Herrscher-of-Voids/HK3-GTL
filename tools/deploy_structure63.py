# -*- coding: utf-8 -*-
"""变更记录 #1 · 2026-09-24 00:16:00 · 修订63。
校验构建包后仅备份并替换指定实例HK3GTL，拒绝运行中的游戏；不更换其他依赖。
Verify and deploy only HK3GTL to the requested instance, with hash-verified backup and running-game guard.
"""
from pathlib import Path
from datetime import datetime
import subprocess,json,zipfile,hashlib,shutil,re,argparse

# 变更记录 #2 · 2026-09-24 01:02:29 · 修订64。
# 新增显式修订参数，保留原63默认；复用备份、进程检查和哈希验证，不为每次构建增加临时部署脚本。
# Explicit revision argument reuses process guards/backups/hash checks; legacy revision63 remains the default.
parser=argparse.ArgumentParser()
parser.add_argument('--revision',type=int,default=63)
revision=parser.parse_args().revision
if revision < 63: raise SystemExit('This deployer requires approved structures from revision63 or later.')

root=Path(__file__).resolve().parents[1]
instance=Path('C:/Users/OWNER/AppData/Roaming/PrismLauncher/instances/GregTech-Leisure-1.4.5.2/minecraft')
mods=instance/'mods';source=root/'build/libs/hk3gtl-0.5.0.jar'
processes=subprocess.check_output(['powershell','-NoProfile','-Command',
    "Get-CimInstance Win32_Process -Filter \"name = 'javaw.exe' OR name = 'java.exe'\" | Select-Object ProcessId,CommandLine | ConvertTo-Json -Compress"],text=True,encoding='utf8',errors='replace').strip()
rows=json.loads(processes) if processes else []
if isinstance(rows,dict):rows=[rows]
for row in rows:
    args=row.get('CommandLine') or ''
    if 'GregTech-Leisure-1.4.5.2' in args:raise SystemExit('The target instance is running; close it before deployment.')
with zipfile.ZipFile(source) as z:
    assert json.loads(z.read('assets/hk3gtl/changelog.json'))['entries'][0]['revision']==revision
    for id in ['i01','i02']:
        name='data/hk3gtl/structures/approved/'+id+'.nbt'
        assert z.read(name)==(root/'src/main/resources'/name).read_bytes()
        assert z.read('assets/hk3gtl/textures/block/overlay/'+id+'/overlay_front.png').startswith(b'\x89PNG')
    for cls in ['Hk3I01CollectionPatternImpl','Hk3I02SpectrumPatternImpl','Hk3StructureBlocks']:
        assert 'com/sirin/hk3gtl/common/multiblock/pattern/'+cls+'.class' in z.namelist()
    # 修订70：四台正式模板、逐格资源及专用控制器三状态纹理必须全部进入发布包。
    if revision >= 70:
        for key in ['i01','i02','i03','s01']:
            for name in ['data/hk3gtl/structures/approved/'+key+'.nbt',
                         'data/hk3gtl/approved_architecture/'+key+'.json']:
                assert z.read(name)==(root/'src/main/resources'/name).read_bytes()
            for suffix in ['', '_active', '_paused']:
                assert z.read('assets/hk3gtl/textures/block/overlay/'+key+'_v2/overlay_front'+suffix+'.png').startswith(b'\x89PNG')
        assert 'com/sirin/hk3gtl/common/multiblock/pattern/Hk3ApprovedArchitecturePatterns.class' in z.namelist()
installed=[]
for p in mods.glob('*.jar'):
    try:
        with zipfile.ZipFile(p) as z:meta=z.read('META-INF/mods.toml').decode('utf8')
        if re.search(r'modId\s*=\s*[\"\x27]hk3gtl[\"\x27]',meta):installed.append(p)
    except (KeyError,zipfile.BadZipFile):pass
assert len(installed)==1,installed
backup=instance/'hk3gtl-mod-backups'/('revision'+str(revision)+'-'+datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
backup.mkdir(parents=True)
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
shutil.copy2(installed[0],backup/installed[0].name)
assert digest(installed[0])==digest(backup/installed[0].name)
pending=installed[0].with_suffix('.jar.pending');shutil.copy2(source,pending)
assert digest(pending)==digest(source)
pending.replace(installed[0]);assert digest(installed[0])==digest(source)
result=dict(revision=revision,installed=str(installed[0]),backup=str(backup),sha256=digest(source))
(backup/'deployment.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(result,ensure_ascii=False,indent=2))
