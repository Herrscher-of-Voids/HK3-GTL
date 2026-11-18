# -*- coding: utf-8 -*-
"""Revision55 initial tool; revision56 2026-09-23 restricts synchronization to existing libs only.
依赖同步：仅替换libs已有对应包，下载GTLAdditions优先；不再全量镜像实例。
"""
from pathlib import Path
from datetime import datetime
import zipfile,re,json,hashlib,shutil,sys
root=Path(__file__).resolve().parents[1]
mods=Path(r'C:\Users\OWNER\AppData\Roaming\PrismLauncher\instances\GregTech-Leisure-1.4.5.2\minecraft\mods')
download=Path(r'C:\Users\OWNER\下載\gtladditions-3.3.jar')
def metadata(p):
    with zipfile.ZipFile(p) as z:
        if 'META-INF/mods.toml' in z.namelist():
            text=z.read('META-INF/mods.toml').decode('utf-8-sig')
            blocks=re.findall(r'\[\[mods\]\](.*?)(?=\[\[|\Z)',text,re.S)
            ids=[]
            for block in blocks:
                match=re.search(r'^\s*modId\s*=\s*[\"\']([^\"\']+)',block,re.M)
                if match: ids.append(match.group(1))
            return ids
        if 'fabric.mod.json' in z.namelist(): return [json.loads(z.read('fabric.mod.json'))['id']]
    return []
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()
assert download.is_file() and 'gtladditions' in metadata(download), 'Expected GTLAdditions download'
sources={}
for p in mods.glob('*.jar'):
    ids=metadata(p)
    if 'hk3gtl' in ids: continue
    if 'gtladditions' in ids: continue
    for mod in ids:
        if mod in sources: raise RuntimeError('Duplicate instance mod ID: '+mod)
        sources[mod]=p
sources['gtladditions']=download
selected={download.name:download}
for existing in (root/'libs').glob('*.jar'):
    for mod in metadata(existing):
        if mod in sources:
            p=sources[mod]; selected[p.name]=p
    # Metadata-free library jars may only replace an already-present exact filename.
    candidate=mods/existing.name
    if not metadata(existing) and candidate.is_file(): selected[candidate.name]=candidate
replacements=[]; retained=[]
for old in (root/'libs').glob('*.jar'):
    matches={sources[i] for i in metadata(old) if i in sources}
    if len(matches)>1: raise RuntimeError('Ambiguous replacement for '+old.name)
    if matches:
        new=matches.pop()
        if old.name!=new.name or sha(old)!=sha(new): replacements.append((old,new))
    else:retained.append(old.name)
print('Instance source jars:',len(selected),'Replacement jars:',len(replacements),'Source size MiB:',sum(p.stat().st_size for p in selected.values())//1048576)
for old,new in replacements: print(old.name,'->',new.name)
print('Project-only retained:',retained)
if '--apply' not in sys.argv: sys.exit(0)
stamp=datetime.now().strftime('%Y-%m-%d_%H-%M-%S'); archive=root/'archive'/('dependency-sync-'+stamp)
archive.mkdir(parents=True)
for name in ['build.gradle','gradle.properties','tools/deploy_research_terminal.py']:
    dest=archive/name; dest.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(root/name,dest)
for old,new in replacements:
    dest=archive/'libs'/old.name; dest.parent.mkdir(parents=True,exist_ok=True)
    # Both targets are fixed descendants of the project; retain old jars outside active libs.
    assert old.resolve().parent==(root/'libs').resolve() and archive.resolve().is_relative_to(root.resolve())
    old.rename(dest)
records=[]
for name,source in selected.items():
    target=root/'libs'/name
    digest=sha(source)
    if not target.exists() or sha(target)!=digest: shutil.copy2(source,target)
    assert sha(target)==digest
    records.append(dict(file=name,ids=metadata(source),source=str(source),sha256=digest))
# Activate the explicitly requested new GTLAdditions in the user's instance as well.
instance_backup=mods.parent/'hk3gtl-mod-backups'/('gtladditions-'+stamp)
for old in list(mods.glob('*.jar')):
    if 'gtladditions' in metadata(old) and (old.name!=download.name or sha(old)!=sha(download)):
        instance_backup.mkdir(parents=True,exist_ok=True)
        assert old.resolve().parent==mods.resolve()
        old.rename(instance_backup/old.name)
shutil.copy2(download,mods/download.name)
assert sha(mods/download.name)==sha(download)
# Update only already-declared local dependencies; copied client-only mods are not all added to Gradle.
p=root/'build.gradle'; s=p.read_text(encoding='utf-8')
for old,new in replacements:
    s=s.replace(old.name,new.name).replace('dev:'+old.stem+'"','dev:'+new.stem+'"')
s+='\n// Change #7 '+stamp+' revision55: align declared local dependencies with the user instance; archive old JARs.\n'
s+='// Only existing corresponding libraries are synchronized; no complete instance mirror.\n'
p.write_text(s,encoding='utf-8')
report=dict(stamp=stamp,replacements=[dict(old=a.name,new=b.name) for a,b in replacements],retained=retained,jars=records,archive=str(archive),instance_backup=str(instance_backup))
(archive/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(root/'tools/dependency_sync_latest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Verified',len(records),'JAR hashes. Archive:',archive)
