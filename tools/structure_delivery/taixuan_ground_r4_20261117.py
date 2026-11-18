import numpy as np
from scipy.ndimage import distance_transform_edt

import taixuan_landscape_20261116 as landscape
from taixuan_ground_r3_20261117 import path_bed
from taixuan_common_20261116 import Part, model, ROCK, ROCK_DARK, ROCK_PALE, MOSS


def island(source,courtyard):
    p=Part('terrace','草岩嵌观主岛',inference='按负责人要求扩大主岛，以自然草坡包入院坪基础，岩腹同步外扩；新增地形属于项目设计。')
    keep=source.p[:,1]<58
    p.chunks.append(source.p[keep])
    p.values.append(source.states[keep])
    lower=source.p[source.p[:,1]==57][:,[0,2]]
    upper=courtyard.p[courtyard.p[:,1]==157][:,[0,2]]
    extent=np.concatenate([lower,upper])
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
    slope=np.clip((outside-12)/(margin+2),0,1)
    cap=160-np.rint(38*slope**1.7).astype(int)
    bank=np.rint(4*np.exp(-((outside-17)/13)**2)*np.clip((-z-75)/80,0,1)).astype(int)
    cap+=np.where(fields[1]<0,bank,0)
    river=127+42*(np.clip((z+117)/99,0,1)**2)
    channel=(z>=-117)&(z<=-18)&(abs(x-river)<=6)
    cap[channel]=np.minimum(cap[channel],159)
    outlet=(x>=164)&(abs(z+17)<6+np.maximum(x-169,0)*.18)
    cap[outlet]=np.minimum(cap[outlet],50)
    for start,end in zip(landscape.ROUTE[:-1],landscape.ROUTE[1:]):
        delta=end[[0,2]]-start[[0,2]]
        t=np.clip(((x-start[0])*delta[0]+(z-start[2])*delta[1])/(delta@delta),0,1)
        distance=np.hypot(x-start[0]-t*delta[0],z-start[2]-t*delta[1])
        height=np.floor(start[1]+(end[1]-start[1])*t-4+np.maximum(distance-9,0)*.8).astype(int)
        cap=np.where((fields[1]<0)&(distance<28),np.minimum(cap,height),cap)
    dz,dx=np.gradient(cap.astype(float))
    grassy=(np.hypot(dx,dz)<.95)&(cap>=150)
    for y in range(58,int(cap.max())+1):
        t=np.clip((y-57)/65,0,1)
        t=t*t*(3-2*t)
        ledge=2*np.sin(angle*11+y*.055)+1.1*np.sin(angle*19-y*.04)
        body=fields[1]+margin+14+ledge
        mask=(fields[0]*(1-t)+body*t>0)&(y<=cap)
        xx,zz=x[mask],z[mask]
        seam=((xx+(zz//28)*7)//29+zz//34+y//37+2)%11
        states=np.full(len(xx),ROCK,np.uint8)
        states[seam<3]=ROCK_DARK
        states[seam==7]=ROCK_PALE
        states[grassy[mask]&(y>=cap[mask]-1)]=MOSS
        p.chunks.append(np.c_[xx,np.full(xx.size,y),zz].astype(np.int32))
        p.values.append(states)
    return model(p,['主岛在院坪外扩出起伏草坡与不规则岩肩，浅色基础嵌入岛面。',
        '承重岩腹同步加宽，从宽肩分层收向原岛底。','上山石阶沿草岩缓坡进入院坪。'],
        ['G01','G05','G06','G08','G09','O15'],{})


def build():
    terrain=landscape.terrain()
    courtyard=landscape.courtyard()
    terrain[0]=island(terrain[0],courtyard)
    road=landscape.paths()
    return terrain+[courtyard,path_bed(terrain,road),road,landscape.foliage(),landscape.waterfall()]
