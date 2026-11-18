import math

import numpy as np
from scipy.ndimage import distance_transform_edt

import taixuan_landscape_20261116 as landscape
import taixuan_ground_r5_20261117 as previous
from taixuan_water_r6_20261117 import Creek
from taixuan_common_20261116 import Part, model, ROCK, ROCK_DARK, ROCK_PALE, MOSS, LOG, LEAF


ROUTE=previous.ROUTE
PEAKS=[
    ('west_peak','西侧层叠远峰',(-250,-207),[(8,14,18,2,0),(90,38,48,0,0),
        (142,62,62,-4,-6),(174,68,57,-4,-6),(225,47,44,4,-10),
        (258,52,46,4,-11),(302,29,31,0,-8),(329,14,18,-1,-10)],3),
    ('rear_peak','背山远峰',(-55,-310),[(35,17,20,0,0),(135,43,49,0,2),
        (205,62,56,8,0),(246,53,44,8,0),(290,40,38,4,-3),
        (322,44,35,4,-7),(350,24,26,-2,-7),(369,10,13,-2,-7)],6),
    ('east_peak','溪源青岩峰',(198,-192),[(12,15,20,0,0),(100,44,53,0,0),
        (166,73,73,0,0),(205,79,66,0,-2),(250,62,57,-6,-2),
        (278,52,46,-8,-5),(306,33,34,-1,-6),(335,16,20,1,-6)],9),
    ('east_spire','云海外侧岩峰',(345,-57),[(23,9,13,0,0),(100,25,32,0,0),
        (163,46,45,6,-5),(200,39,34,3,-6),(243,29,30,3,-6),
        (269,34,27,3,-7),(292,17,17,-2,-7),(304,8,10,-2,-7)],1),
    ('west_spire','西侧云隙岩峰',(-345,18),[(29,8,12,0,0),(100,24,31,-3,0),
        (153,43,39,0,-4),(192,36,32,5,-8),(224,29,29,5,-8),
        (241,34,25,5,-9),(259,18,18,2,-9),(266,9,11,2,-9)],4),
    ('front_west','左侧云海草峰',(-257,158),[(12,11,17,0,0),(67,32,38,0,0),
        (110,53,49,0,-2),(138,45,42,6,0),(165,30,29,3,-3),
        (185,18,22,2,-5)],8),
    ('front_east','右侧云海草峰',(257,162),[(19,9,13,0,0),(82,33,38,0,0),
        (126,49,44,5,-1),(157,43,35,0,0),(190,29,26,-3,-3),
        (210,17,19,-6,-4)],5)]


