# -*- coding: utf-8 -*-
from pathlib import Path
import json
import sys

import cv2
from PIL import Image, ImageDraw, ImageFont

CACHE = Path('C:/Users/OWNER/.cache/hk3gtl-w09-reference-videos')
FONT = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 18)


def scan(video, start, end, step):
    capture = cv2.VideoCapture(str(CACHE / (video + '.mp4')))
    out = CACHE / ('r2scan-' + video)
    out.mkdir(exist_ok=True)
    times = [start + step * i for i in range(int((end - start) / step) + 1)]
    for offset in range(0, len(times), 20):
        sheet = Image.new('RGB', (1920, 4 * 300), '#181818')
        draw = ImageDraw.Draw(sheet)
        for i, seconds in enumerate(times[offset:offset + 20]):
            capture.set(cv2.CAP_PROP_POS_MSEC, seconds * 1000)
            _, frame = capture.read()
            im = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            im.thumbnail((480, 270))
            x, y = i % 4 * 480, i // 4 * 300
            sheet.paste(im, (x, y))
            draw.text((x + 8, y + 270), f'{seconds:g}s', font=FONT, fill='white')
        sheet.save(out / f'{offset // 20:02d}.jpg', quality=91)
    capture.release()
    print(out)


if __name__ == '__main__':
    scan(sys.argv[1], *map(float, sys.argv[2:]))
