from author_w05_shapes_20261115 import Part


STONE, DARK, TRIM, GOLD, WHITE, RED, CARPET_EDGE, LAMP, GLASS, IRIS, HK, BRONZE = range(1, 13)


def _frame(part, a, b, c, d, inset, width, bottom, top, state):
    left, right, rear, front = a+inset, b-inset, c+inset, d-inset
    part.box((left, bottom, rear), (right, top, rear+width-1), state)
    part.box((left, bottom, front-width+1), (right, top, front), state)
    part.box((left, bottom, rear), (left+width-1, top, front), state)
    part.box((right-width+1, bottom, rear), (right, top, front), state)


def build_ceiling_details():
    parts = []
    xs, zs = [-480, -375, 0, 375, 480], [-486, -75, 180, 430, 500]
    for xi, (a, b) in enumerate(zip(xs[:-1], xs[1:])):
        for zi, (c, d) in enumerate(zip(zs[:-1], zs[1:])):
            part = Part(f'roof_coffer_details_{xi}_{zi}', '矩形凹顶双层线脚与梁交点嵌板',
                        section='roof', source='V010-0025.0s.jpg',
                        confirmed='矩形凹板、内收窄线脚与梁端连接块',
                        inferred='三阶收边深度、交点四分嵌板及单格金点按整数格补全')
            _frame(part, a, b, c, d, 11, 5, 609, 617, STONE)
            _frame(part, a, b, c, d, 16, 2, 613, 618, TRIM)
            _frame(part, a, b, c, d, 20, 3, 616, 618, STONE)
            _frame(part, a, b, c, d, 24, 1, 618, 618, TRIM)
            for x, sx in [(a, 1), (b, -1)]:
                for z, sz in [(c, 1), (d, -1)]:
                    part.box((x, 595, z), (x+sx*13, 598, z+sz*13), STONE)
                    part.box((x, 594, z), (x+sx*10, 594, z+sz*10), TRIM)
                    part.box((x, 593, z), (x+sx*8, 593, z+sz*8), DARK)
                    part.box((x, 592, z), (x+sx*5, 592, z+sz*5), STONE)
                    part.box((x, 591, z), (x, 591, z), GOLD)
            parts.append(part.finish())
    return parts
