# -*- coding: utf-8 -*-
"""DeepSeek改进独立V5，应用十五奇观美观优先决定并保留旧版。"""
import json,shutil
from pathlib import Path
import w03_crown_geometry_v5_20261108 as geometry
from build_max_structure_candidate import generate,save

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'deliveries/W03_穹界虚数锚定环_悬天瞳冠_DeepSeek改进_V5_20261108'
LOG=ROOT/'logs/w03-crown-v5-20261108'
V2='W03_穹界虚数锚定环_坠落冠冕_DeepSeek原案_V2_20261107'
V4='W03_穹界虚数锚定环_曲翼深渊神殿_Gemini2.0_V4_20261107'


def decorate():
    view=OUT/'w03';p=view/'三维评审.html';text=p.read_text(encoding='utf8')
    replacements={' V1':' V5 · DeepSeek改进','MAX · ':'美观优先 · 紫黑／品红 · ',
        '既定四台MAX复制系统的独立外观候选，内部需求号W03。名称与工艺尚未冻结，未批准、未实装。':
            '沿DeepSeek V2另制：高悬中空瞳孔环、内弯五脊、破碎两格薄翼、不触地长锚。W01–W15不强制电压机壳主导，外观待负责人选择。',
        '六处接口全部通用，不固定输入输出。':'十二处接口分布于五矛根与中央基座，全部通用，不固定输入输出。',
        'MAX在当前范围无更低档比较对象，不虚报递增通过率。':
            '2026-11-08负责人决定W01–W15外观只以美观为前提；不强制电压或律者机壳主导，旧规模递增仅统计。运行、成型与性能仍独立验收。'}
    for old,new in replacements.items():assert old in text;text=text.replace(old,new)
    text=text.replace('<div id="viewName">','<p><button id="crownView">查看悬环与长锚</button><button data-view="low">地面仰视</button><button id="completeView">还原完整外观</button></p><div id="viewName">',1)
    text=text.replace('<script src="viewer.bundle.js"></script>','<script src="viewer.bundle.js"></script><script src="w03-review.js"></script>',1)
    p.write_text(text,encoding='utf8')
    p=view/'viewer.bundle.js';s=p.read_text(encoding='utf8').replace('后侧天线与轴座','后侧破碎光翼与内弯矛脊').replace('主控舱材质近景','独立地面主控基座')
    old='alphaTest:t.transparent?.12:0,side:t.transparent?2:0';assert old in s
    s=s.replace(old,'alphaTest:t.transparent?.02:0,transparent:!!t.transparent,depthWrite:!t.transparent,side:t.transparent?2:0')
    old='window.reviewApi={setView:q,rebuild:W,renderer:S,scene:b,camera:C}';assert old in s
    s=s.replace(old,'window.reviewApi={setView:q,rebuild:W,renderer:S,scene:b,camera:C,controls:w}')
    p.write_text(s,encoding='utf8')
    shutil.copy2(ROOT/'tools/structure_delivery/w03_crown_review_v5_20261108.js',view/'w03-review.js')
    check=json.loads((OUT/'verification.json').read_text(encoding='utf8'));manifest=json.loads((OUT/'manifest.json').read_text(encoding='utf8'))
    now='2026-11-08'
    manifest.update(candidate_version='V5',target_voltage='CIV',appearance_voltage='自由美观选材／紫黑品红',generated_at=now,
        ordinary_materials=check['ordinary_materials'],status='candidate_waiting_user_review',design_rules_passed=True,
        beauty_first_exception=check['beauty_first_exception'],source_author='DeepSeek改进意见；负责人提供文字，Codex转译逐格几何',
        claim_boundary='外观候选，美观仍由负责人选择；主材和数字递增不再作为W01–W15外观门槛，未批准、未部署。')
    save(OUT/'manifest.json',manifest);save(LOG/'voltage-progression.json',check['voltage_progression'])
    save(OUT/'改进落地与规则记录.json',dict(source_author='DeepSeek',basis='针对原V2草图的负责人本轮转交意见',
        implemented=['Y200中空3×3八边悬环与四向十字星，环内缘真实超导线圈',
            '五根内弯中空黑紫矛脊、品红玻璃细缝、尖锐根部与冠刺；五根真实接续同一悬环',
            '四组两格厚白／品红破碎薄翼，锯齿扇缘、径向裂口、弧形海晶灯纹',
            '十二根90～100格倒锥长锚，尖端Y100～110且不触地，中央75格半径空域贯通',
            '五矛根设备鞍座共十个通用接口，低矮独立地面主控基座另两个通用接口'],
        interpretations=check['source_interpretations'],actual_blocks=check['blocks'],beauty_first_exception=check['beauty_first_exception'],
        prior_versions_preserved=True,not_verified=check['not_verified']))
    for folder,label in [(V2,'V2'),(V4,'V4')]:shutil.copy2(ROOT/'deliveries'/folder/'完整预览.png',OUT/(label+'对照.png'))
    (OUT/'index.html').write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>W03 · 悬天瞳冠 · DeepSeek改进V5</title>
