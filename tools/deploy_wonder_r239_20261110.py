"""仅向增强版3.5部署本轮控制器并保存回滚，不修改其他实例或生产规则。"""
import hashlib,json,os,shutil,zipfile,sys
from datetime import datetime,timezone
from pathlib import Path
import deploy_industrial_build as base
from deploy_late_industrial_20261026 import source_inputs

ROOT=Path(__file__).resolve().parents[1]
LOG=ROOT/'logs/w01-w03-implementation-20261110'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,data):(LOG/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf8')
def deploy():
    revision=int(sys.argv[1]) if len(sys.argv)>1 else 239
    build=LOG/f'build-r{revision}-final'
    guard=base.target_process_guard()
    receipt=json.loads((build/'clean-build.json').read_text('utf8'))
    assert receipt['status']=='passed' and receipt['revision']==revision
    assert source_inputs()==json.loads((build/'build-source-inputs.json').read_text('utf8'))
    source=base.SOURCE;target=base.TARGET
    assert sha(source)==receipt['jar_sha256']
    with zipfile.ZipFile(source) as jar:
        assert json.loads(jar.read('assets/hk3gtl/changelog.json'))['entries'][0]['revision']==revision
        for name in ['common/machine/Hk3CommissionMachine','common/machine/w02/Hk3W02Machine','common/machine/w03/Hk3W03Machine','common/command/Hk3WonderCommissionCommands']:
            jar.getinfo('com/sirin/hk3gtl/'+name+'.class')
        for name in ['w01_hall.bin.gz','w02_19c_a2.bin.gz','w03_c9.bin.gz']:
            path=ROOT/'src/main/resources/data/hk3gtl/structures'/name
            assert jar.read('data/hk3gtl/structures/'+name)==path.read_bytes()
    before={p.name:sha(p) for p in target.parent.glob('*.jar')}
    backup=LOG/f'before-r{revision}.jar';assert not backup.exists()
    shutil.copy2(target,backup)
    guard_replace=base.target_process_guard()
    staging=target.with_suffix(f'.r{revision}.tmp');shutil.copy2(source,staging);os.replace(staging,target)
    after={p.name:sha(p) for p in target.parent.glob('*.jar')}
    assert before.keys()==after.keys() and all(v==after[k] for k,v in before.items() if k!=target.name)
    assert sha(target)==receipt['jar_sha256']
    save(f'deployment-r{revision}.json',dict(revision=revision,pack='增强版3.5（负责人确认）',installed_at=datetime.now(timezone.utc).isoformat(),
        target=str(target),sha256=sha(target),bytes=target.stat().st_size,backup=str(backup),previous_sha256=sha(backup),
        third_party_jars_unchanged=True,process_guards=[guard,guard_replace],game_verified=False))
    print(f'r{revision}部署及目标回读通过；尚未游戏验收')

if __name__=='__main__':deploy()
