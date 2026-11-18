import math

import numpy as np

from author_w05_shapes_20261115 import Part


ORIGIN = np.array([-68, -66, -46])
SIZE = np.array([137, 161, 143])


def region(low, high):
    low, high = np.floor(low).astype(int), np.ceil(high).astype(int)
    x, y, z = np.mgrid[low[0]:high[0]+1, low[1]:high[1]+1, low[2]:high[2]+1]
    return tuple(slice(a, b+1) for a, b in zip(low-ORIGIN, high-ORIGIN)), x, y, z


def sphere(volume, center, radius, state):
    block, x, y, z = region(np.asarray(center)-radius, np.asarray(center)+radius)
    distance = (x-center[0])**2+(y-center[1])**2+(z-center[2])**2
    volume[block][distance <= radius*radius] = state


def phalanx(volume, start, end, radius):
    a, b = np.asarray(start, float), np.asarray(end, float)
    block, x, y, z = region(np.minimum(a, b)-radius, np.maximum(a, b)+radius)
    direction = b-a
    length = np.linalg.norm(direction)
    direction /= length
    q = np.stack((x, y, z), -1)-a
    along = np.sum(q*direction, -1)
    radial = q-along[..., None]*direction
    side = np.array([1., 0., 0.])-direction*direction[0]
    side /= np.linalg.norm(side)
    face = np.cross(side, direction)
    u, v = np.sum(radial*side, -1), np.sum(radial*face, -1)
    progress = np.clip(along/length, 0, 1)
    width = radius*(1-.17*progress)+.45*(progress < .28)
    inside = (np.maximum(np.abs(u), np.abs(v)) <= width*.94) & (np.abs(u)+np.abs(v) <= width*1.34) & (along >= 1.8) & (along <= length-1.9)
    volume[block][inside] = 6
    volume[block][inside & (v > width*.22)] = 5
    volume[block][inside & (v < -width*.65)] = 7


def hinge(volume, center, axis, radius):
    sphere(volume, center, radius, 1)
    block, x, y, z = region(np.asarray(center)-radius*1.2, np.asarray(center)+radius*1.2)
    q = np.stack((x, y, z), -1)-center
    across = np.sum(q*np.asarray(axis), -1)
    disc = (np.sum(q*q, -1)-across*across <= (radius*.62)**2) & (np.abs(across) >= radius*.78) & (np.abs(across) <= radius*1.12)
    volume[block][disc] = 6
    volume[block][disc & (np.abs(across) > radius*.96)] = 5


def finger(volume, root, lengths, bends, splay, radius):
    joints = [np.asarray(root, float)]
    for length, bend in zip(lengths, bends):
        angle = math.radians(bend)
        direction = np.array([math.sin(splay)*math.cos(angle), math.cos(splay)*math.cos(angle), math.sin(angle)])
        joints.append(joints[-1]+direction*length)
    side = np.array([math.cos(splay), -math.sin(splay), 0])
    for joint in joints[:-1]:
        hinge(volume, joint, side, radius*.9)
    for i, (a, b) in enumerate(zip(joints[:-1], joints[1:])):
        width = radius*(1-.1*i)
        phalanx(volume, a, b, width)
    sphere(volume, joints[-1], radius*.66, 6)


POSES = {
    "舒展": ([5, 12, 22], [0, 8, 20], [4, 14, 30], [12, 27, 43]),
    "前伸": ([4, 12, 28], [8, 20, 43], [25, 55, 85], [40, 80, 115]),
    "弯抓": ([25, 62, 105], [15, 58, 110], [20, 65, 115], [35, 82, 125]),
    "握拳": ([40, 92, 145], [35, 90, 145], [40, 98, 150], [45, 105, 155]),
    "垂指": ([12, 42, 77], [2, 25, 62], [12, 48, 88], [32, 67, 108]),
}


