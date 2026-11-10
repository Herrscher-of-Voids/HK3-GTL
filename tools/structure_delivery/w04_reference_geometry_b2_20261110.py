# -*- coding: utf-8 -*-
"""按44张分源参考重做雷龙与七雷；B1场景其余十三构件逐格保留。"""
from copy import deepcopy
from pathlib import Path
import json
import math
import numpy as np
import w04_gemini_dragon_b1_20261110 as b
from w02_19c_geometry_v2_20261110 import panel
from w02_bunny_dock_geometry_v3_20261108 import encode

ROOT=b.ROOT
OUT=ROOT/'deliveries/W04_俱利伽罗七雷_参考校准_B2_20261110'
LOG=ROOT/'logs/w04-reference-b2-20261110'
PRIOR=b.OUT
BLACK,DARK,RED,GOLD,SILVER,LIGHT,GLASS,VIOLET=b.STATES
WHITE='minecraft:white_concrete'
PURPLE='minecraft:purple_concrete'
PINK='minecraft:magenta_concrete'
STATES=b.STATES+[WHITE,PURPLE,PINK]
IDS={s:i+1 for i,s in enumerate(STATES)}
ROLES={**b.ROLES,WHITE:'参考中的长角、腹甲与刀柄白色缠带',
    PURPLE:'鸣雷见紫色实体刃面',PINK:'鸣雷见亮紫刃口与龙眼窄光纹'}


class Part(b.Part):
    def points(self,points,state):
        a=np.rint(points).astype(np.int32).reshape(-1,3)
        if len(a):
            assert np.all(abs(a)<2048),'只报错，不裁切完整几何'
            self.chunks.append(a);self.values.append(np.full(len(a),IDS[state],np.uint8))


def plate(p,outline,z0,z1,state):
    panel(p,outline,z0,z1,state,0)


def blade(p,path,widths,thickness,state,normal=(0,0,1)):
    normal=np.array(normal,float);normal/=np.linalg.norm(normal)
    sections=[]
    for i,(c,width) in enumerate(zip(path,widths)):
        c=np.array(c,float);t=np.array(path[min(i+1,len(path)-1)])-path[max(0,i-1)]
        u=np.cross(normal,t);u/=np.linalg.norm(u)
        sections.append(np.array([c-u*width,c+normal*thickness,c+u*width,c-normal*thickness]))
    b.loft(p,sections,state)


def sword():
    p=Part('03_倒悬涤罪七雷巨刃')
    # R25～R35：弯刃、紫色刃面和枝状镂空护手；不沿用B1三角剑与巴纹圆盘。
    outline=[(-22,55),(-11,71),(-10,96),(-7,118),(-1,145),(2,173),(7,198),
        (13,216),(9,230),(18,246),(22,256),(8,256),(0,244),(-7,234),(-15,228),
        (-12,216),(-20,209),(-16,195),(-19,179),(-21,157),(-23,133),(-21,108),(-20,86)]
    plate(p,outline,-4,4,BLACK)
    luminous=[(-22,55),(-12,74),(-12,100),(-8,122),(-2,148),(1,175),(6,199),
        (12,215),(5,224),(-4,216),(-8,204),(-8,184),(-13,159),(-16,133),(-16,107),(-17,82)]
    for flank in [-1,1]:
        temp=Part('刃面')
        plate(temp,luminous,4,6,PURPLE)
        plate(temp,[(-22,55),(-14,77),(-15,102),(-11,126),(-6,151),(-3,176),
            (0,195),(-5,188),(-10,162),(-15,137),(-18,109),(-18,83)],6,7,PINK)
        temp.finish();temp.p[:,2]*=flank
        for i,state in enumerate(STATES,1):
            points=temp.p[temp.states==i]
            if len(points):p.points(points,state)
        b.trace(p,[[-18,88,flank*8],[-16,112,flank*8],[-12,134,flank*8]],.7,SILVER)
        b.trace(p,[[-9,157,flank*8],[-5,174,flank*8]],.7,LIGHT)
    # 两条分叉护手形成可见开口，轮廓参照超限形态而非原案的130格圆盘。
    for side in [-1,1]:
        q=lambda x,y,z:np.array([side*x,y,z],float)
        route=[q(1,231,0),q(19,242,0),q(29,264,0),q(23,277,0),q(15,268,0)]
        blade(p,route,[3,5,4,.6,.4],3,RED)
        b.trace(p,[q(4,238,4),q(18,249,4),q(24,264,4)],1.2,PURPLE)
        blade(p,[q(8,242,0),q(28,239,0),q(39,221,0)],[4,4,.3],3,BLACK)
        b.trace(p,[q(9,243,4),q(26,240,4),q(38,222,1)],.9,PINK)
        blade(p,[q(4,259,0),q(13,272,0),q(15,283,0)],[4,3,.4],3,PURPLE)
    b.hull(p,[[0,247,8],[9,259,0],[0,271,8],[-9,259,0],[0,259,11],[0,259,-8]],PURPLE)
    plate(p,[(-6,257),(0,250),(6,259),(0,267)],9,11,PINK)
    p.beam([0,273,0],[0,328,0],5,DARK)
    for side in [-1,1]:
        b.trace(p,[[side*6,279,-4],[side*5,280,4]],1.4,PURPLE)
        for y in range(286,325,7):p.beam([-5,y,5],[5,y+5,5],1.1,WHITE)
    blade(p,[[0,322,0],[2,333,0],[1,343,0]],[6,7,.4],4,BLACK)
    plate(p,[(-3,329),(1,326),(5,333),(1,339)],4,6,PURPLE)
    return p.finish()


