# -*- coding: utf-8 -*-
"""第十一批批准建筑文件接入；只新增独立目录，不替换运行中的模组或存档。"""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import json
import shutil
import zipfile
from max_structure_review import ROOT,INDEX,read,save,digest,publisher
from project_paths import project_path

WORK=ROOT/'logs/batch11-buildings-20261107'
GAME=Path('C:/Users/OWNER/AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版/minecraft')
IDS=['MX-C01','MX-C02','MX-C03','MX-C04','W02']


def main():
    WORK.mkdir(exist_ok=True);original=INDEX.read_bytes();index=json.loads(original.decode('utf8'))
    assert read(GAME.parent/'mrpack/modrinth.index.json')['versionId']=='3.0'
    assert index['pending_batch']['approved_machine_ids']==IDS and index['pending_batch']['count']==5
    assert not (WORK/'installation.json').exists()
    save(WORK/'previous-index.json',index)
    jar=GAME/'mods/HK3GTL-内测5.jar';jar_sha=digest(jar);rows=[]
    for identity in IDS:
        e=next(r for r in index['entries'] if r['id']==identity);archive=project_path(e['archive'])
        assert digest(project_path(e['archive_zip']))==e['archive_zip_sha256']
        nbt=project_path(e['approved_nbt']);assert digest(nbt)==e['approved_nbt_sha256']
        schems=list(archive.rglob('*.schem'));assert len(schems)==1
        with zipfile.ZipFile(project_path(e['archive_zip'])) as z:
            assert z.testzip() is None
            for p in (nbt,schems[0]):assert z.read(p.relative_to(project_path(e['approval_manifest']).parent).as_posix())==p.read_bytes()
        rows.append(dict(id=identity,nbt=str(nbt),schem=str(schems[0]),nbt_sha256=digest(nbt),schem_sha256=digest(schems[0]),size_xyz=e['size_xyz']))
    folder='HK3GTL_batch11_MAX4_W02V2_20261107'
    targets=[GAME/'schematics'/folder,GAME/'config/worldedit/schematics'/folder]
    assert not any(p.exists() or p.with_name(p.name+'.pending').exists() for p in targets)
    now=datetime.now(timezone(timedelta(hours=-5))).isoformat(timespec='seconds')
    receipt=dict(passed=True,batch='batch-11',installed_at=now,instance=str(GAME),instance_version='3.0',
        structures=rows,targets=list(map(str,targets)),installed_building_files=True,formal_pattern_installed=False,
        game_verified=False,jar_unchanged=True,saves_modified=False,
        boundary='五份确认建筑的NBT与Sponge文件已接入；正式控制器、Pattern和运行逻辑仍待接通，正式资源仍52。')
    for target in targets:
        stage=target.with_name(target.name+'.pending');stage.mkdir(parents=True)
        for row in rows:
            for kind in ('nbt','schem'):
                dest=stage/(row['id'].lower()+'-approved.'+kind);shutil.copy2(row[kind],dest)
                assert digest(dest)==row[kind+'_sha256']
        save(stage/'manifest.json',receipt);stage.rename(target)
    assert digest(jar)==jar_sha
    for e in index['entries']:
        if e['id'] in IDS:e.update(game_files_installed=True,status='appearance_installed_formal_pending',building_files_batch='batch-11')
    index.setdefault('building_file_deployments',[]).append(receipt)
    index['approved_undeployed_machine_ids']=[];index['approved_undeployed_count']=0
    index['pending_batch']=dict(id='batch-12',approved_machine_ids=[],count=0,required=5,deployment_eligible=False,
        status='waiting_new_approvals',game_files_installed=False,game_verified=False,note='第十一批建筑文件已接入；正式Pattern另计。新批次0/5。')
    index['scope']='批准57／正式52；batch-11五份建筑文件已接入增强版3.0，正式Pattern和游戏运行另验；batch-12为0/5。'
    index['batch_rule']='每累计5台明确批准即按不可变原件接入；建筑文件、正式Pattern、游戏验收分别记账。'
    index['updated_at']=now
    index['_change_records'].append(dict(record=len(index['_change_records'])+1,time=now,reason='W02 V2外观明确认可使batch-11满五台。',
        previous_index=str(WORK/'previous-index.json'),added='五台批准建筑文件接入收据',modified='开启batch-12；正式资源52和74项范围不变。'))
    publisher().publish_transaction({INDEX:json.dumps(index,ensure_ascii=False,indent=2)+'\n'},{INDEX:original})
    save(WORK/'installation.json',receipt);print(json.dumps(dict(passed=True,building_files=20,approved=57,formal=52,next_batch='batch-12'),ensure_ascii=False))


if __name__=='__main__':main()
