# -*- coding: utf-8 -*-
"""I26 V5：保留撤塔主体，以固定随机种子摆放疏散货柜和车辆。"""
import base64, collections, copy, gzip, hashlib, io, json, random, re, shutil, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageStat
import build_i26_no_tower_v4_20261026 as previous
import build_i26_vehicle_combinations_20261026 as vehicles

ROOT, base = previous.ROOT, previous.base
OUT = ROOT / 'deliveries/I26_葵涌码头_疏散货柜与随机集卡运营场景_V5_20261026'
VIEW = OUT / 'i26'
NAME = 'hk3gtl-i26-operating-yard-v5-20261026'
TITLE = '世界泡无人采掘调度台 · 葵涌码头运营场景'
SEED = 26102605


def bounds(cells):
    return [min(p[i] for p in cells) for i in range(3)], [max(p[i] for p in cells) for i in range(3)]


def rotated(cells, turns):
    for _ in range(turns % 4):
        cells = {(-z, y, x): state for (x,y,z),state in cells.items()}
    lo, _ = bounds(cells)
    return {(x-lo[0],y-lo[1],z-lo[2]):state for (x,y,z),state in cells.items()}


def intersects(a, b, margin=0):
    return all(a[0][i] <= b[1][i]+margin and b[0][i] <= a[1][i]+margin for i in range(3))


