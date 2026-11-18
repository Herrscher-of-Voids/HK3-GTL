import numpy as np

from author_w05_shapes_20261115 import Part, trace


VOID, DEEP, BLUE, LIGHT, PALE, GOLD, SHADE, RED, GLOW, EDGE = range(1, 11)


def inside(points, polygon):
    x, y = points.T
    result = np.zeros(len(points), bool)
    for a, b in zip(polygon, np.roll(polygon, -1, axis=0)):
        if a[1] != b[1]:
            result ^= ((a[1] > y) != (b[1] > y)) & (x < (b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0])
    return result


def patch(part, polygon, surface, depth, state, inset=None, reverse=False):
    polygon = np.asarray(polygon, float)
    lo, hi = np.floor(polygon.min(0)).astype(int), np.ceil(polygon.max(0)).astype(int)
    x, y = np.meshgrid(np.arange(lo[0], hi[0]+1), np.arange(lo[1], hi[1]+1))
    q = np.c_[x.ravel(), y.ravel()]
    mask = inside(q, polygon)
    if inset is not None:
        mask &= ~inside(q, np.asarray(inset))
    q = q[mask]
    z = surface(q[:, 0], q[:, 1])
    for offset in range(depth):
        part.points(np.c_[q, z+(offset if reverse else -offset)], state)


def leaf(part, a, b, width, surface, state=GOLD, rim=2.5, bend=0, reverse=False):
    a, b = np.asarray(a, float), np.asarray(b, float)
    v = b-a
    normal = np.array([-v[1], v[0]])/np.linalg.norm(v)
    t = np.linspace(0, 1, 33)
    center = a[None]+t[:, None]*v+normal[None]*bend*np.sin(np.pi*t)[:, None]
    outer = normal[None]*width*np.sin(np.pi*t)[:, None]
    polygon = np.r_[center+outer, (center-outer)[::-1]]
    inner_t = np.linspace(.12, .88, 29)
    inner_c = a[None]+inner_t[:, None]*v+normal[None]*bend*np.sin(np.pi*inner_t)[:, None]
    inner_w = np.maximum(0, width-rim)*np.sin(np.pi*(inner_t-.12)/.76)
    inner = np.r_[inner_c+normal[None]*inner_w[:, None], (inner_c-normal[None]*inner_w[:, None])[::-1]]
    patch(part, inner, lambda x, y: surface(x, y)+(1 if reverse else -1), 5, VOID, reverse=reverse)
    patch(part, polygon, surface, 6, state, inner, reverse)


def loft(part, samples, state, inner=0, power=2.3):
    samples = np.asarray(samples, float)
    for y in range(int(samples[0, 0]), int(samples[-1, 0])+1):
        cx, cz, rx, rz = [np.interp(y, samples[:, 0], samples[:, j]) for j in range(1, 5)]
        x, z = np.meshgrid(np.arange(np.floor(cx-rx), np.ceil(cx+rx)+1), np.arange(np.floor(cz-rz), np.ceil(cz+rz)+1))
        radius = (abs((x-cx)/rx)**power+abs((z-cz)/rz)**power)
        selected = (radius <= 1) & (radius >= inner)
        part.points(np.c_[x[selected], np.full(selected.sum(), y), z[selected]], state)


def ellipsoid(part, center, radii, state):
    c, r = np.asarray(center), np.asarray(radii)
    x, z = np.meshgrid(np.arange(c[0]-r[0], c[0]+r[0]+1), np.arange(c[2]-r[2], c[2]+r[2]+1))
    for y in range(int(c[1]-r[1]), int(c[1]+r[1])+1):
        selected = ((x-c[0])/r[0])**2+((y-c[1])/r[1])**2+((z-c[2])/r[2])**2 <= 1
        part.points(np.c_[x[selected], np.full(selected.sum(), y), z[selected]], state)


CHEST = np.array([[227, 0, -2, 34, 20], [246, 0, -2, 43, 26], [272, 0, 0, 49, 32],
                  [310, 0, 0, 66, 38], [336, 0, -1, 70, 37], [355, 0, -3, 51, 28], [370, 0, -5, 26, 14]])


