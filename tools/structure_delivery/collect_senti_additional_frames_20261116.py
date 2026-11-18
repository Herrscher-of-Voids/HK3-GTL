# -*- coding: utf-8 -*-
from pathlib import Path
import json

import cv2
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
CACHE = Path('C:/Users/OWNER/.cache/hk3gtl-w09-reference-videos')
OUT = ROOT / 'deliveries/0005_W09_识律武器补充参考_R2_20261116/演示补充'
SELECTION = [
    ('j4_DF561wmw', 11, '武器匣', '背斜面全长', '宽面、红色侧壁与下端弯尖同框，人物用于长度比较。'),
    ('j4_DF561wmw', 34.5, '长枪', '前斜侧展开', '查看长枪长叶尖端、窄杆与另一端套帽，橙色轨迹另看。'),
    ('j4_DF561wmw', 41, '长枪', '后斜侧展开', '补充另一持握方向的两端轮廓与枪杆相对长度。'),
    ('j4_DF561wmw', 53, '链刃', '双端近身展开', '可见自由端骨白包边与持握端，红色拖影不计为实体。'),
    ('j4_DF561wmw', 83, '武器匣', '冠口前斜面', '近身观察太极盘、圆晶、冠口与抽出柄段。'),
    ('j4_DF561wmw', 149, '武器匣', '滑行低侧面', '匣体横置脚下，可观察侧壁与下表面投影。'),
    ('j4_DF561wmw', 155, '武器匣', '滑行正侧面', '补充横置时的厚度、弯尖与红色侧壁。'),
    ('6zC-Z4sgxWI', 256, '武器匣', '角色菜单背侧近景', '宽面大面积骨白与朱红纹清楚，作为背侧配色核对。'),
]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    refs = []
    for i, (video, seconds, subject, view, note) in enumerate(SELECTION, 1):
        capture = cv2.VideoCapture(str(CACHE / (video + '.mp4')))
        capture.set(cv2.CAP_PROP_POS_MSEC, seconds * 1000)
        _, frame = capture.read()
        capture.release()
        im = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        filename = f'R2-G{i:02d}-{video}-{seconds:g}s.png'
        im.save(OUT / filename)
        info = json.loads((CACHE / (video + '.info.json')).read_text('utf8'))
        refs.append(dict(id=f'R2-G{i:02d}', subject=subject, view=view, note=note,
            file='演示补充/' + filename, seconds=seconds, resolution=list(im.size),
            source_url=f'https://www.youtube.com/watch?v={video}&t={int(seconds)}s',
            kind='玩家测试服录像', source_title=info['title'], author=info['channel'],
            upload_date=info['upload_date'], group=video,
            status='新增原帧，测试服4.6v1'))
    (OUT / 'references.json').write_text(json.dumps(refs, ensure_ascii=False, indent=2), 'utf8')
    print(len(refs))


if __name__ == '__main__':
    main()
