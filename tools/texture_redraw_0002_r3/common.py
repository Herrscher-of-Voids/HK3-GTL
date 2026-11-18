from PIL import Image, ImageDraw

STEEL = ['#202935', '#475362', '#81909d', '#becbd1', '#eff1e7']
WHITE = ['#354253', '#7c8b9a', '#bac7ce', '#e2e8e8', '#fff9e7']
GOLD = ['#453322', '#80613a', '#b88e4e', '#e2c47f', '#fff1ba']
COPPER = ['#462a24', '#87503b', '#b87b50', '#e8ad76', '#ffe2ae']
VIOLET = ['#261d40', '#4c3474', '#8358b2', '#bc8be5', '#f0d8ff']
BLUE = ['#19364d', '#326583', '#5b9dba', '#a1d6dc', '#e0f4e7']
BLACK = ['#151c27', '#2b3541', '#4b5662', '#7f8d98', '#b7c3cc']


class Pixel:
    def __init__(self):
        self.im = Image.new('RGBA', (64, 64))
        self.d = ImageDraw.Draw(self.im)

    def plate(self, points, pal=STEEL, shade=2, grain=0):
        self.d.polygon(points, fill=pal[shade], outline=pal[0])
        mask = Image.new('1', (64, 64))
        ImageDraw.Draw(mask).polygon(points, fill=1)
        left, top, right, bottom = mask.getbbox()
        for y in range(top + 2, bottom - 2):
            for x in range(left + 2, right - 2):
                if mask.getpixel((x, y)) and (x * 17 + y * 7 + grain) % 43 < 2:
                    self.d.line((x, y, x + 1, y), fill=pal[max(1, shade - 1)])
        self.d.line(points[:2], fill=pal[min(shade + 1, 4)])

    def box(self, area, pal=STEEL, shade=2):
        x, y, r, b = area
        self.d.rectangle(area, fill=pal[shade], outline=pal[0])
        self.d.line((x + 1, y + 1, r - 1, y + 1), fill=pal[4])
        self.d.line((x + 1, y + 2, x + 1, b - 1), fill=pal[min(shade + 1, 4)])
        self.d.line((r - 1, y + 1, r - 1, b - 1), fill=pal[1])

    def bolt(self, x, y, pal=STEEL):
        self.d.rectangle((x, y, x + 2, y + 2), fill=pal[0])
        self.d.line((x, y, x + 1, y), fill=pal[4])
        self.d.point((x + 1, y + 1), fill=pal[2])

    def cylinder(self, area, pal=STEEL):
        x, y, r, b = area
        self.d.rectangle((x, y + 3, r, b - 3), fill=pal[1], outline=pal[0])
        self.d.rectangle((x + 2, y + 3, (x + r) // 2, b - 3), fill=pal[2])
        self.d.line((x + 3, y + 3, x + 3, b - 4), fill=pal[3])
        self.d.ellipse((x, b - 6, r, b), fill=pal[1], outline=pal[0])
        self.d.ellipse((x, y, r, y + 6), fill=pal[3], outline=pal[0])
        self.d.line((x + 3, y + 1, r - 3, y + 1), fill=pal[4])
