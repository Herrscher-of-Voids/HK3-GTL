"""将百万格生产蓝图导出为两格厚空心结构。"""
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import time

from structure_delivery.hollow_blueprint import HollowBlueprint, read_header
from structure_delivery.hollow_scene_resources import scene_protected_linear, sync_scene_resources


THRESHOLD = 1_000_000
THICKNESS = 2


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(chunk)
    return value.hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf8')


def structures(resources):
    directory = resources / 'data/hk3gtl/structures'
    for path in sorted((directory / 'compact').glob('*.bin.gz')):
        key = path.name.removesuffix('.bin.gz')
        yield key, path, resources / 'data/hk3gtl/compact_architecture' / (key + '.json')
    for index in range(1, 16):
        key = f'w{index:02}'
        name = {1: 'w01_hall', 2: 'w02_19c_a2', 3: 'w03_c9'}.get(index, key + '_candidate')
        yield key, directory / (name + '.bin.gz'), None
    yield 'hyperion', directory / 'hyperion_construction.bin.gz', None


def protected_positions(metadata, shape):
    _, height, depth = shape
    positions = [int(position) for position in metadata.get('layout_state_overrides', {})]
    positions.extend((port['pos'][0] * height + port['pos'][1]) * depth + port['pos'][2]
                     for port in metadata.get('ports', []))
    return positions


def material_counts(palette, counts):
    result = Counter()
    for state, count in zip(palette, counts):
        result[state] += int(count)
    return +result


def update_metadata(path, metadata, hollow, result):
    counts = Counter(metadata['material_counts'])
    for state, change in zip(hollow.palette, hollow.counts_after - hollow.counts_before):
        counts[state] += int(change)
    metadata['blocks'] = result['after']
    metadata['material_counts'] = dict(sorted((+counts).items()))
    metadata['compact_sha256'] = result['sha256']
    metadata['runtime_format'] += '; hollow shell=2'
    source_hashes = {key: metadata.pop(key) for key in
                     ('compact_records_sha256', 'layout_records_sha256') if key in metadata}
    if 'materials' in metadata:
        metadata['materials'] = len(+counts)
    write_json(path, metadata)
    return source_hashes


def process_structure(job):
    resources, key, path, metadata_path = job
    resources, path = Path(resources), Path(path)
    metadata_path = Path(metadata_path) if metadata_path else None
    started = time.monotonic()
    header = read_header(path)
    metadata = json.loads(metadata_path.read_text('utf8')) if metadata_path else {}
    protected = protected_positions(metadata, header['shape'])
    protected.extend(scene_protected_linear(resources, key, header['shape']).tolist())
    before = dict(sha256=digest(path), bytes=path.stat().st_size)
    with tempfile.TemporaryDirectory(prefix='hk3-hollow-' + key + '-') as temporary:
        hollow = HollowBlueprint(path, temporary, thickness=THICKNESS, protected_linear=protected).prepare()
        result = hollow.write(path)
        result.update(key=key, path=path.relative_to(resources).as_posix(), source=before,
                      size_xyz=list(header['shape']), controller_xyz=list(header['controller']))
        if metadata_path:
            result['source_record_hashes'] = update_metadata(metadata_path, metadata, hollow, result)
            index = resources / 'data/hk3gtl/structures/jei_materials' / (key + '.txt')
            states = set(material_counts(hollow.palette, hollow.counts_after))
            states.update(metadata.get('layout_state_overrides', {}).values())
            index.parent.mkdir(parents=True, exist_ok=True)
            index.write_text(''.join(state + '\n' for state in sorted(states)), encoding='utf8')
        result['scene'] = sync_scene_resources(resources, key, hollow)
        result['material_counts'] = dict(sorted(material_counts(hollow.palette, hollow.counts_after).items()))
    result['elapsed_seconds'] = round(time.monotonic() - started, 3)
    return result


def main():
    resources, report = map(Path, sys.argv[1:])
    resources = resources.resolve()
    jobs = [(str(resources), key, str(path), str(metadata_path) if metadata_path else None)
            for key, path, metadata_path in structures(resources) if read_header(path)['count'] >= THRESHOLD]
    report.parent.mkdir(parents=True, exist_ok=True)
    completed = {}
    with ProcessPoolExecutor(max_workers=min(int(os.environ.get("HK3GTL_HOLLOW_WORKERS", "4")), len(jobs))) as pool:
        futures = {pool.submit(process_structure, job): index for index, job in enumerate(jobs)}
        for future in as_completed(futures):
            index = futures[future]
            result = future.result()
            completed[index] = result
            print(json.dumps({field: result[field] for field in ('key', 'before', 'after', 'removed', 'elapsed_seconds')},
                             ensure_ascii=False), flush=True)
            records = [completed[index] for index in sorted(completed)]
            write_json(report, dict(threshold=THRESHOLD, shell_thickness=THICKNESS, structures=records))
    records = [completed[index] for index in range(len(jobs))]
    totals = dict(structures=len(records), blocks_before=sum(row['before'] for row in records),
                  blocks_after=sum(row['after'] for row in records), removed=sum(row['removed'] for row in records))
    result = dict(recorded_at=datetime.now().astimezone().isoformat(), threshold=THRESHOLD,
                  shell_thickness=THICKNESS, summary=totals, structures=records)
    write_json(report, result)
    print(json.dumps(totals), flush=True)


if __name__ == '__main__':
    main()
