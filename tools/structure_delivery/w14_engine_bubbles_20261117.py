import numpy as np

from w14_engine_common_20261117 import (
    Part, BLACK, STUDS, SILVER, WSV, BLUE, BLUE_LIGHT, PURPLE_LIGHT,
    GLASS, STONE, MOSS, DIRT, LOG_BLOCK, LEAVES, SAND, ICE, SNOW,
    MAGMA, OBSIDIAN, WATER, SEA_LIGHT, AMETHYST, END_STONE,
    GREEN_LIGHT, RED_LIGHT, radial, radial_box, rod,
)


def terrain(kind, x, z, radius):
    r = radius
    if kind == 'forest':
        return -.23*r + 6*np.sin(x/17)*np.cos(z/21) + 7*np.exp(-((x+30)**2+(z-17)**2)/(r*.5)**2)
    if kind == 'ocean':
        return -.45*r + .56*r*np.exp(-((x+.40*r)**2+(z-.14*r)**2)/(r*.25)**2) + .46*r*np.exp(-((x-.36*r)**2+(z+.32*r)**2)/(r*.19)**2)
    if kind == 'ice':
        return -.31*r + .69*r*np.exp(-((x+.19*r)**2+(z+.15*r)**2)/(r*.30)**2) + .47*r*np.exp(-((x-.37*r)**2+(z-.22*r)**2)/(r*.23)**2)
    if kind == 'desert':
        return -.22*r + 9*np.sin((x+.7*z)/18) + 5*np.sin((z-.3*x)/29)
    if kind == 'volcano':
        distance = np.sqrt((x+.08*r)**2+z*z)
        return -.35*r + 1.15*r*np.maximum(0, 1-distance/(r*.70)) - .75*r*np.exp(-(distance/(r*.20))**4)
    if kind == 'crystal':
        return -.30*r + 5*np.sin(x/18)*np.cos(z/23)
    return -.25*r + 5*np.sin(x/23) + 3*np.cos(z/17)


def ground(part, center, radius, kind):
    r = radius
    z, x = np.mgrid[-r:r+1, -r:r+1]
    distance2 = x*x+z*z
    top = terrain(kind, x, z, r)
    for y in range(-r+5, int(np.ceil(top.max()))+1):
        mask = (distance2+y*y <= (r-5)**2) & (y <= top)
        states = np.full(mask.sum(), STONE, np.uint8)
        surface = top[mask]-y
        if kind == 'forest':
            states[surface < 9] = DIRT
            states[surface < 2] = MOSS
        elif kind == 'ocean':
            states[surface < 6] = SAND
            states[(surface < 2) & (top[mask] > -.10*r)] = MOSS
        elif kind == 'ice':
            states[surface < 24] = ICE
            states[surface < 3] = SNOW
        elif kind == 'desert':
            states[surface < 14] = SAND
        elif kind == 'volcano':
            states[:] = OBSIDIAN
            distance = np.sqrt((x[mask]+.08*r)**2+z[mask]**2)
            crack = (abs(x[mask]-.14*z[mask]+3*np.sin(z[mask]/13)) < 2.4) | (distance < .18*r)
            states[(surface < 2) & crack] = MAGMA
        elif kind == 'crystal':
            states[surface < 3] = AMETHYST
        else:
            states[surface < 7] = END_STONE
        points = np.c_[x[mask], np.full(mask.sum(), y), z[mask]] + center
        for state in np.unique(states):
            part.points(points[states == state], state)
    if kind == 'ocean':
        for y in [int(-.13*r)-1, int(-.13*r)]:
            mask = (distance2+y*y <= (r-6)**2) & (top < y)
            part.points(np.c_[x[mask], np.full(mask.sum(), y), z[mask]]+center, WATER)


def tree(part, center, radius, kind, x, z, height):
    y = int(terrain(kind, x, z, radius))
    part.box(center+[x-1, y-2, z-1], center+[x+1, y+height, z+1], LOG_BLOCK)
    for dx, dy, dz, crown in [(0, 4, 0, 14), (-8, 0, 0, 10), (8, 1, 1, 10), (0, 0, 8, 10), (0, 0, -8, 10)]:
        part.sphere(center+[x+dx, y+height+dy, z+dz], crown, LEAVES)


