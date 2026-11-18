import math

import numpy as np

from w13_tv_common_20261117 import Part
from w13_tv_crt_20261117 import build_crt


def build_mountain():
    rng = np.random.default_rng(131117)
    buckets, layout = {}, []
    layers = [(-430, 545), (-315, 510), (-200, 470), (-85, 410), (30, 340), (145, 260), (250, 175)]
    screens = ['off'] * 10 + ['static'] * 4 + ['white', 'cyan', 'bars', 'code']
    for level, (height, radius) in enumerate(layers):
        for ring, distance in enumerate([radius, radius * .53, 0]):
            count = max(1, round(math.tau * distance / 125))
            phase = level * .19 + ring * .41
            for slot in range(count):
                angle = math.tau * slot / count + phase
                edge = 1 + .065 * math.sin(3 * angle + level * .45) + .035 * math.sin(5 * angle - level * .3)
                cx = round(math.sin(angle) * distance * edge + 27 * math.sin(level * .7) + rng.integers(-13, 14))
                cz = round(math.cos(angle) * distance * edge * .83 - 32 + rng.integers(-15, 16))
                cy = height + int(rng.integers(-18, 19))
                if level == 6 and ring > 0 and slot % 2 == 0:
                    cy += 45
                w, h, d = int(rng.integers(105, 151)), int(rng.integers(119, 153)), int(rng.integers(83, 119))
                if (slot + level * 2) % 9 == 0:
                    w, h = h + 20, w - 24
                orientation = ['front', 'right', 'back', 'left'][round(angle / (math.pi / 2)) % 4]
                if ring == 1 and slot % 4 == 0:
                    orientation = 'up'
                if ring == 0 and slot % 11 == 7:
                    orientation = ['back', 'left', 'front', 'right'][round(angle / (math.pi / 2)) % 4]
                lean = int(rng.choice([0, 0, 0, 0, -7, 6, -11, 9]))
                display = screens[int(rng.integers(len(screens)))]
                name = f'crt_{len(layout) + 1:03d}'
                label = f'旧电视{len(layout) + 1}'
                item = build_crt(name, label, [w, h, d], [cx, cy, cz], orientation, lean, display, len(layout) + 13)
                key = (level, cx // 230, cz // 230)
                if key not in buckets:
                    buckets[key] = Part('mountain_' + '_'.join(map(str, key)), f'电视山第{level + 1}层分簇{len(buckets) + 1}', group='mountain')
                buckets[key].chunks.append(item.p)
                buckets[key].values.append(item.states)
                layout.append(dict(id=name, size=[w, h, d], center=[cx, cy, cz], orientation=orientation, lean=lean, screen=display,
                    bounds=dict(min=item.p.min(0).tolist(), max=item.p.max(0).tolist())))
                if (slot + level * 3) % 10 == 3:
                    mini_size = [round(w * .48), round(h * .43), round(d * .58)]
                    mini_center = [cx + round(w * .26), cy + round(h * .53), cz + round(d * .18)]
                    mini = build_crt(f'crt_{len(layout) + 1:03d}', f'小型旧电视{len(layout) + 1}', mini_size, mini_center,
                        orientation, -lean, screens[(slot + level) % len(screens)], len(layout) + 13)
                    buckets[key].chunks.append(mini.p)
                    buckets[key].values.append(mini.states)
                    layout.append(dict(id=mini.name, size=mini_size, center=mini_center, orientation=orientation, lean=-lean,
                        screen=mini.metadata['screen'], bounds=dict(min=mini.p.min(0).tolist(), max=mini.p.max(0).tolist())))
        print(f'电视山第{level + 1}层：累计{len(layout)}台', flush=True)
    parts = [part.finish() for part in buckets.values()]
    return parts, layout
