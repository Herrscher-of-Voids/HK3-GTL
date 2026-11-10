"""贴图评审81：从修订76基线制作原图换色、局部修改和独立像素候选。

变更记录 #1：2026-09-27 00:55:57。
新增：带来源哈希和像素约束核验的候选、中文对照图；删除：无。
修改：仅写入 logs/art-review81，不改正式资源、不调用旧版应用脚本。
用途：负责人逐图审阅；动画保留源元数据，未知电压只标候选。
"""
from pathlib import Path
from io import BytesIO
from datetime import datetime
import colorsys
import hashlib
import json
import math
import random
import zipfile
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'logs/art-review81'
TEX = ROOT / 'src/main/resources/assets/hk3gtl/textures/item'
MANIFEST = json.loads((ROOT/'logs/revision76/art-candidates/manifest.json').read_text('utf-8-sig'))
REFS = {e['id']: e for e in MANIFEST['previews']}
ENTRIES = []

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def original(ident):
    e = REFS[ident]
    if '!/' in e['source']:
        jar, member = e['source'].split('!/', 1)
        with zipfile.ZipFile(jar) as z:
            raw = z.read(member)
            meta = z.read(member+'.mcmeta') if member+'.mcmeta' in z.namelist() else None
    else:
        path = Path(e['source']); raw = path.read_bytes()
        meta = path.with_suffix('.png.mcmeta').read_bytes() if path.with_suffix('.png.mcmeta').exists() else None
    assert sha(raw) == e['source_sha256'], ident
    return Image.open(BytesIO(raw)).convert('RGBA'), meta

def recolor(im, color, darken=1):
    assert len(color) == 7 and color[0] == '#'
    h,s,_ = colorsys.rgb_to_hsv(*(int(color[i:i+2],16)/255 for i in (1,3,5)))
    out = im.copy()
    out.putdata([tuple(round(c*255) for c in colorsys.hsv_to_rgb(h,s,max(r,g,b)/255*darken))+(a,) if a else (r,g,b,a) for r,g,b,a in im.getdata()])
    assert out.getchannel('A').tobytes() == im.getchannel('A').tobytes()
    assert all(max(b[:3]) == round(max(a[:3])*darken) for a,b in zip(im.getdata(),out.getdata()) if a[3])
    return out

def add(ident, title, im, reference=None, note='', meta=None, checks=None):
    target = OUT/'candidates'/f'{ident}.png'; target.parent.mkdir(parents=True,exist_ok=True)
    im.save(target)
    if meta: target.with_suffix('.png.mcmeta').write_bytes(meta)
    if reference:
        (OUT/'references').mkdir(exist_ok=True)
        ref,_ = original(reference)
        ref.save(OUT/'references'/f'{ident}.png')
    elif (TEX/f'{ident}.png').exists():
        ref = Image.open(TEX/f'{ident}.png').convert('RGBA')
    else: ref = None
    ENTRIES.append({'id':ident,'title':title,'size':list(im.size),'note':note,'reference':reference,
                    'source':REFS[reference]['source'] if reference else '本次逐像素绘制／项目既有核心',
                    'source_sha256':REFS[reference]['source_sha256'] if reference else None,
                    'sha256':sha(target.read_bytes()),'checks':checks or {},'animation':bool(meta)})
    return ref

def line3(d, points, dark='#131b29', mid='#64788c', light='#c1d2d9', width=3):
    d.line(points,fill=dark,width=width+2)
    d.line(points,fill=mid,width=width)
    d.line([(x,y-1) for x,y in points],fill=light,width=1)

