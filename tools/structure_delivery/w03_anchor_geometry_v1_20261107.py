# -*- coding: utf-8 -*-
"""西琳的穹界锚定环：纵向主门、前后折叠门庭与四向空间锚臂。"""
import numpy as np
from scipy import ndimage
from i42_prefabrication_geometry_v1_20261028 import Material
from w02_matrix_geometry_v1_20261107 import STATES as BASE_STATES
from structure_size_baseline import baselines
from w03_voltage_progression_20261107 import progression

W,H,D=673,321,529
M=Material();M.WFV='hk3gtl:voltage_machine_casing_hcv'
STATES=sorted({M.WFV if s=='hk3gtl:voltage_machine_casing_hbv' else s for s in BASE_STATES}|{'minecraft:crying_obsidian'})
IDS={s:i+1 for i,s in enumerate(STATES)}
ROLES={s:'空间锚定、隔离、校准或维护设备构件' for s in STATES}
ROLES.update({M.WFV:'HCV虚空琥珀；主锚门、折叠门庭和四向锚座主体',M.CONTROL:'北向主控预览标记；W03对应西琳',
    M.PORT:'通用接口标记；物品流体输入输出不按位置限制',M.ATOMIC:'主门黑色裂隙轮廓与空间隔离脊',
    'minecraft:crying_obsidian':'空间断层边界与锚座隔离面',M.GOLD:'门框与空间标尺的金色校准基准',
    M.LIGHT:'静态锚定焦点；不代表传送、粒子或实体已实现',M.FUSION_GLASS:'门庭侧缘静态光场',
    M.GRATE:'锚臂巡检通道',M.STEEL_PIPE:'两端接入校准设备的冷却支路'})


