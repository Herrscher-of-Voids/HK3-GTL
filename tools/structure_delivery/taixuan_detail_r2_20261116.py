import math

import numpy as np

from taixuan_common_20261116 import Part, model, PAVING, ROCK, ROCK_DARK, ROCK_PALE, MOSS, GRASS, LEAF, WOOD, FRAME, ROOF
from taixuan_landscape_20261116 import ROUTE
from taixuan_architecture_r2_20261116 import _roof


def bridge():
    p=Part('mountain_path','观东溪上石拱桥',inference='桥面起拱、低实栏与方柱来自R2G15；跨径、拱腹和接入观东水道的位置为本项目补建。')
    for x in range(126,170):
        t=(x-126)/43
        y=163+round(5*math.sin(math.pi*t))
        p.box((x,y-3,-54),(x,y,-40),PAVING)
        for z in (-54,-40):
            p.box((x,y+1,z),(x,y+4,z),ROCK_PALE)
            p.box((x,y+5,z),(x,y+5,z),PAVING)
        if (x-126)%10==0 or x==169:
            for z in (-54,-40):
                p.box((x-1,y+1,z-1),(x+1,y+6,z+1),ROCK_DARK)
                p.box((x-1,y+7,z-1),(x+1,y+7,z+1),PAVING)
    for x in (126,168):
        p.box((x,156,-53),(x+1,162,-41),ROCK_DARK)
        p.box((x-2,160,-57),(x+3,161,-55),MOSS)
    for sign,edge in [(-1,126),(1,169)]:
        for step in range(1,4):
            x=edge+sign*step
            p.box((x,160,-51),(x,163-step,-43),PAVING)
    return model(p,['观东水道上补凸拱石桥，桥面逐格起伏、低石栏与方形栏柱。'],['R2G15'],
        {'bridge':dict(label='溪上石桥',center=[148,166,-47],half=[28,16,15],direction=[.7,.5,1])})


def creek_bank():
    p=Part('terrace','溪桥东岸岩台',inference='为衔接现有水道、桥东端与观前台地补建局部溪岸、桥头及沿溪石路；其坐标与支承截面为项目设计。')
    for z in range(-90,-28):
        cx=127+round(42*((z+117)/99)**2)
        width=9+round(13*math.exp(-((z+47)/16)**2))
        for y in range(135,161):
            t=(y-135)/25
            left=cx-16+round(22*t)
            right=cx+6+round(width*(.4+.6*t))
            p.box((left,y,z),(right,y,z),MOSS if y==160 else ROCK)
        p.box((cx+9,160,z),(cx+15,160,z),PAVING)
    return model(p,['桥东端补接岸岩台，沿溪石路接回上游台地；两端各补三格踏步。'],['R2G15'],{})


def bamboo():
    p=Part('trees','山径竹丛与苔石踏步',inference='分节细竹、偏侧叶簇及苔石踏步来自R2G08；竹丛坐标沿现有上山路径补建。')
    for index,(a,b) in enumerate(zip(ROUTE[:-1],ROUTE[1:])):
        delta=(b-a)[[0,2]]
        across=np.array([-delta[1],delta[0]])/np.linalg.norm(delta)
        for j in range(4):
            c=np.rint(a+(b-a)*(.22+j*.18)).astype(int)
            side=1 if index%2 else -1
            x,z=np.rint(c[[0,2]]+across*5*side).astype(int)
            p.box((x,c[1],z),(x,c[1],z),MOSS)
            h=17+(j*5+index*3)%13
            p.box((x,c[1]+1,z),(x,c[1]+h,z),GRASS)
            for y in range(c[1]+4,c[1]+h,5):
                p.points([(x,y,z)],MOSS)
            for k in range(3):
                y=c[1]+h-k*5
                d=1 if (j+k)%2 else -1
                for u in range(1,5):
                    p.points([(x+d*u,y+u//3,z),(x+d*u,y+u//3,z+1)],LEAF)
    return model(p,['细竹分节、斜展叶簇和石阶边缘苔色。'],['R2G08'],
        {'bamboo':dict(label='山径竹丛',center=[63,101,244],half=[37,47,44],direction=[.9,.4,1])})


def build():
    return [creek_bank(),bridge(),bamboo(),gate()]


def gate():
    p=Part('gallery','三开间太虚山门',inference='四柱三开间、高中檐低侧檐与檐下短椽取R2O11；山门尺寸、背面和庭院入口坐标为项目补建。')
    for x in (-33,-13,13,33):
        p.box((x-2,-12,-2),(x+2,3,2),ROCK_DARK)
        p.box((x-1,4,-1),(x+1,40 if abs(x)==13 else 31,1),WOOD)
        p.box((x-4,28,-2),(x+4,30,2),FRAME)
    p.box((-34,26,-1),(34,28,1),WOOD)
    p.box((-15,36,-2),(15,38,2),WOOD)
    _roof(p,(0,0),(20,9),38,7)
    for sign in (-1,1):
        _roof(p,(sign*29,0),(14,8),29,6)
    for x in range(-41,42,3):
        p.box((x,27,-5),(x,28,5),WOOD)
    for x in range(-18,19,3):
        p.box((x,36,-7),(x,37,7),WOOD)
    for x0,x1,y in [(-8,8,45),(-34,-24,35),(24,34,35)]:
        p.box((x0,y,0),(x1,y+1,0),FRAME)
    end=ROUTE[0]
    forward=(ROUTE[0]-ROUTE[1])[[0,2]]
    forward/=np.linalg.norm(forward)
    across=np.array([forward[1],-forward[0]])
    p.chunks=[np.rint(np.c_[end[0]+a[:,0]*across[0]+a[:,2]*forward[0],a[:,1]+end[1],end[2]+a[:,0]*across[1]+a[:,2]*forward[1]]).astype(np.int32) for a in p.chunks]
    return model(p,['三开间四柱山门，高中央屋檐、低侧檐、横枋和密排短椽。'],['R2O11'],
        {'gate_detail':dict(label='三间山门',center=[74,181,145],half=[47,30,27],direction=[.8,.35,1])})