def chest_front(x, y):
    w, d, c = [np.interp(y, CHEST[:, 0], CHEST[:, j]) for j in [3, 4, 2]]
    return c+d*np.maximum(0, 1-(abs(x)/w)**2.3)**(1/2.3)


def build_chest():
    p = Part('torso', '前凸胸腹、四叶金饰与收腰背甲', section='body')
    loft(p, CHEST, DEEP)
    loft(p, CHEST, BLUE, .67)
    front = lambda x, y: chest_front(x, y)+1
    for sign in [-1, 1]:
        polygon = np.array([[0, 348], [22, 366], [46, 358], [63, 344], [48, 331], [21, 342]])
        polygon[:, 0] *= sign
        patch(p, polygon, lambda x, y: front(x, y)+2, 5, LIGHT)
        trace(p, [(sign*59, 344, float(front(sign*59, 344)+5)), (sign*32, 354, float(front(sign*32, 354)+5)), (0, 340, float(front(0, 340)+6))], 1.3, EDGE)
        leaf(p, [sign*4, 307], [sign*49, 340], 12.5, lambda x, y: front(x, y)+4, PALE, 6.3, sign*4)
        leaf(p, [sign*5, 307], [sign*41, 261], 10.5, lambda x, y: front(x, y)+3, GOLD, 5.4, -sign*4)
        leaf(p, [sign*58, 329], [sign*45, 263], 5, lambda x, y: front(x, y)+1, SHADE, 2.5, sign*5)
        patch(p, [[sign*3, 345], [sign*14, 354], [sign*24, 345], [sign*14, 341]], lambda x, y: front(x, y)+6, 2, BLUE)
    patch(p, [[0, 323], [10, 312], [8, 299], [0, 291], [-8, 299], [-10, 312]], lambda x, y: front(x, y)+4, 6, GOLD)
    patch(p, [[0, 319], [3, 311], [0, 304], [-3, 311]], lambda x, y: front(x, y)+7, 1, PALE)
    back = lambda x, y: 2*np.interp(y, CHEST[:, 0], CHEST[:, 2])-chest_front(x, y)-3
    for sign in [-1, 1]:
        coords = np.array([[sign*42, 351], [sign*47, 333], [sign*40, 320], [sign*21, 310], [0, 307]])
        trace(p, [(x, y, float(back(x, y))) for x, y in coords], 2.5, GOLD)
        seam = [[sign*23, 365], [sign*43, 352], [sign*55, 333], [sign*51, 312], [sign*38, 290], [sign*29, 250]]
        trace(p, [(x, y, float(back(x, y)+1)) for x, y in seam], 1.2, EDGE)
        leaf(p, [0, 275], [sign*29, 298], 5, back, GOLD, 1.6, reverse=True)
        leaf(p, [0, 275], [sign*24, 249], 4, back, GOLD, 1.5, reverse=True)
    loft(p, [[213, 0, -2, 23, 14], [235, 0, -2, 33, 20]], VOID)
    loft(p, [[218, 0, -2, 30, 19], [229, 0, -2, 37, 23], [241, 0, -2, 35, 22]], BLUE, .76)
    leaf(p, [0, 226], [0, 143], 11, lambda x, y: 26+0*x, GOLD, 4)
    return p.finish()


