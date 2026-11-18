# -*- coding: utf-8 -*-
import json
from pathlib import Path

from package_0005_w12_author_blueprint_20261116 import mesh_part
from w13_tv_body_20261117 import build_screen


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/0005_W13_侵蚀之律者电视山_T2_20261117'


def main():
    materials = json.loads((OUT / 'materials.json').read_text('utf8'))
    part = build_screen(include_pupil=False)[0]
    screen, quads = mesh_part(part, materials)
    screen.update(id='eye_background', modelId='screen', blocks=len(part.p))
    payload = dict(revision='T2-M1', scope='网页运行预览', screen=screen,
        dynamic_eye='瞳环转动与注视偏移', dynamic_cables='固定根部、错相分节甩动；主控缆两端固定',
        static_nbt='W13-侵蚀之律者电视山-T2.nbt')
    (OUT / 'motion.json').write_text(json.dumps(payload, ensure_ascii=False, separators=(',', ':')), 'utf8')
    print(json.dumps(dict(background_blocks=len(part.p), background_quads=quads)))


if __name__ == '__main__':
    main()
