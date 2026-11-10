"""用1.20.1原版Bootstrap实际注册表核验礼堂状态；不启动游戏界面或世界。"""
import hashlib
import json
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'output/hall-azu-analysis'
PRISM = Path('C:/Users/OWNER/AppData/Roaming/PrismLauncher')
INSTANCE = PRISM / 'instances/GregTech Leisure-增强版/minecraft'
CLIENT = PRISM / 'libraries/com/mojang/minecraft/1.20.1/minecraft-1.20.1-client.jar'
CACHE = Path.home() / '.gradle/caches/forge_gradle/minecraft_repo/versions/1.20.1'
JAVA = PRISM / 'java/java-runtime-gamma/bin/java.exe'
SOURCE = ROOT / 'tools/structure_delivery/HallAzuRegistryAudit.java'


def sha(path, kind='sha256'):
    digest = hashlib.new(kind)
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    work = DATA / 'compatibility-runtime'
    work.mkdir(exist_ok=True)
    metadata = json.loads((CACHE / 'version.json').read_text(encoding='utf-8'))
    assert metadata['id'] == '1.20.1' and sha(CLIENT, 'sha1') == metadata['downloads']['client']['sha1']
    with zipfile.ZipFile(CLIENT) as archive:
        target_version = json.loads(archive.read('version.json'))
    libraries = [PRISM / 'libraries' / row['downloads']['artifact']['path']
                 for row in metadata['libraries'] if row.get('downloads', {}).get('artifact')]
    libraries = [path for path in libraries if path.is_file()]
    classpath = ';'.join(str(path) for path in [CLIENT, *libraries])
    args = ['-Xmx768M', '-Djava.awt.headless=true', '-Dfile.encoding=UTF-8', '--class-path', classpath,
            str(SOURCE), str(DATA / 'palette.json'), str(work / 'runtime-raw.json')]
    argfile = work / 'java-args.txt'
    argfile.write_text('\n'.join('"' + arg.replace('\\', '/').replace('"', '\\"') + '"' for arg in args), encoding='utf-8')
    process = subprocess.run([str(JAVA), '@' + str(argfile)], cwd=work, capture_output=True, text=True,
                             encoding='utf-8', errors='replace', timeout=90)
    (work / 'stdout.log').write_text(process.stdout, encoding='utf-8')
    (work / 'stderr.log').write_text(process.stderr, encoding='utf-8')
    if process.returncode:
        raise RuntimeError(process.stderr[-6000:] + process.stdout[-1500:])
    report = json.loads((work / 'runtime-raw.json').read_text(encoding='utf-8'))
    audit = json.loads((ROOT / 'deliveries/永恒的礼堂_Azu_预览与方块审计_20261029/audit-data.json').read_text(encoding='utf-8'))
    counts = {r['state']: r['counts'] for r in audit['states']}
    for row in report['states']:
        row['counts'] = counts[row['state']]
    missing_ids = sorted({r['block'] for r in report['states'] if not r['block_exists']})
    invalid_states = [r['state'] for r in report['states'] if not r['state_instance_verified']]
    scopes = {}
    for scope in ['saved', 'hall', 'body', 'tower', 'towers', 'other']:
        rows = [r for r in report['states'] if r['counts'][scope]]
        scopes[scope] = dict(block_ids=len({r['block'] for r in rows}), states=len(rows),
                             blocks=sum(r['counts'][scope] for r in rows),
                             missing_ids=sorted({r['block'] for r in rows if not r['block_exists']}),
                             invalid_states=[r['state'] for r in rows if not r['state_instance_verified']])
    report.update(method='真实Minecraft 1.20.1原版Bootstrap / BuiltInRegistries.BLOCK / StateDefinition；官方映射反射',
                  target_instance=str(INSTANCE), target_minecraft_version='1.20.1', target_data_version=target_version['world_version'],
                  source_minecraft_version='1.20.4', source_data_version=3700,
                  missing_block_ids=missing_ids, invalid_states=invalid_states, scopes=scopes,
                  source_paths=dict(client=str(CLIENT), client_sha256=sha(CLIENT),
                                    client_official_sha1_verified=True, official_mappings=str(CACHE / 'client_mappings.txt'),
                                    mappings_sha256=sha(CACHE / 'client_mappings.txt'), java_program=str(SOURCE),
                                    vanilla_library_jars=len(libraries), program_sha256=sha(SOURCE)),
                  boundaries=['未启动Minecraft客户端界面、服务器或世界；仅执行原版注册表初始化。',
                              '没有加载增强版模组与Mixin，结果是目标1.20.1的原版ID和状态定义兼容核验，不是完整增强版或FCL运行验收。',
                              '建筑材料和状态存在，不等于1.20.4整个存档可安全直接降级到1.20.1；世界数据版3700高于目标3465，导入迁移另验。',
                              '未更改上传压缩包、当前实例、世界存档、建筑、Pattern或正式资源。'])
    assert scopes['saved']['block_ids'] == 87 and scopes['saved']['states'] == 345
    assert scopes['hall']['block_ids'] == 66 and scopes['hall']['states'] == 323
    (DATA / 'compatibility-1.20.1.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: report[k] for k in ['method', 'missing_block_ids', 'invalid_states', 'scopes']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
