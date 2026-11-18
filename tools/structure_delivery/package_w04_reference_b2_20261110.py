# -*- coding: utf-8 -*-
"""复用完整导出与表面预览，补齐B2参考证据和B1历史校验。"""
from pathlib import Path
import json
import shutil
import package_w04_gemini_b1_20261110 as base
import w04_reference_geometry_b2_20261110 as g


def main():
    g.LOG.mkdir(exist_ok=True)
    before=base.hashes(g.PRIOR);base.save(g.LOG/'b1-before-hashes.json',before)
    base.g=g;base.main()
    assert before==base.hashes(g.PRIOR),'B1历史被改写'
    viewer=g.OUT/'生成脚本/viewer.mjs';source=viewer.read_text('utf8')
    source=source.replace("if(name==='orthofront')direction.set(0,0,1);", "if(name==='orthofront'||name==='dragonfront')direction.set(0,0,1);\n    if(name==='dragonside')direction.set(1,0,0);")
    viewer.write_text(source,'utf8')
    data=json.loads((g.OUT/'manifest.json').read_text('utf8'))
    page=(g.OUT/'w04/三维评审.html').read_text('utf8')
    page=page.replace('Gemini B1','图片校准B2').replace('B1 · 俱利伽罗盘枢','B2 · 图片校准')
    page=page.replace('← B1与A1对照','← B2与参考图')
    page=page.replace('<button data-view="sword">巨刃近景</button>',
        '<button data-view="sword">七雷近景</button><button data-view="wing">翼爪近景</button><button data-view="body">龙体近景</button>')
    page=page.replace('Gemini第二候选，全部静态。', '44张分源参考校准的B2，全部静态。')
    (g.OUT/'w04/三维评审.html').write_text(page,'utf8')
    page=(g.OUT/'index.html').read_text('utf8')
    page=page.replace('Gemini俱利伽罗盘枢B1','俱利伽罗与七雷·图片校准B2')
    page=page.replace('俱利伽罗 · 盘枢B1','俱利伽罗与七雷 · 图片校准B2')
    page=page.replace('Gemini第二候选','Gemini场景·图片校准B2')
    page=page.replace('Gemini B1：鬼手锁三环、倒悬巨刃、俱利伽罗盘枢','B2：白角V形面甲、叠甲长颈与刃状翼爪；修长紫色七雷')
    page=page.replace('<p><a href="w04/三维评审.html">',
        '<p><a href="参考图总览.html">打开44张分源参考图集</a> · <a href="../'+g.PRIOR.name+'/index.html">保留的B1对照</a></p><p><a href="w04/三维评审.html">',1)
    page=page.replace('<img src="完整预览.png" alt="W04 Gemini B1完整预览">',
        '<p class="note">参考共44张：20张官方教学原帧、19张玩家游戏原帧、5张社区转存图。不同姿态与局部不等于44个独立机位；两张低清社区图仅作辅助。盘枢长尾、额外扣环前肢与工业连接为场景转译，遮挡处尚待核对。</p><p>改动7个构件：七雷、龙躯、双翼、龙首和双前爪。其余13个构件逐格保持B1。超限武器以游戏界面的「涤罪七雷·鸣雷见」为准；「鸣雷神」为技能名。B1的宽三角剑、圆盘刀锷、红色网格翼已退出本候选。</p><img src="完整预览.png" alt="W04图片校准B2完整预览">')
    page=page.replace('全静态。A1全部原文件保持不变。','全静态。A1与B1全部原文件保持不变。')
    page=page.replace('动画关闭。A1全部原文件保持不变。','动画关闭。A1与B1全部原文件保持不变。')
    page=page.replace('</html>','<h2>图片校准后的独立构件</h2><div class="grid"><figure><img src="巨刃近景.png" alt="涤罪七雷"><figcaption>修长紫色弯刃、镂空护手与白色柄带</figcaption></figure><figure><img src="翼爪近景.png" alt="俱利伽罗翼爪"><figcaption>红色分体刃爪与内侧暗色翼膜</figcaption></figure></div></html>')
    (g.OUT/'index.html').write_text(page,'utf8')
    verification=json.loads((g.OUT/'verification.json').read_text('utf8'))
    verification.update(b1_unchanged=True,reference_images=44,unchanged_components=13,replaced_components=7)
    base.save(g.OUT/'verification.json',verification)
    for file in [Path(__file__),Path(g.__file__),g.ROOT/'tools/structure_delivery/collect_w04_references_20261110.py',
        g.ROOT/'tools/structure_delivery/package_w04_gemini_b1_20261110.py',
        g.ROOT/'tools/structure_delivery/w04_gemini_dragon_b1_20261110.py']:
        shutil.copy2(file,g.OUT/'生成脚本'/file.name)
    base.save(g.LOG/'b1-preservation.json',dict(passed=before==base.hashes(g.PRIOR),files=len(before)))
    print(json.dumps(dict(passed=True,size=data['size'],blocks=data['blocks'],b1_unchanged=True)))


if __name__=='__main__':main()
