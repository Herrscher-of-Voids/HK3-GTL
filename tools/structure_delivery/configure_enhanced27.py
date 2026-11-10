# -*- coding: utf-8 -*-
"""变更记录 #1 · 2026-10-15 02:06:20 · 内测5修订157。
删除：无；新增：资源包恢复和实例专用内存调整模式，修改前逐文件备份。
修改：只写目标实例相关键；用途：同一资源包组合对比，不修改全局启动器或玩家存档。
"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import json, os, shutil, sys

ROOT=Path(__file__).resolve().parents[2]
INSTANCE=Path(os.environ['APPDATA'])/'PrismLauncher/instances/GregTech Leisure-增强版 2.7'
GAME=INSTANCE/'minecraft'
BACKUP=GAME/'hk3gtl-mod-backups/20261015_014243_enhanced27_r156/settings-before/minecraft/options.txt'
mode=sys.argv[1]
stamp=datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d_%H%M%S')
folder=GAME/'hk3gtl-mod-backups'/f'{stamp}_settings_{mode}'
folder.mkdir(parents=True)
for path in [GAME/'options.txt',INSTANCE/'instance.cfg']:
    shutil.copy2(path,folder/path.name)
options=(GAME/'options.txt').read_text(encoding='utf-8')
original=BACKUP.read_text(encoding='utf-8')

def replace_keys(text, replacements):
    lines=text.splitlines()
    remaining=dict(replacements)
    for i,line in enumerate(lines):
        key=line.split(':',1)[0]
        if key in remaining: lines[i]=key+':'+remaining.pop(key)
    return '\n'.join(lines+[k+':'+v for k,v in remaining.items()])+'\n'

if mode=='restore-packs':
    keys={line.split(':',1)[0]:line.split(':',1)[1] for line in original.splitlines()
          if line.startswith(('resourcePacks:','incompatibleResourcePacks:'))}
    options=replace_keys(options,keys)
    (GAME/'options.txt').write_text(options,encoding='utf-8')
elif mode=='optimize':
    options=replace_keys(options,{'renderDistance':'12','simulationDistance':'8'})
    (GAME/'options.txt').write_text(options,encoding='utf-8')
    cfg=(INSTANCE/'instance.cfg').read_text(encoding='utf-8-sig')
    lines=cfg.splitlines()
    values={'OverrideMemory':'true','MinMemAlloc':'1024','MaxMemAlloc':'8192'}
    insert=next((i for i,l in enumerate(lines) if l.startswith('[') and l!='[General]'),len(lines))
    for key,value in values.items():
        found=next((i for i,l in enumerate(lines[:insert]) if l.startswith(key+'=')),None)
        if found is None: lines.insert(insert,key+'='+value);insert+=1
        else: lines[found]=key+'='+value
    (INSTANCE/'instance.cfg').write_text('\n'.join(lines)+'\n',encoding='utf-8')
else:
    raise ValueError(mode)
receipt={'mode':mode,'time':stamp,'instance':str(INSTANCE),'backup':str(folder),
         'resourcepacks':next(l for l in options.splitlines() if l.startswith('resourcePacks:')),
         'renderDistance':next(l for l in options.splitlines() if l.startswith('renderDistance:')),
         'simulationDistance':next(l for l in options.splitlines() if l.startswith('simulationDistance:'))}
(ROOT/'logs/enhanced27-memory-20261015'/f'config-{mode}-{stamp}.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(receipt,ensure_ascii=False,indent=2))