def probe():
    im=Image.new('RGBA',(64,64));d=ImageDraw.Draw(im)
    # 双翼分块阵列、隔热金属机身和大口径扫描碟，保留卫星探测器语义。
    line3(d,[(8,17),(52,46)])
    for ox,oy in [(3,9),(39,37)]:
        pts=[(ox,oy+6),(ox+9,oy),(ox+21,oy+8),(ox+12,oy+14)]
        d.polygon(pts,fill='#152131',outline='#a9b6bd')
        for j in range(3):
            for k in range(2):
                x=ox+3+j*4+k*3;y=oy+5+j*3-k*2
                d.polygon([(x,y),(x+3,y-2),(x+6,y),(x+3,y+2)],fill=['#4c3975','#795399','#ac82bb'][(j+k)%3])
        d.line([pts[0],pts[1],pts[2]],fill='#d3c4de')
    d.polygon([(22,25),(32,18),(44,29),(34,43),(22,42),(16,35)],fill='#182331',outline='#111620')
    d.polygon([(22,25),(32,20),(38,26),(26,36),(18,34)],fill='#c0c4bf')
    d.polygon([(26,36),(38,26),(43,30),(34,42),(26,42)],fill='#596875')
    d.polygon([(18,35),(26,37),(26,42),(22,40)],fill='#8b969e')
    d.line([(23,27),(30,23),(34,25)],fill='#f2ebe0',width=2)
    for i in range(3):d.line([(30+i*3,34+i),(34+i*3,29+i)],fill='#232e3d',width=1)
    d.rectangle((24,31,27,33),fill='#402257');d.point((25,31),fill='#e2abff')
    line3(d,[(34,22),(42,13)],width=2)
    d.polygon([(32,10),(37,5),(51,12),(48,20),(40,20)],fill='#273548',outline='#0c1422')
    d.polygon([(33,10),(38,7),(49,12),(47,17),(41,17)],fill='#bec8ce')
    d.polygon([(36,10),(39,9),(46,12),(44,15),(41,14)],fill='#6e7d8c')
    d.line([(41,12),(45,6)],fill='#1a2232',width=3);d.line([(41,12),(45,6)],fill='#d6c4e4')
    d.rectangle((44,4,46,6),fill='#a86ed4');d.point((44,4),fill='#f4c8ff')
    line3(d,[(22,40),(15,48),(10,48)],width=2)
    d.ellipse((7,45,13,51),fill='#21273a',outline='#aab7bf');d.ellipse((9,47,11,49),fill='#b67ef0')
    d.polygon([(29,44),(34,45),(31,51),(27,49)],fill='#282336',outline='#9399ac')
    d.line([(28,49),(31,50)],fill='#bc74e1')
    return im

def bubble(src):
    # 原图放大为整数像素后，仅沿水平方向扩宽容器，继续使用原金属端盖。
    im=Image.new('RGBA',(32,32));s=src.resize((32,32),Image.Resampling.NEAREST)
    for y in range(32):
        for x in range(2,29):
            sx=4+round((x-2)*21/26)
            im.putpixel((x,y),s.getpixel((sx,y)))
    d=ImageDraw.Draw(im)
    d.ellipse((6,10,25,28),fill='#141322',outline='#4f446c')
    d.ellipse((7,11,24,27),fill='#03050c')
    d.arc((7,11,24,27),195,285,fill='#595a8c',width=1)
    for x,y,c in [(10,15,'#777aaa'),(11,17,'#353359'),(12,19,'#494069'),(14,20,'#383158'),(16,21,'#2f2d4a'),(18,22,'#393856'),(20,23,'#292d46')]:d.point((x,y),fill=c)
    for x,y,c in [(10,14,'#f0efff'),(16,13,'#a8bce1'),(21,16,'#fff5df'),(13,17,'#b5a4d0'),(18,19,'#edeaff'),(9,21,'#999bd0'),(15,24,'#e5e9ff'),(21,23,'#c5b0e8'),(12,23,'#606c91'),(22,20,'#a0b3d8')]:d.point((x,y),fill=c)
    return im

