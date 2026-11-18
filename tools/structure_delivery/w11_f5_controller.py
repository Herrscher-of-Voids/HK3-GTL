from pathlib import Path
import hashlib
import json

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import build_controller_texture_candidates_20261026 as faces

ROOT = Path(__file__).resolve().parents[2]
LOG = ROOT / 'logs/0005-w11-f5-production-20261117'
SOURCE = LOG / 'w11_f5_surfaces.npz'
TARGET = ROOT / 'src/main/resources/assets/hk3gtl/textures/block/overlay/w11_puppetry_f5'
CONTROLLER = [0, 20, 500]


def surface_vertices(quads):
    vertices = np.repeat(quads[:, None, 3:6].astype(np.float32), 4, axis=1)
    corners = np.asarray([[0, 0], [1, 0], [1, 1], [0, 1]], dtype=np.float32)
    for normals, axis, u, v, positive in [((0, 1), 0, 2, 1, 0), ((2, 3), 2, 0, 1, 2), ((4, 5), 1, 0, 2, 5)]:
        at = np.flatnonzero(np.isin(quads[:, 2], normals))
        vertices[at, :, axis] += (quads[at, 2] == positive)[:, None]
        vertices[at, :, u] += quads[at, 6, None] * corners[None, :, 0]
        vertices[at, :, v] += quads[at, 7, None] * corners[None, :, 1]
    return vertices


def projected_surfaces(vertices, width=44, height=37, margin=1):
    uv = faces.projection(vertices.reshape(-1, 3)).reshape(-1, 4, 3)
    low, high = uv[:, :, :2].min(axis=(0, 1)), uv[:, :, :2].max(axis=(0, 1))
    scale = min((width - 1 - margin * 2) / (high[0] - low[0]),
                (height - 1 - margin * 2) / (high[1] - low[1]))
    offset = (np.asarray([width - 1, height - 1]) - (high - low) * scale) / 2
    pixels = np.rint((uv[:, :, :2] - low) * scale + offset).astype(np.int32)
    depths = uv[:, :, 2].mean(axis=1)
    image = Image.new('F', (width, height), -np.inf)
    draw = ImageDraw.Draw(image)
    for index in np.argsort(depths):
        draw.polygon([tuple(point) for point in pixels[index]], fill=float(depths[index]))
    depth = np.asarray(image)
    valid = np.isfinite(depth)
    edge, ridges = np.zeros_like(valid), np.zeros_like(valid)
    threshold = max(float(uv[:, :, 2].max() - uv[:, :, 2].min()) * .035, 1)
    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        neighbour = np.roll(valid, (dy, dx), (0, 1))
        other = np.roll(depth, (dy, dx), (0, 1))
        delta = np.zeros_like(depth)
        np.subtract(depth, other, out=delta, where=valid & neighbour)
        edge |= valid & ~neighbour
        ridges |= valid & neighbour & (np.abs(delta) > threshold)
    return depth, valid, edge, ridges, low, scale, offset


def main():
    with np.load(SOURCE) as source:
        quads = source['quads']
    vertices = surface_vertices(quads)
    projected = projected_surfaces(vertices)
    faces.projected_geometry = lambda points, width, height, margin=1: projected
    TARGET.mkdir(parents=True, exist_ok=True)
    sheet = Image.new('RGB', (1536, 570), '#101827')
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 24)
    textures = {}
    for index, (state, suffix) in enumerate(faces.STATE_SUFFIX.items()):
        image, pattern = faces.candidate_face(vertices.reshape(-1, 3), [], CONTROLLER, state)
        path = TARGET / ('overlay_front' + suffix + '.png')
        image.save(path)
        sheet.paste(image.resize((512, 512), Image.Resampling.NEAREST), (index * 512, 48))
        draw.text((index * 512 + 220, 8), faces.STATE_CN[state], font=font, fill='#dde8f3')
        textures[state] = dict(path=path.relative_to(ROOT).as_posix(), sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    sheet.save(LOG / 'controller-panels.png')
    record = dict(source=SOURCE.relative_to(ROOT).as_posix(), source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                  quad_count=len(quads), geometry_pattern_sha256=pattern, controller_xyz=CONTROLLER,
                  method='完整F5整机合面四顶点正交投影，填充全部投影面，复用原生64×64三态主控面板', textures=textures)
    (LOG / 'controller-textures.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', 'utf-8')
    print(json.dumps(record, ensure_ascii=False))


if __name__ == '__main__':
    main()
