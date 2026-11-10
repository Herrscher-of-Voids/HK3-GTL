# -*- coding: utf-8 -*-
"""修订181：核验第9批五台及原41形态，沿用既有停机、备份和原子替换门禁。"""
from datetime import datetime, timedelta, timezone
import argparse
import hashlib
import json
from pathlib import Path
from structure_delivery.project_paths import project_path
import zipfile

import deploy_late_industrial_20261026 as release

ROOT = release.ROOT
LOG = ROOT / 'logs/batch09-install-20261027'
REVIEW = ROOT / 'logs/batch09-review-20261027'
NEW = ['i34', 'i35', 'i36', 'i38', 'i39']
OLD = list(release.KEYS) + [f'i{n}' for n in range(29, 34)]
VERSIONS = {'i34': 'V2', 'i35': 'V3', 'i36': 'V1', 'i38': 'V1', 'i39': 'V1'}


def entry_sha(jar, name):
    value = hashlib.sha256()
    with jar.open(name) as stream:
        for chunk in iter(lambda: stream.read(1048576), b''): value.update(chunk)
    return value.hexdigest()


def verify():
    release.LOG = LOG
    before = release.read(REVIEW / 'before.json')
    generation = release.read(LOG / 'resource-generation.json')
    release.require(generation['status'] == 'passed' and generation['revision'] == 181 and len(generation['structures']) == 5, '第9批逐格资源核验未通过')
    index = release.read(ROOT / 'deliveries/多方块确认归档/当前归档索引.json')
    release.require(index['pending_batch']['id'] == 'batch-09' and index['pending_batch']['approved_machine_ids'] == [k.upper() for k in NEW] and index['pending_batch']['count'] == 5, '未达到本批五台明确批准')
    release.require(index['formal_structure_forms'] == 41 and index['approved_structure_forms'] == 46, '批次前状态改变')
    approved = {row['key']: row for row in index['entries'] if row['id'] in [k.upper() for k in NEW]}
    release.require(release.sha(release.base.TARGET) == before['installed_jar_sha256'], '部署前r180目标被改变')
    release.require(before['source_new_resource_collisions'] == [] and before['source_new_resources_absent'], '缺少无碰撞事前证据')
    release.require(all(release.sha(ROOT / path) == value for path, value in before['existing_formal_resources'].items()), '原41形态/旧面板源资源改变')
    frozen, extra = [], []
    with zipfile.ZipFile(release.base.SOURCE) as jar, zipfile.ZipFile(release.base.TARGET) as previous:
        release.require(jar.testzip() is None, '待部署JAR压缩校验失败')
        for name, value in before['installed_resource_hashes'].items():
            release.require(entry_sha(previous, name) == entry_sha(jar, name) == value, '原41建筑或旧控制器贴图改变：' + name)
            frozen.append(dict(path=name, sha256=value))
        for lang, values in before['old_language_values'].items():
            after = json.loads(jar.read(f'assets/hk3gtl/lang/{lang}.json'))
            release.require(all(after.get(k) == v for k, v in values.items()), '旧语言键改变：' + lang)
        machine_class = jar.read('com/sirin/hk3gtl/common/machine/Hk3LateIndustrialMachines.class')
        release.require(b'_unique_r181' in machine_class, '第9批独立材质未引用')
        names = jar.namelist(); fronts = []
        for key in NEW:
            row = approved[key]
            release.require(row['approved_version'] == VERSIONS[key] and row['external_approval_is_authoritative'], '外部批准身份不符：' + key)
            approval = release.read(row['approval_manifest'])
            release.require(approval['external_approval_is_authoritative'] and approval['source_all_bytes_unchanged'], '缺少不可变批准证据：' + key)
            path = f'data/hk3gtl/structures/approved/{key}.json'; metadata = json.loads(jar.read(path))
            release.require(metadata['source_snapshot'] == row['archive'], '未采用各自批准现物：' + key)
            release.require(metadata['revision'] == 181 and metadata['geometry_nbt_json_per_block_verified'] and metadata['game_verified'] is False, '新结构修订或核验边界不符：' + key)
            release.require(metadata['blocks'] == row['block_count'] and metadata['controller'] == row['controller'], '新结构数量/主控偏离批准：' + key)
            release.require(metadata['machine'].split(':', 1)[1].encode() in machine_class, '正式控制器未注册：' + key)
            source_nbt = project_path(row['approved_nbt']); release.require(release.sha(source_nbt) == row['approved_nbt_sha256'], '批准NBT身份改变：' + key)
            paths = [path, f'data/hk3gtl/approved_architecture/{key}.json', f'data/hk3gtl/structures/approved/{key}.nbt', f'data/hk3gtl/structures/approved_preview/{key}.bin.gz']
            panels = [f'assets/hk3gtl/textures/block/overlay/{key}_unique_r181/overlay_front{s}.png' for s in ('', '_active', '_paused')]
            for name in paths + panels:
                value = entry_sha(jar, name); release.require(value == release.sha(ROOT / 'src/main/resources' / name), '新增资源打包不一致：' + name)
                extra.append(dict(path=name, sha256=value))
            fronts.append(entry_sha(jar, panels[0]))
        release.require(len(set(fronts)) == 5, '新增控制器正面不独立')
        release.require(len([p for p in names if p.startswith('data/hk3gtl/structures/approved/') and p.endswith('.nbt')]) == 46, '正式完整NBT不是46形态')
        release.require('data/hk3gtl/structures/approved/i37.nbt' not in names, '未批准I37混入正式包')
    result = dict(status='passed', revision=181, original_shapes=41, new_shapes=5, formal_shapes=46, frozen_resources=frozen,
        new_preview_and_texture_resources=extra, new_cells=generation['cells'], game_verified=False, provisional_processes_unlocked=0,
        new_controller_survival_recipes=0, source_snapshots_external_approval_verified=True, old_language_keys_unchanged=True)
    release.save('batch09-package-verification.json', result)
    return result


