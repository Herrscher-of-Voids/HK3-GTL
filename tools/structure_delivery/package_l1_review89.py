# -*- coding: utf-8 -*-
"""候选89离线交付：逐格JSON→技能NBT→Sponge回读，复用完整方块材质。
变更记录 #1：新增五机候选打包及真实贴图的等轴缩略图；非浏览器截图、非游戏验收。
变更记录 #2（2026-09-27）：修正前左上方视角的投影符号，使朝北、朝西和顶面与深度顺序一致；不修改逐格建筑。
变更记录 #3（2026-09-27 03:37:51）：增加独立候选目录和标题参数，接口调整版不覆盖旧预览。
只写独立评审目录和logs/revision89；不部署、不替换正式结构。
"""
from pathlib import Path
from collections import Counter
from datetime import datetime
import os,sys,json,io,base64,subprocess,hashlib,math
import nbtlib
from PIL import Image,ImageDraw,ImageFont,ImageEnhance
import package_i03_review as sponge

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'doc/HK3GTL-内测5/03_机器结构/L1五机重设计_候选89'
SKILL=Path.home()/'.codex/skills/minecraft-builder-skill'
MATS={m['state']:m for m in json.loads((ROOT/'logs/revision89/expanded-materials.json').read_text(encoding='utf-8'))}
# 钻石标记沿用此前已解析的原版完整方块材质。
MATS.update({m['state']:m for m in json.loads((ROOT/'logs/revision89/candidate-materials.json').read_text(encoding='utf-8')) if m['state'].startswith('minecraft:')})


def render_iso(data,materials,out):
    """固定相机的真实方块纹理仿射投影；不模拟MC光照、动态动画或材质染色。"""
    occupied={tuple(b['pos']):b['state'] for b in data['blocks']}
    transparent={m['state'] for m in materials if m['transparent']}
    # 选定比例让每一个像素方块都可读，最终缩小仅用于画廊缩略图。
    scale=16;sy=8;sz=16
    def projection(x,y,z):return ((x-z)*scale,-(x+z)*sy-y*sz)
    corners=[projection(x,y,z) for x in (0,data['size'][0]) for y in (0,data['size'][1]) for z in (0,data['size'][2])]
    lo=[min(p[i] for p in corners) for i in (0,1)];hi=[max(p[i] for p in corners) for i in (0,1)]
    image=Image.new('RGBA',(int(hi[0]-lo[0])+120,int(hi[1]-lo[1])+100),(19,26,40,255))
    # 各面的三个顶点分别对应原贴图左上、右上、左下。
    # Match the cube model UV directions: north runs -X, west runs +Z,
    # and the top texture's upper edge faces -Z.
    vertices={'north':[(1,1,0),(0,1,0),(1,0,0)],'west':[(0,1,0),(0,1,1),(0,0,0)],'up':[(0,1,0),(1,1,0),(0,1,1)]}
    patches={}
    for m in materials:
        for face,points in vertices.items():
            tex=Image.open(io.BytesIO(base64.b64decode(m['faces'][face].split(',')[1]))).convert('RGBA')
            tex=ImageEnhance.Brightness(tex).enhance({'north':.9,'west':.67,'up':1.12}[face])
            a,b,c=[projection(*p) for p in points];four=(b[0]+c[0]-a[0],b[1]+c[1]-a[1])
            x0=min(a[0],b[0],c[0],four[0]);y0=min(a[1],b[1],c[1],four[1]);x1=max(a[0],b[0],c[0],four[0]);y1=max(a[1],b[1],c[1],four[1])
            ax,ay=a[0]-x0,a[1]-y0;ux,uy=b[0]-a[0],b[1]-a[1];vx,vy=c[0]-a[0],c[1]-a[1]
            det=ux*vy-uy*vx;w,h=tex.size
            coeff=(w*vy/det,-w*vx/det,w*(-vy*ax+vx*ay)/det,-h*uy/det,h*ux/det,h*(uy*ax-ux*ay)/det)
            patch=tex.transform((int(x1-x0)+1,int(y1-y0)+1),Image.Transform.AFFINE,coeff,Image.Resampling.NEAREST)
            # 仿射矩形以外透明，不让贴图扩展重复盖住其他面。
            mask=Image.new('L',patch.size,0);ImageDraw.Draw(mask).polygon([(p[0]-x0,p[1]-y0) for p in [a,b,four,c]],fill=255)
            from PIL import ImageChops
            patch.putalpha(ImageChops.multiply(patch.getchannel('A'),mask));patches[m['state'],face]=(patch,x0,y0)
    visible={'north':(0,0,-1),'west':(-1,0,0),'up':(0,1,0)}
    for p,state in sorted(occupied.items(),key=lambda e:e[0][0]+e[0][2]-e[0][1]*1.3,reverse=True):
        base=projection(*p)
        for face,delta in visible.items():
            other=occupied.get(tuple(p[i]+delta[i] for i in range(3)))
            if other is not None and (other not in transparent or other==state):continue
            patch,x,y=patches[state,face]
            image.alpha_composite(patch,(round(base[0]-lo[0]+60+x),round(base[1]-lo[1]+50+y)))
    image.convert('RGB').save(out/'等轴预览.png')
    return image.convert('RGB')


