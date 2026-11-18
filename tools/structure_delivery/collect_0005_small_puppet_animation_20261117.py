from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import cv2
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/0005_千人人偶_独立像素模型_D1_20261117/references/animation'
CACHE = Path('C:/Users/OWNER/.cache/hk3gtl-w11-reference-videos')
VIDEO = 'n1rjfW-5HAE'
TIMES = [19.2, 24.2, 24.6, 38.2, 39, 40, 40.8, 41.2, 41.8, 42.2, 42.8, 43.2,
    48.8, 49.6, 50, 50.4, 50.8, 51.2, 51.6, 52, 52.4, 53,
    59.8, 60.6, 61.4, 62.2, 63, 63.8, 70, 71, 71.8, 72.2, 72.6, 73,
    73.6, 74.2, 74.8, 75.4, 76, 76.6, 77.2, 77.8, 78.4, 79, 79.6,
    185.6, 186.4, 187.2, 188, 188.8, 189.6, 190.4, 191.2]


def main():
    (OUT / 'frames').mkdir(parents=True, exist_ok=True)
    (OUT / 'thumbnails').mkdir(exist_ok=True)
    info = json.loads((CACHE / f'{VIDEO}.info.json').read_text('utf8'))
    cap = cv2.VideoCapture(str(CACHE / f'{VIDEO}.mp4'))
    records = []
    for index, sec in enumerate(TIMES, 1):
        cap.set(cv2.CAP_PROP_POS_MSEC, sec*1000)
        ok, pixels = cap.read()
        encoded = cv2.imencode('.jpg', pixels, [cv2.IMWRITE_JPEG_QUALITY, 95])[1].tobytes()
        rid = f'SA{index:03d}'
        name = f'frames/{rid}-{sec:07.3f}s.jpg'
        (OUT / name).write_bytes(encoded)
        im = Image.fromarray(cv2.cvtColor(pixels, cv2.COLOR_BGR2RGB))
        im.thumbnail((480, 270), Image.Resampling.LANCZOS)
        im.save(OUT / f'thumbnails/{rid}.jpg', quality=92)
        records.append(dict(id=rid, file=name, thumbnail=f'thumbnails/{rid}.jpg',
            source_url=f'https://www.youtube.com/watch?v={VIDEO}&t={sec:g}s',
            source_title=info['title'], publisher=info['channel'], time_seconds=sec,
            source_nature='官方动画原帧', width=pixels.shape[1], height=pixels.shape[0],
            sha256=hashlib.sha256(encoded).hexdigest(), reviewed=False, observations=[]))
    cap.release()
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 18)
    for start in range(0, len(records), 12):
        sheet = Image.new('RGB', (1920, 918), '#14161c')
        draw = ImageDraw.Draw(sheet)
        for i, ref in enumerate(records[start:start+12]):
            x, y = i % 4 * 480, i // 4 * 306
            sheet.paste(Image.open(OUT / ref['thumbnail']), (x, y))
            draw.text((x+8, y+274), f"{ref['id']} {ref['time_seconds']:g}s", font=font, fill='#e9ddbc')
        sheet.save(OUT / f'contact-{start//12+1:02d}.jpg', quality=94)
    (OUT / 'candidates.json').write_text(json.dumps(dict(count=len(records), references=records), ensure_ascii=False, indent=2), 'utf8')
    print(len(records))


if __name__ == '__main__':
    main()
