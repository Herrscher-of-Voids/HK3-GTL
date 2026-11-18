import gzip
from io import BytesIO
import json
import lzma
from pathlib import Path
import re
import struct
import sys
from zipfile import ZipFile
import zlib


RUNTIME = re.compile(
    r'com/sirin/hk3gtl/.+\.class|'
    r'assets/hk3gtl/(?:lang/(?:zh_cn|en_us)\.json|'
    r'ftbquests/chapters/hk3_(?:stargate|multiblock_patterns|industrial_(?:early|world|late)|voltage_(?:0[1-9]|1[0-6]))\.snbt|changelog\.json|'
    r'narrative/(?:approved|easter_eggs|easter_rules|faction_first_contacts|progress_correspondence|'
    r'social_dialogues|social_personas|story)\.json|'
    r'(?:models|blockstates)/.+\.json|models/scene/.+\.bin\.(?:gz|xz)|'
    r'textures/.+\.png(?:\.mcmeta)?|shaders/.+\.(?:json|fsh|vsh)|(?:effects|wonder)/.+\.bin\.gz)|'
    r'data/hk3gtl/(?:structures/(?:approved/[^/]+\.json|.+\.bin\.(?:gz|xz)|ae_nexus_a1\.nbt|jei_materials/(?:i\d+(?:_\d+)?|s\d+)\.txt)|'
    r'catalog/(?:industrial_(?:content|expansion_fluids|expansion_items|support_items)|natural_supply_sources|world_bubble_resources|multiblock_pattern_library)\.json|'
    r'(?:advancements|calendar|compact_architecture|dimension|dimension_type|guide|loot_tables|'
    r'narrative|recipes|research|sgjourney|worldgen)/.+\.json)|'
    r'data/(?:forge|gtceu)/tags/items/.+\.json|data/minecraft/tags/blocks/.+\.json|'
    r'pack\.mcmeta|hk3gtl\.mixins\.json|[^/]+-refmap\.json|'
    r'META-INF/(?:MANIFEST\.MF|mods\.toml|jarjar/metadata\.json|jars/(?:mixinextras-forge-[^/]+|xz-1\.10)\.jar)'
)
DEVELOPMENT_CLASSES = re.compile(
    r'com/sirin/hk3gtl/common/(?:registration/Hk3Industrial(?:AuditReport|DependencyAudit)|'
    r'command/Hk3LiquidLine(?:Audit|RuntimeCheck))(?:\$[^/]+)?\.class'
)
PRIVATE = re.compile(
    rb'"(?:[a-z_]*_quote|conversation_id|approval_basis|approval_manifest|authorization|'
    rb'runtime_provenance|_comment[a-z_0-9]*|_history|dev_note|internal_note)"\s*:|'
    rb'\b01a1[0-9a-f]{4}-[0-9a-f-]{27}\b|[A-Za-z]:[/\\]+(?:Users|Prism|AI)[/\\]+|'
    rb'"(?:deliveries|source_archives|logs)/(?!hk3gtl-)|' +
    r'(?:负责人(?:原话|要求|明确批准|授权)|用户原话|对话原话|审核原话|审核备注|开发备注|授权备注|正文校对|已审核正文|变更记录|修订\s*(?:#|＃|:|：)?\s*[0-9]+|第(?:[0-9]+|一|二|三|四|五|六|七|八|九|十)+次备注)'.encode('utf-8')
)

MARKERS = tuple(f.encode('utf-8') for f in (
    '_quote', 'conversation_id', 'approval_basis', 'approval_manifest', 'authorization',
    'runtime_provenance', '_comment', '_history', 'dev_note', 'internal_note', '01a1',
    '"deliveries/', '"source_archives/', '"logs/', '负责人', '用户原话', '对话原话', '审核原话', '审核备注', '开发备注', '授权备注', '正文校对', '已审核正文', '变更记录', '修订', '次备注',
)) + tuple((separator + folder).encode('ascii') for separator in (':/', ':\\', ':\\\\')
          for folder in ('Users', 'Prism', 'AI'))


def review_quotes(resources):
    structures = resources / 'data/hk3gtl/structures'
    fields = re.compile(rb'"(?:[a-z_]*_quote|approval_basis|authorization)"\s*:\s*("(?:[^"\\]|\\.)*")')
    paths = [*structures.glob('w*_approved.json'), *(structures / 'approved').glob('*.json'),
             resources / 'data/hk3gtl/catalog/world_bubble_resources.json']
    values = {json.loads(match) for path in paths for match in fields.findall(path.read_bytes())}
    return tuple(value.encode('utf-8') for value in sorted(values) if len(value) >= 12)


def contains_private(part, quotes):
    return (part.startswith(b'XML:com.adobe.xmp')
            or (any(marker in part for marker in MARKERS) and PRIVATE.search(part))
            or any(q in part for q in quotes))


def png_metadata(raw):
    offset = 8
    while offset < len(raw):
        length, kind = struct.unpack_from('>I4s', raw, offset)
        chunk = raw[offset + 8:offset + length + 8]
        offset += length + 12
        if kind == b'zTXt':
            key, rest = chunk.split(b'\0', 1)
            yield key + zlib.decompress(rest[1:])
        elif kind == b'iTXt':
            key, rest = chunk.split(b'\0', 1)
            _, _, text = rest[2:].split(b'\0', 2)
            yield key + (zlib.decompress(text) if rest[0] else text)
        elif kind in (b'tEXt', b'eXIf'):
            yield chunk


def compressed_metadata(archive, name):
    codec = lzma.open if name.endswith('.xz') else gzip.open
    with archive.open(name) as stream, codec(stream, 'rb') as decoded:
        tail = b''
        while chunk := decoded.read(1024 * 1024):
            yield tail + chunk
            tail = chunk[-512:]


def audit(path, quotes=()):
    files = 0
    problems = []
    with ZipFile(path) as archive:
        for item in archive.infolist():
            if item.is_dir():
                continue
            files += 1
            name = item.filename
            if DEVELOPMENT_CLASSES.fullmatch(name):
                problems.append((name, '开发核验类不属于正式发布范围'))
            elif not RUNTIME.fullmatch(name):
                problems.append((name, '不在正式发布文件范围'))
            if name.endswith('.jar'):
                with ZipFile(BytesIO(archive.read(item))) as dependency:
                    if any(contains_private(dependency.read(entry), quotes) for entry in dependency.infolist() if not entry.is_dir()):
                        problems.append((name, '内嵌依赖包含内部记录或开发路径'))
                continue
            if name.endswith(('.gz', '.xz', '.nbt')):
                content = compressed_metadata(archive, name)
            elif name.endswith('.png'):
                content = png_metadata(archive.read(item))
            else:
                content = (archive.read(item),)
            if any(contains_private(part, quotes) for part in content):
                problems.append((name, '包含内部记录或开发路径'))
    return {'jar': str(path), 'entries': files, 'findings': problems}


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    result = audit(Path(sys.argv[1]), review_quotes(Path(sys.argv[2])))
    for name, reason in result['findings']:
        print(f'{reason}：{name}')
    print(f"正式 JAR 文件核对：{result['entries']} 项，问题 {len(result['findings'])} 项。")
    sys.exit(bool(result['findings']))
