# -*- coding: utf-8 -*-
"""导出W02重建候选与完整边界预览，保留所有旧版。"""
import hashlib
import json
from pathlib import Path
import shutil
import numpy as np
from build_max_structure_candidate import generate, save
from build_wonder_boundary_repairs_20261108 import preview_page
import w02_bunny_dock_geometry_v3_20261108 as geometry

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/W02_Gemini_十二翼重构船坞_V3_20261108'
LOG = ROOT / 'logs/w02-bunny-dock-v3-20261108'


def audit(cube,data):
    assert len(data['towers'])==64 and len(data['wings'])==12 and len(data['cables'])==8 and len(data['crowns'])==3
    assert data['core']['faces']==20 and data['core']['edges']==30 and data['cannons']['count']==2
    assert len(data['ports'])==8 and data['controller_face']=='south'
    for side in (-1,1):
        assert [round(w['angle_degrees']) for w in data['wings'] if w['side']==side]==[-15,0,15,30,45,60]
    counts=np.bincount(cube.ravel(),minlength=len(geometry.STATES)+1);h,d,w=cube.shape
    assert np.all(counts[1:])
    assert all(np.any(np.take(cube,i,axis=axis)) for axis in range(3) for i in (0,cube.shape[axis]-1))
    port_checks=[]
    for item in [dict(id='主控',pos=data['controller'])]+data['ports']:
        p=np.array(item['pos']);inner=p-[0,0,1]
        assert cube[p[1],p[2],p[0]] and cube[inner[1],inner[2],inner[0]]
        for step in range(1,6):
            at=p+[0,0,step]
            if np.all(at<[w,h,d]):assert not cube[at[1],at[2],at[0]]
        port_checks.append(dict(id=item['id'],position=p.tolist(),inner_backed=True,outer_clear=5,
                                beyond_exact_export_bounds_is_air=True))
    check=dict(passed=True,approved=False,installed=False,game_verified=False,
        size_xyz=[w,h,d],size_wdh=[w,d,h],bounds_xyz=dict(min=[0,0,0],max=[w-1,h-1,d-1]),
        blocks=int(counts[1:].sum()),unique_materials=len(geometry.STATES),palette=dict(zip(geometry.STATES,map(int,counts[1:]))),
        port_checks=port_checks,pipe_routes_count=0,pipe_routes_passed=False,open_pipe_ends=None,
        no_nominal_clipping=True,source_conflicts=data['source_conflicts'],part_overlaps=data['component_overlaps'],
        original_components_saved=True,dynamic_effects_implemented=False,desktop_used=False,game_started=False,
        checks=['完整坐标生成后按实际包围盒导出，不把名义尺寸当裁切窗口。','主控及八通用接口背衬与五格外接线净空通过，精确包围盒外视为空气。'],
        not_verified=['建筑未批准、未部署；正式Pattern、成型、加工与性能另验。','冷却网络仅为实体管路布局，未逐路验收实际流体运输。'])
    assert all(p['outer_clear']==5 for p in check['port_checks'])
    check['design_rules_passed']=False
    check['geometry_passed']=True
    check['checks'].append('64冷却塔、12片完整翼、8根注入缆、两门180格主炮及三环数量与角度通过。')
    check['not_verified'].extend(['原文冲突与相交按原案保留，不能据合成文件回读一致宣称独立构件无穿模。',
        '专属新材质、CTM、自发光光路、流体和运行演出未实装；本轮使用真实现有方块。'])
    return check


