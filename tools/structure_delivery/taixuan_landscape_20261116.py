import math

import numpy as np

from taixuan_common_20261116 import *

ROUTE=np.array([[74,159,145],[82,153,169],[-47,119,207],[76,88,244],[47,58,284]],float)


def mountain(name, label, center, sections, seed, refs):
    part = Part(name, label)
    cx, cz = center
    outline=np.array([[1,0],[.91,.43],[.49,.68],[.21,1],[-.4,.87],[-.91,.4],
        [-1,-.17],[-.63,-.36],[-.82,-.86],[-.06,-1],[.62,-.81],[.57,-.31]])
    angle=seed*math.pi/7
    outline=outline@np.array([[math.cos(angle),-math.sin(angle)],[math.sin(angle),math.cos(angle)]])
    for a, b in zip(sections[:-1], sections[1:]):
        for y in range(a[0], b[0]):
            t = (y - a[0]) / (b[0] - a[0])
            rx, rz, dx, dz = np.array(a[1:]) * (1 - t) + np.array(b[1:]) * t
            ledge = 1 + .012 * math.sin((y // 18) * 2.2 + seed)
            vx = cx + dx + outline[:,0] * rx * ledge
            vz = cz + dz + outline[:,1] * rz * ledge
            z, x = np.mgrid[math.floor(vz.min()):math.ceil(vz.max())+1,
                math.floor(vx.min()):math.ceil(vx.max())+1]
            mask = np.zeros(x.shape, bool)
            for i in range(12):
                j = (i + 1) % 12
                mask ^= ((vz[i] > z) != (vz[j] > z)) & (x < (vx[j]-vx[i]) * (z-vz[i]) / (vz[j]-vz[i]) + vx[i])
            xx, zz = x[mask], z[mask]
            cap=sections[-1][0]-1-np.floor((xx-cx+rx)*.10+(zz-cz+rz)*.045).astype(int)
            keep=y<=cap
            if name=='path_rock':
                for start,end in zip(ROUTE[:-1],ROUTE[1:]):
                    delta=end[[0,2]]-start[[0,2]]
                    t=np.clip(((xx-start[0])*delta[0]+(zz-start[2])*delta[1])/(delta@delta),0,1)
                    distance=(xx-start[0]-t*delta[0])**2+(zz-start[2]-t*delta[1])**2
                    keep &= (distance>9**2)|(y<=np.rint(start[1]+(end[1]-start[1])*t)-4)
            if name=='east_peak' and 160<=y<=280:
                keep &= (xx<121)|(xx>133)|(zz<-117)
            xx,zz,cap=xx[keep],zz[keep],cap[keep]
            points = np.c_[xx, np.full(xx.size, y), zz]
            seams = ((xx + (zz // 28) * 7) // 29 + zz // 34 + y // 37 + seed) % 11
            states = np.full(len(points), ROCK, np.uint8)
            states[seams < 3] = ROCK_DARK
            states[seams == 7] = ROCK_PALE
            states[y>=cap-2] = MOSS
            part.chunks.append(points.astype(np.int32))
            part.values.append(states)
    return model(part, [label + '采用手定多边形截面、错层岩台与薄草顶。',
        '岩层和草皮依据可见机位；整座山峰的背面、海拔与相互坐标为复刻推断。'], refs, {})


def terrain():
    specs = [
        ('terrace', '观前主台地', (0, 0), [(25,32,41,-12,4),(58,87,103,8,0),
            (108,151,151,0,-5),(154,160,159,0,-5),(161,151,151,0,-5)], 2),
        ('west_peak', '西侧分节青岩峰', (-190,-160), [(8,16,21,4,0),(80,44,51,0,0),
            (142,55,58,-4,-6),(150,63,63,-4,-6),(249,60,58,1,-8),
            (258,49,54,4,-11),(329,47,50,-1,-12)], 3),
        ('rear_peak', '背山高峰', (-47,-233), [(35,25,25,0,0),(154,57,60,0,2),
            (238,62,51,8,0),(246,49,40,8,0),(309,48,39,4,-3),
            (315,38,35,4,-7),(369,32,33,-2,-7)], 6),
        ('east_peak', '东侧瀑布峰', (158,-173), [(12,19,24,0,0),(110,51,59,0,0),
            (183,75,73,0,0),(247,75,65,-6,-2),(253,59,57,-8,-5),
            (292,57,54,-7,-5),(298,47,47,-1,-6),(335,45,43,1,-6)], 9),
        ('east_spire', '云海外侧石柱', (269,-48), [(23,12,14,0,0),(100,24,28,0,0),
            (170,43,41,6,-5),(239,42,39,3,-6),(246,30,28,3,-7),(304,28,27,-2,-7)], 1),
        ('west_spire', '西侧临云石柱', (-270,15), [(29,11,14,0,0),(112,26,31,-3,0),
            (182,39,35,0,-4),(229,36,33,5,-8),(235,28,27,5,-9),(266,27,25,2,-9)], 4),
        ('front_west', '左侧低草台', (-190,116), [(12,15,19,0,0),(63,35,37,0,0),
            (115,49,54,0,-2),(169,41,43,6,0),(185,31,34,2,-5)], 8),
        ('front_east', '右侧临崖草台', (188,121), [(19,12,15,0,0),(88,39,42,0,0),
            (134,48,45,5,-1),(196,42,35,0,0),(210,28,25,-6,-4)], 5),
        ('path_rock', '入山折径岩脊', (27,191), [(5,19,45,-10,0),(39,58,93,0,0),
            (76,82,96,0,-12),(112,86,79,-9,-15),(143,70,56,0,-25),(160,42,29,3,-44)], 7),
    ]
    return [mountain(n,l,c,s,seed,['G01','G05','G06','G08','G09','O15']) for n,l,c,s,seed in specs]


def courtyard():
    p = Part('courtyard', '石坪与八卦练武台')
    z,x = np.mgrid[-131:151,-131:132]
    court = (np.maximum(abs(x)-105,0)**2 + np.maximum(abs(z-7)-116,0)**2) < 26**2
    for y in range(157,161):
        p.points(np.c_[x[court],np.full(court.sum(),y),z[court]], PAVING)
    stone=((x/39)**2+((z-20)/40)**2<1)|((abs(x)<20)&(z<45))|((abs(x)<58)&(z>39))
    grass=court&~stone
    p.points(np.c_[x[grass],np.full(grass.sum(),160),z[grass]],MOSS)
    joints=court&stone&((x%15==0)|(z%15==0))
    p.points(np.c_[x[joints],np.full(joints.sum(),160),z[joints]],ROCK_PALE)
    for xx,zz in [(-78,47),(-79,26),(-68,8),(-57,-12),(51,-5),(73,17),(83,41),(94,63)]:
        p.box([xx-4,160,zz-3],[xx+4,160,zz+3],ROCK_PALE)
    z,x = np.mgrid[42:150,-54:55]
    dx,dz=x,z-96
    r = np.sqrt(dx*dx+dz*dz)
    base=(abs(dx)<=52)&(abs(dz)<=52)&(abs(dx)+abs(dz)<=73)
    p.points(np.c_[x[base],np.full(base.sum(),161),z[base]],ROCK_PALE)
    octagon=np.maximum(np.maximum(abs(dx),abs(dz)),(abs(dx)+abs(dz))/math.sqrt(2))
    for radius in [48,51]:
        line=abs(octagon-radius)<.65
        p.points(np.c_[x[line],np.full(line.sum(),162),z[line]],GOLD)
    a = r < 17
    yin = dx < 0
    yin[(dx*dx + (dz-8.5)**2)<8.5**2] = True
    yin[(dx*dx + (dz+8.5)**2)<8.5**2] = False
    yin[(dx*dx + (dz-8.5)**2)<2**2] = False
    yin[(dx*dx + (dz+8.5)**2)<2**2] = True
    for state, mask in [(TILE,a&yin),(PAVING,a&~yin)]:
        p.points(np.c_[x[mask],np.full(mask.sum(),162),z[mask]],state)
    for k in range(8):
        angle=k*math.pi/4
        for j in range(3):
            radial=33+j*4
            for tangent in range(-8,9):
                if (k >> j)&1 and abs(tangent)<2:
                    continue
                xx=round(radial*math.cos(angle)-tangent*math.sin(angle))
                zz=96+round(radial*math.sin(angle)+tangent*math.cos(angle))
                p.box([xx,162,zz],[xx+1,162,zz+1],GOLD)
    for x0,z0,r0 in [(-111,65,17),(109,78,13),(-82,132,9),(122,-24,9)]:
        z,x=np.mgrid[z0-r0:z0+r0+1,x0-r0:x0+r0+1]
        m=(x-x0)**2+(z-z0)**2<=r0*r0
        p.points(np.c_[x[m],np.full(m.sum(),161),z[m]],MOSS)
    return model(p,['草地石径、土金八卦外圈与灰褐阴阳鱼薄台。','练武台位置及场景比例按可见庭院关系推断。'],
        ['G10','G11','G14','O13'],{'bagua':dict(label='八卦练武台',center=[0,162,96],half=[57,8,57],direction=[0,1,.35])})


def paths():
    p=Part('mountain_path','回折山径与临崖石阶')
    for a,b in zip(ROUTE[:-1],ROUTE[1:]):
        steps=math.ceil(np.linalg.norm((b-a)[[0,2]]))
        direction=(b-a)[[0,2]]; direction/=np.linalg.norm(direction)
        across=np.array([-direction[1],direction[0]])
        for i in range(steps+1):
            c=np.rint(a+(b-a)*i/steps).astype(int)
            for t in range(-6,7):
                xx,zz=np.rint(c[[0,2]]+across*t).astype(int)
                p.box([xx,c[1]-3,zz],[xx+1,c[1],zz+1],ROCK_DARK if abs(t)==6 else PAVING)
            if i%10==0:
                for side in [-1,1]:
                    xx,zz=np.rint(c[[0,2]]+across*6*side).astype(int)
                    p.box([xx,c[1]+1,zz],[xx+1,c[1]+5,zz+1],ROCK_PALE)
            for side in [-1,1]:
                xx,zz=np.rint(c[[0,2]]+across*6*side).astype(int)
                p.box([xx,c[1]+4,zz],[xx+1,c[1]+4,zz+1],ROCK_PALE)
    return model(p,['曲折上山路径接入完整庭院，石阶逐层递升。','山径连接为场景复刻设计；岩缝与步道材质取游戏实景。'],
        ['G02','G07','G08','A01'],{'stairs':dict(label='上山石阶',center=[20,114,216],half=[90,60,80],direction=[-.6,.55,1])})


def foliage():
    p=Part('trees','古松、灌木与苔台')
    specs=[(-106,161,-36,37,3), (101,161,-38,43,6),(-117,161,96,27,7),
        (112,162,112,32,2),(-175,321,-169,29,1),(168,328,-177,24,4),
        (-187,181,112,28,5),(185,207,117,25,8),(-263,262,7,22,9)]
    for cx,y,cz,h,seed in specs:
        top=np.array([cx+int(7*math.sin(seed)),y+h,cz+4],float)
        bend=np.array([cx+math.sin(seed)*5,y+h*.5,cz-5])
        p.beam([cx,y,cz],bend,2.7,LOG)
        p.beam(bend,top,2.1,LOG)
        for j in range(5):
            angle=j*2.4+seed
            length=12+(j*7+seed)%15
            c=top+np.array([math.cos(angle)*length,-j*4,math.sin(angle)*length*.72])
            p.beam(bend,c,1.6,LOG)
            radii=np.array([9+(j+seed)%3*3,4+j%3,6+(j+seed)%4*2])
            lo=np.floor(c-radii).astype(int); hi=np.ceil(c+radii).astype(int)
            z,x=np.mgrid[lo[2]:hi[2]+1,lo[0]:hi[0]+1]
            for yy in range(lo[1],hi[1]+1):
                shape=((x-c[0])/radii[0])**2+((z-c[2])/radii[2])**2+((yy-c[1])/radii[1])**2
                mask=shape<1+.12*np.sin(x*.55+seed)*np.cos(z*.4)
                p.points(np.c_[x[mask],np.full(mask.sum(),yy),z[mask]],LEAF)
    for cx,cz in [(-122,-10),(-120,17),(119,-7),(99,129),(-81,132)]:
        for j in range(4):
            p.sphere([cx+j*3,163+j%2,cz+2*math.sin(j)],3,LEAF)
    return model(p,['依崖古松采用弯干、分枝与横展分簇树冠，庭院边缘补低灌木。'],
        ['G01','G06','O02','O03','O15'],{'pine':dict(label='古松方块近景',center=[101,184,-38],half=[40,36,39],direction=[-.5,.28,1])})


def waterfall():
    p=Part('waterfall','青岩双段瀑布')
    for z,low,high,cx,width in [(-117,161,280,127,9),(-18,51,161,169,7)]:
        for y in range(low,high+1):
            for x in range(cx-width//2,cx+width//2+1):
                p.box([x,y,z],[x,y,z+2],WATER)
    for z in range(-117,-16):
        t=(z+117)/99
        x=127+round(42*t*t)
        p.box([x-7,157,z],[x+7,159,z+1],ROCK)
        p.box([x-7,160,z],[x-6,161,z+1],MOSS)
        p.box([x+6,160,z],[x+7,161,z+1],MOSS)
        p.box([x-5,160,z],[x+5,161,z+1],WATER)
    return model(p,['青色瀑布从东侧高岩落到石坪边水道，再垂落云层。','水流以玻璃方块标出体积，波光为网页演示。'],
        ['G06','O06','O11','O15'],{'fall':dict(label='瀑布与岩台',center=[150,172,-68],half=[50,118,75],direction=[1,.2,1])})


def build():
    return terrain()+[courtyard(),paths(),foliage(),waterfall()]
