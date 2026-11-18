from w08_common_20261116 import *


def _axes(start, end):
    axis = end - start
    axis /= np.linalg.norm(axis)
    across = np.array([-axis[2], 0, axis[0]])
    across /= np.linalg.norm(across)
    normal = np.cross(across, axis)
    return axis, across, normal


def _keel(side):
    word = 'left' if side < 0 else 'right'
    label = '左' if side < 0 else '右'
    start = np.array([CX + side * 38, 190, 520.0])
    end = start + [side * 402, 120, math.sqrt(450 ** 2 - 402 ** 2 - 120 ** 2)]
    axis, across, normal = _axes(start, end)
    p = Part(f'wing_keel_{word}', f'{label}翼450格白金黑金主龙骨',
             source='二·3·从反应堆后方伸出的450格V形机械龙骨',
             centerline=[start.tolist(), end.tolist()], nominal_length=450,
             sampling='主轴450格，顶轴Y310；分段白金侧甲与顶甲包围四根黑金桁架，装甲截面宽38、厚20，最上表面约Y320。')
    for u in (-13, 13):
        for v in (-6, 6):
            a, b = start + across * u + normal * v, end + across * u + normal * v
            rod(p, a, b, 3, DARK)
    for index in range(10):
        t0, t1 = index * 45, min((index + 1) * 45, 450)
        a, b = start + t0 * axis, start + t1 * axis
        for v in (-6, 6):
            rod(p, a - across * 13 + normal * v, b + across * 13 + normal * v, 2, GOLD)
            rod(p, a + across * 13 + normal * v, b - across * 13 + normal * v, 2, DARK)
        for u in (-13, 13):
            rod(p, a + across * u - normal * 6, a + across * u + normal * 6, 3, METAL)
        t, u, v = np.meshgrid(np.arange(t0 + 3, t1 - 2, .75), np.arange(-19, 20), np.arange(-10, 11), indexing='ij')
        taper = 19 - 7 * t / 450
        mask = (abs(u) <= taper) & ((abs(v) >= 7) | (abs(u) >= taper - 3))
        q = start + t[mask, None] * axis + u[mask, None] * across + v[mask, None] * normal
        p.points(q, ARMOR)
        gold = mask & (abs(u) >= taper - 1) & (v >= 8)
        p.points(start + t[gold, None] * axis + u[gold, None] * across + v[gold, None] * normal, GOLD)
        center = start + (t0 + 22) * axis + normal * 10
        rod(p, center - across * 4, center + across * 4, 2, COOL)
    root = start - axis * 18
    rod(p, root, start + axis * 22, 16, DARK)
    rod(p, root, start + axis * 22, 18, GOLD, inner=15)
    return p.finish(), start, end


def _feather(side, index, start, end):
    word = 'left' if side < 0 else 'right'
    label = '左' if side < 0 else '右'
    p = Part(f'wing_feather_{word}_{index + 1:02d}', f'{label}翼第{index + 1:02d}根200×25机械羽骨',
             source='二·3·左右各8根宽25格、长200格机械羽骨',
             nominal_length=200, nominal_width=25, centerline=[start.tolist(), end.tolist()],
             sampling='200格中心轴与25格最大局部截面；端部25格内收尖，黑桁架外侧每34格分段包白金装甲，浅蓝冷却晶条位于装甲接缝。')
    axis, across, normal = _axes(start, end)
    t, u, v = np.meshgrid(np.arange(0, 200, .5), np.arange(-12, 13), np.arange(-5, 6), indexing='ij')
    taper = np.minimum(1, (200 - t) / 25)
    width, thickness = 12 * taper, 5 * taper
    boundary = (abs(u) <= width) & (abs(v) <= thickness)
    spine = boundary & (((abs(u) <= 3) & (abs(v) <= 4)) |
                        ((abs(u) >= width - 2) & (abs(v) <= 3)) |
                        ((np.abs((t % 34) - 17) <= 1.5) & (abs(v) <= 3)))
    p.points(start + t[spine, None] * axis + u[spine, None] * across + v[spine, None] * normal, DARK)
    armor = boundary & (t % 34 <= 27) & ((abs(v) >= thickness - 2) | (abs(u) >= width - 2))
    p.points(start + t[armor, None] * axis + u[armor, None] * across + v[armor, None] * normal, ARMOR)
    edge = boundary & (t % 34 <= 27) & (v >= thickness - 1) & (abs(u) >= width - 1)
    p.points(start + t[edge, None] * axis + u[edge, None] * across + v[edge, None] * normal, GOLD)
    cooling = boundary & (t % 34 >= 28) & (abs(u) <= 3) & (v >= thickness - 1)
    p.points(start + t[cooling, None] * axis + u[cooling, None] * across + v[cooling, None] * normal, COOL)
    p.points([end], ARMOR)
    return p.finish()


