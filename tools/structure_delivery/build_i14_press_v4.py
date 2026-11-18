# -*- coding: utf-8 -*-
"""I14 正梁锻心 V4：实际资源预览、结构导出与独立候选交付。
变更#1 2026-10-15 10:33:00：新增V4交付；固定增强版2.7资源来源，不改实例。
"""
import collections
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

import nbtlib
import build_i07_calibration_preview as preview
from build_i09_i13_redesign_v6 import lodestone_export
from build_i01_orthogonal_v8 import save_record
from i01_v8_gallery import orthographic
from i14_press_v4 import build
from redesign69_geometry import ROOT

OUT = ROOT / 'deliveries/I14_魂钢聚合压铸机_正梁锻心重设计_V4_20261015'
LOG = ROOT / 'logs/i14-press-v4'
INSTANCE = Path.home() / 'AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版 2.7/minecraft'
ARCHIVE = 'I14_V4_结构与预览.zip'


def bundle():
    target = OUT / ARCHIVE
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in sorted(OUT.rglob('*')):
            if p.is_file() and p != target:
                z.write(p, p.relative_to(OUT))
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None
        assert all(z.read(n) == (OUT/n).read_bytes() for n in z.namelist())
    return {'bytes': target.stat().st_size, 'sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
            'all_entries_equal_disk': True}


def write_page(data):
    blocks = f'{len(data["blocks"]):,}'
    page = '''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I14 · 魂钢聚合压铸机 · 正梁锻心 V4</title><style>
*{box-sizing:border-box}body{margin:0;background:#101722;color:#eef2f7;font:16px/1.85 'Microsoft YaHei',sans-serif}main{max-width:1320px;margin:auto;padding:46px 30px}small{color:#cbac75;letter-spacing:3px}h1{font-size:42px;line-height:1.3;margin:15px 0}p{color:#bac7d5;max-width:1080px}a{color:#d5bd94;text-decoration:none}a:hover{color:white}nav{display:flex;gap:24px;align-items:center;flex-wrap:wrap;margin:28px 0}.button{padding:10px 18px;border:1px solid #b19b78;border-radius:5px}.hero{display:block;border:1px solid #344055;border-radius:12px;overflow:hidden;background:#131a28}img{width:100%;display:block}.drawings{display:grid;grid-template-columns:1fr 1fr;gap:22px;margin-top:26px}.drawing{padding:18px;background:#182231;border:1px solid #344055;border-radius:10px}.drawing span{color:#c6b493;font-size:14px}.drawing img{margin-top:12px}.note{margin-top:30px;border-left:3px solid #9d8e72;padding:6px 18px;color:#91a3b7;font-size:14px}footer{font-size:14px;margin-top:25px;color:#91a3b7}@media(max-width:800px){main{padding:28px 18px}h1{font-size:30px}.drawings{grid-template-columns:1fr}}
</style></head><body><main><small>HK3GTL / I14 / V4</small><h1>魂钢聚合压铸机 · 正梁锻心</h1><p>深蓝灰的四柱压住平直厚梁，银色冲杆垂直落向一枚暖色坯芯。压板与下模之间留出的空气，让整座机器的力量有了方向。</p><p>'''+data['description']+'''</p><p>47 × 43 × 39（宽 × 深 × 高） · '''+blocks+''' 个实体方块 · 7 个主要设备分区。</p><nav><a class="button" href="三维评审.html">旋转与剖切结构 ↗</a><a href="'''+ARCHIVE+'''">下载结构与预览包</a><a href="'''+data['name']+'''.schem">Schematic</a><a href="'''+data['name']+'''.nbt">NBT</a><a href="设计与检查.json">设计与检查</a></nav><a class="hero" href="三维评审.html"><img src="等轴预览.png" alt="正梁四柱魂钢聚合压铸机，实际方块材质等轴图"></a><div class="drawings"><a class="drawing" href="正面立面.png"><span>北面立面 · 中央冲程与四柱框架</span><img src="正面立面.png" alt="正面立面"></a><a class="drawing" href="俯视布局.png"><span>俯视布局 · 中轴滚床与两侧工段</span><img src="俯视布局.png" alt="俯视布局"></a></div><p class="note">外观候选，接口用途和管线均为设计表达，尚未接入正式 Pattern。预览使用增强版 2.7 中实际方块纹理与静态模型；不模拟 Minecraft 光影。生成脚本依赖当前工作区工具链。</p><footer>2026-10-15 · V4 待审。<a href="结构参考.json">结构参考</a> · <a href="manifest.json">文件清单</a></footer></main></body></html>'''
    (OUT/'index.html').write_text(page, encoding='utf-8')


