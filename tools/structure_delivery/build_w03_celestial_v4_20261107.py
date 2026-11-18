# -*- coding: utf-8 -*-
"""生成Gemini 2.0独立候选，附原V3对照与明确的几何转译记录。"""
from datetime import datetime,timezone,timedelta
import json,shutil
from pathlib import Path
import w03_celestial_geometry_v4_20261107 as geometry
from build_max_structure_candidate import generate,save

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'deliveries/W03_穹界虚数锚定环_曲翼深渊神殿_Gemini2.0_V4_20261107'
LOG=ROOT/'logs/w03-celestial-v4-20261107'
V3='W03_穹界虚数锚定环_三环双翼神殿_Gemini原案_V3_20261107'


def decorate():
    view=OUT/'w03';p=view/'三维评审.html';text=p.read_text(encoding='utf8')
    replacements={
        ' V1':' V4 · Gemini 2.0', 'MAX · ':'原案圣白／黑紫 · ',
        '既定四台MAX复制系统的独立外观候选，内部需求号W03。名称与工艺尚未冻结，未批准、未实装。':
            'Gemini 2.0曲翼深渊神殿。六柄分体主矛与正八面体核心分支；保留既有三版，未批准、未实装。',
        '六处接口全部通用，不固定输入输出。':'八处接口全部通用，不固定输入输出。',
        'MAX在当前范围无更低档比较对象，不虚报递增通过率。':
            '本版是Gemini改进意见的造型转译；HCV主材及既定递增规则差距仍保留，不为达标另加方块。'}
    for old,new in replacements.items():assert old in text;text=text.replace(old,new)
    text=text.replace('<div id="viewName">','<p><button id="celestialView">查看三环与六矛骨架</button><button id="completeView">还原完整外观</button></p><div id="viewName">',1)
    text=text.replace('<script src="viewer.bundle.js"></script>','<script src="viewer.bundle.js"></script><script src="w03-review.js"></script>',1)
    p.write_text(text,encoding='utf8')
    p=view/'viewer.bundle.js';text=p.read_text(encoding='utf8').replace('后侧天线与轴座','后侧曲线双翼与深渊池').replace('主控舱材质近景','V字舰桥与黑金主控祭坛')
    old='alphaTest:t.transparent?.12:0,side:t.transparent?2:0';assert old in text
    text=text.replace(old,'alphaTest:t.transparent?.02:0,transparent:!!t.transparent,depthWrite:!t.transparent,side:t.transparent?2:0')
    p.write_text(text,encoding='utf8')
    js=(ROOT/'tools/structure_delivery/w03_celestial_review_v3_20261107.js').read_text(encoding='utf8').replace('Gemini原案取景','Gemini 2.0曲翼取景').replace('三环与十二柄矛','三环与六柄分体主矛').replace('camera.zoom=18','camera.zoom=9')
    (view/'w03-review.js').write_text(js,encoding='utf8')
    check=json.loads((OUT/'verification.json').read_text(encoding='utf8'));manifest=json.loads((OUT/'manifest.json').read_text(encoding='utf8'))
    now=datetime.now(timezone(timedelta(hours=-5))).isoformat(timespec='seconds')
    manifest.update(candidate_version='V4',target_voltage='CIV',appearance_voltage='原案圣白／黑紫',ordinary_materials=check['ordinary_materials'],
        generated_at=now,status='original_concept_visualization_only',design_rules_passed=False,source_author='Gemini 2.0；负责人提供改进方案，Codex转译逐格几何',
        claim_boundary='仅造型比较；六柄分体矛及正八面体分支，局部转译见记录。未批准、未部署。')
    save(OUT/'manifest.json',manifest);save(LOG/'voltage-progression.json',check['voltage_progression'])
    rail=manifest['rings'][0]['rail_color_share_before_crossing_parts']
    save(OUT/'改进方案落地记录.json',dict(source_author='Gemini 2.0',source_version='负责人本轮提供的算法级重构建议',
        implemented=['十片二次贝塞尔弧形翼刃，菱形截面12×6，悬浮根部与收尖末端',
            '两条24×6开放三维曲线飘带，24枚沿轨递减28→6并递增旋转的紫晶立方体',
            '三重双轨窄环、轨间16格空隙、每15度X型金色桁架及紫晶接管',
            '24枚45格双尖浮游晶柱取代贴环短粗金锥',
            '六柄205格分体主矛，80格白刃、10格断口、18格紫晶、C形金护手及螺旋黑柄',
            '黑金正八面体外框、三层同心半透明紫晶菱形壳、橙金球核心',
            '45格深阶梯反应池、48道白金放射散热肋与V字双塔舰桥、24格白色天桥'],
        main_ring_rail_palette_share_before_crossing_parts=rail,geometry_interpretations=check['source_geometry_conflicts'],
        actual_blocks=check['blocks'],no_growth_rule_expansion=True,no_hcv_recolor=True,no_new_block_registration=True,
        prior_v3_preserved=True,runtime_features_implemented=False,not_verified=check['not_verified']))
    shutil.copy2(ROOT/'deliveries'/V3/'完整预览.png',OUT/'V3对照.png')
    (OUT/'index.html').write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>W03 · 曲翼深渊神殿 · Gemini 2.0 V4</title>