<style>body{{max-width:1500px;margin:32px auto;padding:0 22px;background:#18121f;color:#eee4f2;font:16px/1.8 system-ui}}a{{color:#edb1db}}img{{width:100%;display:block}}.note{{padding:18px;border-left:3px solid #c56ba9;background:#302039}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}.compare{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}}figure{{margin:0}}@media(max-width:850px){{.grid,.compare{{display:block}}figure{{margin-bottom:22px}}}}</style>
<small>HK3GTL / W03西琳 / V5 · DeepSeek改进 / {now}</small><h1>穹界·虚数锚定环 · 悬天瞳冠</h1>
<p class="note">673×529×321（宽×深×高），{check['blocks']:,}实体方块，{check['unique_materials']}种材料。沿DeepSeek V2独立改进，保留V1～V4；美观待负责人选择，未批准、未部署。</p>
<p><a href="w03/三维评审.html">完整三维与地面仰视</a> · <a href="verification.json">完整核验</a> · <a href="改进落地与规则记录.json">转译与新规则</a> · <a href="材料清单.json">材料用量</a></p>
<p class="note">负责人2026-11-08决定：W01–W15外观只以美观为前提，不强制对应电压或律者机壳主导，也不为旧递增数字堆料。原机壳映射仅作参考；运行电压、工艺、研究、实体身份与实际成型／性能独立保留。旧版包内的主材与递增限制是当时规则的历史记录，不再是当前外观否决依据。</p>
<img src="完整预览.png" alt="五脊高悬瞳孔环与破碎光翼完整预览"><p>{manifest['description']}</p>
<div class="grid"><figure><img src="地面仰视.png" alt="地面仰视高悬瞳孔与不触地长锚"><figcaption>Y200悬环与Y100～110长锚尖端；主结构只由五矛根支撑，中央基座独立。</figcaption></figure><figure><img src="悬环刺桩.png" alt="隐藏玻璃查看五脊接续与十二长锚"><figcaption>只隐藏真实玻璃，不改建筑或补画切面；五根矛脊接续同一个悬环已核验。</figcaption></figure><figure><img src="俯视布局.png" alt="锯齿破碎光翼与中空十字瞳孔"><figcaption>白／品红两格薄翼含径向裂口与弧形光纹；中央半径75格空域贯通。</figcaption></figure><figure><img src="主控材质近景.png" alt="低矮主控基座及两侧通用舱位"><figcaption>地面主控宽度居中，五矛根十个接口与基座两个接口全通用；有背板和五格净空。</figcaption></figure></div>
<h2>分别沿各自原案迭代</h2><div class="compare"><figure><a href="../{V2}/index.html"><img src="V2对照.png" alt="DeepSeek原案V2">V2 · DeepSeek原案</a></figure><figure><img src="完整预览.png" alt="DeepSeek改进V5">V5 · DeepSeek改进：悬天瞳冠</figure><figure><a href="../{V4}/index.html"><img src="V4对照.png" alt="Gemini 2.0 V4">V4 · Gemini 2.0：曲翼深渊神殿</a></figure></div>
<h2>明确转译</h2><p>原V2本已将环设在Y200，本版重点改善仰视轮廓、五脊内弯接续和光翼破碎层次，不伪称把原环从地面首次抬升。八边环名义直径250，含端点实体宽251，截面3×3；线圈与十字星独立计入实体。Y200环、80～100格长锚与Y80尖端不能同时满足，本版选择90～100格长、Y100～110尖端，保留悬空。独立中央基座是地面设备，不充当悬环支柱。</p>
<p>未执行原文示例的WorldEdit命令；以本版完整NBT与Schematic为准。原文不是逐格图纸，五向角度、曲率、裂隙、设备细节与材料近似由本次实现解释。使用已有完整方块，未以楼梯、末地烛的方盒代理替代真实模型，未新增专用机壳、CTM或动态光翼。</p>
<p>完整NBT/Schematic逐格回读、表面合并重展、五矛接环、中央贯通、接口及十二条冷却支路两端均离线核验。旧电压递增结果仍完整记录，按最新奇观例外不作外观门槛；这不代表美观已批准或正式Pattern、配方、角色出场、8GB工况通过。</p>
<p>范围74项、批准57／正式52、batch-12为0/5与系统评分保持。W03对应西琳，W15凌虛晴、十周年预案与西瓜ARG按原决定保留。</p></html>''',encoding='utf8')
    shutil.copy2(ROOT/'tools/structure_delivery/w03_crown_review_v5_20261108.js',OUT/'生成脚本/w03_crown_review_v5_20261108.js')
    receipt=json.loads((LOG/'package-status.json').read_text(encoding='utf8'))
    receipt.update(design_rules_passed=True,beauty_first_exception=check['beauty_first_exception'],target_voltage='CIV',
        appearance_voltage=manifest['appearance_voltage'],ordinary_materials=check['ordinary_materials'],lower_form_count=56,
        voltage_progression_passed=check['voltage_progression']['passed'],voltage_progression_required=False)
    save(LOG/'package-status.json',receipt)


if __name__=='__main__':
    generate(geometry,OUT,LOG,__file__)
    decorate()
