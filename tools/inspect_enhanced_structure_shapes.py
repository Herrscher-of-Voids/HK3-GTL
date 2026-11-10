"""读取增强版真实布局制作正投影参考，不使用虚构纹理，不修改实例。
变更记录#1：实际时间记录到JSON；新增28项布局投影，删除无。
按StructureData.read字节码确认的z/y/x顺序读取；灰度表示投影深度，并非实际方块颜色。
"""
from pathlib import Path
import datetime,gzip,json,zipfile
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'logs/research-migration-20260928'

def main():
 info=json.loads((OUT/'enhanced-structure-reference-28.json').read_text(encoding='utf-8'))
 font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',17)
 small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',13)
 sheet=Image.new('RGB',(2000,7*340+95),(22,26,34));draw=ImageDraw.Draw(sheet)
 draw.text((20,12),'增强版28项替换结构 · 原始布局正投影',font=font,fill='white')
 draw.text((20,42),'仅用于轮廓与体量研究：左为俯视，右为沿z方向投影；灰度为深度，不是材质或游戏截图。各图独立缩放。',font=small,fill=(190,198,210))
 with zipfile.ZipFile(info['source']) as z:
  for i,row in enumerate(info['rows']):
   lines=gzip.decompress(z.read('data/gtl_enhancedcore/structures/gtl/'+row['id']+'.pattern.gz')).decode('ascii').splitlines()
   w,h,l=map(int,lines[0].split());assert len(lines)==1+h*l and all(len(s)==w for s in lines[1:])
   a=np.frombuffer(''.join(lines[1:]).encode('ascii'),dtype=np.uint8).reshape(l,h,w)
   occupied=(a!=32)
   # 最大y作为顶部；前视沿z取第一层。投影用于原始布局轴，不承诺游戏朝向。
   top=np.max(np.where(occupied,np.arange(h)[None,:,None]+1,0),axis=1)
   front=np.max(np.where(occupied,l-np.arange(l)[:,None,None],0),axis=0)[::-1]
   x=(i%4)*500;y=95+(i//4)*340
   draw.text((x+12,y+3),row['id'],font=small,fill='white')
   draw.text((x+12,y+25),f'{w} × {h} × {l} | {row["material_count"]}种绑定材料',font=small,fill=(180,190,205))
   for j,(view,extent) in enumerate([(top,h),(front,l)]):
    light=np.where(view>0,90+165*view/extent,25).astype(np.uint8)
    im=Image.fromarray(light).convert('RGB');im.thumbnail((232,258),Image.Resampling.NEAREST)
    sheet.paste(im,(x+10+j*245+(232-im.width)//2,y+60+(258-im.height)//2))
   draw.line((x+8,y+334,x+490,y+334),fill=(58,66,80))
 path=OUT/'enhanced-28-shape-projections.png';assert not path.exists();sheet.save(path)
 (OUT/'enhanced-shape-projection-validation.json').write_text(json.dumps({'time':datetime.datetime.now().astimezone().isoformat(),'structures':28,'layout_order':'z/y/x，经StructureData.read字节码核对','texture_rendered':False,'game_screenshot':False,'output':str(path),'instance_modified':False},ensure_ascii=False,indent=2),encoding='utf-8')
 print(path)
if __name__=='__main__':main()
