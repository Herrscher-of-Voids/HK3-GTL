# -*- coding: utf-8 -*-
"""俱利伽罗专属多视角图集；动作、相邻原帧与派生裁图分别标注。"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone,timedelta
from html import escape
from pathlib import Path
import hashlib,json,shutil,subprocess
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'deliveries/W04_俱利伽罗_独立静态小样_D1_20261110'
LOG=ROOT/'logs/w04-kurikara-d1-20261110'
CACHE=Path.home()/'.cache/hk3gtl-w04-reference-videos'
SOURCES={
    'guide':dict(video='Q0asaihK0VA',author='Honkai Impact 3rd',kind='官方教学原帧',
        title='Herrscher of Thunder Tutorial Video',channel_id='UCko6H6LokKM__B03i5_vBQQ'),
    'player':dict(video='vCMehnpv8gE',author='舞亜',kind='玩家游戏原帧',
        title='崩坏3rd 5.8版本 新武器－裁决之键「涤罪七雷·鸣」')}
GUIDE=[(128,'背上骑乘与肩颈','背面'),(129,'翼根和背脊过渡','背面'),(130,'红色翼刃和白光嵌片','翼爪'),
    (131,'翼膜与前翼刃连接','翼爪'),(132,'正面平展轮廓','正面'),(133,'正面收翼过渡','正面'),
    (134,'正面垂翼、细尾和长颈','正面'),(135,'正面抬翼过渡','正面'),(136,'上举翼骨轮廓','正面'),
    (138,'肩背装甲与翼根','背面'),
    (140,'前上方展开轮廓','俯视'),(140.5,'前上方长角与翼臂','俯视'),(141,'白角、红面甲与肩甲','龙首'),
    (141.5,'龙首转正过渡','龙首'),(142,'白色长角、V形面甲和颈腹','龙首'),(142.5,'龙首与胸前甲','龙首'),
    (143,'头颈转侧','侧面'),(143.5,'头颈侧面和翼爪姿态','侧面'),(144,'前侧双翼刃展开','翼爪'),
    (144.5,'前侧翼爪错层','翼爪'),(145,'前侧颈甲与翼爪','侧面'),(146,'上方翼爪和背部','俯视'),
    (147,'肩翼俯视过渡','俯视'),(148,'后上方尾脊和翼膜','背面'),(149,'背侧膜与尾','背面'),
    (150,'侧后尾部与收拢后足','尾腹'),(151,'尾脊白刺和后足','尾腹'),(152,'下腹与后爪','尾腹'),
    (153,'侧后尾节过渡','尾腹'),(154,'胸腹和后足','尾腹'),(156,'背上方翼根与尾缘','背面'),
    (158,'侧面吐息下的头身比例','侧面'),(160,'前侧翼刃厚度','翼爪'),(166,'侧面完整长尾','侧面')]
PLAYER=[(226,'侧头颊环与红甲','龙首'),
    (227,'悬停正面长颈与垂翼','正面'),(227.4,'悬停腹部与尾根','尾腹'),(228,'后足、骨白腹纹和红爪','尾腹'),
    (229,'正面头甲（部分遮挡）','龙首'),(230,'翼爪与颈甲正侧','翼爪'),
    (230.5,'翼刃细节和肩部','翼爪'),(231,'展开姿态比例辅助','正面')]


def main():
    folder=OUT/'参考图';folder.mkdir(parents=True,exist_ok=True);LOG.mkdir(exist_ok=True)
    rows=[]
    for key,items in [('guide',GUIDE),('player',PLAYER)]:
        for seconds,label,angle in items:
            info=SOURCES[key]
            rows.append(dict(id=f'R{len(rows)+1:02d}',source=key,seconds=seconds,label=label,angle=angle,
                kind=info['kind'],author=info['author'],title=info['title'],file=f'{key}-{seconds:05.1f}.jpg',
                url=f'https://www.youtube.com/watch?v={info["video"]}&t={seconds}s'))
    def extract(row):
        target=folder/row['file']
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-ss',str(row['seconds']),'-i',
            str(CACHE/(SOURCES[row['source']]['video']+'.mp4')),'-frames:v','1','-q:v','2','-y',str(target)],check=True)
        with Image.open(target) as im:row['resolution']=list(im.size)
        row['sha256']=hashlib.sha256(target.read_bytes()).hexdigest();return row
    rows=list(ThreadPoolExecutor(4).map(extract,rows))
    prior=ROOT/'logs/w04-reference-study-20261110'
    wiki=json.loads((prior/'wiki-imageinfo.json').read_text('utf8'))
    item=next(p for p in wiki['query']['pages'].values() if 'Kurikara_(Profile)' in p['title'].replace(' ','_'))
    info=item['imageinfo'][0];name='Kurikara_(Profile).jpg';shutil.copy2(prior/'images'/name,folder/name)
    rows.append(dict(id=f'R{len(rows)+1:02d}',source='wiki',kind='社区转存游戏图',angle='正面',label='完整前侧翼爪与颈腹',
        author='Honkai Impact 3rd Wiki（社区）',title=item['title'],file=name,url=info['descriptionurl'],
        original_url=info['url'],resolution=[info['width'],info['height']],sha256=hashlib.sha256((folder/name).read_bytes()).hexdigest()))
    assert len(rows)==43 and len(set(r['sha256'] for r in rows))==43
    font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',16)
    for start in range(0,len(rows),12):
        canvas=Image.new('RGB',(1600,1000),'#16121c');draw=ImageDraw.Draw(canvas)
        for i,row in enumerate(rows[start:start+12]):
            im=Image.open(folder/row['file']).convert('RGB');im.thumbnail((400,218));x=i%4*400;y=i//4*250
            canvas.paste(im,(x+(400-im.width)//2,y));draw.text((x+5,y+220),f'{row["id"]} {row["label"]}',font=font,fill='white')
        canvas.save(OUT/f'参考拼图{start//12+1}.jpg',quality=92)
    crops=[]
    for source,box,name,label in [('guide-142.0.jpg',(555,0,1130,845),'参考_龙首正面.jpg','龙首正面：长角与V形面甲'),
        ('guide-144.0.jpg',(1010,180,1920,1050),'参考_翼爪.jpg','翼爪：宽刃与白色嵌片'),
        ('guide-150.0.jpg',(250,80,1230,1050),'参考_尾腹.jpg','尾腹：白刺、细尾和后足'),
        ('player-228.0.jpg',(600,0,1420,1000),'参考_后足.jpg','后足：分段关节和红爪')]:
        with Image.open(folder/source) as im:im.crop(box).save(OUT/name,quality=94)
        crops.append(dict(source=source,bounds=box,file=name,label=label,derived=True,counted_as_independent_reference=False))
    manifest=dict(generated_at=datetime.now(timezone(timedelta(hours=-5))).isoformat(timespec='seconds'),count=43,
        official_frames=34,player_frames=8,community_stills=1,sources=SOURCES,images=rows,detail_crops=crops,
        excluded_frames=['guide-137.0（转场太暗）','guide-139.0（角色镜头）','player-226.3（角色镜头）','player-226.6（角色镜头）','player-228.4（后足已离开画面）'],
        distinction='34张官方教学原帧、8张玩家游戏原帧、1张社区转存图；含同镜头相邻动作，不是43个独立机位。派生局部裁图不另计数。',
        limitations=['没有官方三视尺寸图，精确比例、底面遮挡及背部连接仍需核对。',
            '采用双翼前肢＋一对后足的悬停姿态；不带B2场景额外扣环前爪。',
            '玩家画面受武器光效遮挡；红白翼刃与白角主要以官方教学的常态画面校准。',
            '无骑乘者、吐息束、工业环与机械锁链；该小样只制作龙本体。'])
    for path in [OUT/'参考图清单.json',LOG/'reference-manifest.json']:
        path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n','utf8')
    cards=''.join(f'<article data-angle="{r["angle"]}" data-kind="{r["kind"]}"><a href="参考图/{r["file"]}" target="_blank"><img loading="lazy" src="参考图/{r["file"]}" alt="{escape(r["label"])}"></a><b>{r["id"]} · {escape(r["label"])}</b><p>{r["kind"]} · {r.get("seconds","静帧")} · {r["resolution"][0]}×{r["resolution"][1]}</p><a href="{r["url"]}" target="_blank">{escape(r["author"])} · 来源</a></article>' for r in rows)
    page=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>俱利伽罗 · 43张专属参考</title><style>:root{{color-scheme:dark}}body{{max-width:1600px;margin:28px auto;padding:0 22px;background:#16121c;color:#ede6ef;font:15px/1.7 system-ui}}a{{color:#ed9aaa}}.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(350px,1fr));gap:16px}}article{{background:#281b25;padding:12px}}img{{width:100%;height:230px;object-fit:contain;background:#100b12}}p{{margin:7px 0}}select{{padding:8px}}[hidden]{{display:none}}.note{{padding:16px;border-left:3px solid #C93F63;background:#2a1721}}</style><a href="index.html">← 俱利伽罗独立小样</a><h1>俱利伽罗 · 43张专属参考</h1><p class="note">{manifest['distinction']}</p><p>只参考雷之律者的俱利伽罗。白角、V形红面甲、暗灰分节颈腹、刃状翼爪、细尾与收拢后足均可分组核对。战斗白光不等于装甲整体白色，骑乘者的紫发也不属于龙本体。已剔除5张转场或以角色为主的画面。</p><label>部位<select id="angle"><option>全部</option>{''.join('<option>'+a+'</option>' for a in sorted({r['angle'] for r in rows}))}</select></label> <label>来源<select id="kind"><option>全部</option>{''.join('<option>'+a+'</option>' for a in sorted({r['kind'] for r in rows}))}</select></label> <span id="count">43张</span><p><a href="参考图清单.json">来源、原始尺寸、时间点与哈希</a></p><section class="grid">{cards}</section><script>function filter(){{let n=0;document.querySelectorAll('article').forEach(e=>{{e.hidden=(angle.value!=='全部'&&e.dataset.angle!==angle.value)||(kind.value!=='全部'&&e.dataset.kind!==kind.value);if(!e.hidden)n++;}});count.textContent=n+'张';}}angle.onchange=filter;kind.onchange=filter;</script></html>'''
    (OUT/'参考图总览.html').write_text(page,'utf8')
    print(json.dumps(dict(passed=True,count=43,official=34,player=8,community=1)))


if __name__=='__main__':main()
