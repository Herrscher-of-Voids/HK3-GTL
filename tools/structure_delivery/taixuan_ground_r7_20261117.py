import taixuan_ground_r6_20261117 as base
from taixuan_water_r7_20261117 import Creek


landscape=base.landscape
previous=base.previous
PEAKS=base.PEAKS
ROUTE=base.ROUTE
water_parameters={}


class Watercourse(Creek):
    def __init__(self,peak):
        super().__init__(peak)
        water_parameters.update(self.parameters())


def build():
    base.Creek=Watercourse
    parts=base.build()
    parts[0].metadata['features']=['草岩主岛承托完整院坪，东侧岩床接山脚浅潭与贴山短溪。',
        '紫线外岸直接断落为水帘，原下游回弯恢复草岩岸坡。']
    return parts
