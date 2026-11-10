# -*- coding: utf-8 -*-
"""生成Gemini原案V3及三版对照；保留原案风格与既定事实边界。"""
from datetime import datetime,timezone,timedelta
import json
from pathlib import Path
import shutil
import w03_celestial_geometry_v3_20261107 as geometry
from build_max_structure_candidate import generate as export_candidate,save

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'deliveries/W03_穹界虚数锚定环_三环双翼神殿_Gemini原案_V3_20261107'
LOG=ROOT/'logs/w03-celestial-v3-20261107'
V1='W03_穹界虚数锚定环_四极折界门庭_V1_20261107'
V2='W03_穹界虚数锚定环_坠落冠冕_DeepSeek原案_V2_20261107'


def decorate():
    view=OUT/'w03';p=view/'三维评审.html';text=p.read_text(encoding='utf8')
    substitutions={
        ' V1':' V3 · 原案预览',
        'MAX · ':'Gemini原案白金／黑紫 · ',
        '既定四台MAX复制系统的独立外观候选，内部需求号W03。名称与工艺尚未冻结，未批准、未实装。':
            '三环、不对称双翼、十二柄矛和超立方体；不按递增指标增料。原文420格直立圆环与总高冲突，按范围表转译为椭圆。未批准、未实装。',
        '六处接口全部通用，不固定输入输出。':'八处接口全部通用，不固定输入输出。',
        'MAX在当前范围无更低档比较对象，不虚报递增通过率。':
            '本版仅还原Gemini原案风格；现有材料近似白金／黑紫，不新增专属机壳或CTM。递增及HCV主材差距仅记录，不主动改造。'}
    for old,new in substitutions.items():assert old in text;text=text.replace(old,new)
    text=text.replace('<div id="viewName">','<p><button id="celestialView">查看环与矛阵骨架</button><button id="completeView">还原完整外观</button></p><div id="viewName">',1)
    text=text.replace('<script src="viewer.bundle.js"></script>','<script src="viewer.bundle.js"></script><script src="w03-review.js"></script>',1)
    p.write_text(text,encoding='utf8')
    p=view/'viewer.bundle.js';text=p.read_text(encoding='utf8')
    text=text.replace('后侧天线与轴座','后侧双翼与三重环').replace('主控舱材质近景','正前白金门面与主控')
    old='alphaTest:t.transparent?.12:0,side:t.transparent?2:0';assert old in text
    text=text.replace(old,'alphaTest:t.transparent?.02:0,transparent:!!t.transparent,depthWrite:!t.transparent,side:t.transparent?2:0')
    p.write_text(text,encoding='utf8')
    source=ROOT/'tools/structure_delivery/w03_celestial_review_v3_20261107.js';shutil.copy2(source,view/'w03-review.js')
    check=json.loads((OUT/'verification.json').read_text(encoding='utf8'));manifest=json.loads((OUT/'manifest.json').read_text(encoding='utf8'))
    now=datetime.now(timezone(timedelta(hours=-5))).isoformat(timespec='seconds')
    manifest.update(candidate_version='V3',target_voltage='CIV',appearance_voltage='原案白金／黑紫',ordinary_materials=check['ordinary_materials'],
        generated_at=now,status='original_concept_visualization_only',design_rules_passed=False,source_author='Gemini；负责人提供文字原案，Codex转译逐格几何',
        claim_boundary='仅造型比较；保留原案白金黑紫风格，不为递增规则增料或改为HCV。原文尺寸冲突及材质近似已注明。')
    save(OUT/'manifest.json',manifest);save(LOG/'voltage-progression.json',check['voltage_progression'])
    save(OUT/'原案落地记录.json',dict(source_author='Gemini',coordinate_interpretation='文字不是逐格图纸；翼片排布、矛轴、倾角基准与材质近似由本次转译。',
        retained=['八角阶梯底座、15格深十字导流槽、八根倾斜锚柱','三重交错环及第二环12段装甲与紫晶桥',
            '24片白金羽翎与三条25格宽半扭转闭合带','32枚15格虚数立方体与前后护盾菱晶','十二柄白金枪尖、金色护手、紫晶护心、黑紫尾翼的实体矛',
            '85格超立方体框架、约50格旋转玻璃内立方体、25格瞳孔球','120格天顶王冠与实体向下光柱','正前45格白金门面与宽度中线主控'],
        geometry_conflicts=check['source_geometry_conflicts'],material_substitutions={
            '白金虚数装甲方块':'minecraft:quartz_block 配 minecraft:gold_block；无新贴图、无CTM',
            '折叠维度钨钢机壳':MATERIAL_BLACK,'超导律者金镀层方块':'minecraft:gold_block',
            '亚空晶格玻璃':'minecraft:magenta_stained_glass','奇点流体／光束':'minecraft:orange_stained_glass 配 minecraft:sea_lantern，均静态实体'},
        source_envelope_cells=673*529*321,actual_blocks=check['blocks'],no_growth_rule_expansion=True,no_new_block_registration=True,
        runtime_features_implemented=False,not_verified=check['not_verified']))
    for folder,label in [(V1,'V1'),(V2,'V2')]:shutil.copy2(ROOT/'deliveries'/folder/'完整预览.png',OUT/(label+'对照.png'))
    (OUT/'index.html').write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>W03 · 三环双翼神殿 · Gemini原案V3</title>