def hand_volume(pose):
    volume = np.zeros(SIZE, np.uint8)
    x, y, z = np.mgrid[ORIGIN[0]:ORIGIN[0]+SIZE[0], ORIGIN[1]:ORIGIN[1]+SIZE[1], ORIGIN[2]:ORIGIN[2]+SIZE[2]]
    radius = np.sqrt(x*x+z*z)
    rim_y = -48+2*np.cos(np.arctan2(z, x)*4)
    sleeve_radius = 23+3*np.clip((-y-19)/29, 0, 1)
    sleeve = (y >= rim_y) & (y <= -19) & (radius <= sleeve_radius)
    volume[sleeve] = 3
    volume[sleeve & (z < -8)] = 2
    volume[sleeve & (z > 8)] = 4
    cavity = (y >= -51) & (y <= -23) & (radius < sleeve_radius-4)
    volume[cavity] = 0
    lining = sleeve & (radius < sleeve_radius-3) & (radius >= sleeve_radius-4.5)
    volume[lining] = 1
    rear_lip = (y >= rim_y) & (y <= rim_y+2) & (radius >= sleeve_radius-3) & (radius <= sleeve_radius+1)
    volume[rear_lip] = 6
    volume[rear_lip & (z > 0)] = 5

    sleeve_surface = sleeve & (radius >= sleeve_radius-1.5) & (z > 0)
    emblem = (x/6.8)**2+((y+34)/10.5)**2
    volume[sleeve_surface & (emblem <= 1)] = 6
    volume[sleeve_surface & (emblem < .45)] = 1

    palm = (np.abs(x)/31)**3+((np.abs(y-4))/27)**3+(np.abs(z)/14)**3 <= 1
    volume[palm] = 2
    volume[palm & (z < -3)] = 3
    volume[palm & (z < -11)] = 4
    back_outline = (np.abs(x)/29)**3+(np.abs(y-3)/24)**3
    back_z = -12-3.5*(1-np.clip(back_outline, 0, 1))
    back_plate = (back_outline <= 1) & (z >= back_z) & (z <= -10)
    volume[back_plate] = 3
    volume[back_plate & (z < back_z+1.5)] = 4
    for center in [-13, 0, 13]:
        t = (y+11)/30
        leaf_width = 2.2*np.sin(np.pi*np.clip(t, 0, 1))**.8
        groove = (t >= 0) & (t <= 1) & (np.abs(x-center) <= leaf_width) & (back_outline <= 1)
        volume[groove & (z >= back_z) & (z < back_z+1.6)] = 0
        volume[groove & (z >= back_z+1.6) & (z < back_z+3)] = 10
    cuff = (y >= -23) & (y <= -19) & (radius <= 27) & (radius >= 23)
    volume[cuff] = 6
    volume[cuff & (z > 5)] = 5
    palm_outline = (np.abs(x)/31)**3+(np.abs(y-4)/27)**3
    border = palm & (palm_outline >= .72) & (np.abs(z) <= 6)
    volume[border] = 6
    for root_x, root_y in zip([-22, -7, 7, 22], [21, 27, 29, 23]):
        lobe = ((x-root_x)/8)**2+((y-root_y)/7)**2 <= 1
        volume[lobe & (np.abs(z) <= 10)] = 6

    leaf_root = np.array([0., -17.])
    for leaf_tip, width in [((-42, -32), 8), ((-17, -60), 10), ((17, -60), 10), ((42, -32), 8)]:
        direction = np.array(leaf_tip)-leaf_root
        t = ((x-leaf_root[0])*direction[0]+(y-leaf_root[1])*direction[1])/np.dot(direction, direction)
        across = ((x-leaf_root[0])*direction[1]-(y-leaf_root[1])*direction[0])/np.linalg.norm(direction)
        profile = np.sin(np.pi*np.clip(t, 0, 1))
        leaf_width = 1+width*profile**.72
        leaf_z = -17-11*np.clip(t, 0, 1)
        thickness = 2.5+1.5*profile
        leaf = (t >= 0) & (t <= 1) & ((across/leaf_width)**2+((z-leaf_z)/thickness)**2 <= 1)
        volume[leaf] = 6
        volume[leaf & (z > leaf_z+.8)] = 5
        vein = leaf & (t >= .22) & (t <= .85) & (np.abs(across) <= leaf_width*.33) & (z > leaf_z+1)
        volume[vein] = 7
        volume[vein & (z > leaf_z+2)] = 1

    for i, (root_x, root_y, length, bends) in enumerate(zip([-22, -7, 7, 22], [21, 27, 29, 23], [15, 19, 20, 16], POSES[pose])):
        finger(volume, (root_x, root_y, 3), [length*1.15, length*.897, length*.736], bends, [-.23, -.07, .06, .24][i], 5.5)
    thumb = [(-29, -2, 4), (-42, 6, 9), (-46, 23, 17), (-36, 32, 23)]
    if pose == "握拳":
        thumb = [(-29, -2, 4), (-41, 9, 12), (-30, 23, 27), (-11, 25, 31)]
    saddle = ((x+28)/9)**2+((y+3)/12)**2+((z-2)/11)**2 <= 1
    volume[saddle] = 6
    volume[saddle & (z >= 0)] = 5
    saddle_inset = ((x+30)/6)**2+((y+1)/8)**2 <= 1
    volume[saddle & saddle_inset & (z >= 7)] = 2
    for joint in thumb[:-1]:
        hinge(volume, joint, [0, -.3, math.sqrt(.91)], 5.3)
    for i, (a, b) in enumerate(zip(thumb[:-1], thumb[1:])):
        phalanx(volume, a, b, 6.3-i*.55)
    sphere(volume, thumb[-1], 3.7, 6)
    return volume


