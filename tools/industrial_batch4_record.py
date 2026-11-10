"""批次4文档与构建证据 / Batch 4 documentation and build evidence.
变更记录 #1：2026-09-22 15:24:00，新增可追溯文件目录、归档校验与验收结果。
Run once to record changes; --verified appends evidence only after successful build.
无游戏存档操作，HTML链接指向真实项目文件。No game-save writes; HTML links target project files.
"""
from pathlib import Path
from datetime import datetime
import hashlib
import html
import json
import os
import sys
import zipfile
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'doc/HK3GTL-内测5/09_测试发布/研究执行与专用贴图_批次4.html'
PROGRESS = ROOT / 'doc/HK3GTL-内测5/09_测试发布/代码落实进度与旧实现归档.html'
ANALYSIS = ROOT / 'doc/崩坏三-GTL/00_项目总览/模组全面系统性分析报告.html'
STAMP = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
FILES = {
    'src/main/java/com/sirin/hk3gtl/common/research/Hk3ResearchMath.java': '新增：S01免疫、注视压力、材料增量与速度公式。',
    'src/main/java/com/sirin/hk3gtl/common/research/Hk3ResearchWorkQueue.java': '新增：付费任务、唯一进度、五阶槽位、按有效tick推进与严格NBT恢复。',
    'src/main/java/com/sirin/hk3gtl/common/research/Hk3ResearchData.java': '修改：任务与知识同档保存，提供可信结算服务入口。',
    'src/test/java/com/sirin/hk3gtl/test/research/ResearchExecutionTest.java': '新增：付款、并行、暂停、重启、费用快照、重复调用与公式回归。',
    'src/test/java/com/sirin/hk3gtl/test/research/ResearchCatalogTest.java': '修改：保留旧Accounts精确校验，同时验证新增Jobs字段。',
    'build.gradle': '追加第4次备注和runResearchExecutionTest检查任务。',
    'src/main/resources/assets/hk3gtl/textures/item/imitation_reason_core.png': '新增：Python原创16×16 RGBA像素贴图；蓝白核心与金色机械约束环。',
    'src/main/resources/assets/hk3gtl/models/item/imitation_reason_core.json': '替换紫水晶纹理引用为本模组专用贴图，保留历史备注。',
    'src/main/resources/assets/hk3gtl/changelog.json': '追加revision42。',
    'tools/generate_reason_core_texture.py': '新增：确定性生成专用PNG，不读取第三方图片。',
    'tools/industrial_batch4_record.py': '新增：本批记录与构建证据脚本。',
}


def page(title, body):
    """生成UTF-8可点击HTML记录；仅格式化文档。 / Render navigable UTF-8 HTML, documentation only."""
    return '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>'+title+'</title><style>body{max-width:1100px;margin:auto;padding:28px;background:#101526;color:#edf2ff;font:16px/1.8 system-ui}a{color:#9cdedc}td,th{border:1px solid #506079;padding:8px}table{border-collapse:collapse}img{image-rendering:pixelated}</style><body><h1>'+title+'</h1><p>'+STAMP+' Asia/Hong_Kong</p>'+body+'</body></html>'


def append(path, section):
    """在正文末追加历史，不重写旧结论。 / Append evidence without overwriting historical conclusions."""
    text = path.read_text(encoding='utf-8')
    assert '</body>' in text
    path.write_text(text.replace('</body>', section+'</body>'), encoding='utf-8')


