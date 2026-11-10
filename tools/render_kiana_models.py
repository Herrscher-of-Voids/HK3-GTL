# -*- coding: utf-8 -*-
"""修订142：只读实际几何、标准皮肤UV的离线正交核对图，不模拟Minecraft光照。"""
from pathlib import Path
import json, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'deliveries/修订142_琪亚娜二审无武器'
data=json.loads((OUT/'kiana_review.json').read_text(encoding='utf-8'))
skin=Image.open(OUT/'kiana_review.png').convert('RGBA')
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',24)
small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',17)
def render(mode,az=.22,el=.1):
    faces=[]
    # 从正面负Z观察。模型Y向下，屏幕坐标也向下。
    view=np.array([[math.cos(az),0,math.sin(az)],[-math.sin(az)*math.sin(el),math.cos(el),math.cos(az)*math.sin(el)],[-math.sin(az)*math.cos(el),-math.sin(el),math.cos(az)*math.cos(el)]])
    def quad(verts,color,shade):
        v=np.array(verts)@view.T
        faces.append((v[:,2].mean(),v[:,:2],tuple(int(c*shade) for c in color[:3])))
    def cube(o,s,color,uv=None):
        x,y,z=o;w,h,d=s
        planes=[([(x+w,y,z),(x+w,y,z+d),(x+w,y+h,z+d),(x+w,y+h,z)],.78),
                ([(x,y,z+d),(x,y,z),(x,y+h,z),(x,y+h,z+d)],.83),
                ([(x,y,z+d),(x+w,y,z+d),(x+w,y,z),(x,y,z)],1),
                ([(x,y+h,z),(x+w,y+h,z),(x+w,y+h,z+d),(x,y+h,z+d)],.65),
                ([(x+w,y,z+d),(x,y,z+d),(x,y+h,z+d),(x+w,y+h,z+d)],.85),
                ([(x,y,z),(x+w,y,z),(x+w,y+h,z),(x,y+h,z)],.98)]
        for i,(verts,shade) in enumerate(planes):
            if uv is None:quad(verts,color,shade);continue
            u,v,a,b=uv[i];px=skin.crop((u*2,v*2,(u+a)*2,(v+b)*2));verts=np.array(verts)
            for py in range(b*2):
                for pxn in range(a*2):
                    c=px.getpixel((pxn,py))
                    if c[3]<15:continue
                    def at(xx,yy):return verts[0]+(verts[1]-verts[0])*xx/(a*2)+(verts[3]-verts[0])*yy/(b*2)
                    quad([at(pxn,py),at(pxn+1,py),at(pxn+1,py+1),at(pxn,py+1)],c,shade)
    for p in data['parts']:
        if mode!='all' and not (mode=='wings' and p['name'].startswith('wing')) and p['name']!=mode:continue
        offset={'body':[0,0,0],'right_arm':[-5,2.5,0],'left_arm':[5,2.5,0]}[p['attachment']]
        for c in p['cubes']:
            cube(np.array(c['origin'])+offset,c['size'],tuple(bytes.fromhex(c['color'])))
    if mode=='all':
        def body(o,s,u,v,infl=0):
            w,h,d=s;uv=[(u+d+w,v+d,d,h),(u,v+d,d,h),(u+d,v,w,d),(u+d+w,v,w,d),(u+2*d+w,v+d,w,h),(u+d,v+d,w,h)]
            cube(np.array(o)-infl,np.array(s)+2*infl,(255,255,255),uv)
        for o,s,u,v,layer in [([-4,-8,-4],[8,8,8],0,0,False),([-4,0,-2],[8,12,4],16,16,False),([-4,12,-2],[4,12,4],0,16,False),([0,12,-2],[4,12,4],16,48,False),([-7,.5,-2],[3,12,4],40,16,False),([4,.5,-2],[3,12,4],32,48,False),([-4,-8,-4],[8,8,8],32,0,True),([-4,0,-2],[8,12,4],16,32,True),([-4,12,-2],[4,12,4],0,32,True),([0,12,-2],[4,12,4],0,48,True),([-7,.5,-2],[3,12,4],40,32,True),([4,.5,-2],[3,12,4],48,48,True)]:
            body(o,s,u,v,.25 if layer else 0)
    points=np.concatenate([f[1] for f in faces]);lo=points.min(0);hi=points.max(0)
    scale=min(1000/(hi[0]-lo[0]),850/(hi[1]-lo[1]));center=(lo+hi)/2
    im=Image.new('RGB',(1200,1100),'#171b2b');draw=ImageDraw.Draw(im)
    for _,v,c in sorted(faces,key=lambda f:-f[0]):
        screen=(v-center)*scale+[600,570];draw.polygon([tuple(p) for p in screen],fill=c)
    title={'all':'琪亚娜 · 二审形象','wings':'双翼 · 三片分叉与星空内翼','gun':'枪 · 双孔枪口与镂空护圈','sword':'剑 · 长刃与分叉剑格'}[mode]
    draw.text((32,25),title,font=font,fill='#f0e6ff');draw.text((32,68),'游戏同源几何的离线正交图 · 并非游戏内截图',font=small,fill='#b8aecb')
    path=OUT/f'{mode}.png';im.save(path);print(path.name)
for mode,az in [('all',.2),('wings',.22)]:render(mode,az)
