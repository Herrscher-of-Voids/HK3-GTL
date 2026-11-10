# -*- coding: utf-8 -*-
"""保存胸腹比例对照与摆位证据；更新固定审计，分数保持不变。"""
from copy import deepcopy
from datetime import datetime,timezone,timedelta
from pathlib import Path
from html import escape
import hashlib,json,re,shutil,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import w04_kurikara_d4_20261110 as g
from package_w04_gemini_b1_20261110 import hashes,save

P1=g.ROOT/'deliveries/W04_龙踞雷池七雷镇枢_组合布局_P1_20261110'
REPORT=g.ROOT/'logs/beta5-completion-audit-20261030'
load=lambda p:json.loads(p.read_text('utf8'))


def comparisons():
    font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',27)
    for name,part in [('身躯D3_D4同机位.png','全身'),('胸腹D3_D4同机位.png','胸腹')]:
        canvas=Image.new('RGB',(1900,950),'#15131b');draw=ImageDraw.Draw(canvas)
        draw.text((30,18),'同机位、同缩放；左D3，右D4。双翼、厚尾、头和腿爪保持。',font=font,fill='#f1dce7')
        for col,version in enumerate(['D3','D4']):
            image=Image.open(g.OUT/f'对照{version}{part}.png').convert('RGB');image.thumbnail((920,790))
            canvas.paste(image,(col*950+(950-image.width)//2,95+(790-image.height)//2))
            draw.text((col*950+30,900),version+('：原胸腹和肩背' if col==0 else '：加厚胸腹和肩背，头颈平滑过渡'),font=font,fill='#eac8d7')
        canvas.save(g.OUT/name)


def geometry():
    old=np.load(g.ROOT/'logs/w04-kurikara-d3-20261110/components.npz');new=np.load(g.LOG/'components.npz')
    manifest=load(g.OUT/'manifest.json')
    for name in manifest['unchanged_components']:
        for suffix in ['__p','__states']:
            assert np.array_equal(old[name+suffix],new[name+suffix]),(name,suffix)
    points=lambda a:next(a[k] for k in a.files if k.startswith('02_') and k.endswith('__p'))
    a,b=points(old),points(new)
    rows=[]
    for y in [145,176,199,220]:
        widths=[]
        for points_ in [a,b]:
            section=points_[abs(points_[:,1]-y)<=1]
            widths.append(dict(width=int(np.ptp(section[:,0])+1),depth=int(np.ptp(section[:,2])+1)))
        rows.append(dict(y=y,d3=widths[0],d4=widths[1]))
    assert len(b)>len(a)*1.5
    for axis in [0,2]:assert np.ptp(b[:,axis])>np.ptp(a[:,axis])
    for data in [a,b]:assert len(data[data[:,1]>=263])>0
    sort=lambda p:p[np.lexsort(p.T)]
    assert np.array_equal(sort(a[a[:,1]>=263]),sort(b[b[:,1]>=263])),'头颈接合区发生变化'
    assert manifest['connectivity']['six_neighbor_components']==1
    result=dict(passed=True,unchanged_components=manifest['unchanged_components'],only_torso_changed=True,
        torso_raw_voxels_d3=len(a),torso_raw_voxels_d4=len(b),sections=rows,
        head_attachment_above_y263_unchanged=True,static=True,source_mesh_used=False)
    save(g.LOG/'geometry-detail-qa.json',result);return result


def main():
    comparisons()
    if '--images-only' in sys.argv:return
    proof=geometry();manifest=load(g.OUT/'manifest.json');qa=load(g.LOG/'viewer-qa.json')
    verify=load(g.OUT/'verification.json');layout=load(P1/'verification.json')
    assert qa['passed'] and layout['passed'] and qa['static']
    assert verify['readback']['geometry_nbt_schematic_per_block_equal']
    assert {p.name:hashes(p) for p in [g.PRIOR,g.SWORD]}==load(g.LOG/'prior-before-hashes.json')
    refs=load(g.OUT/'参考图清单.json')
    refroot=g.ROOT/'deliveries/W04_俱利伽罗_腿爪与叠甲细化_D2_20261110/参考图'
    for item in refs['images']:assert hashlib.sha256((refroot/item['file']).read_bytes()).hexdigest()==item['sha256']
    verify.update(geometry_detail=proof,reference_images=57,game_verified=False);save(g.OUT/'verification.json',verify)
    now=datetime.now(timezone(timedelta(hours=-5))).isoformat(timespec='seconds')
    history=g.LOG/('d4-p1-audit-before-'+datetime.now().strftime('%Y%m%d-%H%M%S-%f'));history.mkdir()
    for name in ['index.html','current-summary.json']:shutil.copy2(REPORT/name,history/name)
    for name in ['AGENTS.md','rule/当前多方块设计规则.md']:shutil.copy2(g.ROOT/name,history/Path(name).name)
    before=load(history/'current-summary.json');data=deepcopy(before)
    item=dict(id='W04',candidate='俱利伽罗厚躯肩背D4与龙踞雷池七雷镇枢P1',
        preview=(g.OUT/'index.html').relative_to(g.ROOT).as_posix(),
        layout_preview=(P1/'index.html').relative_to(g.ROOT).as_posix(),
        scope='独立静态龙体与整机组合摆位草案',size_xyz=manifest['size'],blocks=manifest['blocks'],
        proportion_metrics=proof,layout_verification=layout,reference_images=57,added_references=0,
        static=True,approved=False,installed=False,game_verified=False,d3_retained=True,sword_s1_unchanged=True,
        remaining=['外观与组合摆位待负责人评审。','P1工业设施仅为体量草模，非逐格整机蓝图。',
            '暂无官方精确三视尺寸，背部遮挡细节仍待核对。','未注册、未在游戏搭建或验证成型／运行。'],updated_at=now)
    system=next(s for s in data['systems'] if s['id']=='multiblocks')
    system['w04_kurikara_body_d4_layout_p1']=deepcopy(item);system['updated_at']=now
    data['current_work']['w04_kurikara_body_d4_layout_p1']=deepcopy(item);data['report_updated_at']=now
    data['systems'].sort(key=lambda s:s['percent'])
    score=lambda d:{s['id']:(s['earned'],s['possible'],s['percent']) for s in d['systems']}
    assert score(data)==score(before) and data['overall_percent']==before['overall_percent']
    text=(history/'index.html').read_text('utf8');anchor='<main><h1>系统完成度 · 低到高 · 固定入口</h1>'
    assert anchor in text
    note=f'{now} · W04龙体D4仅加厚胸腹肩背，保持D3头、双翼、尾与腿爪；16视角、同机位对照、连通和NBT／Schematic逐格回读通过。P1为龙踞后上方、七雷斜悬前方并共用雷池的静态布局，刀仅在组合中等比缩小，源模型保持；工业体量为草模。外观待评审，未实装，系统分数不变。'
    text=re.sub(r'<p class="notice" id="w04-d4-p1-current">.*?</p>','',text,flags=re.S)
    text=text.replace(anchor,anchor+'<p class="notice" id="w04-d4-p1-current">'+escape(note)+
        ' <a href="../../'+item['preview']+'">D4厚躯对照</a> · <a href="../../'+item['layout_preview']+'">P1组合摆位</a></p>',1)
    text,n=re.subn(r'<p>更新 [^<]+</p>','<p>更新 '+escape(now)+' · W04 D4与P1候选</p>',text,count=1);assert n==1
    text,n=re.subn(r'(?<=id="audit-data">).*?(?=</script>)',lambda _:json.dumps(data,ensure_ascii=False).replace('<','\\u003c'),text,count=1,flags=re.S);assert n==1
    assert json.loads(re.search(r'id="audit-data">(.*?)</script>',text,re.S)[1])==data
    assert re.findall(r'<details class="system" data-id="([^"]+)"',text)==[s['id'] for s in data['systems']]
    note='\n\n## 2026-11-10 W04厚躯D4与组合布局P1候选\n\n'
    note+='- 负责人指出D3身躯显小并要求考虑七雷与龙的组合。D4仅加厚胸腹肩背并平滑收束至头颈，D3头、双翼、厚尾与腿爪逐格保持；沿用57张参考，美术比例修订不宣称官方精确尺寸。\n'
    note+='- P1为“龙踞雷池·七雷镇枢”静态摆位草案：龙踞后上空，七雷斜悬前方，刀尖对准共同雷池，前庭保留控制器及同面3×3周围8接口示意；仅在布局内等比缩放刀，龙与刀源模型保留。工业设施是体量草模，不等于完整多方块蓝图；不直接覆盖旧Gemini候选。\n'
    note+=f'- D4预览：{item["preview"]}；P1预览：{item["layout_preview"]}。D4实际907×596×399格，16视角与同机位对照、连通、导出回读通过；P1完整取景与龙刀前后净空核验见各自verification.json。两者均无动画、待外观评审、未游戏实装；系统分数与批准数量不变。\n'
    for file in [g.ROOT/'AGENTS.md',g.ROOT/'rule/当前多方块设计规则.md']:
        content=file.read_text('utf8');marker='## 2026-11-10 W04厚躯D4与组合布局P1候选'
        content=re.sub(r'\n\n'+re.escape(marker)+r'.*?(?=\n\n## |\Z)',lambda _:note,content,flags=re.S) if marker in content else content+note
        file.write_text(content,'utf8')
    save(REPORT/'current-summary.json',data);(REPORT/'index.html').write_text(text,'utf8')
    receipt=dict(passed=True,history=str(history),systems=len(data['systems']),overall_percent=data['overall_percent'],
        scores_unchanged=True,html_json_synced=True,ascending_order=True,game_verified=False)
    save(g.LOG/'d4-p1-audit-update.json',receipt)
    shutil.copy2(Path(__file__),g.OUT/'生成脚本'/Path(__file__).name)
    print(json.dumps(receipt))


if __name__=='__main__':main()
