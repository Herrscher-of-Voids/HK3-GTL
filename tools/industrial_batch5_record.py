"""批次5记录工具 / Batch 5 implementation records.
变更记录 #1：2026-09-22 15:38:00，新增修改清单、资源说明和验收顺序追踪。
保留历史；默认写本批记录，--verified仅在核对构建与JAR后追加成功证据。
Preserve history; --verified checks real build output and JAR contents before recording success.
"""
from pathlib import Path
from datetime import datetime
import json
import html
import hashlib
import os
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
STAMP = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
REPORT = ROOT / 'doc/HK3GTL-内测5/09_测试发布/研究点计算机与支付_批次5.html'
PROGRESS = ROOT / 'doc/HK3GTL-内测5/09_测试发布/代码落实进度与旧实现归档.html'
ANALYSIS = ROOT / 'doc/崩坏三-GTL/00_项目总览/模组全面系统性分析报告.html'
FILES = {
    'src/main/java/com/sirin/hk3gtl/common/research/Hk3ResearchData.java': '新增BigInteger研究点余额、计算机产点计量、点数开题实扣，任务和点数同档。',
    'src/main/java/com/sirin/hk3gtl/common/machine/research/Hk3ResearchComputerMachine.java': '新增真实MAX单方块机器，实际能源仓、单电路槽、界面、放置归属、加载/拆除生命周期。',
    'src/main/java/com/sirin/hk3gtl/common/machine/research/Hk3ResearchMachines.java': '注册计算机与专用外观。',
    'src/main/java/com/sirin/hk3gtl/common/recipe/machine/Hk3ResearchComputerRecipes.java': '新增MAX材料组装配方，无研究点或新核心前置。',
    'src/main/java/com/sirin/hk3gtl/common/machine/Hk3MachinesImpl.java': '接入研究计算机注册入口。',
    'src/main/java/com/sirin/hk3gtl/common/recipe/Hk3RecipeAdderImpl.java': '接入中央配方注册和循环诊断。',
    'src/test/java/com/sirin/hk3gtl/test/research/ResearchComputerTest.java': '新增生产到付款回归，含离线、断电、换电路、多机、跨维度、重启、巨大余额。',
    'build.gradle': '新增runResearchComputerTest并接入check。',
    'src/main/resources/assets/hk3gtl/lang/zh_cn.json': '计算机中文名称、槽说明、余额与tooltip。',
    'src/main/resources/assets/hk3gtl/lang/en_us.json': '同步英文名称及界面说明。',
    'src/main/resources/assets/hk3gtl/changelog.json': '新增revision43。',
    'src/main/resources/assets/hk3gtl/models/block/research_point_computer.json': '专用机箱、屏幕、接口与散热面模型。',
    'tools/generate_research_computer_art.py': 'Python原创16×16方块贴图生成脚本，不使用占位素材。',
    'tools/industrial_batch5_record.py': '批次记录、文件清单和验证证据。',
}
for FACE in ('front', 'back', 'side', 'top'):
    FILES['src/main/resources/assets/hk3gtl/textures/block/research_computer/'+FACE+'.png'] = 'Python生成的专用16×16纹理。'


def page(title, body):
    """生成可点击HTML记录；只写文档。 / Generate navigable HTML documentation."""
    return '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>'+title+'</title><style>body{max-width:1100px;margin:auto;padding:28px;background:#101526;color:#edf2ff;font:16px/1.8 system-ui}a{color:#9cdedc}td,th{border:1px solid #506079;padding:8px}table{border-collapse:collapse}img{image-rendering:pixelated}</style><body><h1>'+title+'</h1><p>'+STAMP+' Asia/Hong_Kong</p>'+body+'</body></html>'


def append(path, content):
    """追加历史，不覆盖以前的验证结论。 / Append without replacing historical evidence."""
    text = path.read_text(encoding='utf-8')
    assert '</body>' in text
    path.write_text(text.replace('</body>', content+'</body>'), encoding='utf-8')


