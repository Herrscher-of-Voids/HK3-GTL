# -*- coding: utf-8 -*-
"""I20候选同源导出、真实材质视图和评审页面；不写入游戏或正式资源。

【变更记录 #1】2026-10-23 17:06:43（候选制作，不增加模组修订）
删除：无。新增：累积继承证据、NBT/Sponge、实际模型纹理、主控近景和待审页面。
修改：复用公共导出器与既有技能适配器；部署条件采用负责人最新五台先装2.9决定。
用途：使外观候选可以直接审阅，并区分结构文件、真实机器与升级兼容性。
【变更记录 #2】2026-10-23 19:41:07（I20原位主控修订V2）
删除：第136格新主控的页面定位和整宽中心线。新增：I19原位主控近景、空区A标注及用途缺口说明。
修改：导出V2同源数据；空区只说明真实原因，不擅自增加设施。用途：落实负责人对系列主控的纠正。
【变更记录 #3】2026-10-23 20:00:24（检修厂房及外围路V3）
删除：空区A仍待处理的当前说明。新增：检修厅近景与剖切、后退道路定位、工位静态可达性。
修改：同源导出尺寸271×155×233；用途：落实用户红圈指示，外围道路包住厂房，不改正式资源。
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

from build_i20_qsv_maintenance_v3 import OUT, LOG, ROOT, NAME, BASE, W, H, D, STATES, QSV, build
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
    draw.line((95*5+2, 0, 95*5+2, 174*5), fill='#ffde78', width=2)
    draw.rectangle((12*5, 186*5, 104*5-1, 221*5-1), outline='#f6a557', width=3)
    draw.rectangle((0, 228*5, W*5-1, D*5-1), outline='#90e3bd', width=3)
    draw.text((12*5, 190*5), 'A: 检修厂房', font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 25), fill='#f6b878')
    x, y, z = data['controller']; draw.ellipse((x*5-7, z*5-7, x*5+12, z*5+12), outline='#fff5b6', width=3)
    image.save(OUT/'俯视布局.png')
    north = front_image(data, materials); north.save(OUT/'北立面定位.png')
    # 绘制继承的I19主厂房北面，主控保持原位；不更改交付体素。
    local = {**data, 'blocks': [b for b in data['blocks'] if 72 <= b['pos'][0] <= 181 and 20 <= b['pos'][2] <= 72]}
    front = front_image(local, materials)
    crop = front.crop((35+79*14, 65+(H-1-13)*14, 35+112*14, 65+H*14))
    crop.resize((crop.width*2, crop.height*2), Image.Resampling.NEAREST).save(OUT/'主控近景.png')
    cut = {**data, 'blocks': [b for b in data['blocks'] if b['pos'][1] <= 18 and not
            (b['pos'][1] > 2 and (b['pos'][2] in (184, 222) or b['pos'][0] in (108, 171, 175, 264)))]}
    temp = LOG/'cut-render'; temp.mkdir(exist_ok=True)
    render(cut, materials, temp); shutil.copy2(temp/'等轴预览.png', OUT/'内部剖切.png')
    # 仅在近景中移去屋顶和近侧墙，展示吊车与检修设备；交付体素不变。
    local_blocks = [{'pos': [b['pos'][0]-6,b['pos'][1],b['pos'][2]-184], 'state': b['state']}
                    for b in data['blocks'] if 6 <= b['pos'][0] <= 108 and 184 <= b['pos'][2] <= 227]
    local = {**data, 'size': [103, 40, 44], 'blocks': local_blocks}
    temp = LOG/'workshop-render'; temp.mkdir(exist_ok=True)
    render(local, materials, temp); shutil.copy2(temp/'等轴预览.png', OUT/'检修厂房近景.png')
    local['blocks'] = [b for b in local_blocks if b['pos'][1] <= 28 and not
                       (b['pos'][1] > 2 and (b['pos'][0] <= 7 or b['pos'][2] <= 3))]
    render(local, materials, temp); shutil.copy2(temp/'等轴预览.png', OUT/'检修厂房剖切.png')
    print('俯视、主控与检修厂房内外视图完成', flush=True)


def index(data, audit):
    page = f"""<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I20 检修厂房与外围路修订V3</title>