def rotation(angles):
    x, y, z = np.radians(angles)
    cx, sx, cy, sy, cz, sz = math.cos(x), math.sin(x), math.cos(y), math.sin(y), math.cos(z), math.sin(z)
    return np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]]) @ np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]]) @ np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])


HANDS = [
    ("F01", (-306, 488, -35), (-16, -25, -18), .48, "握拳"),
    ("F02", (-125, 465, 45), (0, -8, 8), .78, "弯抓"),
    ("F03", (-314, 366, 75), (-15, -15, 58), .95, "舒展"),
    ("F04", (-386, 323, -65), (15, 22, -32), .43, "握拳"),
    ("F05", (-396, 205, 65), (22, -22, 145), .83, "弯抓"),
    ("F06", (-253, 235, -50), (-26, 12, -155), .59, "前伸"),
    ("F07", (140, 463, 50), (20, 18, 165), .83, "垂指"),
    ("F08", (316, 370, 60), (-18, 20, -55), .95, "舒展"),
    ("F09", (386, 319, -45), (12, -20, 30), .52, "握拳"),
    ("F10", (373, 218, 85), (15, 22, -100), .87, "弯抓"),
]


def place_hand(volume, code, center, angles, scale, pose):
    occupied = np.argwhere(volume)
    low, high = occupied.min(0)+ORIGIN, occupied.max(0)+ORIGIN
    corners = np.array([[a, b, c] for a in [low[0]-.5, high[0]+.5] for b in [low[1]-.5, high[1]+.5] for c in [low[2]-.5, high[2]+.5]])
    matrix = rotation(angles)
    corners = corners @ matrix.T*scale+center
    lo, hi = np.floor(corners.min(0)).astype(int), np.ceil(corners.max(0)).astype(int)
    part = Part(f"floating_hand_{code.lower()}", f"独立悬浮手{code}·{pose}", section="hands", source="V05", source_hand=code, center=list(center), rotation=list(angles), scale=scale, pose=pose)
    x, z = np.mgrid[lo[0]:hi[0]+1, lo[2]:hi[2]+1]
    for y in range(lo[1], hi[1]+1):
        world = np.c_[x.ravel(), np.full(x.size, y), z.ravel()]
        local = np.rint(((world-center) @ matrix)/scale).astype(int)-ORIGIN
        inside = np.all((local >= 0) & (local < SIZE), axis=1)
        selected = local[inside]
        states = volume[selected[:, 0], selected[:, 1], selected[:, 2]]
        points = world[inside]
        for state in range(1, 11):
            part.points(points[states == state], state)
    return part.finish()


def build_hands():
    volumes = {pose: hand_volume(pose) for pose in POSES}
    return [place_hand(volumes[pose], code, center, angles, scale, pose) for code, center, angles, scale, pose in HANDS]
