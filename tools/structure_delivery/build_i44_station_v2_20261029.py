# -*- coding: utf-8 -*-
"""I44候选：真实目标实例材质、完整结构与纯HTML评审交付。"""
import base64
import datetime as dt
import gzip
import html
import json
import shutil
import i44_station_geometry_v2_20261029 as geometry
from i44_station_audit_v2_20261029 import audit
import build_i25_world_bubble_observatory_20261025 as resources
from i34_open_observatory_export_20261027 import export_dense
from i37_surface_runs_20261027 import merge_surface_runs

ROOT = geometry.ROOT
OUT = ROOT / 'deliveries/I44_仿制的千界一乘信标_穹顶站台与坐标调度总站_V2_20261029'
LOG = ROOT / 'logs/i44-station-v2-20261029'


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def report(data, check):
    esc = html.escape
    p = check['voltage_progression']
    rows = ''.join(f'<tr><td><code>{esc(s)}</code></td><td>{n:,}</td><td>{esc(geometry.ROLES[s])}</td></tr>' for s,n in check['palette'].items())
    comparison = ''.join(f'<tr><td>{label}</td><td>{p["metrics"][key]:,}</td><td>{p["lower_maxima"][key]["value"]:,}</td><td>通过</td></tr>' for key,label in [('blocks','实体方块'),('materials','普通材料'),('volume','真实包围盒体积'),('height','高度')])
    return f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I44 V2 · 穹顶站台与坐标调度总站</title><style>
