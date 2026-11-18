import base64
import copy
import hashlib
import json
from pathlib import Path

import numpy as np

from author_w05_shapes_20261115 import Part, bezier
from w08_common_20261116 import rod


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/0005_W13_侵蚀之律者电视本体_T1_20261117'
LOG = ROOT / 'logs/0005-w13-tv-t1-20261117'
BLACK, STUDS, GRAY, SILVER, VENT, CLEAN, WHITE, WHITE_STUDS, GOLD, YELLOW, PINK, MAGENTA, RED, PINK_GLASS, MAGENTA_GLASS, PINK_LIGHT, MAGENTA_LIGHT, RED_LIGHT, BLUE, CYAN_GLASS, WHITE_LIGHT, COMPUTER, ADVANCED, CONTROL, IWV = range(1, 26)
CONTROLLER = np.array([0, 16, 472])
EYE = np.array([0, 525, 247])


def materials():
    original = json.loads((ROOT / 'deliveries/0005_W13_蚀界研究母机_作者蓝图_A1_20261117/materials.json').read_text('utf8'))
    indices = [0, 1, 2, 3, 10, 11, 12, 13, 17, 18, 19, 20, 21, 24, 25, 27, 28, 29, 30, 31, 32, 33, 34, 35]
    result = [copy.deepcopy(original[i]) for i in indices]
    labels = ['吸光深色机壳', '铆接包边', '中灰折板', '浅灰框缘', '散热格栅', '金属壳体浅面', '浅色铭牌', '浅色铆钉', '黄铜触点', '插头警示套圈', '屏幕粉色暗层', '屏幕洋红暗纹', '暗红数据层', '粉色透光细节', '洋红透光细节', '粉色显示像素', '洋红显示像素', '红色显示像素', '冷蓝状态标记', '青色透光细节', '白色显示像素', '旧电视控制单元', '主机运算机匣', '唯一主控定位', '侵蚀洋红机壳']
    for m, label in zip(result, labels):
        m['label'] = label
    path = ROOT / 'src/main/resources/assets/hk3gtl/textures/block/voltage_casings/iwv/casing.png'
    png = path.read_bytes()
    faces = {face: 'data:image/png;base64,' + base64.b64encode(png).decode() for face in result[0]['faces']}
    result.append(dict(state='hk3gtl:voltage_machine_casing_iwv', label=labels[-1], faces=faces,
                       transparent=False, emissive=False,
                       source=dict(kind='hk', entry=str(path.relative_to(ROOT)), png_sha256=hashlib.sha256(png).hexdigest(), texture_mode='原生像素贴图，无额外染色')))
    return result


def rounded(x, y, hx, hy, bevel):
    return (abs(x) <= hx) & (abs(y) <= hy) & (abs(x) + abs(y) <= hx + hy - bevel)


def line(part, a, b, radius, state):
    rod(part, a, b, radius, state)


def curve(part, controls, radius, state, steps=40):
    points = np.array([bezier(controls, t) for t in np.linspace(0, 1, steps)])
    for a, b in zip(points[:-1], points[1:]):
        rod(part, a, b, radius, state)


def box_shell(part, low, high, thickness, state):
    lo, hi = np.array(low), np.array(high)
    for axis in range(3):
        for end in [0, 1]:
            a, b = lo.copy(), hi.copy()
            if end:
                a[axis] = hi[axis] - thickness + 1
            else:
                b[axis] = lo[axis] + thickness - 1
            part.box(a, b, state)
