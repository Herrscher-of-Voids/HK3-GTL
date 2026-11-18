"""修订183交付核验与独立暂存；不部署、不操作游戏、不修改存档。

变更记录#1：2026-10-30 00:38:30：新增构建成功、JAR资源、完整稀疏布局和旧包未变核验。
输入为本轮clean check build；输出独立发布包/收据和HTML状态，不能将离线检查记作成型。
"""
import gzip
import hashlib
import json
import shutil
import struct
import sys
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from deploy_industrial_build import target_process_guard

DELIVERY = ROOT / 'deliveries/W01_永恒礼堂_干燥建材与入口主控修订_V2_20261030'
LOGS = ROOT / 'logs/w01-dry-layout-20261030'
GAME = Path('C:/Users/OWNER/AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版/minecraft')


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def main():
    # 根据BOM识别重定向编码；旧编译器中文编码不影响ASCII成功行和退出码。
    raw_log = (LOGS / 'build.log').read_bytes()
    log = raw_log.decode('utf-16' if raw_log.startswith((b'\xff\xfe', b'\xfe\xff')) else 'utf-8', errors='replace')
    assert 'BUILD SUCCESSFUL' in log and '89 actionable tasks: 89 executed' in log
    source = ROOT / 'build/libs/hk3gtl-0.5.0.jar'
    resource = ROOT / 'src/main/resources/data/hk3gtl/structures/w01_hall.bin.gz'
    with zipfile.ZipFile(source) as jar:
        assert jar.testzip() is None
        assert json.loads(jar.read('assets/hk3gtl/changelog.json'))['entries'][0]['revision'] == 183
        assert jar.read('data/hk3gtl/structures/w01_hall.bin.gz') == resource.read_bytes()
        for suffix in ['common/multiblock/build/Hk3W01BuildBudget', 'common/multiblock/build/Hk3W01BuildOrder',
                       'common/multiblock/build/Hk3W01TerminalBuilder', 'client/preview/Hk3W01PreviewWorld']:
            assert 'com/sirin/hk3gtl/' + suffix + '.class' in jar.namelist()
        assert '1,932,713' in json.loads(jar.read('assets/hk3gtl/lang/zh_cn.json'))['hk3gtl.w01.count']
    header = struct.unpack('>9iH', gzip.decompress(resource.read_bytes())[:38])
    assert header == (0x57303141, 1, 680, 383, 767, 231, 29, 383, 1932713, 276)
    target = GAME / 'mods/HK3GTL-内测5.jar'
    previous = sha(target)
    assert previous == '913369119e2c7df979274f25c199b449d9daa901157e0aba8ab23fea36cd6ba2'
    assert sha(LOGS / 'original-w01_hall.bin.gz') == 'c43f907ada1f8ad7ec288c1ea477199c54dd38a6590833bed358d2f59fbc506e'
    try:
        process = {'guard': target_process_guard(), 'status': '未运行目标实例，仍遵循负责人交还控制的决定暂存'}
    except RuntimeError as error:
        process = {'status': '目标运行或身份未获安全确认，未尝试替换', 'reason': str(error)}
    release = ROOT / 'releases/W01_干燥修订_r183_20261030'
    release.mkdir(parents=True, exist_ok=True)
    packaged = release / 'HK3GTL-内测5.jar'
    shutil.copy2(source, packaged)
    assert sha(packaged) == sha(source) and sha(target) == previous
    now = datetime.now(timezone(timedelta(hours=8))).isoformat()
    report = {'revision': 183, 'created_at': now, 'build': 'clean check build', 'result': '成功',
        'tasks_executed': 89, 'build_elapsed': '7m58s', 'staged_jar': str(packaged),
        'staged_sha256': sha(packaged), 'resource_sha256': sha(resource), 'target_jar': str(target),
        'target_sha256': previous, 'target_unchanged': True, 'deployed': False, 'game_tested': False,
        'speed_measured': False, 'controller_formed_verified': False, 'process': process,
        'checks': ['1932713实体/276状态全量布局', '粉末、含水、指定植物、黄圈样件零残留',
                   '1995叶块保留', '旧主控还原及新入口坐标', '全实体预览索引', '阶段排序和自适应预算',
                   '真实模型HTML离线预览与主控特写', 'JAR完整性与资源逐字节一致']}
    for path in [LOGS / 'release-verification.json', DELIVERY / 'release-verification.json', release / 'verification.json']:
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    html = (DELIVERY / 'index.html').read_text(encoding='utf-8')
    html = html.replace('<span class="badge pending" id="build-status">本轮构建待核验</span>',
        '<span class="badge ok" id="build-status">r183 构建通过 · 89/89</span>')
    html = html.replace('<li id="build-result"><span class="pending">构建状态：</span>本轮修订 r183 构建结果待补，先前 r182 的构建成功不代表本轮已通过。</li>',
        '<li id="build-result"><span class="ok">构建通过：</span>r183 clean check build，89/89任务全部执行成功（7分58秒）。<a href="release-verification.json">包与资源核验</a> · <a href="../../releases/W01_干燥修订_r183_20261030/HK3GTL-内测5.jar">已暂存新包</a>。当前实例旧包未变；换包需退出游戏，旧建筑不会自动改写。</li>')
    (DELIVERY / 'index.html').write_text(html, encoding='utf-8')
    audit = ROOT / 'doc/崩坏三-GTL/00_项目总览/模组全面系统性分析报告.html'
    original = audit.read_text(encoding='utf-8')
    if 'id="w01-dry-r183"' not in original:
        addition = ('<section id="w01-dry-r183"><h2>修订183 · W01干燥建材、入口主控及终端调度</h2>'
            '<p>'+now+'：已将7690格白色混凝土粉末改为混凝土，1282格含水状态清空，清除1040格指定植物和14格样件；1995格树叶保留。'
            '主控改至局部[231,29,383]朝西。实体1932713格，完整GT成型和JEI预览保留。</p>'
            '<p>终端改为单遍放置及2–12ms预算；clean check build 89/89任务通过。仅暂存新包，未部署、未操作当前游戏或存档，未实测提速或成型，生存/AE取料仍未接入。</p>'
            '<p><a href="../../../deliveries/W01_永恒礼堂_干燥建材与入口主控修订_V2_20261030/index.html">本轮HTML与真实材质预览</a> · '
            '<a href="../../../logs/w01-dry-layout-20261030/release-verification.json">构建与资源核验</a></p>'
            '<small>变更记录#183：追加修复状态与边界，历史评分和批准范围不改。</small></section>')
        audit.write_text(original.replace('</body>', addition+'</body>'), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    main()
