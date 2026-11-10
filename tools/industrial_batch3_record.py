"""Batch 3 documentation/revision record, 2026-09-22. Run once after code tests.
批次3记录工具：追加历史，不覆盖旧讨论；不操作游戏实例。
"""
from pathlib import Path
from datetime import datetime
import json
import html
import hashlib
import zipfile

root = Path(__file__).resolve().parents[1]
now = datetime.now()
stamp = now.strftime('%Y-%m-%d %H:%M:%S')
changes = [
    '旧实现保存在archive/beta5-batch3-before，不删除归档。',
    '新增100项RN课题目录、前置DAG校验和独立世界SavedData；旧赠物标记不能解锁新研究。',
    'ULV–MAX共15种电路重构改为逐级技术与样本分析授权，配方要求不消耗的仿制理之律者核心；重构阵列控制器改绑RN-RCA。',
    '未知研究ID拒绝放行，不再回退到R-AB-001；setupRecipe在燃料与输入扣除前检查研究。',
    '新增核心中英文名称与引用原版紫水晶纹理的临时模型，无第三方素材复制。',
    '边界：尚未接入研究执行、核心制造、样本分析与团队继承；当前开发包不能通关，配方数值仍待平衡。',
]
p = root / 'src/main/resources/assets/hk3gtl/changelog.json'
data = json.loads(p.read_text(encoding='utf-8'))
assert not any(e.get('revision') == 41 for e in data['entries'])
data['entries'].insert(0, dict(version='0.4.0-beta.1', revision=41,
    codename='内测5开发批次3（未发布）', date=now.strftime('%Y-%m-%d'), time=now.strftime('%H:%M:%S'),
    summary='理之核心电路重构门控与新版研究账本基础。',
    reason='落实确认的电路重构后移，不以旧馈赠或未知研究回退绕过新门槛。', changes=changes))
p.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def page(title, body):
    return '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>'+title+'</title><style>body{max-width:1050px;margin:auto;padding:28px;background:#101526;color:#edf2ff;font:16px/1.8 system-ui}a{color:#9cdedc}code{overflow-wrap:anywhere}</style><body><h1>'+title+'</h1><p>'+stamp+' Asia/Hong_Kong</p>'+body+'</body></html>'

body = '<h2>已落实</h2><ul>'+''.join('<li>'+html.escape(x)+'</li>' for x in changes)+'</ul>'
body += '<h2>验证与局限</h2><p>研究专项测试通过：100课题DAG、缺失前置、循环、等级、逐电路分析授权、玩家与世界隔离、NBT往返及损坏字段。完整构建结果待补记。未进行Forge游戏运行验收，Mixin已核对GTCEu 1.4.4源签名并编译。</p><p>研究账本仅接受未来可信机器结算结果，没有玩家绕过研究的解锁命令。尚无生存获取核心与完成RN研究的流水线，所以电路重构目前有意保持锁定。没有多方块外观或Pattern修改，没有运行中实例JAR替换。</p>'
body += '<h2>接续工作</h2><p>依已冻结研究方案接入研究所执行、付款与进度、核心制造及样本分析，再落实团队权限和显示同步；继续迁移旧研究依赖与FTB任务。旧数值和六章任务不视为内测5完成。</p>'
body += '<h2>来源与变更</h2><p>设计来源：研究课题目录与前置树_v1.html、理之核心与电路重构_已确认.html、2026-09-22_14-38_理之核心电路重构解锁迁移.html。目录由tools/research_catalog.py导出；GTCEu仅本地接口核对，临时模型引用Minecraft自带纹理。语言文件各增加item.hk3gtl.imitation_reason_core，旧文本保留。变更记录 #1：'+stamp+'，批次3/revision41。</p>'
report = root / 'doc/HK3GTL-内测5/09_测试发布/理之核心批次3实现与验收.html'
report.write_text(page('理之核心批次3实现与验收', body), encoding='utf-8')
record = root / 'doc/HK3GTL-内测5/讨论记录' / (now.strftime('%Y-%m-%d_%H-%M')+'_理之核心代码执行记录.html')
record.write_text(page('理之核心代码执行记录', '<p>负责人确认14:38设计，随后明确“继续代码阶段”。本记录是实施追踪，不是新增设计裁定。</p>'+body+'<p>禁止恢复旧馈赠绕过核心、增加虚空万藏前置、把未实现流水线写成已完成。未决：最终数值及完整机器运行验收；按现有授权继续落实。</p>'), encoding='utf-8')
arc = root / 'archive/beta5-batch3-before'
rows = []
for f in sorted(arc.iterdir()):
    if f.is_file() and f.suffix in ('.zip', '.java'):
        rows.append('<li>'+f.name+' SHA256: '+hashlib.sha256(f.read_bytes()).hexdigest()+'</li>')
with zipfile.ZipFile(arc / 'changed-files.zip') as z:
    members = z.namelist()
(arc / 'index.html').write_text(page('批次3修改前归档', '<p>ZIP保存本批修改前原件，两个额外Java原件单独保存。复原前按同名文件比对，不覆盖其他批次修改。</p><ul>'+''.join(rows)+'</ul><pre>'+html.escape('\n'.join(members))+'</pre><p>Java位于src/main/java；语言与changelog位于src/main/resources/assets/hk3gtl；build.gradle位于项目根。完整基线另见beta4-baseline-2026-09-22_13-33-45。</p>'), encoding='utf-8')
for path in [root / 'doc/HK3GTL-内测5/09_测试发布/代码落实进度与旧实现归档.html', root / 'doc/崩坏三-GTL/00_项目总览/模组全面系统性分析报告.html']:
    text = path.read_text(encoding='utf-8')
    addition = '<section><h2>内测5批次3：研究账本与理之核心门控</h2><p>'+stamp+'。100课题目录、研究账本、逐级电路分析授权、非消耗核心条件、扣料前门控已落实。修正未知研究ID回退早期节点的放行漏洞。研究专项测试通过；完整构建结果见批次3验收报告。研究执行、核心制造、样本分析、团队继承未完成，当前不是可通关发布包。</p><p>变更记录：追加批次3/revision41，保留历史状态。详见doc/HK3GTL-内测5/09_测试发布/理之核心批次3实现与验收.html。</p></section>'
    assert '</body>' in text
    path.write_text(text.replace('</body>', addition+'</body>'), encoding='utf-8')
print('Recorded batch 3, revision 41, archive and progress reports.')

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