def main():
    LOG.mkdir(parents=True,exist_ok=True); OUT.mkdir(parents=True,exist_ok=True)
    baseline=LOG/'report-baseline'
    if not baseline.exists():
        baseline.mkdir()
        for name in ('index.html','current-summary.json'):
            shutil.copy2(ROOT/'logs/beta5-completion-audit-20261030'/name,baseline/name)
        old=ROOT/'deliveries/W02_万象自律工业矩阵_递归构造环_V2_20261107'
        save(LOG/'old-v2-sha256.json',{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
             for p in old.rglob('*') if p.is_file()})
    generate(type('Geometry',(),dict(STATES=geometry.STATES,ROLES=geometry.ROLES,__file__=geometry.__file__,
        build=staticmethod(geometry.build),audit=staticmethod(audit))),OUT,LOG,__file__)
    manifest=json.loads((OUT/'manifest.json').read_text('utf8'))
    manifest.update(target_voltage='WSV',candidate_version='V3-Gemini重装小兔十二翼船坞',source_author='Gemini，负责人提供完整文字原案')
    save(OUT/'manifest.json',manifest)
    check=json.loads((OUT/'verification.json').read_text('utf8'))
    preview_page(OUT,manifest,check,manifest['description']+' 原文冲突照实保留，未批准、未部署；运行特效待接入。')
    view=OUT/'w02';page=view/'三维评审.html'
    text=page.read_text('utf8').replace('</html>','<script src="bunny-review.js"></script></html>')
    text=text.replace('钻石块占位。','钻石块占位；主控朝南。')
    page.write_text(text,'utf8')
    save(OUT/'原案参数与冲突.json',dict(nominal_size_xyz=manifest['nominal_size_xyz'],
         actual_size_xyz=manifest['size'],source_conflicts=manifest['source_conflicts'],
         coordinate_interpretation=manifest['coordinate_interpretation'],part_overlaps=manifest['component_overlaps'],
         dynamics=manifest['dynamic_effects']))
    script=ROOT/'tools/structure_delivery/w02_bunny_review_v3_20261108.js'
    shutil.copy2(script,view/'bunny-review.js');shutil.copy2(script,OUT/'生成脚本'/script.name)
    w,h,d=manifest['size'];overlaps=len(manifest['component_overlaps'])
    (OUT/'index.html').write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>W02 Gemini十二翼重构船坞 V3</title>
<style>:root{{color-scheme:dark}}body{{max-width:1400px;margin:30px auto;padding:0 24px;background:#101c2c;color:#e2f2ff;font:16px/1.8 system-ui}}a{{color:#7fdfff}}img{{width:100%;display:block}}.note{{background:#20354a;padding:16px;border-left:3px solid #7fdfff}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}@media(max-width:800px){{.grid{{display:block}}}}</style>
<h1>理之律者 · 万象·自律工业矩阵</h1><h2>Gemini · 重装小兔十二翼重构船坞 V3</h2>
<p class="note">完整原案转译候选，旧V2保留。实际{w}×{d}×{h}（宽×深×高），{check['blocks']:,}个实体方块，{len(geometry.STATES)}种已有真实材料。名义649×493×303不作裁切窗口。未批准、未部署。</p>
<p><a href="w02/三维评审.html">打开完整三维预览</a> · <a href="原案参数与冲突.json">原案参数、坐标转译与冲突</a> · <a href="材料清单.json">真实方块清单</a> · <a href="verification.json">完整回读核验</a> · <a href="../W02_万象自律工业矩阵_递归构造环_V2_20261107/index.html">旧V2对照</a></p>
<img src="完整预览.png" alt="十二翼重装船坞完整原案预览">
<p>四象限各16座六角冷却塔；中央双层85格二十面体机械笼、45格逻辑核心与8根斜注入缆；前后各180格分体轨道炮、贯穿Z轴的15格激光通道；左右各6片160格翼；三重380／260／140格冠冕。南侧Y32胸甲平台包含主控和8处通用接口。</p>
<section class="grid"><img src="正面十二翼.png" alt="正面十二翼与主控平台"><img src="俯视布局.png" alt="四象限冷却塔与十字物流槽"></section>
<p>原文缺少逐翼坐标、冷却塔布局和完整施工切片，本版公开所有坐标转译。中环高度与翼区范围冲突保留；共有{overlaps}对构件交叠记录，包含承台接合，也可能有原案构件干涉。独立构件原坐标另存于日志original-components.npz，合成导出同格按生成顺序取后者；不把文件回读通过冒充无穿模。</p>
<p>原案幻想材质暂映射真实方块，静态玻璃不冒充流体、CTM、滚动公式或Shader。核心扫描、三环转动、翼悬浮、光柱和全息幕均为后续运行演出要求，本轮未实装。运行WSV、角色身份、研究与毕业条件不因外观重建改变。</p>
<p><a href="w02/{manifest['name']}.nbt">完整NBT</a> · <a href="w02/{manifest['name']}.schem">Sponge结构</a> · <a href="../../logs/beta5-completion-audit-20261030/index.html">固定审计</a></p></html>''','utf8')
    print(json.dumps(dict(passed=True,size_xyz=manifest['size'],blocks=check['blocks'],overlap_pairs=overlaps),ensure_ascii=False))


if __name__=='__main__':main()
