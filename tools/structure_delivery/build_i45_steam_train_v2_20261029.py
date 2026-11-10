# -*- coding: utf-8 -*-
"""I45蒸汽列车候选：真实材质、完整逐格导出及独立审阅报告。"""
import base64
import datetime as dt
import gzip
import hashlib
import html
import io
import json
from pathlib import Path
import shutil
from PIL import Image, ImageStat
import i45_steam_train_geometry_v2_20261029 as geometry
from i45_steam_train_audit_v2_20261029 import audit
import build_i25_world_bubble_observatory_20261025 as resources
from i34_open_observatory_export_20261027 import export_dense
from i37_surface_runs_20261027 import merge_surface_runs

ROOT = geometry.ROOT
OUT = ROOT / 'deliveries/I45_仿制的千界一乘列车_黑金蒸汽机车与双节旅客车_V2_20261029'
LOG = ROOT / 'logs/i45-steam-train-v2-20261029'


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def report(data, check):
    esc = html.escape
    p = check['voltage_progression']
    comparison = ''.join(f'<tr><td>{label}</td><td>{p["metrics"][key]:,}</td><td>{p["lower_maxima"][key]["value"]:,}</td><td>通过</td></tr>' for key, label in [('blocks', '实体'), ('materials', '普通材料'), ('volume', '真实包围盒'), ('height', '高度')])
    materials = ''.join(f'<tr><td><code>{esc(s)}</code></td><td>{n:,}</td><td>{esc(geometry.ROLES[s])}</td></tr>' for s, n in check['palette'].items())
    ports = ''.join(f'<tr><td>{esc(x["id"])}</td><td>{x["pos"]}</td><td>{x["face"]}</td><td>{esc(x["role"])}</td></tr>' for x in data['ports'])
    return f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I45 · 黑金蒸汽机车与双节旅客车 V2</title><style>
