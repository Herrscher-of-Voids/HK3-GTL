# -*- coding: utf-8 -*-
"""修订180：复用停机、备份及原子替换门禁，额外核验第8批五台与原36形态冻结身份。"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import zipfile

import deploy_late_industrial_20261026 as release

ROOT = release.ROOT
LOG = ROOT / 'logs/batch08-install-20261027'
NEW = [f'i{number}' for number in range(29, 34)]
OLD = list(release.KEYS)


def digest_entry(archive, path):
    digest = hashlib.sha256()
    with archive.open(path) as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def verify():
    release.LOG = LOG
    generation = release.read(LOG / 'resource-generation.json')
    release.require(generation['status'] == 'passed' and len(generation['structures']) == 5,
                    '第8批逐格资源核验未完成')
    frozen, extra = [], []
    with zipfile.ZipFile(release.base.SOURCE) as archive, zipfile.ZipFile(release.base.TARGET) as previous:
        for key in OLD:
            paths = [f'data/hk3gtl/approved_architecture/{key}.json',
                     f'data/hk3gtl/structures/approved/{key}.json',
                     f'data/hk3gtl/structures/approved/{key}.nbt']
            if key in {f'i{number}' for number in range(19, 29)}:
                paths.append(f'data/hk3gtl/structures/approved_preview/{key}.bin.gz')
            for path in paths:
                digest = digest_entry(archive, path)
                release.require(digest == digest_entry(previous, path), '原36批准建筑被改变：' + path)
                frozen.append({'path': path, 'sha256': digest})
        for path in previous.namelist():
            if path.startswith('assets/hk3gtl/textures/block/overlay/') and path.endswith('.png'):
                digest = digest_entry(previous, path)
                release.require(digest_entry(archive, path) == digest, '旧控制器贴图被改变：' + path)
                frozen.append({'path': path, 'sha256': digest})
        for language in ('zh_cn', 'en_us'):
            path = f'assets/hk3gtl/lang/{language}.json'
            before = json.loads(previous.read(path))
            after = json.loads(archive.read(path))
            release.require(all(after.get(key) == value for key, value in before.items()), '旧语言键被改变：' + language)
        machine_class = archive.read('com/sirin/hk3gtl/common/machine/Hk3LateIndustrialMachines.class')
        late_class = archive.read('com/sirin/hk3gtl/common/machine/research/Hk3LateIndustrialMachine.class')
        release.require(b'_unique_r180' in machine_class, '新控制器未引用独立材质')
        for key in NEW:
            manifest = json.loads(archive.read(f'data/hk3gtl/structures/approved/{key}.json'))
            release.require(manifest['machine'].split(':', 1)[1].encode() in machine_class,
                            '新正式控制器未注册：' + key)
            release.require(manifest['revision'] == 180 and manifest['game_verified'] is False,
                            '第8批修订或验收边界不符：' + key)
            if key in ('i29', 'i30', 'i31'):
                release.require(key.upper().encode() in late_class, '模拟世界泡任务未保持关闭：' + key)
            paths = [f'data/hk3gtl/structures/approved_preview/{key}.bin.gz']
            paths += [f'assets/hk3gtl/textures/block/overlay/{key}_unique_r180/overlay_front{state}.png'
                      for state in ('', '_active', '_paused')]
            for path in paths:
                digest = digest_entry(archive, path)
                release.require(digest == release.sha(ROOT / 'src/main/resources' / path), '第8批打包缺失或不一致：' + path)
                extra.append({'path': path, 'sha256': digest})
    result = dict(status='passed', revision=180, original_shapes=36, new_shapes=5, formal_shapes=41,
                  frozen_resources=frozen, new_preview_and_texture_resources=extra,
                  new_cells=generation['cells'], game_verified=False,
                  provisional_processes_unlocked=0, new_controller_survival_recipes=0)
    release.save('batch08-package-verification.json', result)
    return result


def report(status, detail):
    from html import escape
    text = f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>第8批正式接入 · 修订180</title>
<style>body{{font:16px/1.7 system-ui;background:#101927;color:#dce5f2;max-width:1050px;margin:40px auto;padding:24px}}a{{color:#8ad6ec}}section{{background:#182638;padding:24px;margin:20px 0;border-radius:12px}}li{{margin:8px 0}}code{{overflow-wrap:anywhere}}</style>
<h1>I29–I33 第8批正式接入</h1><p>修订180 · {datetime.now(timezone(timedelta(hours=8))).isoformat()}</p>
<section><h2>部署状态：{escape(status)}</h2><p>{escape(detail)}</p>
<p>唯一目标：GregTech Leisure-增强版 2.9.2 / Minecraft 1.20.1 / Forge 47.4.16。</p></section>
<section><h2>本批范围</h2><ul><li>I29 模拟世界泡构筑机，批准V1，ICV。</li><li>I30 模拟世界泡稳定控制器，批准V1，ICV。</li>
<li>I31 模拟世界泡终止回收机，批准V1，ICV。</li><li>I32 遗留技术逆向实验室，批准V1，QAV。</li><li>I33 仿制神之键装配中心，批准V1，QCV。</li></ul>
<p>41种正式建筑形态，包含原36种及本批5种；完整建筑、原位控制器与工作仓、精确Pattern、完整游戏内预览、独立三态面板与中英文名称同包接入。</p></section>
<section><h2>证据</h2><p><a href="resource-generation.json">批准档案与正式资源逐格核验</a> · <a href="clean-build.json">完整构建收据</a> · <a href="clean-build.log">完整测试输出</a> · <a href="batch08-package-verification.json">新增资源及原36形态冻结核验</a> · <a href="package-verification.json">41形态包核验</a> · <a href="controller-textures.html">5套独立面板</a> · <a href="deployment.json">部署收据</a> · <a href="rollback.json">备份身份</a></p></section>
<section><h2>验收边界</h2><p>文件安装与源码测试已分别记录。游戏内完整预览显示、实际成型、运行及大型结构性能尚需实机验收。未启动或停止游戏，未读写存档，未更改第三方模组。暂定工艺、I29–I31未实现的模拟世界泡任务及新控制器生存获取保持关闭。</p></section></html>'''
    (LOG / 'index.html').write_text(text, encoding='utf-8')


def main():
    LOG.mkdir(parents=True, exist_ok=True)
    verify()
    release.KEYS = OLD + NEW
    try:
        release.main(180, LOG)
    except RuntimeError as failure:
        report('已构建，部署未完成', str(failure))
        release.save('deployment-blocked.json', dict(status='not_installed', reason=str(failure), revision=180))
        raise
    receipt = release.read(LOG / 'deployment.json')
    receipt.update(batch='batch-08', new_formal_controllers=5, new_machine_ids=[key.upper() for key in NEW],
                   existing_36_shapes_unchanged=True, new_world_tasks_unlocked=0)
    release.save('deployment.json', receipt)
    report('已安装', f"已备份旧包并替换唯一目标HK3GTL包；SHA-256：{receipt['sha256']}。本批5台，累计41形态。")


if __name__ == '__main__':
    main()
