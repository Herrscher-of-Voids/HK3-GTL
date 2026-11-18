"""按工艺用途重绘仍使用旧模板的样本、纳米件与燃料中间件。"""
from pathlib import Path
import hashlib
import json

from PIL import Image, ImageDraw, ImageFont
from item_texture_64 import canvas64, refine64
from industrial_content_catalog import CATALOG

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'src/main/resources/assets/hk3gtl'
LOG = ROOT / 'logs/item-texture-refresh-20261112'
INK, DARK, STEEL, SILVER, LIGHT = '#17202e', '#354253', '#65768b', '#aabcca', '#e1edf0'
PURPLE, VIOLET, LILAC, PINK = '#553462', '#9d5bb3', '#d4a6e8', '#e38cc0'
GOLD, BRASS, GOLD_LIGHT = '#b88a49', '#77572e', '#edd099'
BLUE, CYAN, TEAL = '#4387ca', '#76d8e0', '#30777f'
RUST, ASH, PALE = '#765247', '#817e76', '#beb7a0'


def canvas():
    return canvas64()


def slide():
    im, d = canvas()
    d.polygon([(1, 6), (10, 1), (15, 5), (6, 14), (1, 10)], fill=INK)
    d.polygon([(2, 6), (10, 2), (13, 5), (6, 12), (2, 9)], fill=STEEL)
    d.polygon([(3, 6), (9, 3), (11, 5), (6, 10), (3, 8)], fill='#315365')
    d.polygon([(6, 5), (9, 5), (10, 7), (7, 9), (5, 7)], fill=VIOLET)
    d.line([(3, 6), (9, 3), (11, 4)], fill=LIGHT)
    d.line((5, 8, 9, 4), fill=LILAC)
    d.rectangle((10, 9, 14, 13), fill=INK)
    d.line([(11, 11), (12, 12), (14, 9)], fill=CYAN)
    return im


def reference():
    im, d = canvas()
    d.polygon([(3, 3), (5, 1), (10, 1), (12, 3), (12, 11), (10, 13), (5, 13), (3, 11)], fill=INK)
    d.rectangle((5, 3, 10, 11), fill='#284452')
    d.rectangle((6, 5, 9, 10), fill=PURPLE)
    d.rectangle((6, 8, 9, 10), fill=VIOLET)
    d.line((5, 4, 5, 10), fill=LIGHT)
    d.rectangle((5, 1, 10, 3), fill=STEEL)
    d.line((5, 1, 9, 1), fill=LIGHT)
    d.rectangle((2, 11, 4, 14), fill=BRASS)
    d.rectangle((11, 10, 13, 14), fill=BRASS)
    d.line([(2, 11), (2, 14), (13, 14)], fill=GOLD)
    d.line((6, 13, 9, 13), fill=GOLD_LIGHT)
    for y in (5, 7, 9):
        d.point((11, y), fill=GOLD_LIGHT)
    return im


def crystal_seed():
    im, d = canvas()
    d.polygon([(7, 1), (11, 5), (9, 10), (6, 12), (4, 7)], fill=INK)
    d.polygon([(7, 2), (10, 5), (8, 9), (6, 10), (5, 7)], fill=VIOLET)
    d.polygon([(7, 2), (7, 8), (5, 7)], fill=LILAC)
    d.line((7, 3, 6, 5), fill=LIGHT)
    d.polygon([(1, 9), (3, 8), (6, 11), (10, 10), (12, 7), (14, 8), (12, 13), (6, 15), (2, 12)], fill=INK)
    d.line([(2, 10), (4, 12), (7, 13), (11, 12), (13, 9)], fill=GOLD, width=2)
    d.line([(2, 9), (4, 11), (6, 12)], fill=GOLD_LIGHT)
    return im


def crystal():
    im, d = canvas()
    d.polygon([(7, 0), (11, 4), (10, 12), (6, 15), (2, 10), (3, 4)], fill=INK)
    d.polygon([(7, 1), (10, 5), (9, 11), (6, 14), (3, 9), (4, 4)], fill=VIOLET)
    d.polygon([(7, 1), (7, 10), (4, 8), (4, 4)], fill=LILAC)
    d.polygon([(7, 2), (10, 5), (8, 9)], fill=PINK)
    d.polygon([(12, 5), (15, 8), (13, 13), (10, 14), (11, 9)], fill=INK)
    d.polygon([(12, 6), (14, 8), (12, 12), (11, 12)], fill=VIOLET)
    d.line([(6, 3), (5, 4), (5, 6)], fill=LIGHT)
    d.line((12, 7, 12, 9), fill=LILAC)
    return im