def beaker():
    im=Image.new('RGBA',(32,32));d=ImageDraw.Draw(im)
    # 敞口直壁烧杯，有倾倒嘴、液面、刻度和玻璃反光，不使用瓶颈。
    d.polygon([(5,5),(24,5),(28,3),(26,9),(26,26),(23,29),(8,29),(5,26)],fill='#273443')
    d.polygon([(7,7),(24,7),(24,25),(22,27),(9,27),(7,25)],fill='#536675')
    d.rectangle((9,9,22,15),fill='#233340')
    d.polygon([(7,16),(24,16),(24,25),(22,27),(9,27),(7,25)],fill='#54217c')
    d.rectangle((9,18,22,25),fill='#863ab7');d.rectangle((10,19,19,24),fill='#9c48c4')
    d.ellipse((7,14,24,19),fill='#ac58d5',outline='#d9a2e9')
    d.line([(6,5),(24,5),(28,3)],fill='#d1e9ee');d.line([(7,7),(23,7),(26,5)],fill='#8eaab9')
    d.line([(7,9),(7,25),(9,27),(22,27)],fill='#adcad4')
    d.line([(24,9),(24,25)],fill='#698194')
    d.line((9,10,9,14),fill='#e0f4f3');d.line((9,20,9,23),fill='#d4b5e9')
    for y in (10,13,21,24): d.line((20,y,23,y),fill='#d3dbe1')
    d.ellipse((14,20,16,22),outline='#d09fe6');d.point((18,23),fill='#dab4f0')
    return im

def robot(size):
    im=Image.new('RGBA',(32,32));d=ImageDraw.Draw(im)
    for pts in [[(12,12),(7,8),(3,9)],[(19,12),(24,8),(28,9)],[(11,16),(6,17),(3,21)],[(20,16),(25,17),(28,21)],[(13,20),(10,25),(7,27)],[(18,20),(21,25),(24,27)]]:
        line3(d,pts,width=1)
        x,y=pts[1];d.rectangle((x-1,y-1,x+1,y+1),fill='#71518c');d.point((x-1,y-1),fill='#d4c2e4')
        x,y=pts[-1];d.line([(x-1,y),(x,y+2),(x+2,y+1)],fill='#c3c9cd')
    d.polygon([(12,9),(19,9),(22,14),(20,21),(13,23),(9,18),(9,13)],fill='#141d28',outline='#0b111b')
    d.polygon([(12,10),(18,10),(20,13),(18,18),(12,18),(10,14)],fill='#9aa7ac')
    d.polygon([(12,19),(18,19),(20,15),(19,21),(14,22)],fill='#4f5f6f')
    d.line([(12,10),(17,10),(19,12)],fill='#dfe3dc')
    d.rectangle((13,12,17,15),fill='#382748');d.rectangle((14,12,16,14),fill='#9a67bd');d.point((14,12),fill='#e9c7fb')
    d.line((13,17,17,17),fill='#222c3c')
    d.line([(15,9),(15,6),(18,4)],fill='#859bad');d.point((18,4),fill='#dab6f5')
    return im.resize((size,size),Image.Resampling.NEAREST)

def swarm():
    im=Image.new('RGBA',(64,64))
    for size,xy in [(22,(36,3)),(25,(3,5)),(28,(34,34)),(36,(7,25))]:im.alpha_composite(robot(size),xy)
    return im

def lattice():
    im=Image.new('RGBA',(48,48));d=ImageDraw.Draw(im)
    a=(23,3);b=(40,13);c=(40,32);e=(23,43);f=(7,33);g=(7,13);o=(23,23)
    for pts in [[a,b,c,e,f,g,a],[g,o,b],[o,e]]:
        d.line(pts,fill='#242238',width=3);d.line(pts,fill='#7f68a8',width=1)
    d.line([a,o,c],fill='#443956');d.line([f,o],fill='#443956')
    inner=[(23,12),(32,18),(32,28),(23,34),(15,28),(15,18),(23,12)]
    d.line(inner,fill='#b395d6',width=2);d.line([(15,18),(23,24),(32,18)],fill='#ead8f5');d.line([(23,24),(23,34)],fill='#b990dc')
    d.polygon([(23,17),(28,22),(23,28),(19,23)],fill='#653690',outline='#c391ed')
    d.line([(23,18),(25,21),(23,24),(21,22),(23,18)],fill='#f1d6ff')
    for x,y in (a,b,c,e,f,g):
        d.polygon([(x,y-2),(x+2,y),(x,y+2),(x-2,y)],fill='#abb1c7',outline='#302e43');d.point((x,y-1),fill='#efdefa')
    # 分离的小约束节点让晶格显出悬浮间隙。
    for x,y in [(4,23),(43,24),(23,46)]:d.point((x,y),fill='#c5a1ed')
    return im