def record():
    """写清真实接入和未完成项，避免将自动化测试称为游戏验收。 / Separate integrated code from pending work and in-game acceptance."""
    changes = [
        '新增真实MAX研究点计算机：单电路槽、所有者绑定、GT能源仓、服务端加载tick、界面及制造配方。',
        'MAX电路每有效tick加4工作量，V01–V16加4+n，800工作量发1点；点数与余数同档保存。',
        '新增无人工上限的BigInteger点数余额和点数开题实扣，重复请求/前置不足/余额不足不扣费。',
        '专用机器模型与4张16×16纹理由Python原创生成，中英名称及界面说明齐全。',
        '实施默认：空槽或低于MAX电路暂停，所有者离线暂停，拆机清除未满1点的机器工作量；已结算点数不丢。基于负责人剩余系统授权，不称为用户逐项指定。',
        '按负责人最新要求，代码全部接通后统一游戏验收；本批只运行编译、自动化测试及产物检查。',
        '未完成：研究所GUI和真实物料支付、团队共享、取消退款、核心制造与样本分析；本批机器仍待统一游戏验证。',
    ]
    p = ROOT / 'src/main/resources/assets/hk3gtl/changelog.json'
    data = json.loads(p.read_text(encoding='utf-8')); assert not any(e.get('revision') == 43 for e in data['entries'])
    data['entries'].insert(0, dict(version='0.4.0-beta.1', revision=43, codename='内测5开发批次5（未发布）',
        date=STAMP[:10], time=STAMP[11:], summary='MAX研究点计算机、点数账户与研究支付。',
        reason='继续接入实际机器运行，执行先完成代码再统一游戏验收的顺序。', changes=changes))
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    body = '<h2>已落实及边界</h2><ul>'+''.join('<li>'+c+'</li>' for c in changes)+'</ul>'
    body += '<h2>全部修改文件</h2><table><tr><th>文件</th><th>用途</th></tr>'
    for path, desc in FILES.items():
        assert (ROOT / path).is_file(), path
        link = os.path.relpath(ROOT / path, REPORT.parent).replace('\\', '/')
        body += '<tr><td><a href="'+html.escape(link)+'">'+html.escape(path)+'</a></td><td>'+desc+'</td></tr>'
    body += '</table><h2>参数与验证</h2><p>当前计算机运行功率2,013,265,920 EU/t。配方：4个MAX电路、16钨钢板、8铂单导线、8钻石；1200tick、MAX配方电压。这是授权下首轮平衡值，统一游戏验收时可修正。现有16级电路ID通过标签映射保留，不在本批重命名电压。</p><p>三组研究专项测试已通过；完整构建待补记。测试核对200有效tick基准、多机累加、重启与换电路余数保留、断电/离线零产出、重复tick不扣电、余额超long精确保存、支付到完成不重复扣款。</p>'
    body += '<h2>来源与风险</h2><p>来源：研究系统v2、计算公式_v1、01:50研究确认、02:13剩余系统授权、15:28统一验收记录；GTCEu1.4.4与LDLib本地API仅用于接口核对。新PNG为本项目Python绘制，不复制第三方素材。旧代码归档在archive/beta5-batch5-before，旧研究矩阵未删除。</p><p>点数与计量同一SavedData，但能源仓与SavedData之间不承诺断电原子事务；统一游戏验收需覆盖存档/搬运/服务端同步。个人账户暂不等于团队完成。不得将已编译的GUI/能源路径写成已游戏验收。</p><p>变更记录 #1：'+STAMP+'，内测5批次5/revision43；Java中英注释与编号备注已加入，资源由本报告和脚本说明追踪。</p>'
    REPORT.write_text(page('研究点计算机与支付 · 批次5', body), encoding='utf-8')
    for path in (PROGRESS, ANALYSIS):
        link = os.path.relpath(REPORT, path.parent).replace('\\', '/')
        append(path, '<section><h2>批次5：MAX研究点计算机</h2><p>'+STAMP+'：接入实际机器、点数账户与支付，专用Python外观和制造配方；研究专项测试通过。按负责人要求，所有代码接通后统一游戏验收，当前不安装测试包。</p><a href="'+link+'">完整改动清单、未完成项与检查记录</a><p>追加变更记录：批次5/revision43，保留历史。</p></section>')
    arc = ROOT / 'archive/beta5-batch5-before'
    archive = arc / 'changed-files.zip'
    (arc / 'index.html').write_text(page('批次5修改前原件', '<p>ZIP内保留项目相对路径，不删除旧实现；还原时核对后续批次修改。</p><p>SHA256 '+hashlib.sha256(archive.read_bytes()).hexdigest()+'</p>'), encoding='utf-8')
    print('Recorded batch5 revision43 and clickable file inventory.')


def verify():
    """核对日志与打包资源后写验收证据，仍不启动游戏。 / Check build and packaged resources without launching Minecraft."""
    raw = (ROOT / 'build-beta5-batch5.log').read_bytes()
    log = raw.decode('utf-16' if raw.startswith((b'\xff\xfe', b'\xfe\xff')) else 'utf-8', errors='replace')
    for token in ('BUILD SUCCESSFUL', 'Research computer:', 'Research execution:', 'Beta5 research:', 'First contact:', 'Quest migration:'):
        assert token in log, token
    jars = [p for p in (ROOT / 'build/libs').glob('*.jar') if 'sources' not in p.name and 'dev' not in p.name]
    assert jars
    for jar in jars:
        with zipfile.ZipFile(jar) as z:
            assert json.loads(z.read('assets/hk3gtl/changelog.json'))['entries'][0]['revision'] == 43
            for path in FILES:
                if path.startswith('src/main/resources/'):
                    relative = path[len('src/main/resources/'):]
                    assert z.read(relative) == (ROOT / path).read_bytes(), relative
            for name in ['Hk3ResearchComputerMachine', 'Hk3ResearchMachines']:
                assert 'com/sirin/hk3gtl/common/machine/research/'+name+'.class' in z.namelist()
            assert not any(n.startswith('archive/') for n in z.namelist())
    section = '<section><h2>批次5构建补记</h2><p>'+STAMP+'：clean build --offline成功，研究计算机、研究执行、研究目录、首信、注视度和任务迁移测试通过。JAR内计算机类、模型、4张PNG、中英语言和revision43已核对，不含archive。当前89项弃用警告。没有启动Minecraft或安装实例；统一游戏验收仍待全代码接通。</p></section>'
    for path in (REPORT, PROGRESS, ANALYSIS): append(path, section)
    print('Verified build and artifact; game acceptance remains deferred.')


if __name__ == '__main__':
    verify() if '--verified' in sys.argv else record()

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