def build():
    data = previous.build()
    body = {tuple(b['pos']):b['state'] for b in data['blocks']}
    previous.geometry.assert_left_right_symmetry(data)
    cells = dict(body); records = []; boxes = []; rng = random.Random(SEED)

    def place(local, origin, kind, **info):
        transformed = {(x+origin[0],y+origin[1],z+origin[2]):s for (x,y,z),s in local.items()}
        bb = bounds(transformed)
        assert not (set(transformed) & set(cells)), ('构件碰撞', kind, origin)
        # 包围盒也检查，避免将原建筑穿入中空箱体或车体内部。
        assert not any(bb[0][0] <= x <= bb[1][0] and bb[0][1] <= y <= bb[1][1] and bb[0][2] <= z <= bb[1][2] for x,y,z in body), ('侵入建筑', origin)
        foot = [(x,y,z) for x,y,z in transformed if y == bb[0][1]]
        assert foot and all((x,y-1,z) in cells for x,y,z in foot), ('承载面缺失', origin)
        cells.update(transformed)
        record = dict(id=f'{kind}-{len(records)+1:02}',kind=kind,origin=list(origin),bounds=bb,blocks=len(local),**info)
        records.append(record); boxes.append(bb)
        return record

    # 保留两条纵向空带；车辆位置轻微错开，颜色与挂箱组合可复现随机。
    truck_specs = [(92,128,0,True),(232,187,2,True),(93,190,0,True),(232,240,2,True),
                   (94,245,2,False),(233,145,0,False),(49,123,1,False),(268,181,3,False)]
    truck_colors = [t for t,_ in vehicles.TIERS[:4]] * 2
    rng.shuffle(truck_colors)
    cargo_colors = [t for t,_ in vehicles.TIERS]
    for n,(x,z,turn,loaded) in enumerate(truck_specs):
        x+=rng.choice((0,1));z+=rng.choice((-2,-1,0,1,2))
        tier = truck_colors[n]; cargo = rng.choice(cargo_colors) if loaded else None
        local = rotated(vehicles.assemble(tier,cargo),turn)
        role = '场桥装卸位' if loaded and n in (0,3) else '车道待行' if loaded else '短暂停靠/空载待命'
        place(local,(x,13,z),'vehicle',tractor=tier,cargo=cargo,rotation=turn*90,role=role)

    candidates = []
    for side in ('west','east'):
        xs = (18,30,42,54,66,78) if side == 'west' else (246,258,270,282,294,306)
        for row,z in enumerate((141,197,253)):
            candidates.extend(dict(x=x,z=z,turn=0,side=side,row=row) for x in xs)
        xs = (18,43,68) if side == 'west' else (246,271,296)
        for row,z in enumerate((120,179,235)):
            candidates.extend(dict(x=x,z=z,turn=1,side=side,row=row+3) for x in xs)
    # 先按分区挑选，避免全部随机集中到一侧；明确保留空位。
    chosen = []
    for side in ('west','east'):
        pool = [s for s in candidates if s['side']==side]; rng.shuffle(pool)
        for slot in pool:
            local = rotated(vehicles.samples.container('HBV'),slot['turn'])
            moved = {(x+slot['x'],y+13,z+slot['z']):s for (x,y,z),s in local.items()}
            bb = bounds(moved)
            if any(intersects(bb,b,2) for b in boxes): continue
            chosen.append(slot); boxes.append(bb)
            if sum(s['side']==side for s in chosen) == 18: break
    assert len(chosen)==36, ('落地箱位不足',len(chosen))
    boxes = [r['bounds'] for r in records]
    palette = (cargo_colors*5)[:36]; rng.shuffle(palette)
    ground = []
    for slot,tier in zip(chosen,palette):
        r = place(rotated(vehicles.samples.container(tier),slot['turn']),(slot['x'],13,slot['z']),
                  'container',tier=tier,level=1,rotation=slot['turn']*90,side=slot['side'])
        ground.append((slot,r))
    stack_choices = rng.sample(ground,6)
    for slot,lower in stack_choices:
        tier = rng.choice(cargo_colors)
        place(rotated(vehicles.samples.container(tier),slot['turn']),(slot['x'],22,slot['z']),
              'container',tier=tier,level=2,rotation=slot['turn']*90,side=slot['side'],on=lower['id'])
    assert all(cells[p]==state for p,state in body.items()), '码头主体被改写'
    assert len(cells)==len(body)+sum(r['blocks'] for r in records)
    assert all(not (275 <= p[2] <= 278 and p[1] > 12) for p in set(cells)-set(body)), '仓门前区被占用'
    assert all(not (126 <= p[0] <= 206 and 111 <= p[2] <= 174) for p in set(cells)-set(body))
    data.update(name=NAME,title=TITLE,candidate_version='V5')
    data['description']='撤塔对称主体保持不变；货柜一至两层，位置和颜色错落，四台挂箱车与四台空载拖头组成静态运营场景。'
    data['composition'].update(ground_containers=36,stacked_containers=6,container_boxes=42,
                               containers_on_vehicles=4,container_blocks=46*770,
                               unmanned_tractor_heads=8,loaded_tractors=4,empty_tractors=4)
    vehicle_slot_count=0
    for slot in candidates:
        shape=rotated(vehicles.samples.container('HBV'),slot['turn'])
        bb=bounds({(x+slot['x'],y+13,z+slot['z']):s for (x,y,z),s in shape.items()})
        if any(intersects(bb,r['bounds']) for r in records if r['kind']=='vehicle'):vehicle_slot_count+=1
    data['operating_layout']={'seed':SEED,'items':records,'candidate_ground_slots':len(candidates),
                              'occupied_ground_slots':36,'vehicle_occupied_slots':vehicle_slot_count,
                              'unstacked_candidate_slots':len(candidates)-36,
                              'empty_ground_slots':len(candidates)-36-vehicle_slot_count,
                              'yard_footprint_ratio':round(36*9*21/(2*87*161),4),'max_stack_levels':2}
    assert data['operating_layout']['vehicle_occupied_slots']==2
    data['zone_descriptions']=[{'name':'疏散货柜场','description':'36只落地箱，6只叠第二层；8色随机混排，保留空箱位与作业巷道。'},
                               {'name':'无人集卡','description':'4台挂箱与4台空载拖头，分散在车道、场桥作业位和待命区。'},
                               {'name':'主体与主控','description':'撤塔主体、居中主控及8个接口保持逐格不变；货物和车辆不要求镜像。'}]
    for zone in data['zones']:
        zone['name']=zone['name'].replace('空箱场桥作业坪','货柜场桥作业区').replace('空置车辆通道','无人集卡作业通道')
    data['blocks']=[{'pos':list(p),'state':s} for p,s in sorted(cells.items(),key=lambda v:(v[0][1],v[0][2],v[0][0]))]
    return data,body,records


def make_plan(data,body,records,materials):
    colors={m['state']:tuple(round(v) for v in ImageStat.Stat(Image.open(io.BytesIO(base64.b64decode(m['faces']['up'].split(',')[1]))).convert('RGB')).mean) for m in materials}
    image=Image.new('RGB',(1560,1360),'#111b28');draw=ImageDraw.Draw(image);scale=4;ox,oz=45,100
    tops={}
    for b in data['blocks']:
        x,y,z=b['pos']
        if y<=35 and ((x,z) not in tops or y>tops[x,z][0]): tops[x,z]=(y,b['state'])
    for (x,z),(_,s) in tops.items():
        draw.rectangle((ox+x*scale,oz+z*scale,ox+x*scale+3,oz+z*scale+3),fill=colors[s])
    draw.text((35,20),'I26 V5 · 货柜与车辆运行态布局（Y≤35层俯视）',font=base.font(26),fill='#e5edf5')
    for r in records:
        if r['kind']!='vehicle':continue
        lo,hi=r['bounds'];draw.rectangle((ox+lo[0]*scale-2,oz+lo[2]*scale-2,ox+(hi[0]+1)*scale+1,oz+(hi[2]+1)*scale+1),outline='#f1d69b',width=2)
    draw.text((36,1320),'42只堆场箱（36落地＋6叠层）· 8台集卡（4挂箱＋4空载）· 金框为车辆 · 底图使用实际贴图均色',font=base.font(22),fill='#c4d5df')
    image.save(OUT/'运营布局俯视.png')


