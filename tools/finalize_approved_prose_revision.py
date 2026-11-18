"""修订93交付记录：追加变更备注与讨论记录，不改写历史修订。"""
from pathlib import Path
from datetime import datetime
import json, re, html
ROOT=Path(__file__).resolve().parents[1]
stamp=datetime.now().astimezone()
now=stamp.strftime('%Y-%m-%d %H:%M:%S')
base=ROOT/'src/main/java/com/sirin/hk3gtl'
notes={
 'Hk3Gtl.java':'新增审核原文对白注册，先注册共同人物与段落，再注册正式终审。',
 'client/bootstrap/Hk3ModWelcomeScreen.java':'更新窗口接入审核正文与反馈QQ，完整换行；确认后记录已读，稍后阅读不记录。未实现系统的宣传不放进当前更新窗口。',
 'client/communication/Hk3LetterScreen.java':'首信、两种回信、观测附件及两种后续来信读取审核原文；新增附件与后续阅读按钮，不误发回信。',
 'client/dialogue/Hk3DialogueScreen.java':'逐句显示；IF分页保留选项索引，满五选只禁用未选分支；ESC暂停，正常读完才发送完成标记；校对显示只读状态。',
 'common/badending/SirinBadEndingManager.java':'攻击阶段对白使用审核FP03，重返后九句收束使用F09。保留攻击阈值、演出时序、世界改名、强制登出及旧世界级结算。',
 'common/command/Hk3DebugCommands.java':'调试重开清除新检查点；正式终审读取本存档玩家IF账本，不使用旧跨存档掩码。',
 'common/communication/Hk3FirstContactService.java':'开放审核附件及后续来信；服务端核验后续来信与真实回信状态一致，阅读不改写合作决定。',
 'common/dialogue/DialogueSessionManager.java':'正式终审保存段落检查点及每人每存档五选；校验选择的当前段落；仅FU01自然结束可结算，暂停及校对不结算。',
 'common/dialogue/definition/Hk3IfArchiveDialogue.java':'免费IF指令共用26条审核原文，每条十句，不扣正式终审五选名额。',
 'common/dialogue/definition/SirinDialogueDefinitions.java':'移除未调用的旧段落构造器；正式入口换为F01及26条IF图，保留原结束处理器。',
 'common/entity/VoidQueenSirinEntity.java':'终审使用本存档玩家IF账本，以活跃会话去重，关闭后允许继续；保留出场及翅膀时序。',
 'common/event/Hk3ModWelcomeHandler.java':'修订93独立已读标识，新增hk3updates重读；确认才持久化已读。',
 'common/network/DialogueCloseC2SPacket.java':'关闭包区分暂停与自然完成，服务端仍核验会话与正式终审末段。',
 'common/network/DialoguePlayerChoiceC2SPacket.java':'选择包加入当前段落ID及长度限制，拒绝过时段落请求。',
 'common/network/Hk3LetterOpenPacket.java':'阅读范围扩展到六份首信相关文档，后续来信仍由服务端核验状态。',
 'common/network/Hk3Network.java':'网络协议升至10；客户端与服务端必须同时使用新包。'
}
for rel,note in notes.items():
 p=base/rel
 s=p.read_text(encoding='utf-8')
 if rel.endswith('/SirinDialogueDefinitions.java') and '    /**\n     * INTRO：' in s:
  start=s.index('    /**\n     * INTRO：')
  s=s[:start]+'}\n'
  s=s.replace('    /** IF 分支最大预留行数；客户端会自动过滤不存在的翻译键。 */\n    private static final int MAX_IF_LINES = 20;\n','')
  s=s.replace('结构: intro segment + 10个IF分支 segment（0~4 内测二主题，5~9 内测三模组包/模组类别隐喻）','结构：审核 F01、26条 IF、暂缓及现实生活收束。')
 if '内测5修订93' not in s:
  n=max([int(x) for x in re.findall(r'变更记录 #(\d+)',s)]+[0])+1
  comment=f'/**\n * 【变更记录 #{n}】{now}（内测5修订93）\n * - 删除：旧正文活动引用被审核原文替代；保留历史资源和存档。\n * - 新增／修改：{note}\n * - 用途：接通审核正文；其他系统触发及归属不据此宣称完成。\n */\n'
  at=s.index('import ')
  s=s[:at]+comment+s[at:]
 p.write_text(s,encoding='utf-8')
newfiles=[base/'common/narrative/Hk3ApprovedProse.java',base/'common/dialogue/definition/Hk3ApprovedDialogues.java',base/'common/command/Hk3ProseCommand.java',ROOT/'src/test/java/com/sirin/hk3gtl/test/dialogue/ApprovedProseTest.java']
for p in newfiles:
 s=p.read_text(encoding='utf-8').replace('2026-09-29 17:00:00',now).replace('2026-09-29 17:45:00',now)
 p.write_text(s,encoding='utf-8')