body{{max-width:1280px;margin:32px auto;padding:0 24px;background:#111b28;color:#e5edf6;font:16px/1.8 system-ui}}h1{{line-height:1.35}}a{{color:#9adce4}}.note{{padding:16px;border-left:4px solid #8fa2db;background:#232c40}}img{{width:100%;display:block}}table{{width:100%;border-collapse:collapse}}td,th{{padding:10px;border-bottom:1px solid #425466;text-align:left;overflow-wrap:anywhere}}.links{{display:flex;gap:18px;flex-wrap:wrap}}small{{color:#a9bad0}}figure{{margin:24px 0}}code{{overflow-wrap:anywhere}}
</style><small>HK3GTL · QCV / V06 / tier20 · I44 V2 · 待审外观候选</small>
<h1>仿制的千界一乘·信标<br>穹顶站台与坐标调度总站</h1>
<p class="note">负责人指定：信标做火车站，千界一乘列车做蒸汽火车。本站是I44独立坐标信标；I45是另一台固定蒸汽列车。站房登记、复测、锁定和调度目的地，列车执行既定获准旅行。</p>
<div class="links"><a href="i44/三维评审.html">真实MC材质三维预览</a><a href="完整预览.png">全景</a><a href="车站后方.png">后方站台</a><a href="车站俯视.png">俯视</a><a href="主控材质近景.png">主控近景</a><a href="verification.json">结构核验</a></div>
<figure><a href="i44/三维评审.html"><img src="完整预览.png" alt="I44车站式信标全景"></a></figure>
<h2>让车站真正像车站</h2><p>宽281、深741、高209，{check['blocks']:,}个实体。前部站房以大型站钟、双侧入口和内嵌坐标柜建立正面识别；两翼分别承接坐标复测、无人任务、供能与冷却。后部大跨度弧形雨棚覆盖双侧站台和贯通中央股道，浅银拱肋、深靛蓝承力带和玻璃透光条共同定义轮廓。站台有座椅、目的地指示牌、检修步道、照明与两端测定工位。</p>
<p>雨棚曲面由逐格阶梯、连续立面和落地拱脚组成，所有构件六邻接单连通。顶端来自雨棚自身，不追加凑高度的孤塔。轨心距70格；中部保留123格车体净宽，配套列车可独立布置，超出雨棚的车厢可处于露天股道。本轮不将两个多方块合并为同一Pattern。</p>
<h2>职责与造型决定</h2><p>I25解析坐标，I44登记、复测、锁定并交接目的地；I45固定列车执行已有许可旅行。本站按负责人指定采用火车站形式，是项目建筑设计，不宣称原作信标建筑的逐形复刻。没有新增神之键、维度、非法目标或移动列车实体。</p>
<h2>主控与接口自然融入站房</h2><p>主控蓝图XYZ <code>{data['controller']}</code>，整宽281格的第141格，从1起算为[141,15,17]，嵌在正面中央坐标登记柜的连续墙面。8个工业接口对称嵌入两翼真实设备外壁；有内背板、四周连续壳体和5格外侧净空。预览用1格钻石标主控，通用工业方块标接口。正式能力和仓室替换另验。</p>
<h2>QCV主机壳及低阶比较</h2><p>QCV主机壳{check['qcv_casing_count']:,}格，为最多单材。共25材料，排除主控和接口标记后为23种普通材料；配色取目标增强版2.9.2真实贴图。对24个较低电压批准形态重新统计并核对哈希，四项严格递增通过；同阶不强制排序，体积来自实际边界，不是空白声明。</p><table><tr><th>指标</th><th>本站</th><th>低阶最大</th><th>比较</th></tr>{comparison}</table>
<details><summary>25种材料及构件用途</summary><table><tr><th>方块</th><th>数量</th><th>用途</th></tr>{rows}</table></details>
<h2>完整结构与离线预览</h2><p><a href="i44/{data['name']}.nbt">完整NBT</a> · <a href="i44/{data['name']}.schem">Schematic</a>。两种导出逐格回读一致；真实MC材质逐格重复，外露面合并后仍保持原始坐标，按需绘制、分帧初始化。预览可离线打开；不证明游戏内或FCL性能。</p>
<p class="note">I44 V2与配套I45均为未批准、未安装候选，不修改正式控制器、Pattern、配方、实例或旧版归档。I43仍待审；batch-10仍I40/I41/I42三台（3/5），I37留最后。全结构完成后再进行三场景运行内存实测。</p>
<footer><small>变更记录 #2 · 2026-10-29：按负责人指定重新设计为车站式信标，旧V1保留。<a href="../../doc/HK3GTL-内测5/完整对话归档/2026-10-29_02-10-01_I44火车站与I45蒸汽列车方向_a727d99d16.html">本轮完整对话</a></small></footer></html>'''


def main():
    OUT.mkdir(parents=True, exist_ok=True); LOG.mkdir(parents=True, exist_ok=True)
    view = OUT / 'i44'; view.mkdir(exist_ok=True)
    print('生成I44独立几何，核对连通性、接口及24个QCV低阶…', flush=True)
    cube, data = geometry.build(); check = audit(cube, data)
    version = json.loads((resources.INSTANCE.parent / 'mrpack/modrinth.index.json').read_text(encoding='utf-8'))['versionId']
    assert version == '2.9.2'
    materials, sources, packs = resources.resource_materials(geometry.STATES)
    assert all(m['complete_cube'] and not m['tinted'] for m in materials)
    print('真实材质通过，导出完整NBT/Schematic并逐格回读…', flush=True)
    result = export_dense(cube, geometry.STATES, data['name'], view)
    assert result['block_count'] == check['blocks']
    raw = result['surface_groups']
    check.update(nbt_schem_sha256=result['hashes'], readback=result['readback'],
        viewer_surface_faces=sum(len(f) for g in raw for f in g), source_instance=str(resources.INSTANCE),
        instance_version=version, material_resource_sources=sources, enabled_file_resource_packs=packs)
    groups, lengths, merged = merge_surface_runs(raw, data['size'])
    check.update(viewer_surface_merge=merged, viewer_rendered_quads=merged['rendered_quads'])
    counts = {'GTCEu': 0, 'GTL Core': 0, '其他模组': 0, '原版': 0, '项目QCV主机壳': 0, '主控标记': 0, '工业接口标记': 0}
    for state, count in check['palette'].items():
        if state == geometry.material.CONTROL: group = '主控标记'
        elif state == geometry.material.PORT: group = '工业接口标记'
        elif state == geometry.material.QCV: group = '项目QCV主机壳'
        elif state.startswith('minecraft:'): group = '原版'
        elif state.startswith('gtceu:'): group = 'GTCEu'
        elif state.startswith('gtlcore:'): group = 'GTL Core'
        elif state.startswith('hk3gtl:'): raise ValueError(('非白名单项目方块', state))
        else: group = '其他模组'
        counts[group] += count
    check['material_source_counts'] = {k: v for k, v in counts.items() if v}
    payload = dict(data=data, palette=geometry.STATES, surfaceGroups=groups, surfaceRunLengths=lengths,
        blockCount=check['blocks'], materials=materials, audit=check, names={s: s.split(':')[1] for s in geometry.STATES})
    compressed = gzip.compress(json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), 6)
    (view / 'data.js').write_text('window.HK3_PAYLOAD=' + json.dumps(base64.b64encode(compressed).decode('ascii')) + ';', encoding='utf-8')
    check['viewer_payload_gzip_bytes'] = len(compressed)
    save(OUT / 'manifest.json', dict(data, approved=False, installed=False, game_verified=False,
        status='candidate_waiting_user_review', target_voltage='QCV', voltage_mapping='V06 / tier20',
        blocks=check['blocks'], unique_materials=len(materials), ordinary_materials=check['ordinary_materials'],
        source_instance=str(resources.INSTANCE), instance_version=version,
        generated_at=dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat(timespec='seconds')))
    save(OUT / 'verification.json', check)
    save(OUT / '材料清单.json', [dict(state=m['state'], count=check['palette'][m['state']], role=geometry.ROLES[m['state']],
        complete_cube=m['complete_cube'], source=sources.get(m['state'], {}), survival_stage_verified=False) for m in materials])
    save(LOG / 'lower-voltage-evidence.json', check['voltage_progression'])
    (OUT / 'index.html').write_text(report(data, check), encoding='utf-8')
    scripts = OUT / '生成脚本'; scripts.mkdir(exist_ok=True)
    for name in ('i44_station_geometry_v2_20261029.py', 'i44_station_audit_v2_20261029.py',
                 'i44_voltage_progression_20261029.py', 'build_i44_station_v2_20261029.py'):
        shutil.copy2(ROOT / 'tools/structure_delivery' / name, scripts / name)
    save(LOG / 'package-status.json', dict(passed=True, approved=False, installed=False, game_verified=False,
        output=str(OUT), size_xyz=data['size'], blocks=check['blocks'], materials=len(materials),
        rendered_quads=merged['rendered_quads'], payload_bytes=len(compressed), nbt_schem_sha256=result['hashes']))
    print(json.dumps(dict(output=str(OUT), blocks=check['blocks'], rendered_quads=merged['rendered_quads']), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