def matrix():
    im, d = canvas()
    d.polygon([(1, 6), (8, 1), (14, 5), (14, 11), (7, 15), (1, 11)], fill=INK)
    d.polygon([(2, 6), (8, 2), (13, 5), (7, 11)], fill=STEEL)
    d.polygon([(2, 7), (7, 12), (13, 7), (13, 10), (7, 14), (2, 10)], fill=DARK)
    for p in ([(4, 6), (8, 3), (10, 5), (6, 8)], [(7, 8), (11, 5), (12, 6), (8, 10)]):
        d.line(p, fill=GOLD, width=2)
    d.polygon([(7, 4), (9, 6), (7, 9), (5, 7)], fill=PURPLE)
    d.line([(7, 5), (6, 7), (7, 8)], fill=LILAC)
    d.line([(2, 6), (8, 2), (11, 4)], fill=LIGHT)
    d.line((4, 11, 6, 12), fill=GOLD_LIGHT)
    return im


def impurity():
    im, d = canvas()
    d.polygon([(3, 5), (4, 2), (8, 3), (11, 1), (13, 5), (12, 8), (15, 11), (11, 14), (6, 13), (2, 14), (1, 10)], fill=INK)
    d.polygon([(4, 5), (5, 3), (8, 5), (11, 3), (12, 6), (10, 8), (13, 11), (9, 12), (5, 11), (3, 12), (2, 10)], fill='#494146')
    d.polygon([(4, 5), (7, 5), (6, 8), (3, 9)], fill=ASH)
    d.polygon([(9, 5), (11, 6), (9, 9), (7, 8)], fill=PURPLE)
    d.line([(9, 5), (9, 7), (8, 8)], fill=VIOLET)
    d.line([(4, 4), (5, 3), (7, 4)], fill=PALE)
    d.line((11, 10, 12, 11), fill=RUST)
    d.point((5, 12), fill=VIOLET)
    return im


def separation_residue():
    im, d = canvas()
    d.polygon([(1, 10), (4, 8), (5, 5), (8, 6), (11, 7), (12, 10), (14, 11), (13, 14), (3, 14)], fill=INK)
    d.polygon([(2, 11), (5, 8), (6, 6), (8, 7), (11, 10), (13, 12), (10, 13), (4, 13)], fill=RUST)
    d.polygon([(3, 10), (6, 7), (8, 8), (7, 10), (4, 11)], fill=PALE)
    d.line((6, 7, 8, 8), fill='#e0d2ab')
    for x, y in ((2, 13), (5, 12), (8, 11), (10, 12), (11, 9), (13, 13), (1, 7), (13, 6)):
        d.point((x, y), fill=ASH)
    d.rectangle((9, 5, 10, 6), fill='#565258')
    d.point((9, 5), fill=VIOLET)
    return im


def fuel_matrix():
    im, d = canvas()
    d.polygon([(4, 2), (11, 2), (14, 6), (14, 11), (10, 14), (4, 14), (1, 10), (1, 6)], fill=INK)
    d.polygon([(4, 3), (10, 3), (13, 6), (13, 10), (10, 12), (4, 12), (2, 9), (2, 6)], fill=PURPLE)
    for x, y in ((4, 5), (8, 4), (10, 7), (6, 8), (3, 9), (8, 10)):
        d.rectangle((x, y, x + 1, y + 1), fill='#b66b91')
        d.point((x, y), fill=PINK)
    d.line([(4, 3), (10, 3), (12, 5)], fill=LILAC)
    d.line((4, 13, 10, 13), fill='#3d2b49')
    return im


def fuel_tailings():
    im, d = canvas()
    d.polygon([(1, 10), (4, 9), (4, 6), (7, 7), (9, 5), (11, 8), (14, 10), (12, 14), (5, 14), (2, 12)], fill=INK)
    d.polygon([(2, 10), (5, 10), (5, 7), (8, 9), (10, 7), (13, 10), (11, 13), (5, 13)], fill='#6b4658')
    d.line([(5, 7), (6, 8), (5, 10)], fill='#a87587')
    d.polygon([(2, 5), (3, 3), (7, 4), (6, 6)], fill=BRASS)
    d.line((3, 3, 6, 4), fill=GOLD)
    for p in ((3, 11), (8, 11), (11, 9), (12, 12), (7, 6), (1, 14)):
        d.point(p, fill=RUST)
    d.point((7, 10), fill=VIOLET)
    return im