p=ROOT/'src/main/resources/assets/hk3gtl/changelog.json'
data=json.loads(p.read_text(encoding='utf-8'))
if not any(x.get('revision')==93 for x in data['entries']):
 data['entries'].insert(0,{'version':'0.5.0','revision':93,'codename':'HK3GTL-内测5','date':stamp.strftime('%Y-%m-%d'),'time':stamp.strftime('%H:%M:%S'),'reason':'负责人要求审核正文加入游戏；保留世界改名与强制登出。','changes':['新增：736个审核正文条目及来源清单，含480条访客对白、92条五方贸易与26条逐句IF。','修改：正式终审、现有首信及附件后续、更新窗口、坏结局文本读取审核原文。','新增：管理员hk3text全文及只读预览；hk3if免费26条；hk3updates重读。','修改：终审每玩家每存档五选、段落检查点、暂停不结算、服务端选项校验；网络协议10。','保留：出场回退和翅膀时序、坏结局改名及强退、旧世界级毕业结算。','边界：家园实体、贸易履约、自然二审、右侧通知、个人工程复核尚未实现。','语言：英文环境使用审核中文回退，不冒称英译完成。','检查：资源完整性、IF逐句、分支及只读边界加入check；构建部署结果另记。']})
 p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
manifest=json.loads((ROOT/'logs/approved-prose-20260929/import-manifest.json').read_text(encoding='utf-8'))
record=ROOT/'doc/HK3GTL-内测5/讨论记录'/f'{stamp:%Y-%m-%d_%H%M%S}_已审核正文实装_修订93.html'
body=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>已审核正文实装 · 修订93</title><style>body{{max-width:980px;margin:40px auto;padding:0 24px;background:#131724;color:#e5e7f1;font:17px/1.8 sans-serif}}h1,h2{{color:#d7bdff}}code{{color:#8cddff}}</style><h1>已审核正文实装 · 修订93</h1><p>讨论及记录时间：{now}（Asia/Hong_Kong）</p><h2>负责人本次决定</h2><p>“已经审核过的正文，我们全部塞进游戏里。”承接上一轮：出场恢复旧效果基础少量粒子；翅膀与人物同步；坏结局世界改名与强制登出保留。</p><h2>正文接线</h2><p>736个条目进入资源并注册游戏内逐句对白。数量：{html.escape(str(manifest['counts']))}。</p><ul><li>正式终审F01新开场；26条IF各十句。五选按玩家UUID和存档隔离，重读免费；免费IF命令不动账本。</li><li>六份首信文档：首信、两种回信、附件、两种后续来信；后续按真实回信状态核验。</li><li>更新详情使用审核正文及群758974004、作者QQ3929461640；稍后不记已读。</li><li>坏结局攻击文本用FP03，重返九句收束用F09；改名、强退和演出时序保留。</li></ul><h2>明确边界</h2><p>全文入包、可读不等于全部系统完成。贸易、家园访客、一审及二审等批量正文可在校对目录阅读，尚未接通的自然触发、实体、交易履约不冒充完成。自然二审、右侧通知仍待实现。正式终审和坏结局仍使用旧世界级毕业结算，本次未完成个人工程核验和多人归属重构。</p><p>量子之海首次观测草案缺明确批准依据，未擅自导入。旧语言键保留历史兼容，正式终审不再读取旧开场。</p><h2>游戏内查看</h2><ul><li><code>/hk3text</code>：管理员全文目录，只读不发奖励。</li><li><code>/hk3text finale</code>、<code>/hk3text second_review</code>：完整分支预览。</li><li><code>/hk3if</code>：免费26条IF逐句阅读。</li><li><code>/hk3updates</code>：重读更新说明。</li></ul><h2>验证与交付</h2><p>正文专项检查通过；最终构建、双实例复制记录见 logs/approved-prose-20260929/delivery.json。未经游戏实际运行，不把编译通过写成实机通过。英文环境使用中文回退，英译未完成。</p></html>'''
record.write_text(body,encoding='utf-8')
report={'timestamp':now,'revision':93,'discussion':str(record),'javaFiles':[str(base/p) for p in notes]+[str(p) for p in newfiles],'counts':manifest['counts'],'status':'awaiting_final_build_and_deployment'}
(ROOT/'logs/approved-prose-20260929/revision-record.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'record':str(record),'javaCount':len(report['javaFiles'])},ensure_ascii=True))