def local_frame(curve,t):
    tangent=curve(t,1);tangent/=np.linalg.norm(tangent)
    up=np.array([0.,1.,0.]);up-=tangent*np.dot(up,tangent);up/=np.linalg.norm(up)
    right=np.cross(up,tangent);right/=np.linalg.norm(right)
    return tangent,right,up


def dragon_body():
    p=Part('08_俱利伽罗S形分节骨甲龙躯');curve=b.dragon_curve()
    radius=lambda t:float(np.interp(t,[0,.15,.4,.65,.76,.83,.9,1],[2,7,16,30,31,24,12,13]))
    def section(t,scale=1):
        tangent,u,v=local_frame(curve,t);r=radius(t)*scale
        return np.array([curve(t)+u*x*r+v*y*r*.82 for x,y in b.octagon(1,1)])
    b.loft(p,[section(t,.75) for t in np.linspace(0,1,100)],DARK)
    stations=np.linspace(.018,.985,59)
    for a,c in zip(stations[:-1],stations[1:]):
        center=curve((a+c)/2);axis,u,v=local_frame(curve,(a+c)/2);r=radius((a+c)/2)
        # 鳞片按背、左右侧和腹面分开；不再把等截面环套在蛇管上。
        for angles,state in [(np.linspace(.1,math.pi-.1,6),RED),
            (np.linspace(math.pi,2*math.pi,6),BLACK)]:
            rings=[]
            for t,scale in [(a,.9),((a+c)/2,1.04),(c,.86)]:
                cc=curve(t);_,uu,vv=local_frame(curve,t);rr=radius(t)
                rings.append(np.array([cc+(uu*math.cos(ang)+vv*math.sin(ang)*.82)*rr*scale for ang in angles]))
            b.hull(p,np.vstack(rings),state)
        if a>.14:
            belly=center-v*r*.79
            b.hull(p,[belly-u*r*.36-axis*4,belly+u*r*.36-axis*4,belly+axis*6-v*2,
                belly-u*r*.26+axis*4,belly+u*r*.26+axis*4,belly+v*2],SILVER if a<.7 else BLACK)
        if .15<a<.86:
            base=center+v*r*.78
            blade(p,[base-axis*5,base+v*(r*.45+3)-axis*8,base-axis*14],
                [max(2,r*.18),max(1,r*.1),.3],2.2,RED,normal=u)
    # R04、R09、R18：胸前V形叠甲，窄颈与两条收拢后肢。
    for side in [-1,1]:
        q=lambda x,y,z:np.array([side*x,y,z],float)
        for y,z,w in [(217,67,27),(229,66,33),(241,62,32)]:
            b.hull(p,[q(0,y-7,z+3),q(w,y+6,z-3),q(w+4,y+14,z-7),q(0,y+3,z+7),q(0,y-4,z-4)],BLACK)
        leg=[q(47,237,20),q(61,197,25),q(48,165,53),q(53,145,71)]
        b.taper(p,leg,[13,15,9,6],BLACK,.8)
        blade(p,[leg[0]+[0,3,7],leg[1]+[0,2,10],leg[2]+[0,2,6]],
            [10,12,5],3,RED,normal=(0,0,1))
        for dx in [-6,0,6]:
            claw=[leg[-1]+[dx,0,0],leg[-1]+[dx,-7,11],leg[-1]+[dx,-10,16]]
            b.taper(p,claw,[3,3,.3],RED,.7)
    sample=curve(np.linspace(0,1,1001));length=float(np.linalg.norm(np.diff(sample,axis=0),axis=1).sum())
    assert length>650
    return p.finish(),length