def report(status, detail):
    from html import escape
    text = f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>第9批正式接入 · 修订181</title>
<style>body{{font:16px/1.7 system-ui;background:#101927;color:#dce5f2;max-width:1050px;margin:40px auto;padding:24px}}a{{color:#8ad6ec}}section{{background:#182638;padding:24px;margin:20px 0}}code{{overflow-wrap:anywhere}}</style>
<h1>I34、I35、I36、I38、I39 · 第9批正式接入</h1><p>修订181 · {datetime.now(timezone(timedelta(hours=8))).isoformat()}</p>
<section><h2>部署状态：{escape(status)}</h2><p>{escape(detail)}</p><p>唯一目标：增强版2.9.2 / Minecraft1.20.1 / Forge47.4.16。</p></section>
<section><h2>范围</h2><p>I34 V2虚数之树观测阵列、I35 V3虚数空间锚定阵列、I36 V1崩坏能现实稳定锚、I38 V1虚数能量整流中枢、I39 V1无人跨界航路中继站。各自批准版本完整建筑、精确Pattern、游戏内完整预览、独立三态控制器和中英文名称接入，累计46形态；I37仍未批准。</p></section>
<section><h2>证据</h2><p><a href="resource-generation.json">逐格资源核验</a> · <a href="clean-build.json">完整构建收据</a> · <a href="clean-build.log">完整测试</a> · <a href="batch09-package-verification.json">旧41形态冻结与新资源</a> · <a href="package-verification.json">46形态包核验</a> · <a href="controller-textures.html">五套控制器三态</a> · <a href="deployment.json">安装收据</a> · <a href="../batch09-review-20261027/installed-review.json">独立安装核对</a> · <a href="rollback.json">回滚身份</a></p></section>
<section><h2>验收边界</h2><p>文件安装与源码测试分别记录；游戏内实际成型、预览交互、功能工艺及FCL/PC性能另验。本轮不启动/停止游戏，不写存档或第三方模组；暂定工艺与新增控制器生存获取保持关闭。先完成本批接入，再回I37制作。</p></section></html>'''
    (LOG / 'index.html').write_text(text, encoding='utf-8')


def main():
    LOG.mkdir(parents=True, exist_ok=True); verify(); release.KEYS = OLD + NEW
    try:
        release.main(181, LOG)
    except RuntimeError as failure:
        report('已构建，部署未完成', str(failure)); release.save('deployment-blocked.json', dict(status='not_installed', reason=str(failure), revision=181)); raise
    receipt = release.read(LOG / 'deployment.json')
    receipt.update(batch='batch-09', new_formal_controllers=5, new_machine_ids=[key.upper() for key in NEW], existing_41_shapes_unchanged=True, new_world_tasks_unlocked=0)
    release.save('deployment.json', receipt)
    report('已安装，待独立核对', f"旧包备份后替换唯一HK3GTL包；SHA-256：{receipt['sha256']}。本批五台，累计46形态；游戏运行未验收。")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--verify-only', action='store_true')
    args = parser.parse_args(); verify() if args.verify_only else main()
