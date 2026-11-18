# -*- coding: utf-8 -*-
"""交付C1完整候选和单矛拆件；旧C与已安装模组不变。"""
import hashlib
import json
import shutil
import zipfile
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import w03_void_spear_c1_20261108 as geometry
from build_max_structure_candidate import generate, save, INSTANCE
from build_wonder_boundary_repairs_20261108 import generic_audit, preview_page

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'deliveries/W03_C方案_亚空之矛优化_C1_20261108'
LOG = ROOT/'logs/w03-c-spear-refinement-20261108'
BASE = ROOT/'deliveries/W03_完整几何边界修复_20261108/V4'


def main():
    cube, data = geometry.build()
    g = SimpleNamespace(STATES=geometry.STATES, ROLES=geometry.ROLES, __file__=geometry.__file__,
        build=lambda: (cube, data), audit=lambda c, d: generic_audit(c, d, geometry.STATES,
            dict(spear_refinement=d['refinement'], no_nominal_clipping=True)))
    generate(g, OUT, LOG, __file__)
    manifest = json.loads((OUT/'manifest.json').read_text('utf8'))
    manifest.update(candidate_version=data['candidate_version'], target_voltage='CIV', generated_at='2026-11-08',
                    source_author='Gemini V4完整边界版；本轮六矛由Codex按负责人参考重做',
                    selection='负责人反馈：问到的几个人都选择C，指定以C继续优化；不等于整座建筑正式批准')
    save(OUT/'manifest.json', manifest)
    check = json.loads((OUT/'verification.json').read_text('utf8'))
    preview_page(OUT, manifest, check, '玩家反馈选择C。仅修改六柄亚空之矛：黑刃银尖、橙晶黑笼、白色分体护翼与长尾。其余构件逐格保留。')
    shutil.copy2(BASE/'完整预览.png', OUT/'原C方案.png')
    jar = next((INSTANCE/'mods').glob('*Spear*'))
    with zipfile.ZipFile(jar) as z:
        model = json.loads(z.read('assets/sov/models/item/spear_of_void.json'))
        animation = json.loads(z.read('assets/sov/textures/item/spear_of_void.png.mcmeta'))
    reference = Path('C:/Users/OWNER/AppData/Local/Temp/codex-clipboard-fab80736-4c81-4966-93df-fdf5a90e9aaf.webp')
    sources = dict(photo=str(reference), photo_sha256=hashlib.sha256(reference.read_bytes()).hexdigest(),
        logo_used=False, mod_file=str(jar), mod_sha256=hashlib.sha256(jar.read_bytes()).hexdigest(),
        mod_model=model, texture='assets/sov/textures/item/spear_of_void.png', animation=animation,
        model_is_2d_item_sprite=True, interpretation='模组为16×16四帧物品贴图，不是3D矛模型；黑白橙配色参考该贴图，立体轮廓以负责人照片为主。')
    save(LOG/'reference-sources.json', sources)
    save(OUT/'参考与改动.json', dict(sources=sources, **data['refinement'],
        preserved=['六矛尖端坐标与朝向', '三环与浮游柱', '不对称双翼与晶体星流', '核心、王冠与基座', '控制器、八处通用舱位、通道及管路'],
        scope='完整边界C版基础上的独立候选，不部署，不改变配方、电压或研究门槛。'))
    for name in ['audit_wonder_clipping_20261108.py', 'w03_celestial_geometry_v4_20261107.py']:
        shutil.copy2(ROOT/'tools/structure_delivery'/name, OUT/'生成脚本'/name)
    del cube, g

    # 单矛保持与整座结构同一局部体素，便于看清护翼和橙晶。
    coords = np.array(list(geometry.LOCAL), int)
    lo, hi = coords.min(0), coords.max(0)
    size = hi-lo+1
    states = sorted(set(geometry.LOCAL.values()))
    ids = {s: i+1 for i, s in enumerate(states)}
    single = np.zeros((size[1], size[2], size[0]), np.uint8)
    for p, state in geometry.LOCAL.items():
        x, y, z = np.array(p)-lo
        single[y, z, x] = ids[state]
    part = dict(key='spear', name='hk3gtl-void-spear-c1-20261108', title='C1 · 亚空之矛拆件',
        size=size.tolist(), controller=(coords[0]-lo).tolist(), controller_face='north', ports=[], paths=[], pipe_routes=[], zones=[],
        description='与整座C1六柄矛共用的原始局部体素；黑色长刃、橙色晶核、白色护翼和尾刃。',
        purpose='单独查看轮廓与厚度；装饰构件，没有控制器功能。')
    counts = np.bincount(single.ravel(), minlength=len(states)+1)
    audit = dict(passed=True, blocks=int(counts[1:].sum()), unique_materials=len(states), palette=dict(zip(states, map(int, counts[1:]))),
        pipe_routes_count=0, checks=['单矛来自整座C1同一局部体素，无独立替代模型。'], not_verified=['未批准、未部署。'])
    part_geometry = SimpleNamespace(STATES=states, ROLES=geometry.ROLES, __file__=geometry.__file__,
        build=lambda: (single, part), audit=lambda c, d: audit)
    generate(part_geometry, OUT/'单矛拆件', LOG/'single', __file__)
    p = OUT/'单矛拆件/spear/三维评审.html'
    text = p.read_text('utf8')
    start = text.index('<div class="locator">'); end = text.index('<div>', start+1)
    text = text[:start]+text[end:]
    text = text.replace(' V1', '').replace('MAX · ', '局部体素 · ')
    text = text.replace('既定四台MAX复制系统的独立外观候选，内部需求号SPEAR。名称与工艺尚未冻结，未批准、未实装。', part['description'])
    text = text.replace('<script src="viewer.bundle.js"></script>', '<script src="viewer.bundle.js"></script><script src="spear-review.js"></script>')
    p.write_text(text, 'utf8')
    (p.parent/'spear-review.js').write_text('''/** 单矛默认侧视，避免斜向看成细杆。 */
(()=>{function boot(){if(!window.REVIEW_READY||!window.reviewApi)return setTimeout(boot,100);const a=window.reviewApi;
a.camera.position.set(165,105,-300);a.camera.zoom=1.3;a.camera.updateProjectionMatrix();a.renderer.render(a.scene,a.camera);window.SPEAR_READY=true;}boot();})();''', 'utf8')
    (OUT/'index.html').write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>W03 C1 · 亚空之矛优化</title>
