import numpy as np

import taixuan_ground_r6_20261117 as base
from taixuan_water_r8_20261117 import Creek
from taixuan_common_20261116 import ROCK, ROCK_DARK, MOSS


landscape=base.landscape
previous=base.previous
PEAKS=base.PEAKS
ROUTE=base.ROUTE
water_parameters={}
original_island=base.island


class Watercourse(Creek):
    def __init__(self,peak):
        super().__init__(peak)
        water_parameters.update(self.parameters())


def island(source,courtyard,creek):
    part=original_island(source,courtyard,creek)
    z,x=np.mgrid[-67:15,140:220]
    distance,height,width=creek.field(x,z)
    mask=distance<=width+1
    chunks=[part.p];states=[part.states]
    for offset in (0,1,2):
        y=height[mask]+offset
        chunks.append(np.c_[x[mask],y,z[mask]].astype(np.int32))
        states.append(np.where((offset==2)&(y>=149),MOSS,
            np.where((x[mask]+z[mask])%7==0,ROCK_DARK,ROCK)).astype(np.uint8))
    part.p=np.concatenate(chunks);part.states=np.concatenate(states)
    part.metadata['features']=['恢复T6外围岩岸和连续岩路，旧下游河床补回草岩。',
        '拐点下方接局部窄瀑，岩岸顶面保留，T7大范围削岸退出。']
    return part


def build():
    base.Creek=Watercourse
    base.island=island
    return base.build()
