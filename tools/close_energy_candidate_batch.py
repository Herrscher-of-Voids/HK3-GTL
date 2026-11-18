# -*- coding: utf-8 -*-
"""汇总能源候选、定量风险与审批边界，更新既有主审计而不改正式资源。
【变更记录 #1】2026-10-19 14:14:17（香港时间，候选文档批次172）
删除：无；新增：定量边界HTML、整批交付讨论记录及接续规则读取凭据。
修改：主审计追加同燃料跨阶倍率风险；用途：保留候选、实现与游戏验收的区别。
"""
from datetime import datetime, timezone, timedelta
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit
import hashlib
import html
import json
import os
import re

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / 'logs/energy-production-r172'
AUDIT = ROOT / 'doc/HK3GTL-内测5/09_测试发布/内测5全库逐份代码文档对照审计_20261017.html'
HK = timezone(timedelta(hours=8))
STYLE = '''body{max-width:1160px;margin:30px auto;padding:0 22px;font:16px/1.85 system-ui,"Microsoft YaHei",sans-serif;color:#163b44;background:#edf4f3}header{padding:24px 30px;background:#173f48;color:white;border-radius:12px}section{padding:20px 26px;background:white;border:1px solid #ccdcde;border-radius:10px;margin:18px 0}h1{font-size:29px}h2{font-size:22px}a{color:#096d7b}table{border-collapse:collapse;width:100%;font-size:14px}th,td{border:1px solid #cbdadd;padding:9px 11px;text-align:left}th{background:#deeced}.scroll{overflow-x:auto}.alert{background:#fff1e5;border-left:5px solid #bd602a;padding:15px}code{overflow-wrap:anywhere}small{color:#526e76}blockquote{border-left:4px solid #298a83;background:#ecf7f5;padding:12px 18px}li{margin:7px 0}footer{font-size:13px;color:#526e76}'''


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def link(origin, target, label):
    relative = os.path.relpath(target, origin.parent).replace('\\', '/')
    return f'<a href="{html.escape(relative, quote=True)}">{html.escape(label)}</a>'


def page(title, stamp, content):
    return f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><style>{STYLE}</style></head><body><header><h1>{title}</h1><p>{stamp} · Asia/Hong_Kong（UTC+08:00）</p></header>{content}</body></html>'