def build():
    c=np.zeros((H,D,W),np.uint8)
    def box(a,b,s):
        x,y,z=a;X,Y,Z=b
        assert 0<=x<=X<W and 0<=y<=Y<H and 0<=z<=Z<D,(a,b)
        c[y:Y+1,z:Z+1,x:X+1]=IDS[s] if s else 0
    def beam(a,b,s,r=3):
        a=np.asarray(a);b=np.asarray(b)
        for x,y,z in np.rint(np.linspace(a,b,int(max(abs(b-a)))+1)).astype(int):box((x-r,y-r,z-r),(x+r,y+r,z+r),s)
    zz,xx=np.ogrid[:D,:W];q=np.sqrt(((xx-336)/336)**2+((zz-264)/264)**2)
    theta=np.arctan2((zz-264)/264,(xx-336)/336)
    # 低位回路沿四向锚座贯通；中部留空，不铺满矩形广场。
    for y in range(16,81):
        outer=((q-.78)/.22)**2+((y-48)/32)**2
        inner=((q-.78)/.11)**2+((y-48)/16)**2
        mask=(outer<=1+1e-9)&(inner>=1)
        c[y][mask]=IDS[M.WFV]
        c[y][mask&(np.abs(np.sin(theta*4))<.11)]=IDS[M.ATOMIC]
        c[y][mask&(outer>.78)&(np.abs(np.sin(theta*4))>.11)&(np.abs(np.sin(theta*4))<.16)]=IDS[M.GOLD]
    # 三座同轴门庭保留贯穿的真实空腔；前后级差形成空间折叠的透视。
    yy,xx=np.ogrid[:H,:W]
    for zc,depth,rx,ry,ix,iy in [(264,88,294,153,210,108),(102,36,207,115,160,84),(426,36,207,115,160,84)]:
        r=((xx-336)/rx)**2+((yy-167)/ry)**2
        hole=((xx-336)/ix)**2+((yy-167)/iy)**2<1
        for z in range(zc-depth,zc+depth+1):
            taper=1-.10*(abs(z-zc)/depth)**4;mask=(r<=taper*taper+1e-9)&~hole
            view=c[:,z,:];view[mask]=IDS[M.WFV]
            rim=mask&((r>(taper-.045)**2)|(((xx-336)/ix)**2+((yy-167)/iy)**2<1.15))
            view[rim]=IDS[M.ATOMIC]
            if abs(z-zc)>depth-6:view[mask&~rim]=IDS[M.GOLD if abs(z-zc)%6<2 else M.WFV]
            if abs(z-zc)<depth-10:view[mask&(r>.82)&(np.abs(yy-167)<77)]=IDS[M.FUSION_GLASS]
    # 中央低位承台与主门下缘连为一体，作为角色会面区的建筑预留。
    for y in range(0,25):
        radius=1-y*.007
        mask=((xx-336)/94)**2+((zz-264)/73)**2<=radius*radius
        c[y][mask]=IDS[M.WFV if y>7 else M.PLASCRETE]
    zones=[dict(name='西琳 · 主锚门与中央会面承台',pos=[336,20,264]),
        dict(name='前层折叠门庭',pos=[336,270,102]),dict(name='后层折叠门庭',pos=[336,270,426])]
    anchors=[(120,112),(552,112),(120,416),(552,416)]
    processes=[(M.LASER,M.IRIDIUM,M.LAFIUM,M.LAMINATED),(M.DIMENSION,M.PROCESS,M.STRESS,M.VIBRATION),
        (M.COMPUTER,M.MULTI,'gtceu:computer_casing',M.FILTER),(M.HEATPROOF,M.FROST,M.INERT,M.INSULATE)]
    for i,((cx,cz),process) in enumerate(zip(anchors,processes)):
        z0,z1=cz-45,cz+45;x0,x1=cx-54,cx+54
        zz0,xx0=np.ogrid[z0:z1+1,x0:x1+1];r=((xx0-cx)/54)**2+((zz0-cz)/45)**2
        for y in range(21,202):
            outer=r+((y-111)/90)**2;mask=(outer<=1)&(outer>=.62)
            v=c[y,z0:z1+1,x0:x1+1];v[mask]=IDS[M.WFV]
            if y%32<5:v[mask]=IDS['minecraft:crying_obsidian']
            if y%32 in (5,6):v[mask]=IDS[M.GOLD]
            if y%32>14:v[mask&(np.abs(xx0-cx)<28)]=IDS[M.GLASS]
            if y%32>25:v[mask&(np.abs(xx0-cx)<22)]=IDS[M.BLUE_GLASS]
        for level,y in enumerate((70,105,140)):
            mat=process[level]
            box((cx-25,y,cz-22),(cx+25,y+5,cz+22),mat)
            box((cx-21,y+6,cz-18),(cx+21,y+11,cz+18),process[(level+1)%4])
            box((cx-17,y+12,cz-16),(cx+17,y+17,cz-12),M.VENT)
            beam((cx-28,y+1,cz),(cx+28,y+1,cz),M.ASSEMBLY,2)
        beam((cx,54,cz),(cx,170,cz),M.ROBUST,6)
        end=(128 if cx<336 else 544,190,264)
        beam((cx,160,cz),end,M.WFV,11)
        beam((cx,175,cz),(end[0],205,264),M.GRATE,2)
        zones.append(dict(name=f'空间锚座{i+1} · 隔离与三层校准机组',pos=[cx,111,cz]))
    # 对称的几何量测设备沿主门两侧布置，不另立接口柜墙。
    extra=[M.MACERATOR,M.GEAR,M.SOLID,M.STEEL,M.MIXING,M.CLEAN,M.POWER,M.TUNG_PIPE,M.STABLE,M.IRON,M.OBSIDIAN,M.INTAKE]
    for i,mat in enumerate(extra):
        cx=80 if i%2==0 else 592;y=104+(i//2)*17
        box((cx-13,y,244),(cx+13,y+9,284),mat)
        beam((cx,y+4,264),(128 if cx<336 else 544,y+4,264),M.ROBUST,3)
    # 主控在实际主门的北向下缘内嵌，整宽中线与八个通用仓位保持可达。
    box((278,34,176),(394,46,183),M.WFV)
    box((280,35,176),(392,45,176),M.CLEAN)
    box((282,37,176),(390,43,176),M.WFV)
    control=[336,40,176];box(control,control,M.CONTROL);ports=[]
    for i,x in enumerate((286,298,310,322,350,362,374,386),1):
        p=[x,40,176];box(p,p,M.PORT)
        ports.append(dict(id=f'通用接口{i:02}',pos=p,face='north',group='generic',purpose='按接入舱室提供物品、流体或能源能力；不预设输入输出位置'))
    box((278,36,171),(394,44,175),None)
    routes=[]
    for i,(cx,cz) in enumerate(anchors):
        px=128 if cx<336 else 544;pz=190 if cz<264 else 314;y=180
        for z in (pz,pz+24):box((px-4,y-4,z-4),(px+4,y+4,z+4),M.TURBINE)
        box((px-1,y-1,pz),(px+1,y+1,pz+24),M.STEEL_PIPE)
        routes.append(dict(id=f'锚臂{i+1}冷却联络',start=[px,y,pz],end=[px,y,pz+24],
            path=[[px,y,z] for z in range(pz,pz+25)],state=M.STEEL_PIPE,endpoint_state=M.TURBINE))
    # 焦点内衬与隔离片分别安装在可见门缘；黑玻璃保留局部观察视窗。
    for x in (120,552):
        box((x-6,190,258),(x+6,202,270),M.LIGHT)
        box((x-9,203,255),(x+9,207,273),M.BLACK_GLASS)
    data=dict(key='w03',name='hk3gtl-w03-void-anchor-v1-20261107',candidate_version='V1',
        title='空之律者 · 穹界·虚数锚定环 · 四极折界门庭',size=[W,H,D],controller=control,controller_face='north',
        ports=ports,zones=zones,paths=[dict(min=[278,36,171],max=[394,44,175])],pipe_routes=routes,
        target_voltage='CIV',appearance_voltage='HCV',character='西琳',
        description='纵向主锚门贯穿前后两层折叠门庭，四座隔离锚塔以悬臂约束主门两侧；低位椭圆回路连接锚座，中央承台保留西琳会面区域。HCV琥珀主体配黑色断层边界、金色空间标尺和局部静态光场。',
        purpose='W03对应空之律者西琳，运行CIV、外观HCV。空间锚定、隔离与校准构成建筑职责；八处接口均通用。角色实体、传送、跨维度许可、粒子演出和配方不由外观候选代替实现。')
    return c,data


def audit(c,data):
    counts=np.bincount(c.ravel(),minlength=len(STATES)+1);assert np.all(counts[1:]),[s for s,n in zip(STATES,counts[1:]) if not n]
    palette=dict(sorted(zip(STATES,map(int,counts[1:])),key=lambda p:-p[1]));occupied=c!=0;bounds=[]
    for axis in (2,0,1):
        p=np.flatnonzero(np.any(occupied,axis=tuple(i for i in range(3) if i!=axis)));bounds.append([int(p[0]),int(p[-1])])
    assert bounds==[[0,W-1],[0,H-1],[0,D-1]],bounds
    labels,n=ndimage.label(occupied);assert n==1,('六邻接游离件',n)
    del labels,occupied
    assert palette[M.WFV]==max(palette.values()) and palette[M.CONTROL]==1 and palette[M.PORT]==len(data['ports'])==8
    assert data['controller'][0]==(W-1)//2 and data['character']=='西琳'
    assert {s for s in STATES if s.startswith('hk3gtl:')}=={M.WFV,M.PORT}
    markers=[]
    for item in [dict(id='主控',pos=data['controller'])]+data['ports']:
        x,y,z=item['pos'];assert c[y,z+1,x]
        assert all(c[y+dy,z,x+dx] for dx,dy in ((-1,0),(1,0),(0,1),(0,-1)))
        assert not np.any(c[y,z-5:z,x]);markers.append(dict(id=item['id'],position=item['pos'],flush_shell=True,inner_backed=True,outer_clear=5))
    for route in data['pipe_routes']:
        p=route['path'];assert p[0]==route['start'] and p[-1]==route['end']
        assert all(sum(abs(a-b) for a,b in zip(p[i],p[i+1]))==1 for i in range(len(p)-1))
        assert all(c[y,z,x]==IDS[route['state']] for x,y,z in p)
        for x,y,z in (p[0],p[-1]):assert c[y+3,z,x]==IDS[route['endpoint_state']]
    for path in data['paths']:
        x,y,z=path['min'];X,Y,Z=path['max'];assert not np.any(c[y:Y+1,z:Z+1,x:X+1])
    for zone in data['zones']:
        x,y,z=zone['pos'];assert c[y,z,x],zone
    baseline=baselines()['W03']['size'];assert all(a>=b for a,b in zip((W,D,H),baseline))
    metrics=dict(blocks=int(counts[1:].sum()),materials=len(STATES)-2,volume=W*H*D,height=H)
    return dict(passed=True,geometry_passed=True,approved=False,installed=False,game_verified=False,
        size_xyz=[W,H,D],size_wdh=[W,D,H],bounds_xyz=dict(min=[0,0,0],max=[W-1,H-1,D-1]),
        blocks=metrics['blocks'],unique_materials=len(STATES),ordinary_materials=metrics['materials'],palette=palette,
        bounding_box_volume=metrics['volume'],height=H,hcv_casing_count=palette[M.WFV],
        baseline_check=dict(passed=True,baseline_wdh=baseline),voltage_progression=progression(metrics),
        connectivity=dict(passed=True,components=1,neighborhood=6),controller=dict(position=data['controller']),
        port_checks=markers,pipe_routes_count=4,pipe_routes_passed=True,open_pipe_ends=0,character='西琳',
        checks=['实际实体包围盒673×529×321，超过W03总表下限。','CIV运行、HCV外观；HCV是最大单材。',
            '主锚门与前后折叠门庭保留真实贯穿空腔，四锚座与低位回路整体连通。','主控宽度居中，八个通用接口齐平、有背板及五格净空。',
            '四条锚臂冷却管逐格核对指定两端设备。','角色对应西琳；候选不自动召唤实体或授予旅行权限。'],
        not_verified=['本轮为独立V1外观候选，待负责人和DeepSeek方案比较后决定；未批准、未部署。',
            '正式Pattern、角色实体、配方、生存获取、仓室兼容及8GB全建筑运行目标均另行验收。'])


if __name__=='__main__':
    import json
    c,d=build();v=audit(c,d);print(json.dumps({k:v[k] for k in ('passed','blocks','unique_materials','connectivity')},ensure_ascii=False))
