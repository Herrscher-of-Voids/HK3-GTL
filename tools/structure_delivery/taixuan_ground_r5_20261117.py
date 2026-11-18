import math

import numpy as np

import taixuan_landscape_20261116 as landscape
import taixuan_ground_r4_20261117 as ground
import taixuan_detail_r2_20261116 as detail
from taixuan_common_20261116 import Part, model, PAVING, ROCK_PALE, MOSS, GRASS, LEAF


ROUTE=np.array([[0,160,164],[0,148,197],[-58,119,222],[70,87,250],[47,58,284]],float)
landscape.ROUTE=detail.ROUTE=ROUTE


def paths():
    road=landscape.paths()
    p=Part(road.name,road.label)
    p.chunks.append(road.p)
    p.values.append(road.states)
    p.box((-8,157,149),(8,160,164),PAVING)
    p.box((-8,161,149),(8,161,151),ROCK_PALE)
    return model(p,road.metadata['features']+['八卦台前短径沿X0中轴穿过山门，直行下坡后接折返石阶。'],
        road.metadata['references'],road.metadata['views'])


def foliage():
    trees=landscape.foliage()
    p=Part(trees.name,trees.label)
    p.chunks.append(trees.p)
    p.values.append(trees.states)
    specs=[(-106,161,-36,37,3),(101,161,-38,43,6),(-117,161,96,27,7),
        (112,162,112,32,2),(-175,321,-169,29,1),(168,328,-177,24,4),
        (-187,181,112,28,5),(185,207,117,25,8),(-263,262,7,22,9)]
    for cx,y,cz,h,seed in specs:
        c=np.array([cx+int(7*math.sin(seed)),y+h-1,cz+4])
        z,x=np.mgrid[c[2]-10:c[2]+11,c[0]-12:c[0]+13]
        for yy in range(c[1]-5,c[1]+6):
            shape=((x-c[0])/12)**2+((z-c[2])/10)**2+((yy-c[1])/5)**2
            mask=shape<1+.12*np.sin(x*.55+seed)*np.cos(z*.4)
            p.points(np.c_[x[mask],np.full(mask.sum(),yy),z[mask]],LEAF)
    views=dict(trees.metadata['views'])
    views['all_pines']=dict(label='全部九棵古松',center=[0,260,-38],half=[315,116,250],direction=[-.6,.7,1])
    return model(p,trees.metadata['features']+['九棵松树主干顶补横展扁冠，枝梢与原叶簇衔接。'],
        trees.metadata['references'],views)


def bamboo(terrain):
    p=Part('trees','山径竹丛与苔石踏步')
    lo=np.min([part.p.min(0) for part in terrain],axis=0)
    hi=np.max([part.p.max(0) for part in terrain],axis=0)
    heights=np.full((hi[2]-lo[2]+1,hi[0]-lo[0]+1),-1,np.int32)
    for part in terrain:
        q=part.p
        np.maximum.at(heights,(q[:,2]-lo[2],q[:,0]-lo[0]),q[:,1])
    zz,xx=np.mgrid[lo[2]:hi[2]+1,lo[0]:hi[0]+1]
    for index,(a,b) in enumerate(zip(ROUTE[1:-1],ROUTE[2:]),1):
        delta=(b-a)[[0,2]]
        across=np.array([-delta[1],delta[0]])/np.linalg.norm(delta)
        for j in range(4):
            c=np.rint(a+(b-a)*(.22+j*.18)).astype(int)
            side=1 if index%2 else -1
            x,z=np.rint(c[[0,2]]+across*14*side).astype(int)
            shoulder=(heights>=c[1]-10)&(heights<=c[1]+5)&(np.hypot(xx-c[0],zz-c[2])>=11)
            distance=np.where(shoulder,(xx-x)**2+(zz-z)**2,np.inf)
            iz,ix=np.unravel_index(np.argmin(distance),distance.shape)
            x,z=int(xx[iz,ix]),int(zz[iz,ix])
            y=int(heights[z-lo[2],x-lo[0]])
            p.points([(x,y,z)],MOSS)
            h=17+(j*5+index*3)%13
            p.box((x,y+1,z),(x,y+h,z),GRASS)
            for yy in range(y+4,y+h,5):
                p.points([(x,yy,z)],MOSS)
            for k in range(3):
                yy=y+h-k*5
                d=1 if (j+k)%2 else -1
                for u in range(1,5):
                    p.points([(x+d*u,yy+u//3,z),(x+d*u,yy+u//3,z+1)],LEAF)
    return model(p,['竹丛随新山径布置于路外岩肩，根部贴实际岩面；山门前直路留空。'],['R2G08'],
        {'bamboo':dict(label='山径竹丛',center=[30,108,240],half=[89,60,65],direction=[.9,.6,1])})


def build():
    terrain=landscape.terrain()
    courtyard=landscape.courtyard()
    terrain[0]=ground.island(terrain[0],courtyard)
    terrain[-1]=landscape.mountain('path_rock','入山折径岩脊',(27,191),
        [(5,19,45,-10,0),(39,58,93,0,0),(76,82,96,0,-12),
            (112,86,79,-9,-15),(143,70,56,-14,-25),(162,52,32,-27,-31)],
        7,['G02','G07','G08','A01'])
    road=paths()
    gate=detail.gate()
    gate.metadata['views']['gate_detail']=dict(label='中轴三间山门',center=[0,184,164],half=[48,30,30],direction=[0,.28,1])
    gate.metadata['features'].append('山门中心固定X0、Y160、Z164，横向沿X展开，正对八卦台。')
    return terrain+[courtyard,ground.path_bed(terrain,road),road,foliage(),landscape.waterfall(),bamboo(terrain),gate]
