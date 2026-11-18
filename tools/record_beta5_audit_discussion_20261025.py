# -*- coding: utf-8 -*-
"""本轮讨论摘要与原文档案互链；不重写既有I24批准收据。

【变更记录 #1】2026-10-25（生成时间在HTML中精确记录）
删除：无。新增：审计结论、条件更名边界、I25候选和归档关联。
修改：仅记录当前可核验事实；用户原消息时间来自原始会话记录。
用途：压缩后可恢复决定，摘要不冒充逐字原文；完整转录仍由归档器负责。
"""
from pathlib import Path
import datetime as dt
import html
import json
import os
from urllib.parse import quote

ROOT=Path(__file__).resolve().parents[1]
DOC=ROOT/'doc/HK3GTL-内测5'


def main():
    now=dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))
    report=ROOT/'doc/HK3GTL-内测5/09_测试发布/内测5全库完成度与正式版准备审计_20261025.html'
    i25=ROOT/'deliveries/I25_世界泡坐标解析中心_三轴浑仪与双翼解算厅_V1_20261025/index.html'
    raw=DOC/'完整对话归档/2026-10-25_00-41-45_I24明确批准、I25候选与内测5全库完成度审计_3c17914beb.html'
    out=DOC/'讨论记录'/f'{now:%Y-%m-%d_%H-%M-%S}_I25候选与内测5全库审计及正式1.0条件判断.html'
    def link(path,label):
        return '<a href="'+quote(os.path.relpath(path,out.parent).replace('\\','/'),safe='/.:')+'">'+html.escape(label)+'</a>'
    body='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>I25候选与内测5全库审计及正式1.0条件判断</title><style>body{max-width:1050px;margin:30px auto;padding:0 22px;font:16px/1.9 "Microsoft YaHei",sans-serif;color:#18343f}a{color:#12638a}blockquote{border-left:4px solid #7496a8;padding:14px 20px;background:#eef4f6}code{overflow-wrap:anywhere}</style><h1>I25候选与内测5全库审计及正式1.0条件判断</h1>'''
    body+='<p>实际记录时间：'+now.isoformat(timespec='seconds')+' Asia/Hong_Kong。原用户消息时间：2026-10-25 00:41:45.793+08:00（原始会话记录）；记录为讨论摘要，非逐字归档。</p>'
    body+='''<h2>用户要求与关键原话</h2><blockquote>i24 ok<br>下一台吧<br>我们还有多少台多方块结构要弄，我们看一下最新规划里，我们还有多少台多方块结构的然后检查一下所有代码，看一下我们和最新的设计文档与讨论记录差多少，我想检查一下各个系统的完成度，整个内测五的完成度，如果内测5的完成度直接比较高的话，我们就直接将它改名成为HK3GTL正式版1.0就不用再内测来内测去了</blockquote>
<h2>用户已确认与授权边界</h2><ul><li>I24 V2明确批准，已独立不可变归档；batch-07 I22/I23/I24=3/5，未部署。原I24来源“待审”元数据不改写，批准由外部收据证明。</li><li>继续既有规划下一台I25；本轮交候选并不自动视为用户批准。</li><li>检查当前全部产品代码，对照最新内测5设计及讨论判断完成度。用户对1.0更名提出有条件方向，不是无条件更名授权或验收完成。</li></ul>
<h2>实际实施与核验</h2><ul><li>I25「世界泡坐标解析中心」V1：三轴浑仪与双翼解算厅，QEV/V07；宽×长×高85×97×65，48,222方块。钻石主控[42,4,0]居中，5个工业接口齐平嵌入机体；当前仅解析职责，无锁定/捕获/传送实装。</li><li>599份产品Java、79份测试Java逐份语义审查并核对SHA；3462项资源文件建立身份、1810份JSON语法无失败或重复键。相关设计/讨论条款按领域实际读取，不冒称全部历史文档均逐字重读。</li><li>Gradle check离线通过，77任务（70执行7已最新）；69自定义验证任务吻合。76份测试源被check触达，3旧测试不在check。逻辑/合同/模拟通过不等于生存或多人验收。</li><li>最新数量：69具名形态／66编号。84是每新增阶至少5台的理论下限；保持现映射需88。29形态获外观批准、26正式接入，尚59个待设计/批准名额=40具名+19未命名；尚62未正式。I19-I21已有候选，I22批准不反推它们各自单独批准；不宣称59台全没画。</li><li>当前主线有确定缺口：32项暂定工单关闭、反应堆等生产机器未接、世界泡工业执行/真实结算未闭合、C6/C7工程提供者缺失、正式叙事迁移64项仍等待、终审工程准入WAITING。详见完整报告证据。</li><li>未改产品Java、资源、build.gradle、版本或实例；未升级2.9.2、未启动游戏、未发外部AI请求。本轮没有游戏验收新结论。</li></ul>
<h2>助手判断与待定事项</h2><p>当前不具备直接称正式版1.0的条件，继续在内测5完成即可，不需要为阶段命名再增加内测6。优先闭合工业前段与HDV首建、真实能源/世界泡、奇观与休伯利安工程、叙事/终审，最终按既定后置顺序做指定整包单人/专服多人和性能验收。此顺序为审计建议，不是已实施或用户另行批准的范围变更。</p><p>I25外观待用户评审。19补充名额没有本轮擅自命名或逐台新增。2.9.2兼容待负责人升级后实际验证；最终内存优化仍后置，不以本轮静态审计扩大为目标达标。</p>
<h2>旧口径修正与保留</h2><p>电压制作按已授权提案；注视度遵循个人记录＋在线团队最高有效值，不恢复被纠正的团队原始共享G要求；旧电路生产缺失已被当前52电路/64电子平台实现覆盖。取消的组织实物贸易、后置的社交扩展/FTB任务不强加回必需范围；旧叙事按最新迁移要求处理，不照搬废案。全部历史收据、旧报告、候选与失败证据保留。</p><h2>相关成果与原文</h2>'''
    body+='<p>'+link(i25,'I25 V1评审')+' · '+link(report,'本轮完整审计报告')+' · '+link(raw,'本段完整对话归档')+'</p>'
    body+='<p>'+link(DOC/'讨论记录/2026-10-25_00-44-59_I24V2明确批准归档与I25候选继续.html','I24批准摘要与不可变收据入口')+'</p>'
    body+='<footer>【记录 #1】'+now.strftime('%Y-%m-%d %H:%M:%S')+'：新增本轮完成状态、明确边界、可追溯成果与原文互链；不覆盖旧决定或自动批准I25。</footer></html>'
    assert not out.exists(),out
    out.write_text(body,encoding='utf-8')
    override=ROOT/'tools/conversation_archive/topic_overrides.json'
    entries=json.loads(override.read_text(encoding='utf-8'))
    key='01a16eca-2c40-74f2-8f41-dcdf17f9d856'
    entry=entries[key]
    entry['related_paths']=list(dict.fromkeys(entry.get('related_paths',[])+[out.relative_to(ROOT).as_posix(),report.relative_to(ROOT).as_posix(),i25.relative_to(ROOT).as_posix()]))
    entry['pending']=['I25 V1待用户批准，batch-07仍3/5。','内测5主线与实机发布条件未闭合，暂不更名1.0。','19个补充结构名额尚未逐一命名或作为新机器获批。']
    override.write_text(json.dumps(entries,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(out)


if __name__=='__main__':main()
