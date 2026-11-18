from datetime import datetime
from hashlib import sha256
from pathlib import Path
from zipfile import ZipFile
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'logs/world-farview-surface-r264-20261112'
AUDIT = ROOT / 'logs/beta5-completion-audit-20261030'
BASE = ROOT / 'logs/campus-ring-city-20261112/HK3GTL-r258-campus-ring-city-r263.jar'
BUILT = ROOT / 'build/libs/hk3gtl-0.5.0.jar'
MIXIN = 'com/sirin/hk3gtl/mixin/Hk3WorldFarChunkMapAccess'


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8')


def main():
    OUT.mkdir(exist_ok=True)
    now = datetime.now().astimezone()
    history = OUT / ('audit-before-' + now.strftime('%Y%m%d-%H%M%S'))
    history.mkdir()
    for name in ['index.html', 'current-summary.json']:
        shutil.copy2(AUDIT / name, history / name)
    prefixes = tuple('com/sirin/hk3gtl/' + name for name in [
        'client/farview/Hk3FarMaterials', 'client/farview/Hk3FarTileMesh',
        'client/farview/Hk3FarViewRenderer', 'client/farview/Hk3WorldFarTerrain',
        'common/farview/Hk3WorldFarSurface', 'common/farview/Hk3FarViewSync',
        'common/network/Hk3Network']) + (MIXIN,)
    shaders = {'assets/hk3gtl/shaders/core/farview.' + suffix for suffix in ['vsh', 'fsh', 'json']}
    candidate = OUT / 'HK3GTL-r263-farview-surface-r264.jar'
    with ZipFile(BASE) as previous, ZipFile(BUILT) as current:
        replacements = {name: current.read(name) for name in current.namelist()
                        if name.endswith('.class') and name.startswith(prefixes) or name in shaders}
        config = json.loads(previous.read('hk3gtl.mixins.json'))
        if 'Hk3WorldFarChunkMapAccess' not in config['mixins']:
            config['mixins'].append('Hk3WorldFarChunkMapAccess')
        replacements['hk3gtl.mixins.json'] = json.dumps(config, ensure_ascii=False, indent=2).encode('utf8')
        refmap = json.loads(previous.read('hk3gtl-refmap.json'))
        added = json.loads(current.read('hk3gtl-refmap.json'))
        refmap['mappings'][MIXIN] = added['mappings'][MIXIN]
        for context, mappings in added['data'].items():
            if MIXIN in mappings:
                refmap['data'].setdefault(context, {})[MIXIN] = mappings[MIXIN]
        replacements['hk3gtl-refmap.json'] = json.dumps(refmap, ensure_ascii=False, indent=2).encode('utf8')
        before = {entry.filename: previous.read(entry.filename) for entry in previous.infolist()}
        with ZipFile(candidate, 'w') as result:
            for entry in previous.infolist():
                result.writestr(entry, replacements.get(entry.filename, before[entry.filename]))
            for name in sorted(replacements.keys() - before.keys()):
                result.writestr(current.getinfo(name), replacements[name])
    with ZipFile(candidate) as result:
        after = {name: result.read(name) for name in result.namelist()}
    changed = sorted(name for name in before.keys() & after.keys() if before[name] != after[name])
    build_log = ROOT / 'logs/farview-surface-repair-20261112-build.log'
    shutil.copy2(build_log, OUT / 'build.log')
    screenshot = Path('C:/Users/OWNER/AppData/Local/Temp/codex-clipboard-3797b9c9-3526-4a69-aba9-c2806a89b441.png')
    shutil.copy2(screenshot, OUT / 'user-missing-terrain.png')
    receipt = dict(
        updated_at=now.isoformat(), status='离线修复候选；未安装，等待负责人客户端验收',
        candidate=candidate.relative_to(ROOT).as_posix(), base=BASE.relative_to(ROOT).as_posix(),
        sha256=sha256(candidate.read_bytes()).hexdigest(), bytes=candidate.stat().st_size,
        changed_entries=changed, added_entries=sorted(after.keys() - before.keys()),
        removed_entries=sorted(before.keys() - after.keys()), protocol_version=36,
        changes=['移除hasChunk交接依据，按实际编译状态与统一投影深度交接',
                 '真实模型不可用或超额时使用有界可见LOD，不再空模型消失',
                 '保留每个已知区块最低地表预算，再自适应简化细节与侧壁',
                 '统一承载地表采样，过滤树叶和细装饰，跨LOD边界补裙边',
                 '通过原版异步IO读取已生成地形，不强制加载、生成或模拟区块',
                 '服务端最多2并发读取、4区块发送每tick，维度与会话隔离'],
        limitations=['未生成区块没有真实数据，不凭空补造地形',
                     '高度面是有界LOD，不复制洞穴、多层建筑内部或所有动态方块实体',
                     '远距水面是表面颜色替代，玻璃与精确流体保留透明',
                     '低内存/FCL、增强版当前客户端、连续移动和透明交接仍由负责人验证'],
        build=next(line.strip() for line in build_log.read_text('utf8').splitlines() if 'BUILD SUCCESSFUL' in line),
        installed=False, game_desktop_instance_operations=False, client_visual_verified=False,
        client_performance_verified=False, score_delta=0)
    save(OUT / 'completion.json', receipt)
    summary = json.loads((history / 'current-summary.json').read_text('utf8'))
    system = next(item for item in summary['systems'] if item['id'] == 'multiblocks')
    system['world_farview_surface_fix'] = receipt
    system['updated_at'] = now.isoformat()
    summary['current_work'].update(system='通用超远景修复', state=receipt['status'],
        scope='仓库代码与离线构建；不操作游戏、桌面、活动实例或存档。',
        next_turn='负责人反馈真实画面与性能后继续修复；不将离线构建转记实机通过。',
        world_farview_surface_fix=receipt)
    summary['world_farview_surface_receipt'] = (OUT / 'completion.json').relative_to(ROOT).as_posix()
    summary['report_updated_at'] = summary['updated_at'] = now.isoformat()
    summary['systems'].sort(key=lambda item: item['percent'])
    save(AUDIT / 'current-summary.json', summary)
    page = (history / 'index.html').read_text('utf8')
    notice = ('<section class="notice" id="world-farview-r264"><h2>通用超远景 R264 离线修复候选</h2>'
              '<p>修复地表缺面、预算整批省略、材质空模型和近远景交接；补充已生成地形的有界异步只读数据。'
              '未安装、未操作客户端，真实画面、透明排序及性能待负责人验收。37域、原分母及研发／验收分数保持。</p>'
              '<p><a href="../world-farview-surface-r264-20261112/completion.json">构建与修复回执</a></p></section>')
    page = page.replace('<body><main>', '<body><main>' + notice, 1)
    sections = re.findall(r'<details id="system-[^"]+".*?</details>', page, re.S)
    by_id = {re.search(r'id="system-([^"]+)"', section).group(1): section for section in sections}
    if sections:
        ordered = ''.join(by_id[item['id']] for item in summary['systems'])
        page = page.replace(''.join(sections), ordered, 1)
    page = re.sub(r'(<script type="application/json" id="audit-data">).*?(</script>)',
                  lambda match: match[1] + json.dumps(summary, ensure_ascii=False, indent=2) + match[2], page, count=1, flags=re.S)
    (AUDIT / 'index.html').write_text(page, 'utf8')
    print(json.dumps({key: receipt[key] for key in ['candidate', 'sha256', 'build', 'installed']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
