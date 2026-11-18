from pathlib import Path
import hashlib
import json
import math
import shutil

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'src/main/resources/assets/hk3gtl'
TEXTURES = ASSETS / 'textures/block/fluids'
REPORT = ROOT / 'logs/fluid-texture-refresh-20261112'
BACKUP = REPORT / 'before'
TAU = math.tau

# ID、流纹、深底至高光的五级配色、透明度、颗粒形状、相位。
FLUIDS = [
    ('liquid_honkai_energy', 'veins', '341447 542067 7b2fbe a65fe0 d6a3f3', 255, '', 0),
    ('crude_honkai_energy', 'sludge', '302136 493047 68465e 865780 b57dba', 255, 'sediment', 1),
    ('clarified_honkai_mother_liquor', 'ripples', '4b365f 6e4e91 916abd b595db d9c4ef', 228, 'fine', 2),
    ('honkai_mother_liquor', 'eddies', '382340 573654 795473 a0789a c6a2c8', 255, 'seed', 3),
    ('stabilized_liquid_honkai_energy', 'cells', '402553 62357f 8651b4 b37ae0 dac0f2', 255, '', 1),
    ('honkai_separation_medium', 'bands', '1c3c4a 285a6d 3a8295 70b4bd b2dee0', 232, '', 2),
    ('honkai_stabilization_medium', 'ripples', '29394d 445778 6979a1 99a9cc ced9eb', 240, 'fine', 1),
    ('spent_honkai_stabilization_medium', 'sludge', '34343c 4b4853 65626f 85818d a9a2b1', 255, 'sediment', 3),
    ('spent_analysis_reagent', 'droplets', '494438 67604c 858263 a3a486 c6c3a1', 245, 'sediment', 2),
    ('honkai_analysis_reagent', 'droplets', '183d4a 245c6e 3f8998 7bbec4 c1e8e7', 220, 'fine', 0),
    ('unrecoverable_process_effluent', 'sludge', '282c29 3d4138 555749 74735f 96927a', 255, 'sediment', 0),
    ('liquid_honkai_fuel', 'folds', '3c183e 602251 8e396f b45a90 e295c0', 255, '', 1),
    ('concentrated_liquid_honkai_fuel', 'rifts', '281332 481744 72215e a23d82 e284bc', 255, 'fine', 2),
    ('fuel_refining_residual', 'bands', '3e292d 5c3c3f 7e5256 9f7471 c9a397', 255, 'sediment', 1),
    ('crystallization_residual_liquid', 'crystals', '392b4b 564269 7e608d aa8bb7 d5c2d9', 244, 'shards', 2),
    ('soulium_precursor_fluid', 'suspension', '494b58 6c6974 8d8790 b5adb2 ddd4d3', 255, 'flakes', 1),
    ('soulium_process_solvent', 'ripples', '54442a 7a6239 a78951 d1b87c eee0af', 222, 'fine', 3),
    ('spent_soulium_solvent', 'sludge', '38332d 534d3f 746b53 968b70 bcb08f', 255, 'flakes', 2),
    ('nano_reaction_tail_liquid', 'suspension', '243a3d 3d5354 617473 8c9f99 bfcec2', 248, 'flakes', 3),
    ('honkai_resistant_coating', 'folds', '39334e 57516d 7a748f a19db6 ccc9df', 255, '', 2),
    ('spent_resistant_coating', 'rifts', '3e383c 5e515a 7b6871 9b8892 c4b1ba', 255, 'shards', 0),
    ('gaseous_honkai_energy', 'gas_curl', '56336b 75478f 9866b5 bd95d8 e0c7ed', 110, '', 0),
    ('soulium_protective_gas', 'gas_veil', '65818c 84a0a9 a5bec5 c8d9dc e7eff0', 82, '', 1),
    ('spent_soulium_process_gas', 'gas_cloud', '4c493e 6d6655 90846d b5a68b dbccb1', 138, 'fine', 2),
    ('hot_soulium_exhaust', 'gas_rise', '604539 855b47 b47a56 d9a778 f2d9aa', 122, '', 3),
    ('bubble_confinement_medium', 'cells', '193f4d 285f75 4b859c 80b4c4 bce0e5', 224, '', 2),
    ('world_stabilization_medium', 'woven', '302a50 4b426e 716694 9f93bc cfc5e2', 238, 'fine', 1),
    ('spent_world_stabilization_medium', 'rifts', '363643 514d62 6f657e 9489a3 bfb3c9', 252, 'sediment', 2),
    ('honkai_coolant', 'streams', '123b52 1d6180 3394ad 78c9d4 c3f0ed', 236, '', 0),
    ('hot_honkai_coolant', 'convection', '473c51 725368 a77979 d6a893 f7dfbc', 244, 'bubble', 2),
    ('lost_coolant_residue', 'sludge', '2c3b3a 455654 63736b 89958a b3bbae', 255, 'sediment', 1),
    ('fuel_waste_processing_fluid', 'convection', '48362d 695342 95724d bf9b68 e4c590', 255, 'flakes', 3),
    ('circuit_growth_medium', 'dendrites', '173d3c 245e55 3d8973 77b99b b9dfbf', 242, 'seed', 1),
    ('spent_circuit_growth_medium', 'suspension', '2f3b2e 4c5840 6d7957 98a27b c4cbab', 255, 'shards', 0),
    ('honkai_circuit_etchant', 'droplets', '3c4a24 607331 91a54a bbc76f e4e6ac', 234, 'bubble', 2),
    ('spent_honkai_etchant', 'eddies', '43352c 654a37 8b6948 b68e67 d9b98e', 255, 'sediment', 1),
    ('stable_transport_medium', 'laminar', '263c5a 3e5d7e 6488ac 9db9d3 d5e5f0', 232, '', 3),
    ('soulium', 'metal', '4b4d64 737487 999ba9 c0c8d0 edeff3', 255, '', 0),
]