<style>body{{margin:0;background:#11262c;color:#e3efef;font:16px/1.85 'Microsoft YaHei',sans-serif}}main{{max-width:1280px;padding:30px;margin:auto}}header{{background:#23464b;border-left:5px solid #83b6bd;padding:25px}}h1{{margin:0}}a{{color:#a4dce4}}img{{max-width:100%}}.notice{{padding:15px;background:#3a3828;border-left:4px solid #d8c384}}iframe{{width:100%;height:850px;border:1px solid #4d7279}}code{{overflow-wrap:anywhere}}small{{color:#b6ccd0}}</style>
<main><header><small>HK3GTL / I20 / 建筑候选 V3</small><h1>中型崩坏能反应堆 · 检修厂房与完整外围路</h1><p>原西南空区补齐检修厂房；南侧外围路退至全部厂房之后。主控保留I19原位。</p></header>
<p>宽×深×高 <b>{W}×{D}×{H}</b> · 实体 <b>{data['block_count']:,}</b> · I19原位原状态保留 <b>256,075块</b> · 主控 <b>[95,3,20]朝北</b> · 接口 <b>16口原位</b></p>
<p class="notice">本版是依据本轮修改要求制作的新候选，尚未获得整版外观批准，未写入正式资源或游戏实例。满五台明确批准后先装2.9；负责人升级后再验证2.9.2兼容性。</p>
<p><a href="i20/三维评审.html">打开三维评审</a> · <a href="i20/三维评审.html?view=controller">原位主控</a> · <a href="i20/{NAME}.nbt">NBT</a> · <a href="i20/{NAME}.schem">Schematic</a> · <a href="../{OUT.name}.zip">完整ZIP</a></p>
<h2>红圈所指的南侧外围路</h2><p>原道路位于Z218–222，与厂房后部投影重叠。现向南后退10格至Z228–232，东西两侧道路同步接长并转角闭合。原厂房最南后墙为Z222，墙外Z223–227连续留出5格宽维护带，外围路完整包住检修厅、仪控厅与透平厅。厂房原坐标不动。</p><p>俯视图橙框A是新增检修厂房；绿色框是后退后的南侧道路。深度由223增至233格，来自有用途的道路与维护空间。</p><img src="俯视布局.png" alt="检修厂房与完整外围路实际俯视图">
<h2>把空区变成有内容的检修厂房</h2><p>厂房本体X12–103、Z186–220，宽92格、深35格，最高屋顶Y37。QSV机壳组成低拱连续屋面与门式框架，双条天窗采光；北侧两个卸件门洞接联合检修路，东侧实体连廊接仪控厅，南侧留完整后墙外维护带。</p><p>内部包括由立柱和连续轨梁承托的桥式吊车、中央拆装床、三组待修泵转子与后墙备件架；北侧卸件通廊、中央工位通道和后侧通道保持净空。没有新增控制器或接口，也没有为填空堆实心方块。</p><img src="检修厂房近景.png" alt="QSV检修厂房实际材质近景"><p>以下剖切仅在视图中隐藏屋顶及近侧墙，展示设备和承重关系；NBT与Schematic保留完整厂房。</p><img src="检修厂房剖切.png" alt="吊车检修工位与备件架剖切">
<h2>整体与主控</h2><img src="i20/等轴预览.png" alt="V3全厂实际方块纹理预览"><iframe src="i20/三维评审.html" title="I20 V3三维评审"></iframe><p>主控继续使用I19原宽191的第96格[95,3,20]，嵌原主厂房北墙。新增厅没有第二主控；I19全部原方块原色及16个接口均保留。</p><img src="主控近景.png" alt="I19原位主控"><p><a href="内部剖切.png">整体低位剖切</a> · <a href="北立面定位.png">北立面</a> · <a href="i20/设计与检查.json">接口坐标与检查</a></p>
<h2>材料与验证边界</h2><p>沿用当前实际资源核对过的完整立方体：QSV阶段新增主体采用QSV机壳，原HBV部分不刷色；辅助材料使用GT机壳、完整管道外壳、格栅、齿轮箱及玻璃，没有新增方块ID。普通建材按实际用量统计：{html.escape('；'.join(k+' '+str(v)+'块（'+str(audit['namespace_percent'][k])+'%）' for k,v in audit['namespace_counts'].items()))}；普通原版建材为零。钻石核心3块与接口标记16块单列。</p>
<p>几何、通道、导出逐格回读与静态步行检查分别记录；吊车、检修设备与管线属于建筑表达，不代表已有可执行检修配方。I20真实控制器/Pattern、能源工艺、完整材料祖先链、RN-MCE/RN-SSQ研究与生存首建尚未验收；没有验证2.9.2运行或本地file页面自动交互。</p>
<p><a href="verification.json">本版检查</a> · <a href="材料阶段依据.json">材料阶段依据</a> · <a href="资源来源.json">实际模型纹理来源</a></p><p>XYZ尺寸271×155×233；原点/粘贴锚点[0,0,0]，Offset零；建议底部世界Y=-60，最高Y=94。</p><small>变更#3：{audit['time']}；新增检修厂房及内部设备，南路后退10格并闭合外围，I19与原位主控保持。候选制作未修改正式资源或实例。</small></main></html>"""
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
             'checks': ['全部实际模型为完整立方体', 'NBT/Sponge含空气逐格一致', '主控继承I19[95,3,20]朝北，扩建厅不另设主控',
                        'I19全部原块原色继承，删除及异材覆盖为零', '双塔喉口与敞口保留空气',
                        '单一六面连通、十三条通道净空、外围路包住全部厂房', '主控及16接口有正面净空、背接和静态步行操作位'],
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
    subprocess.run(['node', str(ROOT/'tools/structure_delivery/package_integration_review.mjs'), str(OUT), '检修厂房与外围路V3・待审'], check=True)
    page = folder/'三维评审.html'
    page.write_text(page.read_text(encoding='utf-8').replace('全部21形态', 'I20交付总览').replace('href="../index.html#i20"', 'href="../index.html"'), encoding='utf-8')
    save(OUT/'manifest.json', {**meta, 'generated_at': now, 'hashes': hashes, 'verification': geometry, 'approval': audit['approval']})
    index(data, audit)
    scripts = OUT/'生成脚本'; scripts.mkdir(exist_ok=True)
    for source in (ROOT/'tools/structure_delivery/build_i20_qsv_second_unit_v1.py', ROOT/'tools/structure_delivery/build_i20_qsv_inherited_controller_v2.py', ROOT/'tools/structure_delivery/build_i20_qsv_maintenance_v3.py', ROOT/'tools/structure_delivery/package_i20_qsv_candidate_v3_20261023.py'):
        shutil.copy2(source, scripts/source.name)
    shutil.copy2(ROOT/'tools/structure_delivery/package_integration_review.mjs', scripts/'package_integration_review.mjs')
    shutil.copy2(Path.home()/'.codex/skills/minecraft-builder-skill/node_modules/three/LICENSE', OUT/'Three许可.txt')
    print(json.dumps({'blocks': data['block_count'], 'hashes': hashes, 'controller': data['controller'], 'access_passed': len(reaches)}, ensure_ascii=False), flush=True)


if __name__ == '__main__': main()