def build_legs():
    parts = []
    for sign in [-1, 1]:
        p = Part('leg_'+str(sign), ('左' if sign < 0 else '右')+'悬空尖盾腿甲', section='legs')
        cx = sign*60
        samples = np.array([[0, sign*46, -1, 1, 2], [30, sign*48, 0, 14, 12], [70, sign*53, 0, 30, 22],
                            [122, sign*58, 1, 44, 29], [178, sign*62, 2, 54, 32], [216, sign*62, 1, 58, 31], [235, sign*59, -1, 40, 21]])
        loft(p, samples, DEEP)
        loft(p, samples, BLUE, .66)
        def front(x, y):
            center, w, d, c = [np.interp(y, samples[:, 0], samples[:, j]) for j in [1, 3, 4, 2]]
            return c+d*np.maximum(0, 1-(abs(x-center)/w)**2.3)**(1/2.3)+1
        def poly(coords):
            return [[cx+sign*x*1.08, y] for x, y in coords]
        def raised(x, y, center_x, center_y, width, height, rise):
            local = (x-cx)*sign/1.08
            return front(x, y)+2+rise*np.maximum(0, 1-((local-center_x)/width)**2-((y-center_y)/height)**2)
        def plate(coords, shape, state):
            polygon = np.array(poly(coords))
            surface = lambda x, y: raised(x, y, *shape)
            patch(p, polygon, surface, 21, EDGE)
            inset = polygon.mean(0)+(polygon-polygon.mean(0))*.91
            patch(p, inset, lambda x, y: surface(x, y)+1, 21, state)
        patch(p, poly([[-44, 216], [-28, 235], [0, 241], [30, 235], [46, 219], [29, 196], [6, 206], [-22, 200]]), lambda x, y: raised(x, y, 0, 219, 49, 30, 8), 13, LIGHT)
        plate([[-39, 198], [-22, 211], [0, 202], [12, 165], [4, 121], [-9, 104], [-28, 136]], (-13, 163, 28, 59, 13), BLUE)
        plate([[4, 200], [31, 209], [45, 188], [36, 152], [10, 133], [2, 158]], (25, 177, 24, 44, 12), DEEP)
        plate([[-31, 140], [-7, 115], [5, 139], [19, 155], [29, 133], [15, 86], [-5, 27], [-13, 76]], (1, 98, 26, 69, 14), BLUE)
        for path in [[[-42, 213], [-27, 232], [-3, 238], [27, 234], [43, 222]], [[-31, 142], [-10, 118], [5, 134], [25, 150]], [[-5, 27], [5, 67], [24, 112]]]:
            trace(p, [(cx+sign*x*1.08, y, float(front(cx+sign*x*1.08, y)+5)) for x, y in path], 1.4, EDGE)
        for x, y, radius in [(-12, 226, 3.5), (12, 226, 3.5), (0, 217, 3.0)]:
            center = cx+sign*x*1.08
            ellipsoid(p, (center, y, round(float(raised(center, y, 0, 219, 49, 30, 8)))), (radius, radius, 2), VOID)
        for x, y, peak in [(-37, 231, 256), (-18, 238, 260), (27, 233, 262), (44, 219, 247)]:
            center = cx+sign*x*1.08
            p.hull([(center-4, y, -3), (center+4, y, -3), (center-4, y, 9), (center+4, y, 9), (center+sign*3, peak, -5)], GOLD)
        leaf(p, [cx+sign*48, 213], [cx+sign*39, 156], 4.7, lambda x, y: front(x, y)+1, SHADE, 1.7)
        back = lambda x, y: 2*np.interp(y, samples[:, 0], samples[:, 2])-front(x, y)-1
        for coords in [[[-29, 210], [-7, 223], [22, 218], [36, 195], [20, 152], [-7, 116], [-29, 145]],
                       [[-20, 148], [1, 115], [18, 135], [18, 103], [-5, 30], [-10, 81]]]:
            polygon = np.array(poly(coords))
            patch(p, polygon, back, 5, EDGE, reverse=True)
            inset = polygon.mean(0)+(polygon-polygon.mean(0))*.94
            patch(p, inset, lambda x, y: back(x, y)-1, 5, BLUE, reverse=True)
        parts.append(p.finish())
    return parts