def record():
    """首次记录修改范围、实现边界及原件校验。 / Record scope, implementation limits and original-file hashes once."""
    changes = [
        '按负责人要求，以Python生成专用16×16透明像素贴图，替换理之核心的紫水晶外观；保留标准item/generated模型作为图片载体。',
        '新增世界级研究执行队列，开题扣费接口、1/2/4/8/16槽、同课题唯一任务、按有效tick推进及费用快照。',
        '任务与完成知识同档保存；离线、失去成型和断电暂停，完成拒绝时保留满进度且不再次扣电。',
        '接入已确认研究公式：S01注视免疫、材料开题锁定、稳定锚与各一次加速；无旧随机失败。',
        '保留旧矩阵代码及修改前原件，新增执行回归；旧存档测试升级但仍精确检查知识条目保留。',
        '边界：只有服务端执行内核，真实研究所/界面/仓库扣费/研究点生产/团队/取消退款适配及核心制造仍未接通，不能据此宣称生存流程可玩。',
    ]
    p = ROOT / 'src/main/resources/assets/hk3gtl/changelog.json'
    data = json.loads(p.read_text(encoding='utf-8'))
    assert not any(e.get('revision') == 42 for e in data['entries'])
    data['entries'].insert(0, dict(version='0.4.0-beta.1', revision=42, codename='内测5开发批次4（未发布）',
        date=STAMP[:10], time=STAMP[11:], summary='理之核心专用Python贴图与研究执行内核。',
        reason='负责人要求取消临时外观并继续代码；落实研究机制v2及已确认公式。', changes=changes))
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    rows = []
    for path, desc in FILES.items():
        assert (ROOT / path).is_file(), path
        link = os.path.relpath(ROOT / path, REPORT.parent).replace('\\', '/')
        rows.append('<tr><td><a href="'+html.escape(link)+'">'+html.escape(path)+'</a></td><td>'+desc+'</td></tr>')
    texture = os.path.relpath(ROOT / 'src/main/resources/assets/hk3gtl/textures/item/imitation_reason_core.png', REPORT.parent).replace('\\', '/')
    body = '<h2>负责人要求与实施</h2><ul>'+''.join('<li>'+c+'</li>' for c in changes)+'</ul>'
    body += '<h2>专用贴图</h2><img width="192" height="192" src="'+texture+'" alt="理之核心专用像素贴图"><p>原生16×16，透明底，Python/Pillow确定性绘制，无第三方图片或临时借用素材。PNG说明与可复现来源保存在生成脚本及本报告。</p>'
    body += '<h2>修改文件</h2><table><tr><th>路径（点击查看）</th><th>变化</th></tr>'+''.join(rows)+'</table>'
    body += '<h2>验收与风险</h2><p>研究执行与既有研究专项测试通过；完整构建待补记。API仅允许可信服务端适配器调用，尚未暴露给玩家。扣费回调要求原子全有或全无、禁止重入；独立仓库文件与SavedData之间尚无断电事务保证。未知课题任务保留费用供恢复，不能靠未知ID解锁。</p>'
    body += '<h2>来源、未决与后续</h2><p>研究机制v2、研究计算与注视度公式草案_v1、01:50研究确认及02:13授权收口记录。无新外部代码或素材复制。待办：真实仓库与点数账户、实验凭据、机器与GUI、团队继承、取消退款及完整生存验收。多方块外观按负责人要求后置。禁止以单元测试冒充实机验收，不恢复旧赠物作为新研究捷径。</p>'
    body += '<p>变更记录 #1：'+STAMP+'，内测5批次4/revision42。Java文件均有编号、时间及中英文说明，旧记录保留。</p>'
    REPORT.write_text(page('研究执行与专用贴图 · 批次4', body), encoding='utf-8')
    record_path = ROOT / 'doc/HK3GTL-内测5/讨论记录' / (datetime.now().strftime('%Y-%m-%d_%H-%M')+'_专用物品贴图与研究执行代码.html')
    record_path.write_text(page('专用物品贴图与研究执行代码', '<p>负责人明确要求新增物品使用Python生成专用图片，不接受临时物品模型，并授权继续代码。本记录保留要求与执行范围，不重新开启已授权事项的审批。</p>'+body.split('<h2>修改文件</h2>')[0]+'<p>完整文件清单及验收见09_测试发布/研究执行与专用贴图_批次4.html。</p>'), encoding='utf-8')
    archive = ROOT / 'archive/beta5-batch4-before'
    items = []
    for file in sorted(archive.iterdir()):
        if file.suffix in ('.zip', '.java'):
            items.append('<li>'+file.name+' SHA256 '+hashlib.sha256(file.read_bytes()).hexdigest()+'</li>')
    (archive / 'index.html').write_text(page('批次4修改前归档', '<p>ZIP使用项目相对路径保存修改前原件；ResearchCatalogTest.java单独保存旧测试。PNG为新贴图放大预览，不是旧资源备份。</p><ul>'+''.join(items)+'</ul>'), encoding='utf-8')
    for path in (PROGRESS, ANALYSIS):
        link = os.path.relpath(REPORT, path.parent).replace('\\', '/')
        append(path, '<section><h2>批次4：专用贴图与研究执行内核</h2><p>'+STAMP+'：修复理之核心借用临时外观，增加付费任务持久化、并行与暂停逻辑；执行内核专项测试通过。仍未接通实机和支付仓库，不是生存完成版。</p><a href="'+link+'">完整修改文件、来源与验收记录</a><p>变更记录：追加批次4/revision42，保留旧内容。</p></section>')
    print('Recorded batch4 revision42 and clickable file inventory.')


def verify():
    """核对真实日志与产物后补记，不用预期结果冒充成功。 / Verify real build output and artifact before recording success."""
    # Windows PowerShell重定向可能为UTF-16；按BOM解码，不能误判成功日志。
    # PowerShell redirection may emit UTF-16; honor the BOM before checking results.
    raw = (ROOT / 'build-beta5-batch4.log').read_bytes()
    log = raw.decode('utf-16' if raw.startswith((b'\xff\xfe', b'\xfe\xff')) else 'utf-8', errors='replace')
    assert 'BUILD SUCCESSFUL' in log
    for result in ['Research execution:', 'Beta5 research:', 'First contact:', 'Quest migration:']:
        assert result in log, result
    jars = [p for p in (ROOT / 'build/libs').glob('*.jar') if 'sources' not in p.name and 'dev' not in p.name]
    assert jars
    for jar in jars:
        with zipfile.ZipFile(jar) as z:
            assert json.loads(z.read('assets/hk3gtl/changelog.json'))['entries'][0]['revision'] == 42
            model = json.loads(z.read('assets/hk3gtl/models/item/imitation_reason_core.json'))
            assert model['textures']['layer0'] == 'hk3gtl:item/imitation_reason_core'
            assert z.read('assets/hk3gtl/textures/item/imitation_reason_core.png') == (ROOT / 'src/main/resources/assets/hk3gtl/textures/item/imitation_reason_core.png').read_bytes()
            for name in ['Hk3ResearchMath', 'Hk3ResearchWorkQueue', 'Hk3ResearchData']:
                assert 'com/sirin/hk3gtl/common/research/'+name+'.class' in z.namelist()
            assert not any(n.startswith('archive/') for n in z.namelist())
    image = Image.open(ROOT / 'src/main/resources/assets/hk3gtl/textures/item/imitation_reason_core.png')
    assert image.mode == 'RGBA' and image.size == (16, 16)
    section = '<section><h2>批次4完整构建补记</h2><p>'+STAMP+'：clean build --offline成功，研究执行、新版研究、首信、注视度和任务迁移测试通过。已核对JAR内专用PNG、模型引用、研究类及revision42，不含根archive。85项既有弃用警告仍在。未启动游戏验收，未安装到Prism；版本仍为开发用0.4.0-beta.1。</p></section>'
    for path in (REPORT, PROGRESS, ANALYSIS): append(path, section)
    print('Build, texture and artifact evidence verified and recorded.')


if __name__ == '__main__':
    verify() if '--verified' in sys.argv else record()

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