def dragon_wing(side):
    p=Part(f'09_{side:+d}_俱利伽罗折角机械雷翼');q=lambda x,y,z:np.array([side*x,y,z],float)
    root=q(26,250,30);elbow=q(95,275,8);wrist=q(146,282,-5)
    b.taper(p,[root,elbow,wrist],[13,10,12],BLACK,.7)
    for a,c in [(root,elbow),(elbow,wrist)]:
        blade(p,[a+[0,4,3],(a+c)/2+[0,8,2],c+[0,4,2]],[9,10,6],3,RED)
    tips=[q(260,319,-98),q(260,278,-53),q(239,242,7),q(200,218,50)]
    normal=np.array([0,.4,1.]);normal/=np.linalg.norm(normal)
    # R02、R11～R16：外端是巨大的分体刃爪，内侧才有暗色膜；不是红色网格蝠翼。
    for i,tip in enumerate(tips):
        start=wrist+q(0,-i*3,i*4)
        mid=start*.42+tip*.58+q(6,12,9)
        route=[start,mid,tip]
        blade(p,route,[9,15 if i<3 else 11,.35],4,RED,normal)
        blade(p,[start-normal*4,mid-normal*4,tip],[6,10,.3],1.2,BLACK,normal)
        inner=[start+q(0,-5,2),mid+q(0,-7,2),tip]
        b.trace(p,inner,1.8,WHITE)
        if i<3:b.trace(p,[mid+normal*4,mid*.55+tip*.45+normal*3,tip],1.2,LIGHT)
    # 膜片保留凹弧缺口，以三角分片表达；中央龙身及翼爪之间仍有透空。
    for i in range(3):
        a=tips[i]*.58+wrist*.42;c=tips[i+1]*.56+wrist*.44
        inner=elbow*.45+root*.55+q(0,-16,-2)
        scallop=(a+c)*.5+q(-16,13,0)
        for triangle in [[inner,a,scallop],[inner,scallop,c]]:
            b.hull(p,[v+normal*d for v in triangle for d in [-1.5,1.5]],DARK)
        b.trace(p,[inner,a],2.2,BLACK);b.trace(p,[inner,c],2.2,BLACK)
    blade(p,[wrist,q(139,252,9),q(120,226,18)],[6,5,.3],3,RED)
    return p.finish()


