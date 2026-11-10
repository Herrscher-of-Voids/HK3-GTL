# -*- coding: utf-8 -*-
"""I09–I13 新造型的接口、分区与数据合同，保留完整方块约束。"""
from redesign69_geometry import Build, ROOT

PORT = 'hk3gtl:industrial_port_casing'
DIAMOND = 'minecraft:diamond_block'
PIPE = 'gtceu:tungstensteel_pipe_casing'
GEAR = 'gtceu:tungstensteel_gearbox'
GRATE = 'gtceu:assembly_line_grating'
PANEL = 'gtceu:advanced_computer_casing'


def start(key, title, size, form, flow):
    brief = {'id': key.upper(), 'title': title, 'minimum_wdh': [size[0], size[2], size[1]],
             'form': form, 'flow': flow}
    a = Build(brief)
    a.w, a.h, a.d = size
    a.cx, a.cz = a.w // 2, a.d // 2
    return a


def zone(a, name, lo, hi, role, kind='equipment'):
    a.zones.append({'name': name, 'min': list(lo), 'max': list(hi),
                    'pos': [(lo[0]+hi[0])//2, hi[1], (lo[2]+hi[2])//2],
                    'role': role, 'kind': kind, 'service_face': '外侧维护面'})


def route(a, source, target, points, material=PIPE):
    for p, q in zip(points, points[1:]):
        a.line(p, q, material)
    a.links.append({'from': source, 'to': target, 'route': [list(p) for p in points]})


def interfaces(a, purposes, shell):
    """居中主控及左右分组接口，正面三格检修带保持可达。"""
    center = a.w // 2
    a.box((center-3, 0, 5), (center+3, 1, 6), shell)
    a.box((center-3, 2, 5), (center+3, 5, 6), shell)
    a.set(center, 3, 5, DIAMOND)
    positions = [center-13, center-9, center-5, center+5, center+9, center+13]
    ports = []
    for x, (key, purpose) in zip(positions, purposes):
        a.box((x-1, 0, 5), (x+1, 1, 7), shell)
        a.box((x-1, 2, 5), (x+1, 4, 6), shell)
        a.set(x, 3, 5, PORT)
        ports.append({'id': key, 'pos': [x, 3, 5], 'face': 'north', 'purpose': purpose})
    a.box((center-15, 0, 2), (center+15, 0, 4), GRATE)
    a.paths.append({'name': '正面接口检修带', 'min': [center-15, 1, 2], 'max': [center+15, 4, 4]})
    return [center, 3, 5], ports


def finish(a, name, description, purposes, shell, references):
    controller, ports = interfaces(a, purposes, shell)
    return {'key': a.brief['id'].lower(), 'name': name, 'title': a.brief['title'],
            'size': [a.w, a.h, a.d], 'controller': controller, 'ports': ports,
            'paths': a.paths, 'zones': a.zones, 'links': a.links, 'brief': a.brief,
            'description': description, 'references': references,
            'role_materials': {k: sorted(v) for k, v in a.roles.items()},
            'blocks': [{'pos': list(p), 'state': s} for p, s in sorted(a.b.items())]}