def main():
    LOG.mkdir(parents=True, exist_ok=True)
    data = build()
    anchor = data['controller']
    offset = [-v for v in anchor]
    data['construction_notes'] = {
        'origin': [0, 0, 0], 'paste_anchor': anchor, 'schematic_offset': offset,
        'orientation': 'X向东、Y向上、Z向南，主控朝北。',
        'recommended_bottom_world_y': -60, 'recommended_controller_world_y': -57,
        'world_height_range': [-60, -22],
        'status': 'V4正梁锻心外观候选，待用户审阅；未正式部署。',
        'survival_materials': '仅核验当前实例资源存在，不声明生存材料可达性。',
    }
    preview.TEST_INSTANCE = INSTANCE
    preview.package(data, OUT, 'i14', [
        '四柱及平直厚梁构成竖直承力轮廓，梁间保留屋顶开口',
        '主缸、冲杆、压板、空气、暖色坯芯与砧座沿中央力线分层',
        '前后滚床同轴，保温炉、双联蓄压站和尾液回收段独立',
        '左右维护道均有地面且保持四格净高'])
    nbt_sha = lodestone_export(data, OUT, LOG)
    schem_path = OUT/(data['name']+'.schem')
    s = nbtlib.load(schem_path)
    s['Offset'] = nbtlib.IntArray(offset)
    s.save(schem_path, gzipped=True)
    assert list(map(int, nbtlib.load(schem_path)['Offset'])) == offset

    record = json.loads((OUT/'设计与检查.json').read_text(encoding='utf-8'))
    audit = record['audit']
    markers = ('minecraft:diamond_block', 'hk3gtl:industrial_port_casing')
    ordinary = collections.Counter(q['state'].split(':')[0] for q in data['blocks'] if q['state'] not in markers)
    audit.update(
        hashes={'nbt': nbt_sha, 'schem': hashlib.sha256(schem_path.read_bytes()).hexdigest()},
        namespace_counts=dict(ordinary),
        namespace_percent={k: round(v/sum(ordinary.values())*100, 2) for k, v in ordinary.items()},
        design_markers=dict(collections.Counter(q['state'] for q in data['blocks'] if q['state'] in markers)),
        reference_report='结构参考.json', approval='V4待审，未部署', schematic_offset=offset)
    assert audit['design_markers'] == {'minecraft:diamond_block': 1, 'hk3gtl:industrial_port_casing': 6}
    audit['checks'] += ['Lodestone导出与蓝图逐格一致', 'Sponge粘贴锚点对应主控', '主控周围八格白框完整']
    audit['not_verified'] = [
        '待用户外观确认', '浏览器交互验证另记logs，不以离线渲染代替',
        '未接入正式Pattern或配方', '未进行Minecraft成型或生产验收',
        '未验证生存获取路线', '未测试整包内存或光影表现']
    payload = save_record(OUT, record)
    orthographic(data, payload['materials'], OUT)
    page = (OUT/'三维评审.html').read_text(encoding='utf-8')
    page = page.replace('href="设计与检查.json"', 'href="index.html"').replace('← 设计与检查', '← 正梁锻心')
    page = page.replace('自由设计候选', '正梁锻心 V4 候选')
    page = page.replace('未接入生产Pattern，未实测浏览器交互或游戏。', '外观候选，尚未接入正式Pattern；游戏成型与生产待验收。')
    (OUT/'三维评审.html').write_text(page, encoding='utf-8')

    reference = {
        '机器': 'I14 魂钢聚合压铸机', '版本': 'V4 正梁锻心',
        '现实设备转译': ['四柱液压压机的竖直受力轴', '直线滚床与独立保温炉', '双联蓄压站与开放板式冷却段'],
        '模组参考': [
            {'来源': '当前实例GTCEu装配线', '取用': '轴向加工节奏与驱动分层'},
            {'来源': '当前实例GTLCore PCB工厂', '取用': '独立工段与低位总管'},
        ],
        '本地参考证据': 'logs/i09-i13-redesign-v6/reference-study.json，及本轮实际资源逐种解析',
        '与V3区别': ['拱形曲冠改为平直厚梁', '暖色集中在保温炉与模芯', '区分移动压板、冲程空气和下模', '散热片等高且低于压机'],
        '限制': '原创候选，不复制第三方Pattern；未使用未安装GTLsupb的方块，不声明正式工艺。',
    }
    (OUT/'结构参考.json').write_text(json.dumps(reference, ensure_ascii=False, indent=2), encoding='utf-8')
    source = OUT/'生成脚本'
    source.mkdir(exist_ok=True)
    for name in ('i14_press_v4.py', 'build_i14_press_v4.py', 'verify_i14_press_v4.py'):
        p = ROOT/'tools/structure_delivery'/name
        if p.exists():
            shutil.copy2(p, source/name)
    write_page(data)
    summary = {
        'key': data['key'], 'title': data['title'], 'version': data['candidate_version'],
        'size_xyz': data['size'], 'blocks': len(data['blocks']), 'controller': anchor,
        'ports': data['ports'], 'paths': data['paths'], 'ordinary_counts': dict(ordinary),
        'markers': audit['design_markers'], 'hashes': audit['hashes'],
        'size_baseline': audit['size_baseline'], 'materials': len(payload['materials']),
        'resource_instance': str(INSTANCE), 'status': '外观待审，不部署',
    }
    (OUT/'manifest.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    summary['archive'] = bundle()
    (LOG/'final-verification.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == '__main__':
    main()
