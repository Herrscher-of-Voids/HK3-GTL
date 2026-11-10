# -*- coding: utf-8 -*-
"""I20候选同源导出、真实材质视图和评审页面；不写入游戏或正式资源。

【变更记录 #1】2026-10-23 17:06:43（候选制作，不增加模组修订）
删除：无。新增：累积继承证据、NBT/Sponge、实际模型纹理、主控近景和待审页面。
修改：复用公共导出器与既有技能适配器；部署条件采用负责人最新五台先装2.9决定。
用途：使外观候选可以直接审阅，并区分结构文件、真实机器与升级兼容性。
"""
import base64
import collections
import datetime as dt
import gzip
import hashlib
import html
import io
import json
import shutil
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from build_i20_qsv_second_unit_v1 import OUT, LOG, ROOT, NAME, BASE, W, H, D, STATES, QSV, build
from build_i19_hbv_coastal_station_v3 import INSTANCE
from build_redesign69 import export, render
from build_i09_i13_redesign_v6 import lodestone_export
from build_i18_hbv_fuel_rod_encapsulation_v1 import stage_evidence
from build_integration_revision_20261023 import access
from review_controller_integration_20261023 import front_image
from material_resources import Resources


def save(path, value): path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def images(data, materials):
    render(data, materials, OUT/'i20')
    print('等轴图完成', flush=True)
    colors = {}
    for m in materials:
        pic = Image.open(io.BytesIO(base64.b64decode(m['faces']['up'].split(',')[1]))).convert('RGB')
        colors[m['state']] = tuple(np.array(pic).mean(axis=(0, 1)).astype(int))
    image = Image.new('RGB', (W*5, D*5), '#132033')
    draw = ImageDraw.Draw(image)
    for b in data['blocks']:
        x, y, z = b['pos']; draw.rectangle((x*5, z*5, x*5+4, z*5+4), fill=colors[b['state']])
    draw.line((135*5+2, 0, 135*5+2, D*5), fill='#ffde78', width=2)
    x, y, z = data['controller']; draw.ellipse((x*5-7, z*5-7, x*5+12, z*5+12), outline='#fff5b6', width=3)
    image.save(OUT/'俯视布局.png')
    north = front_image(data, materials); north.save(OUT/'北立面定位.png')
    # 从新控制厅自身北面绘制，避免旧核岛在全厂投影中遮挡主控；不更改交付体素。
    local = {**data, 'blocks': [b for b in data['blocks'] if 108 <= b['pos'][0] <= 171 and b['pos'][2] >= 184]}
    front = front_image(local, materials)
    crop = front.crop((35+119*14, 65+(H-1-13)*14, 35+152*14, 65+H*14))
    crop.resize((crop.width*2, crop.height*2), Image.Resampling.NEAREST).save(OUT/'主控近景.png')
    cut = {**data, 'blocks': [b for b in data['blocks'] if b['pos'][1] <= 18 and not
            (b['pos'][1] > 2 and (b['pos'][2] in (184, 222) or b['pos'][0] in (108, 171, 175, 264)))]}
    temp = LOG/'cut-render'; temp.mkdir(exist_ok=True)
    render(cut, materials, temp); shutil.copy2(temp/'等轴预览.png', OUT/'内部剖切.png')
    print('俯视、主控和剖切图完成', flush=True)


def index(data, audit):
    counts = audit['palette']
    rows = ''.join('<tr><td><code>'+html.escape(s)+'</code></td><td>'+f'{n:,}'+'</td></tr>' for s, n in counts.items())
    page = f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I20 中型崩坏能反应堆・双岛复合厂区</title>
