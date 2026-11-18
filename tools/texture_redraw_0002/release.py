# -*- coding: utf-8 -*-
from pathlib import Path
from datetime import datetime, timedelta, timezone
from zipfile import ZipFile
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/0002贴图材质_全量重绘_V2_20261114'
LOG = ROOT / 'logs/textures-redraw-0002-v2-20261114'
REPORT = ROOT / 'logs/beta5-completion-audit-20261030'
SOURCE = ROOT / 'deliveries/物品贴图与旧资源清理_20261114/0002贴图材质-0.5.0.jar'
JAR = OUT / '0002贴图材质-0.5.0-R2.jar'
NOW = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    manifest = json.loads((OUT / 'manifest.json').read_text(encoding='utf-8'))
    changed = {f'assets/hk3gtl/{row["path"]}': (OUT / row['path']).read_bytes()
               for row in manifest['items'] if row['changed']}
    untouched_before = {}
    with ZipFile(SOURCE) as source, ZipFile(JAR, 'w') as output:
        for entry in source.infolist():
            data = source.read(entry.filename)
            if entry.filename in changed:
                output.writestr(entry, changed[entry.filename])
            else:
                untouched_before[entry.filename] = digest(data)
                output.writestr(entry, data)
    unchanged_matches = 0
    with ZipFile(JAR) as result:
        for path, sha in untouched_before.items():
            unchanged_matches += digest(result.read(path)) == sha
    jar_hash = digest(JAR.read_bytes())
    jar_bytes = JAR.stat().st_size
    receipt = {
        'revision': 'R2', 'updated_at': NOW, 'candidate': {
            'path': str(JAR.relative_to(ROOT)).replace('\\', '/'),
            'bytes': jar_bytes, 'sha256': jar_hash,
            'source_path': str(SOURCE.relative_to(ROOT)).replace('\\', '/'),
            'source_sha256': digest(SOURCE.read_bytes()),
            'changed_texture_entries': len(changed), 'untouched_entries': len(untouched_before),
            'untouched_entry_contents_match': unchanged_matches == len(untouched_before),
            'installed': False, 'game_tested': False
        },
        'redrawn_count': manifest['redrawn_count'], 'preserved_count': manifest['preserved_count'],
        'gallery': 'deliveries/0002贴图材质_全量重绘_V2_20261114/index.html',
        'manifest': 'deliveries/0002贴图材质_全量重绘_V2_20261114/manifest.json',
        'art_approved': False, 'audit_score_changed': False,
        'build_note': '仅将本对话0.5.0候选JAR内的87张物品PNG替换为R2；沿用原编译代码，未重新构建共享工程。'
    }
    (LOG / 'completion.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (OUT / 'completion.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    summary_path = REPORT / 'current-summary.json'
    html_path = REPORT / 'index.html'
    shutil.copy2(summary_path, REPORT / 'current-summary-before-item-texture-redraw-0002-R2.json')
    shutil.copy2(html_path, REPORT / 'index-before-item-texture-redraw-0002-R2.html')
    summary = json.loads(summary_path.read_text(encoding='utf-8'))
    summary['item_texture_redraw_0002_r2_20261114_completion'] = receipt
    if summary['current_work']['evidence'] == 'logs/item-resource-cleanup-20261114/completion.json':
        summary['current_work'] = {
            'system': '物品贴图材质（对话2 / 0002）',
            'state': '87张原生64×64透明物品贴图重绘候选已完成；保留负责人认可的真实采掘遗留资料，并让仿制虚空万藏继续复用普通原图。待负责人评审。',
            'remaining': ['负责人美术评审待进行；本候选未安装，未进行游戏验收。', '候选JAR只沿用本对话上一版编译代码，未合入其他并行对话更新。'],
            'scope': '贴图及独立候选资源包；不修改系统分数、分母、验收记录或系统排序。',
            'evidence': receipt['gallery']
        }
    summary['report_updated_at'] = NOW
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    page = html_path.read_text(encoding='utf-8')
    card = f'<section id="item-texture-redraw-0002-r2-20261114" class="notice"><h2>0002贴图材质 · R2全量重绘候选</h2><p>{NOW} · 87张物品贴图按Minecraft像素实物、GregTech工业材质与崩坏3身份形制重画，均为原生64×64透明PNG；仅保留你认可的“真实采掘遗留资料”。仿制虚空万藏继续引用普通原图。美术待负责人评审，未安装、未游戏验收，不改完成分。</p><p><a href="../../deliveries/0002贴图材质_全量重绘_V2_20261114/index.html">查看88张新旧对照</a> · <a href="../../logs/textures-redraw-0002-v2-20261114/completion.json">R2交付回执</a></p></section>'
    anchor = '<section id="offline-maximize-current">'
    page = page.replace(anchor, card + anchor, 1)
    data_open = page.index('id="audit-data"')
    data_start = page.index('{', data_open)
    data_end = page.index('</script>', data_start)
    page = page[:data_start] + json.dumps(summary, ensure_ascii=False, indent=2) + '\n' + page[data_end:]
    html_path.write_text(page, encoding='utf-8')
    print(json.dumps({'jar': receipt['candidate'], 'audit_score_changed': False}, ensure_ascii=False))


if __name__ == '__main__':
    main()
