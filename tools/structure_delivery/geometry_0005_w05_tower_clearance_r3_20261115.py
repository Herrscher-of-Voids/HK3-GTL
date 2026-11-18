import math

import numpy as np

import author_w05_wings_20261115 as original
from author_w05_wings_20261115 import lift_rotor as original_lift_rotor
from author_w05_shapes_20261115 import Part, SHELL, ARMOR, COIL, FRAME


def tower(side, index):
    name = 'left' if side < 0 else 'right'
    x, z = side*175, original.TOWER_Z[index]
    p = Part(f'wing_{name}_vortex_tower_{index+1}', f'{"左" if side < 0 else "右"}翼第{index+1}座直径90贯通涡流副塔',
             source='二·3：每侧3座直径90的上下贯通垂直涡流副塔',
             effect=dict(kind='vortex_tower', center=[x, 132, z], bottom=58, top=210, radius=34),
             diameter=90, open_ends=True)
    for y in (64, 204):
        p.ring([x, y, z], 45, 7, SHELL, depth=12)
        p.ring([x, y+5, z], 45, 3, ARMOR, depth=2)
        p.ring([x, y+6, z], 39, 1.5, COIL, depth=1)
    for y in (99, 132, 168):
        p.ring([x, y, z], 43, 2, FRAME, depth=3)
    for angle in np.arange(8)*math.pi/4:
        dx, dz = 42*math.cos(angle), 42*math.sin(angle)
        p.beam([x+dx, 66, z+dz], [x+dx, 201, z+dz], 2.2, FRAME)
        for y in (71, 113, 155):
            next_angle = angle+math.pi/4
            if y == 113:
                t = np.linspace(0, 1, 17)
                radius = 42+2*np.sin(math.pi*t)
                theta = angle+(next_angle-angle)*t
                route = np.c_[x+radius*np.cos(theta), y+35*t, z+radius*np.sin(theta)]
                for a, b in zip(route[:-1], route[1:]):
                    p.beam(a, b, .9, FRAME)
            else:
                p.beam([x+dx, y, z+dz], [x+42*math.cos(next_angle), y+35, z+42*math.sin(next_angle)], .9, FRAME)
    return p.finish()


def lift_rotor(side, index):
    p = original_lift_rotor(side, index)
    x, _, z = p.metadata['motion']['pivot']
    keep = np.hypot(p.p[:, 0]-x, p.p[:, 2]-z) <= 35
    p.p, p.states = p.p[keep], p.states[keep]
    p.metadata['blade_radius'] = 35
    return p


def vortex(side, index):
    name = 'left' if side < 0 else 'right'
    x, z = side*175, original.TOWER_Z[index]
    p = Part(f'wing_{name}_vortex_column_{index+1}', f'{"左" if side < 0 else "右"}翼第{index+1}座发光龙卷风柱',
             source='二·3：副塔内部由发光青色方块构成龙卷风柱',
             motion=dict(kind='vortex', pivot=[x, 132, z], axis=[0, 1, 0], sign=side),
             axis_light_bridge=dict(path=[[x, 119, z], [x, 137, z]], radius=.6,
                                    visual_only=True, rotor_hole_axis=[x, 128, z],
                                    solid_gap_y=[120.5, 135.5], rotor_surface_y=[123.5, 132.5]))
    for y, factor in (
        (np.linspace(60, 119, 300), lambda y: np.clip((119-y)/12, 0, 1)),
        (np.linspace(137, 208, 360), lambda y: np.clip((y-137)/12, 0, 1)),
    ):
        taper = factor(y)
        taper = taper*taper*(3-2*taper)
        radius = (8+23*((y-60)/148)**1.4)*taper
        angle = (y-60)/148*math.pi*7
        for phase in (0, math.pi):
            route = np.c_[x+radius*np.cos(angle+phase), y, z+radius*np.sin(angle+phase)]
            original.solid_route(p, route, 1.5, COIL)
    return p.finish()
