"""贴图评审83：七种指定配色核心与两版无人资源探测器。

【变更记录 #1】2026-09-27（贴图候选；准确生成时刻写入清单）
删除：无。新增：用户指定核心配色、侵蚀数据流、约束金链、探测器双候选。
修改：沿用理核心金环；探测器A从可无损还原的整合包原图局部强化。
用途：仅生成评审文件，不改正式资源；清单记录像素约束与源文件哈希。
"""
import colorsys
import json
from datetime import datetime
from PIL import Image, ImageDraw
import preview_art81 as a
import preview_art82 as b

OUT=a.ROOT/'logs/art-review83'

def main():
    before={str(p.relative_to(a.ROOT)):a.sha(p.read_bytes()) for p in (a.ROOT/'src').rglob('*') if p.is_file()}
    (OUT/'candidates').mkdir(parents=True,exist_ok=True)
    (OUT/'references').mkdir(exist_ok=True)
    b.OUT=OUT
    entries=[]
    def add(ident,title,im,ref,note,checks):
        dest=OUT/'candidates'/f'{ident}.png';im.save(dest)
        entries.append(dict(id=ident,title=title,note=note,candidate=str(dest),reference=str(ref),size=list(im.size),sha256=a.sha(dest.read_bytes()),checks=checks))
    source=Image.open(a.TEX/'imitation_reason_core.png').convert('RGBA')
    configs=[('thunder','雷','#9946e5'),('ice','冰','#2986ef'),('wind','风','#20bf7a'),('corruption','侵蚀','#572980'),('binding','约束','#f0cb49'),('rock','岩','#ac783a'),('void','空','#ed981b')]
    for key,name,color in configs:
        h,s,v=colorsys.rgb_to_hsv(*(int(color[i:i+2],16)/255 for i in (1,3,5)))
        im,checks=b.core(h); mask={tuple(p) for p in checks['mask']}
        if key=='corruption':
            for xy in mask:
                r,g,bl,alpha=im.getpixel(xy)
                hh,ss,vv=colorsys.rgb_to_hsv(r/255,g/255,bl/255)
                im.putpixel(xy,tuple(round(c*255) for c in colorsys.hsv_to_rgb(hh,ss,vv*.40))+(alpha,))
            # 短竖线与断续像素表现数据流，严格限定在原晶体区域内。
            for x,y in [(7,3),(7,4),(7,6),(8,6),(8,7),(8,9),(6,7),(6,8),(8,12)]:
                if (x,y) in mask: im.putpixel((x,y),(178,98,240,source.getpixel((x,y))[3]))
        elif key=='rock':
            for xy in mask:
                r,g,bl,alpha=im.getpixel(xy)
                hh,ss,vv=colorsys.rgb_to_hsv(r/255,g/255,bl/255)
                im.putpixel(xy,tuple(round(c*255) for c in colorsys.hsv_to_rgb(hh,ss*.85,vv*.77))+(alpha,))
        embellishments=[]
        if key=='binding':
            # 两组小链环放在原图空白处；金色圆环的任何像素均不覆盖。
            for x,y in [(1,5),(12,3),(1,7),(12,5)]:
                for dx,dy in [(0,0),(1,0),(0,1),(1,2),(0,2)]:
                    xy=(x+dx,y+dy)
                    if source.getpixel(xy)[3]==0:
                        im.putpixel(xy,((255,223,114,255) if dy==0 else (174,120,39,255)));embellishments.append(xy)
        unchanged=all(im.getpixel((x,y))==source.getpixel((x,y)) for y in range(16) for x in range(16) if (x,y) not in mask and (x,y) not in embellishments)
        assert unchanged
        checks.update(outside_mask_unchanged=unchanged,embellishment_pixels=embellishments,alpha_equal=im.getchannel('A').tobytes()==source.getchannel('A').tobytes(),color_authority='负责人本轮明确指定；非网络推断')
        note={'corruption':'黑紫晶体＋亮紫断续数据流；保留金色圆环。','binding':'金色晶体＋外侧小金链；原金色圆环不覆盖。'}.get(key,{'thunder':'紫色','ice':'蓝色','wind':'翠绿色','rock':'赭金色','void':'琥珀色'}[key]+'晶体；外侧两点同色，保留原金色圆环。') if key not in ('corruption','binding') else {'corruption':'黑紫晶体＋亮紫断续数据流；保留金色圆环。','binding':'金色晶体＋外侧小金链；原金色圆环不覆盖。'}[key]
        ident=f'imitation_{key}_core'
        add(ident,f'仿制{name}之律者核心',im,b.OLD.parent/'art-review82/candidates'/f'{ident}.png',note,checks)
    b.gallery(entries,'review-cores.png','贴图评审83 · 用户指定的七种核心配色')
    start=len(entries)
    src,_=a.original('unmanned_resource_probe')
    reduced=src.resize((16,16),Image.Resampling.NEAREST)
    assert reduced.resize(src.size,Image.Resampling.NEAREST).tobytes()==src.tobytes()
    ref=OUT/'references/probe-original-16.png';reduced.save(ref)
    im=reduced.copy();d=ImageDraw.Draw(im)
    # 原双翼、机身主体与朝向保持，只增加机身装甲高光和扫描端。
    d.line([(5,10),(7,8),(8,8)],fill='#d0d7d2')
    d.point((6,11),fill='#899b9f')
    d.rectangle((10,3,12,5),fill='#34444b')
    d.line((10,3,12,3),fill='#becdca')
    d.point((11,4),fill='#c880f0');d.point((12,4),fill='#7950a2')
    d.point((8,10),fill='#9063b4')
    changed=[(x,y) for y in range(16) for x in range(16) if im.getpixel((x,y))!=reduced.getpixel((x,y))]
    add('unmanned_resource_probe_a','探测器 A · 原图局部强化',im,ref,'直接使用整合包原图；保留斜向双翼与机身，只强化扫描头和装甲。',{'original_128_to_16_lossless':True,'changed_pixels':changed,'original_source_sha256':a.REFS['unmanned_resource_probe']['source_sha256']})
    im=b.sprite([
        '................',
        '.......hh.......',
        '......hmmh......',
        '.......ss.......',
        '......#hh#......',
        '.####.#mm#.####.',
        '.hvp#smpvms#pvh.',
        '.hpv#smlvms#vph.',
        '.hvp#smpvms#pvh.',
        '.####.#ss#.####.',
        '......#mm#......',
        '.......ss.......',
        '......#vv#......',
        '.......hh.......',
        '................',
        '................'])
    add('unmanned_resource_probe_b','探测器 B · 紧凑扫描卫星',im,ref,'全新16像素稿；左右双翼、中央机身、顶部扫描碟与底部传感器。',{'native_16_pixels':True})
    b.gallery(entries[start:],'review-probes.png','贴图评审83 · 无人资源探测器双候选')
    after={str(p.relative_to(a.ROOT)):a.sha(p.read_bytes()) for p in (a.ROOT/'src').rglob('*') if p.is_file()};assert before==after
    report=dict(created_at=datetime.now().astimezone().isoformat(),status='仅候选，未应用',source_tree_unchanged=True,entries=entries,accepted_review82=['03','05','10','11'],retained='未改已认可候选；未部署、未游戏测试')
    (OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(dict(candidates=len(entries),source_tree_unchanged=True)))

if __name__=='__main__':main()
