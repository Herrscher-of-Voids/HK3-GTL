# -*- coding: utf-8 -*-
"""I44候选：真实目标实例材质、完整结构与纯HTML评审交付。"""
import base64
import datetime as dt
import gzip
import html
import json
import shutil
import i44_beacon_geometry_v1_20261029 as geometry
from i44_beacon_audit_v1_20261029 import audit
import build_i25_world_bubble_observatory_20261025 as resources
from i34_open_observatory_export_20261027 import export_dense
from i37_surface_runs_20261027 import merge_surface_runs

ROOT = geometry.ROOT
OUT = ROOT / 'deliveries/I44_仿制的千界一乘信标_双楔准星与轴向观测坞_V1_20261029'
LOG = ROOT / 'logs/i44-beacon-v1-20261029'


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def report(data, check):
    esc = html.escape
    p = check['voltage_progression']
    rows = ''.join(f'<tr><td><code>{esc(s)}</code></td><td>{n:,}</td><td>{esc(geometry.ROLES[s])}</td></tr>' for s, n in check['palette'].items())
    comparison = ''.join(f'<tr><td>{label}</td><td>{p["metrics"][key]:,}</td><td>{p["lower_maxima"][key]["value"]:,}（{", ".join(p["lower_maxima"][key]["ids"])}）</td><td>通过</td></tr>' for key, label in [('blocks', '实体方块'), ('materials', '普通材料种类'), ('volume', '真实包围盒体积'), ('height', '实际高度')])
    ordinary = check['blocks'] - 9
    source_rows = ''.join(f'<tr><td>{esc(name)}</td><td>{count:,}</td><td>{"标记单列" if name.endswith("标记") else format(count / ordinary * 100, ".3f") + "%"}</td></tr>' for name, count in check['material_source_counts'].items())
    return f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I44 · 双楔准星与轴向观测坞 V1</title><style>
