# -*- coding: utf-8 -*-
"""将用户确认的 I01-1 V1 原样封存，不安装游戏文件。"""
import datetime as dt
import hashlib
import html
import json
import shutil
import zipfile
from pathlib import Path

import nbtlib


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'deliveries/I01-1_崩坏能采集塔液态_分层集流塔_V1_20261025'
ARCHIVES = ROOT / 'deliveries/多方块确认归档'
RECORDS = ROOT / 'doc/HK3GTL-内测5/讨论记录'
APPROVAL = 'ok 下一台吧'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    now = dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))
    stamp = now.strftime('%Y%m%d_%H%M%S_%f')
    name = f'{stamp}_I01-1_HBV液态采集塔V1'
    snapshot = ARCHIVES / name
    bundle = ARCHIVES / f'{name}.zip'
    record = RECORDS / f'{now:%Y-%m-%d_%H-%M-%S}_I01-1_V1确认归档.html'
    if snapshot.exists() or bundle.exists() or record.exists():
        raise FileExistsError(f'归档目标已存在：{name}')

    source_files = {p.relative_to(SOURCE).as_posix(): sha(p)
                    for p in sorted(SOURCE.rglob('*')) if p.is_file()}
    source_report = json.loads((SOURCE / '设计与检查.json').read_text(encoding='utf-8'))
    source_data, source_audit = source_report['data'], source_report['audit']
    nbt_path = SOURCE / (source_data['name'] + '.nbt')
    schem_path = SOURCE / (source_data['name'] + '.schem')
    nbt = nbtlib.load(nbt_path)
    if len(nbt['blocks']) != source_audit['block_count']:
        raise ValueError('I01-1 NBT 方块数与审计记录不符')
    if int(nbt['DataVersion']) != 3465:
        raise ValueError('I01-1 NBT DataVersion 不符')
    if list(map(int, nbt['size'])) != source_data['size']:
        raise ValueError('I01-1 NBT 尺寸与审计记录不符')
    if sha(nbt_path) != source_audit['hashes']['nbt']:
        raise ValueError('I01-1 NBT SHA-256 与审计记录不符')
    if sha(schem_path) != source_audit['hashes']['schem']:
        raise ValueError('I01-1 Sponge SHA-256 与审计记录不符')

    snapshot.mkdir(parents=True)
    archived_delivery = snapshot / 'I01-1'
    shutil.copytree(SOURCE, archived_delivery)
    if source_files != {p.relative_to(archived_delivery).as_posix(): sha(p)
                        for p in sorted(archived_delivery.rglob('*')) if p.is_file()}:
        raise ValueError('封存副本与原交付 SHA-256 不一致')

    dependencies = snapshot / '生成依赖'
    dependencies.mkdir()
    for filename in ('build_i01_liquid_redesign_v1.py', 'build_redesign69.py',
                     'material_resources.py', 'redesign69_geometry.py',
                     'structure_size_baseline.py', 'check_i01_upgrade.py'):
        source = ROOT / 'tools/structure_delivery' / filename
        shutil.copy2(source, dependencies / filename)
    shutil.copy2(Path(__file__), dependencies / Path(__file__).name)

    rows = []
    for path in sorted(snapshot.rglob('*')):
        if path.is_file():
            rel = path.relative_to(snapshot).as_posix()
            rows.append(f'<tr><td><code>{html.escape(rel)}</code></td>'
                        f'<td><code>{sha(path)}</code></td></tr>')
    manifest = snapshot / '确认与校验清单.html'
    manifest.write_text(f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>I01-1 V1 确认与校验归档</title>
<style>body{{max-width:1100px;margin:32px auto;padding:0 20px;background:#111923;color:#e8edf3;font:15px/1.7 system-ui,"Microsoft YaHei",sans-serif}}a{{color:#80d8d0}}table{{width:100%;border-collapse:collapse;overflow-wrap:anywhere}}td,th{{border:1px solid #42515e;padding:7px;text-align:left}}code{{font-size:12px;overflow-wrap:anywhere}}.ok{{color:#a6e5d5}}</style></head><body>
<h1>I01-1 崩坏能采集塔·液态 V1</h1>
<p>确认时间：{html.escape(now.isoformat())}（Asia/Hong_Kong）</p>
<p>确认原话：<q>{html.escape(APPROVAL)}</q>。状态：用户已批准外观与逐格结构；独立归档，未接入游戏实例。</p>
<p>结构：43×55×43（宽×高×深），{source_audit['block_count']:,} 个方块、{source_audit['unique_material_count']} 种材料、实体包围盒体积 {source_audit['actual_volume']:,}、高度 {source_audit['actual_size_wdh'][1]}；主控锚点 {html.escape(str(source_data['controller']))}。</p>
<p class="ok">NBT 与 Sponge v2 的记录 SHA-256、尺寸和方块数已核对；封存副本逐文件 SHA-256 与原交付一致；ZIP 完整性与成员哈希均已核对。</p>
<p>下一阶段 I01-2 以本归档的 I01-1 逐格结构为底稿，保持同一主控世界锚点，仅替换实际阶段控制器并扩建；本预览归档不证明 Pattern、配方、生存可达性或游戏内成型。</p>
<p>源交付：<code>{html.escape(str(SOURCE))}</code><br>归档目录：<code>{html.escape(str(snapshot))}</code></p>
<h2>封存文件 SHA-256</h2><table><thead><tr><th>文件</th><th>SHA-256</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
</body></html>''', encoding='utf-8')

    archived_hashes = {p.relative_to(snapshot).as_posix(): sha(p)
                       for p in sorted(snapshot.rglob('*')) if p.is_file()}
    with zipfile.ZipFile(bundle, 'x', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for relative in archived_hashes:
            archive.write(snapshot / relative, relative)
    with zipfile.ZipFile(bundle) as archive:
        if archive.testzip() is not None or set(archive.namelist()) != set(archived_hashes):
            raise ValueError('归档 ZIP 文件清单或 CRC 校验失败')
        for relative, expected in archived_hashes.items():
            if hashlib.sha256(archive.read(relative)).hexdigest() != expected:
                raise ValueError(f'归档 ZIP 成员 SHA-256 不符：{relative}')

    zip_hash = sha(bundle)
    record.write_text(f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>I01-1 V1 用户确认与归档</title>
<style>body{{max-width:900px;margin:36px auto;padding:0 22px;background:#111923;color:#e8edf3;font:16px/1.8 system-ui,"Microsoft YaHei",sans-serif}}code{{overflow-wrap:anywhere}}a{{color:#80d8d0}}</style></head><body>
<h1>I01-1 V1 用户确认与归档</h1><p>记录时间：{html.escape(now.isoformat())}；界面原始确认消息：<q>{html.escape(APPROVAL)}</q>。</p>
<p>确认范围：HBV 液态采集塔 V1 的外观和逐格结构。状态：已批准并独立封存；未部署游戏文件。</p>
<p>归档 ZIP：<code>{html.escape(str(bundle))}</code><br>ZIP SHA-256：<code>{zip_hash}</code></p>
<p>确认清单：<a href="../../../deliveries/多方块确认归档/{html.escape(name)}/确认与校验清单.html">HTML 清单</a>；评审页：<a href="../../../deliveries/多方块确认归档/{html.escape(name)}/I01-1/index.html">原样封存的 I01-1 V1</a>。</p>
<p>I01-2 将基于此封存版本扩建。游戏内 Pattern、配方、生存材料前置和成型运行仍需另行核验。</p>
</body></html>''', encoding='utf-8')
    if source_files != {p.relative_to(SOURCE).as_posix(): sha(p)
                        for p in sorted(SOURCE.rglob('*')) if p.is_file()}:
        raise ValueError('归档过程修改了原始候选交付')
    print(json.dumps({'snapshot': str(snapshot), 'zip': str(bundle), 'zip_sha256': zip_hash,
                      'approval_record': str(record), 'source_unchanged': True,
                      'files_verified': len(archived_hashes)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
