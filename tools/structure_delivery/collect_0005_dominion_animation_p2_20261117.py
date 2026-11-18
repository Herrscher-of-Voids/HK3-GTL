from pathlib import Path
from datetime import datetime, timezone
from PIL import Image, ImageDraw, ImageFont
import cv2
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/0005_乌合之众_原作像素重建_P2_20261117/references/animation'
CACHE = Path('C:/Users/OWNER/.cache/hk3gtl-w11-reference-videos')
VIDEO = 'n1rjfW-5HAE'
WINDOWS = [
    (7, 9, .4, '开场悬浮手', '仰视暗部轮廓'),
    (16, 19, .4, '悬浮手', '极低仰视掌心与腕口'),
    (24, 29, .4, '本体胸腿', '低仰三分之四全体'),
    (34, 38, .4, '悬浮手与胸甲', '掌心斜侧、胸肩近景、筒腕后口'),
    (44, 49, .4, '本体与手阵', '掌根近景、正面全身群手'),
    (53, 59, .4, '悬浮手', '高位俯视掌心、指节、掌缘'),
    (65, 70, .4, '头盔胸甲', '正面头盔与金纹近景'),
    (80, 90, .4, '悬浮手与上身', '掌心、掌背、指根和高位俯视胸肩'),
    (104, 117, 1., '握持手轮廓', '线描表现，记录屈指包围关系'),
    (149, 155, .4, '本体胸肩', '低仰胸甲前凸与头肩侧形'),
    (253, 259, .4, '悬浮手阵', '高空正背交错与掌心仰视'),
    (264, 269, .4, '本体背面', '迎光高举双臂背部轮廓'),
    (279, 283, .4, '群手防壁', '多层手甲围球的侧背轮廓'),
    (304, 311, .4, '群手阵列', '手背排布与金色层甲'),
    (315, 319, .4, '头盔胸甲', '正面高位近景与绿色特效照明'),
]


def main():
    (OUT / 'frames').mkdir(parents=True, exist_ok=True)
    (OUT / 'thumbnails').mkdir(exist_ok=True)
    video_info = json.loads((CACHE / (VIDEO + '.info.json')).read_text('utf8'))
    cap = cv2.VideoCapture(str(CACHE / (VIDEO + '.mp4')))
    records, seen = [], set()
    for scene, (start, end, step, subject, view) in enumerate(WINDOWS, 1):
        for index in range(round((end - start) / step) + 1):
            sec = round(min(end, start + step * index), 3)
            cap.set(cv2.CAP_PROP_POS_MSEC, sec * 1000)
            ok, pixels = cap.read()
            if not ok:
                continue
            encoded = cv2.imencode('.jpg', pixels, [cv2.IMWRITE_JPEG_QUALITY, 94])[1].tobytes()
            digest = hashlib.sha256(encoded).hexdigest()
            if digest in seen:
                continue
            seen.add(digest)
            rid = f'A{len(records) + 1:03d}'
            file = f'frames/{rid}-{sec:07.3f}s.jpg'
            (OUT / file).write_bytes(encoded)
            im = Image.fromarray(cv2.cvtColor(pixels, cv2.COLOR_BGR2RGB))
            w, h = im.size
            im.thumbnail((480, 270), Image.Resampling.LANCZOS)
            thumb = f'thumbnails/{rid}.jpg'
            im.save(OUT / thumb, quality=92)
            records.append(dict(id=rid, file=file, thumbnail=thumb, source_url=f'https://www.youtube.com/watch?v={VIDEO}&t={sec:g}s',
                video_id=VIDEO, time_seconds=sec, source_title=video_info['title'], publisher=video_info['channel'],
                category='官方动画研究原帧', form='动画乌合之众及独立悬浮手', subject=subject, angle=view,
                scene=scene, width=w, height=h, sha256=digest, reviewed=False,
                observations=[], counting='同镜头连续运动研究帧，独立角度按scene分组核对。'))
    cap.release()
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 17)
    for start in range(0, len(records), 12):
        sheet = Image.new('RGB', (1920, 3 * 306), '#14161c')
        draw = ImageDraw.Draw(sheet)
        for index, ref in enumerate(records[start:start + 12]):
            im = Image.open(OUT / ref['thumbnail'])
            x, y = index % 4 * 480, index // 4 * 306
            sheet.paste(im, (x, y))
            draw.text((x + 8, y + 273), f"{ref['id']}  {ref['time_seconds']:g}s  镜头组{ref['scene']} {ref['subject']}", font=font, fill='#e9ddbc')
        sheet.save(OUT / f'contact-{start // 12 + 1:02d}.jpg', quality=94)
    payload = dict(created_at=datetime.now(timezone.utc).isoformat(), count=len(records),
        counting='官方动画同镜头运动研究帧；本清单原帧数量与独立角度数量分别记录，缩略图和联系图不计。',
        scene_groups=len(WINDOWS), references=records)
    (OUT / 'references.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2), 'utf8')
    print(json.dumps(dict(count=len(records), contacts=(len(records) + 11) // 12, out=str(OUT)), ensure_ascii=False))


if __name__ == '__main__':
    main()
