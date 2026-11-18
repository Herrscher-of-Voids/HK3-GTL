import numpy as np
from scipy.interpolate import CubicSpline, PchipInterpolator
from scipy.spatial import cKDTree

from taixuan_common_20261116 import Part, model, WATER
from taixuan_water_r6_20261117 import Creek as PreviousCreek


class Creek(PreviousCreek):
    def __init__(self,peak):
        super().__init__(peak)
        self.end=-68
        self.points=np.array([[self.x,166,self.z+9],[165,164,-100],[158,161,self.end]],float)
        t=np.r_[0,np.cumsum(np.linalg.norm(np.diff(self.points[:,[0,2]],axis=0),axis=1))]
        u=np.linspace(0,t[-1],600)
        self.path=CubicSpline(t,self.points[:,[0,2]],axis=0)(u)
        self.heights=np.rint(PchipInterpolator(t,self.points[:,1])(u)).astype(int)
        self.widths=5.5+1.1*np.sin(u*.075)+.5*np.cos(u*.19)+12*np.exp(-(u/17)**2)
        self.tree=cKDTree(self.path)
        self.grid_z,self.grid_x=np.mgrid[self.z-1:self.end+1,137:221]
        distance,self.grid_h,width=self.field(self.grid_x,self.grid_z)
        self.surface=distance<=width
        edge=np.where(self.surface,self.grid_x,-1000).max(1)
        rows=np.arange(len(edge))
        flowing=self.grid_z[:,0]>=self.z+10
        self.lip_z=self.grid_z[flowing,0]
        self.lip_x=edge[flowing]
        self.lip_h=self.grid_h[rows[flowing],self.lip_x-137]

    def field(self,x,z):
        distance,height,width=super().field(x,z)
        return np.where(z<=self.end,distance,1000),height,width

    def carve(self,part):
        x,y,z=part.p.T
        distance,height,width=self.field(x,z)
        channel=(distance<=width+1)&(y>=height-1)&(y<=height+12)
        bend=self.x+np.rint(1.3*np.sin(y*.047)).astype(int)
        chute=(abs(x-bend)<=6)&(z>=self.z-2)&(y>=166)&(y<=274)
        lip=np.interp(z,self.lip_z,self.lip_x)
        level=np.interp(z,self.lip_z,self.lip_h)
        spill=(z>=self.lip_z[0])&(z<=self.lip_z[-1])&(x>=lip-1)&(x<=275)&(y>=34)&(y<=level+12)
        keep=~(channel|chute|spill)
        part.p,part.states=part.p[keep],part.states[keep]
        return part

    def water(self):
        p=Part('waterfall','紫线外沿直落水帘')
        for y in range(166,271):
            cx=self.x+round(1.3*np.sin(y*.047))
            width=4+round(1.1*np.sin(y*.12)**2)
            p.box((cx-width,y,self.z),(cx+width,y,self.z+2),WATER)
        for depth in (0,-1):
            p.points(np.c_[self.grid_x[self.surface],self.grid_h[self.surface]+depth,
                self.grid_z[self.surface]],WATER)
        for y in range(34,167):
            flowing=(self.lip_h>=y)&(y>=34+np.rint(2*np.sin(self.lip_z*.27)**2))
            for thickness in (0,1):
                p.points(np.c_[self.lip_x[flowing]+thickness,
                    np.full(flowing.sum(),y),self.lip_z[flowing]],WATER)
        return model(p,['上瀑落入浅潭，贴山短溪沿紫线外岸直接垂入云海。',
            '外岸打开为两格厚弧形水帘，取消下游回弯与原单口下瀑；水色沿用T6。'],
            ['G06','O06','O11','O15'],
            {'fall':dict(label='外沿直落水帘',center=[181,168,-119],half=[50,115,69],direction=[1,.48,1])})

    def parameters(self):
        return dict(upstream_chute=[self.x,self.z],short_creek_points=self.points.tolist(),
            spill_edge=dict(start=[int(self.lip_x[0]),int(self.lip_h[0]),int(self.lip_z[0])],
                end=[int(self.lip_x[-1]),int(self.lip_h[-1]),int(self.lip_z[-1])],
                thickness=2,bottom_y=34),removed_outlet=[204,149,-8])
