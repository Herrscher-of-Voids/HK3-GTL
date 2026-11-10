# -*- coding: utf-8 -*-
"""应用负责人已批准的32套独立控制器候选，保留其余四套原像素。

变更记录 #1 · 修订178 · 2026-10-26：仅改控制器渲染引用与96张PNG，
运行前校验候选、批准蓝图和图案唯一性；不改几何、注册ID或语言，不构建/部署。
"""
from pathlib import Path
from project_paths import project_path
from datetime import datetime, timezone, timedelta
import argparse
import hashlib
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'logs/controller-texture-candidates-20261026'
ASSETS = ROOT / 'src/main/resources/assets/hk3gtl'
JAVA = ROOT / 'src/main/java/com/sirin/hk3gtl/common/machine'
PRESERVED = {'i01': 'i01_v2', 'i02': 'i02_v2', 'i03': 'i03_v2', 's01': 's01_v2'}
APPROVAL = '采用32套候选，保留4套原材质'
SUFFIXES = {'idle': '', 'active': '_active', 'paused': '_paused'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def changed_once(text, old, new, label):
    if new in text and old not in text:
        return text
    assert text.count(old) == 1, f'源码锚点不唯一或不存在：{label}'
    return text.replace(old, new, 1)


def java_changes(stamp):
    result = {}
    path = JAVA / 'Hk3MachinesImpl.java'
    text = path.read_text(encoding='utf-8')
    # 四套保留定义不进入替换；仅在升级工厂及各自批准布局处改变覆盖层路径。
    stage = text.index('private static MultiblockMachineDefinition collectionUpgrade(')
    a, b = text[:stage], text[stage:]
    b = changed_once(b, 'new ResourceLocation("hk3gtl", "block/overlay/i01_v2"))',
                     'new ResourceLocation("hk3gtl", "block/overlay/" + layout + "_unique_r178"))', 'I01升级3台')
    b = changed_once(b, '.workableCasingRenderer(casingTex("industrial_controller_shell"), OVERLAY)',
                     '.workableCasingRenderer(casingTex("industrial_controller_shell"),\n'
                     '                        new ResourceLocation("hk3gtl", "block/overlay/" + layout + "_unique_r178"))',
                     'I06-I13')
    for key, field in (('i04', 'LIQUID_HONKAI_STABILIZATION_TOWER = registrate()'),
                       ('i05', 'STABILIZATION_MEDIUM_REGENERATION_TOWER = registrate()')):
        at = a.index(field)
        head, tail = a[:at], a[at:]
        old = '.workableCasingRenderer(casingTex("industrial_controller_shell"), OVERLAY)'
        new = '.workableCasingRenderer(casingTex("industrial_controller_shell"),\n' \
              f'                        new ResourceLocation("hk3gtl", "block/overlay/{key}_unique_r178"))'
        if new not in tail:
            assert old in tail, f'{key}渲染锚点缺失'
            tail = tail.replace(old, new, 1)
        a = head + tail
    text = a + b
    text = re.sub(r'    private static final ResourceLocation OVERLAY = new ResourceLocation\(Hk3Constants\.MOD_ID, "block/overlay/default_set"\);\n', '', text)
    result[path] = text

    path = JAVA / 'Hk3IndustrialExtensionMachines.java'
    text = path.read_text(encoding='utf-8')
    concentration = text.index('public static MultiblockMachineDefinition registerConcentration()')
    registration = text.index('private static MultiblockMachineDefinition register(String name, String layout)')
    head, conc, tail = text[:concentration], text[concentration:registration], text[registration:]
    conc = changed_once(conc, '.workableCasingRenderer(SHELL, OVERLAY)',
                        '.workableCasingRenderer(SHELL, new ResourceLocation("hk3gtl", "block/overlay/i17_unique_r178"))', 'I17')
    tail = changed_once(tail, '.workableCasingRenderer(SHELL, OVERLAY)',
                        '.workableCasingRenderer(SHELL, new ResourceLocation("hk3gtl", "block/overlay/" + layout + "_unique_r178"))', 'I14-I18工厂')
    text = head + conc + tail
    text = text.replace('    private static final ResourceLocation OVERLAY = new ResourceLocation("hk3gtl", "block/overlay/default_set");\n', '')
    result[path] = text

    path = JAVA / 'research/Hk3ResearchMachines.java'
    text = path.read_text(encoding='utf-8')
    text = changed_once(text, 'new ResourceLocation("hk3gtl", "block/overlay/s01_v2"))',
                        'new ResourceLocation("hk3gtl", "block/overlay/" + key + "_unique_r178"))', 'S02-S05工厂')
    result[path] = text

    path = JAVA / 'Hk3LateIndustrialMachines.java'
    text = path.read_text(encoding='utf-8')
    assert '.shapeInfo(def -> Hk3LargeArchitectureShapes.create(def, key))' in text
    assert '.multiblockPreviewRenderer(true, true)' in text
    text = changed_once(text, '.workableCasingRenderer(SHELL, OVERLAY)',
                        '.workableCasingRenderer(SHELL, new ResourceLocation("hk3gtl", "block/overlay/" + key + "_unique_r178"))', 'I19-I28工厂')
    text = text.replace('    private static final ResourceLocation OVERLAY = new ResourceLocation("hk3gtl", "block/overlay/default_set");\n', '')
    result[path] = text

    for path, text in result.items():
        if '【控制器材质变更 · 修订178】' not in text:
            comment = f'/** 【控制器材质变更 · 修订178】{stamp}：按负责人“{APPROVAL}”接入独立三态面板；保留既有四套像素，不改建筑、控制器ID或工艺。 */\n'
            text = re.sub(r'^(package [^;]+;\n)', r'\1\n' + comment, text, count=1)
        result[path] = text
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true', help='按本轮已获明确批准执行正式资源接入')
    args = parser.parse_args()
    manifest_path, verification_path = OUT / 'manifest.json', OUT / 'verification.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    verified = json.loads(verification_path.read_text(encoding='utf-8'))
    assert verified['status'] == 'passed' and sha(manifest_path) == verified['manifest_sha256']
    assert len(manifest['entries']) == manifest['approved_geometry_count'] == 36
    assert manifest['new_candidate_count'] == 32 and manifest['future_unmade_count'] == 52
    preserved_before, source_geometry_before, copies, front_hashes, targets = {}, {}, [], {}, {}
    for entry in manifest['entries']:
        key = entry['key']
        source = project_path(entry['source']['path'])
        assert source.is_file() and sha(source) == entry['source']['sha256'], f'批准几何已变化：{key}'
        source_geometry_before[str(source)] = sha(source)
        overlay = PRESERVED[key] if key in PRESERVED else key + '_unique_r178'
        targets[key] = 'hk3gtl:block/overlay/' + overlay
        for state, suffix in SUFFIXES.items():
            candidate = OUT / entry['candidate'][state]['path']
            assert candidate.is_file() and sha(candidate) == entry['candidate'][state]['sha256']
            destination = ASSETS / f'textures/block/overlay/{overlay}/overlay_front{suffix}.png'
            if key in PRESERVED:
                assert sha(destination) == sha(candidate) == entry['old'][state]['sha256'], f'保留原图已变化：{key}/{state}'
                preserved_before[str(destination)] = sha(destination)
            else:
                if destination.exists():
                    assert sha(destination) == sha(candidate), f'独立目标路径已存在不同文件：{destination}'
                copies.append((candidate, destination))
            if state == 'idle':
                front_hashes[key] = sha(candidate)
    assert len(set(front_hashes.values())) == 36, '36台正面贴图必须独立'
    assert len(copies) == 96 and len(preserved_before) == 12
    stamp = datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')
    changes = java_changes(stamp)
    before_java = {str(p): sha(p) for p in changes}
    if not args.apply:
        print(json.dumps({'status': 'validated_not_applied', 'files_to_copy': len(copies), 'java_files': list(before_java), 'preserved_pngs': 12}))
        return
    backup = OUT / 'application-r178-before'
    backup.mkdir(exist_ok=True)
    for path, content in changes.items():
        relative = path.relative_to(ROOT)
        destination = backup / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if not destination.exists():
            shutil.copyfile(path, destination)
    for source, destination in copies:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        assert sha(source) == sha(destination)
    for path, content in changes.items():
        path.write_text(content, encoding='utf-8')
    assert preserved_before == {p: sha(project_path(p)) for p in preserved_before}
    assert source_geometry_before == {p: sha(project_path(p)) for p in source_geometry_before}
    receipt = {
        'status': 'applied', 'revision': 178, 'applied_at': datetime.now(timezone(timedelta(hours=8))).isoformat(),
        'approval_quote': APPROVAL, 'approval_message_time': '平台未提供，采用实际应用时间记录',
        'manifest_sha256': sha(manifest_path), 'new_sets': 32, 'new_pngs': 96, 'preserved_sets': 4,
        'preserved_pngs': 12, 'preserved_pngs_sha256_unchanged': True, 'approved_geometry_unchanged': True,
        'unique_controller_fronts': 36, 'planned_total': 88, 'future_unmade_count': 52,
        'official_overlay_paths': targets, 'front_sha256': front_hashes, 'preserved_sha256': preserved_before,
        'copied_files': [{'source': str(s), 'target': str(d), 'sha256': sha(d)} for s, d in copies],
        'java_before_sha256': before_java, 'java_after_sha256': {str(p): sha(p) for p in changes},
        'source_geometry_sha256': source_geometry_before,
        'geometry_ids_language_changed': False, 'game_instance_changed': False, 'built_or_deployed': False,
        'mcmeta_required': False, 'mcmeta_reason': '沿用既有workableCasingRenderer静态三态PNG格式，无动画或额外模型元数据。',
        'preview_bindings_preserved': True,
    }
    receipt_path = OUT / 'application-r178.json'
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'status': 'applied', 'receipt': str(receipt_path), 'new_pngs': 96,
                      'unique_controller_fronts': 36, 'preserved_pngs_sha256_unchanged': True}))


if __name__ == '__main__':
    main()
