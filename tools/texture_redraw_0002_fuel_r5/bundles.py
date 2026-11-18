from PIL import Image, ImageDraw


def bundle(rod, count):
    columns, rows, width, height, step, depth_x, depth_y, left = {
        4: (2, 2, 9, 50, 10, 5, 6, 20),
        8: (4, 2, 9, 50, 10, 5, 6, 10),
        16: (4, 4, 7, 40, 8, 4, 5, 10),
    }[count]
    stem = rod.crop(rod.getbbox()).resize((width, height), Image.Resampling.NEAREST)
    im = Image.new('RGBA', (64, 64))
    for row in range(rows):
        for column in range(columns):
            x = left + column * step + (rows - 1 - row) * depth_x
            y = 3 + row * depth_y
            im.alpha_composite(stem, (x, y))

    d = ImageDraw.Draw(im)
    front_y = 3 + (rows - 1) * depth_y
    right = left + (columns - 1) * step + width - 1
    back_x, back_y = (rows - 1) * depth_x, (rows - 1) * depth_y
    for y in (front_y + height // 3, front_y + height * 3 // 4):
        d.polygon([(right, y), (right + back_x, y - back_y),
                   (right + back_x, y - back_y + 2), (right, y + 2)],
                  fill='#59616a', outline='#30363e')
        d.line((right, y, right + back_x, y - back_y), fill='#879296')
        d.rectangle((left, y, right, y + 2), fill='#444c54')
        d.line((left, y, right - 1, y), fill='#a0aba9')
        d.line((left, y + 2, right, y + 2), fill='#252c35')
        d.rectangle((left + 2, y, left + 4, y + 2), fill='#69767a')
        d.point((left + 3, y), fill='#c1c8c1')
    return im
