import numpy as np

from w13_tv_common_20261117 import (
    Part, bezier, rod, box_shell,
    BLACK, STUDS, GRAY, SILVER, VENT, YELLOW, PINK_LIGHT,
    CONTROL, CONTROLLER,
)


def hanging_case(index, low, high):
    part = Part(f'hanging_case_{index:02d}', f'垂挂机匣{index}', group='cables')
    x0, y0, z0 = low
    x1, y1, z1 = high
    box_shell(part, low, high, 3, BLACK)
    for x in [x0, x1 - 5]:
        part.box([x, y0, z1 + 1], [x + 5, y1, z1 + 5], STUDS)
    for y in range(y0 + 19, y1 - 14, 29):
        part.box([x0 + 12, y, z1 + 1], [x1 - 12, y + 7, z1 + 3], VENT)
    box_shell(part, [x0 + 7, y0, z0 - 3], [x1 - 7, y0 + 11, z1 + 4], 3, GRAY)
    part.box([x0 + 12, y0 + 15, z1 + 4], [x0 + 18, y0 + 19, z1 + 5], PINK_LIGHT)
    box_shell(part, [x0 - 5, y1 - 18, z0 - 4], [x1 + 5, y1 - 4, z1 + 4], 3, STUDS)
    return part.finish()


def cable_parts(index, controls, radius, plug=True):
    result = []
    controls = np.array(controls, float)
    for section in range(2):
        part = Part(f'cable_{index:02d}_{section + 1}', f'悬垂主缆{index}第{section + 1}段', group='cables')
        ts = np.linspace(section * .5, (section + 1) * .5, 21)
        points = [bezier(controls, t) for t in ts]
        for a, b in zip(points[:-1], points[1:]):
            rod(part, a, b, radius, BLACK, inner=radius - 3)
        if section == 0:
            for t in [.025, .055]:
                rod(part, bezier(controls, t), bezier(controls, t + .018), radius + 3, STUDS, inner=radius - 2)
        elif plug:
            for i, t in enumerate([.87, .905, .94]):
                rod(part, bezier(controls, t), bezier(controls, t + .023), radius + 4, GRAY if i == 1 else STUDS, inner=radius - 2)
            end = controls[-1]
            direction = end - controls[-2]
            direction /= np.linalg.norm(direction)
            rod(part, end, end + direction * 29, radius + 5, STUDS, inner=radius - 3)
            rod(part, end + direction * 11, end + direction * 19, radius + 6, YELLOW, inner=radius - 2)
            rod(part, end + direction * 29, end + direction * 39, radius - 4, SILVER)
        result.append(part.finish())
    return result


def build_cables():
    cases = [
        ([-190, 158, -25], [-105, 369, 78]),
        ([-52, 112, -20], [37, 369, 80]),
        ([105, 181, -35], [182, 369, 80]),
        ([230, 236, -60], [280, 369, 55]),
    ]
    parts = [hanging_case(i, low, high) for i, (low, high) in enumerate(cases, 1)]
    paths = [
        ([[-260, 365, 170], [-350, 160, 330], [-490, -10, 410], [-475, 120, 395]], 17),
        ([[-110, 360, 195], [-170, 140, 400], [-250, -50, 480], [-280, 65, 430]], 14),
        ([[30, 360, 180], [20, 140, 320], [-30, -5, 460], [0, 32, 450]], 16),
        ([[210, 360, 160], [330, 130, 330], [505, 0, 415], [470, 120, 360]], 18),
        ([[390, 380, -70], [520, 170, -20], [520, 40, 180], [450, 160, 210]], 15),
        ([[230, 360, -150], [390, 180, -290], [440, 50, -425], [390, 125, -400]], 14),
        ([[-20, 360, -170], [-25, 130, -310], [80, 20, -430], [90, 155, -385]], 13),
        ([[-250, 360, -150], [-430, 210, -270], [-510, 50, -305], [-450, 165, -265]], 16),
        ([[-390, 380, 5], [-490, 220, 40], [-505, 80, 170], [-425, 125, 205]], 13),
    ]
    for index, (controls, radius) in enumerate(paths, 1):
        parts.extend(cable_parts(index, controls, radius, plug=index != 3))
    terminal = Part('controller_terminal', '前端主缆检修端子与唯一主控', group='cables')
    box_shell(terminal, [-27, 0, 435], [27, 29, 471], 4, STUDS)
    terminal.box([-20, 5, 470], [20, 26, 471], GRAY)
    terminal.box([-13, 8, 472], [13, 24, 472], BLACK)
    for x in [-22, 21]:
        terminal.box([x, 6, 472], [x + 1, 8, 472], SILVER)
        terminal.box([x, 22, 472], [x + 1, 24, 472], SILVER)
    terminal.points([CONTROLLER], CONTROL)
    parts.append(terminal.finish())
    return parts
