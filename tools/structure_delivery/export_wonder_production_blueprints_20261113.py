"""将已完整生成的W04/W05候选打包为真实主控建造蓝图，保持候选几何和自由接口。"""
from pathlib import Path
import gzip
import json
import struct
import nbtlib
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'logs/remove-fixed-ports-r266-20261113'
DESTINATION = ROOT / 'src/main/resources/data/hk3gtl/structures'


def export(role, controller):
    folder = SOURCE / role.lower()
    meta = json.loads((folder / 'manifest.json').read_text('utf8'))
    structure = nbtlib.load(str(folder / (meta['name'] + '.schem')))
    w, h, d = map(int, (structure['Width'], structure['Height'], structure['Length']))
    palette = [''] * int(structure['PaletteMax'])
    for state, index in structure['Palette'].items():
        palette[int(index)] = state
    cells = np.asarray(structure['BlockData'], dtype=np.uint8).reshape(h, d, w)
    marker = meta['controller'] if role == 'W05' else np.array(meta['controller_world']) + meta['blueprint_to_export_offset_xyz']
    cx, cy, cz = map(int, marker)
    palette.append('hk3gtl:' + controller + '[facing=south]')
    cells[cy, cz, cx] = len(palette) - 1
    count = int(np.count_nonzero(cells))
    with gzip.GzipFile(filename=str(DESTINATION / (role.lower() + '_candidate.bin.gz')), mode='wb', compresslevel=9, mtime=0) as output:
        output.write(struct.pack('>9iH', 0x484b3350, 2, w, h, d, cx, cy, cz, count, len(palette)))
        for state in palette:
            value = state.encode('utf8')
            output.write(struct.pack('>H', len(value)) + value)
        for x in range(w):
            for y in range(h):
                row = cells[y, :, x]
                cuts = np.flatnonzero(np.r_[True, row[1:] != row[:-1], True])
                for start, end in zip(cuts[:-1], cuts[1:]):
                    state = int(row[start])
                    if state:
                        output.write(struct.pack('>iiiHi', (x * h + y) * d + int(start), 1, int(end - start), state, 0))
    print(role, w, h, d, count, flush=True)


if __name__ == '__main__':
    export('W04', 'w04_thunder_superconducting_axis')
    export('W05', 'w05_ideal_fluid_circulation_array')
