"""按负责人撤销决定移除五方贸易运行系统，保存精确归档供追溯。
变更记录 #1：执行时记录本机时间（内测5修订99）。
删除：贸易代码、资源、构建任务及发布脚本；保留：其他系统、历史讨论和存档。
"""
from pathlib import Path
from datetime import datetime
import hashlib
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
NOW = datetime.now()
STAMP = NOW.strftime('%Y%m%d-%H%M%S')
TIME = NOW.strftime('%Y-%m-%d %H:%M:%S')
ARCHIVE = ROOT / 'archive' / ('trade-removed-r99-' + STAMP)
LOG = ROOT / 'logs/trade-removal-r99'
LOG.mkdir(parents=True, exist_ok=True)
manifest = {'revision': 99, 'time': TIME, 'archive': str(ARCHIVE), 'removed': [], 'changed': []}

def target(relative):
    p = (ROOT / relative).resolve()
    assert p.is_relative_to(ROOT) and not p.is_symlink(), p
    return p

def backup(relative):
    p = target(relative)
    assert p.is_file(), p
    dest = ARCHIVE / relative
    assert not dest.exists(), dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(p, dest)
    assert dest.read_bytes() == p.read_bytes()
    return p

def change(relative, transform, purpose=None):
    p = backup(relative)
    old = p.read_text(encoding='utf-8')
    new = transform(old)
    assert old != new, relative
    if purpose and p.suffix == '.java':
        number = max([int(n) for n in re.findall(r'变更记录 #(\d+)', old)] or [0]) + 1
        note = f'/** 【变更记录 #{number}】{TIME}（内测5修订99）：删除：{purpose}；新增：无；修改：按负责人决定撤下五方贸易；用途：保留其他系统独立运行。 */\n'
        # 新记录紧接历史注释，放在类声明或首个导入前，不覆盖旧记录。
        anchor = new.index('import ')
        new = new[:anchor] + note + new[anchor:]
    p.write_text(new, encoding='utf-8', newline='')
    manifest['changed'].append(relative)

def replace(old, a, b, count=1):
    assert old.count(a) == count, (a, old.count(a), count)
    return old.replace(a, b)

base = 'src/main/java/com/sirin/hk3gtl/'
change(base+'Hk3Gtl.java', lambda s: replace(s,'        com.sirin.hk3gtl.common.trade.Hk3TradeService.registerDialogues();\n',''), '贸易对白注册')
change(base+'common/block/Hk3Blocks.java', lambda s: replace(s,'        com.sirin.hk3gtl.common.trade.Hk3TradeBlocks.register();\n',''), 'T02方块及方块实体注册')
change(base+'mixin/Hk3ResearchOutputMixin.java', lambda s: replace(s,'        if(Boolean.TRUE.equals(result.getReturnValue()))\n            com.sirin.hk3gtl.common.trade.Hk3TradeProgress.machineOutput(machine,recipe);\n',''), '机器输出后的贸易电压记账回调')
def network(s):
    block = '        CHANNEL.registerMessage(packetIndex++, com.sirin.hk3gtl.common.trade.Hk3TradeViewPacket.class,\n                com.sirin.hk3gtl.common.trade.Hk3TradeViewPacket::encode, com.sirin.hk3gtl.common.trade.Hk3TradeViewPacket::decode,\n                com.sirin.hk3gtl.common.trade.Hk3TradeViewPacket::handle,\n                java.util.Optional.of(net.minecraftforge.network.NetworkDirection.PLAY_TO_CLIENT));\n'
    return replace(replace(s,block,''),'PROTOCOL_VERSION = "12"','PROTOCOL_VERSION = "13"')
change(base+'common/network/Hk3Network.java', network, '贸易网络包；协议升至13防止旧包序号错配')
def phone(s):
    a = '            app("贸易",x+20,y+94,()->command("hk3trade browse schicksal 0"));\n            app("通知 "+view.getInt("Unread"),x+174,y+94,()->command("hk3phone notifications"));\n            app("信件",x+20,y+158,()->command("hk3letter"));\n            app("更新详情",x+174,y+158,()->command("hk3updates"));\n            app("IF 档案",x+20,y+222,()->command("hk3if"));'
    b = '            app("通知 "+view.getInt("Unread"),x+20,y+94,()->command("hk3phone notifications"));\n            app("信件",x+174,y+94,()->command("hk3letter"));\n            app("更新详情",x+20,y+158,()->command("hk3updates"));\n            app("IF 档案",x+174,y+158,()->command("hk3if"));'
    return replace(s,a,b)
change(base+'client/phone/Hk3PhoneScreen.java', phone, '手机贸易App入口并重排剩余四个应用')
change(base+'common/dialogue/definition/Hk3ApprovedDialogues.java', lambda s: replace(s,'"communication", "trade", "npc"','"communication", "npc"'), '只读全文目录的贸易分类')
test = 'src/test/java/com/sirin/hk3gtl/test/dialogue/ApprovedProseTest.java'
def prose_test(s):
    s=replace(s,'Hk3ApprovedProse.all().size()==736','Hk3ApprovedProse.all().size()==644')
    s=replace(s,'Hk3ApprovedProse.system("trade").size()==92,"五方贸易92条"','Hk3ApprovedProse.system("trade").isEmpty(),"贸易正文已从运行目录移除"')
    return replace(s,'检查通过：736条','检查通过：644条')
change(test,prose_test,'92条贸易正文的活动计数要求，改为验证无贸易分类')

