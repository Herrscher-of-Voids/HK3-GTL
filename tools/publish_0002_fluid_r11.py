# -*- coding: utf-8 -*-
"""记录流体新绘、删除撤销与固定报告状态。"""
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / 'logs/textures-fluid-redraw-0002-r11-20261115'
DELIVERY = ROOT / 'deliveries/0002贴图材质_全流体重绘_R11_20261115'
INVENTORY = ROOT / 'deliveries/0002贴图材质_全库材质清单_R10采用_20261115'
AUDIT = ROOT / 'logs/beta5-completion-audit-20261030'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def main():
    manifest = read(LOG / 'manifest.json')
    inventory = read(INVENTORY / 'manifest.json')
    now = datetime.now(ZoneInfo('Asia/Hong_Kong'))
    stamp = now.isoformat(timespec='seconds')
    backup = LOG / ('before-report-' + now.strftime('%Y%m%d-%H%M%S'))
    backup.mkdir()
    for source in (AUDIT / 'index.html', AUDIT / 'current-summary.json', ROOT / 'AGENTS.md'):
        shutil.copy2(source, backup / source.name)
    summary = read(AUDIT / 'current-summary.json')
    receipt = {'updated_at': stamp, 'conversation_number': '0002',
               'conversation_id': manifest['conversationId'], 'revision': 'R11',
               'state': '负责人撤销55项删除，原资源与关联引用恢复；全部47种流体新绘并接入，待逐项美术评审。',
               'restored_png_count': 55, 'restored_sidecar_count': 10, 'restored_unused_model_count': 11,
               'restored_item_model_reference_count': 8, 'restored_catalog_entry_count': 11,
               'fluid_count': manifest['fluidCount'], 'liquid_count': 43, 'gas_count': 4,
               'runtime_png_count': manifest['textureCount'], 'replaced_png_count': 76, 'new_png_count': 18,
               'animation_frames_per_png': 4,
               'actual_api_sizes': sorted({tuple(r['actualApiSize']) for r in manifest['records']}),
               'originals_preserved': True, 'resized': False, 'runtime_frames_resized': False,
               'animation_method': manifest['animationMethod'], 'reference_images_uploaded': 0,
               'api_model_alias': manifest['apiModelAlias'],
               'api_adapter': 'tools/invoke_image_relay.ps1 -Mode Generate -RelayResponse',
               'bundled_imagegen_cli_used': False, 'art_approved': False,
               'new_fluid_custom_texture_registration_count': 9,
               'current_png_count': inventory['totalPngCount'], 'other_than_r10_count': inventory['otherPngCount'],
               'current_animation_png_count': inventory['animationCount'],
               'category_count': len(inventory['groups']), 'art_status_counts': inventory['statusCounts'],
               'r10_unchanged_count': 39, 'current_accepted_id_count': 66,
               'restoration_receipt': 'logs/textures-fluid-redraw-0002-r11-20261115/restoration.json',
               'scope': 'logs/textures-fluid-redraw-0002-r11-20261115/fluid-scope.json',
               'manifest': (DELIVERY / 'manifest.json').relative_to(ROOT).as_posix(),
               'gallery': (DELIVERY / 'index.html').relative_to(ROOT).as_posix(),
               'prompt_set': 'output/imagegen/fluids-0002-r11/prompts.json',
               'inventory_gallery': (INVENTORY / 'index.html').relative_to(ROOT).as_posix(),
               'visual_readback': 'logs/textures-fluid-redraw-0002-r11-20261115/visual-readback.json',
               'report_backup': backup.relative_to(ROOT).as_posix(),
               'jar_built': False, 'compiled': False, 'installed': False, 'game_tested': False,
               'desktop_operated': False, 'automated_tests_run': False, 'scores_changed': False,
               'overall_percent_unchanged': summary['overall_percent'],
               'development_percent_unchanged': summary['development_metric']['overall_percent'],
               'domain_count_unchanged': summary['domain_count']}
    (LOG / 'completion.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
    summary['report_updated_at'] = stamp
    summary['texture_fluid_redraw_0002_r11_20261115'] = receipt
    summary['texture_retention_0002_20261115'] = {
        'updated_at': stamp, 'decision': '不删贴图了，保留吧，但是所有流体请重新画贴图。',
        'supersedes': 'texture_deletion55_0002_20261115', 'deletion_reversed': True,
        'restored_png_count': 55, 'receipt': receipt['restoration_receipt']}
    summary['texture_inventory_0002_current'] = {
        'updated_at': stamp, 'current_png_count': inventory['totalPngCount'],
        'other_than_r10_count': inventory['otherPngCount'],
        'current_animation_png_count': inventory['animationCount'],
        'fluid_count': 47, 'fluid_png_count': 94, 'art_approved': False,
        'gallery': receipt['inventory_gallery'],
        'manifest': (INVENTORY / 'manifest.json').relative_to(ROOT).as_posix(),
        'receipt': 'logs/textures-fluid-redraw-0002-r11-20261115/completion.json'}
    industrial = next(r for r in summary['systems'] if r['id'] == 'industrial_lines')
    industrial['fluid_texture_redraw_0002_r11'] = {
        'updated_at': stamp, 'state': '47种流体专用彩色材质已接入源码，含9种新增工业流体；待美术评审，未构建或游戏验收。',
        'fluid_count': 47, 'runtime_png_count': 94, 'new_fluid_custom_texture_count': 9,
        'scores_changed': False, 'receipt': 'logs/textures-fluid-redraw-0002-r11-20261115/completion.json'}
    payload = json.dumps(summary, ensure_ascii=False, indent=2)
    page = (AUDIT / 'index.html').read_text(encoding='utf-8-sig')
    old = re.search(r'<section class="notice" id="texture-deletion55-0002">.*?</section>', page, re.S)
    if old:
        page = page[:old.start()] + '<details id="texture-deletion55-history"><summary>55项删除历史 · 已按负责人最新决定撤销</summary>' + old.group() + '</details>' + page[old.end():]
    notice = f'''<section class="notice" id="texture-fluid-0002-r11"><h2>0002 · 旧图恢复保留，47种流体重绘R11</h2><p>负责人已撤销删除：55张旧PNG、10份动画元数据、11份闲置模型及11条目录记录恢复，8份功能模型回到原图引用，关联旧覆层和生成入口一并恢复。R7独立控制器和R10的39张保持。</p><p>本轮按流体名称、实际工艺与用途重新生图：43液体＋4气体，共47张1254×1254完整API原图；由新图接成94张1254×5016的四帧RGBA动画资源，未缩成64或16像素。76张替换、18张新增，9种新增流体接入独立彩色纹理；原图、提示词、气体透明度及平铺预览均保留。美术尚待负责人评审，累计认可仍为66个ID。</p><p>当前全库{inventory['totalPngCount']}张PNG，其中流体94张、动画{inventory['animationCount']}张、18类。两种负载／失活分离介质仅有注册，未找到实际配方；本轮不宣称补齐其工艺闭环。未编译、构建JAR、安装或启动游戏；37域分数与分母保持。</p><p>{stamp} · <a href="../../{receipt['gallery']}">47种流体与动画评审</a> · <a href="../../{receipt['inventory_gallery']}">当前全库清单</a> · <a href="../textures-fluid-redraw-0002-r11-20261115/completion.json">本轮回执</a></p></section>'''
    page = page.replace('<body>', '<body>' + notice, 1)
    page = page.replace('首次完整清点为1633张；负责人随后删除55张，当前清单数量见顶部最新删除记录。', '首次完整清点为1633张；删除决定已撤销，最新数量与全流体重绘见顶部R11记录。')
    page = re.sub(r'(<script\b(?=[^>]*\bid="audit-data")[^>]*>).*?(</script>)', lambda m: m[1] + payload.replace('</', '<\\/') + m[2], page, count=1, flags=re.S)
    (AUDIT / 'current-summary.json').write_text(payload, encoding='utf-8')
    (AUDIT / 'index.html').write_text(page, encoding='utf-8')
    memory = f'''

## 2026-11-15 对话0002：撤销55项删除，全流体重绘R11

- 仅适用于0002贴图材质，对话ID `01a1d68a-a994-7ac0-a48a-54c0f98fd54e`。负责人最新原话：“不删贴图了，保留吧，但是所有流体请重新画贴图。”本条覆盖上文55项删除策略及此前9种新流体免画安排；旧删除回执只作历史，不能继续清理这些路径。
- 删除轮的55张PNG、10份mcmeta、11份闲置模型、11条目录记录、8份功能模型原材质引用、4份Java覆层引用、7个生成工具及76份缓存均已恢复。R7既有独立控制器与R10的39张不变；恢复证据为 `logs/textures-fluid-redraw-0002-r11-20261115/restoration.json`。
- 当前全部47种流体（43液体、4气体）均已独立使用绑定API按名称／工艺新绘，不参考旧贴图。实际原图全部1254×1254，完整保留；由新图接成94张1254×5016四帧RGBA资源，边缘接缝、流向与气体透明度另作接入处理，未缩成64／16。9种新增工业流体的注册已加 `textures(true,true)`，使用专用彩色图，不叠材质染色；未改配方。
- 评审入口 `deliveries/0002贴图材质_全流体重绘_R11_20261115/index.html`；逐项API原图、提示词、平铺、动画与代码事实见同目录及manifest。47种新图待负责人评审，累计认可ID仍66；两种负载／失活分离介质仅有注册而无实际配方，不把图像接入称为工艺闭环完成。
- 当前全库{inventory['totalPngCount']}张PNG，除R10外{inventory['otherPngCount']}张，流体94张，动画{inventory['animationCount']}张；原全库清单入口继续更新。未编译、构建JAR、安装或运行游戏，37域固定分数与分母保持；回执 `logs/textures-fluid-redraw-0002-r11-20261115/completion.json`。
'''
    with (ROOT / 'AGENTS.md').open('a', encoding='utf-8') as stream:
        stream.write(memory)
    print(json.dumps({k: receipt[k] for k in ['fluid_count', 'runtime_png_count', 'current_png_count', 'current_animation_png_count', 'gallery']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