def microstructure_template():
    im, d = canvas()
    d.polygon([(2, 3), (11, 1), (14, 4), (13, 12), (5, 15), (1, 11)], fill=INK)
    d.polygon([(3, 4), (10, 2), (13, 5), (12, 11), (5, 13), (2, 10)], fill=STEEL)
    d.line([(3, 4), (10, 2), (12, 4)], fill=LIGHT)
    for x, y in ((4, 5), (8, 4), (5, 9), (9, 8)):
        d.polygon([(x, y), (x + 2, y - 1), (x + 3, y + 1), (x + 1, y + 3), (x - 1, y + 1)], fill=DARK)
        d.line([(x, y), (x + 2, y - 1), (x + 3, y + 1)], fill=GOLD_LIGHT)
        d.point((x + 1, y + 1), fill=BLUE)
    return im


def nanobot():
    im, d = canvas()
    for line in ([(4, 5), (1, 3), (1, 1)], [(4, 8), (1, 8), (0, 10)], [(5, 11), (3, 14), (1, 14)], [(11, 5), (14, 3), (14, 1)], [(11, 8), (14, 8), (15, 10)], [(10, 11), (12, 14), (14, 14)]):
        d.line(line, fill=INK, width=2)
        d.line(line, fill=STEEL)
    d.polygon([(6, 2), (9, 2), (12, 6), (11, 11), (8, 14), (4, 11), (3, 6)], fill=INK)
    d.polygon([(6, 3), (9, 3), (11, 6), (10, 10), (8, 12), (5, 10), (4, 6)], fill=STEEL)
    d.line([(6, 3), (9, 3), (10, 5)], fill=LIGHT)
    d.rectangle((6, 6, 9, 9), fill=DARK)
    d.line((6, 6, 8, 6), fill=GOLD)
    d.point((7, 4), fill='#d7ad64')
    return im


def swarm(coated=False):
    im, d = canvas()
    d.line([(4, 4), (11, 6), (7, 12), (4, 4)], fill=TEAL, width=2)
    d.line([(4, 4), (11, 6), (7, 12)], fill=CYAN)
    for x, y in ((1, 1), (9, 3), (4, 9)):
        d.polygon([(x + 1, y), (x + 4, y), (x + 5, y + 2), (x + 4, y + 5), (x + 1, y + 5), (x, y + 3)], fill=INK)
        d.polygon([(x + 1, y + 1), (x + 3, y + 1), (x + 4, y + 2), (x + 3, y + 4), (x + 1, y + 4)], fill='#a49caf' if coated else STEEL)
        d.line((x + 1, y + 1, x + 3, y + 1), fill=LIGHT)
        d.point((x + 2, y + 3), fill=VIOLET if coated else CYAN)
        if coated:
            d.line([(x + 1, y), (x + 4, y), (x + 5, y + 2)], fill=LILAC)
    return im


def inactive_unit():
    im, d = canvas()
    d.polygon([(5, 3), (10, 4), (12, 9), (9, 13), (4, 11), (2, 6)], fill=INK)
    d.polygon([(5, 4), (9, 5), (11, 9), (8, 11), (4, 10), (3, 6)], fill='#6a6b6b')
    d.line([(5, 4), (8, 5)], fill=SILVER)
    d.rectangle((5, 6, 8, 9), fill=DARK)
    d.line([(8, 4), (6, 6), (9, 8), (7, 11)], fill=INK)
    d.point((5, 7), fill=RUST)
    d.line([(3, 5), (1, 3), (1, 1)], fill=ASH)
    d.line([(10, 11), (12, 13), (14, 13)], fill=ASH)
    d.line([(13, 4), (14, 6), (13, 8)], fill=STEEL)
    d.point((1, 11), fill=GOLD)
    return im


