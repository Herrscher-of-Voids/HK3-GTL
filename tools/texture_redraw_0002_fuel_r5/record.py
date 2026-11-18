import hashlib
import json
import re
import shutil
import zipfile
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/0002贴图材质_燃料棒_R5_20261114'
LOG = ROOT / 'logs/textures-fuel-0002-r5-20261114'
AUDIT = ROOT / 'logs/beta5-completion-audit-20261030'
REVIEW = ROOT / 'logs/textures-redraw-0002-r3-20261114/art-review.json'


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def record():
    now = datetime.now().astimezone().isoformat(timespec='seconds')
    manifest = json.loads((OUT / 'manifest.json').read_text(encoding='utf-8'))
    inventory = json.loads((LOG / 'inventory.json').read_text(encoding='utf-8'))
    states = [s for f in inventory['families'] for s in f['states']]
    models = [s['model_path'] for s in states if s['texture_ref'] != 'hk3gtl:item/' + s['id']]
    bundle_models = [i['existing_model_path'] for i in manifest['items'] if i['rods'] > 1]
    for source in (REVIEW, AUDIT / 'current-summary.json', AUDIT / 'index.html'):
        dest = LOG / 'before-finalize' / datetime.now().strftime('%Y%m%d-%H%M%S') / source.relative_to(ROOT)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, dest)

    archive = OUT / '0002贴图材质-R5-燃料棒资源.zip'
    manifest['resource_archive'] = archive.name
    manifest['resource_archive_contents'] = {'png': 181, 'existing_model_texture_links': len(models), 'bundle_model_texture_links': len(bundle_models), 'new_model': 0}
    write_json(OUT / 'manifest.json', manifest)
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for local in [i['source_path'] for i in manifest['items']] + models + bundle_models:
            source = ROOT / local
            z.write(source, source.relative_to(ROOT / 'src/main/resources').as_posix())
        z.write(OUT / 'manifest.json', 'manifest.json')

    receipt = {k: manifest[k] for k in ('revision', 'conversation_number', 'conversation_id',
               'native_size', 'mode', 'existing_single_textures', 'new_bundle_textures', 'image_count',
               'art_approved', 'new_items_registered', 'recipe_changed', 'jar_built', 'installed', 'game_tested')}
    receipt.update({'updated_at': now, 'reference_confirmed': True,
        'ordinary_rod_sha256': manifest['reference_sha256'], 'existing_model_texture_links': len(models),
        'model_texture_paths': models, 'bundle_model_texture_links': len(bundle_models),
        'bundle_model_paths': bundle_models, 'bundle_items_registered_by': '0003',
        'new_model_created': False, 'java_changed': False,
        'automated_tests_run': False, 'accepted_40_modified': False, 'score_changed': False,
        'visual_review': ['preview.png', 'state-contact-sheet.png', 'bundle-preview.png'],
        'delivery': (OUT / 'index.html').relative_to(ROOT).as_posix(),
        'manifest': (OUT / 'manifest.json').relative_to(ROOT).as_posix(),
        'resource_archive': archive.relative_to(ROOT).as_posix(),
        'resource_archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
        'remaining': ['181张燃料材质仍待负责人美术评审',
                      '神之键R6两张独立待审；66张认可贴图保持', '5项燃料工艺中间品本轮未重绘']})
    write_json(LOG / 'completion.json', receipt)
    review = json.loads(REVIEW.read_text(encoding='utf-8'))
    singles = {i['id'] for i in manifest['items'] if i['rods'] == 1}
    review.update({'updated_at': now, 'fuel_reference_status': 'confirmed_user_selected_cyan_honkai_fuel_rod',
        'fuel_reference_policy': manifest['reference_policy'], 'fuel_candidate': receipt['delivery'],
        'fuel_candidate_single_ids': sorted(singles), 'fuel_bundle_texture_count': 135,
        'fuel_candidate_image_count': 181, 'fuel_drafts_approved': False,
        'paused_fuel_note': '余下5项是燃料工艺中间品，等待单独重绘；燃料棒母图已确认并完成R5候选。'})
    review['paused_fuel_ids'] = [i for i in review['paused_fuel_ids'] if i not in singles]
    write_json(REVIEW, review)

    summary = json.loads((AUDIT / 'current-summary.json').read_text(encoding='utf-8'))
    summary['updated_at'] = summary['report_updated_at'] = now
    summary['item_texture_fuel_0002_r5_20261114_completion'] = {
        'receipt': (LOG / 'completion.json').relative_to(ROOT).as_posix(),
        'preview': receipt['delivery'], 'single_png': 46, 'bundle_png': 135,
        'existing_model_texture_links': len(models), 'bundle_model_texture_links': len(bundle_models),
        'bundle_items_registered_by': '0003', 'art_approved': False,
        'new_items_registered': False, 'score_changed': False}
    summary['current_work'].update({
        'system': '物品贴图材质（对话2 / 0002）',
        'state': 'R5燃料181张64×64候选保留；0003提供的135个多联模型已接通独立材质，66张认可项及神之键R6候选保持。',
        'remaining': receipt['remaining'] + ['仅资源开发，未打包、安装或运行游戏，37域原分数与分母保持。'],
        'scope': '仅接通0003现有多联模型的layer0材质引用，不改PNG、注册、Java、配方或研究。',
        'evidence': receipt['delivery']})
    write_json(AUDIT / 'current-summary.json', summary)
    html = (AUDIT / 'index.html').read_text(encoding='utf-8-sig')
    payload = json.dumps(summary, ensure_ascii=False).replace('</', '<\\/')
    html = re.sub(r'(<script\b[^>]*\bid=["\']audit-data["\'][^>]*>).*?(</script>)',
                  lambda m: m[1] + payload + m[2], html, flags=re.S)
    notice = ('<section class="notice" id="item-texture-0002-fuel-r5"><h2>0002贴图 · R5燃料棒母型确认</h2>'
        '<p>负责人已指定青白细棒为母图，普通棒原样恢复；15燃料族三状态补齐单／4／8／16连，连同不合格单棒共181张原生64×64透明PNG。'
        '39个单件模型保留独立材质；0003注册的135个多联模型已补对应layer0，66张认可项与神之键R6候选保留。'
        '本轮未打包、安装或运行游戏，不增加37域完成分。</p><p>'
        '<a href="../../deliveries/0002贴图材质_燃料棒_R5_20261114/index.html">查看181张燃料材质</a> · '
        '<a href="../textures-fuel-0002-r5-20261114/completion.json">R5回执</a></p></section>')
    html = re.sub(r'<section class="notice" id="item-texture-0002-fuel-r5">.*?</section>', lambda m: notice, html, flags=re.S)
    (AUDIT / 'index.html').write_text(html, encoding='utf-8')
    return {'single': 46, 'bundles': 135, 'models': len(models), 'archive': str(archive),
        'development_percent': summary['development_metric']['overall_percent'],
        'acceptance_percent': summary['overall_percent'], 'remaining_process_items': review['paused_fuel_ids']}


if __name__ == '__main__':
    print(json.dumps(record(), ensure_ascii=False))
