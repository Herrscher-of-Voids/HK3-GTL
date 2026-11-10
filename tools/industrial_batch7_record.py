# -*- coding: utf-8 -*-
"""Batch7 traceability, asset verification and HTML file inventory; no game/saves writes.
Change #1 2026-09-22: preserve old sources, append revision45 and latest authorized acceptance scope.
"""
from pathlib import Path
from datetime import datetime
import json, html, re
from PIL import Image
from industrial_content_catalog import CATALOG
ROOT=Path(__file__).resolve().parents[1]; RES=ROOT/'src/main/resources'; ART=RES/'assets/hk3gtl'
stamp=datetime.now(); changes=json.loads((ROOT/'tools/industrial_batch7_changed_files.json').read_text(encoding='utf-8'))
changes+=['src/main/java/com/sirin/hk3gtl/common/item/Hk3Items.java','src/main/java/com/sirin/hk3gtl/common/block/Hk3Blocks.java','src/main/java/com/sirin/hk3gtl/common/material/Hk3Materials.java','src/main/java/com/sirin/hk3gtl/common/bootstrap/Hk3ModHealthReport.java','src/main/java/com/sirin/hk3gtl/common/registration/Hk3CreativeTabsImpl.java','src/main/java/com/sirin/hk3gtl/common/registration/Hk3ContentRegistryAudit.java','tools/industrial_content_catalog.py','tools/generate_industrial_content.py','tools/industrial_batch7_record.py','tools/industrial_game_smoke.py']
errors=[]
langs={lang:json.loads((ART/f'lang/{lang}.json').read_text(encoding='utf-8')) for lang in ('zh_cn','en_us')}
for r in CATALOG:
    ident=r['id']; kind=r['kind']; key=f'{"material" if kind=="fluid" else kind}.hk3gtl.{ident}'
    for locale,lang in langs.items():
        if not lang.get(key): errors.append(f'Missing language {locale}:{key}')
    paths=[ART/f'models/item/{ident}.json'] if kind!='fluid' else [ART/f'models/item/{ident}_bucket.json']
    if kind=='block': paths += [ART/f'blockstates/{ident}.json',ART/f'models/block/{ident}.json',RES/f'data/hk3gtl/loot_tables/blocks/{ident}.json']
    paths += [ART/f'textures/{kind}/{ident}.png'] if kind!='fluid' else [ART/f'textures/block/fluids/fluid.{ident}.png',ART/f'textures/block/fluids/fluid.{ident}_flow.png']
    for p in paths:
        if not p.exists(): errors.append(f'Missing {p}')
        elif p.suffix=='.json': json.loads(p.read_text(encoding='utf-8'))
        elif p.suffix=='.png':
            with Image.open(p) as im:
                im.verify()
    if kind=='fluid':
        if r.get('reuse'): java=(ROOT/'src/main/java/com/sirin/hk3gtl/common/material/Hk3Materials.java').read_text(encoding='utf-8')
        else: java=(ROOT/'src/main/java/com/sirin/hk3gtl/common/registration/Hk3IndustrialFluids.java').read_text(encoding='utf-8')
        if f'"{ident}"' not in java: errors.append(f'Fluid absent in source: {ident}')
assert not errors,errors
log=ART/'changelog.json'; data=json.loads(log.read_text(encoding='utf-8'))
if not any(e.get('revision')==45 for e in data['entries']):
    data['entries'].insert(0,dict(version='0.4.0-beta.1',revision=45,codename='内测5开发批次7（未发布）',date=stamp.strftime('%Y-%m-%d'),time=stamp.strftime('%H:%M:%S'),summary='工业实体材料注册、Python专用贴图及启动核验。',reason='先补齐物品流体方块并验证进入游戏，再继续功能代码。',changes=['新增102种物品、35种GT工艺流体、93种结构材料方块；8项沿用原ID。','五种检测器为物品；九类核心区分未封装与封装；HKE与资格保持系统状态。','生成专用16像素纹理、动态流体纹理、模型、双语名称、掉落和工具标签。','修复创造页漏掉新结构方块；服务器启动按目录核对真实注册。','机器控制器与最终Pattern未以普通材料方块冒充，功能配方尚待后续。']))
    log.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
changes.append(str(log.relative_to(ROOT)).replace('\\','/'))
report=ROOT/'doc/HK3GTL-内测5/09_测试发布/物品流体方块注册与贴图_批次7.html'
s=report.read_text(encoding='utf-8')
if 'id="files"' not in s:
    links=''.join(f'<li><a href="../../../../{html.escape(p)}">{html.escape(p)}</a></li>' for p in sorted(set(changes)))
    s=s.replace('</html>',f'<h2 id="files">全部改动文件</h2><p>同批资源变更备注 #1：{stamp:%Y-%m-%d %H:%M:%S}，下列生成JSON/PNG由本报告提供统一说明；源文件备份在 archive/beta5-batch7-before。静态校验：238条物理目录及对应模型、纹理、双语名称全部通过。</p><ul>{links}</ul></html>')
    report.write_text(s,encoding='utf-8')
for p in [ROOT/'doc/HK3GTL-内测5/09_测试发布/代码落实进度与旧实现归档.html',ROOT/'doc/崩坏三-GTL/00_项目总览/模组全面系统性分析报告.html']:
    s=p.read_text(encoding='utf-8')
    if 'beta5-registration-batch7' not in s:
        block=f'<section id="beta5-registration-batch7"><h2>内测5代码批次7 · 物理内容注册</h2><p>{stamp:%Y-%m-%d %H:%M:%S}：102新物品、35新流体、93新结构材料方块，238项目录校验通过。贴图由Python生成，旧ID及实现保留。详见“物品流体方块注册与贴图_批次7.html”；控制器功能、最终建筑和配方不计入本批材料注册完成率。最新要求改为本批先做启动入世界检查。</p></section>'
        s=s.replace('</body>',block+'</body>') if '</body>' in s else s+block
        p.write_text(s,encoding='utf-8')
record=ROOT/'doc/HK3GTL-内测5/讨论记录/2026-09-22_16-33_物理内容注册贴图与入游戏优先.html'
if not record.exists(): record.write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>物理内容注册与游戏启动优先</title><body>
<h1>物理内容注册、贴图及入游戏优先</h1><p>讨论日期：2026-09-22，Asia/Hong_Kong。记录时间：{stamp:%H:%M:%S}。</p>
<p>负责人明确要求：先注册要用的全部物品、流体、方块并做完贴图，能够进入游戏后才继续下一步。沿用之前Python生成专用纹理、不删除旧代码、逐文件报告的要求。</p>
<p>执行范围：已批准工业链的物理内容、资源与启动检查。此项授权覆盖此前统一延后游戏测试的安排。未授权重建全部建筑造型；最终Pattern仍需逐台审阅，不以普通方块冒充可工作控制器。</p>
<p>来源：工业树状图v5、工业能力矩阵v1、工业收口v3、研究课题树；程序绘图原创，无外部图片许可。旧材料及16电压组件保留。HKE、研究与审判资格不变成绕过检查的物品。</p>
<p>待完成验收：运行最终构建、进入独立测试世界、检查注册目录与模型缺失。完整机器功能、配方和多方块成型不因注册完成而视为验收通过。</p></body></html>''',encoding='utf-8')
print('PASS: 238 catalog entries, assets, models and translations. Revision45 and HTML records written.')

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
