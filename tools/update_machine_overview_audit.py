# -*- coding: utf-8 -*-
"""把机器总览本轮证据写回既有全系统HTML审计，不重算其他系统历史分数。
【变更记录 #1】2026-10-19 02:13:37（修订171，香港时间）
删除：当前页依赖多层旧状态脚本覆盖的展示；新增：逐能力数据、当前构建证据和独立快照。
修改：只更新N01、页首和本轮开发说明；用途：能力实现、部署和游戏验收分别记账，保留历史快照。
"""
# 【变更记录 #2】2026-10-19 02:29:03（修订171）：删除评分CSS类精确空格匹配；新增兼容旧尾空格排序、明确模组来源筛选及过载恢复边界；修改为保留真实验收缺口，防止更新脚本中断或误报模块化子模块。
# 【变更记录 #3】2026-10-19 02:32:26（修订171）：删除沿用能源目录读取身份的说明；新增本次总览接续读取凭据直链；修改报告页脚，便于核实六份规则的当前身份。
# 【变更记录 #4】2026-10-19 02:55:00（修订171）：新增实际游戏截图、存档核验及运行证据直链；修改部分GUI通过与多人/恢复待验收的分列，避免将基本交互测试冒充全系统验收。
# 【变更记录 #5】2026-10-19 02:57:43（修订171）：删除表格笼统的实机待验文字；新增基本单人已验与多人/恢复待验区分；修改能力数据和审计行，用于与实际截图及落盘记录保持一致。
from pathlib import Path
from datetime import datetime, timezone, timedelta
import argparse
import html
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'logs/machine-overview-r171'
AUDIT = ROOT / 'doc/HK3GTL-内测5/09_测试发布/内测5全库逐份代码文档对照审计_20261017.html'
REPORT = OUT / '文明机器总览整系统接入与验收.html'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--build', required=True)
    parser.add_argument('--deployment', required=True)
    parser.add_argument('--runtime', required=True)
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')
    scores = [
        ('跨HK3／GT／附属机器的注册ID、名称、模组、控制器类型目录', .5,
         'GT机器实例目录已接HK3与继承GT机器基类的附属；不枚举未放置的全注册目录。非GT专有控制器、实际Pattern关联与子模块适配仍缺。'),
        ('成型／拆除事件登记并低频修复', 1,
         '真实放置、加载、卸载、拆除及成型/失效事件接入；每秒最多64个已登记位置轮转补查，不扫描世界。生命周期队列最多4096项；已有HK卸载记录在过载后可由预算轮转重新验证恢复，新未登记机器超过限额仍可能需现场登记。'),
        ('跨维度位置、区块未加载及重启记录', 1,
         'SavedData保存维度/位置/最后可信状态和存档刻；重启全部先视为未加载，仅检查已加载位置，损坏记录拒绝静默重置。'),
        ('运行、停机、缺EU、缺输入、卸载、未成型、未适配、未知八态', .5,
         '八态模型、GT公开RecipeLogic状态和只读显示已接入；缺电/缺料需可靠原因，无法判定时保留未知，不能把每个附属状态提供者算完整。'),
        ('团队可见而个人信件／HKE保持隐私', 1,
         '每次分页及UUID详情均按当前研究团队过滤；普通现场登记拒绝抢占其他队，权威迁队立即撤销旧队后续查询权限。个人库存、HKE与信件不进入载荷。'),
        ('T03监测与T04调度业务区分', .5,
         '手机仅提供监测和索引登记，不产生远程控制或调度动作；T03实体终端及T04真实调度仍未接入，本次没有新增方块或结构。'),
        ('按所属模组／状态筛选并打开机器详情', 1,
         '手机文明页入口、来源或状态筛选、每页4台、只读详情分页、刷新及原页返回已接入。专有模块化子模块未完成。'),
        ('只读总览、不误写研究／工程进度', 1,
         '总览只读投影；现场登记仅改变索引归属，不改变机器运行、研究、工业事实、物品或能源。'),
    ]
    score = sum(x[1] for x in scores)
    pct = score / len(scores) * 100
    summary = {'revision':171,'updated_at':now,'system':'N01','score':score,'denominator':8,'percent':pct,
               'build':args.build,'deployment':args.deployment,'runtime':args.runtime,
               'capabilities':[dict(name=n,score=s,evidence=e) for n,s,e in scores],
               'unverified':['基本单人目录/详情/筛选和保存落盘已验；完整GUI边界、多人团队、跨维度重启、拆除与大基地仍待验','T03实体终端与T04调度','非GT和专有模块化子模块适配'],
               'energy_score_unchanged':'2/16', 'whole_mod_completion':'未计算，不平均不同系统粒度'}
    (OUT/'capability-audit.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    style='body{max-width:1160px;margin:24px auto;padding:0 22px;background:#eef4f3;color:#183c45;font:16px/1.75 system-ui,"Microsoft YaHei",sans-serif}header{background:#193e47;color:white;padding:24px;border-radius:10px}h1{margin:0;font-size:28px}h2{font-size:22px;margin-top:28px}a{color:#126977}table{width:100%;border-collapse:collapse;background:white}th,td{border:1px solid #c7d7db;padding:12px;text-align:left;vertical-align:top}.box{background:white;padding:18px;border:1px solid #c7d7db;border-radius:8px;margin:16px 0}.warn{background:#fff0e4;border-left:5px solid #a96138;padding:16px}code{overflow-wrap:anywhere}footer{border-top:1px solid #ccd9dd;margin-top:28px;padding-top:12px;color:#536e76}'
    rows=''.join(f'<tr><td>{html.escape(n)}</td><td>{s:g}/1</td><td>{html.escape(e)}</td></tr>' for n,s,e in scores)
    source_files=['common/overview/Hk3MachineOverviewData.java','common/overview/Hk3MachineOverviewService.java','common/overview/Hk3MachineOverviewAdapter.java','common/phone/Hk3PhoneAppService.java','client/phone/Hk3MachineOverviewPane.java']
    sources=' · '.join(f'<a href="../../src/main/java/com/sirin/hk3gtl/{f}">{Path(f).name}</a>' for f in source_files)
    runtime_html = ''
    if (OUT/'runtime-verification.json').exists():
        runtime_html = '<section class="box"><h2>指定2.9实际游戏证据</h2><p>专用创造、超平坦、允许作弊存档：真实玩家放置GT基础组装机后自动登记；目录、详情、返回、来源筛选与运行筛选通过，保存后核对NBT中1条机器记录及坐标。没有把单人基本交互称为多人或重启验收。</p><p><a href="runtime-verification.json">实机与存档核验</a> · <a href="runtime-latest.log">本轮实际日志</a> · <a href="instance-before-launch.json">当前整包组合</a> · <a href="lifecycle-refmap-verification.json">生产方法映射</a></p><p>下图为实际游戏截图；帧数显示不作为整包性能达标证据。</p><a href="runtime-directory.png"><img src="runtime-directory.png" alt="真实放置的基础组装机进入团队机器目录" style="width:100%;height:auto"></a><a href="runtime-detail.png"><img src="runtime-detail.png" alt="机器详情正确显示注册ID、坐标及未知状态" style="width:100%;height:auto"></a></section>'
    report=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>文明机器总览整系统接入与验收 · r171</title><style>{style}</style></head><body><header><h1>文明机器总览：实例索引、状态、团队权限与手机界面</h1><p>{now} · 修订171 · 能力实现 {score:g}/8（{pct:g}%）</p></header><main><section class="box"><p><strong>本轮范围：</strong>从原先仅显示文明等级和研究摘要，接成实际机器实例目录；服务端索引、GT生命周期、权限边界、持久化和手机界面按同一批次交付。</p><p>八项沿用原审计分母；完整实现计1、部分计0.5。缺少实机测试不抹去代码实现，但游戏验收单独保留待完成。不同系统分数不平均成整个模组完成率。</p></section><section class="box"><h2>当前证据</h2><p>构建：{html.escape(args.build)}</p><p>部署：{html.escape(args.deployment)}</p><p>运行：{html.escape(args.runtime)}</p><p><a href="build-final.log">完整构建日志</a> · <a href="package-verification.json">包核验</a> · <a href="deployment.json">部署收据</a> · <a href="capability-audit.json">逐能力数据</a></p></section><h2>逐项差距</h2><div style="overflow:auto"><table><thead><tr><th>能力</th><th>分数</th><th>实现与剩余差距</th></tr></thead><tbody>{rows}</tbody></table></div><section class="box"><h2>权限和性能边界</h2><p>新放置机器使用真实放置者；HK机器沿用固定研究团队。第三方旧机器只能通过现场登记核验准星、同维度8格、已加载、原生UI与FTB领地主队权限，无法证明权限则拒绝。已属于其他团队的记录不能被普通绑定抢占。</p><p>低频补查最多每秒64个已登记位置；卸载后保留最后可信快照，不主动加载区块，不把未知误报成停机。查看机器不会创建研究或工业成果。</p></section><section class="warn"><strong>未收口：</strong>T03实体终端与T04调度、非GT专有机器、模块化子模块、全附属缺电/缺料精确归因，以及当前2.9多人/跨维度/重启/大型基地实机验收。没有新增结构、方块、机壳、燃料或贴图。能源系统仍为2/16；<a href="../energy-production-r171/能源生产整系统阻塞审计与闭环决策_r171.html">能源整系统差距与燃料边界</a>另行保留。</section><h2>实现依据</h2><p>{sources}</p><p><a href="../../doc/HK3GTL-内测5/11_系统专项/文明总览系统/文明总览收口方案_v1.html">既定设计</a> · <a href="../../doc/HK3GTL-内测5/09_测试发布/内测5全库逐份代码文档对照审计_20261017.html#N01">返回全系统审计</a></p></main><footer>记录 #1 · {now}：按整系统接入与逐能力证据更新；保留其他系统快照，未计算全模组发布完成率。规则读取身份见<a href="续接规则读取身份.json">本次六文件读取凭据</a>。历史批准建筑和资源保持原字节。</footer></body></html>'''
    report=report.replace('<h2>逐项差距</h2>',runtime_html+'<h2>逐项差距</h2>',1)
    REPORT.write_text(report,encoding='utf-8')
    source=AUDIT.read_text(encoding='utf-8')
    snapshot=OUT/'全系统审计接入前快照.html'
    if not snapshot.exists(): shutil.copy2(AUDIT,snapshot)
    source=re.sub(r'(<header><h1>.*?</h1>)<p>.*?</p>',lambda m:m[1]+f'<p>本轮更新 {now} · 增强版2.9 · 修订171文明机器总览；其他系统分数保留此前审计快照。</p>',source,count=1,flags=re.S)
    metric=re.search(r'<div class="metrics">.*?</div></div><div class="alert">',source,re.S)
    assert metric,'缺少原审计指标块'
    newmetric=f'<div class="metrics"><div class="metric"><strong>34</strong><span>系统／子系统，保留原分母</span></div><div class="metric"><strong>{score:g} / 8</strong><span>文明机器总览能力实现{pct:g}%；验收另记</span></div><div class="metric"><strong>修订171</strong><span>{html.escape(args.build)}</span></div><div class="metric"><strong>尚未可发布</strong><span>没有可核验的全模组发布完成率</span></div></div><div class="alert">'
    source=source[:metric.start()]+newmetric+source[metric.end():]
    source=re.sub(r'<div class="alert">.*?</div>',f'<div class="alert"><strong>本轮开发文明机器总览：</strong>{score:g}/8（{pct:g}%）；能源仍2/16。构建：{html.escape(args.build)}。部署：{html.escape(args.deployment)}。运行：{html.escape(args.runtime)}。<a href="../../../logs/machine-overview-r171/文明机器总览整系统接入与验收.html">本轮完整报告</a>。未把待审批结构、未完成适配或未验收内容记为完成。</div>',source,count=1,flags=re.S)
    row=f'<tr data-system="N01"><td><a href="#N01"><strong>文明机器总览／T03监测目录</strong></a></td><td><span class="pct">{pct:.2f}%</span><div class="bar"><i style="width:{pct}%"></i></div></td><td>{score:g} / 8<br><span class="small">完整5 · 部分3 · 缺失0</span></td><td>3项能力仍未闭合；基本单人已验，多人／恢复等待验</td><td>本轮整批开发；详细证据见下<br><span class="small">T03实体／T04调度和专有适配仍未完成</span></td></tr>'
    source=re.sub(r'<tr data-system="N01">.*?</tr>',row,source,count=1,flags=re.S)
    def sort_rows(match):
        rows=re.findall(r'<tr.*?</tr>',match[1],re.S)
        rows.sort(key=lambda r:float(re.search(r'class="pct[^"]*">([\d.]+)%',r)[1]))
        return '<tbody>'+''.join(rows)+'</tbody>'
    source=re.sub(r'<tbody>(.*?)</tbody>',sort_rows,source,count=1,flags=re.S)
    article=re.search(r'<article id="N01".*?</article>',source,re.S)[0]
    article=re.sub(r'<h3>.*?</h3>',f'<h3>文明机器总览／T03监测目录 · {score:g}/8（{pct:.2f}%）</h3>',article,count=1,flags=re.S)
    items=''.join(f'<li><span class="state">{"实现" if s==1 else "部分"} · {s:g}</span> <strong>{html.escape(n)}</strong><p>{html.escape(e)}</p></li>' for n,s,e in scores)
    article=re.sub(r'<ol>.*?</ol>',f'<ol>{items}</ol>',article,count=1,flags=re.S)
    article=re.sub(r'<p class="good" id="n01-current">.*?</p>', '', article, flags=re.S)
    article=article.replace('<details>',f'<p class="good" id="n01-current">修订171整批实现，{now}。<a href="../../../logs/machine-overview-r171/文明机器总览整系统接入与验收.html">逐能力与构建／部署／验收证据</a>；T03实体、T04调度和专有模块仍未完成。</p><details>',1)
    source=re.sub(r'<article id="N01".*?</article>',lambda _:article,source,count=1,flags=re.S)
    source=re.sub(r'<h2 id="first-system">.*?</h2><div class="box">.*?</div>',f'<h2 id="first-system">本轮整系统：文明机器总览（修订171）</h2><div class="box"><p>能源最低系统存在结构审批和燃料合同缺口，维持2/16；转向此前并列最低的N01，现为{score:g}/8（{pct:g}%）。</p><p>已接机器索引、生命周期、团队隔离、卸载重启快照、八态与手机分页详情。仍缺实体终端、专有模块与完整实机验收。<a href="../../../logs/machine-overview-r171/文明机器总览整系统接入与验收.html">查看整批证据</a>。</p></div>',source,count=1,flags=re.S)
    script='''<script>const query=document.querySelector('#search'),gaps=document.querySelector('#gaps');const entries=Array.from(document.querySelectorAll('article[data-system]'));function filter(){const q=query.value.trim().toLowerCase();for(const e of entries){const row=document.querySelector('tr[data-system="'+e.dataset.system+'"]');const hide=!e.textContent.toLowerCase().includes(q)||(gaps.checked&&e.dataset.full==='true');e.classList.toggle('hidden',hide);if(row)row.classList.toggle('hidden',hide);}}query.addEventListener('input',filter);gaps.addEventListener('change',filter);</script>'''
    source=re.sub(r'<script>.*?</script>',script,source,flags=re.S)
    energy_note='<p class="good" id="energy-current-r171">修订171：I19–I22各1条暂定计划，合同统一与77项隔离回归见r170；尚无正式控制器、Pattern、真实产电IO和热管理。每台15条独立燃料配方与当前燃料范围仍有未决冲突，能源维持2/16。<a href="../../../logs/energy-production-r171/能源生产整系统阻塞审计与闭环决策_r171.html">能源整系统阻塞与待定路线</a>。</p>'
    source=re.sub(r'<p class="good" id="energy-current-r171">.*?</p>','',source,flags=re.S)
    source=source.replace('<article id="energy_production" data-system="energy_production">','<article id="energy_production" data-system="energy_production">'+energy_note,1)
    note=f'<p class="muted" id="revision171-overview">【追加记录 #7】{now}（修订171）：更新文明机器总览为{score:g}/8；构建、部署、运行状态分别记录。历史r170能源统一合同与r171能源阻塞审计见快照及各自报告；其他33系统不重评分。<a href="../../../logs/machine-overview-r171/全系统审计接入前快照.html">本轮更新前快照</a>。</p>'
    source=re.sub(r'<p class="muted" id="revision171-overview">.*?</p>','',source,flags=re.S)
    source=source.replace('</footer>','</footer>'+note,1)
    AUDIT.write_text(source,encoding='utf-8')
    print(json.dumps({'score':score,'percent':pct,'updated_at':now,'report':str(REPORT)},ensure_ascii=False))


if __name__=='__main__':
    main()
