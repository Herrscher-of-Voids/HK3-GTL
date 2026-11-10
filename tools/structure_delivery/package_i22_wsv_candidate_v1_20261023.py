# -*- coding: utf-8 -*-
"""I22建筑候选的只读资源核对、真实纹理图、技能NBT与离线交付页面。

【变更记录 #1】2026-10-23 21:38:00（I22候选打包，不增加模组修订号）
删除：无。新增：I21全厂逐格继承保护、WSV材料依据、六室冷凝/四堆隔离/六列透平视图和完整结构导出。
修改：打包入口改为动态调用I22最新build结果，所有输出只写I22目录和I22日志。
用途：交付可审阅的新候选，并把建筑设计、阶段闭环及游戏运行分开报告。

【变更记录 #2】2026-10-23（从已有缓存续作，不增加模组修订号）
删除：无。新增：--use-cache只读加载已生成的I22蓝图与几何记录，再生成导出与评审材料。
修改：默认构建流程不变；缓存模式不覆盖蓝图或几何记录。
用途：从用户指定的现有I22缓存继续完成候选包，并保留原始逐格内容。
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
import sys
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image,ImageDraw,ImageFont

from build_i22_wsv_ultimate_reactor_v1 import ROOT,OUT,LOG,BASE,BASE_SHA,NAME,W,H,D,build
from build_i19_hbv_coastal_station_v3 import INSTANCE
from build_redesign69 import export,render
from build_i09_i13_redesign_v6 import lodestone_export
from build_i18_hbv_fuel_rod_encapsulation_v1 import stage_evidence
from build_integration_revision_20261023 import access
from review_controller_integration_20261023 import front_image
from material_resources import Resources


def read(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def now():return dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat()


def checkpoint():
    OUT.mkdir(parents=True,exist_ok=True);LOG.mkdir(parents=True,exist_ok=True);(OUT/'i22').mkdir(exist_ok=True)
    if not (LOG/'protected-before.json').exists():
        prev_out=ROOT/'deliveries/I21_大型崩坏能反应堆_闭式三回路联合厂区候选_V1_20261023'
        prev_zip=prev_out.with_suffix('.zip')
        paths=set(p for p in prev_out.rglob('*') if p.is_file())
        paths.add(prev_zip)
        prior_protection=ROOT/'logs/i21-imv-cogeneration-v1-20261023/protected-before.json'
        if prior_protection.exists():
            paths.update(Path(p) for p in read(prior_protection)['files'])
        paths.add(BASE)
        save(LOG/'protected-before.json',{'time':now(),'files':{str(p):sha(p) for p in sorted(paths)}})
        names=['rules.md','系统角色设定.md','崩坏三-gtl (hk3gtl) 项目规则.md','hk3gtl java文件变更备注规范.md','当前多方块设计规则.md','巨构提示词.txt']
        save(LOG/'rules-read.json',{'recorded_at':now(),'read_in_this_turn':True,'read_time_range_hk':'2026-10-23 22:23–22:27',
             'files':{n:sha(ROOT/'rule'/n) for n in names},'context_gatherer':'当前工具未提供，以实际本地读取替代。',
             'skill':'C:/Users/OWNER/.codex/skills/minecraft-builder-skill/SKILL.md',
             'latest_discussion':'本轮用户原话为“下一台吧”；I21全厂快照与当前I22结构脚本由本地文件读取。'})
    assert sha(BASE)==BASE_SHA


def resources_for(data):
    r=Resources(INSTANCE,project_resources=ROOT/'src/main/resources')
    try:
        mats=[r.material(s) for s in sorted({b['state'] for b in data['blocks']})]
        sources=dict(r.sources)
    finally:r.close()
    assert all(m['complete_cube'] for m in mats)
    jars=list((INSTANCE/'mods').glob('*hk3gtl*.jar'));assert len(jars)==1,jars
    # 项目资源只用于同一字节来源；不以项目未安装材质代替实际实例。
    with zipfile.ZipFile(jars[0]) as jar:
        matches={}
        for rel,source in sources.items():
            if rel.startswith('assets/hk3gtl/'):
                installed=jar.read(rel);actual=Path(source).read_bytes() if '!/' not in source else installed
                assert installed==actual,rel
                matches[rel]=hashlib.sha256(installed).hexdigest()
    meta=INSTANCE.parent/'mrpack/modrinth.index.json';pack=read(meta)
    identity={'time':now(),'instance':str(INSTANCE),'pack_version':pack['versionId'],'pack_metadata_sha256':sha(meta),
              'hk3gtl_jar':str(jars[0]),'hk3gtl_jar_sha256':sha(jars[0]),'hk_assets_byte_match':matches,
              'full_cube_materials':len(mats),'browser_interaction_verified':False}
    save(OUT/'资源来源.json',{'identity':identity,'sources':sources})
    save(LOG/'materials.json',mats)
    return mats,identity


def local_render(data,materials,lo,hi,name,cut_y=None):
    x0,y0,z0=lo;x1,y1,z1=hi
    blocks=[{'pos':[b['pos'][0]-x0,b['pos'][1]-y0,b['pos'][2]-z0],'state':b['state']}
            for b in data['blocks'] if all(lo[i]<=b['pos'][i]<=hi[i] for i in range(3)) and
            (cut_y is None or (b['pos'][1]<=cut_y and not (b['pos'][1]>2 and (b['pos'][0]==x0 or b['pos'][2]==z0))))]
    local={**data,'size':[x1-x0+1,y1-y0+1,z1-z0+1],'blocks':blocks}
    dest=LOG/name;dest.mkdir(exist_ok=True);render(local,materials,dest)
    shutil.copy2(dest/'等轴预览.png',OUT/(name+'.png'))


def images(data,materials):
    render(data,materials,OUT/'i22');print('全厂等轴图完成',flush=True)
    colors={}
    for m in materials:
        im=Image.open(io.BytesIO(base64.b64decode(m['faces']['up'].split(',')[1]))).convert('RGB')
        colors[m['state']]=tuple(np.array(im).mean(axis=(0,1)).astype(int))
    im=Image.new('RGB',(W*5,D*5),'#172434');draw=ImageDraw.Draw(im)
    for b in data['blocks']:
        x,y,z=b['pos'];draw.rectangle((x*5,z*5,x*5+4,z*5+4),fill=colors[b['state']])
    font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',20)
    for text,rect in [('WSV环箍四堆塔',(332,10,396,150)),('六室冷凝阵列',(335,183,392,255)),('稳界蓄能器',(333,256,393,280)),
                      ('WSV燃料轮换厅',(12,296,133,333)),('六列协同透平厅',(140,296,394,333))]:
        x0,z0,x1,z1=rect;draw.rectangle((x0*5,z0*5,x1*5+4,z1*5+4),outline='#f0ba6c',width=3)
        draw.text((x0*5+6,z0*5+7),text,font=font,fill='#fff1c8')
    draw.rectangle((0,341*5,W*5-1,D*5-1),outline='#9be0b0',width=3)
    draw.rectangle((397*5,0,W*5-1,D*5-1),outline='#9be0b0',width=3)
    draw.line((95*5,0,95*5,285*5),fill='#ffe17b',width=2)
    draw.ellipse((95*5-7,20*5-7,95*5+10,20*5+10),outline='#fff0ae',width=3)
    draw.line((0,285*5,W*5-1,285*5),fill='#ffe17b',width=2)
    im.save(OUT/'俯视布局.png')
    local={**data,'blocks':[b for b in data['blocks'] if 72<=b['pos'][0]<=181 and 20<=b['pos'][2]<=72]}
    north=front_image(local,materials)
    crop=north.crop((35+79*14,65+(H-1-13)*14,35+112*14,65+H*14))
    crop.resize((crop.width*2,crop.height*2),Image.Resampling.NEAREST).save(OUT/'原位主控.png')
    local_render(data,materials,(326,0,0),(401,249,280),'WSV北东扩建全景')
    local_render(data,materials,(332,0,35),(396,249,125),'环箍四堆塔内部',125)
    local_render(data,materials,(335,0,183),(392,47,255),'六室冷凝阵列内部',30)
    local_render(data,materials,(12,0,296),(133,42,333),'燃料轮换厅内部',30)
    local_render(data,materials,(140,0,296),(394,58,333),'六列透平厅内部',35)
    print('布局、原位主控和新增设备内外图完成',flush=True)


def stage_materials(counts):
    evidence=stage_evidence()
    paths=['src/main/java/com/sirin/hk3gtl/common/recipe/main/Hk3MainMaterialProductionUpper.java',
           'src/main/java/com/sirin/hk3gtl/common/recipe/main/Hk3MainMaterialFormRecipes.java',
           'src/main/java/com/sirin/hk3gtl/common/recipe/main/Hk3MainMaterialAccess.java',
           'src/main/java/com/sirin/hk3gtl/common/recipe/main/Hk3MainMaterialProductionLower.java',
           'src/main/java/com/sirin/hk3gtl/common/recipe/machine/Hk3VoltageCasingRecipes.java',
           'src/main/resources/data/hk3gtl/research/research_execution.json',
           'doc/HK3GTL-内测5/02_工业计划/工业网络扩展雏形_v6.json',
           'doc/HK3GTL-内测5/02_工业计划/多方块结构电压映射提案_v1.html']
    evidence.update(time=now(),target='WSV V14新增主体，HBV V1/QSV V5/IMV V9前阶段原样继承',
       wsv_route='WFV27锭16+纳米陶瓷64+PBI18432→一级稳界坯16；WFV箔32成形→二级16；冷媒16000疲劳处理→三级16并回收热冷媒；氩气16000质量复核→14坯+2废；成形压机8坯→8外圈板；8板→WSV稳界约束壳材1。',
       power_boundary='WSV V14为多方块阶段电压映射，WSV主材首制链使用WFV前阶材料；industrial_reactor_i22数据工单另列energy_tier=28且provisional=true，不代表已可运行。',
       research_boundary='WSV材料路线绑定RN-WME与RN-WMS；RN-URE执行链及生存首建仍未验收，不能称为已闭环。',
       i22_contract={'source_count':1,'provisional':True,'executor_verified':False,
                     'duties':['奇观级持续供能','多机组协同与隔离','大功率冷却与降载','长周期燃料核验及乏棒交付'],
                     'boundary':'无获批EU/HKE转换；建筑不新增转换、配方或运行能力。'},
       source_hashes={p:sha(ROOT/p) for p in paths},
       ordinary_materials=[{'id':s,'count':n,'stage_evidence':evidence['materials'].get(s),
                           'status':'实际完整方块及已有来源已核对，全部前置与生存阶段未完整验收'}
                           for s,n in counts.items() if s not in ('minecraft:diamond_block','hk3gtl:industrial_port_casing')])
    save(OUT/'材料阶段依据.json',evidence)


def index(data,audit):
    added=audit['geometry']['inheritance']['added_blocks']
    core_count=audit['markers']['minecraft:diamond_block']
    page=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I22 究极崩坏能反应堆 · WSV协同厂区候选</title>
<style>body{{margin:0;background:#14212d;color:#e5edf3;font:16px/1.85 'Microsoft YaHei',sans-serif}}main{{max-width:1320px;margin:auto;padding:30px}}header{{padding:26px;background:#303954;border-left:5px solid #b7a5dc}}h1{{margin:0}}a{{color:#c3d7ff}}img{{max-width:100%;height:auto}}iframe{{width:100%;height:850px;border:1px solid #69718a}}.notice{{background:#3c3827;border-left:4px solid #d0b872;padding:15px}}code{{overflow-wrap:anywhere}}small{{color:#b9c3d1}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px}}.grid>div{{background:#202d3c;padding:12px;border:1px solid #405066}}</style>
<main><header><small>HK3GTL / I22 / 建筑候选V1</small><h1>究极崩坏能反应堆</h1><p>在HBV、QSV、IMV三阶段全厂基础上，扩建WSV文明工程级四腔约束堆塔、冷媒稳定与热管理区、燃料轮换厅和六列协同透平厅。</p></header>
<div class="grid"><div>尺寸 XYZ <b>{W} × {H} × {D}</b><br>即宽 {W} · 高 {H} · 深 {D}</div><div>实体方块 <b>{data['block_count']:,}</b><br>继承 I21 {audit['geometry']['inheritance']['retained_blocks']:,} · 新增 {added:,}</div><div>主控 <b>[95,3,20] 朝北</b><br>接口原24口 + 新10口 = 34口</div><div>钻石核心标记 <b>{core_count}</b><br>前阶段原4块 + I22新增4块</div></div>
<p class="notice">这是待审建筑候选，没有计入五台批准批次，也没有写入正式资源、配方或游戏实例。I22图纸表达不代表机器能力或已完成的生存材料链；负责人升级2.9.2后再单独做兼容性验证。</p>
<p><a href="i22/三维评审.html">打开三维评审</a> · <a href="i22/三维评审.html?view=controller">查看原位主控</a> · <a href="i22/{NAME}.nbt">NBT</a> · <a href="i22/{NAME}.schem">Sponge Schematic</a> · <a href="../{OUT.name}.zip">完整ZIP</a> · <a href="i22/设计与检查.json">设计与接口坐标</a></p>
<h2>四阶段累积扩建</h2><p>I22完全继承I21的{audit['geometry']['inheritance']['retained_blocks']:,}个既有方块，原坐标、状态、颜色、控制器和24个接口保持原样。新增主体用WSV V14电压机壳，配合HBV V1、QSV V5、IMV V9前阶段机壳，四种阶段颜色都保留；新机壳用量 <b>{audit['geometry']['new_stage_palette']['hk3gtl:voltage_machine_casing_wsv']:,}</b> 块。</p>
<img src="俯视布局.png" alt="I22全厂实际方块俯视布局"><h2>新增设备区</h2><p>主塔以双层约束环箍围住四个独立承压腔，竖向约束肋、检修底座与顶部收束结构构成连续设备体；南侧布置六室冷凝阵列和两台稳界冷媒蓄能器，燃料轮换厅内设四组转运床与搬运梁，协同透平厅设置六列机组及一体端壳。结构中的管线以完整方块连接到具体泵、换热室、燃料缓冲箱或透平端壳。</p>
<p>外围新南路位于Z341–345，东路位于X397–401；旧I21道路保留。新增后墙外维护带位于Z334–340，厂房前侧装卸道及设备区净空见布局图和通道审计。接口都贴在泵组、燃料设备或透平端壳上，不另外搭面板或托柱。</p>
<img src="i22/等轴预览.png" alt="四阶段全厂真实材质等轴预览"><iframe src="i22/三维评审.html" title="I22三维评审"></iframe>
<h2>内部视图</h2><p>以下剖切视图仅在图片中隐藏屋顶或近侧墙以展示设备；蓝图、NBT、Schematic和三维数据保留完整外围结构。</p><img src="WSV北东扩建全景.png" alt="WSV北东扩建全景"><img src="环箍四堆塔内部.png" alt="四腔环箍屏蔽堆塔内部"><img src="六室冷凝阵列内部.png" alt="六室冷凝阵列内部"><img src="燃料轮换厅内部.png" alt="燃料轮换厅内部"><img src="六列透平厅内部.png" alt="六列协同透平厅内部"><h2>崩坏能反应堆系列主控</h2><p>主控沿用I19锚点[95,3,20]、朝北，没有随总宽重新居中或另设第二主控。新增的C7/C8为冷却回路计划接口，F7/F8为燃料轮换计划接口，E13–E18为六列电能输出计划接口；均为位置标记，操作面有静态净空和可达路径。具体坐标、朝向和用途见设计与检查文件。</p><img src="原位主控.png" alt="继承的主控位置"><h2>资源、配方与运行边界</h2><p>所有普通建材按当前HK实例模型和纹理核对，且为完整立方体。WSV约束壳源码链使用WFV阶段坯料、纳米陶瓷、PBI、WSV箔、冷媒疲劳处理与氩气终检；该材料路线的祖先材料、研究门槛与生存首建仍未完整验收。数据中的I22动力工单输出电压等级28，但仍标记为 provisional；它不是WSV V14电压机壳阶段的同义词，也不构成已运行的配方。</p>
<p>本轮只交付结构、静态接口/通道验证和离线审阅文件。真实I22 Pattern、控制器能力、负载调度、热排流、乏棒处理、游戏内成型/运行及2.9.2兼容性均未验收。</p><p><a href="verification.json">验证记录</a> · <a href="材料阶段依据.json">材料阶段依据</a> · <a href="资源来源.json">实际资源来源</a>。粘贴原点与Schematic Offset为[0,0,0]；建议底部世界Y=-60，顶部Y=189。file://页面的自动三维交互未在浏览器中验收。</p><small>候选V1 · {audit['time']}：新增WSV V14建筑阶段；前阶段零删除零替换，不修改正式资源、版本修订或实例。</small></main></html>'''
    design_note='<div class="notice"><b>与内测5造型方向的差异，待用户审阅</b><p>内测5 2026-10-20 22:10的最新文字方向为贯穿多层环形检修层的阶梯八角主塔，外围包含不同高度冷却塔、不对称辅助殿、管廊和分格水池。当前缓存V1将其重新诠释为环箍四腔主塔、六室冷凝阵列、燃料轮换厅、六列透平厅和稳界蓄能器；没有独立呈现传统塔形冷却塔、分格水池或隔离廊。该造型差异尚未获用户确认，需按候选审阅。</p></div>'
    page=page.replace('<h2>四阶段累积扩建</h2>',design_note+'<h2>四阶段累积扩建</h2>')
    (OUT/'index.html').write_text(page,encoding='utf-8')


def main():
    checkpoint();folder=OUT/'i22'
    receipt=read(LOG/'rules-read.json')
    receipt.update(latest_discussion='本轮用户原话为“帮我继续写i22，你应该会找到项目里有这玩意的缓存”；续作来源为项目内现有I22蓝图缓存。')
    save(LOG/'rules-read.json',receipt)
    if '--use-cache' in sys.argv:
        data=read(folder/'blueprint.json');geometry=read(LOG/'geometry-preview.json')
        assert data['name']==NAME and data['size']==[W,H,D] and data['block_count']==len(data['blocks'])
        assert geometry['user_target_xyz']==[W,H,D] and geometry['inheritance']['source_sha256']==BASE_SHA
    else:
        data,geometry=build()
        (folder/'blueprint.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
        save(LOG/'geometry-preview.json',geometry)
    mats,identity=resources_for(data)
    if '--export' not in sys.argv or '--refresh-images' in sys.argv:images(data,mats)
    if '--export' not in sys.argv:return
    reaches=access(data);save(LOG/'static-access.json',reaches)
    assert all(p['front_clear'] and p['backing_solid'] and p['walk_access'] for p in reaches),reaches
    print('主控及34接口静态步行可达',flush=True)
    states,groups,hashes=export(data,folder);print('NBT/Sponge含空气全量回读完成',flush=True)
    hashes['nbt']=lodestone_export(data,folder,LOG);print('技能NBT同源导出回读完成',flush=True)
    counts=collections.Counter(b['state'] for b in data['blocks']);markers=('minecraft:diamond_block','hk3gtl:industrial_port_casing')
    ns=collections.Counter(b['state'].split(':')[0] for b in data['blocks'] if b['state'] not in markers)
    audit={'time':now(),'hashes':hashes,'palette':dict(counts),'geometry':geometry,'access':reaches,
           'namespace_counts':dict(ns),'namespace_percent':{k:round(v*100/sum(ns.values()),2) for k,v in ns.items()},
           'markers':{k:counts[k] for k in markers},'target_voltage':'WSV V14新增主体，HBV V1/QSV V5/IMV V9继承',
           'minimum_executable_recipe_voltage':None,'resource_identity':identity,
           'approval':'待用户审批；不计入五台批准批次','deployment_eligible':False,
           'checks':['I21全部839950块原位原状态','主控及旧24口原位；新增10口嵌设备本体','单一六面连通，27条声明通道净空',
                     '全部使用完整立方体，安装HK资源逐字节一致','NBT/Sponge含空气逐格一致，技能NBT全量回读','主控/24口有净空背接与静态步行操作位'],
           'not_verified':['整版外观批准','完整材料祖先链、RN-WME/RN-WMS/RN-URE研究与生存首建','I22控制器/Pattern、能源功能与实际端口',
                           '游戏内成型/运行和2.9.2兼容性','本地file三维页面自动交互']}
    audit['design_alignment']={'status':'候选重新诠释，待用户审阅；未获外观批准',
       'reference':'doc/HK3GTL-内测5/讨论记录/2026-10-20_22-10-02_I19-I22独立重设计与模组结构参照.html',
       'reference_concept':'阶梯八角主塔与多层环形检修层；不同高度冷却塔、不对称辅助殿、管廊、分格水池。',
       'cached_candidate':'环箍四腔主塔、六室冷凝阵列、燃料轮换厅、六列透平厅、稳界蓄能器。',
       'differences':['没有独立呈现传统塔形冷却塔','没有分格水池','没有明确命名或独立表现隔离廊','主塔轮廓从阶梯八角改为环箍圆塔'],
       'approval_boundary':'本轮继续制作候选不等于负责人接受上述造型差异。'}
    save(OUT/'verification.json',audit);stage_materials(counts)
    meta={k:v for k,v in data.items() if k!='blocks'}
    save(folder/'设计与检查.json',{'data':meta,'audit':audit})
    payload={'data':meta,'palette':states,'groups':groups,'materials':mats,'audit':audit,'names':{}}
    packed=base64.b64encode(gzip.compress(json.dumps(payload,ensure_ascii=False,separators=(',',':')).encode('utf-8'),9)).decode('ascii')
    (folder/'data.js').write_text('/* I22候选；建筑表达不等于真实能源能力。 */\nwindow.HK3_PAYLOAD='+json.dumps(packed)+';',encoding='utf-8')
    subprocess.run(['node',str(ROOT/'tools/structure_delivery/package_integration_review.mjs'),str(OUT),'I22究极崩坏能反应堆・WSV V14候选待审'],check=True)
    page=folder/'三维评审.html';page.write_text(page.read_text('utf-8').replace('全部21形态','I22交付总览').replace('href="../index.html#i22"','href="../index.html"'),encoding='utf-8')
    save(OUT/'manifest.json',{**meta,'generated_at':now(),'hashes':hashes,'approval':audit['approval']})
    index(data,audit)
    scripts=OUT/'生成脚本';scripts.mkdir(exist_ok=True)
    for name in ('build_i22_wsv_ultimate_reactor_v1.py','package_i22_wsv_candidate_v1_20261023.py','finalize_i22_wsv_candidate_v1_20261023.py','package_integration_review.mjs'):
        shutil.copy2(ROOT/'tools/structure_delivery'/name,scripts/name)
    shutil.copy2(Path.home()/'.codex/skills/minecraft-builder-skill/node_modules/three/LICENSE',OUT/'Three许可.txt')
    print(json.dumps({'blocks':data['block_count'],'hashes':hashes,'static_access':len(reaches)},ensure_ascii=False),flush=True)


if __name__=='__main__':main()