def gallery(rows, filename, heading):
    font=lambda n:ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',n)
    sheet=Image.new('RGB',(1120,112+len(rows)*182),'#151d2a');d=ImageDraw.Draw(sheet)
    d.text((25,15),heading,font=font(25),fill='#f2f3fa')
    d.text((25,55),'候选未应用 · 原图保持原生分辨率 · 统一显示尺寸，动画只显示第一帧',font=font(17),fill='#b5c3d7')
    for i,e in enumerate(rows):
        y=105+i*182;d.rounded_rectangle((16,y,1104,y+171),radius=7,fill='#253245')
        d.text((29,y+12),e['title'],font=font(19),fill='#ffffff')
        words=e['note']
        for j in range(0,len(words),27):d.text((29,y+47+(j//27)*23),words[j:j+27],font=font(14),fill='#c0cce0')
        id=e['id'];refpath=OUT/'references'/f'{id}.png'
        ref=Image.open(refpath).convert('RGBA') if refpath.exists() else Image.open(TEX/('imitation_reason_core.png' if id=='imitation_flame_core' else f'{id}.png')).convert('RGBA') if (TEX/f'{id}.png').exists() else None
        new=Image.open(OUT/'candidates'/f'{id}.png').convert('RGBA')
        for x,pic,label in [(520,ref,'原图／当前参照'),(746,new,'本次候选')]:
            if pic:
                first=pic.crop((0,0,pic.width,min(pic.height,pic.width))).resize((128,128),Image.Resampling.NEAREST)
                sheet.paste(first,(x,y+9),first)
            else:d.text((x+6,y+55),'全新绘制',font=font(17),fill='#91a3bc')
            d.text((x,y+141),label,font=font(15),fill='#e0e7f1')
        small=new.crop((0,0,new.width,min(new.height,new.width))).resize((32,32),Image.Resampling.NEAREST)
        sheet.paste(small,(975,y+52),small);d.text((937,y+96),'32px识别预览',font=font(13),fill='#bccbdf')
    sheet.save(OUT/filename)

def main():
    OUT.mkdir(exist_ok=True)
    before={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in (ROOT/'src').rglob('*') if p.is_file()}
    for ident,color,factor,title,note in [
        ('honkai_fuel_rod_casing','#9856ce',1,'01 燃料棒壳体','候选G：反应堆燃料棒原图整体紫色；保留64像素原轮廓与明暗。'),
        ('soulium_swarf','#602788',0.72,'06 废料与残渣','候选L：GT金属粉原图，深紫色并降低28%亮度；无新增笔画。'),
        ('separation_filter','#9856ce',1,'09 分离滤芯','候选C：筛分矩阵原图整体紫色；原外框保留阴影，网格不重画。')]:
        src,meta=original(ident);new=recolor(src,color,factor)
        add(ident,title,new,ident,note,meta,{'alpha_equal':True,'brightness_scale':factor,'geometry_preserved':True})
    add('unmanned_resource_probe','02 无人资源探测器',probe(),'unmanned_resource_probe','参考候选H卫星：双翼分块阵列、扫描碟、独立扫描吊舱；新画64像素。')
    src,_=original('sealed_real_world_bubble')
    add('sealed_real_world_bubble','03 世界泡容器',bubble(src),'sealed_real_world_bubble','沿候选I原金属圆柱扩宽；中心换成黑色球体、疏密星点与暗星云。')
    src,meta=original('hyperion_thruster_assembly');new=src.copy();changed=[]
    for y in range(src.height):
        for x in range(src.width):
            r,g,b,a=src.getpixel((x,y));h,s,v=colorsys.rgb_to_hsv(r/255,g/255,b/255)
            if a and s>.3 and .44<h<.73:
                new.putpixel((x,y),tuple(round(c*255) for c in colorsys.hsv_to_rgb(.77,s,v))+(a,));changed.append((x,y))
    assert meta and changed
    add('hyperion_thruster_assembly','04 舰船推进组件',new,'hyperion_thruster_assembly','仅将蓝色／青蓝功能区改紫；金属和红黄指示灯不动，保留两帧动画。',meta,{'changed_pixels':len(changed),'outside_mask_unchanged':True,'alpha_equal':True})
    reason=Image.open(TEX/'imitation_reason_core.png').convert('RGBA');new=reason.copy();mask=[]
    for y in range(16):
        for x in range(4,12):
            r,g,b,a=reason.getpixel((x,y));h,s,v=colorsys.rgb_to_hsv(r/255,g/255,b/255)
            if a and b>r and .45<h<.75:
                new.putpixel((x,y),tuple(round(c*255) for c in colorsys.hsv_to_rgb(.065,s,v))+(a,));mask.append((x,y))
    add('imitation_flame_core','05 仿制炎之律者核心',new,note='以现有理核心为底，只换中心晶核颜色；金色环、外侧碎片和透明度保持。',checks={'core_mask':mask,'outside_mask_unchanged':True,'alpha_equal':True})
    detector=Image.open(TEX/'prototype_honkai_detector.png').convert('RGBA')
    add('prototype_honkai_detector','07 试作型探测器 · 保持当前',detector,note='按要求保持修订76现有图，未使用候选中的UV传感器。')
    add('honkai_analysis_sample','08 崩坏能分析样本',beaker(),note='新画敞口直壁烧杯：倾倒嘴、刻度、玻璃反光、半杯紫色液态崩坏能。')
    add('nano_building_unit','10 纳米构建单元',swarm(),note='已选“微型机器人群”：四个不同尺度机器人，具有机械足、夹爪和紫色核心。')
    add('reconstruction_rule_carrier','11 重构规则载体',lattice(),note='已选“悬浮几何晶格”：嵌套空间骨架、约束节点和中央规则晶体；全新绘制。')
    base,_=original('conducting_composite')
    for ident,title,color,note in [
        ('conducting_composite','12a 导能复合材料 · HDV','#3f56d0','GT碳纤维板原图整体蓝色；依据现有制造电压HDV。'),
        ('reconstructing_composite','12b 重构复合材料 · QAV','#269da8','同一GT原图整体青色；依据现有制造电压QAV。'),
        ('cognitive_composite','12c 认知复合材料 · IWV','#ffaa00','同一GT原图整体金色；依据现有制造电压IWV。'),
        ('confining_composite_a','12d 约束材料 A · 紫色候选','#885ac2','尚无单一电压归属；紫色仅为候选，不代表新增电压映射。'),
        ('confining_composite_b','12e 约束材料 B · 靛青候选','#526f95','尚无单一电压归属；靛青仅为候选，不代表新增电压映射。'),
        ('composite_offcut_a','12f 边角料 A · 灰紫候选','#78637f','通用边角料候选；沿用碳纤维板轮廓，灰紫色便于和成品区分。'),
        ('composite_offcut_b','12g 边角料 B · 灰蓝候选','#637b8e','通用边角料候选；沿用碳纤维板轮廓，灰蓝色不暗示特定电压。')]:
        add(ident,title,recolor(base,color),'conducting_composite',note,checks={'alpha_equal':True,'brightness_equal':True,'geometry_preserved':True})
    order=['honkai_fuel_rod_casing','unmanned_resource_probe','sealed_real_world_bubble','hyperion_thruster_assembly','imitation_flame_core','soulium_swarf','prototype_honkai_detector','honkai_analysis_sample','separation_filter','nano_building_unit','reconstruction_rule_carrier']
    byid={e['id']:e for e in ENTRIES}
    gallery([byid[i] for i in order[:6]],'review-1.png','贴图重做候选 1/3 · 原图染色与指定局部修改')
    gallery([byid[i] for i in order[6:]],'review-2.png','贴图重做候选 2/3 · 探测器保留与全新像素稿')
    gallery([e for e in ENTRIES if e['id'] not in order],'review-3.png','贴图重做候选 3/3 · 制造电压配色与待选材料')
    after={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in (ROOT/'src').rglob('*') if p.is_file()}
    assert before==after
    report={'created_at':datetime.now().astimezone().isoformat(),'status':'仅候选，未应用正式资源','source_tree_unchanged':True,'entries':ENTRIES}
    (OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'candidates':len(ENTRIES),'source_tree_unchanged':True,'pages':3}))

if __name__=='__main__':main()
