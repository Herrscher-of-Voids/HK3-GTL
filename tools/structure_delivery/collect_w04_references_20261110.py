# -*- coding: utf-8 -*-
"""整理实际查看的俱利伽罗与涤罪七雷原帧，保留来源和形态区别。"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta
from html import escape
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'deliveries/W04_俱利伽罗七雷_参考校准_B2_20261110'
LOG=ROOT/'logs/w04-reference-study-20261110'
CACHE=Path.home()/'.cache/hk3gtl-w04-reference-videos'
SOURCES={
    'guide':dict(video='Q0asaihK0VA',title='Herrscher of Thunder Tutorial Video',
        author='Honkai Impact 3rd',kind='官方教学',channel_id='UCko6H6LokKM__B03i5_vBQQ',
        use='俱利伽罗正侧背、白色长角、长颈叠甲、刃状翼爪与尾部；不是涤罪七雷的武器依据'),
    'player':dict(video='vCMehnpv8gE',title='崩坏3rd 5.8版本 新武器－裁决之键「涤罪七雷·鸣」',
        author='舞亜',kind='玩家游戏画面',use='游戏武器界面多角度旋转；分别标注鸣与鸣雷见；结尾辅助龙首和腹尾局部')}
GUIDE=[(128,'背侧骑乘与颈根','背面'),(130,'翼爪刃面与暗色翼膜','翼爪'),
    (132,'正面展开轮廓','正面'),(134,'正面垂翼与长颈','正面'),(136,'正面上举翼骨','正面'),
    (138,'背部肩甲与翼臂连接','背面'),(140,'前上方飞行轮廓','俯视'),(141,'长角与面甲','龙首'),
    (142,'正面白角红面甲和分节颈腹','龙首'),(143,'头颈转侧过渡','侧面'),
    (144,'前侧双翼爪轮廓','翼爪'),(146,'俯前方刃爪展开','俯视'),(148,'背部与肩翼俯视','背面'),
    (150,'侧后尾部和腹甲','尾腹'),(152,'侧后分节尾与前肢','尾腹'),(154,'胸腹和下方爪部','尾腹'),
    (156,'背上方翼根与尾缘','背面'),(158,'侧面吐息姿态','侧面'),(160,'前侧吐息与翼膜','侧面'),
    (166,'侧面长尾与完整翼爪','侧面')]
PLAYER=[(3,'鸣：基础形态全刃','武器·鸣'),(13,'鸣：刃面与黑色握柄','武器·鸣'),
    (24,'鸣：转侧轮廓','武器·鸣'),(68,'鸣雷见：角色装备比例','武器·鸣雷见'),
    (72,'鸣雷见：端向厚度','武器·鸣雷见'),(76,'鸣雷见：反侧弯刃','武器·鸣雷见'),
    (80,'鸣雷见：斜端向护手','武器·鸣雷见'),(84,'鸣雷见：正侧刃面','武器·鸣雷见'),
    (88,'鸣雷见：反面刃脊','武器·鸣雷见'),(92,'鸣雷见：斜侧厚度','武器·鸣雷见'),
    (100,'鸣雷见：弯刃与镂空护手','武器·鸣雷见'),(108,'鸣雷见：护手转侧','武器·鸣雷见'),
    (116,'鸣雷见：斜前握柄','武器·鸣雷见'),(124,'鸣雷见：端向对照','武器·鸣雷见'),
    (128,'鸣雷见：刃背与握柄连接','武器·鸣雷见'),(226,'龙首侧面：眼眶白角与红甲','龙首'),
    (227,'龙身正面：长颈与垂翼','正面'),(228,'下腹分节与收拢后爪','尾腹'),
    (230,'前侧翼爪与颈甲','翼爪')]


def main():
    folder=OUT/'参考图';folder.mkdir(parents=True,exist_ok=True)
    rows=[]
    for key,items in [('guide',GUIDE),('player',PLAYER)]:
        info=SOURCES[key]
        for seconds,label,angle in items:
            rows.append(dict(id=f'R{len(rows)+1:02d}',source=key,seconds=seconds,label=label,angle=angle,
                source_kind=info['kind'],source_title=info['title'],author=info['author'],
                url=f'https://www.youtube.com/watch?v={info["video"]}&t={seconds}s',file=f'{key}-{seconds:03d}.jpg'))
    def extract(row):
        target=folder/row['file'];movie=CACHE/(SOURCES[row['source']]['video']+'.mp4')
        assert movie.is_file(),movie
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-ss',str(row['seconds']),'-i',str(movie),
            '-frames:v','1','-q:v','2','-y',str(target)],check=True)
        with Image.open(target) as image:row['resolution']=list(image.size)
        row['sha256']=hashlib.sha256(target.read_bytes()).hexdigest()
        assert row['resolution'][0]>=1280 and row['resolution'][1]>=720
        return row
    rows=list(ThreadPoolExecutor(4).map(extract,rows))
    wiki=json.loads((LOG/'wiki-imageinfo.json').read_text('utf8'))['query']['pages']
    for item in wiki.values():
        image=item['imageinfo'][0]
        if image['width']<500:continue
        name=item['title'].replace('File:','').replace(' ','_');target=folder/name
        shutil.copy2(LOG/'images'/name,target)
        label='俱利伽罗前侧游戏图' if 'Kurikara' in name else ('鸣雷见' if 'Narukami' in name else '鸣')+'：社区转存展示图'
        rows.append(dict(id=f'R{len(rows)+1:02d}',source='wiki',source_kind='社区转存游戏图',
            source_title=item['title'],author='Honkai Impact 3rd Wiki（社区）',label=label,
            angle='龙首' if 'Kurikara' in name else '武器·鸣雷见' if 'Narukami' in name else '武器·鸣',
            url=image['descriptionurl'],original_url=image['url'],file=name,resolution=[image['width'],image['height']],
            sha256=hashlib.sha256(target.read_bytes()).hexdigest()))
    assert len(rows)==44 and len({r['sha256'] for r in rows})==len(rows)
    manifest=dict(generated_at=datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds'),
        count=len(rows),official_video_frames=len(GUIDE),player_video_frames=len(PLAYER),community_stills=5,
        distinction='44张可溯源画面，含不同角度、动作和局部；不等于44个独立机位。两张545×320社区图仅辅助，不用于精细轮廓。',
        sources=SOURCES,images=rows,weapon_identity=dict(base='涤罪七雷·鸣',pri_arm='涤罪七雷·鸣雷见',
            evidence='player-003、player-068及player-072等游戏界面；鸣雷神为技能名，不是武器本体名。'),
        limitations=['官方教学发布时间早于涤罪七雷；仅校准俱利伽罗，不能当作七雷武器证据。',
            '玩家视频是实际游戏画面，发布者不是官方；Wiki图片也不是本次直接取得的官方发布。',
            '背部、下腹部分被骑乘者和战斗特效遮挡；S形盘枢和工业连接姿态为W04场景转译，不宣称逐处复刻。',
            '罪人挽歌已检索，但未找到可用的俱利伽罗多角度内容，未加入图数。'])
    (OUT/'参考图清单.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n','utf8')
    (LOG/'reference-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n','utf8')
    cards=''.join(f'''<article data-kind="{r['source_kind']}" data-angle="{r['angle']}"><a href="参考图/{r['file']}" target="_blank"><img loading="lazy" src="参考图/{r['file']}" alt="{escape(r['label'])}"></a><b>{r['id']} · {escape(r['label'])}</b><p>{r['source_kind']} · {str(r.get('seconds',''))+'秒' if 'seconds' in r else '静帧'} · {r['resolution'][0]}×{r['resolution'][1]}</p><a href="{escape(r['url'])}" target="_blank">{escape(r['source_title'])} · {escape(r['author'])}</a></article>''' for r in rows)
    kinds=''.join(f'<option>{k}</option>' for k in ['官方教学','玩家游戏画面','社区转存游戏图'])
    angles=''.join(f'<option>{k}</option>' for k in sorted({r['angle'] for r in rows}))
    (OUT/'参考图总览.html').write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>俱利伽罗与涤罪七雷 · 44张参考</title><style>:root{{color-scheme:dark}}body{{background:#140e19;color:#eee4ec;font:15px/1.6 system-ui;max-width:1600px;margin:28px auto;padding:0 20px}}a{{color:#f79ab7}}.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:18px}}article{{padding:12px;background:#291622}}img{{width:100%;height:240px;object-fit:contain;background:black}}article p{{margin:4px 0}}select{{padding:8px;margin:8px}}.note{{border-left:3px solid #C93F63;padding:12px;background:#291622}}[hidden]{{display:none}}</style><a href="index.html">← B2候选</a><h1>俱利伽罗与涤罪七雷 · 图片校准</h1><p class="note">44张：20张官方教学原帧、19张玩家游戏原帧、5张社区转存图；覆盖正侧背、俯视、颈甲、翼爪、腹尾、刀面与端向。不同动作和局部不等于44个独立机位。点击原图查看，来源链接可核对时间点。</p><p>游戏界面显示：基础形态「涤罪七雷·鸣」，超限形态「涤罪七雷·鸣雷见」；「鸣雷神」为技能名。新版以超限形态的修长紫刃和镂空护手为依据，不能把2020年教学中使用的其他刀型混进来。</p><p>遮挡处仍有推定；盘枢长尾与工业连接是场景改编。两张545×320图片只作辅助，不冒充高清参考。</p><label>来源<select id="kind"><option>全部</option>{kinds}</select></label><label>部位<select id="angle"><option>全部</option>{angles}</select></label><span id="count">44张</span><p><a href="参考图清单.json">来源、时间点、分辨率与校验值</a></p><section class="grid">{cards}</section><script>function filter(){{let n=0;document.querySelectorAll('article').forEach(e=>{{e.hidden=(kind.value!=='全部'&&e.dataset.kind!==kind.value)||(angle.value!=='全部'&&e.dataset.angle!==angle.value);if(!e.hidden)n++;}});document.getElementById('count').textContent=n+'张';}}kind.onchange=filter;angle.onchange=filter;</script></html>''','utf8')
    font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',16)
    for name,selected in [('龙体参考',[r for r in rows if not r['angle'].startswith('武器')]),
        ('七雷参考',[r for r in rows if r['angle'].startswith('武器')])]:
        for start in range(0,len(selected),12):
            canvas=Image.new('RGB',(1440,750),'#20121c');draw=ImageDraw.Draw(canvas)
            for i,row in enumerate(selected[start:start+12]):
                im=Image.open(folder/row['file']).convert('RGB');im.thumbnail((360,216));x=i%4*360;y=i//4*250
                canvas.paste(im,(x+(360-im.width)//2,y));draw.text((x+5,y+218),f'{row["id"]} {row["label"]}',font=font,fill='white')
            canvas.save(OUT/f'{name}{start//12+1}.jpg',quality=92)
    print(json.dumps(dict(passed=True,total=len(rows),official_frames=20,player_frames=19,community_stills=5),ensure_ascii=False))


if __name__=='__main__':main()