def dragon_head():
    p=Part('10_俱利伽罗鬼角龙首与张开双颚')
    # R09和R36：细长面甲、白色外角、红色V额甲与侧眼环；不使用B1矩形截面箱头。
    sections=[]
    for z,rx,low,high in [(77,12,244,268),(94,19,243,278),(113,17,239,270),(133,10,231,251),(146,2,230,235)]:
        sections.append(np.array([[0,high,z],[-rx,high-8,z],[-rx,low+4,z],[0,low,z],
            [rx,low+4,z],[rx,high-8,z]]))
    b.loft(p,sections,BLACK)
    plate(p,[(0,277),(-12,287),(-10,272),(0,260),(10,272),(12,287)],109,113,SILVER)
    plate(p,[(0,238),(-12,265),(-7,264),(0,252),(7,264),(12,265)],131,134,RED)
    for side in [-1,1]:
        q=lambda x,y,z:np.array([side*x,y,z],float)
        blade(p,[q(4,271,95),q(17,265,110),q(4,236,143)],[6,8,.5],3,RED)
        blade(p,[q(10,261,104),q(24,253,116),q(12,236,134)],[7,7,.5],3,RED)
        # 角基延续额冠，白色朝外、暗色内芯；角尖向后上收束。
        horns=[q(12,272,94),q(20,291,87),q(30,311,77),q(34,331,66)]
        blade(p,horns,[6,6,3,.35],3,WHITE)
        blade(p,[h+[0,-2,-3] for h in horns],[4,4,2,.25],1.5,BLACK)
        blade(p,[q(12,270,103),q(29,287,91),q(38,298,85)],[5,4,.4],2.5,RED)
        for x,y,z in [(21,249,95),(18,241,94)]:
            blade(p,[q(x,y,z),q(x+8,y+4,z-12),q(x+12,y+9,z-24)],
                [5,5,.3],2,RED)
        eye=q(17,254,111)
        b.annulus(p,eye,[side,0,.12],7,4.5,3,DARK)
        b.annulus(p,eye+[side*2,0,0],[side,0,.12],4.6,0,2,PINK)
        b.annulus(p,eye+[side*3,0,0],[side,0,.12],2.8,0,2,LIGHT)
        b.trace(p,[q(17,252,113),q(12,248,129)],1.2,WHITE)
        b.trace(p,[q(21,256,104),q(16,266,96),q(14,275,89)],1.4,SILVER)
        plate(p,[(side*8,277),(side*4,274),(side*4,270),(side*8,273)],114,115,GOLD)
    jaw=[np.array([[-r,y,z],[0,y-3,z],[r,y,z],[0,y+4,z]]) for z,r,y in
        [(88,13,230),(111,15,216),(140,7,214),(147,1,219)]]
    b.loft(p,jaw,BLACK)
    for side in [-1,1]:
        q=lambda x,y,z:np.array([side*x,y,z],float)
        b.trace(p,[q(12,224,100),q(14,215,119),q(6,215,140)],2,RED)
        for z,x,y in [(117,11,236),(129,8,233),(138,5,231)]:
            b.taper(p,[q(x,y,z),q(x-1,y-7,z+1)],[2,.25],WHITE,.7)
    blade(p,[[0,275,91],[0,285,80],[0,289,73]],[5,4,.4],3,BLACK)
    return p.finish()


def dragon_claw(side):
    p=Part(f'11_{side:+d}_俱利伽罗扣环机械前爪');q=lambda x,y,z:np.array([side*x,y,z],float)
    route=[q(26,232,65),q(61,210,75),q(95,213,88),q(123,225,92)]
    b.taper(p,route,[9,8,7,7],BLACK,.8)
    blade(p,[route[0]+[0,6,4],route[1]+[0,5,5],route[2]+[0,5,5]],
        [7,8,5],3,RED)
    for z in [-9,0,9]:
        finger=[q(122,226,92+z),q(144,235,95+z),q(151,222,98+z),q(145,211,101+z)]
        b.taper(p,finger,[3.8,3.5,3,.3],BLACK,.8)
        b.taper(p,finger[-2:],[3,.3],RED,.7)
    return p.finish()


def load_prior():
    file=b.LOG/'components.npz'
    with np.load(file) as cache:
        parts=[]
        for key in cache.files:
            if not key.endswith('__p'):continue
            name=key[:-3];part=Part(name);part.p=cache[key].copy();part.states=cache[name+'__states'].copy();parts.append(part)
    return parts


