# -*- coding: utf-8 -*-
"""DeepSeek原案可视化；不以资格整改改变原方案体量与配色。"""
from datetime import datetime,timezone,timedelta
import json
from pathlib import Path
import shutil
import w03_crown_geometry_v2_20261107 as geometry
from build_max_structure_candidate import generate as export_candidate,save

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'deliveries/W03_穹界虚数锚定环_坠落冠冕_DeepSeek原案_V2_20261107'
LOG=ROOT/'logs/w03-crown-v2-20261107'
V1='W03_穹界虚数锚定环_四极折界门庭_V1_20261107'


def decorate():
    view=OUT/'w03';page=view/'三维评审.html';text=page.read_text(encoding='utf8')
    replacements={
        ' V1':' V2 · 原案预览',
        'MAX · ':'原案紫黑／品红 · ',
        '既定四台MAX复制系统的独立外观候选，内部需求号W03。名称与工艺尚未冻结，未批准、未实装。':
            '负责人要求先看原案：五矛、四翼、八边悬环、十二刺桩；不按现行递增与HCV规则改造。仅供比较，未批准、未实装。',
        '六处接口全部通用，不固定输入输出。':'十二处高位锚定器舱位均通用，不固定输入输出；本按钮定位地面主控。',
        '各路管道均核对指定两端设备；这不代表流体运行能力。':'十二条锚定器内部冷却支路均核对两端设备；这不代表流体运行能力。',
        'MAX在当前范围无更低档比较对象，不虚报递增通过率。':
            '本版保留原案紫黑配色与薄壳体量。HCV主材、方块量和材料种数与既定规则存在差距，仅记录，不为过审改造。'}
    for old,new in replacements.items():assert old in text;text=text.replace(old,new)
    text=text.replace('<div id="viewName">','<p><button id="crownView">查看悬环与刺桩</button><button id="completeView">还原完整外观</button></p><div id="viewName">',1)
    text=text.replace('<script src="viewer.bundle.js"></script>','<script src="viewer.bundle.js"></script><script src="w03-review.js"></script>',1)
    page.write_text(text,encoding='utf8')
    bundle=view/'viewer.bundle.js';viewer=bundle.read_text(encoding='utf8')
    viewer=viewer.replace('后侧天线与轴座','后侧冠刺与光翼').replace('主控舱材质近景','地面锚点主控近景')
    old='alphaTest:t.transparent?.12:0,side:t.transparent?2:0'
    assert old in viewer
    viewer=viewer.replace(old,'alphaTest:t.transparent?.02:0,transparent:!!t.transparent,depthWrite:!t.transparent,side:t.transparent?2:0')
    bundle.write_text(viewer,encoding='utf8')
    source=ROOT/'tools/structure_delivery/w03_crown_review_v2_20261107.js'
    shutil.copy2(source,view/'w03-review.js')
    now=datetime.now(timezone(timedelta(hours=-5))).isoformat(timespec='seconds')
    manifest=json.loads((OUT/'manifest.json').read_text(encoding='utf8'))
    check=json.loads((OUT/'verification.json').read_text(encoding='utf8'))
    manifest.update(target_voltage='CIV',appearance_voltage='原案紫黑／品红',ordinary_materials=check['ordinary_materials'],
        character='西琳',candidate_version='V2',generated_at=now,status='original_concept_visualization_only',
        design_rules_passed=False,source_author='DeepSeek；负责人提供原文，Codex转译逐格几何',
        user_instruction='你先别动方块量，我想看一下原原本本它给我们的方案',
        claim_boundary='原案预览；不为递增规则增料或改为HCV主材，尚未获设计规则豁免或正式接入批准。')
    save(OUT/'manifest.json',manifest)
    save(LOG/'voltage-progression.json',check['voltage_progression'])
    save(OUT/'原案落地记录.json',dict(source_author='DeepSeek',user_instruction=manifest['user_instruction'],
        retained=['673×529×321边界','五根不等长空心矛梁与五根高低冠刺','四张三格厚渐变光翼，35格间距光带',
            'Y200八边悬环，275格外径，5×5中空管壳','十二根80～120格倒锥刺桩与内部舱位','紫黑／品红配色','独立地面中央主控基座与窄道'],
        not_adjusted=['不为方块数、材料数、HCV主材或全结构连通性改造原案','不把悬环加厚为巨型实体环','不补满矛根之间地面'],
        coordinate_interpretation='原文未给坐标或逐层施工图；五向角度、曲率、分带与舱内细节由本次实现解释，不能称逐格原作。',
        unresolved=check['not_verified'],actual_blocks=check['blocks'],original_estimated_blocks=[800000,1500000],
        estimate_is_not_exact_bill_of_materials=True))
    (OUT/'index.html').write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>W03 · 坠落冠冕 · DeepSeek原案预览</title>
