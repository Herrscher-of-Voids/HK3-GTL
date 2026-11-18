# -*- coding: utf-8 -*-
"""按完整休伯利安舰体生成控制器三态面板并修正绑定。"""
from pathlib import Path
import gzip
import hashlib
import json
import shutil
import struct
import zipfile

from PIL import Image, ImageDraw, ImageFont
import numpy as np

import build_controller_texture_candidates_20261026 as faces

ROOT = Path(__file__).resolve().parents[2]
LOG = ROOT / 'logs/textures-runtime-fixes-0002-r15-20261116'
OUT = ROOT / 'deliveries/0002贴图材质_运行绑定与流体轻量_R15_20261116/hyperion'
SOURCE = ROOT / 'src/main/resources/data/hk3gtl/structures/hyperion_construction.bin.gz'
JAVA = ROOT / 'src/main/java/com/sirin/hk3gtl/common/machine/hyperion/Hk3HyperionMachines.java'
OLD = 'block/overlay/w01_hall'
NEW = 'block/overlay/hyperion_flagship_appearance_0002_r15'
TARGET = ROOT / 'src/main/resources/assets/hk3gtl/textures' / NEW
JAR = Path('C:/Users/OWNER/AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版/minecraft/mods/0002贴图材质-0.5.0-textures-r14.jar')
CLASS = 'com/sirin/hk3gtl/common/machine/hyperion/Hk3HyperionMachines.class'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hull_points():
    data = gzip.decompress(SOURCE.read_bytes())
    magic, version, w, h, d, cx, cy, cz, count, palettes = struct.unpack_from('>9iH', data)
    offset = 38
    for _ in range(palettes):
        offset += 2 + struct.unpack_from('>H', data, offset)[0]
    indices = np.empty(count, dtype=np.int32)
    for i in range(count):
        index, state, payload = struct.unpack_from('>iHi', data, offset)
        indices[i] = index
        offset += 10 + payload
    points = np.column_stack((indices // (h * d), (indices // d) % h, indices % d)).astype(np.int16)
    return points, [cx, cy, cz], [w, h, d]


def binding_constant():
    with zipfile.ZipFile(JAR) as jar:
        data = jar.read(CLASS)
    index, offset = 1, 10
    lengths = {3: 4, 4: 4, 5: 8, 6: 8, 7: 2, 8: 2, 9: 4, 10: 4, 11: 4,
               12: 4, 15: 3, 16: 2, 17: 4, 18: 4, 19: 2, 20: 2}
    while index < struct.unpack_from('>H', data, 8)[0]:
        tag = data[offset]
        offset += 1
        if tag == 1:
            length = struct.unpack_from('>H', data, offset)[0]
            value = data[offset + 2:offset + 2 + length]
            if value == OLD.encode():
                return {'jar': str(JAR), 'class': CLASS, 'class_sha256': hashlib.sha256(data).hexdigest(),
                        'constant_pool_index': index, 'length_offset': offset, 'payload_offset': offset + 2,
                        'old_utf8_length': length, 'old_value': OLD, 'new_value': NEW,
                        'new_utf8_length': len(NEW.encode())}
            offset += 2 + length
        else:
            offset += lengths[tag]
            index += tag in (5, 6)
        index += 1


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    TARGET.mkdir(parents=True, exist_ok=True)
    backup = LOG / 'before' / JAVA.relative_to(ROOT)
    backup.parent.mkdir(parents=True, exist_ok=True)
    if not backup.exists():
        shutil.copy2(JAVA, backup)
    before_sha = sha(backup)
    points, controller, size = hull_points()
    faces.geometry_image(points, OUT / 'whole-machine.png')
    projection = faces.projected_geometry
    projected = projection(points, 44, 37)
    faces.projected_geometry = lambda value, width, height, margin=1: projected
    textures = {}
    for state, suffix in faces.STATE_SUFFIX.items():
        picture, pattern = faces.candidate_face(points, [], controller, state)
        filename = 'overlay_front' + suffix + '.png'
        destination = TARGET / filename
        picture.save(destination)
        shutil.copy2(destination, OUT / filename)
        shutil.copy2(ROOT / 'src/main/resources/assets/hk3gtl/textures' / OLD / filename,
                     OUT / ('before' + suffix + '.png'))
        textures[state] = {'path': destination.relative_to(ROOT).as_posix(), 'sha256': sha(destination),
                           'size': list(picture.size), 'mode': picture.mode}
    faces.projected_geometry = projection
    JAVA.write_text(JAVA.read_text('utf-8').replace(OLD, NEW, 1), 'utf-8')
    sheet = Image.new('RGB', (600, 630), '#091421')
    sheet.paste(Image.open(OUT / 'whole-machine.png'), (0, 0))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 17)
    for column, (state, suffix) in enumerate(faces.STATE_SUFFIX.items()):
        image = Image.open(TARGET / ('overlay_front' + suffix + '.png'))
        sheet.paste(image.resize((160, 160), Image.Resampling.NEAREST), (20 + column * 200, 430))
        draw.text((80 + column * 200, 597), faces.STATE_CN[state], font=font, fill='#d9eaf0')
    sheet.save(OUT / 'preview.png')
    manifest = {'role': 'H01', 'machine': 'hk3gtl:hyperion_flagship', 'name': '休伯利安号舰体搭建控制器',
                'source': SOURCE.relative_to(ROOT).as_posix(), 'source_sha256': sha(SOURCE),
                'size_xyz': size, 'blocks': len(points), 'controller_xyz': controller,
                'method': '完整现行1145格舰体蓝图直接投影，沿用R7统一工业面板与三态，不使用生图API。',
                'overlay_before': 'hk3gtl:' + OLD, 'overlay_after': 'hk3gtl:' + NEW,
                'casing': 'hk3gtl:block/casings/industrial_controller_shell', 'ports_drawn': [],
                'geometry_pattern_sha256': pattern, 'textures': textures,
                'java': JAVA.relative_to(ROOT).as_posix(), 'java_before_sha256': before_sha,
                'java_after_sha256': sha(JAVA), 'runtime_class_binding': binding_constant(),
                'game_verified': False, 'installed': False}
    text = json.dumps(manifest, ensure_ascii=False, indent=2) + '\n'
    (OUT / 'manifest.json').write_text(text, 'utf-8')
    (LOG / 'hyperion-controller.json').write_text(text, 'utf-8')
    print(text)


if __name__ == '__main__':
    main()