def field(style, x, y):
    u, v = x * TAU / 16, y * TAU / 16
    if style == 'veins':
        return .5 + .3 * math.sin(u + .9 * math.sin(v)) + .18 * math.cos(v * 2 - u)
    if style == 'sludge':
        return .45 + .23 * math.sin(u + math.cos(v)) + .19 * math.cos(v * 2 + .4 * math.sin(u))
    if style == 'ripples':
        return .5 + .21 * math.sin(v * 2 + .5 * math.cos(u)) + .12 * math.cos(u + v)
    if style == 'eddies':
        return .5 + .24 * math.sin(u + 1.4 * math.sin(v)) + .21 * math.cos(v - math.sin(u))
    if style == 'cells':
        value = math.cos(u) * math.cos(v) + .28 * math.cos(2 * u + v)
        return .27 + .72 * max(0, 1 - abs(value) * 2.2)
    if style == 'bands':
        return .5 + .28 * math.cos(v * 2 + .6 * math.sin(u)) + .1 * math.cos(u * 2)
    if style == 'droplets':
        return .4 + .19 * math.cos(u + v) + .17 * math.sin(v * 2 - u * 2)
    if style == 'folds':
        return .46 + .29 * math.sin(u + v + .65 * math.sin(v * 2)) + .12 * math.cos(u - v)
    if style == 'rifts':
        return .25 + .7 * max(0, 1 - abs(math.sin(u + .55 * math.sin(v * 2))) * 2.3)
    if style == 'crystals':
        return .43 + .14 * math.cos(u * 2) + .18 * math.sin(v + .6 * math.sin(u))
    if style == 'suspension':
        return .45 + .19 * math.sin(u + v) + .12 * math.cos(u * 2 - v)
    if style == 'gas_curl':
        return .38 + .32 * math.sin(u + 1.3 * math.cos(v)) + .13 * math.cos(v * 2 + u)
    if style == 'gas_veil':
        return .36 + .24 * math.cos(v + .65 * math.sin(u)) + .1 * math.sin(2 * u - v)
    if style == 'gas_cloud':
        return .42 + .22 * math.cos(u) * math.cos(v) + .17 * math.sin(2 * u + v)
    if style == 'gas_rise':
        return .36 + .27 * math.sin(u * 2 + .8 * math.sin(v)) + .17 * math.cos(v + u)
    if style == 'woven':
        return .44 + .26 * math.cos(u + .8 * math.sin(v)) * math.cos(v - .8 * math.sin(u))
    if style == 'streams':
        return .47 + .28 * math.cos(u + .45 * math.sin(v * 2)) + .1 * math.cos(u * 3 - v)
    if style == 'convection':
        return .5 + .2 * math.cos(u + .9 * math.sin(v)) + .22 * math.cos(v - .9 * math.sin(u))
    if style == 'dendrites':
        return .29 + .24 * math.sin(u + v) + .18 * math.cos(u - v * 2)
    if style == 'laminar':
        return .46 + .25 * math.cos(v + .35 * math.sin(u)) + .08 * math.cos(2 * v + u)
    if style == 'metal':
        return .5 + .29 * math.cos(v + .6 * math.sin(u)) + .15 * math.cos(3 * v + .4 * math.sin(u))