def nano_scrap():
    im, d = canvas()
    d.polygon([(2, 3), (7, 2), (8, 5), (6, 6), (7, 10), (3, 9), (1, 6)], fill=INK)
    d.polygon([(3, 4), (6, 3), (6, 5), (4, 6), (5, 8), (2, 6)], fill=STEEL)
    d.line([(3, 4), (5, 3)], fill=LIGHT)
    d.line([(5, 5), (6, 7), (4, 8)], fill=GOLD)
    d.polygon([(9, 7), (14, 7), (13, 11), (15, 13), (11, 15), (7, 12)], fill=INK)
    d.polygon([(10, 8), (13, 8), (11, 10), (13, 13), (10, 13), (8, 11)], fill=TEAL)
    d.line([(10, 8), (12, 8), (10, 10)], fill=CYAN)
    d.rectangle((1, 12, 3, 13), fill=STEEL)
    d.line([(10, 3), (12, 2), (14, 4)], fill=BRASS)
    d.point((12, 2), fill=GOLD_LIGHT)
    return im


def casting_mold():
    im, d = canvas()
    d.polygon([(1, 4), (10, 1), (15, 4), (14, 12), (5, 15), (1, 12)], fill=INK)
    d.polygon([(2, 5), (10, 2), (13, 4), (12, 10), (5, 13), (2, 10)], fill=STEEL)
    d.polygon([(4, 6), (10, 4), (11, 5), (10, 9), (6, 11), (4, 9)], fill=INK)
    d.polygon([(5, 7), (9, 5), (10, 6), (9, 9), (6, 10), (5, 9)], fill=BRASS)
    d.line([(5, 7), (9, 5), (10, 6)], fill=GOLD)
    d.line([(2, 5), (10, 2), (13, 4)], fill=LIGHT)
    d.line((13, 6, 13, 10), fill=DARK)
    for p in ((3, 6), (11, 3), (3, 11), (11, 10)):
        d.point(p, fill=SILVER)
    return im


def polymer_residue():
    im, d = canvas()
    d.polygon([(1, 8), (3, 5), (6, 6), (8, 3), (12, 4), (13, 7), (11, 10), (15, 12), (11, 14), (7, 12), (3, 14), (2, 11)], fill=INK)
    d.polygon([(2, 8), (4, 6), (7, 7), (9, 4), (11, 5), (12, 7), (9, 10), (13, 12), (10, 13), (7, 11), (4, 12)], fill='#7d7982')
    d.polygon([(3, 7), (6, 7), (6, 9), (4, 10), (2, 9)], fill=SILVER)
    d.line([(8, 6), (9, 5), (11, 6)], fill=LIGHT)
    d.line([(6, 9), (8, 8), (9, 10)], fill='#9991a7')
    d.point((7, 10), fill=PURPLE)
    d.point((12, 12), fill=STEEL)
    return im


def data_substrate():
    im, d = canvas()
    d.polygon([(2, 2), (11, 2), (13, 4), (13, 13), (2, 13)], fill=INK)
    d.polygon([(3, 3), (10, 3), (12, 5), (12, 12), (3, 12)], fill=STEEL)
    d.line([(3, 11), (3, 3), (10, 3)], fill=LIGHT)
    for x, y in ((5, 5), (9, 5), (5, 9), (9, 9)):
        d.rectangle((x - 1, y - 1, x + 1, y + 1), fill=DARK)
        d.line((x - 1, y - 1, x + 1, y - 1), fill=BLUE)
        d.point((x, y), fill=CYAN)
    for x in (4, 7, 10):
        d.line((x, 0, x, 2), fill=GOLD)
        d.line((x, 13, x, 15), fill=BRASS)
        d.point((x, 0), fill=GOLD_LIGHT)
    d.line((0, 5, 2, 5), fill=GOLD)
    d.line((13, 9, 15, 9), fill=BRASS)
    return im


def encapsulation():
    im, d = canvas()
    d.polygon([(2, 3), (7, 1), (11, 4), (10, 8), (5, 10), (1, 7)], fill=INK)
    d.polygon([(3, 4), (7, 2), (9, 4), (8, 7), (5, 8), (2, 6)], fill=STEEL)
    d.ellipse((4, 3, 8, 6), fill=INK)
    d.line([(3, 4), (7, 2), (9, 4)], fill=LIGHT)
    d.polygon([(8, 8), (12, 6), (15, 9), (14, 13), (10, 15), (7, 12)], fill=INK)
    d.polygon([(9, 9), (12, 7), (14, 9), (13, 12), (10, 13), (8, 11)], fill=GOLD)
    d.ellipse((10, 9, 12, 11), fill=BRASS)
    d.line([(9, 9), (12, 7), (14, 9)], fill=GOLD_LIGHT)
    d.rectangle((2, 12, 4, 14), fill=STEEL)
    d.point((2, 12), fill=LIGHT)
    return im


