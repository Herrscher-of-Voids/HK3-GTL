"""W01受负责人指定的Azu原建筑；只替换中央礼台一格主控，导出全实体校验资源。"""
# 变更记录#2：2026-10-30 00:05:13，修订183：输入改为独立干燥修订场景；主控改为西入口，原始场景不改。
import gzip
import json
import struct
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'src/main/resources/data/hk3gtl/structures'


def main():
    source_dir = ROOT / 'output/w01-dry-layout-20261030'
    source = np.load(source_dir / 'scene-main.npz')
    world = source['positions']
    states = source['states']
    palette = json.loads((source_dir / 'palette.json').read_text(encoding='utf-8'))
    low, high = world.min(axis=0), world.max(axis=0)
    size = high - low + 1
    control_world = np.array([-55, -34, 7])
    control = control_world - low
    at = np.all(world == control_world, axis=1)
    assert at.sum() == 1 and palette[int(states[at][0])] == 'minecraft:chiseled_quartz_block'
    used = sorted(set(int(s) for s in states))
    remap = np.zeros(len(palette), dtype=np.uint16)
    remap[used] = np.arange(len(used))
    local = (world - low).astype(np.int64)
    packed = (((local[:, 0] << 20) | (local[:, 1] << 10) | local[:, 2]) << 16) | remap[states]
    packed.sort()
    assert len(packed) == 1932713 and np.all(packed[1:] >> 16 != packed[:-1] >> 16)
    header = struct.pack('>9iH', 0x57303141, 1, *size, *control, len(packed), len(used))
    data = bytearray(header)
    for state in (palette[i] for i in used):
        encoded = state.encode('utf-8')
        data.extend(struct.pack('>H', len(encoded)) + encoded)
    data.extend(packed.astype('>i8').tobytes())
    OUT.mkdir(parents=True, exist_ok=True)
    target = OUT / 'w01_hall.bin.gz'
    with target.open('wb') as stream, gzip.GzipFile(fileobj=stream, mode='wb', mtime=0, compresslevel=9) as gz:
        gz.write(data)
    assert gzip.decompress(target.read_bytes()) == data
    # 独立控制器正面：白色多柱拱庭、粉红协奏核与金色向心环，三帧共享建筑识别。
    face_dir = ROOT / 'src/main/resources/assets/hk3gtl/textures/block/overlay/w01_hall'
    face_dir.mkdir(parents=True, exist_ok=True)
    for name, glow in [('overlay_front', '#c8b8ce'), ('overlay_front_active', '#f1a7d5'), ('overlay_front_paused', '#aa9cb5')]:
        image = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.rectangle((1, 1, 14, 14), fill='#272332', outline='#c1b8cf')
        for x in [3, 6, 9, 12]:
            draw.line((x, 6, x, 12), fill='#ded5e3')
        draw.arc((2, 3, 13, 10), 180, 360, fill='#ded5e3')
        draw.ellipse((4, 6, 11, 11), outline='#ceb374')
        draw.rectangle((7, 7, 8, 10), fill=glow)
        draw.line((2, 13, 13, 13), fill='#ded5e3')
        image.save(face_dir / (name + '.png'))
    print(json.dumps({'resource': str(target), 'bytes': target.stat().st_size, 'size_xyz': size.tolist(),
                      'origin_xyz': low.tolist(), 'controller_world': control_world.tolist(),
                      'controller_local': control.tolist(), 'count': len(packed), 'states': len(used)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
