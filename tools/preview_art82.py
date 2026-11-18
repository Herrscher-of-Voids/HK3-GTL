"""贴图评审82：依据负责人反馈制作16像素重绘与原图局部换色候选。

【变更记录 #1】2026-09-27 01:18:51（候选评审，不增加模组修订号）
删除：无；保留评审81及正式资源。新增：16像素探测器、机器人群、对称晶格。
修改：世界泡恢复原图外壳；核心共用理核心底图，外侧碎片同步换色。
用途：仅写入 logs/art-review82，记录来源与像素核验，供负责人审阅。
"""
from pathlib import Path
from datetime import datetime
from collections import Counter
import colorsys
import json
from PIL import Image, ImageDraw, ImageFont
import preview_art81 as base

OUT = base.ROOT / 'logs/art-review82'
OLD = base.ROOT / 'logs/art-review81'
PAL = {'.':(0,0,0,0),'#':'#172331','s':'#526477','m':'#8b9ba5',
       'h':'#d8e1db','p':'#68418d','v':'#aa70d1','l':'#e6c9fa'}

def sprite(rows):
    assert len(rows)==16 and all(len(row)==16 for row in rows)
    im=Image.new('RGBA',(16,16))
    for y,row in enumerate(rows):
        for x,c in enumerate(row): im.putpixel((x,y),Image.new('RGBA',(1,1),PAL[c]).getpixel((0,0)))
    return im

def probe():
    # 十六像素内保留双翼、金属机身、扫描碟与紫色传感头。
    return sprite([
        '.........h......',
        '........hmh.....',
        '........sms.....',
        '.........s......',
        '.####...#h#.....',
        '.hpvp#.#hmms....',
        '.#vpvp#hmmss....',
        '..####hmmss#....',
        '.....#hvss####..',
        '.....#ms#pvpvh..',
        '......##.pvpv#..',
        '......s...####..',
        '.....mh.........',
        '....#vl#........',
        '.....##.........',
        '................'])

def swarm():
    # 两只分离的微型机器人，躯体、机械足、传感核心均落在整数像素。
    im=Image.new('RGBA',(16,16)); d=ImageDraw.Draw(im)
    for x,y in [(4,4),(11,11)]:
        for dx in [-1,1]:
            d.line([(x+dx,y-1),(x+dx*3,y-2),(x+dx*3,y-3)],fill=PAL['m'])
            d.line([(x+dx,y),(x+dx*3,y),(x+dx*3,y+1)],fill=PAL['s'])
            d.line([(x+dx,y+1),(x+dx*2,y+3)],fill=PAL['m'])
        d.rectangle((x-2,y-2,x+2,y+2),fill=PAL['#'])
        d.rectangle((x-1,y-1,x+1,y+1),fill=PAL['m'])
        d.line((x-1,y-2,x+1,y-2),fill=PAL['h'])
        d.point((x,y-1),fill=PAL['l']);d.point((x,y),fill=PAL['v'])
        d.line((x-1,y+2,x+1,y+2),fill=PAL['s'])
    return im

def lattice():
    return sprite([
        '................',
        '.......hh.......',
        '......mppm......',
        '....mm....mm....',
        '..mm...vv...mm..',
        '..m...vllv...m..',
        '..m..v.pp.v..m..',
        '..m.v.pllp.v.m..',
        '..m.v.pllp.v.m..',
        '..m..v.pp.v..m..',
        '..m...vllv...m..',
        '..mm...vv...mm..',
        '....mm....mm....',
        '......mppm......',
        '.......hh.......',
        '................'])

def bubble():
    src,_=base.original('sealed_real_world_bubble'); im=src.copy(); mask=[]
    for y in range(src.height):
        for x in range(src.width):
            r,g,b,a=src.getpixel((x,y))
            if a and ((r>g*1.2 and r>b*1.2) or (x,y)==(7,8)):
                mask.append((x,y)); im.putpixel((x,y),(8,9,18,a))
    for xy,color in { (6,6):(138,150,187), (9,7):(230,229,246),
                      (5,8):(252,247,228), (8,9):(145,154,192),
                      (7,11):(189,172,217)}.items():
        assert xy in mask
        im.putpixel(xy,color+(src.getpixel(xy)[3],))
    assert all(im.getpixel((x,y))==src.getpixel((x,y)) for y in range(16) for x in range(16) if (x,y) not in mask)
    return im,{'changed_region':'原红球及中心白色高光','outside_mask_unchanged':True,'size_unchanged':True,'mask':mask}

def core(hue):
    src=Image.open(base.TEX/'imitation_reason_core.png').convert('RGBA'); im=src.copy(); mask=[]
    for y in range(src.height):
        for x in range(src.width):
            r,g,b,a=src.getpixel((x,y)); h,s,v=colorsys.rgb_to_hsv(r/255,g/255,b/255)
            if a and b>r and .45<h<.75:
                im.putpixel((x,y),tuple(round(c*255) for c in colorsys.hsv_to_rgb(hue,s,v))+(a,));mask.append((x,y))
    assert all(im.getpixel((x,y))==src.getpixel((x,y)) for y in range(16) for x in range(16) if (x,y) not in mask)
    return im,{'gold_frame_unchanged':True,'outside_mask_unchanged':True,'alpha_equal':im.getchannel('A').tobytes()==src.getchannel('A').tobytes(),'mask':mask,'source_sha256':base.sha((base.TEX/'imitation_reason_core.png').read_bytes())}