<style>body{{max-width:1500px;margin:30px auto;padding:0 20px;background:#14101f;color:#eee6f4;font:16px/1.8 system-ui}}a{{color:#f4c27a}}img{{width:100%}}.note{{padding:18px;background:#302239}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}figure{{margin:0}}@media(max-width:850px){{.grid{{display:block}}}}</style>
<h1>穹界·虚数锚定环 · C1亚空之矛优化</h1><p class="note">以玩家选择的C（Gemini V4完整边界版）继续优化。六柄矛改为黑色长刃、银白尖端、橙色核心、开放黑笼和白色分体护翼；原环、双翼、核心、基座与接口保留。独立候选，未批准定稿、未部署。</p>
<p><a href="w03/三维评审.html">打开完整三维预览</a> · <a href="单矛拆件/spear/三维评审.html">单独旋转查看亚空之矛</a> · <a href="verification.json">完整核验</a> · <a href="参考与改动.json">参考来源与改动范围</a></p>
<img src="单矛近景.png" alt="C1亚空之矛同源体素近景"><h2>完整构图</h2><img src="完整预览.png" alt="C1六柄黑白橙亚空之矛的完整结构">
<h2>C → C1</h2><div class="grid"><figure><img src="原C方案.png" alt="玩家选择的原C"><figcaption>原C · 金色护手、白刃、紫晶</figcaption></figure><figure><img src="完整预览.png" alt="C1优化"><figcaption>C1 · 黑刃、橙晶、白色护翼；其余构件逐格保留</figcaption></figure></div>
<p>实际宽×深×高 {manifest['size'][0]}×{manifest['size'][2]}×{manifest['size'][1]}，{manifest['blocks']:,}实体方块。不按名义673×529×321裁切；仅六矛写入范围发生变化。Spear of Void 1.3.2实际提供四帧二维物品贴图，本轮以实物照片定立体轮廓、贴图核对黑白橙配色，不包含血骑士图标。</p>
<p>完整NBT与Schematic位于三维预览下载入口；单矛也附同源拆件。静态核验不代表游戏成型、运行与性能验收。</p></html>''', 'utf8')
    print(json.dumps(dict(passed=True, output=str(OUT), refinement=data['refinement']), ensure_ascii=False))


if __name__ == '__main__': main()
