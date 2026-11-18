"""重画世界泡族十五件模板物品，保留两件已批准精修资源。"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from item_texture_64 import canvas64, refine64
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'src/main/resources/assets/hk3gtl'
OUT = ROOT / 'logs/item-texture-refresh-20261112'
INK, DARK, MID, STEEL, SILVER = '#111825', '#253345', '#526780', '#8da4b7', '#d9e8eb'
BLUE, CYAN, LIGHT = '#356ea9', '#43bac9', '#b1f3ee'
VIOLET, LILAC, PALE = '#6947a2', '#ad82d8', '#e9d5fa'
GOLD, BRASS, AMBER = '#e6c17a', '#8a663c', '#d88b37'
RED, RED_DARK = '#dc685a', '#663441'


def canvas():
    return canvas64()


def spatial_probe():
    im, d = canvas()
    d.line((8, 1, 8, 7), fill=INK, width=3)
    d.line((8, 1, 8, 5), fill=SILVER)
    d.polygon([(5, 3), (6, 1), (10, 1), (12, 3), (10, 4), (7, 4)], fill=INK)
    d.line([(6, 2), (9, 2), (11, 3)], fill=LIGHT)
    d.polygon([(5, 6), (10, 5), (12, 8), (10, 12), (5, 11), (3, 8)], fill=INK)
    d.polygon([(5, 7), (9, 6), (11, 8), (9, 10), (5, 10)], fill=MID)
    d.rectangle((6, 7, 9, 9), fill=BLUE)
    d.line((6, 7, 8, 7), fill=CYAN)
    d.point((7, 8), fill=LIGHT)
    d.polygon([(3, 6), (1, 7), (1, 10), (4, 9)], fill=INK)
    d.line((2, 7, 2, 9), fill=GOLD)
    d.polygon([(12, 6), (14, 5), (14, 9), (11, 9)], fill=INK)
    d.line((13, 6, 13, 8), fill=GOLD)
    d.polygon([(6, 11), (9, 11), (8, 15)], fill=INK)
    d.line((7, 12, 7, 14), fill=CYAN)
    return im


def work_drone(worn=False):
    im, d = canvas()
    d.line((3, 4, 12, 11), fill=INK, width=3)
    d.line((12, 4, 3, 11), fill=INK, width=3)
    d.line((3, 4, 12, 11), fill=STEEL)
    d.line((12, 4, 3, 11), fill=MID)
    for x, y in [(0, 1), (10, 1), (0, 9), (10, 9)]:
        d.ellipse((x, y, x + 5, y + 3), fill=INK)
        d.line((x + 1, y + 1, x + 4, y + 1), fill=STEEL)
        d.point((x + 2, y + 2), fill=CYAN)
    d.polygon([(5, 4), (9, 4), (11, 6), (10, 10), (5, 10), (4, 7)], fill=INK)
    d.polygon([(6, 5), (9, 5), (10, 7), (9, 9), (5, 8)], fill=MID)
    d.line((6, 5, 9, 5), fill=SILVER)
    d.rectangle((6, 6, 8, 8), fill=BRASS)
    d.point((6, 6), fill=GOLD)
    d.line([(6, 10), (5, 12), (3, 13), (4, 14)], fill=INK, width=2)
    d.line([(9, 10), (10, 12), (12, 13), (11, 14)], fill=INK, width=2)
    d.line([(6, 11), (5, 12), (4, 13)], fill=STEEL)
    d.line([(9, 11), (10, 12), (11, 13)], fill=STEEL)
    if worn:
        d.rectangle((10, 1, 15, 4), fill=(0, 0, 0, 0))
        d.line([(10, 5), (12, 4), (13, 5)], fill=BRASS)
        d.line([(6, 5), (7, 6), (6, 7), (8, 8)], fill=INK)
        d.point((9, 7), fill=RED)
        d.point((2, 10), fill=AMBER)
        d.rectangle((11, 13, 12, 14), fill=(0, 0, 0, 0))
    return im


def worn_resource_probe():
    im, d = canvas()
    d.line((3, 12, 12, 3), fill=INK, width=4)
    d.line((3, 12, 11, 4), fill=MID, width=2)
    d.line((3, 11, 8, 6), fill=SILVER)
    d.polygon([(0, 2), (2, 1), (6, 5), (5, 8), (2, 5)], fill=INK)
    d.line([(1, 2), (4, 5), (4, 6)], fill=VIOLET)
    d.point((2, 3), fill=LILAC)
    d.polygon([(9, 9), (11, 9), (14, 12), (14, 14), (12, 15), (9, 12)], fill=INK)
    d.line([(10, 10), (13, 13), (13, 14)], fill=VIOLET)
    d.point((12, 12), fill=LILAC)
    d.polygon([(10, 1), (14, 1), (15, 4), (12, 6), (9, 4)], fill=INK)
    d.rectangle((11, 2, 13, 4), fill=RED_DARK)
    d.point((11, 2), fill=RED)
    d.line((7, 8, 9, 10), fill=BRASS)
    d.point((6, 9), fill=AMBER)
    d.polygon([(1, 12), (3, 11), (5, 13), (2, 15)], fill=STEEL)
    d.point((2, 13), fill=SILVER)
    return im


def drone_scrap():
    im, d = canvas()
    d.ellipse((1, 1, 7, 5), fill=INK)
    d.arc((2, 2, 6, 4), 100, 335, fill=STEEL)
    d.line((4, 2, 6, 3), fill=MID)
    d.polygon([(7, 5), (12, 5), (14, 8), (11, 11), (7, 10), (5, 7)], fill=INK)
    d.polygon([(8, 6), (11, 6), (12, 8), (10, 9), (8, 9), (6, 7)], fill=MID)
    d.line((8, 6, 10, 6), fill=SILVER)
    d.line([(3, 7), (3, 10), (5, 12), (8, 12)], fill=BRASS)
    d.line([(3, 8), (4, 8), (4, 10)], fill=AMBER)
    d.polygon([(1, 12), (4, 12), (5, 14), (2, 15)], fill=INK)
    d.line((2, 13, 4, 14), fill=STEEL)
    d.line((10, 13, 14, 13), fill=INK, width=2)
    d.point((12, 12), fill=CYAN)
    d.point((14, 14), fill=STEEL)
    return im


def cradle(d, damaged=False):
    d.polygon([(1, 7), (3, 7), (5, 12), (10, 12), (12, 7), (14, 7), (13, 11), (11, 14), (4, 14), (2, 11)], fill=INK)
    d.line([(2, 8), (4, 12), (6, 13)], fill=STEEL)
    d.line([(13, 8), (12, 11), (10, 13)], fill=MID)
    d.rectangle((6, 13, 9, 14), fill=DARK)
    d.line((6, 14, 9, 14), fill=CYAN)
    if damaged:
        d.rectangle((12, 7, 14, 10), fill=(0, 0, 0, 0))
        d.point((12, 11), fill=AMBER)
        d.line([(8, 13), (7, 14), (8, 14)], fill=RED)


def empty_vessel():
    im, d = canvas()
    d.ellipse((3, 1, 12, 11), outline=INK, width=2)
    d.arc((4, 2, 11, 10), 155, 320, fill=STEEL)
    d.arc((5, 2, 10, 10), 100, 270, fill=BLUE)
    d.line((7, 2, 7, 10), fill=MID)
    d.line((4, 6, 11, 6), fill=DARK)
    d.line((5, 2, 8, 2), fill=SILVER)
    cradle(d)
    for p in [(3, 5), (12, 5), (6, 1), (9, 1)]:
        d.point(p, fill=GOLD)
    return im


def unstable_bubble():
    im, d = canvas()
    d.polygon([(4, 2), (7, 1), (8, 3), (6, 5), (7, 7), (5, 9), (6, 11), (3, 10), (1, 7), (2, 4)], fill=INK)
    d.polygon([(4, 3), (6, 2), (6, 4), (4, 6), (5, 8), (3, 8), (2, 6)], fill=VIOLET)
    d.line([(4, 3), (5, 2), (6, 2)], fill=PALE)
    d.polygon([(10, 2), (13, 4), (14, 7), (12, 11), (8, 12), (9, 9), (8, 7), (10, 5)], fill=INK)
    d.polygon([(11, 3), (12, 5), (13, 7), (11, 10), (9, 11), (10, 8), (9, 7), (11, 5)], fill=BLUE)
    d.line([(11, 4), (12, 6), (11, 8), (10, 9)], fill=CYAN)
    d.point((8, 1), fill=LILAC)
    d.point((8, 5), fill=PALE)
    d.point((6, 7), fill=LILAC)
    d.point((14, 2), fill=CYAN)
    cradle(d)
    d.point((2, 8), fill=AMBER)
    d.point((13, 8), fill=RED)
    return im


def stable_bubble():
    im, d = canvas()
    d.ellipse((2, 1, 13, 12), fill=INK)
    d.ellipse((3, 2, 12, 11), fill='#1e3b65')
    d.polygon([(4, 4), (7, 2), (10, 3), (11, 6), (9, 10), (5, 10), (3, 7)], fill=BLUE)
    d.ellipse((5, 2, 10, 11), outline=CYAN)
    d.line((7, 2, 7, 11), fill=CYAN)
    d.arc((3, 3, 12, 8), 0, 180, fill=CYAN)
    d.arc((3, 6, 12, 10), 180, 360, fill=CYAN)
    d.line([(4, 3), (6, 2), (8, 2)], fill=LIGHT)
    d.point((7, 6), fill=LIGHT)
    cradle(d)
    for p in [(2, 6), (13, 6), (7, 1)]:
        d.point(p, fill=GOLD)
    return im


def model_carrier():
    im, d = canvas()
    d.polygon([(2, 4), (10, 1), (14, 4), (14, 12), (6, 15), (1, 11), (1, 5)], fill=INK)
    d.polygon([(3, 4), (10, 2), (13, 4), (6, 7)], fill=STEEL)
    d.polygon([(2, 5), (6, 8), (6, 13), (2, 11)], fill=MID)
    d.polygon([(7, 8), (13, 5), (13, 11), (7, 14)], fill=DARK)
    d.polygon([(4, 5), (9, 3), (11, 4), (6, 6)], fill=BLUE)
    d.line([(5, 5), (8, 4), (10, 4)], fill=LIGHT)
    d.line([(8, 9), (11, 8), (11, 10), (9, 11)], fill=CYAN)
    d.point((11, 12), fill=GOLD)
    d.line((3, 8, 4, 9), fill=SILVER)
    d.line((3, 10, 4, 11), fill=STEEL)
    return im


def matter_seed():
    im, d = canvas()
    d.ellipse((1, 5, 14, 11), outline=INK, width=2)
    d.arc((2, 6, 13, 10), 15, 190, fill=BRASS)
    d.arc((2, 6, 13, 10), 190, 310, fill=GOLD)
    d.polygon([(7, 0), (11, 4), (10, 9), (7, 14), (4, 10), (4, 5)], fill=INK)
    d.polygon([(7, 2), (7, 11), (5, 8), (5, 5)], fill=LILAC)
    d.polygon([(8, 3), (10, 5), (9, 9), (8, 11)], fill=VIOLET)
    d.line((7, 3, 6, 5), fill=PALE)
    d.point((2, 5), fill=CYAN)
    d.point((12, 11), fill=CYAN)
    d.point((7, 14), fill=LIGHT)
    d.point((13, 2), fill=LILAC)
    return im


def termination_charge():
    im, d = canvas()
    d.polygon([(2, 3), (5, 1), (6, 3), (4, 5), (4, 10), (6, 12), (5, 14), (1, 11), (1, 5)], fill=INK)
    d.polygon([(3, 4), (4, 3), (4, 4), (3, 6), (3, 10), (5, 12), (4, 12), (2, 10), (2, 5)], fill=STEEL)
    d.polygon([(10, 1), (13, 3), (14, 5), (14, 11), (10, 14), (9, 12), (11, 10), (11, 5), (9, 3)], fill=INK)
    d.line([(11, 3), (13, 5), (13, 10), (11, 12)], fill=MID, width=2)
    d.line((5, 7, 10, 7), fill=VIOLET)
    d.rectangle((6, 5, 9, 10), fill=INK)
    d.rectangle((7, 6, 8, 9), fill=LILAC)
    d.point((7, 6), fill=PALE)
    d.rectangle((5, 12, 10, 14), fill=DARK)
    d.line((6, 13, 9, 13), fill=BRASS)
    d.point((10, 13), fill=RED)
    d.point((3, 5), fill=GOLD)
    return im


def container_remnant():
    im, d = canvas()
    d.arc((3, 1, 12, 11), 110, 280, fill=INK, width=3)
    d.arc((4, 2, 11, 10), 110, 265, fill=STEEL)
    d.line([(7, 1), (9, 2), (10, 1)], fill=INK, width=2)
    d.point((9, 1), fill=CYAN)
    cradle(d, damaged=True)
    d.line((5, 7, 4, 8), fill=CYAN)
    d.line((7, 9, 9, 8), fill=BLUE)
    d.polygon([(12, 4), (14, 5), (13, 7), (11, 6)], fill=INK)
    d.line((12, 5, 13, 5), fill=STEEL)
    d.point((14, 11), fill=SILVER)
    return im


def failed_shell():
    im, d = canvas()
    d.polygon([(4, 1), (11, 2), (14, 5), (13, 10), (10, 14), (4, 13), (1, 9), (2, 4)], fill=INK)
    d.polygon([(4, 2), (10, 3), (12, 5), (11, 10), (9, 12), (5, 11), (3, 8), (3, 5)], fill=MID)
    d.ellipse((4, 3, 10, 10), fill=INK)
    d.arc((4, 3, 10, 10), 155, 275, fill=STEEL)
    d.line([(10, 3), (9, 5), (11, 7), (9, 9), (10, 12)], fill=INK)
    d.line([(4, 2), (6, 2), (8, 3)], fill=SILVER)
    d.line((2, 8, 3, 9), fill=AMBER)
    d.line((5, 12, 9, 13), fill=BRASS)
    d.point((11, 11), fill=RED)
    d.point((13, 2), fill=STEEL)
    return im


def engineering_specimen(failed=False):
    im, d = canvas()
    d.polygon([(1, 10), (8, 8), (14, 10), (14, 13), (7, 15), (1, 12)], fill=INK)
    d.polygon([(2, 10), (8, 9), (12, 10), (7, 12)], fill=MID)
    d.line((3, 10, 6, 10), fill=CYAN)
    d.line((8, 13, 12, 12), fill=BLUE)
    d.polygon([(4, 4), (9, 2), (12, 4), (12, 8), (7, 10), (4, 8)], fill=INK)
    d.polygon([(5, 4), (9, 3), (11, 4), (7, 6)], fill=SILVER)
    d.polygon([(5, 5), (7, 7), (7, 9), (5, 8)], fill=MID)
    d.polygon([(8, 7), (11, 5), (11, 8), (8, 9)], fill=STEEL)
    d.line([(2, 8), (2, 3), (5, 1)], fill=BLUE)
    d.line([(13, 3), (14, 4), (14, 8)], fill=CYAN)
    d.point((3, 2), fill=LIGHT)
    d.line((7, 2, 8, 2), fill=GOLD)
    if failed:
        d.line([(8, 3), (7, 5), (9, 6), (8, 8)], fill=INK)
        d.line((2, 3, 5, 1), fill=BRASS)
        d.line((3, 10, 6, 10), fill=RED)
        d.point((10, 5), fill=AMBER)
        d.point((13, 1), fill=STEEL)
        d.point((14, 9), fill=AMBER)
    return im


DRAWINGS = {
    'spatial_probe': (spatial_probe, '长天线相位探针、弯月接收阵面与双侧校准翼，区别资源钻探与作业无人机。'),
    'industrial_work_drone': (work_drone, '四旋翼工业机身与双关节夹爪，底部开口钳用于作业。'),
    'worn_resource_probe': (worn_resource_probe, '沿资源探针斜向杆身，破损紫色传感帆、裸露接线与红色失效镜头。'),
    'worn_work_drone': (lambda: work_drone(True), '保留作业机四旋翼与钳爪体系，缺失一组旋翼并裂开装甲、断掉末端夹爪。'),
    'drone_disassembly_scrap': (drone_scrap, '拆开的旋翼环、破碎机身、铜线与独立金属残片，不再用完整无人机图形。'),
    'empty_bubble_containment_vessel': (empty_vessel, '空心收容球架、纵向定位轴与底部能量耦合座，透明中心强调未装世界泡。'),
    'unstable_simulated_world_bubble': (unstable_bubble, '断裂蓝紫半球、错位模拟表面与逸出像素，琥珀警示锁扣。'),
    'stable_simulated_world_bubble': (stable_bubble, '闭合蓝色球体、规则青色经纬网格与三点金色锁定节点。'),
    'world_model_carrier': (model_carrier, '斜置立体数据匣、冰蓝网格显示面与侧壁数据回路，不再是球形容器。'),
    'world_matter_seed': (matter_seed, '悬浮紫晶物质种子与环绕的金色约束轨道，细小青色能量节点。'),
    'bubble_termination_charge': (termination_charge, '相向机械钳与紫色能量锁芯、独立底部终止电荷模块。'),
    'bubble_container_remnant': (container_remnant, '失去右上球环的破损收容座、残留蓝色碎片与散落金属。'),
    'failed_containment_shell': (failed_shell, '开孔机械壳体与贯穿侧壁的深裂纹，琥珀缺陷痕和红色废品标记。'),
    'reverse_engineering_specimen': (engineering_specimen, '三维机械试样、蓝色扫描支架与分层测试托盘，独立于世界泡球体。'),
    'failed_engineering_specimen': (lambda: engineering_specimen(True), '开裂复现试样与断开扫描架，红色检测条和飞散残件明确失败状态。'),
}
PRESERVED = {
    'sealed_real_world_bubble': 'art85已批准精修：保留收容容器、窗口内部世界与现行原字节。',
    'unmanned_resource_probe': 'art85已批准精修：保留现行斜向探针与紫色传感帆原字节。',
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    names = json.loads((ASSETS / 'lang/zh_cn.json').read_text(encoding='utf-8-sig'))
    records = []
    sheet = Image.new('RGB', (1200, 5 * 216), '#121b2a')
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 17)
    small = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 13)
    for index, (ident, (paint, design)) in enumerate(DRAWINGS.items()):
        rel = Path('textures/item') / (ident + '.png')
        path = ASSETS / rel
        backup = OUT / 'before/assets/hk3gtl' / rel
        backup.parent.mkdir(parents=True, exist_ok=True)
        if not backup.exists():
            backup.write_bytes(path.read_bytes())
        painted = refine64(paint())
        painted.save(path, optimize=True)
        x, y = index % 3 * 400, index // 3 * 216
        draw.text((x + 16, y + 12), names['item.hk3gtl.' + ident], fill='#e5edf6', font=font)
        for dx, source in [(20, Image.open(backup).convert('RGBA')), (220, painted)]:
            checker = Image.new('RGBA', (64, 64), '#202c3d')
            pattern = ImageDraw.Draw(checker)
            for py in range(0, 64, 16):
                for px in range(0, 64, 16):
                    if (px + py) % 32:
                        pattern.rectangle((px, py, px + 15, py + 15), fill='#2a394e')
            checker.alpha_composite(source.resize((64, 64), Image.Resampling.NEAREST))
            sheet.paste(checker.resize((128, 128), Image.Resampling.NEAREST).convert('RGB'), (x + dx, y + 47))
        draw.text((x + 67, y + 181), '原图', fill='#a8bbd2', font=small)
        draw.text((x + 267, y + 181), '重画', fill='#8edcdb', font=small)
        records.append({'id': ident, 'name': names['item.hk3gtl.' + ident], 'path': rel.as_posix(),
                        'before_sha256': hashlib.sha256(backup.read_bytes()).hexdigest(),
                        'after_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                        'size': [64, 64], 'design': design})
    preserved = []
    for ident, reason in PRESERVED.items():
        rel = Path('textures/item') / (ident + '.png')
        preserved.append({'id': ident, 'path': rel.as_posix(), 'sha256': hashlib.sha256((ASSETS / rel).read_bytes()).hexdigest(), 'reason': reason})
    (OUT / 'world-manifest.json').write_text(json.dumps({'changed': records, 'preserved': preserved}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    sheet.save(OUT / '世界泡族材质新旧对照.png')
    print('世界泡族：重画15张64格静态透明贴图，保留2张已批准精修原图。')


if __name__ == '__main__':
    main()
