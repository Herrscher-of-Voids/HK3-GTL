import hashlib
import json
import sys
from pathlib import Path

from PIL import Image

from sanitize_release_resources import strip_image_history, without


def optimize(resources, report):
    textures = []
    root = resources / 'assets/hk3gtl/textures'
    for path in sorted(root.rglob('*.png')):
        is_item = path.is_relative_to(root / 'item')
        metadata_path = Path(str(path) + '.mcmeta')
        metadata = without(json.loads(metadata_path.read_text('utf-8-sig')), {'_history'}) if metadata_path.exists() else {}
        animation = metadata.get('animation')
        with Image.open(path) as image:
            source_size = image.size
            frame = tuple(animation.get(key, min(image.size)) for key in ('width', 'height')) \
                if animation is not None else image.size
            if (is_item and max(frame) <= 64) or (not is_item and image.size != (1254, 1254)):
                continue
            original = path.read_bytes()
            edge = 64 if is_item else 128
            columns, rows = image.width // frame[0], image.height // frame[1]
            resized = Image.new('RGBA', (columns * edge, rows * edge))
            for y in range(rows):
                for x in range(columns):
                    tile = image.crop((x * frame[0], y * frame[1],
                        (x + 1) * frame[0], (y + 1) * frame[1]))
                    resized.paste(tile.resize((edge, edge), Image.Resampling.LANCZOS),
                        (x * edge, y * edge))
        resized.save(path, optimize=True, compress_level=9)
        strip_image_history(path)
        encoded = path.read_bytes()
        record = dict(path=path.relative_to(resources).as_posix(),
            source_size=list(source_size), runtime_size=list(resized.size),
            source_frame_size=list(frame), runtime_frame_size=[edge, edge],
            source_bytes=len(original), runtime_bytes=len(encoded),
            source_sha256=hashlib.sha256(original).hexdigest(),
            runtime_sha256=hashlib.sha256(encoded).hexdigest())
        if animation is not None:
            source_metadata = metadata_path.read_bytes()
            animation.update(width=edge, height=edge)
            metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
            record['metadata'] = dict(path=metadata_path.relative_to(resources).as_posix(),
                source_sha256=hashlib.sha256(source_metadata).hexdigest(),
                runtime_sha256=hashlib.sha256(metadata_path.read_bytes()).hexdigest())
        textures.append(record)
    record = dict(item_frame_size=[64, 64], large_texture_size=[128, 128], textures=textures,
        source_bytes=sum(item['source_bytes'] for item in textures),
        runtime_bytes=sum(item['runtime_bytes'] for item in textures))
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(f"运行物品贴图最大64×64，其他大贴图128×128：{len(textures)}张，{record['source_bytes']} → {record['runtime_bytes']}字节。")


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf8')
    optimize(Path(sys.argv[1]), Path(sys.argv[2]))