def build_shoulders():
    parts = []
    for sign in [-1, 1]:
        p = Part('shoulder_'+str(sign), ('左' if sign < 0 else '右')+'包覆肩壳与上挑尖峰', section='shoulders')
        p.beam((sign*76, 338, -5), (sign*111, 329, -2), 15, VOID)
        samples = np.array([[302, 145, 16, 15], [312, 145, 36, 24], [328, 147, 53, 34],
                            [346, 149, 59, 39], [364, 154, 55, 36], [382, 162, 44, 29],
                            [400, 172, 30, 22], [418, 182, 16, 13], [433, 190, 6, 6], [444, 194, 1, 2]])
        def face(x, y):
            center, width, depth = [np.interp(y, samples[:, 0], samples[:, j]) for j in [1, 2, 3]]
            return depth*np.maximum(0, 1-(abs(sign*x-center)/width)**2.7)**(1/2.7)
        x, z = np.meshgrid(np.arange(81, 212), np.arange(-43, 44))
        for y in range(302, 445):
            center, width, depth = [np.interp(y, samples[:, 0], samples[:, j]) for j in [1, 2, 3]]
            outer = abs((x-center)/width)**2.7+abs(z/depth)**2.7
            cavity = ((x-116)/31)**2+((y-338)/31)**2+((z-17)/33)**2
            mask = (outer <= 1) & ~((cavity < 1) & (z > -4))
            q = np.c_[sign*x[mask], np.full(mask.sum(), y), z[mask]]
            p.points(q, BLUE)
            p.points(q[(q[:, 2] > 10) & (q[:, 2] > face(q[:, 0], y)-2) & (sign*q[:, 0] < center+5) & (y > 355)], LIGHT)
        ellipsoid(p, (sign*110, 338, -5), (26, 28, 5), VOID)
        theta = np.linspace(.08*np.pi, 1.6*np.pi, 55)
        rim = [(sign*(116+29*np.cos(t)), 338+30*np.sin(t), 18-5*np.cos(t)) for t in theta]
        trace(p, rim, 1.5, SHADE)
        p.hull([(sign*166, 365, -30), (sign*184, 353, -29), (sign*194, 444, -1), (sign*171, 381, -11)], GOLD)
        p.hull([(sign*176, 381, 17), (sign*194, 444, 1), (sign*183, 380, 22), (sign*189, 361, 19)], LIGHT)
        leaf(p, [sign*186, 353], [sign*192, 416], 5, lambda x, y: 20+0*x, GOLD, 2)
        p.hull([(sign*169, 338, 27), (sign*198, 326, 19), (sign*181, 310, 23), (sign*151, 315, 35)], BLUE)
        ridge = [[sign*150, 351], [sign*158, 376], [sign*170, 401], [sign*183, 426], [sign*191, 440]]
        trace(p, [(x, y, float(face(x, y))) for x, y in ridge], 1.2, EDGE)
        slot = [[sign*151, 330], [sign*169, 333], [sign*190, 328], [sign*193, 325], [sign*171, 328], [sign*153, 327]]
        patch(p, slot, lambda x, y: face(x, y)+1, 3, VOID)
        for a, b, width in [([154, 341], [155, 351], 2.1), ([150, 337], [143, 341], 1.7), ([159, 338], [165, 341], 1.7)]:
            leaf(p, [sign*a[0], a[1]], [sign*b[0], b[1]], width, lambda x, y: face(x, y)+1, EDGE, width)
        rear = [[sign*148, 318], [sign*170, 337], [sign*179, 362], [sign*187, 398], [sign*191, 428]]
        trace(p, [(x, y, float(-face(x, y))) for x, y in rear], 1.2, EDGE)
        parts.append(p.finish())
    return parts