def gallery(rows,name,title):
    f=lambda n:ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',n)
    page=Image.new('RGB',(1080,100+len(rows)*175),'#151d2a');d=ImageDraw.Draw(page)
    d.text((24,16),title,font=f(24),fill='#f2f3fa')
    d.text((24,55),'仅候选，未写入正式资源 · 新稿原生16×16 · 放大均用最近邻',font=f(16),fill='#b5c3d7')
    for i,e in enumerate(rows):
        y=95+i*175;d.rounded_rectangle((16,y,1064,y+165),radius=7,fill='#253245')
        d.text((28,y+12),e['title'],font=f(18),fill='white')
        for j in range(0,len(e['note']),24):d.text((28,y+48+j//24*23),e['note'][j:j+24],font=f(14),fill='#c0cce0')
        for x,key,label in [(480,'reference','上一稿／参照'),(680,'candidate','本次16×16候选')]:
            im=Image.open(e[key]).convert('RGBA'); im=im.crop((0,0,im.width,im.width)); pic=im.resize((112,112),Image.Resampling.NEAREST)
            page.paste(pic,(x,y+12),pic);d.text((x-4,y+132),label,font=f(14),fill='#e0e7f1')
        im=Image.open(e['candidate']).convert('RGBA')
        for x,size in [(902,16),(962,32)]:
            pic=im.resize((size,size),Image.Resampling.NEAREST);page.paste(pic,(x,y+55),pic);d.text((x-6,y+101),str(size)+'px',font=f(13),fill='#bccbdf')
    page.save(OUT/name)

def main():
    before={str(p.relative_to(base.ROOT)):base.sha(p.read_bytes()) for p in (base.ROOT/'src').rglob('*') if p.is_file()}
    (OUT/'candidates').mkdir(parents=True,exist_ok=True); entries=[]
    def add(ident,title,im,note,checks=None,reference=None):
        dest=OUT/'candidates'/f'{ident}.png';im.save(dest)
        ref=reference or OLD/'candidates'/f'{ident}.png'
        entries.append({'id':ident,'title':title,'note':note,'candidate':str(dest),'reference':str(ref),'size':list(im.size),'sha256':base.sha(dest.read_bytes()),'checks':checks or {}})
    add('unmanned_resource_probe','02 无人资源探测器',probe(),'双翼、金属机身、扫描碟和传感头；去掉高分辨率碎细节。')
    im,checks=bubble();add('sealed_real_world_bubble','03 世界泡容器',im,'恢复16像素原图外壳与比例，只将原红球改为黑底星点。',checks)
    im,checks=core(.065);add('imitation_flame_core','05 仿制炎之律者核心',im,'中间晶核及外侧两点一并改橙；金色圆环逐像素保持。',checks)
    add('nano_building_unit','10 纳米构建单元',swarm(),'两只可辨认的微型机器人组成一群；简化机械足与躯体。')
    im=lattice();assert im.tobytes()==im.transpose(Image.Transpose.FLIP_LEFT_RIGHT).tobytes()
    add('reconstruction_rule_carrier','11 重构规则载体',im,'对称外框、悬浮内核；左右像素完全镜像，无随机碎点。',{'horizontal_pixel_symmetry':True})
    gallery(entries,'review-changes.png','贴图评审82 · 五项针对性修改')
    core_names={'binding':'约束','corruption':'侵蚀','ice':'冰','void':'空','rock':'岩','thunder':'雷','wind':'风'}
    start=len(entries)
    for key,name in core_names.items():
        ident=f'imitation_{key}_core';src=Image.open(base.TEX/f'{ident}.png').convert('RGBA')
        color=Counter(p for p in src.getdata() if p[3] and p[:3]!=(218,171,68)).most_common(1)[0][0]
        hue=colorsys.rgb_to_hsv(*(c/255 for c in color[:3]))[0]
        im,checks=core(hue)
        add(ident,f'仿制{name}之律者核心',im,'统一理核心底图及金色圆环；暂沿用此物品现有主色，颜色待审阅。',checks,base.TEX/f'{ident}.png')
    gallery(entries[start:],'review-cores.png','贴图评审82 · 其余仿制核心共用底图')
    after={str(p.relative_to(base.ROOT)):base.sha(p.read_bytes()) for p in (base.ROOT/'src').rglob('*') if p.is_file()};assert before==after
    report={'created_at':datetime.now().astimezone().isoformat(),'status':'候选未应用','source_tree_unchanged':True,'entries':entries,'accepted_previous':['honkai_fuel_rod_casing','hyperion_thruster_assembly','soulium_swarf','conducting_composite','reconstructing_composite','cognitive_composite'],'retained_previous':'其余未点名条目保留评审81；约束材料与边角料A/B未擅自选择'}
    (OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'candidates':len(entries),'source_tree_unchanged':True,'pixel_symmetry':True}))

if __name__=='__main__':main()
