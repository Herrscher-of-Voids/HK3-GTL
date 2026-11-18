import numpy as np
from scipy.interpolate import CubicSpline, PchipInterpolator
from scipy.spatial import cKDTree

from taixuan_common_20261116 import Part, model, WATER


class Creek:
    def __init__(self,peak):
        self.x=183
        face=peak.p[(abs(peak.p[:,0]-self.x)<=5)&(peak.p[:,1]==269)]
        self.z=int(face[:,2].max())+1
        points=np.array([[self.x,166,self.z+9],[165,164,-100],
            [158,161,-68],[177,156,-32],[204,149,-8]],float)
        t=np.r_[0,np.cumsum(np.linalg.norm(np.diff(points[:,[0,2]],axis=0),axis=1))]
        u=np.linspace(0,t[-1],900)
        self.path=CubicSpline(t,points[:,[0,2]],axis=0)(u)
        self.heights=np.rint(PchipInterpolator(t,points[:,1])(u)).astype(int)
        self.widths=5.5+1.1*np.sin(u*.075)+.5*np.cos(u*.19)+12*np.exp(-(u/17)**2)
        self.tree=cKDTree(self.path)

    def field(self,x,z):
        distance,index=self.tree.query(np.c_[x.ravel(),z.ravel()])
        return (a.reshape(x.shape) for a in (distance,self.heights[index],self.widths[index]))

    def carve(self,part):
        x,y,z=part.p.T
        distance,height,width=self.field(x,z)
        channel=(distance<=width+1)&(y>=height-1)&(y<=height+12)
        bend=self.x+np.rint(1.3*np.sin(y*.047)).astype(int)
        chute=(abs(x-bend)<=6)&(z>=self.z-2)&(y>=166)&(y<=274)
        outlet=(abs(x-204)<=6)&(z>=-10)&(z<=5+(149-y)*.07)&(y>=58)&(y<=153)
        keep=~(channel|chute|outlet)
        part.p,part.states=part.p[keep],part.states[keep]
        return part

    def water(self):
        p=Part('waterfall','山泉跌瀑、浅潭与弯溪')
        for y in range(166,271):
            cx=self.x+round(1.3*np.sin(y*.047))
            width=4+round(1.1*np.sin(y*.12)**2)
            p.box((cx-width,y,self.z),(cx+width,y,self.z+2),WATER)
        z,x=np.mgrid[self.z-1:20,137:221]
        distance,height,width=self.field(x,z)
        mask=distance<=width
        for depth in (0,-1):
            p.points(np.c_[x[mask],height[mask]+depth,z[mask]],WATER)
        for y in range(34,150):
            cx=204+round(.8*np.sin(y*.07))
            width=min(4,max(1,round((y-34)/6)))
            p.box((cx-width,y,-8),(cx+width,y,-6),WATER)
        return model(p,['上瀑落入山脚浅潭，沿弯曲溪谷逐级下降，再从岛边垂入云海。',
            '水道宽窄、岩肩与岸坡随曲线变化；水体沿用原浅蓝玻璃方块。'],
            ['G06','O06','O11','O15'],
            {'fall':dict(label='溪谷与双段瀑布',center=[182,185,-82],half=[57,104,99],direction=[1,.48,1])})
