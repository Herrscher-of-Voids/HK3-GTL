"""Preserve reviewed previews as immutable, hash-verified delivery snapshots."""
import datetime
import hashlib
import json
import shutil
import zipfile
import nbtlib

from redesign69_geometry import ROOT
from structure_size_baseline import require, SOURCE as SIZE_SOURCE


ENTRIES = [
    ('I01-1', 'I01-1_潮汐采集场_自由设计预览', 'build_i01_tidal_preview.py', 'shape_approved_port_revision', '原造型通过；本快照将候选接口统一改为工业接口机壳，尚未对新版端口重新外观确认。'),
    ('I01-2', 'I01-2_2阶崩坏能采集塔_无拆除扩建预览', 'build_i01_stage2_preview.py', 'shape_approved_port_revision', '原造型通过；本快照将候选接口统一改为工业接口机壳，尚未对新版端口重新外观确认。'),
    ('I01-3', 'I01-3_3阶崩坏能采集塔_无拆除扩建预览', 'build_i01_stage3_preview.py', 'shape_approved_port_revision', '原造型通过；本快照将候选接口统一改为工业接口机壳，尚未对新版端口重新外观确认。'),
    ('I01-4', 'I01-4_4阶崩坏能采集塔_无拆除扩建预览', 'build_i01_stage4_preview.py', 'shape_approved_port_revision', '原造型通过；本快照将候选接口统一改为工业接口机壳，尚未对新版端口重新外观确认。'),
    ('I02', 'I02_样本光谱分析阵列_自由设计预览', 'build_i02_spectrum_preview.py', 'shape_approved_material_port_revision', '原造型通过；高级建材和工业接口机壳属于后续改版，尚未对新版材料与端口重新外观确认。'),
    ('I03', 'I03_崩坏能离心分离中心_自由设计预览', 'build_i03_centrifuge_preview.py', 'shape_approved_port_revision', '高级建材造型通过；本快照更换了接口机壳，尚未对新版端口重新外观确认。'),
    ('I04', 'I04_液态崩坏能稳定塔_自由设计预览', 'build_i04_stabilization_preview.py', 'shape_approved_port_revision', '原造型通过；本快照更换了接口机壳，尚未对新版端口重新外观确认。'),
    ('I05', 'I05_稳定介质再生塔_自由设计预览', 'build_i05_regeneration_preview.py', 'approved', '用户查看新版双塔、28种选材与工业接口预览后明确表示这一台可以并继续下一台。'),
    ('I06', 'I06_崩坏能燃料调配厂_自由设计预览', 'build_i06_fuel_blending_preview.py', 'pending', '新交付外观预览，等待用户逐台确认。'),
    ('I07', 'I07_探测器精密校准台_自由设计预览', 'build_i07_calibration_preview.py', 'pending', '新交付外观预览，等待用户逐台确认。'),
    ('I08', 'I08_仿制核心结晶反应室_自由设计预览', 'build_i08_crystallization_preview.py', 'pending', '新交付外观预览，等待用户逐台确认。'),
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    stamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d_%H%M%S_%f')
    root = ROOT / 'deliveries/多方块确认归档'
    snapshot = root / stamp
    snapshot.mkdir(parents=True, exist_ok=False)
    rows = []
    for key, folder, generator, status, evidence in ENTRIES:
        source = ROOT / 'deliveries' / folder
        assert list(source.glob('*.nbt')) and list(source.glob('*.schem')), source
        size_checks = []
        for path in sorted(source.glob('*.nbt')):
            structure = nbtlib.load(path)
            size_checks.append(require({'key': key,
                'size': [int(v) for v in structure['size']],
                'blocks': [{'pos': [int(v) for v in b['pos']]} for b in structure['blocks']]}))
        target = snapshot / key
        shutil.copytree(source, target)
        recipe = ROOT / 'tools/structure_delivery' / generator
        shutil.copy2(recipe, target / generator)
        files = {}
        for original in source.rglob('*'):
            if original.is_file():
                copied = target / original.relative_to(source)
                assert digest(original) == digest(copied), copied
        for path in sorted(target.rglob('*')):
            if path.is_file():
                files[path.relative_to(snapshot).as_posix()] = digest(path)
        rows.append({'id': key, 'status': status, 'confirmation': evidence,
                     'size_baseline': size_checks,
                     'source': str(source), 'archive': str(target), 'sha256': files})
    helpers = snapshot / 'generator_dependencies'
    helpers.mkdir()
    for name in ('build_redesign69.py', 'material_resources.py', 'redesign69_geometry.py',
                 'package_l1_review89.py', 'structure_size_baseline.py', 'check_i01_upgrade.py',
                 'check_preview_ports.py',
                 '当前多方块设计规则.md'):
        shutil.copy2(ROOT / 'tools/structure_delivery' / name, helpers / name)
    shutil.copy2(SIZE_SOURCE, helpers / SIZE_SOURCE.name)
    manifest = {'snapshot': stamp, 'entries': rows,
                'generator_dependencies': {p.name: digest(p) for p in helpers.iterdir()},
                'integration_rule': '从对应确认归档读取NBT与逐格数据；接入前比对SHA256。待确认及材料修订状态须明确处理，不能当作正式成型验收。',
                'minimum_rule': '保留69座占地总表的尺寸下限；宽、深、高及实际方块边界逐轴检查。自由设计不受旧造型与尺寸上限约束。',
                'limits': '归档保存建筑外观与结构数据；游戏Pattern、配方和生存可达性尚未由此证明。'}
    (snapshot / '确认与校验清单.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    bundle = root / (stamp + '.zip')
    with zipfile.ZipFile(bundle, 'x', zipfile.ZIP_DEFLATED) as archive:
        for path in snapshot.rglob('*'):
            if path.is_file():
                archive.write(path, path.relative_to(snapshot).as_posix())
    with zipfile.ZipFile(bundle) as archive:
        assert archive.testzip() is None
        for row in rows:
            for name, expected in row['sha256'].items():
                assert hashlib.sha256(archive.read(name)).hexdigest() == expected, name
    (root / '当前归档索引.json').write_text(json.dumps({'snapshot': str(snapshot), 'zip': str(bundle),
        'zip_sha256': digest(bundle), 'entries': [{'id': r['id'], 'status': r['status'], 'archive': r['archive']} for r in rows]}, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'snapshot': str(snapshot), 'zip': str(bundle), 'structures': len(rows), 'verified': True}, ensure_ascii=False))


if __name__ == '__main__':
    main()