def marks(image, kind, palette, phase, flow):
    d = ImageDraw.Draw(image)
    shift = phase * 2
    for x, y in ((2, 3), (11, 8), (6, 13)):
        x, y = (x + shift // 2) % 16, (y + (shift if flow else shift // 2)) % 16
        for sx in (-16, 0, 16):
            for sy in (-16, 0, 16):
                a, b = x + sx, y + sy
                if kind == 'sediment':
                    d.rectangle((a, b, a + 2, b + 1), fill=palette[0])
                    d.point((a + 1, b + 2), fill=palette[1])
                elif kind == 'fine':
                    d.point((a, b), fill=palette[3])
                elif kind == 'seed':
                    d.line((a, b + 1, a + 2, b + 1), fill=palette[3])
                    d.point((a + 1, b), fill=palette[4])
                elif kind == 'flakes':
                    d.polygon(((a, b), (a + 2, b), (a + 1, b + 2)), fill=palette[3])
                    d.point((a, b), fill=palette[4])
                elif kind == 'shards':
                    d.line((a, b + 2, a + 2, b, a + 3, b + 2), fill=palette[3])
                    d.point((a + 2, b + 1), fill=palette[4])
                elif kind == 'bubble':
                    d.rectangle((a, b, a + 2, b + 2), outline=palette[3])
                    d.point((a, b), fill=palette[4])


def render(spec, flow):
    ident, style, colors, opacity, grain, phase = spec
    rgb = [tuple(bytes.fromhex(color)) for color in colors.split()]
    gas = style.startswith('gas_')
    alpha = (18, 34, 55, 80, opacity) if gas else (opacity,) * 5
    palette = [color + (a,) for color, a in zip(rgb, alpha)]
    result = Image.new('RGBA', (16, 64))
    for frame in range(4):
        image = Image.new('RGBA', (16, 16))
        for y in range(16):
            for x in range(16):
                px = (x + phase * 3 + (0 if flow or style == 'folds' else frame * 4)) % 16
                py = (y + phase * 2 - frame * 4) % 16
                if flow:
                    px = (px + .55 * math.sin(py * TAU / 16)) % 16
                value = field(style, px, py)
                level = min(4, max(0, int(value * 5)))
                image.putpixel((x, y), palette[level])
        if style == 'dendrites':
            d = ImageDraw.Draw(image)
            for sx in (-16, 0, 16):
                for sy in (-16, 0, 16):
                    a, b = sx + frame * 4, sy - frame * 4
                    d.line((a + 1, b + 13, a + 5, b + 9, a + 5, b + 6, a + 9, b + 2), fill=palette[3])
                    d.line((a + 5, b + 9, a + 9, b + 9, a + 12, b + 6), fill=palette[4])
                    d.line((a + 5, b + 6, a + 2, b + 4), fill=palette[3])
        marks(image, grain, palette, frame + phase, flow)
        result.paste(image, (0, frame * 16))
    return result


def preserve(path, absent):
    target = BACKUP / path.relative_to(ASSETS)
    if path.relative_to(ASSETS).as_posix() in absent:
        return None
    if path.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            shutil.copy2(path, target)
        return hashlib.sha256(target.read_bytes()).hexdigest()
    return None


def main():
    REPORT.mkdir(parents=True, exist_ok=True)
    TEXTURES.mkdir(parents=True, exist_ok=True)
    manifest_path = REPORT / 'fluid-manifest.json'
    previous = json.loads(manifest_path.read_text(encoding='utf-8')) if manifest_path.exists() else []
    absent = {row['path'] for row in previous if row['before_sha256'] is None}
    absent.update(row['metadata_path'] for row in previous if row['metadata_before_sha256'] is None)
    manifest = []
    sheet = Image.new('RGB', (1280, 1400), '#1b232b')
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for index, spec in enumerate(FLUIDS):
        ident, style, colors, opacity, grain, phase = spec
        for flow in (False, True):
            path = TEXTURES / ('fluid.' + ident + ('_flow' if flow else '') + '.png')
            before = preserve(path, absent)
            meta = Path(str(path) + '.mcmeta')
            meta_before = preserve(meta, absent)
            if not meta.exists():
                meta.write_text(json.dumps({'animation': {'frametime': 5, 'interpolate': True}}, indent=2) + '\n', encoding='utf-8')
            image = render(spec, flow)
            image.save(path, optimize=True)
            manifest.append({
                'path': path.relative_to(ASSETS).as_posix(),
                'before_sha256': before,
                'after_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                'size': list(image.size),
                'frames': 4,
                'frametime': 5,
                'interpolate': True,
                'kind': '气体' if style.startswith('gas_') else '液体',
                'texture': '流动' if flow else '静止',
                'pattern': style,
                'palette': colors.split(),
                'metadata_path': meta.relative_to(ASSETS).as_posix(),
                'metadata_before_sha256': meta_before,
                'metadata_after_sha256': hashlib.sha256(meta.read_bytes()).hexdigest(),
            })
        x, y = index % 8 * 160, index // 8 * 280
        for frame in range(4):
            for flow in (False, True):
                tile = render(spec, flow).crop((0, frame * 16, 16, frame * 16 + 16)).resize((32, 32), Image.Resampling.NEAREST)
                sheet.paste(tile, (x + 6 + frame * 36, y + 6 + int(flow) * 36), tile)
        label = ident.replace('_', ' ')
        words, lines, line = label.split(), [], ''
        for word in words:
            if len(line) + len(word) > 22:
                lines.append(line)
                line = word
            else:
                line += (' ' if line else '') + word
        lines.append(line)
        draw.multiline_text((x + 6, y + 82), '\n'.join(lines), fill='#d5e4ee', font=font, spacing=1)
        old = BACKUP / 'textures/block/fluids' / ('fluid.' + ident + '.png')
        if old.exists():
            tile = Image.open(old).crop((0, 0, 16, 16)).resize((48, 48), Image.Resampling.NEAREST)
            sheet.paste(tile, (x + 6, y + 130), tile)
        draw.text((x + 62, y + 147), 'BEFORE', fill='#9aabb8', font=font)
        for tx in range(3):
            for ty in range(2):
                tile = render(spec, False).crop((0, 0, 16, 16)).resize((32, 32), Image.Resampling.NEAREST)
                sheet.paste(tile, (x + 6 + tx * 32, y + 190 + ty * 32), tile)
    sheet.save(REPORT / 'fluid-contact-sheet.png')
    (REPORT / 'fluid-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    sources = REPORT / 'sources'
    sources.mkdir(exist_ok=True)
    shutil.copy2(Path(__file__), sources / Path(__file__).name)
    print(json.dumps({'fluids': len(FLUIDS), 'png': len(manifest), 'new_png': sum(row['before_sha256'] is None for row in manifest), 'manifest': str(REPORT / 'fluid-manifest.json')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
