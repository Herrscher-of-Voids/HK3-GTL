"""绘制采掘资料、舰船档案与侵蚀研究模块专用像素图。"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from item_texture_64 import canvas64, refine64
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'src/main/resources/assets/hk3gtl'
OUT = ROOT / 'logs/item-texture-refresh-20261112'


def mining_record():
    image, d = canvas64()
    d.polygon([(2, 1), (10, 1), (14, 5), (13, 14), (2, 14), (1, 12)], fill='#493f35')
    d.polygon([(3, 2), (9, 2), (9, 5), (13, 5), (12, 13), (3, 13), (2, 11)], fill='#c6ad75')
    d.polygon([(10, 2), (12, 4), (10, 4)], fill='#f4dfaa')
    d.line([(3, 3), (8, 3)], fill='#f4dfaa')
    d.line([(3, 8), (5, 7), (8, 7), (9, 6), (12, 6)], fill='#778255')
    d.line([(3, 10), (5, 9), (8, 10), (10, 9), (12, 9)], fill='#93754b')
    d.line([(4, 12), (6, 11), (9, 12), (12, 11)], fill='#9b8559')
    d.line([(4, 5), (5, 6), (5, 8), (7, 9), (9, 8), (10, 8)], fill='#39779a')
    d.line((9, 7, 11, 9), fill='#305c76')
    d.line((9, 9, 11, 7), fill='#305c76')
    d.point((10, 8), fill='#d9f2f0')
    d.point((4, 5), fill='#eef1c3')
    return image


def ship_archive():
    image, d = canvas64()
    d.polygon([(2, 1), (10, 1), (14, 5), (14, 14), (2, 14)], fill='#121c32')
    d.polygon([(3, 2), (9, 2), (9, 5), (13, 5), (13, 13), (3, 13)], fill='#284970')
    d.polygon([(10, 2), (12, 4), (10, 4)], fill='#638aac')
    d.line((3, 3, 7, 3), fill='#69b5ca')
    d.line((4, 5, 12, 5), fill='#356084')
    d.line((4, 9, 12, 9), fill='#356084')
    d.line((5, 5, 5, 12), fill='#356084')
    d.line((11, 6, 11, 12), fill='#356084')
    d.polygon([(8, 4), (10, 7), (10, 10), (8, 12), (6, 10), (6, 7)], outline='#bfe5eb')
    d.line((8, 5, 8, 11), fill='#6cd4ec')
    d.line((6, 8, 10, 8), fill='#94c3d7')
    d.line((4, 9, 6, 7), fill='#6cd4ec')
    d.line((10, 7, 12, 9), fill='#6cd4ec')
    d.point((8, 4), fill='#f0ffff')
    d.line((3, 12, 5, 12), fill='#69b5ca')
    d.point((12, 12), fill='#69b5ca')
    return image


def erosion_module():
    image, d = canvas64()
    for y in [4, 7, 10]:
        d.rectangle((0, y, 3, y + 1), fill='#73603b')
        d.rectangle((12, y, 15, y + 1), fill='#73603b')
        d.point((0, y), fill='#c4a364')
        d.point((15, y), fill='#c4a364')
    d.polygon([(4, 1), (11, 1), (13, 3), (13, 12), (11, 14), (4, 14), (2, 12), (2, 3)], fill='#292333')
    d.polygon([(4, 2), (11, 2), (12, 3), (12, 12), (11, 13), (4, 13), (3, 12), (3, 3)], fill='#79603e')
    d.line([(4, 2), (10, 2), (12, 4)], fill='#c3a16a')
    d.rectangle((4, 4, 11, 11), fill='#1e162c')
    d.polygon([(5, 5), (9, 4), (10, 7), (9, 10), (6, 11), (5, 8)], fill='#39274b')
    d.polygon([(6, 5), (8, 5), (8, 7), (10, 7), (8, 9), (6, 10), (7, 7)], fill='#654380')
    d.line([(6, 5), (7, 6), (7, 8), (6, 9)], fill='#ae7cce')
    d.line([(9, 10), (10, 9), (10, 8)], fill='#8753ab')
    for x, y in [(4, 3), (11, 3), (4, 12), (11, 12)]:
        d.point((x, y), fill='#e1c18b')
    return image


DRAWINGS = {
    'world_mining_legacy_record': (mining_record, '折角采掘航图、分层地貌、蓝色勘探线路与矿点叉标。', '原借用原版纸张'),
    'ship_engineering_archive': (ship_archive, '深蓝舰船工程图、俯视舰体轮廓、龙骨线与青白测绘线。', '原借用原版纸张'),
    'erosion_research_module': (erosion_module, '暗金八角机械框、双侧引脚、紫黑晶片与紫色侵蚀电路。', '原借用QSV处理器'),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    names = json.loads((ASSETS / 'lang/zh_cn.json').read_text(encoding='utf-8-sig'))
    records, models = [], []
    sheet = Image.new('RGB', (1000, 630), '#121b2a')
    d = ImageDraw.Draw(sheet)
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 20)
    small = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 15)
    for index, (ident, (paint, design, previous)) in enumerate(DRAWINGS.items()):
        texture = ASSETS / 'textures/item' / (ident + '.png')
        image = refine64(paint())
        image.save(texture, optimize=True)
        model = ASSETS / 'models/item' / (ident + '.json')
        backup = OUT / 'before/assets/hk3gtl/models/item' / model.name
        backup.parent.mkdir(parents=True, exist_ok=True)
        if not backup.exists():
            backup.write_bytes(model.read_bytes())
        ref = 'hk3gtl:item/' + ident
        model.write_text(json.dumps({'parent': 'minecraft:item/generated', 'textures': {'layer0': ref}}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        name = names['item.hk3gtl.' + ident]
        records.append({'id': ident, 'name': name, 'path': texture.relative_to(ASSETS).as_posix(), 'before_sha256': None, 'after_sha256': sha(texture), 'size': [64, 64], 'design': design})
        models.append({'path': model.relative_to(ASSETS).as_posix(), 'before_sha256': sha(backup), 'after_sha256': sha(model), 'texture': ref})
        y = index * 210
        d.text((24, y + 12), name, font=font, fill='#e8f1f8')
        d.text((24, y + 44), ident, font=small, fill='#91a8c4')
        d.text((40, y + 88), previous, font=font, fill='#8395ae')
        d.text((40, y + 122), '原无专用贴图', font=small, fill='#8395ae')
        enlarged = image.resize((128, 128), Image.Resampling.NEAREST)
        sheet.paste(enlarged, (350, y + 66), enlarged)
        d.text((505, y + 84), design[:26], font=small, fill='#b9d1e5')
        d.text((505, y + 112), design[26:], font=small, fill='#b9d1e5')
    source = ROOT / 'tools/research_r101_recipes.py'
    source_backup = OUT / 'before/tools/research_r101_recipes.py'
    source_backup.parent.mkdir(parents=True, exist_ok=True)
    if not source_backup.exists():
        source_backup.write_bytes(source.read_bytes())
    source.write_text(source.read_text(encoding='utf-8-sig').replace("'layer0':'minecraft:item/paper'", "'layer0':f'hk3gtl:item/{item}'"), encoding='utf-8')
    manifest = {'changed': records, 'model_changes': models, 'generator_change': {'path': 'tools/research_r101_recipes.py', 'before_sha256': sha(source_backup), 'after_sha256': sha(source)}}
    (OUT / 'record-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    sheet.save(OUT / '档案与侵蚀模块新旧对照.png', optimize=True)
    print('新增3张专用64×64静态材质，同步3个物品模型及2份资料的生成源。')


if __name__ == '__main__':
    main()
