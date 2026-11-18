import sys
from zipfile import ZipFile
import deliver_0001_r22_full as full

shared=full.shared
ROOT=full.ROOT
WORK=shared.Path('C:/Users/OWNER/.codex/builds/0005-wonder-fx-20261117-full')
SOURCE=WORK/'source'
LOG=ROOT/'logs/0005-wonder-effects-repair-20261117/full-build'
OUT=ROOT/'deliveries/0005多方块设计_毕业建筑特效修复_R1_20261117'
VERSION='0.5.0-wonder-fx-r1'
NAME='0005多方块设计-'+VERSION+'.jar'
COMMAND=['gradlew.bat','--no-daemon','--no-build-cache','--max-workers=2',
    '--project-cache-dir','../project-cache','-Parchives_base_name=0005多方块设计',
    '-Pmod_version='+VERSION,'remapJar','-x','check','-x','test','--console=plain']
shared.DIRECTORIES=[*shared.DIRECTORIES,'deliveries/0005_W09_T9与S2山观兵装矩阵_F2_20261117']
full.WORK,full.SOURCE,full.LOG,full.OUT=WORK,SOURCE,LOG,OUT
full.VERSION,full.NAME,full.COMMAND=VERSION,NAME,COMMAND
save,digest,now=shared.save,shared.digest,shared.now
freeze,build,archive,refresh=full.freeze,full.build,full.archive,full.refresh

