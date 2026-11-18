import numpy as np

from taixuan_common_20261116 import Part, model, WATER
from taixuan_water_r6_20261117 import Creek as PreviousCreek


class Creek(PreviousCreek):
    def __init__(self,peak):
        super().__init__(peak)
        self.end=-68

    def carve(self,part):
        x,y,z=part.p.T
        distance,height,width=self.field(x,z)
        channel=(distance<=width+1)&(z<=self.end)&(y>=height-1)&(y<=height+12)
        bend=self.x+np.rint(1.3*np.sin(y*.047)).astype(int)
        chute=(abs(x-bend)<=6)&(z>=self.z-2)&(y>=166)&(y<=274)
        inlet=(x>=152)&(x<=164)&(z>=-74)&(z<=-63)&(y>=153)&(y<=166)
        tunnel=(x>=158)&(x<=174)&(z>=-73)&(z<=-63)&(y>=153)&(y<=157)
        outlet=(x>=172)&(x<=194)&(z>=-74)&(z<=-62)&(y>=34)&(y<=156)
        keep=~(channel|chute|inlet|tunnel|outlet)
        part.p,part.states=part.p[keep],part.states[keep]
        return part

    def water(self):
        p=Part('waterfall','拐点短跌与集中窄瀑')
        for y in range(166,271):
            cx=self.x+round(1.3*np.sin(y*.047))
            width=4+round(1.1*np.sin(y*.12)**2)
            p.box((cx-width,y,self.z),(cx+width,y,self.z+2),WATER)
        z,x=np.mgrid[self.z-1:self.end+1,137:221]
        distance,height,width=self.field(x,z)
        mask=distance<=width
        for depth in (0,-1):
            p.points(np.c_[x[mask],height[mask]+depth,z[mask]],WATER)
        p.box((153,155,-69),(163,161,-67),WATER)
        p.box((158,154,-73),(173,155,-63),WATER)
        for y in range(34,156):
            half=min(5,max(1,(y-34)//4))
            p.box((172,y,-68-half),(173,y,-68+half),WATER)
        return model(p,['水流在开始兜回的拐点短跌，穿过岩岸下方后集中垂入云海。',
            '外围岩路保留连续覆顶，局部窄瀑宽11格，取消下游回弯及T7整片水帘。'],
            ['G06','O06','O11','O15'],
            {'fall':dict(label='拐点窄瀑与完整岩岸',center=[173,148,-85],half=[45,119,91],direction=[1,.4,.8])})

    def parameters(self):
        return dict(bend=[158,161,-68],tunnel=dict(x=[158,174],y=[153,157],z=[-73,-63]),
            waterfall=dict(x=[172,173],z=[-73,-63],y=[34,155]),
            preserved_bank_roof_y=158,removed_outlet=[204,149,-8],
            purple_marking='外围动线，恢复岩石；不作为跌瀑边。')
