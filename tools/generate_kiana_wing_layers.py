# -*- coding: utf-8 -*-
"""修订143：将已确认翼形分为外框、星海、星点三张像素层；从142几何提取轮廓，不重画形状。
新增逐帧星云与错峰闪烁；输出原版item/generated模型和PNG动画，变更时间存入清单。
"""
# 变更记录 #2：2026-10-01 19:30:16（修订144），明确五层间距，星海半透明让中间星点可见。
# 变更记录 #3：2026-10-01 19:47:01（修订145），按新参考重新描录紧凑轮廓，增密星尘并收薄五层。
# 变更记录 #4：2026-10-15 02:01:30（修订157），删除：模型目录中的来源清单输出；新增：独立 provenance/entity 资源目录；修改：生成路径，避免 TextureScaler 将来源清单当作模型读取；用途：保留审计来源且不污染模型扫描输入。
from kiana_reference_shape import masks, bright_points
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageOps, ImageDraw, ImageFont
import json, math, random, shutil
ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'src/main/resources/assets/hk3gtl'
OUT=ROOT/'deliveries/修订145_琪亚娜参考轮廓重制'
SIZE=256

def galaxy_color(x,y,t):
    x,y=x/2,y/2
    ribbon=(math.sin(x*.09-y*.075-t)+1)/2
    cloud=(math.sin(x*.15+y*.10+t)*math.cos(y*.08-x*.11-t)+1)/2
    density=.58*ribbon+.42*cloud
    return (round(37+83*density),round(23+54*density),round(75+110*density))

