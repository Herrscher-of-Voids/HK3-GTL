# -*- coding: utf-8 -*-
"""I45候选最终封包：保留原始导出，核对文件、浏览器回执与ZIP。"""
import hashlib
import json
from pathlib import Path
import shutil
import zipfile
from build_i45_steam_train_v2_20261029 import OUT, LOG, ROOT, save


def digest(path):
    return hashlib.file_digest(path.open('rb'), 'sha256').hexdigest() if hasattr(hashlib, 'file_digest') else hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    browser = json.loads((LOG/'browser-verification.json').read_text(encoding='utf-8'))
    manifest = json.loads((OUT/'manifest.json').read_text(encoding='utf-8'))
    check = json.loads((OUT/'verification.json').read_text(encoding='utf-8'))
    assert browser['passed'] and browser['blocks'] == check['blocks'] == manifest['blocks']
    assert browser['readback'] and check['readback']['geometry_nbt_schematic_per_block_equal']
    assert browser['port_buttons_tested'] == 8 and browser['render_on_demand_tested']
    previous = OUT.parent/'I45_仿制的千界一乘列车_靛蓝蒸汽机车与双节旅客车_V1_20261029'
    old_files = json.loads((previous/'交付文件清单.json').read_text(encoding='utf-8'))['files']
    assert all(digest(previous/name) == item['sha256'] for name, item in old_files.items())
    old_archive = previous.with_suffix('.zip')
    assert digest(old_archive) == 'ae6a97e37c5f929c05d31a02681b543d726ee74ee610ea00405e04fc55f5289c'
    save(LOG/'v1-preservation-verification.json', dict(passed=True, previous=str(previous),
        files_sha256_checked=len(old_files), zip_sha256=digest(old_archive), original_v1_modified=False))
    scripts = OUT/'生成脚本'
    for name in ('build_i45_steam_train_viewer_v2_20261029.mjs', 'capture_i45_steam_train_v2_20261029.mjs',
                 'i45_steam_train_finalize_v2_20261029.py'):
        shutil.copy2(ROOT/'tools/structure_delivery'/name, scripts/name)
    shutil.copy2(LOG/'browser-verification.json', OUT/'浏览器核验.json')
    shutil.copy2(LOG/'评审页面.png', OUT/'评审页面.png')
    check['browser_verification'] = dict(passed=True, evidence='浏览器核验.json', offline=True,
        verified_at=browser['verified_at'], console_errors=0, external_requests=0, broken_local_links=0)
    save(OUT/'verification.json', check)
    evidence = dict(machine='I45', name='仿制的千界一乘·列车', target_voltage='QCV / V06 / tier20',
        current_design='doc/HK3GTL-内测5/02_工业计划/工业网络扩展雏形_v6.json',
        current_design_sha256=digest(ROOT/'doc/HK3GTL-内测5/02_工业计划/工业网络扩展雏形_v6.json'),
        voltage_mapping='doc/HK3GTL-内测5/02_工业计划/多方块结构电压映射提案_v1.html',
        voltage_mapping_sha256=check['voltage_progression']['voltage_mapping_sha256'],
        minimum_wdh=[25, 97, 29], approved=False, installed=False,
        instruction='本轮负责人提供黑金原作视觉参考，并仅对I45批准对应电压机壳最多单材的外观例外；保留蒸汽火车形体。',
        appearance_exception=check['appearance_exception'], black_material=check['black_material_verification'],
        boundary='I44有效坐标→I45授权/能量检查→允许目的地抵达确认与失败恢复；保留生命跨平行宇宙限制和终审维度禁行。',
        railway=check['railway'], lower_voltages='24个已批准较低电压形态；逐份元数据及蓝图哈希重新核验。')
    save(OUT/'设计依据.json', evidence)
    files = sorted(p for p in OUT.rglob('*') if p.is_file() and p.name != '交付文件清单.json')
    assert not any('__pycache__' in p.parts for p in files)
    for file in browser['screenshots']:
        assert (OUT/file).is_file()
    listing = {str(p.relative_to(OUT)).replace('\\', '/'):dict(bytes=p.stat().st_size, sha256=digest(p)) for p in files}
    save(OUT/'交付文件清单.json', dict(approved=False, installed=False, files=listing))
    archive = OUT.with_suffix('.zip')
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as package:
        for path in sorted(p for p in OUT.rglob('*') if p.is_file()):
            package.write(path, str(path.relative_to(OUT)).replace('\\', '/'))
    with zipfile.ZipFile(archive) as package:
        assert package.testzip() is None
        assert len(package.infolist()) == len(listing)+1
        for name, entry in listing.items():
            assert hashlib.sha256(package.read(name)).hexdigest() == entry['sha256']
    archive_hash = digest(archive)
    Path(str(archive)+'.sha256').write_text(archive_hash+'  '+archive.name+'\n', encoding='utf-8')
    save(LOG/'package-verification.json', dict(passed=True, archive=str(archive), sha256=archive_hash,
        files=len(listing)+1, crc_passed=True, per_file_sha256_passed=True, approved=False, installed=False))
    print(json.dumps(dict(archive=str(archive), sha256=archive_hash, files=len(listing)+1), ensure_ascii=False))


if __name__ == '__main__':
    main()
