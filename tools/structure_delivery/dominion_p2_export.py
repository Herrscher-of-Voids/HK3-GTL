import struct

import numpy as np


def chunk(name, content=b'', children=b''):
    return name.encode()+struct.pack('<ii', len(content), len(children))+content+children


def dictionary(values):
    result = struct.pack('<i', len(values))
    for key, value in values.items():
        for item in [key, str(value)]:
            raw = item.encode('utf8')
            result += struct.pack('<i', len(raw))+raw
    return result


def write_vox(path, parts, materials, title='乌合之众原作像素重建'):
    tiles = []
    for part in parts:
        cells = np.floor_divide(part.p, 128)
        unique, indices = np.unique(cells, axis=0, return_inverse=True)
        for tile_id, cell in enumerate(unique):
            selected = indices == tile_id
            points, values = part.p[selected][:, [0, 2, 1]], part.states[selected]
            lo = points.min(0)
            local = points-lo
            size = local.max(0)+1
            records = np.c_[local, values].astype(np.uint8)
            tiles.append((part.label, lo, size, records))
    children = chunk('PACK', struct.pack('<i', len(tiles)))
    for _, _, size, records in tiles:
        children += chunk('SIZE', struct.pack('<iii', *size))
        children += chunk('XYZI', struct.pack('<i', len(records))+records.tobytes())
    palette = bytes.fromhex(''.join(m['color'].lstrip('#')+'ff' for m in materials))
    children += chunk('RGBA', palette+bytes((256-len(materials))*4))
    children += chunk('nTRN', struct.pack('<i', 0)+dictionary({'_name': title})+struct.pack('<iiii', 1, -1, -1, 1)+dictionary({}))
    children += chunk('nGRP', struct.pack('<i', 1)+dictionary({})+struct.pack('<i', len(tiles))+b''.join(struct.pack('<i', 2+2*i) for i in range(len(tiles))))
    for i, (label, lo, size, _) in enumerate(tiles):
        transform, shape = 2+2*i, 3+2*i
        translation = lo+size//2
        children += chunk('nTRN', struct.pack('<i', transform)+dictionary({'_name': label})+struct.pack('<iiii', shape, -1, 0, 1)+dictionary({'_t': ' '.join(map(str, translation))}))
        children += chunk('nSHP', struct.pack('<i', shape)+dictionary({})+struct.pack('<ii', 1, i)+dictionary({}))
    children += chunk('LAYR', struct.pack('<i', 0)+dictionary({'_name': '原色整数格'})+struct.pack('<i', -1))
    path.write_bytes(b'VOX '+struct.pack('<i', 150)+chunk('MAIN', children=children))
    return len(tiles)