<style>body{{max-width:1500px;margin:32px auto;padding:0 22px;background:#151824;color:#eeeaf5;font:16px/1.8 system-ui}}a{{color:#efd394}}img{{width:100%;display:block}}.note{{padding:18px;border-left:3px solid #d5b161;background:#29283b}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}.compare{{display:grid;grid-template-columns:repeat(3,1fr);gap:15px}}figure{{margin:0}}@media(max-width:850px){{.grid,.compare{{display:block}}figure{{margin-bottom:22px}}}}</style>
<small>HK3GTL / W03西琳 / V3 · Gemini文字原案转译 / {now}</small><h1>穹界·虚数锚定环 · 三环双翼神殿</h1>
<p class="note">保留白金／黑紫、不对称双翼、三重天体环与十二柄矛。673×529×321（宽×深×高），{check['blocks']:,}实体方块，{check['unique_materials']}种材料。先看原案造型，不为递增指标增料，不新增专属方块；未批准、未部署。</p>
<p><a href="w03/三维评审.html">打开V3完整三维预览</a> · <a href="verification.json">完整核验</a> · <a href="原案落地记录.json">尺寸冲突与材质近似</a> · <a href="材料清单.json">材料用量</a></p>
<img src="完整预览.png" alt="Gemini三环双翼神殿完整真实方块预览"><p>{manifest['description']}</p>
<div class="grid"><figure><img src="后侧设备.png" alt="后侧查看左右双翼及三环"><figcaption>左侧24片白金羽翎，右侧三条半扭转闭合带与32枚15格虚数立方体。</figcaption></figure><figure><img src="环矛骨架.png" alt="隐藏玻璃查看三重环及十二柄矛"><figcaption>仅隐藏实际玻璃材质；不补画切面，不替换建筑。</figcaption></figure><figure><img src="俯视布局.png" alt="锚盘十字导流槽及不对称平面"><figcaption>八角阶梯底座、十字导流槽、八锚柱与前后护盾菱晶。</figcaption></figure><figure><img src="主控材质近景.png" alt="前侧居中主控和八个通用舱位"><figcaption>白金门面主控居中，八个通用仓位均有背板与五格净空。</figcaption></figure></div>
<h2>三版并排，由你选择</h2><div class="compare"><figure><a href="../{V1}/index.html"><img src="V1对照.png" alt="V1四极折界门庭">V1 · 独立设计：四极折界门庭</a></figure><figure><a href="../{V2}/index.html"><img src="V2对照.png" alt="V2 DeepSeek坠落冠冕">V2 · DeepSeek：坠落冠冕</a></figure><figure><img src="完整预览.png" alt="V3 Gemini三环双翼神殿">V3 · Gemini：三环双翼神殿</figure></div>
<h2>原文冲突，明确转译</h2><p>420格直立正圆无法容纳于321格总高，原文又给外环Y30～310。因此本版优先范围表，外环为宽420、高280的直立椭圆（名义跨度，体素边界含端点），没有把它称为420格真圆。第二环以水平面为倾角基准取30度，内环取−45度。局部Y0～320共321层；原文最高Y321按总层数321解释。</p>
<p>114,281,457是包围盒容量，包含空气；真实实体方块数以本页统计为准。原文没有逐格施工图，翼片排列、倾角基准、枪身细节与坐标均是本次几何解释。白金、黑壳、金、紫晶及橙金光束使用目标增强版3.0已有资源近似，未注册专属机壳、流体或CTM。</p>
<p>完整NBT与Schematic逐格回读、表面合并重展、接口背板与净空及四条冷却管路两端已离线核验。漂浮构件按原案保留。Portal Shader、旋转、雷电、实体角色、成型、配方及8GB工况未实现或验收；静态光柱不是运行特效。本轮未启动游戏。</p>
<p>本版是原案造型预览，HCV主材与递增规则差距仅记录，未获豁免或接入批准。V1、V2与批准归档原字节保留；固定范围74项，批准57／正式52，batch-12为0/5。W03保持西琳身份，W15凌虛晴、十周年预案及西瓜ARG保持原有决定。</p></html>''',encoding='utf8')
    for name in ['w03_celestial_review_v3_20261107.js','build_w03_celestial_v3_20261107.py']:
        shutil.copy2(ROOT/'tools/structure_delivery'/name,OUT/'生成脚本'/name)
    receipt=json.loads((LOG/'package-status.json').read_text(encoding='utf8'))
    receipt.update(original_concept_visualization_only=True,design_rules_passed=False,target_voltage='CIV',appearance_voltage='原案白金／黑紫',
        ordinary_materials=check['ordinary_materials'],lower_form_count=56,voltage_progression_passed=check['voltage_progression']['passed'],
        no_growth_rule_expansion=True,no_new_block_registration=True)
    save(LOG/'package-status.json',receipt)


MATERIAL_BLACK='gtceu:black_large_metal_sheet 配 gtceu:titanium_turbine_casing；无新贴图'
if __name__=='__main__':
    export_candidate(geometry,OUT,LOG,__file__)
    decorate()
