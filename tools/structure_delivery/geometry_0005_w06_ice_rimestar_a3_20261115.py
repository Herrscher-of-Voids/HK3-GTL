import math

import numpy as np
from scipy.ndimage import distance_transform_cdt, label
from scipy.spatial import cKDTree

import geometry_0005_w06_crystal_crown_a2_20261115 as a2


QSV, WHITE, GRAY, BLACK, IRON, LIGHT, GLASS, CYAN, ICE, CONTROL = a2.STATES
RED = 'minecraft:red_terracotta'
STATES = a2.STATES + [RED]
IDS = {s: i for i,s in enumerate(STATES,1)}
NAMES = dict(a2.NAMES, **{RED:'红色陶瓦'})
ROLES = dict(a2.ROLES, **{RED:'陨冰形态中央分缝内的小面积暗红凝态核心'})
ROLES[WHITE] = '陨冰倒锥裙甲、包合弧刃、纯冰长带与冰纹尖徽'
ROLES[BLACK] = '内腔、窄中轴与取自第19章陨冰形态的悬浮扁冠盘'
ROLES[GLASS] = '冷凝室观察面、冰蓝棱柱与外张裙刃透光层'
ROLES[QSV] = '中轴、倒锥与弧刃蓝色收边、低温机组和冷媒回路'
ROLES[CYAN] = '外围冰棱内层与冷媒观察槽'
ROLES[ICE] = 'A2保留材料槽位，本候选未使用'
PARTS = []


def pedestal():
    x,z = a2.grid(-138,138,-143,133)
    metric = a2.hexmetric(x,z+5)
    layers=[]
    for y in range(12,61):
        radius=np.interp(y,[12,23,30,45,60],[116,116,105,103,89])
        state=np.where(metric<=radius,IDS[BLACK if y<=21 else WHITE if y<=28 else QSV],0).astype(np.uint8)
        if y>=36:
            state[metric<radius-10]=0
            state[(metric<=radius)&(metric>=radius-2)]=IDS[LIGHT if y in [43,44,59,60] else WHITE]
        layers.append((y,x,z,state))
    return a2.part('condensation_pedestal',layers)


def lower_shell():
    x,z=a2.grid(-112,112,-75,65)
    layers=[]
    for y in range(85,202):
        r=np.interp(y,[85,110,166,201],[3,25,76,99])
        metric=np.maximum(abs(x),abs(x)*.45+abs(z+5)*1.58)
        mask=(metric<=r)&(metric>=r-4)
        mask &= ~((abs(x)<=9)&(z>=-5))
        state=np.where(mask,IDS[WHITE],0).astype(np.uint8)
        state[mask&(abs(x)>=r-3)]=IDS[QSV]
        state[mask&(abs(z+5)>=r*.58)&(abs(x)<=r*.6)]=IDS[GRAY]
        layers.append((y,x,z,state))
    return a2.part('rimestar_inverted_cone',layers)


def spindle():
    x,z=a2.grid(-32,32,-35,25)
    layers=[]
    for y in range(205,312):
        r=np.interp(y,[205,226,252,275,291,311],[27,17,13,18,11,2])
        metric=a2.hexmetric(x,z+5)
        state=np.where(metric<=r,IDS[GLASS],0).astype(np.uint8)
        state[metric<=r*.55]=IDS[BLACK]
        state[(metric<=r)&(abs(x)>=r*.72)]=IDS[WHITE]
        state[(metric<=r)&(abs(x)<=2)&(z>=-5)]=IDS[QSV]
        layers.append((y,x,z,state))
    return a2.part('ice_herrscher_slim_axis',layers)