def build_main_arms():
    parts = []
    for sign in [-1, 1]:
        p = Part('arm_'+str(sign), ('左' if sign < 0 else '右')+'主臂、金球肘与垂指', section='arms')
        p.beam((sign*118, 325, -3), (sign*137, 274, 9), 16, DEEP)
        p.beam((sign*119, 316, -1), (sign*131, 288, 4), 19, BLUE, 14)
        ellipsoid(p, (sign*139, 262, 14), (26, 27, 26), GOLD)
        ellipsoid(p, (sign*139, 262, 14), (24, 25, 25), PALE)
        elbow = lambda x, y: 14+25*np.sqrt(np.maximum(0, 1-((sign*x-139)/24)**2-((y-262)/25)**2))
        theta = np.linspace(0, 2*np.pi, 33)
        for dx, dy, r in [(0, -6, 8), (-11, 11, 5.5), (11, 11, 5.5)]:
            polygon = np.c_[sign*(139+dx+(r+2)*np.cos(theta)), 262+dy+(r+2)*np.sin(theta)]
            inset = np.c_[sign*(139+dx+r*np.cos(theta)), 262+dy+r*np.sin(theta)]
            patch(p, polygon, lambda x, y: elbow(x, y)+1, 3, SHADE)
            patch(p, inset, lambda x, y: elbow(x, y)+2, 2, VOID)
        for path in [[[-22, -1], [-15, -2], [-9, 0], [-3, 5], [0, 13], [0, 23]],
                     [[22, -1], [15, -2], [9, 0], [3, 5], [0, 13]], [[0, -15], [0, -23]]]:
            trace(p, [(sign*(139+x), 262+y, float(elbow(sign*(139+x), 262+y))) for x, y in path], .8, SHADE)
        samples = [[142, sign*157, 37, 15, 15], [161, sign*154, 32, 25, 25], [201, sign*148, 27, 31, 28], [230, sign*143, 22, 29, 25], [249, sign*143, 20, 19, 17]]
        loft(p, samples, DEEP)
        loft(p, samples, BLUE, .6)
        def face(x, y):
            center, w, d, c = [np.interp(y, np.array(samples)[:, 0], np.array(samples)[:, j]) for j in [1, 3, 4, 2]]
            return c+d*np.maximum(0, 1-(abs(x-center)/w)**2.3)**(1/2.3)
        patch(p, [[sign*x, y] for x, y in [[134, 237], [152, 250], [175, 278], [175, 229], [164, 194], [145, 183], [128, 203]]], lambda x, y: face(x, y)+2, 7, BLUE)
        patch(p, [[sign*x, y] for x, y in [[133, 205], [146, 213], [160, 201], [158, 176], [143, 189]]], lambda x, y: face(x, y)+8, 3, PALE)
        patch(p, [[sign*x, y] for x, y in [[159, 182], [173, 199], [171, 220], [161, 208]]], lambda x, y: face(x, y)+6, 3, GOLD)
        p.hull([(sign*170, 225, 20), (sign*180, 201, 24), (sign*161, 243, 37),
                (sign*177, 279, 16), (sign*179, 279, 16), (sign*177, 279, 18), (sign*179, 279, 18)], BLUE)
        trace(p, [(sign*133, 160, 54), (sign*150, 151, 56), (sign*172, 165, 49)], 2.8, GOLD)
        ellipsoid(p, (sign*158, 133, 39), (17, 18, 12), BLUE)
        p.ring((sign*158, 142, 39), 13, 2, SHADE, depth=4)
        p.ring((sign*158, 145, 39), 13, 1.5, GOLD, depth=2)
        p.beam((sign*152, 141, 46), (sign*169, 133, 45), 4, GOLD)
        for finger in range(4):
            x = sign*(145+8*finger)
            path = [(x, 126, 47), (x-sign*1, 113-finger%2*2, 53), (x-sign*5, 104-finger%2*2, 57), (x-sign*11, 105, 62)]
            for j, (a, b) in enumerate(zip(path, path[1:])):
                p.beam(a, b, 4.6 if j < 2 else 4, GOLD if j != 1 else PALE)
                p.sphere(a, 4.8, SHADE)
            p.sphere(path[-1], 3.7, GOLD)
        path = [(sign*143, 136, 43), (sign*134, 128, 49), (sign*134, 117, 57)]
        trace(p, path, 5.2, GOLD)
        p.sphere(path[1], 5.4, SHADE)
        result = p.finish()
        result.p[:, 0] += sign*30
        parts.append(result)
    return parts


def build_body():
    return [build_chest(), *build_legs(), *build_shoulders(), *build_main_arms()]
