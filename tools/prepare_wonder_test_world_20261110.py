"""复制既有C9测试世界，保留原存档；不注入结构、成型位或研究资格。"""
import json,shutil
from pathlib import Path
import nbtlib
import deploy_industrial_build as base

ROOT=Path(__file__).resolve().parents[1]
LOG=ROOT/'logs/w01-w03-implementation-20261110'
base.target_process_guard()
source=base.INSTANCE/'minecraft/saves/HK3GTL_Farview_r226_ClientTest'
target=source.parent/'HK3GTL_W01_W02_W03_r239_Test'
assert not target.exists()
files={str(p.relative_to(source)):base.sha(p) for p in source.rglob('*') if p.is_file() and p.name!='session.lock'}
shutil.copytree(source,target,ignore=shutil.ignore_patterns('session.lock'))
assert all(base.sha(target/key)==value for key,value in files.items())
level=nbtlib.load(target/'level.dat');level['Data']['LevelName']=nbtlib.String(target.name);level.save()
(LOG/'test-world-copy.json').write_text(json.dumps(dict(source=str(source),target=str(target),source_files=files,
    copied_before_levelname_change=True,only_levelname_changed=True,structures_injected=False,formed_granted=False,research_granted=False),ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps(dict(world=target.name,files=len(files),bytes=sum(p.stat().st_size for p in target.rglob('*') if p.is_file()))))
