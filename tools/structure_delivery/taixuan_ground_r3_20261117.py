import numpy as np
from scipy.ndimage import distance_transform_edt

import taixuan_landscape_20261116 as landscape
from taixuan_common_20261116 import Part, model, ROCK, ROCK_DARK, ROCK_PALE


def terrace(source, courtyard):
    p=Part('terrace','观前连续承岩台地',inference='按院坪实际底面重建上部承岩，保留下部原岩体；轮廓渐变和岩层为项目补建。')
    keep=source.p[:,1]<108
    p.chunks.append(source.p[keep])
    p.values.append(source.states[keep])
    lower=source.p[source.p[:,1]==107][:,[0,2]]
    upper=courtyard.p[courtyard.p[:,1]==157][:,[0,2]]
    extent=np.concatenate([lower,upper])
    lo,hi=extent.min(0)-2,extent.max(0)+2
    z,x=np.mgrid[lo[1]:hi[1]+1,lo[0]:hi[0]+1]
    fields=[]
    for points in [lower,upper]:
        mask=np.zeros(x.shape,bool)
        mask[points[:,1]-lo[1],points[:,0]-lo[0]]=True
        fields.append(distance_transform_edt(mask)-distance_transform_edt(~mask))
    for y in range(108,157):
        t=(y-107)/49
        mask=fields[0]*(1-t)+fields[1]*t>0
        xx,zz=x[mask],z[mask]
        seam=((xx+(zz//28)*7)//29+zz//34+y//37+2)%11
        states=np.full(len(xx),ROCK,np.uint8)
        states[seam<3]=ROCK_DARK
        states[seam==7]=ROCK_PALE
        p.chunks.append(np.c_[xx,np.full(xx.size,y),zz].astype(np.int32))
        p.values.append(states)
    return model(p,['院坪底面Y157与承岩顶面Y156逐格相接。','上部岩壁由旧截面渐变至院坪真实轮廓。'],
        ['G01','G05','G06','G08','G09','O15'],{})


def path_bed(terrain,road):
    p=Part('path_rock','石阶下连续岩脊',inference='按道路实际底面与已有岩体顶面补齐承岩；属于项目地形衔接。')
    lo=np.min([part.p.min(0) for part in terrain+[road]],axis=0)
    hi=np.max([part.p.max(0) for part in terrain+[road]],axis=0)
    columns,index=np.unique(road.p[:,[0,2]],axis=0,return_inverse=True)
    bottom=np.full(len(columns),1000,np.int32)
    np.minimum.at(bottom,index,road.p[:,1])
    height=np.full((hi[2]-lo[2]+1,hi[0]-lo[0]+1),-1,np.int32)
    tops=np.full(height.shape,1000,np.int32)
    tops[columns[:,1]-lo[2],columns[:,0]-lo[0]]=bottom-1
    for part in terrain:
        q=part.p
        q=q[q[:,1]<=tops[q[:,2]-lo[2],q[:,0]-lo[0]]]
        np.maximum.at(height,(q[:,2]-lo[2],q[:,0]-lo[0]),q[:,1])
    anchors={}
    for (x,z),top in zip(columns,bottom-1):
        ground=height[z-lo[2],x-lo[0]]
        if ground<0:
            y=int(top)-12
            if y not in anchors:
                mask=np.zeros(height.shape,bool)
                for part in terrain:
                    q=part.p[part.p[:,1]==y]
                    mask[q[:,2]-lo[2],q[:,0]-lo[0]]=True
                anchors[y]=distance_transform_edt(~mask,return_distances=False,return_indices=True)
            az,ax=anchors[y][:,z-lo[2],x-lo[0]]
            p.beam((ax+lo[0],y,az+lo[2]),(x,top,z),2,ROCK_DARK)
        elif ground<top:
            p.box((x,ground+1,z),(x,top,z),ROCK_DARK)
    return model(p,['山径底面连续接入已有岩脊，补齐门前与折返处空层。','缺少同列下方岩体处，以斜向岩肩接入邻近山岩。'],['G02','G07','G08','A01'],{})


def build():
    terrain=landscape.terrain()
    courtyard=landscape.courtyard()
    terrain[0]=terrace(terrain[0],courtyard)
    road=landscape.paths()
    return terrain+[courtyard,path_bed(terrain,road),road,landscape.foliage(),landscape.waterfall()]
