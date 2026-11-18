# -*- coding: utf-8 -*-
"""W02递归构造环：中央意识、六院三重环与不对称信息喉口。"""
import math
import numpy as np
from scipy import ndimage
from w02_matrix_geometry_v1_20261107 import M,STATES,IDS,ROLES as OLD_ROLES
from structure_size_baseline import baselines
from w02_voltage_progression_20261107 import progression

W,H,D=649,303,493
ROLES=dict(OLD_ROLES)
ROLES.update({M.WFV:'HBV构造蓝；递归主环、装配节点与意识舱主体',
    M.ATOMIC:'扭转主脊线与喉口暗色轮廓',M.CLEAN:'递归轮廓的浅色边界',
    M.PLASCRETE:'三处投影锚座',M.FUSION_GLASS:'奇点舱与本体之间的静态信息束',
    M.BLUE_GLASS:'节点观察场与递归内壁',M.BLACK_GLASS:'局部信息隔离面',
    M.LIGHT:'奇点与信息束发光标记；不代表粒子或动画已实现',
    M.CONTROL:'中央意识舱北向主控预览标记',M.GRATE:'沿递归节点和意识舱连接的巡检桥面'})


def build():
    c=np.zeros((H,D,W),np.uint8)
    def box(a,b,s):
        x,y,z=a;X,Y,Z=b
        assert 0<=x<=X<W and 0<=y<=Y<H and 0<=z<=Z<D,(a,b)
        c[y:Y+1,z:Z+1,x:X+1]=IDS[s] if s else 0
    def tube(a,b,s,r=2):
        a=np.asarray(a);b=np.asarray(b);steps=int(max(abs(b-a)))
        points=np.rint(np.linspace(a,b,steps+1)).astype(int)
        for x,y,z in points:box((x-r,y-r,z-r),(x+r,y+r,z+r),s)
    z,x=np.ogrid[:D,:W]
    q=np.sqrt(((x-324)/324)**2+((z-246)/246)**2)
    theta=np.arctan2((z-246)/246,(x-324)/324)
    height=130-28*np.cos(theta)+18*np.sin(theta)+10*np.sin(2*theta)
    radial=(q-.70)/.30
    angles=[-math.pi*5/6,-math.pi/2,-math.pi/6,math.pi/6,math.pi/2,math.pi*5/6]
    names=['加工院','热工院','混配院','精密院','算力院','构件院']
    nodes=[];zones=[];routes=[]
    for i,t in enumerate(angles):
        cx=round(324+324*.70*math.cos(t));cz=round(246+246*.70*math.sin(t))
        cy=round(130-28*math.cos(t)+18*math.sin(t)+10*math.sin(2*t))
        nodes.append((cx,cy,cz))
    # 主环保留真实空腔；扭转的是沿环体旋进的脊线，不声称实现非欧几何。
    window=np.minimum.reduce([np.abs(np.angle(np.exp(1j*(theta-t)))) for t in angles])<.13
    for y in range(H):
        dy=y-height;outer=radial**2+(dy/80)**2
        inner=((q-.70)/.17)**2+(dy/46)**2
        body=(outer<=1+1e-9)&(inner>=1)
        c[y][body]=IDS[M.WFV]
        phase=2*np.arctan2(dy/80,radial)-3*theta
        edge=body&(outer>.65)
        c[y][edge&(np.abs(np.sin(phase))<.12)]=IDS[M.ATOMIC]
        c[y][edge&(np.abs(np.sin(phase))>=.12)&(np.abs(np.sin(phase))<.17)]=IDS[M.CLEAN]
        c[y][body&window&(np.abs(dy)<43)]=IDS[M.GLASS]
        c[y][body&window&(np.abs(dy)>=43)&(np.abs(dy)<48)]=IDS[M.ROBUST]
        c[y][body&(inner<1.14)&(np.abs(np.sin(theta*3))<.32)]=IDS[M.BLUE_GLASS]
    # 两端口径不同的工艺喉口是造型，不限制玩家的真实物料流向。
    for left in (True,False):
        for xx in (range(0,126) if left else range(523,649)):
            f=xx/125 if left else (648-xx)/125
            cy=158 if left else 100;rz=85-15*f if left else 54+10*f
            ry=69-10*f if left else 46+8*f
            yy,zz=np.ogrid[:H,:D];r=((zz-246)/rz)**2+((yy-cy)/ry)**2
            wall=(r<=1)&(r>=.47)
            c[:,:,xx][wall]=IDS[M.WFV]
            c[:,:,xx][r<.47]=0
            if xx in (0,1,2,3,4,5,6,642,643,644,645,646,647,648):
                c[:,:,xx][wall]=IDS[M.ATOMIC if xx%7<3 else M.CLEAN]
    process=[(M.MACERATOR,M.GEAR,M.SOLID,M.STEEL),(M.HEATPROOF,M.INSULATE,M.TURBINE,M.INTAKE),
        (M.MIXING,M.INERT,M.FROST,M.FILTER),(M.LASER,M.IRIDIUM,M.LAFIUM,M.LAMINATED),
        ('gtceu:computer_casing',M.COMPUTER,M.MULTI,M.INSULATE),(M.DIMENSION,M.PROCESS,M.STRESS,M.VIBRATION)]
    # 每院是主环的三层缩影；六根径向桥分别回到中央意识舱。
    for i,(cx,cy,cz) in enumerate(nodes):
        a,b,lining,accent=process[i]
        for rx,rz,thick,ry,mat in [(52,40,.30,16,a),(34,26,.30,11,b),(17,13,.34,7,lining)]:
            x0,x1=cx-rx,cx+rx;z0,z1=cz-rz,cz+rz
            zz,xx=np.ogrid[z0:z1+1,x0:x1+1];r=np.sqrt(((xx-cx)/rx)**2+((zz-cz)/rz)**2)
            for yy in range(cy-ry,cy+ry+1):
                mask=((r-(1-thick))/thick)**2+((yy-cy)/ry)**2<=1
                view=c[yy,z0:z1+1,x0:x1+1];view[mask]=IDS[mat]
                view[mask&(np.abs(yy-cy)<=2)]=IDS[accent]
        box((cx-5,cy-5,cz-5),(cx+5,cy+5,cz+5),M.LIGHT)
        for dx in (-9,9):tube((cx+dx,cy-48,cz),(cx+dx,cy+48,cz),M.FUSION_GLASS,2)
        box((cx-14,cy+17,cz-4),(cx+14,cy+22,cz+4),M.VENT)
        tube((cx-52,cy,cz),(cx+52,cy,cz),M.ASSEMBLY,1)
        start=(324,151,246);end=(cx,cy-24,cz)
        tube(start,end,M.WFV,7)
        tube((324,160,246),(cx,cy-15,cz),M.GRATE,2)
        # 每条冷却支路嵌在桥内，两端落入独立设备座。
        p0=np.rint(np.asarray(start)*.25+np.asarray(end)*.75).astype(int)
        p1=p0+np.array((18,0,0));p0=list(map(int,p0));p1=list(map(int,p1))
        for px,py,pz in (p0,p1):box((px-3,py-3,pz-3),(px+3,py+3,pz+3),M.TURBINE)
        px,py,pz=p0;X,Y,Z=p1
        box((px,py-1,pz-1),(X,py+1,pz+1),M.STEEL_PIPE)
        routes.append(dict(id=names[i]+'桥内冷却联络',start=p0,end=p1,
            path=[[v,py,pz] for v in range(px,X+1)],state=M.STEEL_PIPE,endpoint_state=M.TURBINE))
        zones.append(dict(name=names[i]+' · 三重递归装配环',pos=[cx,cy,cz]))
    # 中央意识舱：外层光场、中层认知环、内部空腔与局部奇点。
    for rx,ry,rz,mat in [(73,105,70,M.WFV),(48,73,46,M.COMPUTER),(25,40,24,M.FUSION_GLASS)]:
        z0,z1=246-rz,246+rz;x0,x1=324-rx,324+rx
        zz,xx=np.ogrid[z0:z1+1,x0:x1+1];r=((xx-324)/rx)**2+((zz-246)/rz)**2
        for yy in range(151-ry,151+ry+1):
            rr=r+((yy-151)/ry)**2;mask=(rr<=1)&(rr>=.77)
            view=c[yy,z0:z1+1,x0:x1+1];view[mask]=IDS[mat]
            if mat==M.WFV and yy%24>5:view[mask]=IDS[M.FUSION_GLASS]
            if mat==M.COMPUTER and yy%20>12:view[mask]=IDS[M.BLACK_GLASS]
    tube((324,50,246),(324,256,246),M.FUSION_GLASS,4)
    box((317,144,239),(331,158,253),M.LIGHT)
    zones.append(dict(name='中央构造意识 · 六院统合核心',pos=[324,151,246]))
    # 左偏高位奇点以光场而非承重柱连接；顶界来自有用途的完整舱体。
    tube((218,151,246),(324,151,246),M.FUSION_GLASS,4)
    tube((218,151,246),(218,276,246),M.FUSION_GLASS,3)
    zz,xx=np.ogrid[212:281,184:253];r=((xx-218)/34)**2+((zz-246)/34)**2
    for yy in range(250,303):
        rr=r+((yy-276)/26)**2;mask=(rr<=1)&(rr>=.65)
        v=c[yy,212:281,184:253];v[mask]=IDS[M.WFV if yy%13<4 else M.BLUE_GLASS]
    tube((218,254,246),(218,298,246),M.FUSION_GLASS,2)
    box((214,272,242),(222,280,250),M.LIGHT)
    zones.append(dict(name='左偏高位奇点舱 · 信息投影锚点',pos=[218,276,246]))
    # 三组落地锚座承接主环；无需整幅平台填满包围盒。
    for cx,cy,cz in (nodes[0],nodes[2],nodes[4]):
        box((cx-23,0,cz-20),(cx+23,8,cz+20),M.PLASCRETE)
        box((cx-17,9,cz-15),(cx+17,16,cz+15),M.STABLE)
        tube((cx,15,cz),(cx,cy-48,cz),M.ROBUST,5)
    # 北向主控内嵌于意识舱的下部构造臂，宽度中线不偏移。
    box((256,38,149),(392,62,199),M.WFV)
    box((263,43,149),(385,57,152),M.CLEAN)
    box((267,45,149),(381,55,150),M.WFV)
    tube((324,50,196),(324,96,246),M.WFV,8)
    control=[324,50,149];box(control,control,M.CONTROL);ports=[]
    for i,px in enumerate((274,286,298,310,338,350,362,374),1):
        p=[px,50,149];box(p,p,M.PORT)
        ports.append(dict(id=f'通用接口{i:02}',pos=p,face='north',purpose='通用仓位；按接入仓室确定能力，兼容总成方向不由造型限定',group='generic'))
    box((258,46,144),(390,58,148),None)
    # 共享服务阵列嵌入主控构造臂内；每种材料具有明确的设备用途。
    services=[M.ATOMIC,M.POWER,M.TUNG_PIPE,M.STABLE,M.IRON,M.OBSIDIAN,M.GOLD]
    for i,mat in enumerate(services):
        px=266+i*17;box((px,39,170),(px+12,44,191),mat)
    paths=[dict(min=[258,46,144],max=[390,58,148])]
    data=dict(key='w02',name='hk3gtl-w02-autonomous-matrix-v2-20261107',
        title='理之律者 · 万象·自律工业矩阵 · 递归构造环',size=[W,H,D],controller=control,
        controller_face='north',ports=ports,zones=zones,paths=paths,pipe_routes=routes,
        target_voltage='WSV',appearance_voltage='HBV',
        description='扭转脊线贯穿不对称空腔主环，中央构造意识以六根径向巡检桥统合六院；每院包含三重自相似装配环。左大右小的工艺喉口、递归观察场和左偏高位奇点构成信息投影外观。',
        purpose='保留中央矩阵与六院职责、HBV外观和WSV运行目标。八个接口全部通用；喉口只表达视觉流向。光场为真实方块静态造型，未增加媒体、粒子、配方或成型发奖逻辑。')
    return c,data