def blade(side):
    x,z=a2.grid(7,151,-32,87)
    layers=[]
    heights=[92,118,152,185,212,240,267]
    for y in range(92,268):
        inner=np.interp(y,heights,[7,16,22,29,35,46,25])
        outer=np.interp(y,heights,[8,46,91,123,137,100,28])
        span=outer-inner
        across=np.clip((x-inner)/max(span,1),0,1)
        face=62+np.rint(.04*(y-184)-min(87,span*1.3)*across**3)
        mask=(x>=inner)&(x<=outer)&(z>=face)&(z<=face+11)
        state=np.where(mask,IDS[WHITE],0).astype(np.uint8)
        state[mask&(x<=inner+3)]=IDS[QSV]
        state[mask&(x>=outer-2)]=IDS[IRON]
        state[mask&(x>=inner+(outer-inner)*.28)&(x<=inner+(outer-inner)*.46)&(y>=139)&(y<=228)]=IDS[GLASS]
        state[mask&(x>=inner+(outer-inner)*.62)&(x<=inner+(outer-inner)*.64)]=IDS[QSV]
        layers.append((y,x*side,z,state))
    return a2.part('rimestar_enclosing_blade_'+('left' if side<0 else 'right'),layers)


def trailing_blade(side):
    x,z=a2.grid(17,158,-80,-61)
    layers=[]
    for y in range(166,295):
        low=np.interp(y,[166,190,220,250,275,294],[154,137,103,68,32,27])
        high=np.interp(y,[166,190,220,250,275,294],[155,157,132,99,66,28])
        face=-73+np.rint(.04*(x-80))
        mask=(x>=low)&(x<=high)&(z>=face)&(z<=face+6)
        state=np.where(mask,IDS[WHITE],0).astype(np.uint8)
        state[mask&(x>=high-2)]=IDS[QSV]
        layers.append((y,x*side,z,state))
    return a2.part('ice_long_trailing_blade_'+('left' if side<0 else 'right'),layers)


def crown():
    x,z=a2.grid(-118,118,-80,70)
    metric=np.maximum.reduce([abs(x),abs(z+5)/.64,(abs(x)+abs(z+5)/.64)*.7071068])
    layers=[]
    for y in range(323,335):
        radius=np.interp(y,[323,328,334],[109,114,106])
        mask=(metric<=radius)&(metric>=46)
        state=np.where(mask,IDS[BLACK],0).astype(np.uint8)
        state[mask&(metric>=radius-3)]=IDS[WHITE]
        state[mask&(metric<=50)]=IDS[QSV]
        for angle in np.arange(8)*math.pi/4:
            tangential=abs(-x*math.sin(angle)+(z+5)/.64*math.cos(angle))
            state[mask&(tangential<=1.1)&(metric>=50)&(metric<=99)]=IDS[QSV]
        layers.append((y,x,z,state))
    return a2.part('rimestar_flat_dark_crown',layers)


def crest():
    x,z=a2.grid(-29,29,76,82)
    layers=[]
    for y in range(308,358):
        d=y-308
        mask=((abs(x)<=max(1,8-d*.14))&(d<=48))
        for side in [-1,1]:
            mask |= (abs(x-side*np.interp(d,[0,18,31,49],[3,11,24,19]))<=2)&(d>=8)
            mask |= (abs(x-side*np.interp(d,[0,20,38,49],[3,7,12,9]))<=1)&(d>=20)
        state=np.where(mask,IDS[WHITE],0).astype(np.uint8)
        state[mask&(abs(x)<=2)]=IDS[LIGHT]
        layers.append((y,x,z,state))
    return a2.part('ice_forked_crystal_crest',layers)


def spear(side):
    cx=side*184
    x,z=a2.grid(cx-18,cx+18,-5,1)
    layers=[]
    for y in range(113,326):
        shaft=(abs(x-cx)<=2)&(abs(z+2)<=2)
        ring=(np.hypot(x-cx,y-263)>=13)&(np.hypot(x-cx,y-263)<=17)&(abs(z+2)<=2)
        radius=np.interp(y,[113,283,303,325],[0,0,10,0])
        tip=(abs(x-cx)<=radius)&(abs(z+2)<=min(3,radius))&(y>=283)
        state=np.where(shaft|ring|tip,IDS[WHITE],0).astype(np.uint8)
        state[tip&(abs(x-cx)<=3)]=IDS[LIGHT]
        state[shaft&(abs(x-cx)<=1)]=IDS[QSV]
        layers.append((y,x,z,state))
    return a2.part('ice_ceremonial_spear_'+('left' if side<0 else 'right'),layers)


