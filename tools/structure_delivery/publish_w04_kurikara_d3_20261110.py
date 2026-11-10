# -*- coding: utf-8 -*-
"""生成腿爪对照，核验部件与来源；更新固定审计但不增加完成分。"""
from copy import deepcopy
from datetime import datetime,timezone,timedelta
from html import escape
from pathlib import Path
import hashlib,json,re,shutil,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import w04_kurikara_d3_20261110 as g
from package_w04_gemini_b1_20261110 import hashes,save

REPORT=g.ROOT/'logs/beta5-completion-audit-20261030'


def load(path):return json.loads(path.read_text('utf8'))


def comparisons():
    font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',28)
    small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',23)
    for name,part,caption,labels in [
        ('翼尾D2_D3同机位.png','全身','同一机位和缩放；左D2，右D3',
            ['D2：原翼展与细尾','D3：展开翼骨、宽翼膜、加厚尾体']),
        ('尾部D2_D3同机位.png','尾部','同一尾部路径、机位和缩放；左D2，右D3',
            ['D2：细尾根与细中段','D3：粗尾根、厚中段，逐节渐细'])]:
        canvas=Image.new('RGB',(1900,950),'#15131b');draw=ImageDraw.Draw(canvas)
        draw.text((32,20),caption,font=font,fill='#f0e5ec')
        for col,version in enumerate(['D2','D3']):
            im=Image.open(g.OUT/f'对照{version}{part}.png').convert('RGB');im.thumbnail((920,790))
            canvas.paste(im,(col*950+(950-im.width)//2,100+(790-im.height)//2))
            draw.text((col*950+32,900),labels[col],font=small,fill='#e8c7d4')
        canvas.save(g.OUT/name)


def verify_geometry():
    old=np.load(g.ROOT/'logs/w04-kurikara-d2-20261110/components.npz')
    new=np.load(g.LOG/'components.npz');manifest=load(g.OUT/'manifest.json')
    for name in manifest['unchanged_components']:
        assert np.array_equal(old[name+'__p'],new[name+'__p']),('保留构件坐标改变',name)
        assert np.array_equal(old[name+'__states'],new[name+'__states']),('保留构件材质改变',name)
    def join(data,prefixes):return np.vstack([data[k] for k in data.files if k.endswith('__p') and k.startswith(prefixes)])
    ow,nw=join(old,('04_','05_')),join(new,('04_','05_'))
    span=lambda points:int(np.ptp(points[:,0])+1)
    assert span(nw)>span(ow)*1.35
    ot,nt=join(old,('03_',)),join(new,('03_',));sections=[]
    for z in [-100,-198,-283]:
        section=lambda points:points[abs(points[:,2]-z)<=1]
        a,b=span(section(ot)),span(section(nt));assert b>a*1.55
        sections.append(dict(z=z,old_width=a,new_width=b,ratio=b/a))
    before=load(g.PRIOR/'manifest.json')
    assert abs(before['tail_centerline_length']-manifest['tail_centerline_length'])<1e-9
    assert manifest['connectivity']['six_neighbor_components']==1
    proof=dict(passed=True,unchanged_components=manifest['unchanged_components'],
        wingspan_old=span(ow),wingspan_new=span(nw),wingspan_ratio=span(nw)/span(ow),
        tail_sections=sections,tail_centerline_unchanged=True,removed_voxels=0,
        full_geometry_connected=True,animation_enabled=False,source_mesh_used=False)
    save(g.LOG/'geometry-detail-qa.json',proof)
    return proof


def main():
    if '--images-only' in sys.argv:comparisons();return
    comparisons();geometry=verify_geometry()
    manifest=load(g.OUT/'manifest.json');qa=load(g.LOG/'viewer-qa.json')
    verification=load(g.OUT/'verification.json');references=load(g.OUT/'参考图清单.json')
    assert qa['passed'] and qa['screenshots']==16 and qa['static']
    assert verification['readback']['geometry_nbt_schematic_per_block_equal']
    assert {p.name:hashes(p) for p in [g.PRIOR,g.SWORD]}==load(g.LOG/'prior-before-hashes.json')
    assert references['count']==57
    for r in references['images']:
        assert hashlib.sha256((g.PRIOR/'参考图'/r['file']).read_bytes()).hexdigest()==r['sha256']
    verification.update(geometry_detail=geometry,reference_images=57,fan_model_images=13,
        source_mesh_used=False,official_dragon_model_status='未确认公开源文件',game_verified=False)
    save(g.OUT/'verification.json',verification)
    history=g.LOG/('d3-audit-before-'+datetime.now().strftime('%Y%m%d-%H%M%S-%f'));history.mkdir()
    for name in ['index.html','current-summary.json']:shutil.copy2(REPORT/name,history/name)
    for name in ['AGENTS.md','rule/当前多方块设计规则.md']:shutil.copy2(g.ROOT/name,history/Path(name).name)
    before=load(history/'current-summary.json');data=deepcopy(before)
    now=datetime.now(timezone(timedelta(hours=-5))).isoformat(timespec='seconds')
    item=dict(id='W04',candidate='俱利伽罗展翼与厚尾D3',scope='独立静态龙体，不含七雷或整机场景',
        preview=(g.OUT/'index.html').relative_to(g.ROOT).as_posix(),
        references=(g.OUT/'参考图总览.html').relative_to(g.ROOT).as_posix(),
        reference_images=57,added_references=0,fan_model_images=13,official_frames=34,proportion_metrics=geometry,
        fan_model_url='https://www.artstation.com/artwork/n0bPo1',official_dragon_model_status='未确认公开源文件',
        source_mesh_used=False,size_xyz=manifest['size'],blocks=manifest['blocks'],components=9,
        static=True,approved=False,installed=False,game_verified=False,d2_retained=True,sword_s1_unchanged=True,
        offline_verification='logs/w04-kurikara-d3-20261110/viewer-qa.json',
        remaining=['外观待负责人评审。','未取得官方龙体三视尺寸或公开源模型，背部遮挡细节仍待核对。',
            '独立细节比例尚未安放进W04整机。','未注册、未在游戏搭建或验证成型／运行。'],updated_at=now)
    system=next(s for s in data['systems'] if s['id']=='multiblocks')
    system['w04_kurikara_wing_tail_d3']=deepcopy(item);system['updated_at']=now
    data['current_work']['w04_kurikara_wing_tail_d3']=deepcopy(item);data['report_updated_at']=now
    data['systems'].sort(key=lambda s:s['percent'])
    scores=lambda d:{s['id']:(s['earned'],s['possible'],s['percent']) for s in d['systems']}
    assert scores(data)==scores(before) and data['overall_percent']==before['overall_percent']
    page=(history/'index.html').read_text('utf8')
    note=f'{now} · W04俱利伽罗独立静态D3：按既有57张参考校准翼尾比例，翼展由{geometry["wingspan_old"]}扩至{geometry["wingspan_new"]}格，翼膜后展，尾根与中段加厚，尾部中心线不变；头、躯干、双腿爪逐格保留D2。16视角、同机位对照、完整取景、静态控件、连通与NBT／Schematic逐格回读通过。美术比例修订非官方精确尺寸，外观待评审，未游戏实装；D2与鸣雷见S1未变，分数不变。'
    anchor='<main><h1>系统完成度 · 低到高 · 固定入口</h1>';assert anchor in page
    page=re.sub(r'<p class="notice" id="w04-kurikara-d3-current">.*?</p>','',page,flags=re.S)
    page=page.replace(anchor,anchor+'<p class="notice" id="w04-kurikara-d3-current">'+escape(note)+
        ' <a href="../../'+item['preview']+'">D3预览与对照</a> · <a href="../../'+item['references']+'">57张参考</a></p>',1)
    page,n=re.subn(r'<p>更新 [^<]+</p>','<p>更新 '+escape(now)+' · W04俱利伽罗D3候选</p>',page,count=1);assert n==1
    page,n=re.subn(r'(?<=id="audit-data">).*?(?=</script>)',lambda _:json.dumps(data,ensure_ascii=False).replace('<','\\u003c'),page,count=1,flags=re.S);assert n==1
    assert json.loads(re.search(r'id="audit-data">(.*?)</script>',page,re.S)[1])==data
    assert re.findall(r'<details class="system" data-id="([^"]+)"',page)==[s['id'] for s in data['systems']]
    note='\n\n## 2026-11-10 W04俱利伽罗展翼与厚尾D3候选\n\n'
    note+='- 负责人指出D2翅膀过小、尾巴过细。D3扩大翼骨、翼膜与四片翼刃，按原中心线加厚尾根和中段并逐节收细；D2头、躯干、双腿爪逐格保留。D2与鸣雷见S1完整保留，继续独立静态龙体，不合并W04整机。\n'
    note+=f'- 翼展{geometry["wingspan_old"]}→{geometry["wingspan_new"]}格，尾部三截面厚度见logs/w04-kurikara-d3-20261110/geometry-detail-qa.json。沿用57张分源参考，重点对照官方展翼与侧背原帧；扩大比例是美术修订，不宣称官方精确比例或使用了官方源网格。\n'
    note+=f'- 预览：{item["preview"]}；证据logs/w04-kurikara-d3-20261110/。实际宽{manifest["size"][0]}×深{manifest["size"][2]}×高{manifest["size"][1]}，{manifest["blocks"]:,}实体；16视角、同机位对照、无裁切、六向连通及NBT／Schematic逐格回读通过。外观待评审，未游戏实装；系统分数及批准数量不变。\n'
    for path in [g.ROOT/'AGENTS.md',g.ROOT/'rule/当前多方块设计规则.md']:
        content=path.read_text('utf8')
        marker='## 2026-11-10 W04俱利伽罗展翼与厚尾D3候选'
        if marker in content:
            content=re.sub(r'\n\n'+re.escape(marker)+r'.*?(?=\n\n## |\Z)',lambda _:note,content,flags=re.S)
        else:content+=note
        path.write_text(content,'utf8')
    save(REPORT/'current-summary.json',data);(REPORT/'index.html').write_text(page,'utf8')
    receipt=dict(passed=True,updated_at=now,history=str(history),systems=len(data['systems']),
        overall_percent=data['overall_percent'],scores_unchanged=True,html_json_synced=True,ascending_order=True,
        reference_images=57,d2_unchanged=True,sword_s1_unchanged=True,game_verified=False)
    save(g.LOG/'d3-audit-update.json',receipt)
    shutil.copy2(Path(__file__),g.OUT/'生成脚本'/Path(__file__).name)
    print(json.dumps(receipt,ensure_ascii=True))


if __name__=='__main__':main()
