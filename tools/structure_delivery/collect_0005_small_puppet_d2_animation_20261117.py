from pathlib import Path
import hashlib
import json

import cv2
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'deliveries/0005_千人人偶_原作重建_D2_20261117/references/animation'
CACHE = Path('C:/Users/OWNER/.cache/hk3gtl-w11-reference-videos')
VIDEO = 'n1rjfW-5HAE'
WINDOWS = [
    ('F01', 23.7, 25.6, 1, '正面蒙眼、额纹、侧发与头肩'),
    ('F02', 40.8, 43.8, 2, '后脑、锥冠、肩背与裙腿'),
    ('F03', 48.4, 50.6, 2, '后领、金手、黑袖与侧前胸裙'),
    ('F04', 50.65, 52.35, 1, '正脸、蒙眼边缘与胸裙'),
    ('F05', 71.4, 74.05, 2, '裙底、机械腿、手掌与正侧面'),
    ('F06', 75.1, 76.95, 2, '低仰裙底、膝腿关节'),
    ('F07', 77.0, 79.0, 2, '完整群像与前侧后方向'),
    ('F08', 186.45, 187.75, 2, '完整空中姿态与头身比例'),
    ('F09', 188.1, 189.25, 2, '远景站姿与机械腿姿态'),
]


def main():
    (OUT/'frames').mkdir(parents=True, exist_ok=True)
    (OUT/'contact-sheets').mkdir(exist_ok=True)
    info = json.loads((CACHE/f'{VIDEO}.info.json').read_text('utf8'))
    cap = cv2.VideoCapture(str(CACHE/f'{VIDEO}.mp4'))
    fps = cap.get(cv2.CAP_PROP_FPS)
    records = []
    for wid, start, end, step, purpose in WINDOWS:
        for frame_number in range(round(start*fps), round(end*fps)+1, step):
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ok, pixels = cap.read()
            sec = frame_number/fps
            encoded = cv2.imencode('.jpg', pixels, [cv2.IMWRITE_JPEG_QUALITY, 96])[1].tobytes()
            rid = f'D2A{len(records)+1:03d}'
            name = f'frames/{rid}-{sec:07.3f}s.jpg'
            (OUT/name).write_bytes(encoded)
            records.append(dict(id=rid, file=name, window_id=wid, window_purpose=purpose,
                source_url=f'https://www.youtube.com/watch?v={VIDEO}&t={sec:.3f}s',
                source_title=info['title'], publisher=info['channel'], time_seconds=round(sec, 6),
                source_frame=frame_number, source_nature='官方动画原始完整帧',
                width=pixels.shape[1], height=pixels.shape[0],
                sha256=hashlib.sha256(encoded).hexdigest(), reviewed=False))
    cap.release()
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 21)
    sheets = []
    for start in range(0, len(records), 20):
        sheet = Image.new('RGB', (2560, 1960), '#191b20')
        draw = ImageDraw.Draw(sheet)
        for i, ref in enumerate(records[start:start+20]):
            x, y = i % 4*640, i//4*392
            im = Image.open(OUT/ref['file'])
            im.thumbnail((640, 360), Image.Resampling.LANCZOS)
            sheet.paste(im, (x, y))
            draw.text((x+8, y+362), f"{ref['id']} {ref['time_seconds']:.3f}s {ref['window_id']}", font=font, fill='#f0dfb4')
        filename = f'contact-sheets/candidate-{start//20+1:02d}.jpg'
        sheet.save(OUT/filename, quality=96)
        sheets.append(dict(file=filename, ids=[r['id'] for r in records[start:start+20]], reviewed=False))
    (OUT/'candidates.json').write_text(json.dumps(dict(subject='金发黑蒙眼千人人偶',
        count=len(records), source_count=1, source_fps=fps,
        windows=[dict(id=w[0], start=w[1], end=w[2], frame_step=w[3], purpose=w[4]) for w in WINDOWS],
        contact_sheets=sheets, references=records), ensure_ascii=False, indent=2), 'utf8')
    print(json.dumps(dict(candidates=len(records), contact_sheets=len(sheets)), ensure_ascii=False))


if __name__ == '__main__':
    main()
