# -*- coding: utf-8 -*-
"""修订88核验：比较修改前备份、复用贴图及实际打包结果；不启动游戏、不部署。

【变更记录 #1】2026-09-27 03:09:30（内测5修订88）
删除：无。新增：接口机械方块的资源及开发源码核验。
修改：检查历史翻译和修订87未涉及文件不变，记录包哈希。
用途：区分静态、构建、部署及游戏验收证据；断言失败直接终止。
"""
from pathlib import Path
from datetime import datetime
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / 'logs/revision88'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


manifest_path = LOG / 'application.json'
manifest = read(manifest_path)
paths = [entry if isinstance(entry, str) else entry['path'] for entry in manifest['files']]
records = []
for path in paths:
    backup = LOG / 'backup' / path
    records.append({'path': path, 'before': digest(backup) if backup.exists() else None,
                    'after': digest(ROOT / path)})
manifest['files'] = records
manifest['completed_at'] = datetime.now().isoformat()
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

unchanged = []
for entry in read(ROOT / 'logs/revision87/application.json')['files']:
    if entry['path'] not in paths:
        assert digest(ROOT / entry['path']) == entry['after'], entry['path']
        unchanged.append(entry['path'])
for lang in ['zh_cn', 'en_us']:
    path = f'src/main/resources/assets/hk3gtl/lang/{lang}.json'
    current, old = read(ROOT / path), read(LOG / 'backup' / path)
    assert all(current[key] == value for key, value in old.items())
    assert set(current) - set(old) == {'block.hk3gtl.industrial_port_casing'}

resource_root = ROOT / 'src/main/resources'
texture = resource_root / 'assets/hk3gtl/textures/block/casings/industrial_controller_shell.png'
model = read(resource_root / 'assets/hk3gtl/models/block/industrial_port_casing.json')
assert model['parent'] == 'minecraft:block/cube_all'
assert model['textures']['all'] == 'hk3gtl:block/casings/industrial_controller_shell'
jar = ROOT / 'build/libs/hk3gtl-0.5.0.jar'
matched_resources, matched_sources = [], []
with zipfile.ZipFile(jar) as release, zipfile.ZipFile(ROOT / 'build/devlibs/hk3gtl-0.5.0-sources.jar') as sources:
    for path in paths:
        if path.startswith('src/main/resources/'):
            key = path[len('src/main/resources/'):]
            assert release.read(key) == (ROOT / path).read_bytes(), path
            matched_resources.append(key)
        elif path.startswith('src/main/java/'):
            key = path[len('src/main/java/'):]
            assert sources.read(key) == (ROOT / path).read_bytes(), path
            matched_sources.append(key)
    assert json.loads(release.read('assets/hk3gtl/changelog.json'))['entries'][0]['revision'] == 88
    assert release.read('assets/hk3gtl/textures/block/casings/industrial_controller_shell.png') == texture.read_bytes()
    for key in ['registration/Hk3IndustrialContent', 'multiblock/pattern/Hk3ApprovedArchitecturePatterns',
                'multiblock/pattern/Hk3LiquidLinePatterns', 'recipe/machine/Hk3LiquidLineControllerRecipes']:
        assert b'industrial_port_casing' in release.read('com/sirin/hk3gtl/common/' + key + '.class')
assert digest(jar) == digest(ROOT / 'build/libs/HK3GTL-内测5.jar')
build = (LOG / 'clean-build.log').read_text(encoding='utf-8', errors='replace')
assert 'BUILD SUCCESSFUL' in build
report = {
    'revision': 88, 'time': datetime.now().isoformat(), 'jar': str(jar),
    'bytes': jar.stat().st_size, 'sha256': digest(jar),
    'resources_exact_match': matched_resources, 'development_sources_exact_match': matched_sources,
    'release_registration_and_recipe_constants': True, 'existing_translations_preserved': True,
    'unchanged_revision87_files': unchanged, 'texture_sha256': digest(texture),
    'chinese_jar_identical': True,
    'predicate_source_review': '已核对GTCEu1.4.4源码：or保留受限谓词，testGlobal记录未匹配能力为0，BlockPattern最终检查minCount。属于源码核验，未运行游戏成型。',
    'build': 'BUILD SUCCESSFUL in 1m 14s; 23 actionable tasks: 23 executed',
    'custom_test_tasks': [line.strip() for line in build.splitlines() if line.startswith('> Task :run')],
    'deployed': False, 'game_started': False, 'game_tested': False
}
(LOG / 'package-verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'revision': 88, 'bytes': report['bytes'], 'sha256': report['sha256'],
                  'resources': len(matched_resources), 'sources': len(matched_sources),
                  'unchanged_revision87_files': len(unchanged), 'deployed': False}, ensure_ascii=True))

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
