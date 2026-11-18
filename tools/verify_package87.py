# -*- coding: utf-8 -*-
"""修订87包核验：开发包比较编译结果，发布包核对资源及关键常量；区分Loom重映射差异。"""
from pathlib import Path
from datetime import datetime
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / 'logs/revision87'
sha = lambda data: hashlib.sha256(data).hexdigest()
manifest = json.loads((LOG / 'application.json').read_text(encoding='utf-8'))
assert all(sha((ROOT / entry['path']).read_bytes()) == entry['after'] for entry in manifest['files'])
jar = ROOT / 'build/libs/hk3gtl-0.5.0.jar'
resources, sources, classes = [], [], []
with zipfile.ZipFile(jar) as release,\
        zipfile.ZipFile(ROOT / 'build/devlibs/hk3gtl-0.5.0-dev.jar') as dev,\
        zipfile.ZipFile(ROOT / 'build/devlibs/hk3gtl-0.5.0-sources.jar') as source:
    assert json.loads(release.read('assets/hk3gtl/changelog.json'))['entries'][0]['revision'] == 87
    for entry in manifest['files']:
        path = entry['path']
        if path.startswith('src/main/resources/'):
            name = path[len('src/main/resources/'):]
            assert release.read(name) == (ROOT / path).read_bytes(), name
            resources.append(name)
        elif path.startswith('src/main/java/'):
            name = path[len('src/main/java/'):]
            assert source.read(name).decode('utf-8').replace('\r\n', '\n') == (ROOT / path).read_text(encoding='utf-8'), name
            compiled = name[:-5] + '.class'
            assert dev.read(compiled) == (ROOT / 'build/classes/java/main' / compiled).read_bytes(), compiled
            assert compiled in release.namelist()
            sources.append(name)
            classes.append(compiled)
    checks = {
        'recipe/honkai/HonkaiRecipes': ['honkai_reference_sample', 'notConsumable'],
        'recipe/honkai/Hk3LiquidLoopRecipes': ['industrial_liquid_fractionation_reflux', 'industrial_fresh_analysis_reagent', 'clarified_honkai_mother_liquor'],
        'registration/Hk3IndustrialFluids': ['clarified_honkai_mother_liquor'],
        'multiblock/pattern/Hk3ApprovedArchitecture': ['i04', 'i05'],
    }
    for name, constants in checks.items():
        bytecode = release.read('com/sirin/hk3gtl/common/' + name + '.class')
        assert all(value.encode('utf-8') in bytecode for value in constants), name
assert jar.read_bytes() == (ROOT / 'build/libs/HK3GTL-内测5.jar').read_bytes()
log = (LOG / 'clean-build-structures.log').read_text(encoding='utf-8', errors='replace')
assert 'BUILD SUCCESSFUL in 46s' in log and '23 actionable tasks: 23 executed' in log
report = {
    'time': datetime.now().isoformat(), 'revision': 87,
    'jar': str(jar), 'bytes': jar.stat().st_size, 'sha256': sha(jar.read_bytes()),
    'resources_exact_match': resources, 'development_sources_match': sources,
    'development_classes_exact_match': classes, 'release_key_constants_present': checks,
    'application_hashes_match': True, 'chinese_jar_identical': True,
    'source_comparison_note': '发布源码包经过Loom名称重映射及导入补充，不断言其字节等于工作区；开发源码与编译类分别核对。',
    'build': 'BUILD SUCCESSFUL in 46s; 23 actionable tasks: 23 executed',
    'custom_test_tasks': [line for line in log.splitlines() if line.startswith('> Task :run')],
    'deployed': False, 'game_tested': False,
}
target = LOG / 'package-verification.json'
target.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
assert json.loads(target.read_text(encoding='utf-8')) == report
print(json.dumps({'resources': len(resources), 'sources_and_classes': len(sources),
    'custom_tests': len(report['custom_test_tasks']), 'sha256': report['sha256'],
    'report': str(target)}, ensure_ascii=False))

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