<style>body{{margin:0;background:#11262c;color:#e3efef;font:16px/1.85 'Microsoft YaHei',sans-serif}}main{{max-width:1280px;padding:30px;margin:auto}}header{{background:#23464b;border-left:5px solid #83b6bd;padding:25px}}h1{{margin:0}}a{{color:#a4dce4}}img{{max-width:100%}}.facts{{display:flex;gap:24px;flex-wrap:wrap}}.notice{{padding:15px;background:#3a3828;border-left:4px solid #d8c384}}iframe{{width:100%;height:850px;border:1px solid #4d7279}}td,th{{padding:8px;border-bottom:1px solid #47616a;text-align:left}}table{{border-collapse:collapse;width:100%}}code{{overflow-wrap:anywhere}}small{{color:#b6ccd0}}</style>
<main><header><small>HK3GTL / I20 / 累积扩建候选 V1</small><h1>中型崩坏能反应堆 · 双岛复合厂区</h1><p>保留HBV旧机组，新增QSV圆顶核岛、第二冷却塔和透平设备，联合仪控嵌入真实厂房。</p></header>
<div class="facts"><p>宽×深×高 <b>271×223×155</b></p><p>实体 <b>{data['block_count']:,}</b></p><p>保留I19 <b>256,075块</b></p><p>新增 <b>{audit['geometry']['inheritance']['added_blocks']:,}块</b></p></div>
<p class="notice"><b>待用户审阅，未写入正式资源或实例。</b>最新决定已恢复五台一批先实装2.9，负责人升级后再核验2.9.2。目前I14–I18五台已在2.9安装修订175；没有新的未实装五台。本候选不自动算作批准。</p>
<p><a href="i20/三维评审.html">打开三维评审</a> · <a href="i20/三维评审.html?view=controller">定位主控</a> · <a href="i20/{NAME}.nbt">NBT</a> · <a href="i20/{NAME}.schem">Schematic</a> · <a href="../{OUT.name}.zip">完整ZIP</a></p>
<p>主控 <b>[135,3,184]</b>，整宽第136格，朝北；嵌在39格深的联合仪控厅实墙，背后连接室内仪控工位。旧I19主控[95,3,20]与8个接口全部保留；新增8个接口分布在燃料热室、泵房和透平送出设备，不另立面板或托接口柱。</p>
<img src="i20/等轴预览.png" alt="I20实际纹理等轴图"><iframe src="i20/三维评审.html" title="I20三维评审"></iframe>
<h2>在旧机组旁形成第二套完整工艺</h2><p>西侧旧厂区完整保留原位与原色；东侧新敞口塔采用更高的收腰壳体、透空支腿、独立集水与布水环。圆顶核岛内置厚壁反应器和换热设备，与旧方舱核岛形成轮廓差异。燃料热室通过封闭转运桥进入屏蔽区；泵房与塔底、核岛形成错层冷却管廊。南侧三段透平厅及联合仪控通过实体通廊相连，电力接口融入透平厅侧壁的送出设备。</p>
<p>271×155×223（XYZ）逐轴高于旧目标270×154×222一格，为待审设计选择；宽度采用奇数以获得唯一中线。原I19 256,075块全部逐格状态相同，删除0、异材覆盖0，原维护道及燃料接口东侧通道保留。</p>
<p><a href="俯视布局.png">俯视布局与整宽中心线</a> · <a href="内部剖切.png">内部设备剖切</a> · <a href="i20/设计与检查.json">全部接口坐标及检查</a></p>
<h2>居中主控近景</h2><p>以下视图从新仪控厅北墙观察，隐藏前方旧核岛以看清墙面；交付结构本身没有删改。</p><img src="主控近景.png" alt="主控嵌入QSV仪控厅实墙近景"><p><a href="北立面定位.png">全厂北立面</a></p>
<h2>电压、材料与实际能力</h2><p>QSV为既定映射，新增主体采用现有QSV叠态压机械方块，旧HBV保留。QSV主材源码路线为HDV阶段的导网层、介质层、压合、表面分选和板材成形，再以8同级板合成机壳；RN-MCE/RN-SSQ研究仍为provisional，完整生存首建尚未验收。GT辅助材料复用当前2.9资源和既有有效配方快照，未假称2.9.2已核验。</p>
<p>I20目前只有一条暂定能源计划，尚无绑定真实I20控制器/Pattern的可执行配方；15条独立燃料工艺、真实仓室结算、热管理、发电生命周期和生存研究仍待实现/验收。管线与设备是建筑表达，接口仍是无功能位置标记。</p>
<p>普通建材实际占比：{html.escape('；'.join(k+' '+str(v)+'（'+str(audit['namespace_percent'][k])+'%）' for k,v in audit['namespace_counts'].items()))}；原版普通建材零。钻石与接口标记单列。<a href="材料阶段依据.json">材料阶段依据</a> · <a href="资源来源.json">实际模型纹理来源</a> · <a href="verification.json">检查及未验收范围</a></p><table><tr><th>实际方块ID</th><th>用量</th></tr>{rows}</table>
<p>原点/粘贴锚点[0,0,0]；Schematic Offset零；建议底部世界Y=-60，最高Y=94。结构文件留在项目交付目录。</p><p>本地file三维页的浏览器自动化此前受协议安全策略阻止，本轮未绕过；真实材质静态图已生成，三维交互未自动验收。</p>
<small>变更记录 #1：{audit['time']}；新增I20待审候选、累积继承与新部署顺序说明。正式机器、配方、实例文件未修改。</small></main></html>'''
    (OUT/'index.html').write_text(page, encoding='utf-8')


def main():
    OUT.mkdir(parents=True, exist_ok=True); LOG.mkdir(parents=True, exist_ok=True)
    folder = OUT/'i20'; folder.mkdir(exist_ok=True)
    data, geometry = build()
    (folder/'blueprint.json').write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    save(LOG/'geometry-preview.json', geometry)
    resources = Resources(INSTANCE, project_resources=ROOT/'src/main/resources')
    try:
        materials = [resources.material(s) for s in sorted({b['state'] for b in data['blocks']})]
        sources = dict(resources.sources)
    finally: resources.close()
    assert all(m['complete_cube'] for m in materials)
    images(data, materials)
    reaches = access(data)
    save(LOG/'static-access.json', reaches)
    assert all(p['front_clear'] and p['backing_solid'] and p['walk_access'] for p in reaches), reaches
    states, groups, hashes = export(data, folder)
    print('NBT和Sponge全量回读完成', flush=True)
    hashes['nbt'] = lodestone_export(data, folder, LOG)
    print('技能NBT导出并逐格回读完成', flush=True)
    counts = collections.Counter(b['state'] for b in data['blocks'])
    markers = ('minecraft:diamond_block', 'hk3gtl:industrial_port_casing')
    namespaces = collections.Counter(b['state'].split(':')[0] for b in data['blocks'] if b['state'] not in markers)
    old = json.loads(BASE.read_text(encoding='utf-8'))
    old_counts = collections.Counter(b['state'] for b in old['blocks'])
    now = dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat()
    audit = {'time': now, 'hashes': hashes, 'palette': dict(counts), 'new_stage_palette': dict(counts-old_counts),
             'namespace_counts': dict(namespaces), 'namespace_percent': {k: round(100*v/sum(namespaces.values()), 2) for k,v in namespaces.items()},
             'markers': {s: counts[s] for s in markers}, 'target_voltage': 'QSV19新增主体；HBV15旧区保留',
             'minimum_executable_recipe_voltage': None, 'geometry': geometry, 'access': reaches,
             'approval': '待用户审批，不计入已批准批次', 'deployment_eligible': False,
             'deployment_policy': '累计五台明确批准后先实装2.9；负责人升级后验证2.9.2，发现实际问题再修改。',
             'resource_environment': '增强版2.9既有资源只读，2.9.2尚未核验',
             'checks': ['全部实际模型为完整立方体', 'NBT/Sponge含空气逐格一致', '主控位于整宽第136格',
                        'I19全部原块原色继承，删除及异材覆盖为零', '双塔喉口与敞口保留空气',
                        '六面连通、六条新旧维护道净空', '主控及16接口有正面净空、背接和静态步行操作位'],
             'not_verified': ['用户外观批准', '完整材料祖先链、研究及生存首建', 'I20控制器/Pattern与真实能源功能',
                              '游戏内成型运行和多人验收', '2.9.2兼容性', '本地file三维页面的浏览器自动交互']}
    save(OUT/'verification.json', audit)
    save(OUT/'资源来源.json', sources)
    evidence = stage_evidence()
    evidence['qsv_audit'] = '评审依据/material-tooling-audit.json'
    evidence['current_boundary'] = audit['resource_environment']
    evidence['ordinary_materials'] = [{'state': s, 'count': counts[s], 'full_cube': True,
                                       'stage': '原HBV或新增QSV目标；生存祖先链与研究未验收',
                                       'effective_recipe_evidence': evidence['materials'].get(s)} for s in states if s not in markers]
    save(OUT/'材料阶段依据.json', evidence)
    meta = {k:v for k,v in data.items() if k != 'blocks'}
    save(folder/'设计与检查.json', {'data': meta, 'audit': audit})
    payload = {'data': meta, 'palette': states, 'groups': groups, 'materials': materials, 'audit': audit, 'names': {}}
    packed = base64.b64encode(gzip.compress(json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), 9)).decode('ascii')
    (folder/'data.js').write_text('/* I20累积扩建候选；标记不代表真实能源功能。 */\nwindow.HK3_PAYLOAD='+json.dumps(packed)+';', encoding='utf-8')
    subprocess.run(['node', str(ROOT/'tools/structure_delivery/package_integration_review.mjs'), str(OUT), '累积扩建V1・待审'], check=True)
    page = folder/'三维评审.html'
    page.write_text(page.read_text(encoding='utf-8').replace('全部21形态', 'I20交付总览').replace('href="../index.html#i20"', 'href="../index.html"'), encoding='utf-8')
    save(OUT/'manifest.json', {**meta, 'generated_at': now, 'hashes': hashes, 'verification': geometry, 'approval': audit['approval']})
    index(data, audit)
    scripts = OUT/'生成脚本'; scripts.mkdir(exist_ok=True)
    for source in (ROOT/'tools/structure_delivery/build_i20_qsv_second_unit_v1.py', ROOT/'tools/structure_delivery/package_i20_qsv_candidate_20261023.py'):
        shutil.copy2(source, scripts/source.name)
    shutil.copy2(ROOT/'tools/structure_delivery/package_integration_review.mjs', scripts/'package_integration_review.mjs')
    shutil.copy2(Path.home()/'.codex/skills/minecraft-builder-skill/node_modules/three/LICENSE', OUT/'Three许可.txt')
    print(json.dumps({'blocks': data['block_count'], 'hashes': hashes, 'controller': data['controller'], 'access_passed': len(reaches)}, ensure_ascii=False), flush=True)


if __name__ == '__main__': main()

