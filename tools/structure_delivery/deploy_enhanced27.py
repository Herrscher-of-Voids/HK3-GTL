# -*- coding: utf-8 -*-
"""变更记录 #1 · 2026-10-15 02:05:00 · 内测5修订157。
职责：仅部署负责人指定增强版2.7实例，核对JAR身份、资源和SHA并保存可回滚备份。
删除：无；新增：清单确认的JECharacters重复项隔离、每次部署收据；修改：测试目标。
用途：初次集成和优化后复测共用，不修改玩家存档、不修改其他实例；启动中拒绝替换。
"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib, json, os, re, shutil, subprocess, zipfile

ROOT = Path(__file__).resolve().parents[2]
INSTANCE = Path(os.environ['APPDATA']) / 'PrismLauncher/instances/GregTech Leisure-增强版 2.7'
GAME = INSTANCE / 'minecraft'
LOG = ROOT / 'logs/enhanced27-memory-20261015'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def ids(path):
    with zipfile.ZipFile(path) as archive:
        text = archive.read('META-INF/mods.toml').decode('utf-8')
    return [m.group(1) for section in re.findall(r'^\s*\[\[mods\]\]([^\[]*)', text, re.M)
            for m in [re.search(r'^\s*modId\s*=\s*[\"\']([^\"\']+)', section, re.M)] if m]

def main():
    ps = "@(Get-CimInstance Win32_Process -Filter \"Name='java.exe' OR Name='javaw.exe'\" | Where-Object { $_.CommandLine -match 'forgeclient|org\\.multimc\\.EntryPoint|cpw\\.mods\\.modlauncher' }).Count"
    assert subprocess.check_output(['powershell.exe','-NoProfile','-Command',ps],text=True).strip() == '0', '游戏尚在运行'
    assert 'name=GregTech Leisure-增强版 2.7' in (INSTANCE/'instance.cfg').read_text(encoding='utf-8-sig')
    source = ROOT/'build/libs/hk3gtl-0.5.0.jar'
    assert ids(source) == ['hk3gtl']
    with zipfile.ZipFile(source) as archive:
        assert archive.testzip() is None
        keys = sorted(p.stem for p in (ROOT/'src/main/resources/data/hk3gtl/approved_architecture').glob('*.json'))
        assert len(keys) == 21
        for key in keys:
            for folder,ext in [('approved_architecture','json'),('structures/approved','nbt'),('structures/approved','json')]:
                name = f'data/hk3gtl/{folder}/{key}.{ext}'
                assert archive.read(name) == (ROOT/'src/main/resources'/name).read_bytes(), name
        revision=json.loads(archive.read('assets/hk3gtl/changelog.json'))['entries'][0]['revision']
    stamp=datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d_%H%M%S')
    backup=GAME/'hk3gtl-mod-backups'/f'{stamp}_enhanced27_r{revision}'
    backup.mkdir(parents=True)
    LOG.mkdir(parents=True,exist_ok=True)
    mods=GAME/'mods'
    before={p.name:sha(p) for p in mods.glob('*.jar')}
    for p in [INSTANCE/'instance.cfg',GAME/'options.txt'] + list((GAME/'config').glob('*')):
        if p.is_file():
            dest=backup/'settings-before'/p.relative_to(INSTANCE)
            dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(p,dest)
    manifest=json.loads((INSTANCE/'mrpack/modrinth.index.json').read_text(encoding='utf-8'))
    official=[p for p in manifest['files'] if 'jecharacters' in p['path']]
    removed=[]
    redundant=mods/'jecharacters-1.20.1-forge-4.6.3-fix.jar'
    if redundant.exists():
        assert len(official)==1 and official[0]['path']=='mods/jecharacters-1.20.1-forge-4.6.11.jar'
        keep=mods/Path(official[0]['path']).name
        assert hashlib.sha1(keep.read_bytes()).hexdigest()==official[0]['hashes']['sha1']
        assert ids(redundant)==['jecharacters'] and ids(keep)==['jecharacters']
        removed.append(redundant)
    removed += [p for p in mods.glob('*.jar') if 'hk3gtl' in ids(p)]
    for p in removed:
        shutil.copy2(p,backup/p.name)
        assert sha(backup/p.name)==before[p.name]
    target=mods/'HK3GTL-内测5.jar'
    pending=mods/f'hk3gtl-{stamp}.pending'
    shutil.copy2(source,pending)
    assert sha(pending)==sha(source)
    for p in removed:
        p.unlink()
    os.replace(pending,target)
    after={p.name:sha(p) for p in mods.glob('*.jar')}
    assert all(after.get(name)==digest for name,digest in before.items() if name not in {p.name for p in removed})
    assert len([p for p in mods.glob('*.jar') if 'hk3gtl' in ids(p)])==1
    receipt={'instance':str(INSTANCE),'installed_jar':str(target),'revision':revision,'sha256':sha(target),
             'bytes':target.stat().st_size,'backup':str(backup),'removed':[p.name for p in removed],
             'unrelated_jars_unchanged':True,'before':before,'after':after,'time':stamp}
    out=LOG/f'deployment-r{revision}-{stamp}.json'
    out.write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in receipt.items() if k not in ('before','after')},ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