def island(source,courtyard,creek):
    p=Part('terrace','草岩主岛与溪谷岩肩')
    keep=source.p[:,1]<58
    p.chunks.append(source.p[keep]);p.values.append(source.states[keep])
    lower=source.p[source.p[:,1]==57][:,[0,2]]
    upper=courtyard.p[courtyard.p[:,1]==157][:,[0,2]]
    extent=np.concatenate([lower,upper,creek.path.astype(int)])
    lo,hi=extent.min(0)-90,extent.max(0)+90
    z,x=np.mgrid[lo[1]:hi[1]+1,lo[0]:hi[0]+1]
    fields=[]
    for points in [lower,upper]:
        mask=np.zeros(x.shape,bool)
        mask[points[:,1]-lo[1],points[:,0]-lo[0]]=True
        fields.append(distance_transform_edt(mask)-distance_transform_edt(~mask))
    angle=np.arctan2(z-7,x)
    margin=40+8*np.sin(angle*3+.7)+6*np.cos(angle*5-1)+4*np.sin(angle*7)
    outside=np.maximum(-fields[1],0)
    cap=160-np.rint(38*np.clip((outside-12)/(margin+2),0,1)**1.7).astype(int)
    cap+=np.where(fields[1]<0,np.rint(4*np.exp(-((outside-17)/13)**2)*np.clip((-z-75)/80,0,1)).astype(int),0)
    distance,water,width=creek.field(x,z)
    shore=water-1+np.rint(np.maximum(distance-width,0)*.45).astype(int)
    blend=np.clip((distance-width-3)/18,0,1)
    raised=np.rint(shore*(1-blend)+cap*blend).astype(int)
    cap=np.where(distance<width+21,np.maximum(cap,raised),cap)
    cap=np.where(distance<=width+1,water-2,cap)
    for start,end in zip(ROUTE[:-1],ROUTE[1:]):
        delta=end[[0,2]]-start[[0,2]]
        t=np.clip(((x-start[0])*delta[0]+(z-start[2])*delta[1])/(delta@delta),0,1)
        d=np.hypot(x-start[0]-t*delta[0],z-start[2]-t*delta[1])
        height=np.floor(start[1]+(end[1]-start[1])*t-4+np.maximum(d-9,0)*.8).astype(int)
        cap=np.where((fields[1]<0)&(d<28),np.minimum(cap,height),cap)
    dz,dx=np.gradient(cap.astype(float))
    grassy=(np.hypot(dx,dz)<1.05)&(cap>=149)
    for y in range(58,int(cap.max())+1):
        t=np.clip((y-57)/65,0,1);t=t*t*(3-2*t)
        ledge=2*np.sin(angle*11+y*.055)+1.1*np.sin(angle*19-y*.04)
        body=fields[1]+margin+14+ledge
        shoulder=(distance<4+20*np.clip((y-80)/65,0,1))&(y>=80)
        mask=((fields[0]*(1-t)+body*t>0)|shoulder)&(y<=cap)
        xx,zz=x[mask],z[mask]
        seam=((xx+(zz//28)*7)//29+zz//34+y//37+2)%11
        states=np.full(len(xx),ROCK,np.uint8)
        states[seam<3]=ROCK_DARK;states[seam==7]=ROCK_PALE
        states[grassy[mask]&(y>=cap[mask]-1)]=MOSS
        states[(distance[mask]<=width[mask]+1)&(y>=cap[mask]-1)]=ROCK_DARK
        p.chunks.append(np.c_[xx,np.full(xx.size,y),zz].astype(np.int32));p.values.append(states)
    return model(p,['主岛保持草岩包覆院坪，东侧岩肩承接弯曲溪谷。',
        '溪岸顺水位升降，水道凹入岩床；岛边下瀑从自然缺口流入云海。'],['G01','G06','O15'],{})


def clear_floor(terrain,courtyard):
    lo=np.min([p.p.min(0) for p in terrain+[courtyard]],axis=0)
    hi=np.max([p.p.max(0) for p in terrain+[courtyard]],axis=0)
    floor=np.full((hi[2]-lo[2]+1,hi[0]-lo[0]+1),-1,np.int32)
    q=courtyard.p
    np.maximum.at(floor,(q[:,2]-lo[2],q[:,0]-lo[0]),q[:,1])
    for part in terrain:
        q=part.p;limit=floor[q[:,2]-lo[2],q[:,0]-lo[0]]
        keep=(limit<0)|(q[:,1]<limit)
        part.p,part.states=part.p[keep],part.states[keep]


def foliage(terrain):
    p=Part('trees','避让建筑的古松与草台')
    specs=[(-175,55,37,3,'terrace'),(150,16,43,6,'terrace'),(-117,96,27,7,'terrace'),
        (112,112,32,2,'terrace'),(-249,-217,29,1,'west_peak'),(199,-198,32,4,'east_peak'),
        (-255,153,28,5,'front_west'),(251,158,25,8,'front_east'),(-343,9,22,9,'west_spire')]
    by_name={part.name:part for part in terrain}
    for cx,cz,h,seed,name in specs:
        ground=by_name[name].p
        y=int(ground[(ground[:,0]==cx)&(ground[:,2]==cz),1].max())+1
        top=np.array([cx+int(7*math.sin(seed)),y+h,cz+4],float)
        bend=np.array([cx+math.sin(seed)*5,y+h*.5,cz-5])
        p.beam([cx,y,cz],bend,2.7,LOG);p.beam(bend,top,2.1,LOG)
        crowns=[]
        for j in range(5):
            angle=j*2.4+seed;length=12+(j*7+seed)%15
            c=top+[math.cos(angle)*length,-j*4,math.sin(angle)*length*.72]
            p.beam(bend,c,1.6,LOG)
            crowns.append((c,np.array([9+(j+seed)%3*3,4+j%3,6+(j+seed)%4*2])))
        crowns.append((top+[0,-1,0],np.array([12,5,10])))
        for c,radii in crowns:
            lo=np.floor(c-radii).astype(int);hi=np.ceil(c+radii).astype(int)
            z,x=np.mgrid[lo[2]:hi[2]+1,lo[0]:hi[0]+1]
            for yy in range(lo[1],hi[1]+1):
                shape=((x-c[0])/radii[0])**2+((z-c[2])/radii[2])**2+((yy-c[1])/radii[1])**2
                mask=shape<1+.12*np.sin(x*.55+seed)*np.cos(z*.4)
                p.points(np.c_[x[mask],np.full(mask.sum(),yy),z[mask]],LEAF)
    for cx,cz in [(-140,-10),(-140,17),(119,-7),(99,129),(-81,132)]:
        for j in range(4):
            p.sphere([cx+j*3,163+j%2,cz+2*math.sin(j)],3,LEAF)
    return model(p,['西廊原松移到廊外草岩肩，东侧松移离主殿屋檐。','外峰松随山体重新落根，九棵均保留中央顶冠。'],
        ['G01','G06','O02','O03','O15'],
        {'pine':dict(label='廊外古松',center=[-175,181,55],half=[45,40,43],direction=[-.7,.4,1]),
            'all_pines':dict(label='全部九棵古松',center=[0,260,-50],half=[390,116,300],direction=[-.6,.7,1])})


def build():
    source=landscape.mountain('terrace','观前主台地',(0,0),
        [(25,32,41,-12,4),(58,87,103,8,0),(108,151,151,0,-5),
            (154,160,159,0,-5),(161,151,151,0,-5)],2,['G01','G06','O15'])
    peaks=[]
    for n,l,c,s,seed in PEAKS:
        part=landscape.mountain('creek_peak' if n=='east_peak' else n,l,c,s,seed,['G01','G05','G06','G08','G09','O15'])
        part.name=n
        peaks.append(part)
    creek=Creek(peaks[2])
    courtyard=landscape.courtyard()
    terrain=[island(source,courtyard,creek)]+peaks+[landscape.mountain('path_rock','入山折径岩脊',(27,191),
        [(5,19,45,-10,0),(39,58,93,0,0),(76,82,96,0,-12),(112,86,79,-9,-15),
            (143,70,56,-14,-25),(162,52,32,-27,-31)],7,['G02','G07','G08','A01'])]
    terrain=[creek.carve(part) for part in terrain]
    clear_floor(terrain,courtyard)
    road=previous.paths()
    gate=previous.detail.gate()
    gate.metadata['views']['gate_detail']=dict(label='中轴三间山门',center=[0,184,164],half=[48,30,30],direction=[0,.28,1])
    return terrain+[courtyard,previous.ground.path_bed(terrain,road),road,foliage(terrain),
        creek.water(),previous.bamboo(terrain),gate]
