"""Verify and stage r219; replace the target only with a confirmed stopped client."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[2]
WORK=ROOT/'logs/native-distance-package-r219-20261108'
OUT=ROOT/'deliveries/内测5_r219_原生远景与无损压缩_20261108'
GAME=Path('C:/Users/OWNER/AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版/minecraft')


def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def main():
    source=ROOT/'build/libs/hk3gtl-0.5.0.jar'
    assert 'BUILD SUCCESSFUL' in (WORK/'validation-final.log').read_text(encoding='utf-8',errors='replace')
    runtime=json.loads((WORK/'runtime-verification.json').read_text(encoding='utf-8'));assert runtime['passed']
    resources=json.loads((WORK/'compact-resource-verification.json').read_text(encoding='utf-8'))
    assert len(resources['structures'])==52 and all(r['all_records_and_entities_equal'] and 'layout_records_sha256' in r for r in resources['structures'])
    with zipfile.ZipFile(source) as jar:
        names=jar.namelist();assert len(names)==len(set(names))
        assert not any(n.startswith(('data/hk3gtl/approved_architecture/','data/hk3gtl/structures/approved_preview/')) for n in names)
        assert not any(n.startswith('data/hk3gtl/structures/approved/') and n.endswith('.nbt') for n in names)
        assert len([n for n in names if n.startswith('data/hk3gtl/structures/compact/') and n.endswith('.bin.gz')])==52
        assert len([n for n in names if n.startswith('data/hk3gtl/compact_architecture/') and n.endswith('.json')])==52
        assert json.loads(jar.read('assets/hk3gtl/changelog.json'))['entries'][0]['revision']==219
        for name in ['com/sirin/hk3gtl/client/farview/Hk3FarViewRenderer.class','com/sirin/hk3gtl/common/farview/Hk3FarViewData.class',
                     'com/sirin/hk3gtl/common/multiblock/pattern/Hk3StructureStream.class','assets/hk3gtl/shaders/core/farview.fsh']:
            assert name in names
        assert not any('hk3hyperionacceptance' in n or 'distanthorizons' in n.lower() for n in names)
        hull=hashlib.sha256(jar.read('data/hk3gtl/structures/hyperion_construction.bin.gz')).hexdigest()
        assert hull=='a2d3a38c6a51da8f0c3ff31607a81de6dc9fc9b724c48643f83cdf79edfd5861'
        assert jar.testzip() is None
    previous_bytes=772696920
    package=dict(passed=True,revision=219,bytes=source.stat().st_size,previous_bytes=previous_bytes,
        reduction_percent=100*(1-source.stat().st_size/previous_bytes),sha256=sha(source),entries=len(names),
        duplicate_building_representations_removed=True,source_records_preserved=resources['total_blocks'],
        source_building_count=52,full_entity_nbt_retained=True,hyperion_source_sha256=hull,external_dependencies_added=0)
    assert package['bytes']<100*1024*1024
    save(WORK/'package-verification.json',package)
    OUT.mkdir(exist_ok=True);shutil.copy2(source,OUT/'HK3GTL-内测5-r219.jar')
    assert sha(OUT/'HK3GTL-内测5-r219.jar')==package['sha256']
    sys.path.insert(0,str(ROOT/'tools'))
    from deploy_industrial_build import target_process_guard
    try:guard=target_process_guard()
    except RuntimeError as blocked:
        save(WORK/'release.json',dict(passed=True,revision=219,installed=False,reason=str(blocked),
            client_launched=False,user_worlds_written=False,delivery=str(OUT/'HK3GTL-内测5-r219.jar'),sha256=package['sha256']))
        print(json.dumps({**package,'installed':False}));return
    backup=WORK/'deployment-backup';backup.mkdir(exist_ok=False)
    targets=[GAME/'mods/HK3GTL-内测5.jar',ROOT/'HK3GTL-内测5.jar']
    third_before={p.name:sha(p) for p in (GAME/'mods').glob('*.jar') if p!=targets[0]}
    copies=[]
    for i,target in enumerate(targets):
        prior=sha(target);assert prior=='ec513be41ae850fe162f71ca2da59ee81fa77b6a2614e0b8d72ddd9c23366ca5'
        saved=backup/f'{i}-r218.jar'
        if i:os.link(backup/'0-r218.jar',saved)
        else:shutil.copy2(target,saved)
        assert sha(saved)==prior
        temporary=target.with_suffix('.r219-tasktmp');shutil.copy2(source,temporary);assert sha(temporary)==package['sha256']
        temporary.replace(target);assert sha(target)==package['sha256']
        copies.append({'path':str(target),'sha256':package['sha256'],'backup':str(saved)})
    alias=ROOT/'build/libs/HK3GTL-内测5.jar'
    if alias.exists() and sha(alias)!='ec513be41ae850fe162f71ca2da59ee81fa77b6a2614e0b8d72ddd9c23366ca5':
        raise RuntimeError("构建别名不是预期r218，保留原文件")
    shutil.copy2(source,alias);assert sha(alias)==package['sha256']
    assert third_before=={p.name:sha(p) for p in (GAME/'mods').glob('*.jar') if p!=targets[0]}
    release=dict(passed=True,revision=219,installed=True,guard=guard,copies=copies,
        third_party_jars_unchanged=len(third_before),client_launched=False,user_worlds_written=False,
        delivery=str(OUT/'HK3GTL-内测5-r219.jar'),sha256=package['sha256'])
    save(WORK/'release.json',release);print(json.dumps(package))


if __name__=='__main__':main()
