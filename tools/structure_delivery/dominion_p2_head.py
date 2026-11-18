import numpy as np

from author_w05_shapes_20261115 import Part


def face_mask(x, y, outline):
    inside = np.zeros(x.shape, bool)
    for a, b in zip(outline, outline[1:]+outline[:1]):
        if a[1] == b[1]:
            continue
        inside ^= ((a[1] > y) != (b[1] > y)) & (x < (b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0])
    return inside


def build_head():
    x, y, z = np.mgrid[-34:35, 358:427, -33:36]
    volume = np.zeros(x.shape, np.uint8)
    plane = 414-.18*(z+1)
    radial = (x/30)**2+((z+1)/25)**2
    bowl = radial+((plane-y)/33)**2
    cranium = (x/30)**2+((y-401)/23)**2+((z+3)/27)**2
    skull = ((bowl <= 1) & (y <= plane)) | (cranium <= 1)
    skin = np.minimum(bowl, cranium) > .88
    volume[skull] = 3
    volume[skull & (x > 9)] = 2
    volume[skull & (x < -10) & skin & (y > 397)] = 4
    volume[skull & (y < 388)] = 2
    neck = (x/11)**2+((y-369)/11)**2+((z+4)/12)**2 <= 1
    volume[neck] = 1

    width = np.interp(y, [375, 384, 399, 409], [1, 11, 23, 25])
    opening = (z > 4) & (y < 408) & (np.abs(x) < width+1)
    volume[opening] = 0
    face_z = 20-.12*np.abs(x)
    face = (y >= 375) & (y <= 410) & (np.abs(x) <= width) & (z >= 4) & (z <= face_z)
    volume[face] = 1

    brow = (radial >= .76) & (radial <= 1.03) & (np.abs(y-plane) <= 2.5)
    volume[brow] = 6
    volume[brow & (y >= plane+.3)] = 5
    volume[brow & (x > 11) & (y < plane)] = 7
    brow_front = face_mask(x, y, [(-29, 415), (-22, 407), (0, 402), (22, 407), (29, 415), (17, 413), (0, 408), (-17, 413)])
    brow_z = 32-.25*np.abs(x)
    brow_front &= (z >= brow_z-4) & (z <= brow_z)
    volume[brow_front] = 6
    volume[brow_front & (y >= 408)] = 5
    back_leaf = (x/22)**2+((y-402)/18)**2
    volume[skull & (z < -7) & skin & (np.abs(back_leaf-1) < .07)] = 6
    curl = face_mask(z, y, [(-25, 400), (-21, 388), (-12, 382), (0, 383),
        (8, 390), (4, 393), (-3, 388), (-11, 389), (-16, 398), (-20, 403)])
    curl &= (np.abs(x) >= 19) & (np.abs(x) <= 28) & (cranium <= 1.14)
    volume[curl] = 3
    volume[curl & (np.abs(x) >= 27)] = 2
    curl_groove = face_mask(z, y, [(-20, 398), (-17, 390), (-10, 386),
        (-1, 387), (4, 391), (-3, 389), (-11, 389), (-16, 394)])
    volume[curl_groove & curl & (np.abs(x) >= 26)] = 10

    nose = face_mask(x, y, [(-7, 404), (7, 404), (2, 378), (0, 375), (-2, 378)])
    nose_z = 29-.12*(404-y)-.10*np.abs(x)
    nose &= (z >= nose_z-3) & (z <= nose_z)
    volume[nose] = 6
    volume[nose & (x <= 0)] = 5
    volume[nose & (y < 382)] = 7

    for side in (-1, 1):
        eye = face_mask(side*x, y, [(10, 399), (17, 404), (19, 403), (17, 399),
            (15, 399), (16, 397), (13, 396), (11, 397)])
        eye_z = 23-.13*np.abs(x)
        slot = face_mask(side*x, y, [(7, 399), (21, 407), (21, 397), (10, 393)])
        slot &= (z >= eye_z-3) & (z <= eye_z-1)
        volume[slot] = 1
        eye &= (z >= eye_z-2) & (z <= eye_z)
        volume[eye] = 8
        pupil = np.abs(side*x-14.5)+np.abs(y-400.5) <= 1.1
        volume[eye & pupil] = 1
        cheek = face_mask(side*x, y, [(21, 403), (24, 399), (19, 386), (2, 374), (8, 383), (16, 393)])
        cheek_z = 21-.1*np.abs(x)+.1*(400-y)
        cheek &= (z >= cheek_z-5) & (z <= cheek_z)
        volume[cheek] = 6 if side > 0 else 5
        groove = face_mask(side*x, y, [(17, 395), (16, 390), (8, 382), (12, 389)])
        volume[groove & cheek & (z >= cheek_z-1.2)] = 10
        volume[groove & cheek & (z >= cheek_z-.3)] = 1

    part = Part('dominion_p2_head', '乌合之众原作头盔', section='head',
        references=['A043', 'A075', 'A101', 'A134', 'A179', 'A181'],
        notes='A179斜口厚金眉与黑眼槽，A181圆鼓后颅和卷曲侧下缘，A134金颊折面与细长V形面甲。')
    indices = np.where(volume)
    part.points(np.c_[x[indices], y[indices], z[indices]], volume[indices])
    return [part.finish()]
