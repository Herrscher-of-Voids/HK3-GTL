"""贴图评审84：改善约束、岩、空核心的小尺寸辨识度。

【变更记录 #1】2026-09-27 01:34:04（候选修改）
删除：无。新增：三套明暗色阶、核心内部纹路和小尺寸并排对照。
修改：只更新候选；保留理核心金环与原轮廓，约束金链使用透明空位。
用途：让负责人判断16像素下的辨识度；记录探测器A已选，未应用正式资源。
"""
from datetime import datetime
import json
from PIL import Image, ImageDraw, ImageFont
import preview_art81 as a
import preview_art82 as b

OUT=a.ROOT/'logs/art-review84'

def main():
    before={str(p.relative_to(a.ROOT)):a.sha(p.read_bytes()) for p in (a.ROOT/'src').rglob('*') if p.is_file()}
    (OUT/'candidates').mkdir(parents=True,exist_ok=True)
    src=Image.open(a.TEX/'imitation_reason_core.png').convert('RGBA')
    _,checks=b.core(0.1);mask={tuple(p) for p in checks['mask']}
    colors=sorted({src.getpixel(xy) for xy in mask},key=lambda p:sum(p[:3]))
    configs=[
        ('binding','约束：亮金＋链环',['#514511','#998019','#d8b52f','#f3d64b','#ffe875','#fff1a2','#fff9cd'],'亮金晶体，金链形成侧边轮廓；区别于赭褐与深橙。'),
        ('rock','岩：深赭＋矿物分层',['#271c16','#493020','#775032','#98683d','#b3864e','#d0ac70','#e6cd95'],'深赭褐主体，横向矿物分层与少量赭金高光。'),
        ('void','空：橙琥珀＋暗色裂隙',['#401606','#883004','#c14b04','#e97708','#ffa725','#ffc653','#ffdfa0'],'饱和橙琥珀，纵向暗色裂隙与明亮晶面。')]
    entries=[]
    for key,title,palette,note in configs:
        im=src.copy();lookup=dict(zip(colors,palette)); extra=[]
        for xy in mask:
            im.putpixel(xy,Image.new('RGBA',(1,1),lookup[src.getpixel(xy)]).getpixel((0,0)))
        def points(coords,color):
            for xy in coords:
                if xy in mask:im.putpixel(xy,Image.new('RGBA',(1,1),color).getpixel((0,0)))
        if key=='rock':
            points([(5,6),(6,6),(7,6),(8,6),(9,6),(6,9),(7,9),(8,9)],'#493020')
            points([(6,5),(7,5),(8,5),(7,8),(8,8),(9,8)],'#b3864e')
        if key=='void':
            points([(8,4),(8,5),(7,6),(7,7),(7,8),(8,9),(8,10)],'#632305')
            points([(9,4),(9,5),(8,6),(8,7),(8,8)],'#ffc653')
        if key=='binding':
            # 空心链环位于左右留白，不覆盖现有金环与晶体。
            for ox,oy in [(0,5),(0,8),(12,0),(12,3)]:
                for dx,dy in [(0,0),(1,0),(2,0),(0,1),(2,1),(0,2),(1,2),(2,2)]:
                    xy=(ox+dx,oy+dy)
                    if src.getpixel(xy)[3]==0:
                        im.putpixel(xy,Image.new('RGBA',(1,1),'#f9df69' if dy==0 else '#b18a28').getpixel((0,0)));extra.append(xy)
        assert all(im.getpixel((x,y))==src.getpixel((x,y)) for y in range(16) for x in range(16) if (x,y) not in mask and (x,y) not in extra)
        ident=f'imitation_{key}_core';dest=OUT/'candidates'/f'{ident}.png';im.save(dest)
        entries.append(dict(id=ident,title=title,note=note,candidate=str(dest),reference=str(a.ROOT/'logs/art-review83/candidates'/f'{ident}.png'),size=[16,16],sha256=a.sha(dest.read_bytes()),checks={'gold_frame_unchanged':True,'core_geometry_preserved':True,'added_chain_pixels':extra}))
    b.OUT=OUT;b.gallery(entries,'review-cores.png','贴图评审84 · 三种暖色核心的辨识度修改')
    font=lambda size:ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',size)
    sheet=Image.new('RGB',(720,300),'#18202c');d=ImageDraw.Draw(sheet)
    d.text((20,15),'同屏辨识：约束 / 岩 / 空（从左至右）',font=font(21),fill='white')
    for row,bg in enumerate(['#292d35','#c6c6c6']):
        y=65+row*115;d.rectangle((16,y,704,y+100),fill=bg)
        for col,size in enumerate([16,32,64]):
            x=45+col*225;d.text((x,y+7),f'{size}px',font=font(14),fill='#939393')
            for i,e in enumerate(entries):
                im=Image.open(e['candidate']).resize((size,size),Image.Resampling.NEAREST)
                sheet.paste(im,(x+i*(size+7),y+30),im)
    sheet.save(OUT/'recognition.png')
    after={str(p.relative_to(a.ROOT)):a.sha(p.read_bytes()) for p in (a.ROOT/'src').rglob('*') if p.is_file()};assert before==after
    report=dict(created_at=datetime.now().astimezone().isoformat(),status='候选未应用',entries=entries,source_tree_unchanged=True,selected_probe={'candidate':'logs/art-review83/candidates/unmanned_resource_probe_a.png','sha256':a.sha((a.ROOT/'logs/art-review83/candidates/unmanned_resource_probe_a.png').read_bytes()),'selection':'负责人已确认A：原图局部强化'})
    (OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'candidates':3,'source_tree_unchanged':True,'gold_frames_unchanged':True}))

if __name__=='__main__':main()
