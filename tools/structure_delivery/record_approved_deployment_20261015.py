# -*- coding: utf-8 -*-
"""变更记录 #1：2026-10-15 01:31:00 Asia/Hong_Kong（修订156）。
保存四个用户指定ZIP的来源哈希、最终部署讨论记录及I14浏览器观察。
不改批准归档或生产源码；输入为已完成部署收据及已有截图，缺少证据直接失败。
"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import html

ROOT = Path(__file__).resolve().parents[2]
NOW = datetime.now(timezone(timedelta(hours=8)))
LOG = ROOT / 'logs/approved-architecture-20261015'
receipt = json.loads((LOG/'deployment-receipt.json').read_text(encoding='utf-8'))
sources = [
    'I09-I13_重设计_V6_20261014/I09-I13_V6_结构与预览.zip',
    'I01-I08_重设计_V7_20261014/I01-I08_V7_结构与预览.zip',
    'I01_采集塔四阶_正交重设计_V8_20261014/I01_V8_四阶结构与预览.zip',
    'S01-S05_研究所五阶_原地扩建_V1_20261014/S01-S05_研究所五阶_结构与预览.zip',
]
source_evidence = []
for name in sources:
    path = ROOT/'deliveries'/name
    source_evidence.append({'file':str(path),'bytes':path.stat().st_size,
        'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
(LOG/'four-approved-archives.json').write_text(json.dumps(source_evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

proof = ROOT/'logs/i14-press-v3/browser-full-view.jpg'
assert proof.is_file()
browser_evidence = {
    'time':NOW.isoformat(), 'url':'http://127.0.0.1:8370/三维评审.html',
    'title':'魂钢聚合压铸机 · V3 曲冠压铸候选',
    'observed_ui_checks':['完整视图材质与双曲冠主体可见','前右整体正常切换','内部剖切将层高42改为20并隐藏玻璃',
        '净空维护路径可见','重置恢复完整层高42及玻璃','浏览器捕获error日志为空'],
    'screenshot':str(proof), 'geometry_changed':False, 'game_verified':False, 'user_approved':False,
    'note':'生成包内未实测浏览器字样记录生成时状态；本文件为随后完成的独立浏览器实测记录。'
}
(ROOT/'logs/i14-press-v3/browser-verification.json').write_text(json.dumps(browser_evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

out = ROOT/'doc/HK3GTL-内测5/讨论记录'/f'{NOW:%Y-%m-%d_%H-%M-%S}_四包最新结构正式实装与下一座I14候选.html'
content = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>四包最新结构正式实装与下一座I14候选</title><style>body{{max-width:1100px;margin:auto;padding:30px;background:#101722;color:#e9eef5;font:16px/1.8 system-ui,"Microsoft YaHei",sans-serif}}h1,h2{{color:#9fe7d4}}section{{background:#172234;border:1px solid #32445e;border-radius:10px;padding:18px;margin:16px 0}}code{{color:#ffd590}}a{{color:#9fe7d4}}</style></head><body><h1>四包最新结构正式实装与下一座 I14 候选</h1><p>记录时间：{NOW:%Y-%m-%d %H:%M:%S} Asia/Hong_Kong（UTC+08:00）</p>
<section><h2>用户要求与已确认决定</h2><p>“要将我最新决定好的，也就是你设计的多方块结构实装到游戏里”，明确指定四个 ZIP。继续此前“先把现在这些多方块结构实装到游戏里，然后继续进行下一个多方块结构的设计”的任务。</p><ul><li>I01四阶以正交V8覆盖V7旧I01；I02–I08采用V7。</li><li>I09–I13采用V6；S01–S05采用五阶原地扩建V1。</li><li>目标为PrismLauncher的GTL十一周目，当前明确目标覆盖旧GregTech-Leisure实例约束。</li><li>共18个机器族、21种结构。下一座I14只作为候选，不进入正式包。</li></ul></section>
<section><h2>实际执行与验证</h2><ul><li>正式包：<code>{html.escape(receipt['installed_jar'])}</code>。</li><li>SHA-256：<code>{receipt['jar_sha256']}</code>，{receipt['jar_bytes']:,} bytes。</li><li>63份结构JSON/NBT/模板元数据及3份语言与修订资源，与源码共66份逐字节相同；模组元数据按UTF-8读取正确，先前终端乱码为解码误报。</li><li>最终clean build成功，65个任务执行；21项正式资源、端口能力、七次逐块继承与研究执行等回归通过。单独编译和静态检查不视为游戏内成型。</li><li>旧HK3GTL与完全同SHA的重复GTMThings已备份，active hk3gtl及gtmthings各一个；其余JAR逐文件哈希不变。原禁用包继续禁用。</li><li>研究所S02–S05装配消耗前阶主控并沿用S01现有BOM、1200tick和MAX耗电，按ALE/QLE/ILE/CLE研究开放；I13沿用工业控制器模板并受RN-HRC约束。未把研究开题费用当成制造成本。</li><li>本轮未启动游戏或修改存档；游戏成型、GUI、配方运行及S05扫描1747305格的性能仍待实际验收。</li></ul></section>
<section><h2>备份与交付</h2><p>备份：<code>{html.escape(receipt['backup_directory'])}</code>。</p><p>正式交付：<code>{html.escape(receipt['release_directory'])}</code>，含JAR、21份可放置NBT和部署收据。内置<code>/hk3structure place s01 ~ 100 ~</code>需OP、创造及整个包围盒为空；模板不依赖投影或WorldEdit，本轮没有启动命令。</p></section>
<section><h2>I14下一座候选与待定事项</h2><p>魂钢聚合压铸机曲冠V3：51×47×43（宽×深×高），11,507个方块。四根收腰巨柱托起双曲冠承重梁，中央压杆、压板与下模外露；偏置熔炼坩埚及蓄压冷却分区，前入料到后脱模形成直线工艺轴。已检查完整、右侧和内部剖切视图及维护净空，浏览器error日志为空。该候选待用户外观决定，没有正式部署。</p><p><a href="../../../deliveries/I14_魂钢聚合压铸机_曲冠重设计_V3_20261015/index.html">I14预览</a> · <a href="../../../deliveries/I14_魂钢聚合压铸机_曲冠重设计_V3_20261015/I14_V3_结构与预览.zip">I14结构包</a></p></section>
<section><h2>相关文档与后续</h2><p><a href="../../../logs/approved-architecture-20261015/clean-build-final.log">最终构建</a> · <a href="../../../logs/approved-architecture-20261015/deployment-receipt.json">部署收据</a> · <a href="../../../logs/approved-architecture-20261015/four-approved-archives.json">四ZIP来源哈希</a> · <a href="../../../logs/approved-architecture-20261015/independent-integration-review.json">独立源码复核快照</a> · <a href="../../../logs/i14-press-v3/browser-verification.json">I14浏览器实测</a>。</p><p>下一步为指定实例专用测试存档的实际成型与性能验收，以及用户对I14候选的外观意见；不把候选预览自动视为批准。历史讨论和归档均保留。</p></section><footer>变更记录 #1 · {NOW:%Y-%m-%d %H:%M:%S} Asia/Hong_Kong · 修订156正式部署记录，区分已确认、已实施、静态通过和游戏未验收。</footer></body></html>'''
out.write_text(content,encoding='utf-8')
print(out)
