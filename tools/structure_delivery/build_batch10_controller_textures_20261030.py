# -*- coding: utf-8 -*-
"""从六台批准布局生成独立三态主控；保留已采用的面板边框与全部旧贴图。

2026-10-30（修订182）：复用已采用的几何投影方法，图案只来自各自批准版本。
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import time

import numpy as np
from PIL import Image, ImageDraw

import build_controller_texture_candidates_20261026 as faces

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'src/main/resources/data/hk3gtl'
OVERLAYS = ROOT / 'src/main/resources/assets/hk3gtl/textures/block/overlay'
OUT = ROOT / 'logs/batch10-install-20261030'
KEYS = tuple(f'i{number}' for number in range(40, 46))
VERSIONS = ('V1', 'V3', 'V1', 'V1', 'V2', 'V2')


def sha(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            value.update(chunk)
    return value.hexdigest()


def points_from_formal(path, count):
    # 只读取坐标，避免把千万级状态字符串和方块字典同时展开。
    points = np.empty((count, 3), dtype=np.int16)
    expression = re.compile(rb'"pos":\[(\d+),(\d+),(\d+)\]')
    cursor = 0
    with path.open('rb') as stream:
        assert stream.readline().endswith(b'"blocks":[\n'), '正式布局格式改变'
        tail = b''
        while chunk := stream.read(8 * 1024 * 1024):
            chunk = tail + chunk
            end = chunk.rfind(b'\n')
            data, tail = chunk[:end + 1], chunk[end + 1:]
            ending = data.find(b'],"ports":')
            if ending >= 0:
                data = data[:ending]
            coordinates = expression.findall(data)
            length = len(coordinates)
            assert cursor + length <= count, '正式布局实体计数越界'
            if length:
                points[cursor:cursor + length] = np.asarray(coordinates, dtype=np.int16)
                cursor += length
            if ending >= 0:
                break
    assert cursor == count, ('正式布局实体计数不符', cursor, count)
    return points


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--wait', action='store_true', help='等待同批正式资源逐台落盘')
    parser.add_argument('keys', nargs='*')
    arguments = parser.parse_args()
    selected = arguments.keys or KEYS
    if len(set(selected)) != len(selected) or any(key not in KEYS for key in selected):
        parser.error('机器键只能从i40至i45选择，且不能重复')
    OUT.mkdir(parents=True, exist_ok=True)
    old = {path: sha(path) for path in OVERLAYS.rglob('*.png')
           if not any(key + '_unique_r182' in path.parts for key in selected)}
    old_fronts = {digest for path, digest in old.items() if path.name == 'overlay_front.png'}
    records, patterns, new_fronts = [], set(), set()
    original_projection = faces.projected_geometry
    for key in selected:
        metadata_path = DATA / 'structures/approved' / (key + '.json')
        if arguments.wait and not metadata_path.is_file():
            print(json.dumps({'waiting_for_formal_resource': key}), flush=True)
            deadline = time.monotonic() + 3600
            while not metadata_path.is_file():
                if time.monotonic() >= deadline:
                    raise TimeoutError('正式资源尚未完成：' + key)
                time.sleep(2)
        meta = json.loads(metadata_path.read_text(encoding='utf-8'))
        layout = DATA / 'approved_architecture' / (key + '.json')
        digest = sha(layout)
        assert digest == meta['sha256'] and meta['revision'] == 182
        assert not meta['game_verified'], '不能把贴图生成标成游戏验收'
        points = points_from_formal(layout, meta['blocks'])
        projected = original_projection(points, 44, 37)
        # 三态共用同一轮廓，不重复投影数千万坐标。
        faces.projected_geometry = lambda value, width, height, margin=1: projected
        target = OVERLAYS / (key + '_unique_r182')
        target.mkdir(parents=True, exist_ok=True)
        textures = {}
        for state, suffix in faces.STATE_SUFFIX.items():
            picture, pattern = faces.candidate_face(points, meta['ports'], meta['controller'], state)
            destination = target / ('overlay_front' + suffix + '.png')
            picture.save(destination)
            assert picture.size == (64, 64)
            textures[state] = {'target': str(destination), 'sha256': sha(destination)}
        faces.projected_geometry = original_projection
        assert pattern not in patterns and textures['idle']['sha256'] not in old_fronts | new_fronts
        assert len({entry['sha256'] for entry in textures.values()}) == 3
        patterns.add(pattern)
        new_fronts.add(textures['idle']['sha256'])
        records.append({'key': key, 'approved_version': VERSIONS[KEYS.index(key)],
                        'machine': meta['machine'], 'formal_layout_sha256': digest,
                        'source_snapshot': meta['source_snapshot'],
                        'source_nbt_sha256': meta['source_nbt_sha256'],
                        'source_metadata_sha256': sha(metadata_path), 'blocks': meta['blocks'],
                        'geometry_pattern_sha256': pattern, 'textures': textures})
        del points
        print(json.dumps({'key': key, 'blocks': meta['blocks'], 'states': 3}), flush=True)
    assert all(sha(path) == digest for path, digest in old.items()), '旧贴图被改动'
    for entry in records:
        metadata = DATA / 'structures/approved' / (entry['key'] + '.json')
        assert sha(metadata) == entry['source_metadata_sha256'], '生成期间正式资源有更新，须刷新对应材质追溯'
    assert len({v['sha256'] for entry in records for v in entry['textures'].values()}) == len(selected) * 3
    receipt = {'revision': 182, 'keys': list(selected), 'entries': records,
               'old_pngs_unchanged': len(old), 'game_verified': False,
               'visual_method': '沿已采用的64像素金属边框，以各自批准几何、深度棱线和原位接口生成独立图案。',
               'old_controller_sha256': {str(path): value for path, value in old.items()}}
    suffix = '' if tuple(selected) == KEYS else '-' + '-'.join(selected)
    (OUT / ('controller-textures' + suffix + '.json')).write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    sheet = Image.new('RGB', (240 * len(records), 320), '#101827')
    draw = ImageDraw.Draw(sheet)
    for index, entry in enumerate(records):
        draw.text((index * 240 + 15, 8), entry['key'].upper(), fill='white')
        picture = Image.open(entry['textures']['idle']['target']).convert('RGB')
        sheet.paste(picture.resize((224, 224), Image.Resampling.NEAREST), (index * 240 + 8, 40))
    sheet.save(OUT / ('controller-texture-overview' + suffix + '.png'))


if __name__ == '__main__':
    main()
