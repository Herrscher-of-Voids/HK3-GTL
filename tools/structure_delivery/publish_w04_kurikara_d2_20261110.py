# -*- coding: utf-8 -*-
"""生成腿爪对照，核验部件与来源；更新固定审计但不增加完成分。"""
from copy import deepcopy
from datetime import datetime,timezone,timedelta
from html import escape
from pathlib import Path
import hashlib,json,re,shutil,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import w04_kurikara_d2_20261110 as g
from package_w04_gemini_b1_20261110 import hashes,save

REPORT=g.ROOT/'logs/beta5-completion-audit-20261030'


def load(path):return json.loads(path.read_text('utf8'))


def comparisons():
    font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',28)
    small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',23)
    for name,left,right,caption,labels in [
        ('腿爪D1_D2对照.png','D1后足同机位.png','后足近景.png','同一镜头方向、范围与缩放；左D1，右D2',
            ['D1：细腿、窄掌、短平爪','D2：厚腿甲、反折关节、宽掌与长钩爪']),
        ('腿爪参考对照.jpg','参考_后足.jpg','后足近景.png','左为玩家游戏原帧，右为D2；不同视角，不作像素叠图匹配',
            ['游戏画面：骨白叠甲与粗壮红爪','D2：按原版分段结构细化'])]:
        canvas=Image.new('RGB',(1900,950),'#15131b');draw=ImageDraw.Draw(canvas)
        draw.text((32,20),caption,font=font,fill='#f0e5ec')
        for col,file in enumerate([left,right]):
            im=Image.open(g.OUT/file).convert('RGB');im.thumbnail((920,790))
            canvas.paste(im,(col*950+(950-im.width)//2,100+(790-im.height)//2))
            draw.text((col*950+32,900),labels[col],font=small,fill='#e8c7d4')
        canvas.save(g.OUT/name,**({'quality':94} if name.endswith('.jpg') else {}))


def verify_geometry():
    old=np.load(g.ROOT/'logs/w04-kurikara-d1-20261110/components.npz')
    new=np.load(g.LOG/'components.npz');manifest=load(g.OUT/'manifest.json')
    for name in manifest['unchanged_components']:
        assert np.array_equal(old[name+'__p'],new[name+'__p']),('保留构件坐标改变',name)
        assert np.array_equal(old[name+'__states'],new[name+'__states']),('保留构件材质改变',name)
    legs=[]
    for side in ['+1','-1']:
        ok=next(k for k in old.files if k.startswith('06_'+side) and k.endswith('__p'))
        nk=next(k for k in new.files if k.startswith('06_'+side) and k.endswith('__p'))
        op,np_=old[ok],new[nk]
        # 同一脚掌高度段核对体积变化；不把全腿增长当作脚掌加宽证据。
        def span(points):
            section=points[(points[:,1]>=25)&(points[:,1]<=40)&(points[:,2]>25)]
            assert len(section)>0
            return int(np.ptp(section[:,0])+1)
        a,b=span(op),span(np_)
        assert len(np_)>len(op)*3 and b>a*1.35
        legs.append(dict(side=side,old_blocks=len(op),new_blocks=len(np_),volume_ratio=len(np_)/len(op),
            palm_section_old_width=a,palm_section_new_width=b))
    assert manifest['connectivity']['six_neighbor_components']==1
    proof=dict(passed=True,unchanged_components=manifest['unchanged_components'],legs=legs,
        removed_voxels=0,full_geometry_connected=True,animation_enabled=False,source_mesh_used=False)
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
        assert hashlib.sha256((g.OUT/'参考图'/r['file']).read_bytes()).hexdigest()==r['sha256']
    verification.update(geometry_detail=geometry,reference_images=57,fan_model_images=13,
        source_mesh_used=False,official_dragon_model_status='未确认公开源文件',game_verified=False)
    save(g.OUT/'verification.json',verification)
    history=g.LOG/('d2-audit-before-'+datetime.now().strftime('%Y%m%d-%H%M%S-%f'));history.mkdir()
    for name in ['index.html','current-summary.json']:shutil.copy2(REPORT/name,history/name)
    for name in ['AGENTS.md','rule/当前多方块设计规则.md']:shutil.copy2(g.ROOT/name,history/Path(name).name)
    before=load(history/'current-summary.json');data=deepcopy(before)
    now=datetime.now(timezone(timedelta(hours=-5))).isoformat(timespec='seconds')
    item=dict(id='W04',candidate='俱利伽罗腿爪与叠甲细化D2',scope='独立静态龙体，不含七雷或整机场景',
        preview=(g.OUT/'index.html').relative_to(g.ROOT).as_posix(),
        references=(g.OUT/'参考图总览.html').relative_to(g.ROOT).as_posix(),
        reference_images=57,added_references=14,fan_model_images=13,official_frames=34,
        fan_model_url='https://www.artstation.com/artwork/n0bPo1',official_dragon_model_status='未确认公开源文件',
        source_mesh_used=False,size_xyz=manifest['size'],blocks=manifest['blocks'],components=9,
        static=True,approved=False,installed=False,game_verified=False,d1_retained=True,sword_s1_unchanged=True,
        offline_verification='logs/w04-kurikara-d2-20261110/viewer-qa.json',
        remaining=['外观待负责人评审。','未取得官方龙体三视尺寸或公开源模型，背部遮挡细节仍待核对。',
            '独立细节比例尚未安放进W04整机。','未注册、未在游戏搭建或验证成型／运行。'],updated_at=now)
    system=next(s for s in data['systems'] if s['id']=='multiblocks')
    system['w04_kurikara_detail_d2']=deepcopy(item);system['updated_at']=now
    data['current_work']['w04_kurikara_detail_d2']=deepcopy(item);data['report_updated_at']=now
    data['systems'].sort(key=lambda s:s['percent'])
    scores=lambda d:{s['id']:(s['earned'],s['possible'],s['percent']) for s in d['systems']}
    assert scores(data)==scores(before) and data['overall_percent']==before['overall_percent']
    page=(history/'index.html').read_text('utf8')
    note=f'{now} · W04俱利伽罗独立静态D2：57张分源参考，新增玩家三维作品正侧背面、线框与材质展示及其游戏原图14张；作者作品为写实改编，只辅助体积，未使用源网格。重做双后腿、反折关节、宽掌长钩爪，细化胸腹颈甲与翼腕；16视角、静态控件、完整取景、连通及NBT／Schematic逐格回读通过。未确认官方龙体公开模型；外观待评审，未游戏实装，D1与鸣雷见S1未变，分数不变。'
    anchor='<main><h1>系统完成度 · 低到高 · 固定入口</h1>';assert anchor in page
    page=re.sub(r'<p class="notice" id="w04-kurikara-d2-current">.*?</p>','',page,flags=re.S)
    page=page.replace(anchor,anchor+'<p class="notice" id="w04-kurikara-d2-current">'+escape(note)+
        ' <a href="../../'+item['preview']+'">D2预览与对照</a> · <a href="../../'+item['references']+'">57张参考</a></p>',1)
    page,n=re.subn(r'<p>更新 [^<]+</p>','<p>更新 '+escape(now)+' · W04俱利伽罗D2候选</p>',page,count=1);assert n==1
    page,n=re.subn(r'(?<=id="audit-data">).*?(?=</script>)',lambda _:json.dumps(data,ensure_ascii=False).replace('<','\\u003c'),page,count=1,flags=re.S);assert n==1
    assert json.loads(re.search(r'id="audit-data">(.*?)</script>',page,re.S)[1])==data
    assert re.findall(r'<details class="system" data-id="([^"]+)"',page)==[s['id'] for s in data['systems']]
    note='\n\n## 2026-11-10 W04俱利伽罗腿爪与叠甲细化D2候选\n\n'
    note+='- 负责人否定D1腿足过细，要求更多角度与官方／玩家三维模型参考。当前D2重做厚腿根、反折关节、宽爪掌及长钩爪，细化胸腹颈部叠甲和翼腕；D1与超限鸣雷见S1完整保留。继续逐部件制作、无动画，不合并W04整机。\n'
    note+='- 共57张参考：保留D1的43张，新增Terence Chong公开三维作品展示13张（含线框与材质）及其游戏参考图1张。该作品是作者写实改编，仅辅助体积，未使用源网格；已查官方配布页与雷律人物包，尚未确认官方龙体公开源文件，不宣称不存在。\n'
    note+=f'- 预览：{item["preview"]}；参考同目录参考图总览.html；证据logs/w04-kurikara-d2-20261110/。实际宽{manifest["size"][0]}×深{manifest["size"][2]}×高{manifest["size"][1]}，{manifest["blocks"]:,}实体；16视角、无裁切、六向连通和NBT／Schematic逐格回读通过。外观待评审，未游戏实装；系统分数及批准数量不变。\n'
    for path in [g.ROOT/'AGENTS.md',g.ROOT/'rule/当前多方块设计规则.md']:
        content=path.read_text('utf8')
        marker='## 2026-11-10 W04俱利伽罗腿爪与叠甲细化D2候选'
        if marker in content:
            content=re.sub(r'\n\n'+re.escape(marker)+r'.*?(?=\n\n## |\Z)',lambda _:note,content,flags=re.S)
        else:content+=note
        path.write_text(content,'utf8')
    save(REPORT/'current-summary.json',data);(REPORT/'index.html').write_text(page,'utf8')
    receipt=dict(passed=True,updated_at=now,history=str(history),systems=len(data['systems']),
        overall_percent=data['overall_percent'],scores_unchanged=True,html_json_synced=True,ascending_order=True,
        reference_images=57,d1_unchanged=True,sword_s1_unchanged=True,game_verified=False)
    save(g.LOG/'d2-audit-update.json',receipt)
    shutil.copy2(Path(__file__),g.OUT/'生成脚本'/Path(__file__).name)
    print(json.dumps(receipt,ensure_ascii=True))


if __name__=='__main__':main()
