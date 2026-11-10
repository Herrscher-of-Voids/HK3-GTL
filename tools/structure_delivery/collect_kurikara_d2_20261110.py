# -*- coding: utf-8 -*-
"""收集作者公开三维展示与新增官方原帧，保留来源层级及旧参考。"""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from html import escape
import hashlib,json,shutil,subprocess,urllib.request
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'deliveries/W04_俱利伽罗_腿爪与叠甲细化_D2_20261110'
LOG=ROOT/'logs/w04-kurikara-d2-20261110'
OLD=ROOT/'deliveries/W04_俱利伽罗_独立静态小样_D1_20261110'
ART='https://www.artstation.com/artwork/n0bPo1'
ASSETS=[('a','917/920','01'),('b','917/941','02'),('a','917/952','03'),
    ('a','917/962','04'),('b','917/967','05'),('b','917/977','06'),
    ('b','917/989','07'),('b','917/997','08'),('a','918/016','09'),
    ('b','918/023','10'),('a','918/042','11'),('a','918/058','12'),
    ('a','918/080','13'),('a','918/090','screenshot-2023-05-19-222313')]
LABELS=['写实头颈肖像','全身斜前','后侧展翼','高位侧面','三维作品正面','正面线框',
    '三维作品背面','背面线框','三维作品侧面','侧面线框','低位前侧','低位后侧','材质通道展示','作者使用的游戏原型截图']


