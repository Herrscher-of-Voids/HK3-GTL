from PIL import Image, ImageDraw


class Draw64:
    def __init__(self, image):
        self.draw = ImageDraw.Draw(image)

    def __getattr__(self, name):
        method = getattr(self.draw, name)

        def draw(coords, *args, **kwargs):
            def scale(value):
                if isinstance(value, (tuple, list)):
                    return tuple(scale(item) for item in value)
                return value * 4
            if 'width' in kwargs:
                kwargs['width'] *= 4
            if name == 'rounded_rectangle' and args:
                args = (args[0] * 4, *args[1:])
            if name == 'point':
                x, y = scale(coords)
                return self.draw.rectangle((x, y, x + 2, y + 2), *args, **kwargs)
            return method(scale(coords), *args, **kwargs)
        return draw


def canvas64():
    image = Image.new('RGBA', (64, 64))
    return image, Draw64(image)


def refine64(image):
    source = image.copy()
    pixels = image.load()
    original = source.load()
    for y in range(1, 63):
        for x in range(1, 63):
            r, g, b, a = original[x, y]
            if a and not original[x, y - 1][3] and original[x, y + 1][3]:
                pixels[x, y] = (min(255, r + 18), min(255, g + 18), min(255, b + 18), a)
            elif a and not original[x, y + 1][3] and original[x, y - 1][3]:
                pixels[x, y] = (max(0, r - 12), max(0, g - 12), max(0, b - 12), a)
    return image