def decorate(part, center, radius, kind):
    r = radius
    if kind == 'forest':
        for x, z, height in [(-35, 7, 22), (13, -29, 27), (34, 16, 24), (-11, 32, 23), (4, 4, 31), (-29, -32, 24)]:
            tree(part, center, r, kind, x, z, height)
        for x, z in [(-51, 24), (25, 43), (44, -28)]:
            y = int(terrain(kind, x, z, r))
            part.sphere(center+[x, y+2, z], 6, STONE)
    elif kind == 'ocean':
        tree(part, center, r, kind, int(-.40*r), int(.14*r), 17)
        for x, z in [(18, 24), (-8, -27), (39, -2), (-37, -26)]:
            y = int(terrain(kind, x, z, r))
            part.sphere(center+[x, y+2, z], 4, SEA_LIGHT)
    elif kind == 'ice':
        for x, z, height, width in [(-15, -9, 29, 8), (26, 16, 24, 7), (-37, 23, 22, 6)]:
            y = int(terrain(kind, x, z, r))
            part.hull(center+np.array([[x-width,y-3,z-width], [x+width,y-3,z-width], [x+width,y-3,z+width], [x-width,y-3,z+width], [x+2,y+height,z-2]]), ICE)
    elif kind == 'desert':
        for x, z, height in [(-27, -16, 27), (29, 15, 19), (-9, 34, 13)]:
            y = int(terrain(kind, x, z, r))
            part.box(center+[x-3, y-3, z-3], center+[x+3, y+height, z+3], END_STONE)
            part.box(center+[x-4, y+height, z-4], center+[x+4, y+height+2, z+4], SAND)
    elif kind == 'volcano':
        x, z = np.mgrid[-int(.18*r):int(.18*r)+1, -int(.18*r):int(.18*r)+1]
        mask = x*x+z*z <= (.15*r)**2
        y = int(terrain(kind, -.08*r, 0, r))+1
        for layer in range(int(-.10*r), y+1):
            part.points(np.c_[x[mask]-.08*r, np.full(mask.sum(), layer), z[mask]]+center, MAGMA)
    elif kind == 'crystal':
        for x, z, height, width in [(-26, -17, 49, 11), (20, 11, 68, 15), (-3, 31, 40, 10), (-9, -34, 35, 9), (34, -25, 39, 9)]:
            y = int(terrain(kind, x, z, r))
            part.hull(center+np.array([[x,y-7,z], [x-width,y+9,z], [x,y+9,z-width], [x+width,y+9,z], [x,y+9,z+width], [x+3,y+height,z-2]]), AMETHYST)
            part.sphere(center+[x, y+4, z], 4, PURPLE_LIGHT)
    elif kind == 'ruins':
        floor = int(terrain(kind, 0, -12, r))+3
        part.box(center+[-35, floor-6, -35], center+[35, floor, 13], END_STONE)
        for x, z, height in [(-25, -25, 38), (25, -25, 38), (-25, 4, 18), (25, 4, 29)]:
            part.box(center+[x-4, floor-1, z-4], center+[x+4, floor+height, z+4], STONE)
            part.box(center+[x-6, floor+height, z-6], center+[x+6, floor+height+3, z+6], END_STONE)
        part.box(center+[-31, floor+38, -31], center+[31, floor+43, -19], END_STONE)
        part.box(center+[19, floor+29, -22], center+[31, floor+34, 7], STONE)
        for x, z, length in [(-40, 30, 17), (-17, 34, 12), (27, 30, 15)]:
            y = int(terrain(kind, x, z, r))
            part.box(center+[x, y-2, z-3], center+[x+length, y+4, z+3], STONE)