def build(s):
    block='tasks.register("runTradeRuntimeTest", JavaExec) {\n    dependsOn("compileTestJava", "classes")\n    group = "verification"\n    classpath = sourceSets.test.runtimeClasspath\n    mainClass = "com.sirin.hk3gtl.test.trade.TradeRuntimeTest"\n}\ntasks.named("check").configure { dependsOn("runTradeRuntimeTest") }'
    return replace(s,block,f'// 变更记录 #19：{TIME}，修订99。删除贸易专用任务与check依赖；保留其他回归。')
change('build.gradle',build)

def prose(s):
    data=json.loads(s)
    removed=[e for e in data['entries'] if e['system']=='trade']
    assert len(removed)==92
    data['entries']=[e for e in data['entries'] if e['system']!='trade']
    assert len(data['entries'])==644
    data['_removal_r99']={'time':TIME,'reason':'负责人撤销贸易系统，92条贸易原文随修改前文件归档；其他已审正文保留。'}
    return json.dumps(data,ensure_ascii=False,indent=2)+'\n'
change('src/main/resources/assets/hk3gtl/narrative/approved.json',prose)
for locale in ('zh_cn','en_us'):
    def language(s):
        data=json.loads(s)
        keys=[k for k in data if k.startswith(('hk3gtl.trade.','hk3gtl.approved.trade.')) or k=='block.hk3gtl.trade_fulfillment_terminal']
        assert keys
        for k in keys: del data[k]
        data['_comment_trade_removal_r99']=TIME+'：删除五方贸易界面与贸易正文语言键；其他系统保留。'
        return json.dumps(data,ensure_ascii=False,indent=2)+'\n'
    change(f'src/main/resources/assets/hk3gtl/lang/{locale}.json',language)

def changelog(s):
    data=json.loads(s)
    assert not any(e.get('revision')==99 for e in data['entries'])
    data['entries'].insert(0,{'version':'0.5.0','revision':99,'codename':'HK3GTL-内测5','date':NOW.strftime('%Y-%m-%d'),'time':NOW.strftime('%H:%M:%S'),'reason':'负责人明确要求停止并删除贸易系统。','changes':['删除：五方贸易报价、订单结算、AE库存扫描、进度和首信放量逻辑。','删除：T02注册与配方、/hk3trade、手机贸易App、贸易数据包及92条活动贸易正文。','保留：MAX手机制作安装、通知、组织交流、研究、NPC和终审；协议升至13。','归档：本轮撤销的代码、资源和报价工具保留在非构建目录；历史讨论和玩家存档不清除。','测试与实例部署结果另记，不将构建通过视为游戏验证。']})
    return json.dumps(data,ensure_ascii=False,indent=2)+'\n'
change('src/main/resources/assets/hk3gtl/changelog.json',changelog)

removed=[]
for folder in (base+'common/trade',base+'client/trade','src/test/java/com/sirin/hk3gtl/test/trade','src/main/resources/data/hk3gtl/trade'):
    removed.extend(str(p.relative_to(ROOT)).replace('\\','/') for p in target(folder).glob('*') if p.is_file())
for section in ('data/hk3gtl/recipes','data/hk3gtl/loot_tables/blocks','assets/hk3gtl/blockstates','assets/hk3gtl/models/item','assets/hk3gtl/models/block'):
    removed.append('src/main/resources/'+section+'/trade_fulfillment_terminal.json')
removed += ['tools/'+name for name in ('approve_trade_quotes_r95.py','publish_trade_quotes_r95.py','deploy_trade_phone_r95.py','trade_item_pools.py','trade_expansion_review_template.html','build_trade_review_r94.py','build_multimod_trade_review.py','audit_trade_mod_items.py','finalize_trade_r94.py')]
for relative in removed:
    p=backup(relative)
    manifest['removed'].append({'path':relative,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    p.unlink()

(LOG/'source-removal.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
record=ROOT/'doc/HK3GTL-内测5/讨论记录'/f'{NOW:%Y-%m-%d_%H%M%S}_撤销并删除贸易系统.html'
record.write_text(f'<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>撤销并删除贸易系统</title><body><h1>撤销并删除贸易系统</h1><p>{TIME}（本机时间）</p><h2>用户最新决定</h2><p>用户指出海渊、虚数、量子、终焉不是现行16档正式显示名称，明确要求“停手吧，把贸易系统删了吧”。该决定覆盖此前本次贸易扩充、AE识别及分批开放安排；不再继续这些工作。</p><h2>纠错</h2><p>助手误把旧注册键描述为正式名称，并擅自增加电路交付返还方案及每日放量数值。上述未定稿方案撤销，不作为后续实现依据。</p><h2>执行范围</h2><p>五方贸易运行源码、T02、命令、手机入口、AE扫描、活动报价、交易正文和发布工具移出构建；精确修改前文件归档到 {ARCHIVE.relative_to(ROOT).as_posix()}。MAX手机与通知、交流、研究、NPC、终审保持。未清除玩家存档或历史讨论。旧量子工业机器不属于本次新建T02交易系统，未擅自删除它的研究与生产配方。</p><h2>状态</h2><p>源码移除已执行；正在执行clean build与最终JAR检查。双实例的替换及配置移除尚待验证后执行，结果另记。</p></body></html>',encoding='utf-8')
manifest['discussion']=str(record)
(LOG/'source-removal.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'removed':len(removed),'changed':len(manifest['changed']),'archive':str(ARCHIVE),'discussion':str(record)},ensure_ascii=False))
