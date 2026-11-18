import base64
import gzip
import json
from pathlib import Path

import numpy as np


CORNERS = np.asarray([
    [[1, 0, 0], [1, 1, 0], [1, 1, 1], [1, 0, 1]],
    [[0, 0, 1], [0, 1, 1], [0, 1, 0], [0, 0, 0]],
    [[1, 0, 1], [1, 1, 1], [0, 1, 1], [0, 0, 1]],
    [[0, 0, 0], [0, 1, 0], [1, 1, 0], [1, 0, 0]],
    [[0, 0, 1], [0, 0, 0], [1, 0, 0], [1, 0, 1]],
    [[0, 1, 0], [0, 1, 1], [1, 1, 1], [1, 1, 0]],
], dtype=np.float32)


def scene_geometry(scene):
    surfaces = []
    for part in scene['parts']:
        metadata = part.get('metadata', {})
        if metadata.get('mode', 0) >= 2:
            continue
        width, _, depth = part['size']
        origin = np.asarray(part['origin'], dtype=np.float32)
        for material, faces in enumerate(part['starts']):
            for face, starts in enumerate(faces):
                if not starts:
                    continue
                indices = np.asarray(starts, dtype=np.int64)
                positions = np.column_stack((indices % width,
                                             indices // (width * depth),
                                             (indices // width) % depth)).astype(np.float32)
                lengths = np.asarray(part['lengths'][material][face], dtype=np.float32)
                spans = (np.asarray(part['spans'][material][face], dtype=np.float32)
                         if 'spans' in part else np.ones(len(indices), dtype=np.float32))
                axis, cross = (2 if face < 2 else 0), (1 if face < 4 else 2)
                scale = np.ones((len(indices), 3), dtype=np.float32)
                scale[:, axis], scale[:, cross] = lengths, spans
                vertices = positions[:, None, :] + origin + CORNERS[face] * scale[:, None, :]
                if 'mode' in metadata:
                    matrix = np.asarray(metadata['rest_matrix'], dtype=np.float32).reshape(4, 4).T
                    vertices = vertices @ matrix[:3, :3].T + matrix[:3, 3]
                surfaces.append(vertices)
    data = scene['data']
    native = data.get('native_blocks', [])
    if native:
        positions = np.asarray([block['pos'] for block in native], dtype=np.float32)
        surfaces.append((positions[:, None, None, :] + CORNERS).reshape(-1, 4, 3))
    controller = data['controller_blueprint'] if 'controller_blueprint' in data else data['controller']
    return np.concatenate(surfaces), np.asarray(controller, dtype=np.float32)


def read_scene(path):
    path = Path(path)
    if path.suffix == '.js':
        payload = json.loads(path.read_text('utf8').split('=', 1)[1].rstrip(';\n'))
        scene = json.loads(gzip.decompress(base64.b64decode(payload)))
    else:
        with gzip.open(path, 'rt', encoding='utf8') as stream:
            scene = json.load(stream)
    return scene_geometry(scene)