body{{max-width:1320px;margin:32px auto;padding:0 24px;background:#111b28;color:#e5edf6;font:16px/1.8 system-ui}}h1{{line-height:1.3}}a{{color:#9adce4}}.note{{padding:16px;border-left:4px solid #8fa2db;background:#232c40}}img{{width:100%;display:block}}table{{width:100%;border-collapse:collapse}}td,th{{padding:10px;border-bottom:1px solid #425466;text-align:left;overflow-wrap:anywhere}}code{{overflow-wrap:anywhere}}.links{{display:flex;gap:18px;flex-wrap:wrap}}.table{{overflow:auto}}small{{color:#a9bad0}}figure{{margin:24px 0}}figcaption{{font-size:14px;color:#bacada}}
</style><small>HK3GTL · I44 · QCV / V06 / tier20 · V1独立待审候选</small><h1>仿制的千界一乘·信标<br>双楔准星与轴向观测坞</h1>
<p class="note">241×281×177（宽×深×高），{check['blocks']:,}个实体方块、{check['ordinary_materials']}种普通材料。双楔准星由落地机舱渐倾升起，沿中轴八角观测腔指向远处；QCV深靛蓝机壳主导主体，洁净金属口径与窄光缝标明测量基准。</p>
<div class="links"><a href="i44/三维评审.html">真实MC材质三维评审</a><a href="完整预览.png">完整预览图</a><a href="信标后方.png">后侧联锁舱</a><a href="信标俯视.png">俯视布局</a><a href="主控材质近景.png">主控近景</a><a href="verification.json">核验记录</a></div>
<figure><a href="i44/三维评审.html"><img src="完整预览.png" alt="I44深靛蓝双楔准星与轴向观测坞真实方块全景"></a><figcaption>同一份最终几何导出完整NBT、Schematic与三维载荷；实体、坐标和材质数量逐格回读一致。</figcaption></figure>
<h2>原作语义，独立的信标建筑</h2><p>原作参考为官方漫画<a href="https://comic.bh3.com/book/1021/2">《传承·须弥芥子》</a>中第二神之键的深色硬壳、薄光环和轴向观测表达。本轮未取得能够明确指认为原作“信标”独立外形的图像，因此双楔准星与观测坞是本项目工业化演绎，不能称为原作信标复刻。火车头身份不移植到I44；I45保留独立列车职责。</p>
<h2>从输入坐标，到复测，再到目的地交接</h2><p>八角口径朝前，保护窗后保留真实纵向空腔；分离的测头、刻度接点与独立隔振座围绕光路布置。左右机舱承接供能、冷却与维护，双楔斜主脊、关节箱与内部检修层都有实体支撑。后侧短联锁舱沿轴向接续观测腔，坐标读出与目的地交接机架落在承台上；不扩建站场，不铺设旅行轨道。</p>
<p>I25负责解析，I44负责有效坐标锁定与复测、既有加强观测工况、无人任务和I45目的地交接；I45才执行获许可的玩家旅行。I44不生成目标、不运输玩家、不解除终审维度限制，不新增神之键、维度、配方或世界观能力。图中的光窗与工位表达功能组织，不声称真实交接逻辑已接通。</p>
<h2>自然内嵌的主控和接口</h2><p>唯一钻石主控位于蓝图XYZ <code>{data['controller']}</code>，从1起算为[121,23,1]，沿整宽241的第121格，齐平嵌在承托前口径的光学基座连续外壁。八接口分置于两侧实际供能、冷却与维护机舱前壁，左右几何对称，逐个核对内背板、四周连续墙与五格外侧净空；没有外挂面板或托举柱。</p><p><code>hk3gtl:industrial_port_casing</code>仅为接口占位，钻石仅标主控；正式Pattern允许什么仓室、哪些数据与物品交接必须按后续能力合同核验。控制器独立材质在正式接入时随确认建筑制作。</p>
<h2>体量与全部QCV低阶逐项比较</h2><p>历史49×49×81仅为尺寸下限。本候选真实边界241×281×177，包围盒{check['bounding_box_volume']:,}格³；分立基础、卧式空腔和双楔内腔没有全部填实。按当前批准索引，完整覆盖{p['lower_form_count']}个较低电压形态，重新核对正式蓝图与元数据哈希；同阶结构不强制排序。四个量化指标4/4通过，外观仍待负责人审阅。</p><div class="table"><table><tr><th>指标</th><th>I44实际</th><th>低阶最大值</th><th>比较</th></tr>{comparison}</table></div>
<h2>实际建材与来源</h2><p>QCV机壳{check['qcv_casing_count']:,}块，为最多单一材料；其余按承力、光学、机舱、维护与冷却用途分配。仅使用允许的项目QCV机壳及接口标记；没有其他HK3GTL新增专用方块。普通材料分母{ordinary:,}块，主控1格与8接口另计，不混入来源占比。素材已在增强版2.9.2解析，配方阶段可达性仍单独待验。</p><div class="table"><table><tr><th>来源</th><th>数量</th><th>普通建材占比</th></tr>{source_rows}</table></div><details><summary>全部材料与构件职责</summary><div class="table"><table><tr><th>方块状态</th><th>数量</th><th>用途</th></tr>{rows}</table></div></details>
<h2>完整导出与预览优化</h2><p>采用目标实例真实MC纹理、最近邻采样与逐格重复。连续外露面合并且逐格重展相同，按需绘制、初始化分帧；没有缩小几何、纯色替身或只显示控制器。完整<a href="i44/{data['name']}.nbt">NBT</a>与<a href="i44/{data['name']}.schem">Schematic</a>包含全部实体，归档记录逐格回读和SHA256。</p>
<p class="note">本轮仅制作待审建筑候选，未批准、未安装，未修改I44正式控制器、Pattern、配方、实例或存档。I43仍待审；batch-10仍为I40/I41/I42三台（3/5）；I37继续留到最后。PC/FCL三场景运行内存、终极终端批量搭建和强加载表现，待全部结构完成后实测。</p>
<p><a href="../多方块确认归档/当前归档索引.html">当前批准索引</a> · <a href="../../doc/HK3GTL-内测5/完整对话归档/2026-10-29_01-43-26_I44信标外观候选试作授权_27f9321f52.html">本轮完整对话</a></p><footer><small>变更记录 #1 · 2026-10-29：I44新候选，独立几何；不改既有建筑。实际生成时间及核验见manifest/verification。</small></footer></html>'''


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
    for name in ('i44_beacon_geometry_v1_20261029.py', 'i44_beacon_audit_v1_20261029.py',
                 'i44_voltage_progression_20261029.py', 'build_i44_beacon_v1_20261029.py'):
        shutil.copy2(ROOT / 'tools/structure_delivery' / name, scripts / name)
    save(LOG / 'package-status.json', dict(passed=True, approved=False, installed=False, game_verified=False,
        output=str(OUT), size_xyz=data['size'], blocks=check['blocks'], materials=len(materials),
        rendered_quads=merged['rendered_quads'], payload_bytes=len(compressed), nbt_schem_sha256=result['hashes']))
    print(json.dumps(dict(output=str(OUT), blocks=check['blocks'], rendered_quads=merged['rendered_quads']), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