<style>body{{max-width:1500px;margin:32px auto;padding:0 22px;background:#151824;color:#eeeaf5;font:16px/1.8 system-ui}}a{{color:#efd394}}img{{width:100%;display:block}}.note{{padding:18px;border-left:3px solid #d5b161;background:#29283b}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}figure{{margin:0}}@media(max-width:850px){{.grid{{display:block}}figure{{margin-bottom:22px}}}}</style>
<small>HK3GTL / W03西琳 / V4 · Gemini 2.0意见转译 / {now}</small><h1>穹界·虚数锚定环 · 曲翼深渊神殿</h1>
<p class="note">673×529×321（宽×深×高），{check['blocks']:,}实体方块，{check['unique_materials']}种材料。保留V1～V3；本版仅供外观选择，未批准、未实装，不为既定递增门槛增料。</p>
<p><a href="w03/三维评审.html">打开V4完整三维预览</a> · <a href="verification.json">完整核验</a> · <a href="改进方案落地记录.json">改进落实与几何解释</a> · <a href="材料清单.json">材料用量</a></p>
<img src="完整预览.png" alt="曲翼、双飘带、双轨三环与六柄分体矛完整预览"><p>{manifest['description']}</p>
<h2>V3 → V4</h2><div class="grid"><figure><a href="../{V3}/index.html"><img src="V3对照.png" alt="保留的Gemini原案V3">V3 · 三环双翼神殿，查看前三版对照</a></figure><figure><img src="完整预览.png" alt="Gemini 2.0 V4">V4 · 曲翼深渊神殿</figure></div>
<h2>曲线、轻环与反应池</h2><div class="grid"><figure><img src="后侧设备.png" alt="后侧双曲线飘带与星流"><figcaption>原闭合圆带删除，24枚晶体沿两条飘带递减并旋转，末端自然收尖。</figcaption></figure><figure><img src="环矛骨架.png" alt="隐藏玻璃查看双轨桁架与分体矛"><figcaption>三环均分为两轨；六柄宽刃矛留出晶体断口，核心使用正八面体。</figcaption></figure><figure><img src="俯视布局.png" alt="阶梯深渊反应池与48道装甲肋"><figcaption>45格深阶梯反应池，底部同心光环及四条设备间导管，24格白色天桥向中心延伸。</figcaption></figure><figure><img src="主控材质近景.png" alt="V字双塔与黑金主控祭坛"><figcaption>前倾35格双塔护翼与舰桥祭坛；八个通用接口有背板及五格净空。</figcaption></figure></div>
<h2>原文选择与实际转译</h2><p>本版选择六柄205格主矛，不叠加另一分支的四柄300格矛。旋转立方体不会变成正八面体，本版采用原文明确提出的正八面体黑金框及三层菱形壳。翼刃、曲线、姿态与分区由文字转译，不能称为作者给出的逐格图纸。</p>
<p>420格真圆直立后仍超出321格总高，加上45格浮游柱更无法容纳。本版主环名义跨度420×226，上下晶柱沿纵深倾斜；不是420格直立正圆。两轨中心距21格、各厚5格，轨间实际含16个空气体素，24处桁架按15度分布。主环轨道在交叉构件叠加前的真实体素配色：圣白{rail[geometry.WHITE]:.1%}、金{rail[geometry.M.GOLD]:.1%}、黑{rail[geometry.M.ATOMIC]:.1%}，不把整座建筑或交叉矛阵的颜色混入这个比例。</p>
<p>使用目标增强版3.0现有材质，不新增专属机壳、CTM、运行特效或实体。完整NBT、Schematic逐格回读与表面重展、接口净空、管路指定两端及离线预览已检查；不等于成型、配方、8GB工况或图形客户端实测通过。</p>
<p>HCV主材和规模递增仍有差距，未获得豁免；固定范围74项，批准57／正式52、batch-12为0/5，系统评分不变。W03是西琳，W15凌虛晴、十周年预案与西瓜ARG保持原决定。</p></html>''',encoding='utf8')
    for filename in ['w03_celestial_geometry_v3_20261107.py','w03_celestial_review_v3_20261107.js']:
        shutil.copy2(ROOT/'tools/structure_delivery'/filename,OUT/'生成脚本'/filename)
    receipt=json.loads((LOG/'package-status.json').read_text(encoding='utf8'))
    receipt.update(original_concept_visualization_only=True,design_rules_passed=False,target_voltage='CIV',appearance_voltage='原案圣白／黑紫',
        ordinary_materials=check['ordinary_materials'],lower_form_count=56,voltage_progression_passed=check['voltage_progression']['passed'],no_growth_rule_expansion=True)
    save(LOG/'package-status.json',receipt)


if __name__=='__main__':
    generate(geometry,OUT,LOG,__file__)
    decorate()
