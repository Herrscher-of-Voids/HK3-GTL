# -*- coding: utf-8 -*-
"""按来源与时间点整理19C参考，区分官方画面和二创改色模型。"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta
from html import escape
import hashlib
import json
from pathlib import Path
import subprocess
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[2]
LOG=ROOT/'logs/w02-19c-reference-study-20261110'
OUT=ROOT/'deliveries/W02_理之律者19C_多视角重制_V2_20261110'
CACHE=Path.home()/'.cache/hk3gtl-19c-videos'
SOURCES={
    'cg':dict(video='N-VNG8vW5RA',title='Cyberangel: ZERO Exception',author='Honkai Impact 3rd',kind='官方动画',
              use='普通理律19C轮廓、白蓝橙配色、轮组和机械手；摩托变形画面只核对结构来源'),
    'guide':dict(video='sHqseNq6pdI',title='Herrscher of Reason Guide',author='Honkai Impact 3rd',kind='官方教学',
                 use='普通理律游戏模型、背部和战斗姿态；金色强化武装不作为静态默认配色'),
    'model':dict(video='Fz_EvIA070A',title='Project Bunny Animation and Physics Demo',author='Nibor',kind='二创辅助',
                 use='作者声明重建并重贴图的19C；只辅助观察背、侧、俯仰结构，不采用其红色重贴图或舞蹈姿态')}
CG=[(105,'胸部橙色罩体','胸甲'),(106,'展开机械手掌','机械手'),(107,'装甲构造过程','机械手'),
    (115,'正面展开轮廓','正面'),(124,'前臂与机械手','机械手'),(126,'前侧俯视','俯视'),
    (154,'侧轮和外装甲','轮组'),(155,'低视角侧面轮组','仰视'),(158,'侧后约束结构','背面'),
    (170,'罩体正面特写','胸甲'),(175,'轮胎与散热槽','轮组'),(246,'侧面机械手连接','机械手')]
GUIDE=[(48,'右后侧构造姿态','背面'),(52,'侧后机体','侧面'),(58,'后侧展开','背面'),(62,'侧面轮廓','侧面'),
       (76,'背部整体','背面'),(78,'背部轴系','背面'),(90,'前侧武装状态','正面'),(94,'侧后武装状态','侧面'),
       (102,'背部轮组','背面'),(104,'前侧下机体','正面'),(110,'前侧展开轮廓','正面'),(112,'侧面曲臂','侧面'),
       (120,'背部及节链','背面'),(122,'右侧轮组与节链','侧面'),(138,'后侧轴系','背面'),(140,'背部双浮游模块','背面'),
       (148,'侧后伸臂','侧面'),(150,'侧面轮组','轮组'),(208,'正面完整机体','正面'),(216,'侧面完整机体','侧面')]
MODEL=[(7,'背侧曲臂','背面'),(9,'后侧轮组','背面'),(11,'前左侧展开','侧面'),(13,'正面下垂双臂','正面'),
       (15,'前侧静态轮廓','正面'),(17,'前左侧轮组','轮组'),(19,'前方仰起双臂','仰视'),(21,'下方看掌及轮胎','仰视'),
       (23,'后侧肩部','背面'),(25,'前侧曲臂','侧面'),(27,'正面轮胎内侧','轮组'),(29,'后上侧浮游模块','俯视'),
       (31,'后侧轮胎底纹','背面'),(33,'上侧双浮游模块','俯视'),(35,'左侧轮组与节链','侧面'),(37,'前下方观察','仰视'),
       (39,'斜前方关节','侧面'),(41,'左上侧轮廓','俯视'),(43,'正面轮廓','正面'),(45,'侧前方前臂','侧面'),
       (47,'侧方双浮游模块','侧面'),(49,'后下侧掌部','仰视'),(51,'正面下垂双臂','正面'),(53,'上方肩部模块','俯视'),
       (55,'左后侧手臂','背面'),(61,'正上方模块轮廓','俯视'),(65,'后侧节链','背面'),(73,'前上方双臂','俯视')]


def main():
    folder=OUT/'参考图';folder.mkdir(parents=True,exist_ok=True);LOG.mkdir(exist_ok=True)
    rows=[]
    for source,items in [('cg',CG),('guide',GUIDE),('model',MODEL)]:
        for seconds,label,angle in items:
            info=SOURCES[source]
            rows.append(dict(id=f'R{len(rows)+1:02d}',source=source,seconds=seconds,label=label,angle=angle,
                             source_kind=info['kind'],source_title=info['title'],author=info['author'],
                             url=f'https://www.youtube.com/watch?v={info["video"]}&t={seconds}s',
                             file=f'{source}-{seconds:03d}.jpg'))
    assert len(rows)==60 and len({(r['source'],r['seconds']) for r in rows})==60
    def extract(row):
        movie=CACHE/(SOURCES[row['source']]['video']+'.mp4')
        assert movie.is_file(),movie
        target=folder/row['file']
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-ss',str(row['seconds']),'-i',str(movie),
                        '-frames:v','1','-q:v','2','-y',str(target)],check=True)
        with Image.open(target) as image:row['resolution']=list(image.size)
        row['sha256']=hashlib.sha256(target.read_bytes()).hexdigest()
        assert min(row['resolution'])>=1080
        return row
    rows=list(ThreadPoolExecutor(4).map(extract,rows))
    manifest=dict(generated_at=datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds'),
        count=60,official_count=32,fan_assistance_count=28,source_videos=3,
        distinction='60张带时间点的不同画面，不宣称60个独立拍摄机位；包含不同角度、动作和局部特写。',
        palette_identity='W02 HBV构造蓝#428DFF，白装甲、深色内构；橙色罩体小面积保留',
        sources=SOURCES,images=rows,
        limitations=['二创作者明确重贴图，其红色不能替代官方配色。','没有将摩托变形、武装人偶或真理之律者作为19C默认造型。',
                     '动画和游戏帧有姿态、透视、光照差异；以多帧相互核对，不能把单帧遮挡当成不存在。'])
    (OUT/'参考图清单.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n','utf8')
    (LOG/'reference-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n','utf8')
    cards=''.join(f'''<article data-kind="{r['source_kind']}" data-angle="{r['angle']}"><a href="参考图/{r['file']}" target="_blank"><img loading="lazy" src="参考图/{r['file']}" alt="{escape(r['label'])}"></a><b>{r['id']} · {escape(r['label'])}</b><p>{r['source_kind']} · {r['seconds']}秒 · {r['resolution'][0]}×{r['resolution'][1]}</p><a href="{r['url']}" target="_blank">{escape(r['source_title'])} · {escape(r['author'])}</a></article>''' for r in rows)
    angles=sorted({r['angle'] for r in rows})
    options=''.join(f'<option>{a}</option>' for a in angles)
    (OUT/'参考图总览.html').write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>重装小兔19C · 60张多视角参考</title><style>:root{{color-scheme:dark}}body{{background:#0b1624;color:#e5efff;font:15px/1.6 system-ui;max-width:1600px;margin:28px auto;padding:0 20px}}a{{color:#8bb9ff}}.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:18px}}article{{padding:12px;background:#12253a}}img{{width:100%;height:240px;object-fit:contain;background:black}}article p{{margin:4px 0}}select{{padding:8px;margin:8px}}.note{{border-left:3px solid #428DFF;padding:12px;background:#152941}}[hidden]{{display:none}}</style><a href="index.html">← 新版小样</a><h1>普通理之律者 · 重装小兔19C · 多视角参考</h1><p class="note">共60张：32张官方动画／教学原帧，28张二创模型辅助原帧，来自3段视频。覆盖正面、背面、侧面、俯仰、轮组、胸甲和机械手。60张不等于60个独立机位；已保留不同姿态和局部特写。点击图片看原尺寸，点击来源核对对应时间点。</p><p>二创模型作者声明重建、重贴图：只辅助结构，不能照抄红色材质。普通理律19C与真理之律者、武装人偶、19C同名武器分开核对。</p><label>来源<select id="kind"><option>全部</option><option>官方动画</option><option>官方教学</option><option>二创辅助</option></select></label><label>角度／部位<select id="angle"><option>全部</option>{options}</select></label><span id="count">60张</span><p><a href="参考图清单.json">来源、时间点、分辨率和文件校验值</a></p><section class="grid">{cards}</section><script>function filter(){{let count=0;document.querySelectorAll('article').forEach(e=>{{e.hidden=(kind.value!=='全部'&&e.dataset.kind!==kind.value)||(angle.value!=='全部'&&e.dataset.angle!==angle.value);if(!e.hidden)count++;}});document.getElementById('count').textContent=count+'张';}}document.getElementById('kind').onchange=filter;document.getElementById('angle').onchange=filter;</script></html>''','utf8')
    font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',16)
    for category in ['官方','二创']:
        selected=[r for r in rows if r['source_kind'].startswith(category)]
        for batch in range((len(selected)+11)//12):
            tiles=selected[batch*12:(batch+1)*12];canvas=Image.new('RGB',(1440,3*250),'#122030');draw=ImageDraw.Draw(canvas)
            for i,row in enumerate(tiles):
                im=Image.open(folder/row['file']);im.thumbnail((360,216));x=i%4*360;y=i//4*250
                canvas.paste(im,(x+(360-im.width)//2,y));draw.text((x+5,y+218),f'{row["id"]} {row["label"]}',font=font,fill='white')
            canvas.save(OUT/f'{category}参考拼图{batch+1}.jpg',quality=92)
    print(json.dumps(dict(passed=True,total=len(rows),official=32,fan_assistance=28,source_videos=3),ensure_ascii=False))


if __name__=='__main__':main()