def finish():
    manifest=shared.json.loads((LOG/'input-manifest.json').read_text('utf8'))
    command=shared.json.loads((LOG/'build-command.json').read_text('utf8'))
    log=(LOG/'build.log').read_text('utf8')
    tasks=shared.re.findall(r'^> Task :([^\s]+)',log,shared.re.M)
    if int((LOG/'exit-code.txt').read_text('utf8')) or not set(shared.TASKS).issubset(tasks):
        raise RuntimeError('完整生产构建未成功。')
    jar=SOURCE/'build/libs'/NAME
    resources=['assets/hk3gtl/models/scene/w05_r3.json.gz','assets/hk3gtl/models/scene/w06_author.json.gz',
        'assets/hk3gtl/textures/effect/w05_r3_atlas.png','assets/hk3gtl/textures/effect/w06_author_atlas.png',
        'data/hk3gtl/structures/w05_r3_mask.bin.gz','data/hk3gtl/structures/w06_author_mask.bin.gz',
        *['assets/hk3gtl/shaders/core/wonder_fx.'+suffix for suffix in ['json','vsh','fsh']],
        *['assets/hk3gtl/models/scene/'+name+'.json.gz' for name in ['w08_a5','w10_a3','w12_a3']]]
    classes=['client/wonder/'+name for name in ['Hk3WonderFxModel','Hk3WonderFxRenderer','Hk3WonderFxScenes',
        'Hk3WindFrostEffects','Hk3W03FxRenderer','Hk3W08FxRenderer','Hk3W10FxRenderer','Hk3W12FxRenderer']]
    classes+=['common/machine/wonder/'+name for name in ['Hk3AnimatedWonderMachine','Hk3WonderFxPacket']]
    with ZipFile(jar) as zipped:
        names=set(zipped.namelist())
        metadata=zipped.read('META-INF/mods.toml').decode('utf8')
        mod=next(block.split('[[')[0] for block in metadata.split('[[mods]]')[1:]
            if shared.re.search(r'modId\s*=\s*["\x27]hk3gtl["\x27]',block.split('[[')[0]))
        version=shared.re.search(r'version\s*=\s*["\x27]([^"\x27]+)',mod).group(1)
        config=shared.json.loads(zipped.read('hk3gtl.mixins.json'))
        mixins=[config['package'].replace('.','/')+'/'+name.replace('.','/')+'.class'
            for key in ['mixins','client','server'] for name in config.get(key,[])]
        shared.json.loads(zipped.read(config['refmap']))
        checked=[]
        for name in resources:
            raw=zipped.read(name);actual=shared.hashlib.sha256(raw).hexdigest()
            expected=digest(SOURCE/'src/main/resources'/name)
            checked.append(dict(path=name,bytes=len(raw),sha256=actual,snapshot_sha256=expected,matches_snapshot=actual==expected))
        package=dict(mod_id='hk3gtl',version=version,refmap=config['refmap'],refmap_valid=True,
            mixins_complete=all(name in names for name in mixins),
            mixin_plugin_present=config['plugin'].replace('.','/')+'.class' in names,
            animation_classes_complete=all('com/sirin/hk3gtl/'+name+'.class' in names for name in classes),resources=checked)
    if not all([version==VERSION,package['mixins_complete'],package['mixin_plugin_present'],
            package['animation_classes_complete'],all(item['matches_snapshot'] for item in checked)]):
        raise RuntimeError('产物版本、Mixin或动画资源核对失败。')
    OUT.mkdir(parents=True,exist_ok=True)
    artifact=OUT/NAME;shared.shutil.copy2(jar,artifact)
    built_hash,delivery_hash=digest(jar),digest(artifact)
    if built_hash!=delivery_hash:raise RuntimeError('交付副本SHA-256不一致。')
    before={item['path']:dict(bytes=item['bytes'],sha256=item['sha256']) for item in manifest['files']}
    stamps=shared.json.loads((LOG/'input-stamps.json').read_text('utf8'))
    cache={str((ROOT/path).resolve()):(tuple(stamps[path]),entry) for path,entry in before.items()}
    receipt=dict(recorded_at=now(),conversation='0005',conversation_id='01a1e02a-4d20-7d81-bdab-70404f66086d',
        version=VERSION,frozen_at=manifest['frozen_at'],source_snapshot=str(SOURCE),
        input_manifest=str(LOG/'input-manifest.json'),input_manifest_sha256=digest(LOG/'input-manifest.json'),
        input_files=len(before),input_bytes=sum(item['bytes'] for item in before.values()),
        snapshot_consistent=manifest['snapshot_consistent'],full_production_source_set=True,
        command=COMMAND,java_home=shared.JAVA_HOME,project_cache=str(WORK/'project-cache'),
        initial_build_output_empty=command['initial_build_output_empty'],initial_project_cache_empty=command['initial_project_cache_empty'],
        build_successful=True,task_result=next(line for line in log.splitlines() if line.startswith('BUILD SUCCESSFUL')),
        production_tasks=tasks,build_log=str(LOG/'build.log'),direct_official_remap_copy=True,
        jar_repacked=False,post_build_jar_mutation=False,built_jar=str(jar),delivery_jar=str(artifact),
        bytes=jar.stat().st_size,sha256=built_hash,delivery_sha256=delivery_hash,both_hashes_equal=True,
        package_verification=package,post_snapshot_changes_not_included=shared.differences(before,full.inventory(ROOT,cache)),
        automated_tests_run=False,installed=False,game_started=False,game_verified=False)
    save(LOG/'build-receipt.json',receipt);save(OUT/'完整构建回执.json',receipt)
    print(shared.json.dumps(dict(delivery=str(artifact),sha256=built_hash,bytes=receipt['bytes']),ensure_ascii=False),flush=True)

def cleanup():
    record=shared.json.loads((LOG/'snapshot-archive.json').read_text('utf8'))
    receipt=shared.json.loads((LOG/'build-receipt.json').read_text('utf8'))
    if WORK.resolve()!=shared.Path('C:/Users/OWNER/.codex/builds/0005-wonder-fx-20261117-full').resolve():
        raise RuntimeError('本轮临时目录不匹配。')
    if digest(shared.Path(record['archive']))!=record['sha256'] or digest(shared.Path(receipt['delivery_jar']))!=receipt['sha256']:
        raise RuntimeError('清理前压缩归档或交付产物哈希不匹配。')
    shared.shutil.rmtree(WORK);record['temporary_work_removed']=True;save(LOG/'snapshot-archive.json',record)
    print('本轮临时展开快照已清理。',flush=True)

if __name__=='__main__':
    {'freeze':freeze,'build':build,'finish':finish,'archive':archive,'refresh':refresh,'cleanup':cleanup}[sys.argv[1]]()
