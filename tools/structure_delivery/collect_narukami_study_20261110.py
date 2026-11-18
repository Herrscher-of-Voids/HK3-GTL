# -*- coding: utf-8 -*-
"""只整理鸣雷见；转台采样、尺寸辅助和低清转存分别记账。"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone,timedelta
from html import escape
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'deliveries/W04_涤罪七雷鸣雷见_独立小样_S1_20261110'
LOG=ROOT/'logs/w04-narukami-study-20261110'
CACHE=Path.home()/'.cache/hk3gtl-w04-reference-videos'
SOURCES={
    'turn':dict(video='vCMehnpv8gE',author='舞亜',title='崩坏3rd 5.8版本 新武器－裁决之键「涤罪七雷·鸣」',kind='玩家游戏原帧',
        use='仅使用68.5秒以后明确标注鸣雷见的武器转台；基础鸣退出本次图集。'),
    'upgrade':dict(video='NkGlHl51ofw',author='【Ğēłäp「•」黒人】',title='Seven Thunders of Retribution : Narukami (full upgrade)',kind='玩家游戏原帧',
        use='超限锻造与装备界面，辅助核对同一形态和握持尺寸；不是新增独立转台。'),
    'rush':dict(video='3wqJGwWMOfM',author='CrushyRushX',title='Seven Thunders of Retribution, The New Divine Key',kind='玩家游戏原帧',
        use='后半段鸣雷见的装备与战斗尺寸，前半段基础鸣不收录。'),
    'review':dict(video='BZiSwCj65hk',author='Marisa Honkai',title='Seven Thunders of Retribution Review - A Big Upgrade for HoT',kind='玩家评测画面',
        use='鸣雷见形态与武器展示图的交叉核对，不作为背面和厚度的主证据。')}


def main():
    folder=OUT/'参考图';folder.mkdir(parents=True,exist_ok=True)
    rows=[]
    # 一个旋转周期内每半秒取一张，不能把多轮相同转台算成不同机位。
    turns=[(68.5+i*.5,f'转台角度{i+1:02d}：正反与端向连续对照','旋转视角') for i in range(30)]
    sets=[('turn',turns),('upgrade',[(t,label,'形态及尺寸辅助') for t,label in [
        (110,'超限锻造列表'),(174,'鸣雷见升级前界面'),(180,'超限前后同形对照'),(184,'升级界面完整刃形'),
        (196,'升级展示中完整刀型'),(210,'超限装备正侧轮廓'),(216,'鸣雷见名称与刀面'),
        (254,'升级后刃面与护手'),(298,'满级鸣雷见确认'),(302,'角色手持与刀柄比例')]]),
        ('rush',[(t,label,'握持及装备辅助') for t,label in [(82,'装备背侧尺寸'),(118,'战斗中刃长'),
            (130,'结束镜头握持尺寸'),(132,'侧后握柄与刃身')]]),
        ('review',[(2,'评测中的鸣雷见界面','形态及尺寸辅助'),(8,'完整武器插图与名称','形态及尺寸辅助')])]
    for source,items in sets:
        info=SOURCES[source]
        for seconds,label,angle in items:
            rows.append(dict(id=f'R{len(rows)+1:02d}',source=source,seconds=seconds,label=label,angle=angle,
                kind=info['kind'],title=info['title'],author=info['author'],
                url=f'https://www.youtube.com/watch?v={info["video"]}&t={seconds}s',file=f'{source}-{seconds:05.1f}.jpg'))
    def extract(row):
        file=folder/row['file']
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-ss',str(row['seconds']),'-i',str(CACHE/(SOURCES[row['source']]['video']+'.mp4')),
            '-frames:v','1','-q:v','2','-y',str(file)],check=True)
        with Image.open(file) as im:row['resolution']=list(im.size)
        row['sha256']=hashlib.sha256(file.read_bytes()).hexdigest()
        return row
    rows=list(ThreadPoolExecutor(4).map(extract,rows))
    image_info=json.loads((ROOT/'logs/w04-reference-study-20261110/wiki-imageinfo.json').read_text('utf8'))
    for item in image_info['query']['pages'].values():
        if 'Narukami' not in item['title']:continue
        info=item['imageinfo'][0]
        if info['width']<500:continue
        name=item['title'].replace('File:','').replace(' ','_');file=folder/name
        shutil.copy2(ROOT/'logs/w04-reference-study-20261110/images'/name,file)
        rows.append(dict(id=f'R{len(rows)+1:02d}',source='wiki',kind='社区转存游戏图',title=item['title'],
            author='Honkai Impact 3rd Wiki（社区）',angle='完整轮廓图',label='鸣雷见全刃展示' if info['width']>1000 else '鸣雷见透明轮廓图（545×320）',
            url=info['descriptionurl'],original_url=info['url'],file=name,resolution=[info['width'],info['height']],
            sha256=hashlib.sha256(file.read_bytes()).hexdigest()))
    assert len(rows)==48 and len({r['sha256'] for r in rows})==48
    # 取样用原尺寸透明图；放大图仅供人眼核对，不能增加源图精度。
    original=Image.open(folder/'Seven_Thunders_of_Retribution_-_Narukami_(6).png')
    aligned=original.rotate(-31,resample=Image.Resampling.BICUBIC,expand=True);aligned=aligned.crop(aligned.getbbox())
    aligned.save(OUT/'轮廓取样源.png')
    for file in ['profile-grid.png','promo-crop.png']:shutil.copy2(LOG/file,OUT/file)
    manifest=dict(generated_at=datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds'),
        count=48,rotation_samples=30,other_video_frames=16,community_stills=2,sources=SOURCES,images=rows,
        identity='涤罪七雷·鸣雷见（超限），负责人明确选择；不混入基础鸣。',
        distinction='30张来自同一游戏转台的一轮连续角度，16张跨来源形态／尺寸辅助，2张社区转存图；不是48个独立拍摄机位。',
        modeling_source=dict(file='轮廓取样源.png',source_file='Seven_Thunders_of_Retribution_-_Narukami_(6).png',
            original_resolution=[545,320],aligned_resolution=list(aligned.size),rotation_degrees=-31,
            role='侧面轮廓、纹样位置和开口；深度由正反及端向转台约束后手工转译'),
        limitations=['转台总画面1080p不代表武器局部有1080p细节，已提供原帧便于核对。',
            '社区透明图只有545×320；不将放大插值宣称高清新细节。',
            '未找到公开的官方三视尺寸图；精确厚度、背面细纹与隐藏连接仍是参考转译。',
            '新增检索的三段视频中只有有用鸣雷见画面被收录；其他武器、加载页和纯龙镜头不凑数。'])
    for path in [OUT/'参考图清单.json',LOG/'reference-manifest.json']:
        path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n','utf8')
    cards=''.join(f'<article data-angle="{r["angle"]}" data-source="{r["source"]}"><a href="参考图/{r["file"]}" target="_blank"><img loading="lazy" src="参考图/{r["file"]}" alt="{escape(r["label"])}"></a><b>{r["id"]} · {escape(r["label"])}</b><p>{r["kind"]} · {r.get("seconds","静帧")} · {r["resolution"][0]}×{r["resolution"][1]}</p><a href="{r["url"]}" target="_blank">{escape(r["author"])} · 来源</a></article>' for r in rows)
    (OUT/'参考图总览.html').write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>涤罪七雷·鸣雷见 · 48张专属参考</title><style>:root{{color-scheme:dark}}body{{max-width:1600px;margin:30px auto;padding:0 22px;background:#161020;color:#ede5f7;font:15px/1.65 system-ui}}a{{color:#e2adff}}.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(350px,1fr));gap:16px}}article{{background:#281c35;padding:12px}}img{{width:100%;height:230px;object-fit:contain;background:#0d0b14}}p{{margin:7px 0}}select{{padding:9px}}[hidden]{{display:none}}.note{{padding:16px;border-left:3px solid #ad58dc;background:#291c39}}</style><a href="index.html">← 独立小样</a><h1>涤罪七雷·鸣雷见 · 专属参考</h1><p class="note">只收录负责人选定的超限形态。48张＝一轮转台30个角度采样＋16张跨来源形态／尺寸辅助＋2张社区图。30张转台不是30个相机，辅助图也不冒充细节特写。</p><p>新检索并核对了CrushyRushX、Marisa Honkai与升级展示；沿用舞亜的游戏转台作为正反面和端向主参考。社区透明图545×320只提供轮廓和纹样布局，放大不增加精度。</p><p>可筛选旋转视角、握持辅助、完整轮廓。点击原帧查看源尺寸，来源链接带时间点。</p><label>用途 <select id="angle"><option>全部</option>{''.join('<option>'+a+'</option>' for a in sorted({r['angle'] for r in rows}))}</select></label> <span id="count">48张</span><p><a href="参考图清单.json">来源清单</a> · <a href="profile-grid.png">带坐标轮廓</a> · <a href="promo-crop.png">非转台展示图局部</a></p><section class="grid">{cards}</section><script>angle.onchange=()=>{{let n=0;document.querySelectorAll('article').forEach(e=>{{e.hidden=angle.value!=='全部'&&e.dataset.angle!==angle.value;if(!e.hidden)n++;}});count.textContent=n+'张';}};</script></html>''','utf8')
    font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',16)
    for start in range(0,len(rows),12):
        canvas=Image.new('RGB',(1600,4*250),'#171020');draw=ImageDraw.Draw(canvas)
        for i,row in enumerate(rows[start:start+12]):
            im=Image.open(folder/row['file']).convert('RGB');im.thumbnail((400,218));x=i%4*400;y=i//4*250
            canvas.paste(im,(x+(400-im.width)//2,y));draw.text((x+5,y+220),f'{row["id"]} {row["label"]}',font=font,fill='white')
        canvas.save(OUT/f'参考拼图{start//12+1}.jpg',quality=92)
    print(json.dumps(dict(passed=True,count=48,rotation_samples=30,other_video_frames=16,community_stills=2)))


if __name__=='__main__':main()
