import array
import gzip
import hashlib
import json
from pathlib import Path
import struct
import sys

from sanitize_release_resources import select, without


SCENES = ('w05_r3', 'w06_author', 'w07_n2', 'w08_a5', 'w10_a3',
          'w11_f5', 'w12_a3', 'w13_t2_m1', 'w14_e3', 'w15_b1')
SCENE_DATA_FIELDS = set(('sizeXYZ blueprint_to_export_offset_xyz controller_blueprint atlas_grid palette '
                         'material_counts native_blocks bounds effects star_center star_radius corona_radius rig').split())
PART_FIELDS = set('id origin size starts lengths spans metadata'.split())
PART_METADATA = set(('motion_axis pivot idle_speed running_speed motion_kind amplitude frequency effect_mask '
                     'cube_sphere_radius motion_speed visual actor bone parent base_rotation rest_matrix dynamic '
                     'mode cable segment').split())


class Geometry:
    def __init__(self):
        self.data = bytearray()
        self.digest = hashlib.sha256()
        self.arrays = 0
        self.values = 0

    def unsigned(self, value):
        while value > 127:
            self.data.append((value & 127) | 128)
            value >>= 7
        self.data.append(value)

    def delta(self, value):
        self.unsigned((value << 1) ^ (value >> 31))

    def count(self, value):
        self.digest.update(struct.pack('>I', value))
        self.unsigned(value)

    def integers(self, values):
        encoded = array.array('i', values)
        if sys.byteorder == 'little':
            encoded.byteswap()
        self.digest.update(encoded.tobytes())
        self.values += len(values)

    def cube(self, value):
        self.arrays += 1
        self.digest.update(b'\x03')
        self.count(len(value))
        for faces in value:
            self.count(len(faces))
            for values in faces:
                self.count(len(values))
                self.integers(values)
                previous = 0
                for item in values:
                    self.delta(item - previous)
                    previous = item

    def rectangles(self, value):
        self.arrays += 1
        self.digest.update(b'\x02')
        self.count(len(value))
        columns = len(value[0]) if value else 5
        self.unsigned(columns)
        previous = [0] * columns
        for row in value:
            self.digest.update(struct.pack('>I', len(row)))
            self.integers(row)
            for column, item in enumerate(row):
                self.delta(item - previous[column])
                previous[column] = item