<style>body{{max-width:1440px;margin:32px auto;padding:0 22px;background:#17121e;color:#eee4f2;font:16px/1.8 system-ui}}a{{color:#edb1db}}img{{width:100%;display:block}}.note{{padding:18px;border-left:3px solid #ce6aae;background:#302039}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}@media(max-width:800px){{.grid{{display:block}}}}blockquote{{border-left:2px solid #bd8bc9;margin:24px 0;padding-left:20px}}</style>
<small>HK3GTL / W03西琳 / V2 · DeepSeek原案可视化 / {now}</small><h1>穹界·虚数锚定环 · 坠落冠冕</h1>
<p class="note">按负责人最新要求，先看原案：保留紫黑／品红、空心矛梁、薄翼和细悬环，不为现行规模规则增料。673×529×321（宽×深×高），{check['blocks']:,}实体方块，{check['unique_materials']}种材料。仅供两版比较，未批准、未部署。</p>
<p><a href="w03/三维评审.html">旋转、缩放与逐层查看原案V2</a> · <a href="../{V1}/index.html">打开独立V1对照</a> · <a href="verification.json">完整核验</a> · <a href="原案落地记录.json">原案与几何解释</a> · <a href="材料清单.json">材料用量</a></p>
<img src="完整预览.png" alt="五矛四翼与八边悬环的完整真实方块预览"><p>{manifest['description']}</p>
<div class="grid"><figure><img src="俯视布局.png" alt="五向星形与中央瞳孔开口"><figcaption>五向不等长矛脊、四张薄翼、未闭合冠冕；地面不铺满。</figcaption></figure><figure><img src="悬环刺桩.png" alt="隐藏光翼后查看八边悬环与十二刺桩"><figcaption>隐藏玻璃后查看真实悬环与刺桩；不补画切面，不替换结构。</figcaption></figure><figure><img src="后侧设备.png" alt="后侧光翼及尖锐冠刺"><figcaption>前后轮廓均由完整结构表面生成。</figcaption></figure><figure><img src="主控材质近景.png" alt="中心地面主控基座"><figcaption>主控保留地面中央；十二个通用舱位位于高空锚定器内部。</figcaption></figure></div>
<p>原文的80万～150万是体量估计，不是逐格清单；本版统计如上，未以调参补料追某个数字。核心环中心线Y200、外径275，5×5中空管壳；光翼厚3格，光带间距35格；刺桩80～120格。五条矛梁保留内腔。紫黑和品红直接使用增强版3.0内真实方块贴图，不做全局换色。</p>
<p>原文同时描述“十二刺桩唯一触地”和“中央基座及五矛根触地”，两者不能同时逐字满足。本版采用后文：基座与五矛根触地，十二刺桩悬垂。原文没有施工坐标，曲线、五向角度和舱内细节是这次几何转译；不是DeepSeek直接输出的逐格图纸。</p>
<p>完整NBT与Schematic逐格回读、合并表面重展、接口背板与净空、内部管路两端均离线核验。保留原案导致HCV主材与规模递增规则未通过；本版不具备正式接入资格。12～16渲染分区、逐段激活、配方解锁、实体与传送均未实装，8GB性能未验收。本轮未启动游戏。</p>
<blockquote>它不是被建造的。它是被“允许”存在的。<br>五根矛从实数的地面刺出，把一个不属于这里的环钉在半空。环的内侧垂下十二根桩，指向一个从未被填上的瞳孔。<br>当最后一根锚定桩触到基座时，这个空间就不再属于世界了。它属于她。<br><small>——DeepSeek原案图鉴文案；叙事提案，不代表当前刺桩动画或触地机制已实现。</small></blockquote>
<p>V1及批准归档原字节保留；固定范围74项，批准57／正式52，batch-12为0/5。西琳身份、W15凌虛晴、十周年预案与西瓜ARG保持原有决定。</p></html>''',encoding='utf8')
    shutil.copy2(ROOT/'deliveries'/V1/'完整预览.png',OUT/'V1对照.png')
    page=OUT/'index.html';text=page.read_text(encoding='utf8')
    text=text.replace('<p>V1及批准归档原字节保留；',f'<h2>两条路线，等待选择</h2><div class="grid"><figure><img src="V1对照.png" alt="独立V1四极折界门庭"><figcaption><a href="../{V1}/index.html">V1 · 四极折界门庭</a>：HCV琥珀、实体门庭。</figcaption></figure><figure><img src="完整预览.png" alt="DeepSeek原案V2坠落冠冕"><figcaption>V2 · 坠落冠冕：紫黑品红、五矛四翼、悬环刺桩。</figcaption></figure></div><p>V1及批准归档原字节保留；',1)
    page.write_text(text,encoding='utf8')
    for name in ['w03_crown_review_v2_20261107.js','build_w03_crown_v2_20261107.py']:
        shutil.copy2(ROOT/'tools/structure_delivery'/name,OUT/'生成脚本'/name)
    receipt=json.loads((LOG/'package-status.json').read_text(encoding='utf8'))
    receipt.update(original_concept_visualization_only=True,design_rules_passed=False,target_voltage='CIV',appearance_voltage='原案紫黑／品红',
        ordinary_materials=check['ordinary_materials'],lower_form_count=56,voltage_progression_passed=False,user_instruction=manifest['user_instruction'])
    save(LOG/'package-status.json',receipt)


if __name__=='__main__':
    export_candidate(geometry,OUT,LOG,__file__)
    decorate()
