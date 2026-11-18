from types import SimpleNamespace

import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.spatial import cKDTree

import taixuan_ground_r8_20261117 as previous_ground
from taixuan_water_r8_20261117 import Creek


base=previous_ground.base
landscape=base.landscape
previous=base.previous
PEAKS=base.PEAKS
ROUTE=base.ROUTE
water_parameters={}
COAST=np.array([[172,-68],[173,-55],[178,-35],[185,-15],[193,5],[199,20],[202,40]],float)
geometry_parameters=dict(coast_xz=COAST.tolist(),upper_outer_bank_width=8,
    scope='主岛东侧溪肩与岩岸，紫线只约束岩石轮廓。',water_baseline='T8')


class Watercourse(Creek):
    def __init__(self,peak):
        super().__init__(peak)
        water_parameters.update(self.parameters())
        end=np.argmin(np.linalg.norm(self.path-[158,-68],axis=1))+1
        self.bank_path=self.path[:end]
        self.bank_heights=self.heights[:end]
        self.bank_widths=self.widths[:end]
        self.bank_tree=cKDTree(self.bank_path)
        self.banks=SimpleNamespace(path=self.bank_path,field=self.bank_field)

    def bank_field(self,x,z):
        distance,index=self.bank_tree.query(np.c_[x.ravel(),z.ravel()])
        return (a.reshape(x.shape) for a in
            (distance,self.bank_heights[index],self.bank_widths[index]))


def island(source,courtyard,creek):
    part=previous_ground.original_island(source,courtyard,creek.banks)
    x,y,z=part.p.T
    coast=PchipInterpolator(COAST[:,1],COAST[:,0])
    lower=coast(np.clip(z,-68,40))
    row=np.argmin(abs(creek.bank_path[:,1,None]-np.arange(-151,-67)),axis=0)
    upper_x=creek.bank_path[row,0]+creek.bank_widths[row]+8
    upper=np.interp(z,np.arange(-151,-67),upper_x)
    outer=np.where(z<-68,upper,lower)
    flank=np.interp(y,[58,85,115,135,150,160,175],[-12,1,8,4,1,0,0])
    limit=outer+flank+np.sin(z*.12+y*.09)*.7
    zone=(z>=-151)&(z<=40)&(x>135)&(y>=58)
    keep=~zone|(x<=limit)
    part.p,part.states=part.p[keep],part.states[keep]
    part.metadata['features']=['溪谷沿紫线保留窄岩岸，旧回弯溪肩退出山体生成。',
        '拐点以下以连续弧形接回主岛，岩腹随高度渐收，保留T8岩路覆顶及集中窄瀑。']
    return part


def build():
    base.Creek=Watercourse
    base.island=island
    return base.build()