def fuel_rod(mode):
    im, d = canvas()
    dense = mode in ('dense', 'depleted_dense', 'broken_dense')
    depleted = mode == 'depleted_dense'
    broken = mode in ('broken', 'broken_dense')
    if broken:
        d.polygon([(4, 1), (9, 0), (12, 6), (9, 8), (7, 6), (6, 8), (3, 4)], fill=INK)
        d.polygon([(5, 2), (8, 1), (10, 5), (8, 6), (7, 4), (5, 5)], fill=PURPLE)
        d.line((4, 2, 8, 1), fill=LIGHT, width=2)
        d.line((5, 4, 9, 3), fill=STEEL, width=2)
        d.polygon([(3, 10), (6, 9), (8, 11), (9, 9), (12, 12), (10, 15), (4, 15), (1, 12)], fill=INK)
        d.polygon([(4, 11), (6, 10), (8, 13), (10, 12), (10, 14), (4, 14), (2, 12)], fill=VIOLET if dense else '#775278')
        d.line((3, 13, 9, 14), fill=STEEL, width=2)
        d.line([(8, 7), (8, 9), (10, 10)], fill=GOLD)
        d.point((11, 8), fill=PINK)
        d.point((13, 11), fill=PURPLE)
        if dense:
            d.line([(12, 1), (14, 4), (12, 6)], fill=BRASS, width=2)
            d.line((11, 12, 13, 14), fill=GOLD)
    else:
        d.polygon([(5, 0), (10, 1), (11, 13), (9, 15), (5, 14), (4, 2)], fill=INK)
        d.polygon([(6, 2), (9, 2), (10, 12), (8, 13), (6, 12)], fill='#4c394e' if depleted else VIOLET)
        d.line((6, 3, 6, 11), fill='#827078' if depleted else LILAC)
        for y in (1, 6, 12):
            d.rectangle((4, y, 11, y + 1), fill=BRASS if dense else STEEL)
            d.line((4, y, 9, y), fill=GOLD_LIGHT if dense else LIGHT)
        if dense:
            d.line((8, 3, 8, 5), fill='#7f596d' if depleted else PINK)
            d.line((9, 8, 9, 11), fill='#6c5864' if depleted else PINK)
            d.point((6, 10), fill=RUST if depleted else LIGHT)
        if mode == 'rejected':
            d.line([(7, 3), (9, 5), (7, 7), (9, 9), (8, 11)], fill=INK)
            d.polygon([(1, 8), (5, 8), (6, 12), (2, 12)], fill=INK)
            d.line((2, 9, 4, 11), fill='#e07765')
            d.line((4, 9, 2, 11), fill='#e07765')
    return im


def recovered_casing():
    im, d = canvas()
    d.polygon([(1, 3), (6, 1), (9, 3), (8, 6), (4, 8), (1, 6)], fill=INK)
    d.line([(2, 3), (6, 2), (8, 4), (6, 6), (3, 6), (2, 4)], fill=SILVER, width=2)
    d.line((3, 3, 6, 2), fill=LIGHT)
    d.polygon([(8, 8), (13, 5), (15, 8), (13, 12), (10, 15), (7, 12)], fill=INK)
    d.polygon([(9, 9), (13, 6), (14, 8), (12, 11), (10, 13), (8, 11)], fill=STEEL)
    d.line([(9, 9), (13, 6), (14, 8)], fill=LIGHT)
    d.line([(10, 11), (12, 9), (12, 8)], fill=DARK)
    d.line((1, 12, 5, 10), fill=BRASS, width=2)
    d.point((1, 11), fill=GOLD)
    return im


def inactive_residue():
    im, d = canvas()
    d.polygon([(2, 11), (4, 8), (6, 9), (7, 6), (10, 7), (11, 10), (14, 11), (13, 14), (3, 14), (1, 13)], fill=INK)
    d.polygon([(3, 11), (5, 9), (7, 10), (8, 7), (10, 9), (10, 11), (13, 12), (11, 13), (4, 13)], fill='#534b53')
    d.line([(5, 9), (6, 10), (4, 11)], fill=ASH)
    d.line([(8, 8), (9, 8), (10, 10)], fill='#8f747f')
    for p in ((2, 7), (12, 6), (14, 10), (6, 13), (10, 12), (12, 13)):
        d.point(p, fill=RUST)
    d.rectangle((2, 3, 4, 4), fill=DARK)
    d.point((2, 3), fill=ASH)
    return im


