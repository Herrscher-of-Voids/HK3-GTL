# -*- coding: utf-8 -*-
"""修复双罐正面立管断头，并独立检查管路末端与泵罐接点。"""
import numpy as np
import mx_c01_converter_geometry_v1_20261107 as original

W, H, D = original.W, original.H, original.D
STATES, ROLES = original.STATES, original.ROLES
NAME = original.NAME.replace('-v1-', '-v2-')
TITLE = original.TITLE


def build():
    cube, data = original.build()
    for x in (6, 34):
        cube[5:10, 24, x] = original.P
        cube[5, 23, x] = original.P
    data['name'] = NAME
    data['description'] += '双罐正面立管已接回各自循环泵的后上方接点。'
    return cube, data


def audit(cube, data):
    check = original.audit(cube, data)
    ends = []
    for y,z,x in zip(*np.nonzero(cube == original.P)):
        pipe_neighbors = 0
        equipment = []
        for Y,Z,X in ((y+1,z,x),(y-1,z,x),(y,z+1,x),(y,z-1,x),(y,z,x+1),(y,z,x-1)):
            if 0 <= Y < H and 0 <= Z < D and 0 <= X < W:
                material = int(cube[Y,Z,X])
                if material == original.P:
                    pipe_neighbors += 1
                elif material:
                    equipment.append([int(X),int(Y),int(Z)])
        if pipe_neighbors <= 1:
            assert equipment, f'管道断头未接设备：{[int(x),int(y),int(z)]}'
            ends.append(dict(pos=[int(x),int(y),int(z)],equipment_contacts=equipment))
    routes = []
    for x in (6,34):
        positions = [[x,5,23]] + [[x,y,24] for y in range(5,19)] + [[x,18,z] for z in (25,26)]
        assert all(cube[y,z,X] == original.P for X,y,z in positions)
        assert all(sum(abs(a-b) for a,b in zip(p,q)) == 1 for p,q in zip(positions,positions[1:]))
        assert cube[4,23,x] == original.C and cube[18,27,x] == original.C
        routes.append(dict(pump_contact=[x,4,23],tank_contact=[x,18,27],pipe_cells=positions))
    check['pipe_endpoints'] = dict(passed=True,endpoints=ends,open_ends=0,
                                   pump_to_tank_routes=routes,
                                   scope='仅核验实体造型的管段连续与设备接触，不代表流体运行能力')
    check['checks'].append('逐一核验全部管道末端，双罐正面立管连续接到循环泵及罐体')
    return check


if __name__ == '__main__':
    old, data = original.build()
    try:
        audit(old, data)
    except AssertionError as error:
        assert '管道断头未接设备' in str(error)
    else:
        raise AssertionError('回归检查未能识别V1断头')
    new, data = build()
    result = audit(new, data)
    assert result['blocks'] == 10453
    assert int(np.count_nonzero(old != new)) == 12
    print('V1断头已复现；V2双泵罐路及全部管道末端检查通过。')