def generate():
    OUT.mkdir(parents=True,exist_ok=True)
    frame,core=masks(SIZE)
    coords=[(x,y) for y in range(SIZE) for x in range(SIZE) if core.getpixel((x,y))]
    rng=random.Random(143);stars=[]
    for x,y in coords:
        if rng.random()<.06:stars.append((x,y,rng.random()*math.tau,rng.choice([1,1,2,3]),rng.uniform(.25,1)))
    points={(s[0],s[1]):s for s in stars}
    for index,(cx,cy) in enumerate(bright_points(SIZE)):
        for dx,dy,w in [(0,0,1),(-1,0,.85),(1,0,.85),(0,-1,.85),(0,1,.85),(-2,0,.35),(2,0,.35),(0,-2,.35),(0,2,.35)]:
            x,y=cx+dx,cy+dy
            if 0<=x<SIZE and 0<=y<SIZE and core.getpixel((x,y)):points[x,y]=(x,y,index*1.9,1,w)
    stars=list(points.values())
    galaxy=[];sparkles=[]
    for f in range(32):
        im=Image.new('RGBA',(SIZE,SIZE));t=math.tau*f/32
        for x,y in coords:
            im.putpixel((x,y),galaxy_color(x,y,t)+(112,))
        galaxy.append(im)
    for f in range(48):
        im=Image.new('RGBA',(SIZE,SIZE));t=math.tau*f/48
        for x,y,phase,speed,weight in stars:
            brightness=.04+.96*weight*((math.sin(t*speed+phase)+1)/2)**2
            # 暗相融回同一时刻星云底色，不能用不透明黑点遮住内翼。
            base=galaxy_color(x,y,t)
            im.putpixel((x,y),tuple(round(v+(target-v)*brightness) for v,target in zip(base,(245,240,255)))+(255,))
        sparkles.append(im)
    specs=[('frame1',[frame],1,.06,-.3),('galaxy1',galaxy,3,.04,-.15),('stars',sparkles,2,.04,0),('galaxy2',galaxy,3,.04,.15),('frame2',[frame],1,.06,.3)]
    manifest={'revision':145,'recorded':datetime.now().isoformat(timespec='seconds'),'source':'按用户桌面新参考手工描录：紧凑翼根、宽中翼、短下翼、局部白骨架；保留人物原皮肤','description':'两侧各五层item/generated；中心Z=-0.3/-0.15/0/0.15/0.3模型像素，厚度0.06/0.04/0.04/0.04/0.06；星海alpha112/255；星海32帧×3tick，星点48帧×2tick，均为4.8秒循环。星点alpha掩模固定，避免首帧挤出遗漏。','star_count_per_side':len(stars),'texture_size':SIZE,'layout':{'width':38.4,'center_x':21.2,'center_y':4.8,'root_x':2,'cell':38.4/SIZE},'layers':[],'change_record':'2026-10-15 02:01:30（Asia/Hong_Kong，修订157）：来源清单移出models目录，避免TextureScaler按模型扫描时将texture_size标量误作数组。'}
    for side in ['left','right']:
        for name,frames,ticks,depth,z in specs:
            basename=f'kiana_{side}_{name}'
            atlas=Image.new('RGBA',(SIZE,SIZE*len(frames)))
            for i,im in enumerate(frames):atlas.paste(im if side=='left' else ImageOps.mirror(im),(0,i*SIZE))
            texture=ASSETS/f'textures/item/wing/{basename}.png';atlas.save(texture)
            if len(frames)>1:
                (texture.with_suffix('.png.mcmeta')).write_text(json.dumps({'animation':{'width':SIZE,'height':SIZE,'frametime':ticks,'interpolate':True}},indent=2),encoding='utf-8')
                shutil.copy2(texture.with_suffix('.png.mcmeta'),OUT/(basename+'.png.mcmeta'))
            model=ASSETS/f'models/wing/{basename}.json'
            model.write_text(json.dumps({'_comment':manifest['recorded']+' 修订145：琪亚娜'+name+'像素层；ItemRenderer烘焙挤出，动画交由纹理图集。','parent':'item/generated','render_type':'minecraft:translucent' if name.startswith('galaxy') else 'minecraft:cutout','textures':{'layer0':f'hk3gtl:item/wing/{basename}'}},ensure_ascii=False,indent=2),encoding='utf-8')
            shutil.copy2(texture,OUT/texture.name);shutil.copy2(model,OUT/model.name)
            manifest['layers'].append(dict(side=side,name=name,texture=texture.name,frames=len(frames),ticks=ticks,depth=depth,z=z,translucent=name.startswith('galaxy')))
    (OUT/'layers.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    (ASSETS/'provenance/entity/kiana_review.provenance.json').parent.mkdir(parents=True,exist_ok=True)
    (ASSETS/'provenance/entity/kiana_review.provenance.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    shutil.copy2(ASSETS/'textures/entity/kiana_review.png',OUT/'kiana_review.png')
    # 同源帧预览，透明之外不产生可见矩形。
    font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',21)
    sheet=Image.new('RGB',(1600,600),'#171b2b');d=ImageDraw.Draw(sheet)
    for i,(name,ims,_,_,_) in enumerate(specs):
        sheet.paste(ims[0].resize((384,384),Image.Resampling.NEAREST),(i*320,110),ims[0].resize((384,384),Image.Resampling.NEAREST))
        d.text((i*320+25,35),['外框1','星海1 · 半透明','星点 · 中央','星海2 · 半透明','外框2'][i],font=font,fill='white')
    sheet.save(OUT/'五层拆分.png')
    animation=[]
    for tick in range(0,96,2):
        composite=frame.copy()
        for layer in [galaxy[(tick//3)%32],sparkles[(tick//2)%48],galaxy[(tick//3)%32],frame]: composite=Image.alpha_composite(composite,layer)
        canvas=Image.new('RGB',(600,600),'#171b2b');large=composite.crop(composite.getbbox());scale=min(550/large.width,480/large.height);large=large.resize((round(large.width*scale),round(large.height*scale)),Image.Resampling.NEAREST)
        canvas.paste(large,((600-large.width)//2,80),large);ImageDraw.Draw(canvas).text((20,15),'五层同源动画 · 单翼正面',font=font,fill='#f2eafa');animation.append(canvas)
    animation[0].save(OUT/'当前单翼.png')
    animation[0].save(OUT/'星海闪烁.gif',save_all=True,append_images=animation[1:],duration=100,loop=0)
    print(json.dumps({'layers':len(manifest['layers']),'stars_per_side':len(stars),'cycle_seconds':4.8},ensure_ascii=False))

if __name__=='__main__':generate()
