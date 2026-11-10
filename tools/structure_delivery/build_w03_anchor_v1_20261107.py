# -*- coding: utf-8 -*-
"""生成西琳W03独立V1；完整结构、真实资源和候选比较入口一并交付。"""
from datetime import datetime,timezone,timedelta
import json
from pathlib import Path
import shutil
import w03_anchor_geometry_v1_20261107 as geometry
from build_max_structure_candidate import generate as export_candidate,save

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'deliveries/W03_穹界虚数锚定环_四极折界门庭_V1_20261107'
LOG=ROOT/'logs/w03-anchor-v1-20261107'


def decorate():
    view=OUT/'w03';page=view/'三维评审.html';text=page.read_text(encoding='utf8')
    replacements={
        'MAX · ':'运行CIV · HCV虚空琥珀外壳 · ',
        '既定四台MAX复制系统的独立外观候选，内部需求号W03。名称与工艺尚未冻结，未批准、未实装。':
            'W03西琳·四极折界门庭V1，供与后续DeepSeek方案比较。未批准、未实装。',
        '六处接口':'八处接口',
        'MAX在当前范围无更低档比较对象，不虚报递增通过率。':
            '运行CIV，外观HCV。与全部56个已批准低阶形态比较，实体数、44种普通材料、实际包围盒体积与高度四项严格递增。'}
    for old,new in replacements.items():assert old in text;text=text.replace(old,new)
    assert 'MAX' not in text
    text=text.replace('<div id="viewName">','<p><button id="anchorView">查看锚座内腔</button><button id="completeView">还原完整外观</button></p><div id="viewName">',1)
    text=text.replace('<script src="viewer.bundle.js"></script>','<script src="viewer.bundle.js"></script><script src="w03-review.js"></script>',1)
    page.write_text(text,encoding='utf8')
    source=ROOT/'tools/structure_delivery/w03_anchor_review_v1_20261107.js'
    shutil.copy2(source,view/'w03-review.js')
    bundle=view/'viewer.bundle.js';viewer=bundle.read_text(encoding='utf8')
    viewer=viewer.replace('后侧天线与轴座','后侧门庭与锚座')
    bundle.write_text(viewer,encoding='utf8')
    now=datetime.now(timezone(timedelta(hours=-5))).isoformat(timespec='seconds')
    manifest=json.loads((OUT/'manifest.json').read_text(encoding='utf8'))
    manifest.update(target_voltage='CIV',appearance_voltage='HCV',ordinary_materials=44,character='西琳',generated_at=now,
        claim_boundary='西琳W03独立V1外观候选，供与DeepSeek方案比较；未批准、未接入正式Pattern。')
    save(OUT/'manifest.json',manifest)
    check=json.loads((OUT/'verification.json').read_text(encoding='utf8'))
    save(LOG/'voltage-progression.json',check['voltage_progression'])
    (OUT/'index.html').write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{manifest['title']} V1</title>
<style>body{{max-width:1440px;margin:32px auto;padding:0 22px;background:#191521;color:#f4e9da;font:16px/1.8 system-ui}}a{{color:#f1c97d}}img{{width:100%;display:block}}.note{{padding:18px;border-left:3px solid #e0af5a;background:#32243b}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}@media(max-width:800px){{.grid{{display:block}}}}</style>
<small>HK3GTL / W03既定文明奇观 / 西琳 / 独立V1 / {now}</small><h1>{manifest['title']}</h1>
<p class="note">运行CIV；外观HCV虚空琥珀。673×529×321（宽×深×高），{check['blocks']:,}实体方块，46种材料（普通44种）。本版先保留独立设计，待与DeepSeek方案比较后选择；未批准、未部署。</p>
<p><a href="w03/三维评审.html">打开完整三维评审</a> · <a href="verification.json">完整核验记录</a> · <a href="材料清单.json">材料清单</a> · <a href="锚座内腔.png">锚座内腔</a></p>
<img src="完整预览.png" alt="西琳四极折界门庭完整真实材质预览"><p>{manifest['description']}</p><p>{manifest['purpose']}</p>
<div class="grid"><figure><img src="俯视布局.png" alt="前后门庭与四极锚座布局"><figcaption>主锚门、前后门庭与四向锚臂，共同围合中央承台。</figcaption></figure><figure><img src="后侧设备.png" alt="后侧门庭与隔离锚塔"><figcaption>真实贯穿门洞与分层轮廓；低位回路连接四锚座。</figcaption></figure><figure><img src="逐层剖切.png" alt="主门及锚座实际表面剖切"><figcaption>只显示文件中的实际表面，不补画剖切面。</figcaption></figure><figure><img src="主控材质近景.png" alt="居中主控与八个通用接口"><figcaption>主控嵌于主门北侧，宽度居中；八个通用仓位均保留五格接线净空。</figcaption></figure></div>
<p>实际边界达到673×529×321，超过321×321×129下限；按CIV比较全部56个批准低阶形态，实体数、普通材料种数、实际包围盒体积与高度严格递增。HCV为最大单一材料。全部实体六邻接连通，四条锚臂冷却联络均核对两端设备。</p>
<p>完整NBT与Schematic逐格回读一致；查看器表面合并后重展一致，材质取自目标增强版3.0的真实模型与贴图静态首帧。完整资源不代表方块注册、生存获取或实际运行已经通过。</p>
<p>保留西琳身份；不改W15凌虛晴、十周年派对预案、西瓜ARG或毕业条件。正式Pattern、角色实体、跨维度许可、配方、仓室兼容与8GB全建筑运行另验。本轮未启动游戏。固定范围74项，批准57／正式52；batch-12为0/5。</p></html>''',encoding='utf8')
    scripts=OUT/'生成脚本'
    for name in ['w03_anchor_review_v1_20261107.js','w03_voltage_progression_20261107.py','w02_voltage_progression_20261107.py']:
        shutil.copy2(ROOT/'tools/structure_delivery'/name,scripts/name)
    receipt=json.loads((LOG/'package-status.json').read_text(encoding='utf8'))
    receipt.update(target_voltage='CIV',appearance_voltage='HCV',ordinary_materials=44,lower_form_count=56,voltage_progression_passed=True)
    save(LOG/'package-status.json',receipt)


if __name__=='__main__':
    export_candidate(geometry,OUT,LOG,__file__)
    decorate()