def enclosure(part, center, radius, lamp):
    r = radius
    z, x = np.mgrid[-r:r+1, -r:r+1]
    for y in range(-r, r+1):
        distance2 = x*x+z*z+y*y
        mask = (distance2 <= r*r) & (distance2 >= (r-1.3)**2) & (z < -.08*r)
        part.points(np.c_[x[mask], np.full(mask.sum(), y), z[mask]]+center, GLASS)
    part.ring(center, r+4, 3, SILVER, normal=(0, 0, 1), depth=4)
    part.ring(center, r+1, 1, lamp, normal=(0, 0, 1), depth=3)
    part.ring(center+[0, -.12*r, 0], r+4, 3, WSV, normal=(0, 1, 0), depth=4)
    part.ring(center+[0, -.12*r, 0], r+1, 1, lamp, normal=(0, 1, 0), depth=3)


def feed(part, center, radius, distance, angle, lamp):
    r = radius
    radial_box(part, 611, distance-r*.60, -15, 15, 35, 42, angle, BLACK)
    for side in [-13, 13]:
        radial_box(part, 611, distance-r*.60, side-2, side+2, 43, 48, angle, SILVER)
        radial_box(part, 617, distance-r*.60, side-1, side+1, 49, 50, angle, lamp)
    for u in range(624, int(distance-r*.60), 22):
        radial_box(part, u, u+3, -17, 17, 30, 35, angle, STUDS)
    part.ring([center[0], 36, center[2]], .80*r, .80*r, BLACK, depth=8)
    part.ring([center[0], 41, center[2]], .80*r, 4, SILVER, depth=3)
    tray = center[1]-.72*r
    part.ring([center[0], tray, center[2]], .72*r, 8, BLACK, depth=7)
    part.ring([center[0], tray+4, center[2]], .72*r, 2, SILVER, depth=3)
    for direction in [0, .5*np.pi, np.pi, 1.5*np.pi]:
        dx, dz = .65*r*np.cos(direction), .65*r*np.sin(direction)
        foot = np.array([center[0]+dx, 36, center[2]+dz])
        part.box(foot+[-9,-16,-9], foot+[9,0,9], STUDS)
        rod(part, foot, [foot[0], tray, foot[2]], 4, BLUE)
        rod(part, [foot[0], 43, foot[2]], [center[0]+.70*dx, tray-5, center[2]+.70*dz], 3, SILVER)


def build():
    parts, bubble_info = [], []
    bubbles = [
        ('forest', '森林世界泡', 812, 176, 88, GREEN_LIGHT),
        ('ocean', '海洋世界泡', 802, 160, 92, BLUE_LIGHT),
        ('ice', '冰原世界泡', 820, 189, 86, BLUE_LIGHT),
        ('desert', '沙漠世界泡', 810, 154, 80, BLUE_LIGHT),
        ('volcano', '火山世界泡', 800, 220, 90, RED_LIGHT),
        ('crystal', '紫晶世界泡', 816, 202, 82, PURPLE_LIGHT),
        ('ruins', '荒原遗迹世界泡', 808, 184, 85, PURPLE_LIGHT),
    ]
    for i, (kind, label, distance, height, radius, lamp) in enumerate(bubbles):
        angle = np.pi/2+(i+.5)*2*np.pi/7
        center = np.rint(radial(distance, height, 0, angle)).astype(int)
        identity = f'bubble_{i+1:02d}_{kind}'
        landscape = Part(identity+'_world', label+'内景', group='bubbles')
        ground(landscape, center, radius, kind)
        decorate(landscape, center, radius, kind)
        parts.append(landscape.finish())
        shell = Part(identity+'_enclosure', label+'观察壳与约束环', group='bubbles')
        enclosure(shell, center, radius, lamp)
        parts.append(shell.finish())
        support = Part(identity+'_feed', label+'供料桥与支座', group='feed')
        feed(support, center, radius, distance, angle, lamp)
        parts.append(support.finish())
        bubble_info.append(dict(id=identity, label=label, center=center.tolist(), radius=radius,
                                kind=kind, source='本项目世界泡视觉设计'))
    return parts, bubble_info