def _fire_sail(side, index, first, second):
    word = 'left' if side < 0 else 'right'
    label = '左' if side < 0 else '右'
    p = Part(f'cloak_flame_{word}_{index + 1:02d}', f'{label}翼第{index + 1:02d}条破碎等离子火帆',
             source='二·3·机械羽骨之间波浪状红橙黄白固态等离子缎带',
             sampling='相邻羽骨之间以5格实体厚度取样波浪火帆；边缘和末端保留原文破碎光翼的长裂口，左侧火帆较饱满、右侧较短。')
    a0, a1 = first
    b0, b1 = second
    s, u = np.meshgrid(np.arange(0, 1.001, 1 / 230), np.arange(.08, .93, 1 / 65), indexing='ij')
    a = a0 + s[:, :, None] * (a1 - a0)
    b = b0 + s[:, :, None] * (b1 - b0)
    surface = a * (1 - u[:, :, None]) + b * u[:, :, None]
    phase = index * .65 + (0 if side < 0 else 1.2)
    surface[:, :, 1] += 8 * np.sin(s * math.pi * 2 + phase) * np.sin(math.pi * u) - 5
    surface[:, :, 2] += 9 * np.sin(math.pi * s) * np.sin(math.pi * u + phase)
    fringe = 1 - (.11 if side < 0 else .24) * np.sin(u * math.pi * 4 + phase) ** 2
    slits = (s > .42) & (abs(u - (.46 + .12 * np.sin(s * 5 + phase))) < .045)
    mask = (s < fringe) & ~slits
    colors = np.full(s.shape, RED, np.uint8)
    flame = abs(u - (.48 + .14 * np.sin(s * 5 + phase)))
    colors[flame < .28] = ORANGE
    colors[flame < .105] = YELLOW
    colors[(flame < .027) & (s < .74)] = LIGHT
    for thickness in range(-2, 3):
        q = surface[mask] + [0, thickness, 0]
        for state in (RED, ORANGE, YELLOW, LIGHT):
            selected = colors[mask] == state
            p.points(q[selected], state)
    return p.finish()


def _main_cloak():
    p = Part('cloak_main_left', '左肩不对称薪炎机械披风',
             source='二·3·单边不对称披风，从Y280垂落蜿蜒至Z921地面',
             sampling='左侧披风从(160,280,650)至(430,230,560)的斜肩展开；末端五道火舌落向Z921，纵向波浪和折叠横向曲面均以实体整数方块、5格厚度取样。')
    s, u = np.meshgrid(np.arange(0, 1.001, 1 / 520), np.arange(0, 1.001, 1 / 400), indexing='ij')
    x0, y0, z0 = 160 + 270 * u, 280 - 50 * u, 650 - 90 * u
    x1, y1, z1 = 330 + 240 * u, 12 * np.sin(math.pi * u) ** 2, 921 - 45 * np.sin(math.pi * u) ** 2
    x = (1 - s) * x0 + s * x1 + 45 * np.sin(math.pi * s) * np.sin(2 * math.pi * u + 1.2 * s)
    y = (1 - s) ** 1.3 * y0 + s * y1 + 18 * np.sin(math.pi * s) * np.cos(math.pi * u)
    z = (1 - s) * z0 + s * z1 - 35 * np.sin(math.pi * s) * np.sin(math.pi * u)
    surface = np.stack((x, y, z), axis=-1)
    mask = s <= 1 - .05 * np.sin(5 * math.pi * u) ** 2
    fold = np.cos(3 * math.pi * u + .85 * np.sin(2.4 * math.pi * s))
    states = np.full(s.shape, RED, np.uint8)
    states[fold > .64] = ORANGE
    states[(fold > .94) & (s < .9)] = YELLOW
    states[(fold > .996) & (s < .4)] = LIGHT
    for thickness in range(-2, 3):
        q = surface[mask] + [0, thickness, 0]
        for state in (RED, ORANGE, YELLOW, LIGHT):
            p.points(q[states[mask] == state], state)
    return p.finish()


