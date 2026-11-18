# -*- coding: utf-8 -*-
"""归档0005雷律构图A1，局部追加候选与固定报告记录。"""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/0005_W04_鸣霆超导电磁天枢_构图A1_20261114'
LOG = ROOT / 'logs/0005-w04-em-skyhub-a1-20261114'
REPORT = ROOT / 'logs/beta5-completion-audit-20261030'
KEY = 'w04_0005_em_skyhub_a1'
CONVERSATION = '01a1d6b8-bd81-79d3-a6f4-4f590806cc8e'


def load(path):
    return json.loads(path.read_text('utf8'))


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8')


def main():
    manifest = load(OUT / 'manifest.json')
    verification = load(OUT / 'verification.json')
    render = load(LOG / 'viewer-render.json')
    moment = datetime.now(timezone(timedelta(hours=8)))
    now = moment.isoformat(timespec='seconds')
    history = LOG / ('history-' + moment.strftime('%Y%m%d-%H%M%S-%f'))
    history.mkdir()
    for name in ['index.html', 'current-summary.json']:
        shutil.copy2(REPORT / name, history / name)
    for name in ['AGENTS.md', 'rule/当前多方块设计规则.md']:
        shutil.copy2(ROOT / name, history / Path(name).name)

    preview = (OUT / '三维布局.html').relative_to(ROOT).as_posix()
    review = dict(headless=render['headless'], errors=render['errors'],
                  screenshots=[render['screenshot']] + [x['file'] for x in render['rendered']])
    item = dict(id='W04', candidate='0005 鸣霆·超导电磁天枢构图A1', conversation_id=CONVERSATION,
                preview=preview, scope='项目现有材料、完整静态整数格构图预览；待外观评审',
                actual_scene_size_xyz=manifest['actual_scene_size_xyz'], blocks=manifest['block_count'],
                components=manifest['components'], materials=manifest['palette_count'],
                transforms=manifest['transforms'], bounds_world=manifest['bounds_world'],
                blueprint_to_export_offset_xyz=manifest['blueprint_to_export_offset_xyz'],
                whole_integer_voxel=manifest['whole_integer_voxel'],
                export=verification['export'], viewer_review=review,
                controller_world=manifest['controller_world'], controller_registered=False,
                controller_placeholder_state=manifest['controller_placeholder_state'],
                ports_world=manifest['ports_world'], new_block_ids=manifest['new_block_ids'],
                animation_enabled=False, approved=False, game_verified=False,
                remaining=manifest['known_issues'],
                evidence=LOG.relative_to(ROOT).as_posix(), updated_at=now)

    data = load(REPORT / 'current-summary.json')
    system = next(s for s in data['systems'] if s['id'] == 'multiblocks')
    system[KEY] = deepcopy(item)
    system['updated_at'] = now
    data['current_work'][KEY] = deepcopy(item)
    data['report_updated_at'] = now
    data['updated_at'] = now
    width, height, depth = item['actual_scene_size_xyz']
    browser = f'浏览器记录{len(render["errors"])}项错误' if render['errors'] else '浏览器截图已生成，待负责人评审'
    note = (f'{now} · 对话0005独立候选：W04鸣霆·超导电磁天枢构图A1，'
            f'实际宽{width}×深{depth}×高{height}格、{item["blocks"]:,}块、{item["components"]}构件，'
            f'使用{item["materials"]}种现有方块状态。{browser}。'
            '静态；红石块为主控位置占位；未外观批准、未游戏搭建／成型／运行，分数和批准数量不变。')
    page = (REPORT / 'index.html').read_bytes().decode('utf8')
    page = re.sub(r'<p class="notice" id="0005-w04-a1">.*?</p>\s*', '', page, flags=re.S)
    notice = ('<p class="notice" id="0005-w04-a1">' + escape(note)
              + ' <a href="../../' + escape(preview, quote=True) + '">0005构图A1</a></p>')
    page = re.sub(r'(<h1>系统完成度 · 研发口径 · 固定入口</h1>)',
                  lambda m: m[1] + '\n' + notice, page, count=1)
    payload = json.dumps(data, ensure_ascii=False).replace('<', '\\u003c')
    page = re.sub(r'(<script\b[^>]*\bid="audit-data"[^>]*>).*?(</script>)',
                  lambda m: m[1] + payload + m[2], page, count=1, flags=re.S)

    marker = '## 2026-11-14 对话0005：W04鸣霆超导电磁天枢构图A1候选'
    rule = (f'\n\n{marker}\n\n'
            f'- 本节仅适用于对话ID `{CONVERSATION}`（0005多方块设计）及其委派任务；'
            '本对话JAR沿用 `0005多方块设计-<版本号>.jar`，本次未构建JAR。\n'
            f'- 独立预览：`{preview}`；实际宽{width}×深{depth}×高{height}格，'
            f'{item["blocks"]:,}块、{item["components"]}构件、{item["materials"]}种现有方块状态；'
            '三层水平超导磁环、七相汇流雷池、左前七雷、右后龙首与展开双翼，双侧储能塔及低温冷却站。\n'
            '- 龙体由D4按0.74倍缩放后重新量化并平移[65,54,-100]；七雷由S1按0.32倍缩放、'
            '绕Z轴90°后重新量化，锚点[5,53,0]对齐[-90,96,240]；源文件和旧候选保留。'
            '完整生成后计算真实包围盒，未按697×565×343名义范围裁切。\n'
            '- 全静态、使用项目已有材质、无新增方块ID；主控[0,18,329]为红石块占位，'
            '无固定八孔接口，玩家按现行规则在实体非主控位置替换合法通用接口。\n'
            f'- NBT／Schematic回读及浏览器截图的实际记录见 `{item["evidence"]}/`；{browser}。'
            '候选未获外观批准，未进行游戏搭建、成型或运行；不替换旧候选，不改变37域分数、能力分母或批准数量。\n')
    for path in [ROOT / 'AGENTS.md', ROOT / 'rule/当前多方块设计规则.md']:
        content = path.read_bytes().decode('utf8')
        if marker not in content:
            path.write_bytes((content + rule).encode('utf8'))
    save(REPORT / 'current-summary.json', data)
    (REPORT / 'index.html').write_bytes(page.encode('utf8'))
    receipt = dict(recorded_at=now, history=history.relative_to(ROOT).as_posix(),
                   candidate_key=KEY, preview=preview, systems=len(data['systems']),
                   overall_percent=data['overall_percent'], multiblocks_percent=system['percent'],
                   browser_errors=render['errors'], game_verified=False,
                   modified_fields=['multiblocks.' + KEY, 'current_work.' + KEY, '更新时间戳', '0005独立候选记录'])
    save(LOG / 'audit-update.json', receipt)
    shutil.copy2(Path(__file__), OUT / '生成脚本' / Path(__file__).name)
    print(json.dumps(receipt, ensure_ascii=False))


if __name__ == '__main__':
    main()
