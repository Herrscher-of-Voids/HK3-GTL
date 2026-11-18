import math

import numpy as np
from scipy.ndimage import affine_transform

from w09_common_20261116 import Part, ARMOR, DARK, GOLD, RED, GILDED, CENTER
from w08_common_20261116 import rod
from w09_core_20261116 import feather_template, cognitive_core
from w09_landscape_20261116 import fan, chain, link_samples


CORE=np.array([0,-180,0])


def build():
    parts=[]
    leaf=feather_template()
    for i,(radius,normal) in enumerate(zip((100,132,164),([0,.42,.9075],[.78,.55,.3],[-.55,.4,.733]))):
        n=np.array(normal,float);n/=np.linalg.norm(n)
        u=np.cross(n,[0,1,0]);u/=np.linalg.norm(u)
        v=np.cross(n,u)
        ring=Part(f'fusion_feather_{i+1}',f'分层羽刃核心环{i+1}',section='core',
            center=CORE.tolist(),outer_radius=radius,inner_radius=radius-20,
            normal=n.tolist(),feathers=40,motion='第一稿静态排位')
        ring.ring(CORE,radius-1,2,ARMOR,normal=n,depth=3)
        for j in range(40):
            a=math.tau*j/40+i*.026
            radial=u*math.cos(a)+v*math.sin(a)
            tangent=-u*math.sin(a)+v*math.cos(a)
            rr=radius-20+(leaf.p[:,0]-45)*20/45
            q=CORE+rr[:,None]*radial+leaf.p[:,1:2]*tangent+leaf.p[:,2:3]*n
            for s in np.unique(leaf.states):ring.points(q[leaf.states==s],int(s))
        parts.append(ring.finish())
    for p in cognitive_core():
        p.p+=CORE-np.asarray(CENTER,dtype=int)
        p.name='fusion_'+p.name
        p.metadata=dict(section='core',center=CORE.tolist())
        parts.append(p)
    frame=Part('fusion_core_collar','核心外侧固定约束环',section='core_frame',clearance_radius=185)
    for y in (-210,-180,-150):
        frame.ring([0,y,0],195,5,ARMOR,depth=4)
        frame.ring([0,y+3,0],195,1,GOLD,depth=1)
    for a in np.arange(8)*math.pi/4:
        x,z=192*math.cos(a),192*math.sin(a)
        rod(frame,[x,-215,z],[x,-145,z],3,GILDED)
    parts.append(frame.finish())
    samples=link_samples()
    for i in range(8):
        for j in range(4):
            a=i*math.pi/4+(j-1.5)*.025
            start=[400*math.cos(a),-330+j*8,400*math.sin(a)]
            end=[193*math.cos(a),-210+j*20,193*math.sin(a)]
            p=chain(i*4+j+1,start,end,samples,12,'下层矩阵约束梁',i)
            p.name='fusion_'+p.name
            parts.append(p)
    p=fan()
    low=p.p.min(0)
    size=p.p.max(0)-low+1
    cube=np.zeros(tuple(size),np.uint8)
    cube[tuple((p.p-low).T)]=p.states
    matrix=np.diag([1.6,2,-.7]);inverse=np.linalg.inv(matrix)
    pivot=np.array([487,187,900])-low
    corners=np.array(np.meshgrid(*[(0,n-1) for n in size],indexing='ij')).reshape(3,-1).T
    corners=(corners-pivot)@matrix.T
    lo=np.floor(corners.min(0)).astype(int);hi=np.ceil(corners.max(0)).astype(int)
    volume=affine_transform(cube,inverse,offset=pivot+inverse@lo,
        output_shape=tuple(hi-lo+1),order=0,mode='grid-constant',prefilter=False)
    xyz=np.argwhere(volume)
    p.p,p.states=xyz+lo+[0,130,-550],volume[tuple(xyz.T)]
    p.name,p.label='fusion_fan','后方十八骨机械折扇'
    p.metadata=dict(section='rear',ribs=18,source='原案折扇整数格按新构图重取样')
    parts.append(p)
    stand=Part('fusion_fan_stand','兵匣后方折扇承托',section='rear')
    for side in (-1,1):
        rod(stand,[side*190,-90,-470],[side*190,130,-550],7,ARMOR)
        rod(stand,[side*190,-90,-463],[side*190,130,-543],1.4,RED)
        rod(stand,[side*190,100,-537],[0,130,-550],3,GOLD)
    parts.append(stand.finish())
    return parts,[
        '核心移至(0,-180,0)，三羽环外半径100/132/164，单环羽片径向宽20格，分层排位。',
        '固定约束环在半径190格附近，32条实体锁链连接下层矩阵与固定环。',
        '原案十八骨折扇按新构图扩大并放至后方，连接横卧兵匣承托。',
        '本稿所有兵装、羽环及锁链为静态方块，运动演出随外观评审后设计。']
