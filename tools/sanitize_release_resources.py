import json
from pathlib import Path
import struct
import sys


STRUCTURE_FIELDS = set('key machine controller size size_xyz'.split())
COMPACT_FIELDS = STRUCTURE_FIELDS | set('target_voltage blocks ports material_counts layout_state_overrides layout_records_sha256 compact_records_sha256 compact_sha256 source_architecture_sha256 runtime_format'.split())
ART_REPORTS = 'circuit_art75 electronic_art74 gt_circuit_assets voltage_art108 electronic_components voltage_casings voltage_palette circuit_series'.split()


def without(value, fields):
    if isinstance(value, dict):
        return {key: without(item, fields) for key, item in value.items()
                if key not in fields and not key.endswith('_quote') and not key.startswith('_comment')}
    if isinstance(value, list):
        return [without(item, fields) for item in value]
    return value


def select(value, fields):
    return {key: item for key, item in value.items() if key in fields}


def transform(path, project):
    value = json.loads(path.read_bytes())
    public = project(value)
    if public != value:
        path.write_text(json.dumps(public, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')


def strip_image_history(path):
    original = path.read_bytes()
    if b'XML:com.adobe.xmp\0' not in original:
        return
    chunks = [original[:8]]
    offset = 8
    while offset < len(original):
        length, kind = struct.unpack_from('>I4s', original, offset)
        end = offset + length + 12
        if kind != b'iTXt' or not original.startswith(b'XML:com.adobe.xmp\0', offset + 8):
            chunks.append(original[offset:end])
        offset = end
    public = b''.join(chunks)
    if public != original:
        path.write_bytes(public)


def sanitize(root):
    data = root / 'data/hk3gtl'
    assets = root / 'assets/hk3gtl'
    for pattern, fields in [('structures/approved/*.json', STRUCTURE_FIELDS), ('compact_architecture/*.json', COMPACT_FIELDS)]:
        for path in data.glob(pattern):
            transform(path, lambda value: select(value, fields))
    for name in ART_REPORTS:
        (data / 'catalog' / (name + '.json')).unlink(missing_ok=True)
    for directory, pattern in ((assets / 'models', '*.json'), (assets / 'textures', '*.mcmeta'),
                               (root / 'data/forge/tags', '*.json'), (root / 'data/gtceu/tags', '*.json')):
        for path in directory.rglob(pattern):
            transform(path, lambda value: without(value, {'_history'}))
    for path in assets.rglob('*.png'):
        strip_image_history(path)
    transform(data / 'catalog/world_bubble_resources.json', lambda value: select(value,
        {'schema', 'profile', 'version', 'sampling', 'roots', 'processed', 'remaining', 'catalog_hash'}))
    for path, fields in (
        (data / 'research/approved_industrial_processes.json', {'source'}),
        (data / 'research/industrial_processes.json', {'balance_note'}),
        (data / 'research/research_execution.json', {'structure_approval'}),
        (assets / 'models/scene/cocoon_review.json', {'runtime_provenance', 'description'}),
        (assets / 'narrative/approved.json', {'source'}),
    ):
        transform(path, lambda value: without(value, fields))


if __name__ == '__main__':
    sanitize(Path(sys.argv[1]))