def proto_mass(stable=False):
    im, d = canvas()
    if stable:
        d.polygon([(2, 5), (10, 2), (14, 5), (13, 11), (6, 14), (1, 10)], fill=INK)
        d.polygon([(3, 5), (10, 3), (12, 5), (6, 9), (2, 8)], fill=SILVER)
        d.polygon([(2, 9), (6, 10), (12, 6), (12, 10), (6, 13), (2, 10)], fill=STEEL)
        d.line([(3, 5), (10, 3), (12, 5)], fill=LIGHT)
        d.line([(7, 4), (9, 6), (9, 11)], fill=GOLD)
        d.line((9, 6, 10, 5), fill=GOLD_LIGHT)
        d.point((4, 7), fill=CYAN)
    else:
        d.polygon([(1, 6), (4, 3), (7, 4), (11, 2), (14, 6), (12, 10), (13, 12), (8, 14), (4, 12), (1, 11)], fill=INK)
        d.polygon([(2, 6), (5, 4), (8, 6), (11, 3), (13, 6), (10, 9), (12, 11), (8, 12), (4, 10), (2, 10)], fill=STEEL)
        d.polygon([(3, 6), (5, 4), (8, 6), (6, 8)], fill=SILVER)
        d.line([(3, 6), (5, 4), (6, 5)], fill=LIGHT)
        d.line([(9, 7), (11, 5), (12, 6)], fill='#a99aad')
        d.line([(4, 10), (6, 11), (8, 10)], fill=PURPLE)
    return im


def codex():
    im, d = canvas()
    d.polygon([(3, 1), (11, 1), (13, 4), (13, 12), (11, 14), (3, 14), (1, 11), (1, 4)], fill=INK)
    d.rectangle((3, 3, 11, 12), fill='#c1ae85')
    d.line((4, 3, 4, 12), fill='#f0dfb4')
    d.rectangle((2, 1, 12, 3), fill=GOLD)
    d.line((2, 1, 11, 1), fill=GOLD_LIGHT)
    d.rectangle((2, 12, 12, 14), fill=BRASS)
    d.line((3, 12, 11, 12), fill=GOLD)
    d.polygon([(7, 4), (10, 7), (7, 10), (5, 7)], fill='#475b76')
    d.line([(7, 5), (9, 7), (7, 9)], fill=CYAN)
    d.point((7, 6), fill=LIGHT)
    d.line((13, 5, 14, 9), fill=BRASS)
    d.point((14, 10), fill=VIOLET)
    return im