body{{max-width:1380px;margin:32px auto;padding:0 24px;background:#111b28;color:#e5edf6;font:16px/1.8 system-ui}}h1{{line-height:1.35}}a{{color:#9adce4}}.note{{padding:16px;border-left:4px solid #8fa2db;background:#232c40}}img{{width:100%;display:block}}table{{width:100%;border-collapse:collapse}}td,th{{padding:10px;border-bottom:1px solid #425466;text-align:left;overflow-wrap:anywhere}}code{{overflow-wrap:anywhere}}.links{{display:flex;gap:18px;flex-wrap:wrap}}.table{{overflow:auto}}small,figcaption{{color:#acbed2}}figure{{margin:24px 0}}
</style><small>HK3GTL · I45 · QCV / V06 / tier20 · V2独立待审候选</small><h1>仿制的千界一乘·列车<br>黑金蒸汽机车与双节旅客车</h1>
<p class="note">121×821×181（宽×长×高），{check['blocks']:,}个实体方块、{check['ordinary_materials']}种普通材料。黑色金属车皮、薄金边与白银前部识别纹，配合卧式锅炉、巨大动轮、连杆、煤水车和两节旅客车；固定多方块旅行装置，未批准、未安装。</p>
<nav class="links"><a href="i45/三维评审.html">真实MC材质三维评审</a><a href="完整预览.png">完整预览</a><a href="列车侧后方.png">列车侧后方</a><a href="列车俯视.png">列车俯视</a><a href="主控材质近景.png">主控材质近景</a><a href="verification.json">完整核验记录</a></nav>
<figure><a href="i45/三维评审.html"><img src="完整预览.png" alt="黑金蒸汽机车、煤水车和双节客车完整真实方块预览"></a><figcaption>沿同一组固定轨道编组。蒸汽机车造型为本轮负责人指定的工业化演绎，不声称复刻原作尺寸或实现移动载具。</figcaption></figure>
<h2>一眼能辨认的蒸汽列车</h2><p>圆形烟箱和卧式锅炉位于前端，锅炉腰部仅用细金属箍束分段；高处是短烟囱与汽笛，不堆孤立塔来增高。下部四对辐条动轮、轮圈、曲柄与连杆落在实际轮轨高度上。驾驶室接续火箱，后方煤水车有开放煤堆及独立水箱；两节带窗旅客车保留座席、中央通道和固定贯通段。</p><p>列车长821格来自锅炉、驾驶室、煤水补给与两节有实际内部空间的旅客车，未通过空轨或填满场地扩大边界。轨心X25/X95，轨距70格，钢轨各宽5格；轨顶和轮底均Y5，常规车体宽95格，总宽121格含前铲和踏板。可与I44站台协调，但两台仍为独立候选。</p>
<h2>I44交接坐标，I45执行获许可旅行</h2><p>按最新v6职责，I45接收I44有效坐标、传送能量和玩家，出发前核对授权与能量，输出允许目的维度的抵达确认及旅行记录，并处理失败恢复。列车保持固定不移动，不新增神之键或非法目的维度；生命跨平行宇宙运输限制与终审维度禁行边界继续生效。</p><p>煤、水、蒸汽设备表现本轮指定的外观；不以外观擅自添加正式燃料配方、旅行能耗或运行能力。全部真实运行逻辑、Pattern、权限和生存获取仍需后续实装验收。</p>
<h2>主控与接口沿实际车体内嵌</h2><p>唯一主控位于烟箱正前面蓝图XYZ <code>{data['controller']}</code>，整宽第61格，朝北，周围是连续烟箱实体；没有外挂面板或托接口柱。八接口嵌于煤水车、驾驶室和客车的实际外壳，保留内背板、周边四格连续壳体及五格外侧净空。</p><div class="table"><table><tr><th>接口</th><th>XYZ</th><th>朝向</th><th>设备用途</th></tr>{ports}</table></div><p>工业接口块仅作候选位置标记，正式仓室替换、必要能力和数据交接合同单独核验。</p>
<figure><img src="列车侧后方.png" alt="列车侧后方及两节客车"><figcaption>客车与煤水车各有自己的内腔；所有轮对与轨道采用一致标高。</figcaption></figure>
<h2>QCV与低阶全部形态逐项比较</h2><p>本机映射独立核对为QCV/V06/tier20。历史最低25×97×29是下限，不是尺寸上限；真实包围盒{check['bounding_box_volume']:,}格³。重新核验全部{p['lower_form_count']}个已批准QCV低阶的正式元数据及蓝图哈希，四项指标严格递增。比较不包含未批准草稿或同阶建筑。</p><div class="table"><table><tr><th>指标</th><th>I45</th><th>全部低阶最大值</th><th>结果</th></tr>{comparison}</table></div>
<h2>原作黑金配色，I45专项外观例外</h2><p>负责人原话：<q>{esc(check['appearance_exception']['user_quote'])}</q>。仅本台I45列车豁免对应电压机壳必须最多，I44车站不适用；电压仍为QCV/V06/tier20，其他递进和检查全部保留。以原作参考的黑色车皮、薄金边与白银前部识别为依据，蒸汽火车仍为工业化演绎。</p><p>实际黑色金属主材<code>{geometry.material.BLACK}</code>共{check['black_main_material']['count']:,}格，为最多单一材料；已核验目标实例原始纹理，没有改色或替换材质源图。QCV机壳{check['qcv_casing_count']:,}格用于内部传送供能电压组件。{check['ordinary_materials']}种普通材料各有实际用途，主控与8接口另列。项目方块仅QCV机壳和工业接口白名单，其余来自目标增强版2.9.2的真实完整方块；生存阶段获取状态仍未验收。</p><details><summary>全部材料与用途</summary><div class="table"><table><tr><th>状态ID</th><th>数量</th><th>职责</th></tr>{materials}</table></div></details><p><a href="参考/千界一乘.webp">负责人提供的原作参考图</a> · <a href="黑色主材核验.json">真实黑色主材核验</a></p>
<h2>完整导出与离线预览</h2><p><a href="i45/{data['name']}.nbt">完整NBT</a> · <a href="i45/{data['name']}.schem">完整Schematic</a>。原始几何、NBT和Schematic逐格一致；真实外露面连续合并并重新展开核对。预览使用MC真实纹理逐格重复、分帧初始化及静止按需绘制，不缩小几何、不使用纯色代替纹理。9种视角、剖切、玻璃、材质与逐接口定位均可直接离线操作。</p>
<p class="note">当前I45候选未批准、未安装；I44火车站由另一个独立候选交付，I43仍待审；batch-10仍为I40/I41/I42三台，3/5。I37继续留最后。PC/FCL三场景内存与完整游戏运行测试，待全部建筑完成后执行。</p><footer><small>变更记录 #2 · 2026-10-29：按原作参考及负责人I45专项例外，改为真实黑色金属主车皮、薄金箍带与白银前部识别纹。保留V1、蒸汽几何及原位主控接口；不改实例、正式Pattern或批准索引。</small></footer></html>'''


def main():
    OUT.mkdir(parents=True, exist_ok=True); LOG.mkdir(parents=True, exist_ok=True)
    view = OUT / 'i45'; view.mkdir(exist_ok=True)
    print('生成I45固定蒸汽列车，核验轮轨、接口与24个低阶…', flush=True)
    cube, data = geometry.build(); check = audit(cube, data)
    version = json.loads((resources.INSTANCE.parent/'mrpack/modrinth.index.json').read_text(encoding='utf-8'))['versionId']
    assert version == '2.9.2'
    materials, sources, packs = resources.resource_materials(geometry.STATES)
    assert all(x['complete_cube'] and not x['tinted'] for x in materials)
    black = next(x for x in materials if x['state'] == geometry.material.BLACK)
    texture_bytes = base64.b64decode(black['faces']['north'].split(',')[1])
    texture = Image.open(io.BytesIO(texture_bytes)).convert('RGB')
    mean = ImageStat.Stat(texture).mean
    assert max(mean) < 80 and max(mean)-min(mean) < 12
    reference = Path.home() / '下載/千界一乘.webp'
    assert reference.is_file()
    (OUT/'参考').mkdir(exist_ok=True)
    shutil.copy2(reference, OUT/'参考/千界一乘.webp')
    black_evidence = dict(state=geometry.material.BLACK, complete_cube=black['complete_cube'], tinted=black['tinted'],
        mean_rgb=mean, north_texture_png_sha256=hashlib.sha256(texture_bytes).hexdigest(), model=black['model'],
        resource_sources={k:v for k,v in sources.items() if 'netherite_block' in k},
        source_texture_modified=False, reference='参考/千界一乘.webp', reference_sha256=hashlib.sha256(reference.read_bytes()).hexdigest(),
        appearance_exception=check['appearance_exception'], voltage='QCV / V06 / tier20',
        reference_label='用户提供的视觉参考，不宣称原作官方资源授权')
    save(OUT/'黑色主材核验.json', black_evidence)
    check['black_material_verification'] = black_evidence
    print('真实材质通过，导出完整NBT/Schematic并逐格回读…', flush=True)
    result = export_dense(cube, geometry.STATES, data['name'], view)
    assert result['block_count'] == check['blocks']
    raw = result['surface_groups']
    check.update(nbt_schem_sha256=result['hashes'], readback=result['readback'],
        viewer_surface_faces=sum(len(face) for group in raw for face in group), source_instance=str(resources.INSTANCE),
        instance_version=version, material_resource_sources=sources, enabled_file_resource_packs=packs)
    groups, lengths, merged = merge_surface_runs(raw, data['size'])
    check.update(viewer_surface_merge=merged, viewer_rendered_quads=merged['rendered_quads'])
    counts = dict.fromkeys(['GTCEu', 'GTL Core', '其他模组', '原版', '项目QCV主机壳', '主控标记', '工业接口标记'], 0)
    for state, count in check['palette'].items():
        if state == geometry.material.CONTROL: group = '主控标记'
        elif state == geometry.material.PORT: group = '工业接口标记'
        elif state == geometry.material.QCV: group = '项目QCV主机壳'
        elif state.startswith('gtceu:'): group = 'GTCEu'
        elif state.startswith('gtlcore:'): group = 'GTL Core'
        elif state.startswith('minecraft:'): group = '原版'
        elif state.startswith('hk3gtl:'): raise ValueError(('非白名单项目方块', state))
        else: group = '其他模组'
        counts[group] += count
    check['material_source_counts'] = counts
    payload = dict(data=data, palette=geometry.STATES, surfaceGroups=groups, surfaceRunLengths=lengths,
        blockCount=check['blocks'], materials=materials, audit=check, names={s: s.split(':')[1] for s in geometry.STATES})
    compressed = gzip.compress(json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), 6)
    (view/'data.js').write_text('window.HK3_PAYLOAD='+json.dumps(base64.b64encode(compressed).decode('ascii'))+';', encoding='utf-8')
    check['viewer_payload_gzip_bytes'] = len(compressed)
    save(OUT/'manifest.json', dict(data, approved=False, installed=False, game_verified=False,
        status='candidate_waiting_user_review', target_voltage='QCV', voltage_mapping='V06 / tier20',
        appearance_exception=check['appearance_exception'], black_main_material=check['black_main_material'],
        blocks=check['blocks'], unique_materials=len(materials), ordinary_materials=check['ordinary_materials'],
        source_instance=str(resources.INSTANCE), instance_version=version,
        generated_at=dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat(timespec='seconds')))
    save(OUT/'verification.json', check)
    save(OUT/'材料清单.json', [dict(state=x['state'], count=check['palette'][x['state']], role=geometry.ROLES[x['state']],
        complete_cube=x['complete_cube'], source=sources.get(x['state'], {}), survival_stage_verified=False) for x in materials])
    save(LOG/'lower-voltage-evidence.json', check['voltage_progression'])
    (OUT/'index.html').write_text(report(data, check), encoding='utf-8')
    scripts = OUT/'生成脚本'; scripts.mkdir(exist_ok=True)
    for name in ('i45_steam_train_geometry_v2_20261029.py', 'i45_steam_train_audit_v2_20261029.py',
                 'build_i45_steam_train_v2_20261029.py', 'i44_voltage_progression_20261029.py'):
        shutil.copy2(ROOT/'tools/structure_delivery'/name, scripts/name)
    print(json.dumps(dict(output=str(OUT), blocks=check['blocks'], rendered_quads=merged['rendered_quads']), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
