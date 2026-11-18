"""变更#1：2026-09-28，追加用户确认的I44独立起步校准规则，保留原讨论稿。
不修改生产代码；UTF-8脚本避免PowerShell管道的中文编码转换。
"""
from pathlib import Path
from html import escape
import datetime
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
stamp = now.strftime('%Y%m%d-%H%M%S-%f')
plan = ROOT / 'doc/HK3GTL-内测5/09_测试发布/十二天重制计划与交付清单.html'
source = ROOT / 'doc/HK3GTL-内测5/02_工业计划/HK3GTL工业计划树状图_v5.html'
anchor = 'research-s02-20260928-150746-177096'
decision_anchor = 'research-qom-confirmed-' + stamp
answer = 'I44单独完成起步校准；载人传送时才要求I45配对（推荐）'
rules = [
    'QOM的首份证据由I44信标独立运行基础坐标校准取得，真实耗电且成功完成后记账。',
    '该起步校准不要求I45、不要求I24、不要求茧赋予的加强观测；不得把后续I25解析的世界泡坐标反作首次校准输入。',
    '载人传送继续要求I44与I45配对，原有终审维度排除与运输边界不变。',
    '取得异常证据后仍按既定支付/队列规则完成QOM研究，才开放I24；I24真实初观再提供QLE证据，由S02研究后开放S03。',
    '本条覆盖第二阶讨论稿中QOM“记录端待定”和“双机是否必需”的待定状态；不代表已实现，也不替代其他待答问题。',
]
addition = f'<aside id="{decision_anchor}"><h3>已确认：I44独立起步校准</h3><p>记录时间：{now.isoformat()}。用户答复：{escape(answer)}。原消息精确时间未取得，以上为记录时间。</p><ul>'
addition += ''.join('<li>'+escape(x)+'</li>' for x in rules)
addition += '</ul><p>核对依据：工业计划树v5中I44负责定位、观察和锁定，I45负责静止载人传送；加强观测另有茧技术条件。本次仅明确起步实验的双机边界，不擅自决定耗电量、材料、校准时长或异常触发数值。</p></aside>'
before = plan.read_text(encoding='utf-8')
start = before.index('id="' + anchor + '"')
end = before.index('</section>', start)
after = before[:end] + addition + before[end:]
assert after.replace(addition, '', 1) == before
payload = {'time':now.isoformat(),'answer':answer,'status':'用户已确认，游戏未实现','confirmed':rules,
           'supersedes':'第二阶28课题稿中的QOM记录端及双机要求待定项',
           'still_pending':['八项具体工艺合并映射','S01独立工程验证的承载安排及ERM对应机制','具体配方和数值'],
           'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
           'production_changed':False,'compiled':False,'deployed':False,'game_tested':False}
out = ROOT / 'logs/research-migration-20260928' / ('qom-confirmed-' + stamp + '.json')
record = ROOT / 'doc/HK3GTL-内测5/讨论记录' / (now.strftime('%Y-%m-%d_%H-%M-%S-%f') + '_I44独立起步校准裁定.html')
body = '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>I44独立起步校准裁定</title></head><body><h1>I44独立起步校准裁定</h1>' + addition
body += '<h2>原问题</h2><p>QOM首份证据来自基础坐标校准，是否需要I45配合？候选一为I44独立起步、载人传送时配对；候选二为双机空载校准、不要求实际传送玩家。</p>'
body += '<h2>实际执行</h2><p>已将答复写入结构化决定，并追加现有计划页。保留原第二阶讨论稿和历史JSON；本条明确覆盖其中相关待定项。生产代码、研究目录、配方、结构与游戏实例未改，未编译或游戏测试。</p>'
body += '<p>写入前一次PowerShell管道执行因Python收到非UTF-8源码而在解析阶段报错，没有执行文件写入；本次使用UTF-8脚本完成写入并回读。不是终端入口或权限问题。</p>'
body += '<p>仍待答：八项具体工艺合并映射、S01工程验证承载安排。后续继续S03的19个课题，结构外观仍暂停。</p>'
body += f'<p><a href="../09_测试发布/十二天重制计划与交付清单.html#{anchor}">第二阶完整方案与确认补充</a></p><footer>变更#1：追加本轮明确答复；删除无。</footer></body></html>'
with out.open('x',encoding='utf-8') as f:
    json.dump(payload,f,ensure_ascii=False,indent=2)
plan.write_text(after,encoding='utf-8')
with record.open('x',encoding='utf-8') as f:
    f.write(body)
assert plan.read_text(encoding='utf-8') == after
assert record.read_text(encoding='utf-8') == body
assert json.loads(out.read_text(encoding='utf-8'))['answer'] == answer
print(json.dumps({'record':str(record),'decision':str(out),'anchor':decision_anchor,'prior_content_preserved':True,'read_back':True},ensure_ascii=False))