def main():
    folder=OUT/'参考图';folder.mkdir(parents=True,exist_ok=True);LOG.mkdir(exist_ok=True)
    manifest=json.loads((OLD/'参考图清单.json').read_text('utf8'));rows=manifest['images']
    for row in rows:shutil.copy2(OLD/'参考图'/row['file'],folder/row['file'])
    for i,(host,key,suffix) in enumerate(ASSETS):
        original=f'https://cdn{host}.artstation.com/p/assets/images/images/067/{key}/large/qst_tc-'+('kurikara-' if i<13 else '')+suffix+'.jpg'
        rows.append(dict(id=f'R{len(rows)+1:02d}',source='artstation',author='Terence Chong',title='Kurikara',
            kind='玩家三维作品（写实改编）' if i<13 else '玩家转存游戏原图',angle='三维作品' if i<13 else '正面',
            label=LABELS[i],url=ART,original_url=original,file=f'artstation-{i+1:02d}.jpg',
            limitation='写实再创作，只辅助立体体积；不得当成游戏原模或改变原版龙的解剖。' if i<13 else '作者展示的游戏参考图，不属于其三维再创作。'))
    def download(row):
        path=folder/row['file']
        if not path.exists():
            req=urllib.request.Request(row['original_url'],headers={'User-Agent':'Mozilla/5.0'})
            path.write_bytes(urllib.request.urlopen(req,timeout=35).read())
        with Image.open(path) as im:row['resolution']=list(im.size)
        row['sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
    list(ThreadPoolExecutor(4).map(download,rows[43:]))
    # 官方短片补充完整龙姿态，具体时间点由场景接触表核对后加入。
    extra=LOG/'selected-official-frames.json'
    if extra.exists():
        for seconds,label,angle in json.loads(extra.read_text('utf8')):
            path=folder/f'fallen-{seconds:05.1f}.jpg'
            if not path.exists():subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-ss',str(seconds),'-i',
                str(Path.home()/'.cache/hk3gtl-w04-reference-videos/GkphEuqdyYA.mp4'),'-frames:v','1','-q:v','2','-y',str(path)],check=True)
            with Image.open(path) as im:resolution=list(im.size)
            rows.append(dict(id=f'R{len(rows)+1:02d}',source='fallen',author='Honkai Impact 3rd',
                title='Animated Short [Lament of the Fallen]',kind='官方动画原帧',angle=angle,label=label,
                file=path.name,url=f'https://www.youtube.com/watch?v=GkphEuqdyYA&t={seconds}s',seconds=seconds,
                resolution=resolution,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                limitation='动画镜头用于整体姿态与体积，游戏常态细节仍以官方教学和游戏原帧为主。'))
    assert len({r['sha256'] for r in rows})==len(rows)
    manifest.update(count=len(rows),images=rows,old_reference_count=43,added_reference_count=len(rows)-43,
        fan_model_images=13,fan_game_stills=1,official_model_status='已查官方5.2／6.4配布页及雷律包目录，未确认龙体公开模型；不能据此断言不存在。',
        fan_model_status='已确认Terence Chong公开三维作品及线框展示，当前页面未找到模型源文件下载。',
        official_model_pages=['https://www.bilibili.com/blackboard/dynamic/167352','https://www.bilibili.com/blackboard/dynamic/311367'],
        limitations=['图片数量包含同镜头相邻动作，不代表独立机位。','玩家写实作品只作立体辅助；未使用作者网格生成体素。'])
    (OUT/'参考图清单.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n','utf8')
    shutil.copy2(OUT/'参考图清单.json',LOG/'reference-manifest.json')
    for file in ['参考_龙首正面.jpg','参考_翼爪.jpg','参考_后足.jpg','参考_尾腹.jpg']:shutil.copy2(OLD/file,OUT/file)
    kinds=sorted({r['kind'] for r in rows});angles=sorted({r['angle'] for r in rows})
    options=lambda items:'<option>全部</option>'+''.join('<option>'+escape(v)+'</option>' for v in items)
    cards=''.join(f'<article data-kind="{escape(r["kind"])}" data-angle="{escape(r["angle"])}"><img loading="lazy" src="参考图/{r["file"]}" alt="{escape(r["label"])}"><p>{r["id"]} · {escape(r["label"])}<br>{escape(r["kind"])} · {escape(r["author"])}<br><a href="{escape(r["url"])}">查看来源</a></p></article>' for r in rows)
    (OUT/'参考图总览.html').write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>俱利伽罗D2参考核对</title><style>:root{{color-scheme:dark}}body{{background:#15131b;color:#eee5eb;font:16px/1.7 system-ui;margin:24px}}a{{color:#eea4b8}}main{{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:16px}}article{{background:#271c28;padding:10px}}img{{width:100%;height:250px;object-fit:contain}}select{{padding:8px;margin:8px}}</style><a href="index.html">← D2预览</a><h1>{len(rows)}张分源参考</h1><p>新增{len(rows)-43}张。玩家写实三维作品只校准立体体积，原版细节以游戏及官方画面为主。未取得龙体源模型，不宣称直接体素化官方网格。</p><p><a href="{ART}">Terence Chong：三维作品、正侧背面和线框</a> · <a href="参考图清单.json">来源清单</a></p><label>来源<select id="kind">{options(kinds)}</select></label><label>角度<select id="angle">{options(angles)}</select></label><main>{cards}</main><script>function filter(){{document.querySelectorAll('article').forEach(e=>e.hidden=!((kind.value==='全部'||e.dataset.kind===kind.value)&&(angle.value==='全部'||e.dataset.angle===angle.value)))}}kind.onchange=angle.onchange=filter;</script></html>''','utf8')
    font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',17)
    canvas=Image.new('RGB',(1600,1200),'#15131b');draw=ImageDraw.Draw(canvas)
    for i,row in enumerate(rows[43:57]):
        image=Image.open(folder/row['file']).convert('RGB');image.thumbnail((390,250));x=i%4*400;y=i//4*300
        canvas.paste(image,(x+(400-image.width)//2,y));draw.text((x+8,y+255),row['label'],font=font,fill='white')
    canvas.save(OUT/'新增三维参考接触表.jpg',quality=92)
    print(json.dumps(dict(count=len(rows),added=len(rows)-43,fan_model_images=13),ensure_ascii=False))


if __name__=='__main__':main()