def w11_overview(scene):
    step = int(16 * scene['data']['rig'].get('voxel_scale', 1))
    offset = scene['data']['blueprint_to_export_offset_xyz']
    nx, ny, nz = dims = [(n + step - 1) // step for n in scene['data']['sizeXYZ']]
    cells = bytearray(nx * ny * nz)
    weights = bytearray(len(cells))
    strides = (1, nx * nz, nx)
    directions = ((0, 2, 1), (0, 2, 1), (2, 0, 1), (2, 0, 1), (1, 0, 2), (1, 0, 2))
    static = [p for p in scene['parts'] if not p['metadata']['dynamic']]
    for part in static:
        sx, _, sz = part['size']
        ox, oy, oz = [a + b for a, b in zip(part['origin'], offset)]
        for material, faces in enumerate(part['starts'], 1):
            for face, (n, u, v) in enumerate(directions):
                for at, du, dv in zip(faces[face], part['lengths'][material - 1][face], part['spans'][material - 1][face]):
                    xyz = (at % sx + ox, at // (sx * sz) + oy, at // sx % sz + oz)
                    base = xyz[n] // step * strides[n]
                    weight = min(255, min(step, du) * min(step, dv))
                    for j in range(xyz[v] // step, (xyz[v] + dv - 1) // step + 1):
                        row = base + j * strides[v]
                        for i in range(xyz[u] // step, (xyz[u] + du - 1) // step + 1):
                            k = row + i * strides[u]
                            if weight > weights[k]:
                                cells[k], weights[k] = material, weight

    size = scene['data']['sizeXYZ']
    split = ny // 2 * step
    parts = [dict(id=f'static_overview_{i}', origin=[-offset[0], low - offset[1], -offset[2]],
                  size=[size[0], high - low, size[2]], metadata=static[0]['metadata'],
                  **{key: [[[] for _ in directions] for _ in scene['materials']]
                     for key in ('starts', 'lengths', 'spans')})
             for i, (low, high) in enumerate(((0, split), (split, size[1])))]
    for face, (n, u, v) in enumerate(directions):
        outward = 1 if face in (0, 2, 5) else -1
        width, height = dims[u], dims[v]
        mask = bytearray(width * height)
        for plane in range(dims[n]):
            base = plane * strides[n]
            boundary = not 0 <= plane + outward < dims[n]
            for j in range(height):
                row = base + j * strides[v]
                for i in range(width):
                    k = row + i * strides[u]
                    mask[j * width + i] = cells[k] if boundary or not cells[k + outward * strides[n]] else 0
            for j in range(height):
                for i in range(width):
                    k = j * width + i
                    material = mask[k]
                    if not material:
                        continue
                    du = 1
                    while i + du < width and mask[k + du] == material:
                        du += 1
                    strip = bytes([material]) * du
                    dv = 1
                    limit = split // step if v == 1 and j * step < split else height
                    while j + dv < limit and mask[k + dv * width:k + dv * width + du] == strip:
                        dv += 1
                    for r in range(dv):
                        mask[k + r * width:k + r * width + du] = bytes(du)
                    xyz = [0] * 3
                    xyz[n] = min(size[n], (plane + 1) * step) - 1 if outward > 0 else plane * step
                    xyz[u], xyz[v] = i * step, j * step
                    group = int(xyz[1] >= split)
                    mesh = parts[group]
                    mesh['starts'][material - 1][face].append(((xyz[1] - group * split) * size[2] + xyz[2]) * size[0] + xyz[0])
                    mesh['lengths'][material - 1][face].append(min(du * step, size[u] - xyz[u]))
                    mesh['spans'][material - 1][face].append(min(dv * step, size[v] - xyz[v]))
    return parts


def encode(directory, name, scene, source, original, resources):
    geometry = Geometry()
    for key, value in scene.items():
        if key == 'parts':
            for part in value:
                for field, arrays in part.items():
                    if field in ('starts', 'lengths', 'spans'):
                        geometry.cube(arrays)
                        part[field] = 'binary'
        elif key == 'layers':
            for layer in value:
                geometry.rectangles(layer['rectangles'])
                layer['rectangles'] = 'binary'
    public_scene = select(scene, {'data', 'materials', 'parts', 'layers'})
    public_scene['data'] = without(select(scene['data'], SCENE_DATA_FIELDS),
                                   {'original_path', 'archive', 'file', 'runtime_provenance'})
    public_scene['materials'] = [select(material, {'transparent', 'emissive'}) for material in scene['materials']]
    public_scene['parts'] = [select(part, PART_FIELDS) for part in scene['parts']]
    for part in public_scene['parts']:
        if 'metadata' in part:
            part['metadata'] = select(part['metadata'], PART_METADATA)
    if 'layers' in scene:
        public_scene['layers'] = [select(layer, {'y', 'rectangles'}) for layer in scene['layers']]
    header = json.dumps(public_scene, ensure_ascii=False, separators=(',', ':')).encode('utf8')
    destination = directory / f'{name}.scene.bin.gz'
    with destination.open('wb') as stream, gzip.GzipFile(
            fileobj=stream, mode='wb', compresslevel=9, mtime=0, filename='') as output:
        output.write(struct.pack('>III', 0x484B5343, 1, len(header)))
        output.write(header)
        output.write(geometry.data)
    encoded = destination.read_bytes()
    print(f"场景{name}：{len(encoded)}字节。", flush=True)
    return dict(source_path=source.relative_to(resources).as_posix(),
        path=destination.relative_to(resources).as_posix(),
        source_bytes=len(original), runtime_bytes=len(encoded),
        source_sha256=hashlib.sha256(original).hexdigest(),
        runtime_sha256=hashlib.sha256(encoded).hexdigest(),
        geometry_sha256=geometry.digest.hexdigest(), geometry_arrays=geometry.arrays,
        integer_values=geometry.values, parts=len(scene['parts']), layers=len(scene.get('layers', [])),
        header_bytes=len(header), geometry_bytes=len(geometry.data))


def compact(resources, report, names=SCENES):
    directory = resources / 'assets/hk3gtl/models/scene'
    records = []
    for name in names:
        source = directory / f'{name}.json.gz'
        original = source.read_bytes()
        scene = json.loads(gzip.decompress(original))
        if name == 'w11_f5':
            overview = w11_overview(scene)
            moving = [part for part in scene['parts'] if part['metadata']['dynamic']]
            original_faces = sum(len(face) for p in scene['parts'] for material in p['starts'] for face in material)
            overview_faces = sum(len(face) for p in overview for material in p['starts'] for face in material)
            moving_faces = sum(len(face) for p in moving for material in p['starts'] for face in material)
            layers = dict(scene, parts=[])
            scene = dict(scene, parts=[*overview, *moving], layers=[])
            records.append(encode(directory, name + '_layers', layers, source, original, resources))
            records.append(dict(encode(directory, name, scene, source, original, resources),
                original_faces=original_faces, overview_faces=overview_faces, moving_faces=moving_faces, overview_step=int(16 * scene['data']['rig'].get('voxel_scale', 1))))
        elif name in ('w07_n2', 'w13_t2_m1'):
            layers = dict(scene, parts=[])
            overview = dict(scene, parts=[dict(part) for part in scene['parts']], layers=[])
            if name == 'w07_n2':
                moving = dict(scene, parts=[dict(part, **{
                    field: [faces if scene['materials'][material]['emissive'] else [[] for _ in faces]
                            for material, faces in enumerate(part[field])]
                    for field in ('starts', 'lengths', 'spans')}) for part in scene['parts']], layers=[])
                records.append(encode(directory, name + '_lights', moving, source, original, resources))
                records.append(encode(directory, name, overview, source, original, resources))
            else:
                moving = dict(scene, parts=[dict(part) for part in scene['parts']
                                           if part['metadata']['mode'] >= 2], layers=[])
                records.append(encode(directory, name, moving, source, original, resources))
                records.append(encode(directory, name + '_preview', overview, source, original, resources))
            records.append(encode(directory, name + '_layers', layers, source, original, resources))
        else:
            records.append(encode(directory, name, scene, source, original, resources))
        source.unlink()
    record = dict(format='HKSC-v1-delta-zigzag-varint', scenes=records,
        geometry_digest_format='数组维数单字节、各级长度大端uint32、整数值大端int32，按JSON字段及数组顺序；矩形逐行记录长度与值',
        source_bytes=sum({item['source_path']: item['source_bytes'] for item in records}.values()),
        runtime_bytes=sum(item['runtime_bytes'] for item in records))
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf8')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf8')
    compact(Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3:] or SCENES)