def main(log_dir=None, title='五机候选89'):
    manifest=[];images=[]
    for key in ['i01','i02','i03','i04','i05']:
        out=OUT/key;data=json.loads((out/'blueprint.json').read_text(encoding='utf-8'))
        states=sorted({b['state'] for b in data['blocks']});materials=[MATS[s] for s in states]
        assert all(m['complete_cube'] for m in materials)
        env={**os.environ,'HK3_REVIEW_BLUEPRINT':str(out/'blueprint.json')}
        subprocess.run(['node',str(SKILL/'scripts/run-build.mjs'),str(ROOT/'tools/structure_delivery/l1-review89-recipe.mjs'),
            '--out-dir',str(out),'--name',data['name'],'--no-block-state-updates','--json'],cwd=SKILL,env=env,check=True,capture_output=True)
        sponge.OUT=out;sponge.NAME=data['name'];schem,_,_=sponge.write_sponge(data)
        nbt=nbtlib.load(out/(data['name']+'.nbt'))
        decoded={tuple(map(int,b['pos'])):str(nbt['palette'][int(b['state'])]['Name'])+('['+','.join(f'{k}={v}' for k,v in nbt['palette'][int(b['state'])].get('Properties',{}).items())+']' if nbt['palette'][int(b['state'])].get('Properties') else '') for b in nbt['blocks']}
        assert decoded=={tuple(b['pos']):b['state'] for b in data['blocks']}
        audit=json.loads((out/'geometry-audit.json').read_text(encoding='utf-8'))
        audit.update(sha256=hashlib.sha256(schem.read_bytes()).hexdigest(),checks=['逐格JSON、NBT与Sponge回读一致','全部材料使用完整立方体模型','实体六邻接连通','主通道净空与全部接口步行可达'],not_verified=['尚未接入正式Pattern，未做游戏成型','三维采用材质首帧，未模拟游戏全部光照与动态染色'])
        for file,value in [('materials.json',materials),('audit.json',audit)]:
            (out/file).write_text(json.dumps(value,ensure_ascii=False),encoding='utf-8')
        images.append(render_iso(data,materials,out));manifest.append({'key':key,'title':data['title'],'name':data['name'],'size':data['size'],'blocks':len(data['blocks']),'materials':len(states),'namespaces':dict(Counter(b['state'].split(':')[0] for b in data['blocks'])),'description':data['description'],'sha256':audit['sha256']})
        print(key,len(data['blocks']),len(states),'种方块状态，预览与结构同源',flush=True)
    # 总览为同一逐格数据的材质等轴投影，明确区别于三维页面截图。
    width=1920;cellw=640;cellh=700;overview=Image.new('RGB',(width,2*cellh+170),(12,18,29));draw=ImageDraw.Draw(overview)
    font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',26);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)
    draw.text((32,22),'L1 · GT工业 × 崩坏科技  /  '+title,font=font,fill='#e5edf7')
    draw.text((32,67),'真实方块坐标与本地材质的等轴预览；非游戏截图，正式结构未替换。',font=small,fill='#9eafc9')
    for i,(entry,picture) in enumerate(zip(manifest,images)):
        x=(i%3)*cellw;y=(i//3)*cellh+110
        thumb=picture.copy();thumb.thumbnail((cellw-20,cellh-115),Image.Resampling.LANCZOS)
        overview.paste(thumb,(x+(cellw-thumb.width)//2,y+(cellh-115-thumb.height)//2))
        draw.text((x+20,y+cellh-97),entry['title'],font=small,fill='#dbeef1')
        draw.text((x+20,y+cellh-62),' × '.join(map(str,entry['size']))+f"  |  {entry['blocks']} 方块 · {entry['materials']} 种状态",font=small,fill='#9eafc9')
    draw.text((1300,910),'三维评审操作',font=font,fill='#89e5da')
    for j,t in enumerate(['分别进入 I01–I05 页面','鼠标旋转、平移与缩放','逐层剖开、隐藏玻璃','显示接口编号与检修通道','支持单独隐藏某种材料']):draw.text((1300,970+j*46),t,font=small,fill='#c6d3e7')
    overview.save(OUT/'五机总览.png')
    (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    (Path(log_dir or ROOT/'logs/revision89')/'preview-package.json').write_text(json.dumps({'time':datetime.now().isoformat(),'candidate_only':True,'formal_resources_changed':False,'game_instance_changed':False,'machines':manifest},ensure_ascii=False,indent=2),encoding='utf-8')


if __name__=='__main__':main()
