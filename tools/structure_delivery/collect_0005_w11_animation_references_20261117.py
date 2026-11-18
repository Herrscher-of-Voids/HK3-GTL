from datetime import datetime, timezone
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import hashlib
import json
import shutil
import subprocess


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/0005_W11_支配人偶多角度重塑_P1_20261117/references/video'
CACHE = Path('C:/Users/OWNER/.cache/hk3gtl-w11-reference-videos')
MAIN = 'n1rjfW-5HAE'
PICKS = [
    (MAIN, 17.5, '悬浮手掌', '极低仰视', '从下方看手掌、分节金指和带金边的筒状短袖口；手腕悬空。'),
    (MAIN, 27.5, '乌合之众本体', '左前低仰全身', '胸腹甲、前膝盾片和主臂金球肘；前景手指与本体分离。'),
    (MAIN, 35, '悬浮手掌', '掌心斜侧近景', '五指弯曲，指节为金色短圆柱，掌根有蓝灰甲和金色叶状边饰。'),
    (MAIN, 37.5, '悬浮手掌', '腕口背侧近景', '圆筒袖口与金色锯齿掌根，掌背朝外，袖口内面为黑色。'),
    (MAIN, 47.5, '乌合之众本体', '正面全身', '一对粗壮本体主臂向下，外圈独立悬浮多手；宽胸、窄腰、并列巨盾腿与向上尖肩。'),
    (MAIN, 54, '悬浮手掌', '手指上方俯视', '指间距和各节相对方向可见；焦点在地面，参考范围限于前景手指轮廓。'),
    (MAIN, 67.5, '乌合之众头盔', '正面近景', '中央额盔隆起成尖脊，两侧红眼内收，黑色眼窝延伸至脸侧，金色下脸有W形折线。'),
    (MAIN, 72.5, '普通支配人偶', '正面近景', '乳白面罩、黑色整条眼带、三叶结额纹，金色细长指节及细臂关节。'),
    (MAIN, 77.5, '普通支配人偶', '低仰前斜群像', '黑金伞裙、白色下身、细长四肢，周围人偶相互倾斜；只用于普通人偶比例。'),
    (MAIN, 82.5, '悬浮手掌', '掌背极近侧视', '蓝灰甲面有三条细长叶形凹纹，甲缘以金色甲片逐节咬合。'),
    (MAIN, 84, '悬浮手掌', '掌背正面近景', '指根圆轴、蓝灰掌背、拇指外张和金色分节长指，指端有圆孔状端面。'),
    (MAIN, 87.5, '乌合之众本体', '高位俯视上身', '头盔顶蓝灰平面与金色V框，胸甲上缘双V，肩根黑色大环、蓝灰上臂与金球肘。'),
    (MAIN, 88, '悬浮手掌', '弯指掌心近景', '五指屈曲与拇指对合，掌根金色叶片展开，金色各节之间保留黑色缝隙。'),
    (MAIN, 152.5, '乌合之众本体', '右前低仰胸甲', '胸部金色四瓣交叉纹、凸出的上胸甲、两侧金边黑孔、肩甲尖峰和头部侧形。'),
    (MAIN, 187.5, '普通支配人偶', '侧后斜俯视', '可见后脑金色壳、垂落侧发形甲片与裙装外缘，前方人偶的面罩仍可核对。'),
    (MAIN, 267.5, '乌合之众本体', '背部迎光轮廓', '两肩尖峰展开，双臂举高，背中央有金色短纹；景深模糊，范围限于轮廓。'),
    (MAIN, 317.5, '乌合之众头盔', '高位正面近景', '长V形鼻罩、两条狭长红眼，脸部两侧内收，前胸双V上缘托住小头；绿色为运行特效照明。'),
    ('a0YM0Wo2To4', 27, '早期普通支配人偶', '低位正前上身', '浅灰无发式面盔，金色窄眼、长颈、细臂球关节和分块腹甲；与动画女仆型分开记录。'),
    (MAIN, 41, '普通支配人偶', '面罩左侧近景', '口腔开口、前面罩断面、两侧金色包边和额前钻石纹压条；嘴内粉色细线单独记录为提线。'),
    (MAIN, 42, '普通支配人偶', '后脑上方近景', '后脑金色分瓣甲纹和两侧尖锥形发髻、圆形接缝节点，背景可见裙装与膝关节。'),
    (MAIN, 50, '普通支配人偶', '侧后上身近景', '近处人偶后脑与颈后白色皱褶，细臂白色肩关节、黑袖、金手、领口与胸前菱形白片。'),
    (MAIN, 51, '普通支配人偶', '面具正面极近景', '黑眼带上缘有阶梯状边界、面罩外缘为金饰包边和尖齿，嘴部张开；前景手遮住中央部分。'),
    (MAIN, 78.5, '普通支配人偶', '人群掌心与头冠斜视', '金色小手掌展开可看掌内分片和指节连接，头顶甲壳接缝、双侧金冠和金色武器外框同场可辨。'),
    (MAIN, 81.5, '悬浮手掌', '指根掌面斜侧近景', '掌面黑蓝大块与指根金色旋转轴，三节指骨长度和屈曲方向，金边袖口与本体主臂分开可见。'),
    ('a0YM0Wo2To4', 28, '早期普通支配人偶', '后颈及肩背近景', '细颈轴嵌在后脑下部圆孔，肩背以浅灰分片甲包围；红色过渡照明与运动模糊只用于结构方向。'),
]


