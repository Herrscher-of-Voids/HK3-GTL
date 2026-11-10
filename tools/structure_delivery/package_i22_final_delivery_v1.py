# -*- coding: utf-8 -*-
"""I22建筑候选的只读资源核对、真实纹理图、技能NBT与离线交付页面。

【变更记录 #1】2026-10-23 21:38:00（I22候选打包，不增加模组修订号）
删除：无。新增：I21全厂逐格继承保护、WSV材料依据、六室冷凝/四堆隔离/六列透平视图和完整结构导出。
修改：打包入口改为动态调用I22最新build结果，所有输出只写I22目录和I22日志。
用途：交付可审阅的新候选，并把建筑设计、阶段闭环及游戏运行分开报告。
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
        save(LOG/'rules-read.json',{'recorded_at':now(),'read_in_this_turn':True,'read_time_range_hk':'2026-10-23 20:23–20:25',
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
    evidence.update(time=now(),target='WSV28新增主体，HBV15/QSV19/IMV23前阶段原样继承',
       wsv_route='WFV27锭16+纳米陶瓷64+PBI18432→一级稳界坯16；WFV箔32成形→二级16；冷媒16000疲劳处理→三级16并回收热冷媒；氩气16000质量复核→14坯+2废；成形压机8坯→8外圈板；8板→WSV稳界约束壳材1。',
       power_boundary='WSV28主材首制链使用WFV27；industrial_reactor_i22计划输出tier28但仍provisional，不能代替最小可执行配方证据。',
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
    page=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I21 大型崩坏能反应堆 · 闭式三回路联合厂区</title>
<style>body{{margin:0;background:#15252b;color:#e4eeec;font:16px/1.85 'Microsoft YaHei',sans-serif}}main{{max-width:1300px;margin:auto;padding:30px}}header{{padding:26px;background:#294744;border-left:5px solid #b3c7a5}}h1{{margin:0}}a{{color:#b6d7c3}}img{{max-width:100%}}iframe{{width:100%;height:850px;border:1px solid #5b766a}}.notice{{background:#3c3827;border-left:4px solid #c6b66f;padding:15px}}code{{overflow-wrap:anywhere}}small{{color:#b3c8be}}</style>
<main><header><small>HK3GTL / I21 / 建筑候选V1</small><h1>大型崩坏能反应堆</h1><p>闭式三回路联合厂区：保留既有两代机组，由IMV闭式散热、分区核岛与四列透平承担新增高吞吐供能的建筑表达。</p></header>
<p>宽×深×高 <b>{W}×{D}×{H}</b> · 实体 <b>{data['block_count']:,}块</b> · 前阶段保留 <b>522,531块</b> · 新增 <b>{audit['geometry']['inheritance']['added_blocks']:,}块</b> · 主控 <b>[95,3,20]朝北</b> · 接口 <b>原16+新8=24口</b></p>
<p class="notice">本版待用户审阅，未计入批准批次，未写入正式资源或游戏实例。满五台明确批准后先装当前2.9；负责人升级后再验2.9.2。建筑、真实机器功能与兼容性分别验收。</p>
<p><a href="i21/三维评审.html">打开完整三维评审</a> · <a href="i21/三维评审.html?view=controller">原位主控</a> · <a href="i21/{NAME}.nbt">NBT</a> · <a href="i21/{NAME}.schem">Schematic</a> · <a href="../{OUT.name}.zip">完整ZIP</a></p>
<h2>原厂区完整保留，新增设施各有用途</h2><p>I19的HBV与I20的QSV机组、检修厂房、道路、主控和接口逐格原位继承，不刷旧色。东侧增加IMV双筒闭式散热塔楼、低位循环泵房、分区双腔核岛与三组卧式再生换热器；南侧增加燃料分配/乏棒分类厅与四列透平发电厅。新增阶段使用现存IMV电压机壳作为主体识别色，不另添方块ID。</p>
<p>北部新塔由完整门架、集流横臂、成组散热盒和内部双筒组成，轮廓区别于原有敞口冷却塔；高度来自真实设备层次及顶部集流框。新增核岛的双压力容器、设备脊与核心标记对应分区热状态的建筑概念。没有新增EU/HKE转换设备。</p><img src="俯视布局.png" alt="全厂实际方块俯视布局">
<h2>外围道路包住全部厂房</h2><p>旧I20后路原样保留，成为内部横向检修路。新南外围路位于Z281–285、东路位于X321–325，转角闭合；新增厂房最南后墙Z273，墙外Z274–280为连续七格维护带。南厂房前侧留七格连续净空装卸道，管廊支座落在边缘，顶部跨路保留净高。</p>
<img src="i21/等轴预览.png" alt="三代累积机组真实材质等轴预览"><iframe src="i21/三维评审.html" title="I21三维评审"></iframe>
<h2>设备内部与连接</h2><p>第三回路泵房、分区核岛、换热厅与新透平通过有支撑的完整管壳连接。燃料分类厅有四组转运/分类设备、桥式搬运梁与东端转运接点；透平厅有四列独立透平和一体发电机，四个电能口落在端壳上。接口不另立面板或托举柱。</p><img src="IMV东区设备.png" alt="IMV闭式塔楼与分区核岛近景"><p>下列剖切图仅隐藏屋顶及近侧墙以展示内部；导出文件保留完整建筑。</p><img src="透平厅内部.png" alt="四列透平与一体发电机内部"><img src="燃料分类厅内部.png" alt="燃料与乏棒分类厅内部"><img src="再生换热厅内部.png" alt="三组再生换热器内部">
<h2>主控继续在I19原位</h2><p>主控是原宽191的第96格[95,3,20]，朝北。I21不按扩大后的总宽重新迁移，不另设第二主控；新增钻石块仅标记IMV核岛核心。全部24口的用途、本地坐标、外向及静态操作位见<a href="i21/设计与检查.json">设计与检查</a>。</p><img src="原位主控.png" alt="原位主控北墙近景">
<h2>材料、文件与验收边界</h2><p>实际普通建材用量：{html.escape('；'.join(k+' '+str(v)+'块（'+str(audit['namespace_percent'][k])+'%）' for k,v in audit['namespace_counts'].items()))}；普通原版建材为零。钻石核心4块、工业接口标记24块单列。WSV新增主机壳{audit['palette']['hk3gtl:voltage_machine_casing_imv']:,}块；旧HBV/QSV颜色保留。实际安装包与项目所用HK材质逐字节一致，普通构件全部是完整立方体。</p>
<p>来源包括内测5工业网络与电压映射、源码主材链和既有实例有效配方快照。IMV源代码路线为QAV工序首制、RN-SSQ研究、陶瓷坯/板再到八板机壳；完整材料祖先链及研究首建仍未验收。I21真实控制器/Pattern、能源负载跟随、降载、乏棒逻辑和游戏运行尚未接通，本版仅建筑候选。</p><p><a href="verification.json">本轮验证</a> · <a href="材料阶段依据.json">材料阶段依据</a> · <a href="资源来源.json">实际资源来源</a>。XYZ={W}×{H}×{D}；原点/粘贴锚点[0,0,0]、Offset零，建议底部Y=-60、最高Y=133。本地file页面自动交互受环境限制，未声称浏览器旋转按钮或游戏导入已验收。</p><small>变更#1 · {audit['time']}：新增IMV阶段的完整建筑快照；前阶段零删除零替换，不改正式资源、版本修订或实例。</small></main></html>'''
    (OUT/'index.html').write_text(page,encoding='utf-8')


def main():
    checkpoint();data,geometry=build();folder=OUT/'i21'
    (folder/'blueprint.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    save(LOG/'geometry-preview.json',geometry)
    mats,identity=resources_for(data)
    if '--export' not in sys.argv or '--refresh-images' in sys.argv:images(data,mats)
    if '--export' not in sys.argv:return
    reaches=access(data);save(LOG/'static-access.json',reaches)
    assert all(p['front_clear'] and p['backing_solid'] and p['walk_access'] for p in reaches),reaches
    print('主控及24接口静态步行可达',flush=True)
    states,groups,hashes=export(data,folder);print('NBT/Sponge含空气全量回读完成',flush=True)
    hashes['nbt']=lodestone_export(data,folder,LOG);print('技能NBT同源导出回读完成',flush=True)
    counts=collections.Counter(b['state'] for b in data['blocks']);markers=('minecraft:diamond_block','hk3gtl:industrial_port_casing')
    ns=collections.Counter(b['state'].split(':')[0] for b in data['blocks'] if b['state'] not in markers)
    audit={'time':now(),'hashes':hashes,'palette':dict(counts),'geometry':geometry,'access':reaches,
           'namespace_counts':dict(ns),'namespace_percent':{k:round(v*100/sum(ns.values()),2) for k,v in ns.items()},
           'markers':{k:counts[k] for k in markers},'target_voltage':'IMV23新增主体，HBV/QSV继承',
           'minimum_executable_recipe_voltage':None,'resource_identity':identity,
           'approval':'待用户审批；不计入五台批准批次','deployment_eligible':False,
           'checks':['I20 V3全部522531块原位原状态','主控及旧16口原位；新增8口嵌设备本体','单一六面连通，20条声明通道净空',
                     '全部使用完整立方体，安装HK资源逐字节一致','NBT/Sponge含空气逐格一致，技能NBT全量回读','主控/24口有净空背接与静态步行操作位'],
           'not_verified':['整版外观批准','完整材料祖先链、RN-SSQ研究与生存首建','I21控制器/Pattern、能源功能与实际端口',
                           '游戏内成型/运行和2.9.2兼容性','本地file三维页面自动交互']}
    save(OUT/'verification.json',audit);stage_materials(counts)
    meta={k:v for k,v in data.items() if k!='blocks'}
    save(folder/'设计与检查.json',{'data':meta,'audit':audit})
    payload={'data':meta,'palette':states,'groups':groups,'materials':mats,'audit':audit,'names':{}}
    packed=base64.b64encode(gzip.compress(json.dumps(payload,ensure_ascii=False,separators=(',',':')).encode('utf-8'),9)).decode('ascii')
    (folder/'data.js').write_text('/* I21候选；建筑表达不等于真实能源能力。 */\nwindow.HK3_PAYLOAD='+json.dumps(packed)+';',encoding='utf-8')
    subprocess.run(['node',str(ROOT/'tools/structure_delivery/package_integration_review.mjs'),str(OUT),'I21闭式三回路V1・待审'],check=True)
    page=folder/'三维评审.html';page.write_text(page.read_text('utf-8').replace('全部21形态','I21交付总览').replace('href="../index.html#i21"','href="../index.html"'),encoding='utf-8')
    save(OUT/'manifest.json',{**meta,'generated_at':now(),'hashes':hashes,'approval':audit['approval']})
    index(data,audit)
    scripts=OUT/'生成脚本';scripts.mkdir(exist_ok=True)
    for name in ('build_i21_imv_cogeneration_v1.py','package_i21_imv_candidate_v1_20261023.py','package_integration_review.mjs'):
        shutil.copy2(ROOT/'tools/structure_delivery'/name,scripts/name)
    shutil.copy2(Path.home()/'.codex/skills/minecraft-builder-skill/node_modules/three/LICENSE',OUT/'Three许可.txt')
    print(json.dumps({'blocks':data['block_count'],'hashes':hashes,'static_access':len(reaches)},ensure_ascii=False),flush=True)


if __name__=='__main__':main()
