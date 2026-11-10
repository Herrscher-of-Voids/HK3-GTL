"""#1 2026-09-23: verified local Prism deployment, old JARs retained outside mods.
验证class及元数据后部署用户指定实例；同modId旧文件归档，不删除存档或配置。
Checks classes/metadata and archives same-mod-ID jars without touching saves/config.
"""
from pathlib import Path
from datetime import datetime
import hashlib, shutil, zipfile, re, json
mods=Path(r'C:\Users\OWNER\AppData\Roaming\PrismLauncher\instances\GregTech-Leisure-1.4.5.2\minecraft\mods')
assert mods.is_dir()
sources=[Path('build/libs/hk3gtl-0.5.0.jar'),Path('libs/GTLsupb-3.5.jar')]
with zipfile.ZipFile(sources[0]) as z:
    assert 'com/sirin/hk3gtl/common/gui/Hk3ResearchTerminalWidget.class' in z.namelist()
    assert any(e.get('revision')==51 for e in json.loads(z.read('assets/hk3gtl/changelog.json'))['entries'])
with zipfile.ZipFile(sources[1]) as z:
    assert re.search(r'version\s*=\s*[\"\']3\.5[\"\']',z.read('META-INF/mods.toml').decode())
stamp=datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
backup=mods.parent/'hk3gtl-mod-backups'/stamp
backup.mkdir(parents=True)
old=[]
for p in mods.glob('*.jar'):
    try:
        with zipfile.ZipFile(p) as z:
            meta=z.read('META-INF/mods.toml').decode()
        if re.search(r'modId\s*=\s*[\"\'](?:hk3gtl|gtlsupb)[\"\']',meta):
            old.append(p)
    except (KeyError,zipfile.BadZipFile):
        continue
# 先备份全部目标，失败则不开始替换。 Back up all targets before changing active mods.
for p in old:
    shutil.copy2(p,backup/p.name)
    assert hashlib.sha256(p.read_bytes()).digest()==hashlib.sha256((backup/p.name).read_bytes()).digest()
# 将旧活动文件移到已核实备份目录，保留唯一生效JAR。 Retire old active jars to the verified backup directory.
for p in old:
    p.rename(backup/('active-'+p.name))
for source in sources:
    target=mods/source.name
    shutil.copy2(source,target)
    digest=hashlib.sha256(source.read_bytes()).hexdigest()
    assert digest==hashlib.sha256(target.read_bytes()).hexdigest()
    print(target, digest)
print('Backup:',backup)

# Change #2 2026-09-23 03:12:15: deploy the explicit 0.5.0 runtime JAR, never the sources JAR.