def core():
    x,z=a2.grid(-11,11,14,36)
    layers=[]
    for y in range(149,172):
        distance=np.sqrt(x*x+(y-160)**2+(z-25)**2)
        state=np.where(distance<=11,IDS[RED],0).astype(np.uint8)
        state[distance<=4]=IDS[LIGHT]
        layers.append((y,x,z,state))
    return a2.part('rimestar_small_dark_red_core',layers)


def shard(side,index,cx,cz,bottom,top,width,lean):
    p=a2.crystal(f'outward_ice_prism_{side:+d}_{index}',side*cx,cz,bottom,top,width,lean,
        math.atan2(cz+5,side*cx))
    return p


def build():
    entries=[(a2.deck(),'全投影承托基座'),(a2.machinery(),'后部退台冷凝机房'),
        (pedestal(),'中央低温集流承台'),(lower_shell(),'陨冰银白倒锥凝态室'),
        (spindle(),'纯冰纤细凝态中轴'),(core(),'分缝内小面积暗红核心'),
        (crown(),'第19章陨冰宽扁悬冠盘'),(crest(),'纯冰分叉结晶尖徽')]
    for side,name in [(-1,'左'),(1,'右')]:
        entries += [(a2.loop(side),name+'低位闭合冷媒回路')]
        entries += [(a2.heat(side,z),name+f'独立热端机组{i+1}') for i,z in enumerate([-245,0,245])]
        entries += [(blade(side),name+'陨冰包合银白弧刃'),(trailing_blade(side),name+'纯冰长带裙刃'),
            (spear(side),name+'独立细长冰矛与镂空环')]
        for i,(cx,cz,bottom,top,width,lean) in enumerate([(205,-124,43,231,14,14),(206,123,43,189,17,18),
            (112,-166,43,203,16,16),(157,171,43,157,17,19)],1):
            entries.append((shard(side,i,cx,cz,bottom,top,width,lean),name+f'外张错落冰蓝棱柱{i}'))
    entries += [(a2.control(),'前庭居中主控台')]
    PARTS[:]=[dict(id=p.name,name=name) for p,name in entries]
    parts=[p for p,_ in entries]
    low=np.min([p.p.min(0) for p in parts],axis=0)
    high=np.max([p.p.max(0) for p in parts],axis=0)
    size=high-low+1
    cube=np.zeros((size[1],size[2],size[0]),np.uint8)
    owners=np.zeros_like(cube)
    for index,p in enumerate(parts,1):
        q=p.p-low
        occupied=owners[q[:,1],q[:,2],q[:,0]]
        collision=np.flatnonzero(occupied)
        if len(collision):
            c=collision[0]
            raise ValueError(f'{p.name} 交叠{len(collision)}格；坐标{p.p[c].tolist()}，原构件{parts[int(occupied[c])-1].name}')
        owners[q[:,1],q[:,2],q[:,0]]=index
        cube[q[:,1],q[:,2],q[:,0]]=p.states
    footprint=owners[11-low[1]]==1
    projection=(owners>1).any(axis=0)
    outside=int((projection&~footprint).sum())
    margin=int(distance_transform_cdt(footprint,metric='chessboard')[projection].min())-1
    if outside:
        raise ValueError(f'上部投影超出基座{outside}列')
    crystals=[]
    for p in parts:
        if p.name.startswith('outward_ice_prism'):
            q=p.p-p.p.min(0)
            solid=np.zeros(tuple(q.max(0)+1),bool)
            solid[tuple(q.T)]=True
            crystals.append(dict(id=p.name,blocks=len(p.p),six_connected_components=int(label(solid)[1])))
    clearance=dict(method='所有完整独立构件按整数格在合并前查重；交叠即停止，不覆盖消解或裁切。',
        independent_components=len(parts),checked_component_pairs=len(parts)*(len(parts)-1)//2,
        cross_component_overlapping_voxels=0,overlap_pairs=[],all_static=True,runtime_animation=False,
        crystal_connectivity=crystals,base_projection=dict(bottom_size_wd=[801,721],
            outside_top_deck_columns=outside,minimum_projected_border_margin_voxels=margin),
        critical_clearances=[dict(first='中央承台',second='悬浮倒锥',surface_gap_voxels=24,method='完整Y边界60与85'),
            dict(first='纤细凝态中轴',second='陨冰扁冠盘',surface_gap_voxels=11,method='完整Y边界311与323'),
            dict(first='左右冷媒回路',second='中热端脚座',surface_gap_voxels=3,method='完整X边界322与326')],
        intentional_joins='工业底层沿用A2整数格原位几何；主景各悬浮构件保留间隔。构件内材质分区属于同一实体。',
        scope='静态建筑转译与实际占格净空，不代替GT成型、运行或游戏实测。')
    named={p.name:p for p in parts}
    for side in ['left','right']:
        first='rimestar_enclosing_blade_'+side
        for second in ['rimestar_inverted_cone','rimestar_small_dark_red_core']:
            distance=float(cKDTree(named[second].p).query(named[first].p,k=1,p=np.inf,workers=-1)[0].min())
            clearance['critical_clearances'].append(dict(first=first,second=second,
                minimum_center_chebyshev=distance,surface_gap_voxels=int(distance)-1,
                method='完整实际整数格最近切比雪夫中心距减一'))
    def detail(center,half,position):
        return dict(center=(np.array(center)-low).tolist(),half=half,position=(np.array(position)-low).tolist())
    data=dict(title='冰之律者 · 永霜 · 冰律与陨冰凝态宫 A3',name='0005-w06-ice-rimestar-a3',size=size.tolist(),
        controller=(np.array([0,30,310])-low).tolist(),controller_face='south',ports=[],
        summary='参考第18章纯冰律的细冠、细长冰矛与尖角礼装，并结合第19章陨冰的银白倒锥、包合弧刃、窄中轴与宽扁悬冠盘；中央分缝内可见小面积暗红凝态核心，外围错落冰蓝棱柱向上外张。底座、机房、闭合冷媒回路和独立热端沿用A2。全静态。',
        detail_views=dict(core=detail([0,185,39],[160,121,91],[265,225,470]),
            crown=detail([0,306,0],[205,73,125],[420,375,520]),
            heat=detail([351,44,0],[54,55,67],[515,125,230])),
        palette_identity=dict(tier='QSV',name='冰晶蓝',color='#91DCEB',runtime_voltage='WSV'),
        source_blueprint_bounds=dict(min=low.tolist(),max=high.tolist()),source_blueprint_to_export=(-low).tolist(),
        nominal_clipping=False,geometry_clearance=clearance,
        reference_study='logs/0005-w06-ice-rimestar-references-20261115/',
        reference_identity=dict(pure_ice='第18章正式服剧情：FHXHHtfZyvE，1690–1750秒；分叉冠、长白带、独立细矛与镂空环。',
            rimestar='第19章正式服剧情：COQbCcI6Zo8第42秒、lpjSOOh7Epg第85秒；银白倒锥、包合弧刃、窄中轴、宽扁深色冠盘与小面积暗红核心。',
            beta='BETA合成封面不作为正式原帧；未使用源模型。'),
        original_translation='本候选为融合两种原作形体特征的工业建筑转译，比例、工业设施与方块分层均为原创；不宣称角色源模型复刻。',
        animation_enabled=False,approved=False,installed=False,game_verified=False)
    print('W06 A3几何完成',size.tolist(),int(np.count_nonzero(cube)),len(parts),'交叠0，基座外投影',outside,'外沿',margin,flush=True)
    return cube,owners,data