DRAWINGS = {
    'analyzed_honkai_sample': (slide, '斜置载玻片、紫色分析区与青色核验标记'),
    'honkai_reference_sample': (reference, '固定刻度安瓿、黄铜标定支架与标准样本液'),
    'honkai_crystal_seed': (crystal_seed, '小型单晶、黄铜夹爪与尖端高光'),
    'directional_crystallization_matrix': (matrix, '斜向晶格板、定向金色沟槽与中央晶种'),
    'concentrated_honkai_impurity': (impurity, '不规则杂质团、暗紫夹杂与矿质断面'),
    'separation_residue': (separation_residue, '松散灰褐粉渣、粗颗粒与少量紫色残留'),
    'fuel_matrix': (fuel_matrix, '厚六角燃料压坯、蜂窝孔与紫红颗粒'),
    'fuel_blending_residue': (fuel_tailings, '不成形调配尾料、卷边金属碎片与失色颗粒'),
    'soulium_microstructure_template': (microstructure_template, '魂钢薄板、金色微晶网格与蓝色节点'),
    'unprogrammed_nanobot': (nanobot, '六足机械单体、空白编程槽与未激活琥珀指示'),
    'controlled_nano_swarm': (lambda: swarm(False), '三组纳米节点、闭合青色控制链与银色外壳'),
    'inactive_nano_unit': (inactive_unit, '断裂暗色纳米机、缺足与无光核心'),
    'coated_nano_swarm': (lambda: swarm(True), '浅紫护甲包覆的蜂巢节点与受控连接线'),
    'nano_assembly_scrap': (nano_scrap, '破裂电路、金属卡爪和散落导线，明确废件轮廓'),
    'soulium_casting_mold': (casting_mold, '透视厚金属模具、凹陷锭槽与黄铜内衬'),
    'soulium_polymerization_residue': (polymer_residue, '凝结银灰金属瘤、聚合桥与暗紫夹渣'),
    'soulium_data_substrate': (data_substrate, '带定位缺角的金属基板、四组数据阵列与金触点'),
    'fuel_encapsulation_part': (encapsulation, '分离的密封端盖、黄铜压环与连接销'),
    'rejected_fuel_rod': (lambda: fuel_rod('rejected'), '裂缝燃料棒、失配封带与红色报废标签'),
    'depleted_dense_honkai_fuel_rod': (lambda: fuel_rod('depleted_dense'), '完整金色封带、失色暗芯与氧化热斑'),
    'broken_honkai_fuel_rod': (lambda: fuel_rod('broken'), '上下错位的断棒、露出导线与紫色碎屑'),
    'broken_dense_honkai_fuel_rod': (lambda: fuel_rod('broken_dense'), '断开的浓缩燃料束、金色外笼残段与裸露内芯'),
    'recovered_fuel_casing_material': (recovered_casing, '卷曲银色壳片、撕裂边缘与回收铜屑'),
    'inactive_fuel_residue': (inactive_residue, '失色灰紫灰堆、烧结颗粒与锈褐散粒'),
    'honkai_energy_crystal': (crystal, '高耸紫色主晶、侧生晶簇与清晰透明底轮廓'),
    'dense_honkai_fuel_rod': (lambda: fuel_rod('dense'), '金封环浓缩燃料棒、双芯光路与亮紫活性物'),
    'soulium_proto_mass': (lambda: proto_mass(False), '未经整形的粗魂钢块、银色断面与暗紫夹缝'),
    'stabilized_soulium_proto_mass': (lambda: proto_mass(True), '规整魂钢坯、稳定金箍与冷蓝标记'),
    'narrative_codex': (codex, '金属卷轴杆、羊皮载体与蓝色文明符印'),
}


def main():
    catalog = {row['id']: row for row in CATALOG}
    rows = [catalog[ident] for ident in DRAWINGS]
    records = []
    for row in rows:
        path = ASSETS / 'textures/item' / (row['id'] + '.png')
        rel = path.relative_to(ASSETS)
        before = LOG / 'before/assets/hk3gtl' / rel
        before.parent.mkdir(parents=True, exist_ok=True)
        if not before.exists():
            before.write_bytes(path.read_bytes())
        drawing, design = DRAWINGS[row['id']]
        refine64(drawing()).save(path, optimize=True)
        records.append({'id': row['id'], 'name': row['zh'], 'family': row['family'], 'path': rel.as_posix(),
                        'before_sha256': hashlib.sha256(before.read_bytes()).hexdigest(),
                        'after_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                        'size': [64, 64], 'design': design})
    (LOG / 'process-manifest.json').write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    width, height, cols = 300, 232, 5
    sheet = Image.new('RGB', (width * cols, 52 + height * ((len(records) + cols - 1) // cols)), '#121c2a')
    d = ImageDraw.Draw(sheet)
    title_font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 22)
    font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 15)
    tiny = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 11)
    d.text((15, 10), '工艺物品材质 · 29件样本／纳米件／燃料件', fill='#e1edf0', font=title_font)
    for i, row in enumerate(records):
        x, y = i % cols * width, 52 + i // cols * height
        d.rectangle((x + 3, y + 2, x + width - 4, y + height - 4), fill='#1c2a3b')
        d.text((x + 12, y + 8), row['name'], fill='#e1edf0', font=font)
        for k, path in enumerate((LOG / 'before/assets/hk3gtl' / row['path'], ASSETS / row['path'])):
            image = Image.open(path).convert('RGBA').resize((96, 96), Image.Resampling.NEAREST)
            sheet.paste(image, (x + 29 + 140 * k, y + 44), image)
            d.text((x + 55 + 140 * k, y + 146), '原图' if k == 0 else '重绘', fill='#9db2c8', font=font)
        design = row['design']
        d.text((x + 12, y + 179), design[:18], fill='#aec3d3', font=tiny)
        d.text((x + 12, y + 195), design[18:], fill='#aec3d3', font=tiny)
        d.text((x + 12, y + 212), row['id'][:38], fill='#7996b0', font=tiny)
    sheet.save(LOG / '工艺物品新旧对照.png')
    print('工艺物品材质：29张，模型、注册与动画元数据保持。')


if __name__ == '__main__':
    main()