def main():
    if OUT.exists() and (OUT/'manifest.json').exists():
        assert json.loads((OUT/'manifest.json').read_text(encoding='utf-8')).get('approved') is False
    VIEW.mkdir(parents=True,exist_ok=True)
    data,body,records=build();counts=collections.Counter(b['state'] for b in data['blocks'])
    base.W,base.H,base.D=data['size'];base.OUT,base.VIEW,base.NAME,base.TITLE=OUT,VIEW,NAME,TITLE
    body_data=copy.copy(data);body_data['blocks']=[{'pos':list(p),'state':s} for p,s in body.items()]
    base.voltage_comparison=previous.voltage_comparison
    check=base.audit(body_data)
    check.update(passed=False,geometry_passed=True,status='operating_scene_volume_conflict',approved=False,eligible_for_approval=False,
                 blocks=len(data['blocks']),palette=dict(counts.most_common()),unique_materials=len(counts),
                 connectivity=base.connected_components(data),voltage_progression=previous.voltage_comparison(counts,data['size']))
    old=json.loads((previous.OUT/'verification.json').read_text(encoding='utf-8'))
    check['rule_exceptions']=old['rule_exceptions'];check['rule_conflicts']=['volume']
    allowed={vehicles.samples.casing(t) for t,_ in vehicles.TIERS}|{base.PORT}
    assert {s for s in counts if s.startswith('hk3gtl:')} <= allowed
    assert counts[base.QAV]>max(n for s,n in counts.items() if s!=base.QAV)
    check['qav_casing_count']=counts[base.QAV]
    check['checks']=['撤塔V4主体逐格保留，原主控及8个接口坐标与操作净空不变。','货柜与车辆逐项检查承载、碰撞、建筑内部穿入及仓门前区。',
                     '主体左右镜像差异0；货柜与车辆按固定随机种子布置，不机械镜像。','场桥吊具Y37以上；箱体最高Y30，最多两层。',
                     '全体六邻接连通，QAV仍为最大单一材料；真实资源使用增强版2.9.2。']
    check['operating_layout']=data['operating_layout'];check['body_preserved_blocks']=len(body)
    check['body_symmetry']={'axis_x':166,'mismatched_voxels':0,'scope':'建筑主体；不包括随机运营物件'}
    states=sorted(counts);materials,sources,packs,proof=base.resource_materials(states)
    assert proof['instance_version']=='2.9.2'
    states,groups,hashes=base.export(data,VIEW)
    check.update(source_instance=str(base.INSTANCE),instance_proof=proof,material_resource_sources=sources,enabled_file_resource_packs=packs,nbt_schem_sha256=hashes)
    surfaces=base.build_surface_groups(data,states)
    check['viewer_surface_faces']=sum(len(f) for group in surfaces for f in group)
    payload={'data':{k:v for k,v in data.items() if k not in ('blocks','zone_descriptions','operating_layout')},'palette':states,'surfaceGroups':surfaces,
             'blockCount':len(data['blocks']),'materials':materials,'audit':check,'names':{s:s.split(':')[1] for s in states}}
    payload=json.loads(json.dumps(payload,ensure_ascii=False))
    encoded=base64.b64encode(gzip.compress(json.dumps(payload,ensure_ascii=False,separators=(',',':')).encode('utf-8'),9)).decode('ascii')
    assert json.loads(gzip.decompress(base64.b64decode(encoded)))==payload
    (VIEW/'data.js').write_text('window.HK3_PAYLOAD='+json.dumps(encoded)+';',encoding='utf-8')
    subprocess.run(['node',str(base.VIEWER_BUILDER),str(VIEW)],cwd=ROOT,check=True)
    bundle=VIEW/'viewer.bundle.js';bundle.write_text(bundle.read_text(encoding='utf-8').replace('逐格回读与净空检查通过','货柜与车辆摆放检查通过；静态运营场景，尚未实装'),encoding='utf-8')
    page=base.viewer_page(data,check).replace('V2','V5').replace('调度塔','低位航务楼')
    page=re.sub(r'<details open><summary>设计构成</summary>.*?</details>',
                '<details open><summary>随机运营场景</summary><p>42只堆场货柜：36只落地、6只叠第二层；4台挂箱车、4台空载拖头。建筑主体保持镜像，货物与车辆错落分布，保留空位与操作区。固定随机种子便于复核；没有运行动画。</p><p>高度110格沿用已批准例外；体积递增仍未满足，当前为待审场景，不代表游戏成型或接入。</p></details>',page,flags=re.S)
    page=page.replace('V5候选：葵涌码头式泊位、岸桥、堆场和低位航务楼；未获批准、未接入游戏。','V5疏散运营场景候选；主体原样，未获批准、未接入游戏。')
    (VIEW/'三维评审.html').write_text(page,encoding='utf-8')
    base.render(data,materials,OUT);make_plan(data,body,records,materials)
    for side,(x0,x1) in {'西侧':(7,112),'东侧':(220,325)}.items():
        cropped={(b['pos'][0]-x0,b['pos'][1],b['pos'][2]-114):b['state'] for b in data['blocks'] if x0<=b['pos'][0]<=x1 and 114<=b['pos'][2]<=274 and b['pos'][1]<=51}
        path=OUT/(side+'堆场局部');path.mkdir(exist_ok=True)
        local=vehicles.samples.metadata(cropped,side+'堆场',side,[])
        base.render(local,[m for m in materials if m['state'] in set(cropped.values())],path)
    summary={k:v for k,v in data.items() if k not in ('blocks',)}
    manifest=dict(summary,approved=False,eligible_for_approval=False,blocks=len(data['blocks']),unique_materials=len(states),rule_conflicts=['volume'],rule_exceptions=check['rule_exceptions'])
    base.write_json(OUT/'manifest.json',manifest);base.write_json(OUT/'verification.json',check)
    base.write_json(OUT/'运营物件位置.json',data['operating_layout'])
    (OUT/'index.html').write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>I26 V5 · 疏散货柜与随机集卡</title><style>body{{max-width:1380px;margin:28px auto;padding:0 22px;background:#111b28;color:#e5edf5;font:16px/1.8 system-ui,"Microsoft YaHei",sans-serif}}a{{color:#9edce4}}img{{max-width:100%;height:auto}}.note{{padding:14px;background:#203044}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}@media(max-width:800px){{.grid{{display:block}}}}</style><h1>I26 V5 · 葵涌码头疏散运营场景</h1><p class="note">42只堆场货柜（36落地＋6叠层），8台集卡（4挂箱＋4空载）。8色货柜、4色拖头错落布置；保留16个候选空箱位，另有2个未堆箱位置用于车辆。建筑主体和主控不变，货物车辆不机械镜像。</p><p><a href="i26/三维评审.html">打开三维评审</a> · <a href="运营布局俯视.png">查看运营布局</a> · <a href="verification.json">摆放与资源核验</a></p><img src="等轴预览.png" alt="码头整体运营场景"><h2>两侧堆场局部</h2><div class="grid"><div><h3>西侧</h3><img src="西侧堆场局部/等轴预览.png" alt="西侧货柜车辆"></div><div><h3>东侧</h3><img src="东侧堆场局部/等轴预览.png" alt="东侧货柜车辆"></div></div><h2>作业坪俯视</h2><img src="运营布局俯视.png" alt="地面作业坪布局"><p>{len(data['blocks']):,}方块，{len(states)}种材料，333×301×110格；固定随机种子{SEED}。货柜与车辆未覆盖建筑，最多两层，吊具、仓门前区和主控接口净空保留。</p><p class="note">静态运营造型候选，未接入游戏实例。高度110格沿用负责人例外；体积递增项仍低于既有下限，未宣称整体规则、Pattern或真实物流功能通过。</p></html>''',encoding='utf-8')
    (OUT/'生成脚本').mkdir(exist_ok=True);shutil.copy2(__file__,OUT/'生成脚本'/Path(__file__).name)
    print(json.dumps({'output':str(OUT),'blocks':len(data['blocks']),'materials':len(states),'containers':42,'vehicles':8,'faces':check['viewer_surface_faces']},ensure_ascii=False))


if __name__=='__main__':main()
