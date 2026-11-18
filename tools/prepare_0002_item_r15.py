"""整理R15透明物品候选，不改源码或打包。"""
from datetime import datetime
from hashlib import sha256
from pathlib import Path
import json
import shutil

from PIL import Image, ImageDraw, ImageFont
from package_0002_item_r12 import candidate, thumbnail

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'output/imagegen/items-0002-r15'
OUT = ROOT / 'deliveries/0002贴图材质_运行绑定与流体轻量_R15_20261116'
LOG = ROOT / 'logs/textures-runtime-fixes-0002-r15-20261116'


def main():
    specs = []
    for group in ('abyss', 'archives', 'matrices'):
        specs.extend(json.loads((RAW / f'specs-{group}.json').read_text(encoding='utf-8-sig')))
    sheet = Image.new('RGB', (1220, 1140), '#18232e')
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 15)
    draw.text((16, 12), '0002 · R15 · 19项独立物品候选 · 未打包、未安装', font=font, fill='#e9f1f5')
    records = []
    for index, spec in enumerate(specs):
        identity = spec['id']
        folder = OUT / 'items' / identity
        folder.mkdir(parents=True, exist_ok=True)
        original = RAW / f'{identity}.png'
        png = folder / 'texture.png'
        image = candidate(spec, original, png)
        preview = thumbnail(image, 220)
        preview.save(folder / 'preview.png')
        shutil.copy2(original, folder / 'api-original.png')
        (folder / 'prompt.txt').write_text(spec['promptEn'], encoding='utf-8')
        x, y = index % 5 * 244 + 12, index // 5 * 274 + 48
        sheet.paste(preview, (x, y))
        draw.text((x, y + 225), spec['name'], font=font, fill='#e9f1f5')
        records.append({**spec, 'image': f'items/{identity}/texture.png',
                        'preview': f'items/{identity}/preview.png',
                        'original': f'items/{identity}/api-original.png',
                        'size': list(image.size), 'mode': image.mode,
                        'sha256': sha256(png.read_bytes()).hexdigest(),
                        'originalSha256': sha256(original.read_bytes()).hexdigest(),
                        'artApproved': False, 'sourceApplied': False})
    sheet.save(OUT / 'item-overview.png')
    manifest = {'revision': 'R15', 'conversation': '0002',
                'conversationId': '01a1d68a-a994-7ac0-a48a-54c0f98fd54e',
                'updatedAt': datetime.now().astimezone().isoformat(timespec='seconds'),
                'itemCount': len(records), 'records': records,
                'adapter': 'tools/invoke_image_relay.ps1 -Mode Generate -RelayResponse',
                'requestedSize': [1024, 1024], 'originalCanvasPreserved': True,
                'referenceImagesUploaded': 0, 'sourceApplied': False,
                'jarBuilt': False, 'installed': False, 'gameTested': False,
                'decision': '负责人要求先别打包；仅整理候选供查看。',
                'discarded': '海渊四件首稿误用方块面前缀，已隔离至原图目录discarded-block-prefix；未采用。'}
    for target in (OUT / 'item-manifest.json', LOG / 'item-candidates.json'):
        target.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'items': len(records), 'size': sorted({tuple(r['size']) for r in records}),
                      'sourceApplied': False, 'jarBuilt': False, 'installed': False}))


if __name__ == '__main__':
    main()