def main():
    (OUT / 'frames').mkdir(parents=True, exist_ok=True)
    (OUT / 'thumbnails').mkdir(exist_ok=True)
    sources = {}
    for vid in [MAIN, 'zCmw1RgghEI', 'a0YM0Wo2To4']:
        info = json.loads((CACHE / f'{vid}.info.json').read_text('utf8'))
        sources[vid] = {k: info[k] for k in ['title', 'channel', 'channel_id', 'upload_date', 'duration']}
        sources[vid]['url'] = f'https://www.youtube.com/watch?v={vid}'
    refs = []
    for i, (vid, seconds, subject, angle, note) in enumerate(PICKS, 1):
        rid = f'V{i:02d}'
        p = OUT / 'frames' / f'{rid}-{vid}-{seconds:g}s.jpg'
        scan = OUT / 'scan/detail' / (f'{seconds:g}s.jpg' if vid == MAIN else f'pv-{seconds:g}s.jpg')
        if scan.exists():
            shutil.copy2(scan, p)
        else:
            subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-ss', str(seconds), '-i', str(CACHE / f'{vid}.mp4'), '-frames:v', '1', '-q:v', '2', '-y', str(p)], check=True)
        im = Image.open(p).convert('RGB')
        resolution = list(im.size)
        im.thumbnail((640, 360), Image.Resampling.LANCZOS)
        thumb = OUT / 'thumbnails' / f'{rid}.jpg'
        im.save(thumb, quality=91)
        refs.append(dict(id=rid, subject=subject, angle=angle, view=angle, note=note, visible_details=note,
            source_title=sources[vid]['title'], source_url=sources[vid]['url'] + f'&t={seconds:g}s',
            source_nature='官方动画原帧' if vid == MAIN else '官方版本预告原帧',
            title=f'{subject} · {angle}', publisher=sources[vid]['channel'], authority='崩坏3官方频道',
            observations=[note], width=resolution[0], height=resolution[1],
            video_id=vid, seconds=seconds, time_seconds=seconds,
            file=f'frames/{p.name}', thumbnail=f'thumbnails/{rid}.jpg', resolution=resolution,
            sha256=hashlib.sha256(p.read_bytes()).hexdigest(), reviewed=True))
    findings = [
        '巨型本体为一对粗主臂，外圈多只悬浮手掌各自带短袖口。可见镜头未显示这些悬浮手连接到连续六臂肩根。',
        '胸甲为宽大倒梯形甲体，前胸四瓣交叉金纹，上方两瓣呈眼眶形；头相对于胸甲很小，金色尖脊额盔与红眼是强识别特征。',
        '主臂金色球肘带黑孔，前臂有向下尖出的蓝灰甲片；前腿为两个并列长盾甲，上沿三圆孔呈三角分布，下沿收尖。',
        '肩甲先向外展开，再向上形成长尖，肩根保留黑色环孔与金边。',
        '悬浮手掌采用金色分节指与蓝灰掌背，掌根金色叶饰围成花形，掌背有叶形细纹；掌与指之间的黑缝应在方块模型中保留。',
        '普通支配人偶存在版本和表现差异：4.8预告为浅灰无发式细身，薪炎永燃为浅色面罩、黑眼带、金发状甲与黑金裙。巨型本体与普通人偶分别建模。',
        '原作巨型本体主色为蓝灰、金、黑与红眼；W11负责人指定黑白金红配色属于项目工业改编，应在造型清单单列。',
    ]
    manifest = dict(created_at=datetime.now(timezone.utc).isoformat(), count=len(refs),
        counting='只计25张独立选取原帧；扫描联系图、重复帧、缩略图与原图裁切不重复计数。部分同一构件有多个可判读视角，不宣称25个环绕相机角。',
        sources=sources, references=refs, findings=findings,
        excluded=[dict(video_id='zCmw1RgghEI', seconds=1, reason='与薪炎永燃17.5秒低仰悬手镜头重复，只作交叉核对。'),
                  dict(video_id='zCmw1RgghEI', seconds=12, reason='正面全形参考已由薪炎永燃47.5秒覆盖；teaser扫描原图保留，未重复计入。'),
                  dict(video_id=MAIN, seconds=68.5, reason='与67.5秒相同机位和造型，仅火光变化。'),
                  dict(video_id=MAIN, seconds=153.5, reason='与152.5秒相同机位，未增加可判读细节。'),
                  dict(video_id=MAIN, seconds=85, reason='与84秒相同掌背机位，仅动作连续变化。')],
        missing_views=['巨型本体完整无遮挡侧立面', '背面表面近图', '全身无遮挡正交俯视', '悬浮手腕内部机构'],
        geometry_notes=dict(main_arm_pairs=1, floating_hands='外圈多个独立手掌，数量随镜头与遮挡变化；47.5秒可分辨9只。',
            body_proportion='47.5秒图：头部宽约100像素，胸甲宽约300像素，双腿上盾宽合计约360像素；此为透视图相对值。'))
    (OUT / 'references.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', 'utf8')
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 18)
    for start in range(0, len(refs), 9):
        sheet = Image.new('RGB', (1920, 3 * 399), '#111319')
        draw = ImageDraw.Draw(sheet)
        for i, ref in enumerate(refs[start:start + 9]):
            im = Image.open(OUT / ref['thumbnail'])
            x, y = i % 3 * 640, i // 3 * 399
            sheet.paste(im, (x, y))
            draw.text((x + 8, y + 362), f"{ref['id']}  {ref['seconds']:g}s · {ref['subject']} · {ref['angle']}", font=font, fill='#e4d8c3')
        sheet.save(OUT / f'contact-{start // 9 + 1:02d}.jpg', quality=92)
    print(json.dumps(dict(count=len(refs), manifest=str(OUT / 'references.json')), ensure_ascii=False))


if __name__ == '__main__':
    main()