def _cannon(side, row, index):
    word = 'left' if side < 0 else 'right'
    label = '左' if side < 0 else '右'
    number = row * 8 + index + 1
    if row == 0:
        center = np.array([CX + side * (91 + index * 48), 245 + index * 9, 435 + index * 20], float)
    else:
        center = np.array([CX + side * (131 + index * 45), 130 + index * 12, 750 + index * 20], float)
    p = Part(f'cannon_{word}_{number:02d}', f'{label}翼第{number:02d}座40×15×15重装浮游炮',
             source='二·3·左右各16座40×15×15重装浮游炮',
             dimensions_xyz=[40, 15, 15], center=center.tolist(),
             sampling='长轴平行世界X轴，内端为劫灭尖刃炮口；上排8座位于翼骨前上方、下排8座位于火翼后下方，独立保留黑金机身、白金斜肩和赤红炮芯。')
    t, y, z = np.meshgrid(np.arange(40), np.arange(-7, 8), np.arange(-7, 8), indexing='ij')
    radius = np.where(t < 12, 2 + t * 5 / 12, np.where(t > 34, 7 - (t - 34) * .6, 7))
    body = (abs(y) <= radius) & (abs(z) <= radius) & (abs(y) + abs(z) <= radius * 1.65)
    q = np.stack((center[0] + side * (t - 20), center[1] + y, center[2] + z), axis=-1)
    p.points(q[body], DARK)
    plate = body & (t >= 13) & (t <= 34) & ((abs(z) >= radius - 2) | (y >= radius - 2))
    p.points(q[plate], ARMOR)
    gold = plate & ((abs(z) >= radius - 1) & (y >= 2))
    p.points(q[gold], GOLD)
    core = body & (((abs(y) <= 1) & (abs(z) <= 1)) | ((t % 8 == 0) & (abs(y) <= 4) & (abs(z) <= 4)))
    p.points(q[core], RED)
    muzzle = body & (t <= 3) & (abs(y) + abs(z) <= 2)
    p.points(q[muzzle], YELLOW)
    diamond = body & (abs(t - 25) + abs(z) * 2 <= 5) & (y >= 6)
    p.points(q[diamond], COOL)
    nozzle = center + [-side * 20, 0, 0]
    return p.finish(), nozzle


def build():
    parts, paths = [], {}
    for side in (-1, 1):
        keel, start, end = _keel(side)
        parts.append(keel)
        paths[side] = []
        for index in range(8):
            a = start + (end - start) * ((index + 1) / 9)
            dx = 140 - (140 - (978 - (CX + 38 + 402 * 8 / 9))) * index / 7
            dy = -100 + 37 * index / 7
            dz = math.sqrt(200 ** 2 - dx ** 2 - dy ** 2)
            b = a + [side * dx, dy, dz]
            paths[side].append((a, b))
            parts.append(_feather(side, index, a, b))
        for index in range(7):
            parts.append(_fire_sail(side, index, paths[side][index], paths[side][index + 1]))
    parts.append(_main_cloak())
    for side in (-1, 1):
        word, label = ('left', '左') if side < 0 else ('right', '右')
        links = Part(f'cannon_links_{word}', f'{label}侧16条指向恒星的赤红连接束',
                     source='二·3·每座浮游炮与中央恒星相连的赤红激光束或锁链',
                     sampling='采用半径1.5格实体红色连接杆；独立部件可隐藏以观察火翼轮廓。')
        for row in range(2):
            for index in range(8):
                cannon, nozzle = _cannon(side, row, index)
                parts.append(cannon)
                rod(links, nozzle, STAR_CENTER, 1.5, RED)
        parts.append(links.finish())
    notes = [
        '主龙骨从反应堆后方(527/451,190,520)向两侧扬起，中心轴精确450格；轴端Y310，加装甲截面后上缘约Y320。',
        '左右各8根机械羽骨按200格中心线、25格最大局部宽度离散；旋转截面的世界坐标包围盒不等于200×25。',
        '羽骨向后扇开，原文未给出各羽骨方向；采用向外、向后、下垂的连续扇面，最外端轴线到X0/978，实体截面和端点完整保留。',
        '原文翼组500格深度没有给出前后边界；本取样主翼从Z520后展，包含不对称披风至Z921；浮游炮在Z428..897分两排围翼悬浮。',
        '左肩连续披风形成单边不对称主量体，两侧羽骨间另有各7片破碎火帆；波浪、褶皱与裂口为原文未指定曲面的整数格取样。',
        '32座浮游炮均保留40×15×15世界轴包围盒；赤红连接束单独保留，不占用或预留接口位置。',
        '披风厚度5格以表面Y对称取样，落地表面附近自然包含Y=-2/-1的实体格，按完整边界导出，未裁切到名义Y0。',
    ]
    return parts, notes