def audit(c,data):
    counts=np.bincount(c.ravel(),minlength=len(STATES)+1)
    assert np.all(counts[1:]),[s for s,n in zip(STATES,counts[1:]) if not n]
    palette=dict(sorted(zip(STATES,map(int,counts[1:])),key=lambda p:-p[1]))
    occupied=c!=0;bounds=[]
    for axis in (2,0,1):
        p=np.flatnonzero(np.any(occupied,axis=tuple(i for i in range(3) if i!=axis)))
        bounds.append([int(p[0]),int(p[-1])])
    assert bounds==[[0,W-1],[0,H-1],[0,D-1]],bounds
    labels,n=ndimage.label(occupied);assert n==1,('六邻接游离件',n)
    del labels,occupied
    assert palette[M.WFV]==max(palette.values())
    assert palette[M.CONTROL]==1 and palette[M.PORT]==len(data['ports'])==8
    assert {s for s in STATES if s.startswith('hk3gtl:')}=={M.WFV,M.PORT}
    assert data['controller'][0]==(W-1)//2
    markers=[]
    for item in [dict(id='主控',pos=data['controller'])]+data['ports']:
        x,y,z=item['pos'];assert c[y,z+1,x]
        assert all(c[y+dy,z,x+dx] for dx,dy in ((-1,0),(1,0),(0,1),(0,-1)))
        assert not np.any(c[y,z-5:z,x])
        markers.append(dict(id=item['id'],position=item['pos'],flush_shell=True,inner_backed=True,outer_clear=5))
    for route in data['pipe_routes']:
        p=route['path'];assert p[0]==route['start'] and p[-1]==route['end']
        assert all(sum(abs(a-b) for a,b in zip(p[i],p[i+1]))==1 for i in range(len(p)-1))
        assert all(c[y,z,x]==IDS[route['state']] for x,y,z in p)
        for x,y,z in (p[0],p[-1]):assert c[y+3,z,x]==IDS[route['endpoint_state']]
    for path in data['paths']:
        x,y,z=path['min'];X,Y,Z=path['max'];assert not np.any(c[y:Y+1,z:Z+1,x:X+1])
    for zone in data['zones']:
        x,y,z=zone['pos'];assert c[y,z,x],zone
    baseline=baselines()['W02']['size'];assert all(a>=b for a,b in zip((W,D,H),baseline))
    metrics=dict(blocks=int(counts[1:].sum()),materials=len(STATES)-2,volume=W*H*D,height=H)
    return dict(passed=True,geometry_passed=True,approved=False,installed=False,game_verified=False,
        size_xyz=[W,H,D],size_wdh=[W,D,H],bounds_xyz=dict(min=[0,0,0],max=[W-1,H-1,D-1]),
        blocks=metrics['blocks'],unique_materials=len(STATES),ordinary_materials=metrics['materials'],palette=palette,
        bounding_box_volume=metrics['volume'],height=H,hbv_casing_count=palette[M.WFV],
        baseline_check=dict(passed=True,baseline_wdh=baseline),voltage_progression=progression(metrics),
        connectivity=dict(passed=True,components=1,neighborhood=6),controller=dict(position=data['controller']),
        port_checks=markers,pipe_routes_count=6,pipe_routes_passed=True,open_pipe_ends=0,
        recursive_nodes=6,recursive_levels_per_node=3,central_consciousness=1,
        checks=['实际649×493×303边界，不扩大空白导出尺寸。','HBV构造蓝是最大单材；WSV运行档不改。',
            '中央意识与六院职责保留，六院各有三重自相似装配环。','全体六邻接连通；高位奇点通过真实玻璃信息束连接。',
            '主控宽度居中，八处通用接口有背板、齐平并保留五格接线净空。',
            '六条桥内冷却联络逐格核验两端设备；无悬空端点。','按WSV比较53个低阶批准形态，四项严格递增。'],
        not_verified=['外观候选待审，未接入正式Pattern、未部署或游戏验收。',
            '非欧与全息为视觉叙事；没有实现空间拓扑、粒子演出或自动毕业奖励。',
            '研究、角色实体、配方、生存获取、实际仓室兼容和8GB全建筑目标另验。'])


if __name__=='__main__':
    import json
    cube,data=build();check=audit(cube,data)
    print(json.dumps({k:check[k] for k in ('passed','blocks','unique_materials','connectivity','hbv_casing_count')},ensure_ascii=False))