def build():
    prior=load_prior();parts=[];length=0;replaced=[];unchanged=[]
    for old in prior:
        name=old.name
        if name.startswith('03_'):new=sword()
        elif name.startswith('08_'):new,length=dragon_body()
        elif name.startswith('09_'):new=dragon_wing(-1 if '-1_' in name else 1)
        elif name.startswith('10_'):new=dragon_head()
        elif name.startswith('11_'):new=dragon_claw(-1 if '-1_' in name else 1)
        else:new=old
        assert new.name==name
        if new is old:unchanged.append(name)
        else:replaced.append(name)
        parts.append(new);print(name,len(new.p),flush=True)
    assert len(unchanged)==13 and len(replaced)==7
    for name in unchanged:
        a=next(p for p in prior if p.name==name);c=next(p for p in parts if p.name==name)
        assert np.array_equal(a.p,c.p) and np.array_equal(a.states,c.states)
    lo=np.min([p.p.min(0) for p in parts],axis=0);hi=np.max([p.p.max(0) for p in parts],axis=0);size=hi-lo+1
    cube=np.zeros((size[1],size[2],size[0]),np.uint8)
    for p in parts:
        at=p.p-lo;cube[at[:,1],at[:,2],at[:,0]]=p.states
    data=deepcopy(json.loads((PRIOR/'manifest.json').read_text('utf8')))
    data.update(name='hk3gtl-w04-reference-b2-20261110',title='雷之律者 · 鸣霆·超导电磁天枢 · 图片校准B2',
        display_version='B2',size=size.tolist(),blocks=int(np.count_nonzero(cube)),blueprint_bounds=dict(min=lo.tolist(),max=hi.tolist()),
        blueprint_to_export_offset_xyz=(-lo).tolist(),dragon_centerline_length=length,
        unchanged_components=unchanged,replaced_components=replaced,reference_manifest='参考图清单.json',
        summary='保留B1的托卡马克、鸟居、双塔、鬼手锁环场景；按分源图片重做俱利伽罗白角V形面甲、长颈叠甲、红色分体翼爪和细尾，并将中央巨刀改为涤罪七雷·鸣雷见的修长紫色弯刃与镂空护手。',
        detail_views=dict(dragon=dict(center=[0,268,110],half=[58,75,61]),
            hand=data['detail_views']['hand'],sword=dict(center=[0,200,0],half=[50,148,35]),
            wing=dict(center=[145,275,-8],half=[150,65,115]),body=dict(center=[20,198,-67],half=[190,150,225]),
            dragonfront=dict(center=[0,268,110],half=[58,75,61]),dragonside=dict(center=[0,268,110],half=[58,75,61]),
            dragonall=dict(center=[20,198,-67],half=[280,180,250])))
    data['source_conflicts']=[s for s in data['source_conflicts'] if '130' not in s and '太刀局部' not in s]
    data['source_conflicts']+=['负责人要求图片校准后，B2有意替换原案宽三角刀与130格巴纹刀锷；按鸣雷见的修长紫色弯刃和枝状镂空护手重做，不再声称逐条照搬Gemini原文。',
        '44张参考含20张官方教学原帧、19张玩家游戏原帧和5张社区转存图；鸣、鸣雷见分组，鸣雷神为技能名。',
        '白角、V形红面甲、暗色叠甲胸腹、刃状翼爪有画面依据；盘枢长尾、超尺度姿态、额外扣环前肢与工业连接属于场景转译，遮挡处仍待核对。',
        '原案红色透明激光翼膜改为参考中的暗色薄膜与实体红色翼爪；保留少量静态白光纹，未启用动画。',
        '底盘、鸟居、三环、双塔、双机械鬼手、十道锁链、龙口光束及尾部锚座十三构件逐格保持B1；因此既有场景干涉仍不能视为已修复。']
    LOG.mkdir(exist_ok=True)
    (LOG/'geometry-delta.json').write_text(json.dumps(dict(passed=True,unchanged=unchanged,replaced=replaced,
        no_nominal_clipping=True,reference_images=44,game_verified=False),ensure_ascii=False,indent=2)+'\n','utf8')
    return cube,data,parts


if __name__=='__main__':
    cube,data,parts=build();print(data['size'],data['blocks'])
