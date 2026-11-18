# -*- coding: utf-8 -*-
"""I14曲冠压铸机V3的独立结构、真实材质图与三维候选交付。"""
import base64
import collections
import datetime
import gzip
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
from i14_press_v3 import build
from redesign69_geometry import ROOT

OUT=ROOT/'deliveries/I14_魂钢聚合压铸机_曲冠重设计_V3_20261015'
LOG=ROOT/'logs/i14-press-v3'
INSTANCE=Path.home()/'AppData/Roaming/PrismLauncher/instances/GTL十一周目/minecraft'


def bundle():
    target=OUT/'I14_V3_结构与预览.zip'
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(OUT.rglob('*')):
            if p.is_file() and p != target:z.write(p,p.relative_to(OUT))
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None
        for name in z.namelist():assert z.read(name)==(OUT/name).read_bytes()
    return {'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
            'all_entries_equal_disk':True}


def main():
    LOG.mkdir(parents=True,exist_ok=True)
    data=build();anchor=data['controller'];offset=[-q for q in anchor]
    data['construction_notes']={'origin':[0,0,0],'paste_anchor':anchor,'schematic_offset':offset,
        'orientation':'X向东、Y向上、Z向南，主控正面朝北。',
        'recommended_bottom_world_y':-60,'recommended_controller_world_y':-57,
        'world_height_range':[-60,-18], 'status':'V3外观候选，尚未获用户确认；未正式部署。',
        'survival_materials':'沿用用户自由建筑选材授权；不声明生存配方可达性。'}
    preview.TEST_INSTANCE=INSTANCE
    preview.package(data,OUT,'i14',['四柱及双道曲冠构成独立承力轮廓',
        '压板与下模之间保留真实空气，直线输送床前后贯通','局部设备基础及两侧检修空间'])
    sha=lodestone_export(data,OUT,LOG)
    schem_path=OUT/(data['name']+'.schem');s=nbtlib.load(schem_path)
    s['Offset']=nbtlib.IntArray(offset);s.save(schem_path,gzipped=True)
    assert list(map(int,nbtlib.load(schem_path)['Offset']))==offset
    record=json.loads((OUT/'设计与检查.json').read_text(encoding='utf-8'))
    a=record['audit'];markers=('minecraft:diamond_block','hk3gtl:industrial_port_casing')
    ordinary=collections.Counter(q['state'].split(':')[0] for q in data['blocks'] if q['state'] not in markers)
    a.update(hashes={'nbt':sha,'schem':hashlib.sha256(schem_path.read_bytes()).hexdigest()},
        namespace_counts=dict(ordinary),namespace_percent={k:round(v/sum(ordinary.values())*100,2) for k,v in ordinary.items()},
        design_markers=dict(collections.Counter(q['state'] for q in data['blocks'] if q['state'] in markers)),
        reference_report='结构参考.json',approval='待用户审阅V3外观，未部署',schematic_offset=offset)
    assert a['design_markers']=={'minecraft:diamond_block':1,'hk3gtl:industrial_port_casing':6}
    a['checks']+=['Lodestone导出逐格回读一致','Sponge粘贴锚点对应主控','主控周围八格白色框完整']
    state={tuple(q['pos']):q['state'] for q in data['blocks']}
    for x in range(anchor[0]-1,anchor[0]+2):
        for y in range(anchor[1]-1,anchor[1]+2):
            if [x,y,anchor[2]]!=anchor:assert state[x,y,anchor[2]]=='gtceu:clean_machine_casing'
    a['not_verified']=['待用户外观确认','尚未实际操作浏览器交互','未接入正式Pattern或配方',
        '未进行Minecraft实际成型与运行验收','未验证生存获取路线']
    payload=save_record(OUT,record)
    orthographic(data,payload['materials'],OUT)
    page=(OUT/'三维评审.html').read_text(encoding='utf-8')
    page=page.replace('href="设计与检查.json"','href="index.html"').replace('← 设计与检查','← 曲冠压铸机')
    page=page.replace('自由设计候选','V3 曲冠压铸候选')
    (OUT/'三维评审.html').write_text(page,encoding='utf-8')
    reference=json.loads((ROOT/'logs/i09-i13-redesign-v6/reference-study.json').read_text(encoding='utf-8'))
    reference['本轮转译']={'机器':'I14 魂钢聚合压铸机','候选':'曲冠重设计V3',
        '取用原则':['装配床与驱动分层','独立热工与冷却辅助设备','弧形支架与加工内核之间留出空气'],
        '原创构图':'四柱收腰、双曲冠承力、外露中央冲头、直线入料与脱模、偏置坩埚和蓄压罐',
        '边界':'复用已核验三模组JAR参考证据；新设计不是其Pattern复制。'}
    (OUT/'结构参考.json').write_text(json.dumps(reference,ensure_ascii=False,indent=2),encoding='utf-8')
    source=OUT/'生成脚本';source.mkdir(exist_ok=True)
    files=['i14_press_v3.py','build_i14_press_v3.py','verify_i14_press_v3.py','i09_i13_v6_common.py','redesign69_geometry.py',
        'build_i07_calibration_preview.py','build_i03_centrifuge_preview.py','build_i01_tidal_preview.py',
        'build_i01_tianming_preview.py','build_redesign69.py','material_resources.py','structure_size_baseline.py',
        'build_i09_i13_redesign_v6.py','build_i01_orthogonal_v8.py','i01_v8_gallery.py','i01_i08_v7_gallery.py',
        'l1-review89-recipe.mjs']
    for name in files:
        p=ROOT/'tools/structure_delivery'/name
        if p.exists():shutil.copy2(p,source/name)
    title=data['title'];desc=data['description']
    webpage='''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I14 魂钢聚合压铸机 · 曲冠 V3</title><style>
body{margin:0;background:#101823;color:#eef2f7;font:16px/1.9 'Microsoft YaHei',sans-serif}main{max-width:1240px;margin:auto;padding:40px 28px}small{color:#ccac77;letter-spacing:3px}h1{font-size:40px;margin:10px 0}p{max-width:940px;color:#bbcad8}nav{display:flex;gap:25px;flex-wrap:wrap;margin:24px 0}a{color:#d2c09c;text-decoration:none}a:hover{color:white}img{width:100%;border-radius:12px;background:#17202c}.drawings{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:24px}.button{padding:10px 18px;border:1px solid #9b927f;border-radius:6px}footer{color:#90a2b4;font-size:14px;margin-top:25px}@media(max-width:800px){h1{font-size:28px}.drawings{grid-template-columns:1fr}}</style></head><body><main><small>HK3GTL / I14 / V3</small><h1>魂钢聚合压铸机 · 四柱曲冠</h1><p>'''+desc+'''</p><p>51 × 47 × 43（宽 × 深 × 高） · '''+f'{len(data["blocks"]):,}'+''' 个实体方块。四柱、双曲冠和外露压铸芯构成主体；熔料与液压设备分别位于两侧。</p><nav><a class="button" href="三维评审.html">旋转与剖切结构 ↗</a><a href="I14_V3_结构与预览.zip">下载完整结构包</a><a href="'''+data['name']+'''.schem">Schematic</a><a href="'''+data['name']+'''.nbt">NBT</a><a href="设计与检查.json">设计与检查</a></nav><a href="三维评审.html"><img src="等轴预览.png" alt="四柱曲冠压铸机真实材质等轴图"></a><div class="drawings"><img src="正面立面.png" alt="正面立面"><img src="俯视布局.png" alt="俯视工艺分区"></div><footer>2026-10-15 · 外观候选，尚未批准或正式部署。材质/文件检查不代替游戏成型与运行验收。</footer></main></body></html>'''
    (OUT/'index.html').write_text(webpage,encoding='utf-8')
    summary={'key':'i14','title':title,'size_xyz':data['size'],'blocks':len(data['blocks']),
        'controller':anchor,'ports':data['ports'],'paths':data['paths'],'ordinary_counts':dict(ordinary),
        'markers':a['design_markers'],'nbt_sha256':sha,'schem_sha256':a['hashes']['schem'],
        'actual_size_baseline_passed':a['size_baseline']['passed'],'materials':len(a['palette']),
        'six_face_connected':True,'status':'外观待审，不部署'}
    (OUT/'manifest.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    summary['archive']=bundle()
    (LOG/'final-verification.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False))


if __name__=='__main__':main()