def main():
    now = datetime.now(HK)
    stamp = now.isoformat(timespec='seconds')
    numeric = load(LOG/'能源倍率与载能定量边界.json')
    qa = load(LOG/'交付独立核验.json')
    assert qa['pass'] and not qa['failures']
    locked = [Path(row['path']) for row in numeric['locked_review_artifacts']]
    locked_hashes = {str(path): sha(path) for path in locked}
    numeric_html = LOG/'能源倍率与载能定量边界.html'
    rows = ''.join('<tr>'+''.join(f'<td>{value}</td>' for value in [
        row['role'], row['voltage_symbol'], row['fuel_rods_consumed'],
        f"{int(row['va_long_eu_per_tick']):,}", f"{int(row['contract_eu_per_rod']):,}",
        '普通' if row['role']=='I19' else '同一浓缩燃料棒'])+'</tr>' for row in numeric['calculations'])
    content = f'''<section><h2>同一燃料的预算不能由机器电压重置</h2><div class="alert">当前暂定合同中，相同浓缩燃料棒从I20到I21的每棒承诺产电量增加128倍，再到I22增加512倍，累计65,536倍。这里是源代码和已导出配方的算术核对，未发生真实反应堆发电测试。</div><p>4条旧计划均标记暂定，工时3600tick；I20、I21、I22分别消耗2、4、8根相同物品ID的浓缩棒。每根棒的封装均消耗1000mB同一浓缩基液。现有规则直接取机器档位的VA_LONG作为EU/t，没有逐件燃料潜能或有界效率来说明差额。</p><div class="scroll"><table><thead><tr><th>机器</th><th>档位</th><th>每批棒数</th><th>合同EU/t</th><th>每棒合同EU</th><th>燃料身份</th></tr></thead><tbody>{rows}</tbody></table></div><p>I19使用普通燃料，不能将其与浓缩燃料的数值比例当作同燃料复制证明，也不能据此擅定浓缩倍率。冷却剂mB不是热量单位。</p></section>'''
    direction = numeric['design_direction']
    content += '<section><h2>后续实现使用的预算边界</h2><ol>' + ''.join(f'<li>{html.escape(item)}</li>' for item in [
        direction['fuel_budget']['source'], direction['reactor_envelope']['power'],
        direction['reactor_envelope']['throughput'], direction['reactor_envelope']['ordinary_in_large_reactor'],
        direction['energy_and_heat_ledger']['equation'], direction['energy_and_heat_ledger']['recovery'],
        direction['fuel_budget']['depleted']]) + '</ol><p>这些是防止能源重复结算的实现约束。具体潜能、释放速率、转换效率、热容及全生命周期净收益尚未定量，本记录不代替这些工作。</p></section>'
    content += f'''<section><h2>对60份新候选的影响</h2><p>15种燃料、4座反应堆共60份工况目前只给出工艺与IO候选，尚未写入可执行配方。不能把“1份燃料＋1000mB冷却剂”直接套入旧的额定电压×固定工时公式。普通燃料在高阶兼容反应堆可低于额定功率运行；若要满额功率，必须实际消费相应新燃料并处理热量。</p><p>PTFE/PBI工况仍需冷端硬隔离与温度验收；高电压不使聚合物自动耐热。正式控制器、Pattern、真实仓位、热管理及单人/多人运行仍待完成。能源评分保持2/16。</p><p>{link(numeric_html,LOG/'能源倍率与载能定量边界.json','完整公式、源码SHA与运行配方证据')} · {link(numeric_html,LOG/'燃料工艺与60工况候选_r172.html','15种燃料与60份候选')} · {link(numeric_html,AUDIT,'现有全系统审计')}</p></section><footer>【记录 #1】{stamp}：删除无；新增现行合同倍率核对的可读HTML；未改已审工艺JSON/HTML，未修改正式代码、资源、构建或实例。</footer>'''
    numeric_html.write_text(page('能源倍率与载能定量边界',stamp,content),encoding='utf-8')

    # 实际全文读取已完成后才追加指纹，保留此前读取记录。
    identity_path = LOG/'续接规则读取身份.json'
    old_identity = load(identity_path)
    names = ['rules.md','系统角色设定.md','崩坏三-gtl (hk3gtl) 项目规则.md','hk3gtl java文件变更备注规范.md','当前多方块设计规则.md','巨构提示词.txt']
    identity = {'read_at':stamp,'context_gatherer':old_identity['context_gatherer'],
                'files':[{'path':str(ROOT/'rule'/name),'bytes':(ROOT/'rule'/name).stat().st_size,'sha256':sha(ROOT/'rule'/name)} for name in names],
                'history':[old_identity], '_record':f'【记录 #2】{stamp}：压缩接续后再次实际全文读取，截断的两组已独立补读至末尾。'}
    identity_path.write_text(json.dumps(identity,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

    texture = ROOT/'deliveries/能源燃料工艺_39项贴图候选_R172_20261019/39项燃料贴图对照.html'
    shapes = ROOT/'deliveries/21形态_电压主色修订候选_R172_20261019/index.html'
    discussion = ROOT/'doc/HK3GTL-内测5/讨论记录'/f'{now:%Y-%m-%d_%H-%M-%S}_能源工艺与21形态改色候选整批交付.html'
    assert not discussion.exists()
    content = '''<section><h2>已确认范围</h2><blockquote>扩展真实燃料工艺，仍要求每台15条独立配方；新贴图另行审批</blockquote><p>该答复覆盖普通/浓缩两类燃料的范围上限，原两类燃料及原12条工业线保留。原消息精确发送时间未知，本页时间为实际交付记录时间。新增物品设计已有授权，贴图审批仍单列；不擅自新增方块或把建筑候选当作批准。</p></section>'''
    content += f'''<section><h2>本批实际产物</h2><ul><li>{link(discussion,LOG/'燃料工艺与60工况候选_r172.html','15种燃料与60份反应工况候选')}：保留2类，扩展13种载体家族，列出制备、乏料、损耗和回收。核对57,966条2.9最终配方，保存28条原生原料工艺完整证据；这不代表所有祖先原料生存可达性均已验收。HBV首段7种，其余8种QSV后解锁；每座最终15份候选不能混称HBV首段已有15条。</li><li>{link(discussion,texture,'39项贴图原图与候选对照')}：39模型、55完整图层，透明度和原色覆盖层保留，已生成整批ZIP。尚未接入正式资产。</li><li>{link(discussion,shapes,'21形态电压主色修订候选')}：I01四阶、I02–I13及研究所五阶。I01映射HBV→QSV→QCV→IWV；研究所MAX→HDV→QEV→IRV→CIV。I08和五级研究所加强对应电压的实体立面色场。7组前后阶继承、21份NBT/Schematic逐格回读及材料计数通过；原批准归档和正式结构未改。</li></ul></section>'''
    content += f'''<section><h2>待审批的两批</h2><p>已通过原生提问分别提交39项贴图和21形态改色候选；截至本记录尚未收到这两项实际答复。贴图的问题是“是否采用这批13个燃料族的39项贴图”；结构的问题是“是否采用21形态电压改色总览的新配色”。任何推荐选项、超时或旧图获批都不算批准。</p><p>审批要求来自负责人“物品贴图需要审批”，以及{link(discussion,ROOT/'rule/当前多方块设计规则.md','当前多方块设计规则')}中“候选经负责人批准后再替换正式版本”的明确要求。新候选文件已可逐项审阅，再等待采用决定。</p></section>'''
    content += f'''<section><h2>复核与尚缺能力</h2><p>{link(discussion,AUDIT,'现有主审计')}已更新：八大件5/6，机壳5.5/6，依据是此前实现的128条制造和16条八板机壳配方，不是本轮新增代码。其他32域分值未改，能源仍2/16。不可平均成全模组完成率。</p><p>{link(discussion,numeric_html,'同一燃料跨阶65,536倍的合同数值风险')}已核出；此为纯合同和配方定义算术，尚未接入真实发电。后续须绑定固定燃料预算，并统一直接EU、余热、回收与损失账本；不得沿用按机器档位重置单棒出能的规则。</p><p>{link(discussion,LOG/'交付独立核验.json','独立交付核验')}：34域身份与分母保持、31篇其余正文原始字节不变；39身份、55图层、模型、ZIP及正式3028资产集合/SHA通过；46份HTML、1148个本地链接、45段内联JS与最小DOM通过。结构另有21逐格验证、7组扩建继承及本地PNG外观检查。</p><p>实际浏览器创建file://页被工具协议策略拒绝；本批未改用其他通道绕过，未宣称3D交互或游戏画面验证通过。未构建、未启动游戏、未部署，增强版2.9正式包仍为修订171。候选批次172只用于交付归类。</p><p>剩余包括60工况精确物料/能源/热量平衡、I17/I18和4反应堆实际执行器及已批准Pattern、控制器、真实输入输出、故障/卸载生命周期、最终配方与单人/多人自然流程。整包内存优化仍最后执行。</p></section>'''
    content += f'<footer>【记录 #1】{stamp}：删除无；新增本批交付事实、用户已确认范围、两批待审批状态与倍率风险；用途为接续时区分候选与已实施。</footer>'
    discussion.write_text(page('能源工艺与21形态改色候选整批交付',stamp,content),encoding='utf-8')

    source = AUDIT.read_text(encoding='utf-8')
    before_sha = sha(AUDIT)
    note = f'<p class="good" id="energy-budget-risk-r172">{stamp}：同一浓缩燃料棒的旧暂定合同每棒产电从I20到I22放大65,536倍，属于待修正数值风险，非游戏实测。新60工况不可继承此倍率。{link(AUDIT,numeric_html,"定量边界")} · {link(AUDIT,discussion,"本批实际交付与审批边界")}。能源仍2/16，正式游戏包仍171。</p>'
    assert 'id="energy-budget-risk-r172"' not in source
    source = re.sub(r'(<p class="good" id="energy-current-r172">.*?</p>)',lambda m:m[1]+note,source,count=1,flags=re.S)
    source = re.sub(r'(<header><h1>.*?</h1><p>)本轮更新 [^·]+',lambda m:m[1]+'本轮更新 '+stamp+' ',source,count=1,flags=re.S)
    source = source.replace('</body>',f'<p class="muted" id="revision172-closure">【追加记录 #9】{stamp}：删除无；新增能源定量风险、整批核验与待审批记录；原34域分母、分值及31篇其余正文保持不变。</p></body>',1)
    AUDIT.write_text(source,encoding='utf-8')
    receipt_path = LOG/'主审计本批更新.json'
    receipt = load(receipt_path)
    receipt.setdefault('followup_history',[]).append({'at':stamp,'before_sha256':before_sha,'after_sha256':sha(AUDIT),'reason':'只追加已核定量风险及候选交付链接，分值不变'})
    receipt['main_html_sha256'] = sha(AUDIT)
    receipt_path.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    assert all(sha(Path(path))==value for path,value in locked_hashes.items())

    # 只校验本次新增两页；其余交付已经过独立核验。
    class Links(HTMLParser):
        def __init__(self):
            super().__init__(); self.values=[]
        def handle_starttag(self, tag, attrs):
            if tag=='a': self.values += [value for key,value in attrs if key=='href']
    checked=[]
    for file in [numeric_html,discussion]:
        parser=Links(); parser.feed(file.read_text(encoding='utf-8'))
        for raw in parser.values:
            value=urlsplit(raw)
            if value.scheme or not value.path: continue
            target=(file.parent/unquote(value.path)).resolve()
            assert target.exists(), (str(file),raw)
            checked.append({'page':str(file.relative_to(ROOT)),'target':str(target.relative_to(ROOT))})
    result={'recorded_at':stamp,'discussion':str(discussion),'numeric_html':str(numeric_html),'local_links_checked':checked,
            'locked_review_artifacts_unchanged':True,'game_revision':171,'new_executable_recipes':0,
            'pending_approvals':['39项贴图','21形态改色'],'build_run':False,'game_run':False,
            '_record':f'【记录 #1】{stamp}：本批交付结束状态，不代表能源系统完成。'}
    (LOG/'候选批次闭环状态.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({key:result[key] for key in ['recorded_at','discussion','numeric_html','locked_review_artifacts_unchanged','pending_approvals']},ensure_ascii=False))


if __name__=='__main__':
    main()
