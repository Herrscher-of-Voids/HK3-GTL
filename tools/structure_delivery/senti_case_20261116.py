# -*- coding: utf-8 -*-
from pathlib import Path
import math

import cv2
import numpy as np
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[2]
REFERENCE = ROOT / 'deliveries/0005_W09_识律武器多角度参考_20261116/参考原帧/05-Lor5aVmdiUE-136.25s.jpg'
OUTLINE = [(188,852),(300,755),(421,668),(543,583),(663,518),(768,478),
    (860,449),(905,417),(942,379),(974,359),(1008,347),(1042,328),
    (1075,313),(1103,311),(1130,324),(1150,325),(1163,316),(1167,299),
    (1155,271),(1159,260),(1177,281),(1199,287),(1215,291),(1218,261),
    (1238,277),(1258,311),(1276,345),(1294,365),(1313,381),(1316,404),
    (1336,394),(1354,373),(1355,393),(1339,427),(1331,446),(1342,461),
    (1327,489),(1316,504),(1290,514),(1253,511),(1213,507),(1180,491),
    (1146,483),(1116,491),(1078,520),(1047,533),(1008,543),(970,559),
    (929,581),(897,603),(865,632),(835,663),(804,691),(774,709),
    (747,720),(708,737),(663,753),(617,771),(570,785),(521,796),
    (465,807),(418,814),(369,818),(314,827),(255,840)]


def build():
    source = np.asarray(Image.open(REFERENCE).convert('RGB'))
    mask_image = Image.new('L', (1920, 1080))
    ImageDraw.Draw(mask_image).polygon(OUTLINE, fill=255)
    origin = np.array([188., 852.])
    along = np.array([.916, -.401]); along /= np.linalg.norm(along)
    across = np.array([-along[1], along[0]])
    scale = .278
    outline = np.asarray(OUTLINE)
    model = np.c_[(outline-origin) @ across, (outline-origin) @ along] * scale
    low = np.floor(model.min(0)).astype(int) - 2
    high = np.ceil(model.max(0)).astype(int) + 2
    xx, yy = np.meshgrid(np.arange(low[0], high[0]+1), np.arange(low[1], high[1]+1))
    image_xy = origin + xx[...,None] / scale * across + yy[...,None] / scale * along
    coords = np.rint(image_xy).astype(int)
    silhouette = np.asarray(mask_image)[coords[...,1], coords[...,0]] > 0
    rgb = source[coords[...,1], coords[...,0]].astype(float)
    distance = cv2.distanceTransform(silhouette.astype('uint8'), cv2.DIST_L2, 5)
    ivory = (rgb[...,0] > 156) & (rgb[...,1] > 147) & (rgb[...,2] > 138)
    red = (rgb[...,0] > 80) & (rgb[...,0] > rgb[...,1]*1.5) & (rgb[...,0] > rgb[...,2]*1.22)
    count, components, stats, _ = cv2.connectedComponentsWithStats(ivory.astype('uint8'), 8)
    for component in range(1,count):
        if stats[component,cv2.CC_STAT_AREA] < 3:
            ivory[components==component] = False
    voxels, heights = {}, {}
    for row, col in zip(*np.nonzero(silhouette)):
        x, y = int(xx[row,col]), int(yy[row,col])
        edge = distance[row,col]
        thickness = int(min(9, 2+edge*.65))
        front = thickness if not red[row,col] else max(2, thickness-3)
        heights[x,y] = front
        front_state = 3 if ivory[row,col] else 5 if red[row,col] else 1
        if edge < 1.5:
            front_state = 2 if not ivory[row,col] else 3
        for z in range(-thickness, front+1):
            material = 6 if abs(z) < thickness-2 else 2
            if z == front:
                material = front_state
            if z == -thickness:
                material = 3 if edge < 2.5 and ivory[row,col] else 1
            voxels[x,y,z] = material
    for x in range(-31,4):
        for y in range(267,302):
            dx,dy=x+14,y-284
            if dx*dx+dy*dy<=15.5**2 and (x,y) in heights:
                white=dx>=0
                if dx*dx+(dy-7.75)**2<=7.75**2:
                    white=True
                if dx*dx+(dy+7.75)**2<=7.75**2:
                    white=False
                if dx*dx+(dy-7.75)**2<=2.3**2:
                    white=False
                if dx*dx+(dy+7.75)**2<=2.3**2:
                    white=True
                top=heights[x,y]
                voxels[x,y,top]=3 if white else 1
    for x in range(-20,3):
        for y in range(305,328):
            dx,dy=x+9,y-316
            r=math.hypot(dx,dy)
            if r<=9 and (x,y) in heights:
                top=heights[x,y]
                surface=5 if r>6.5 else 11 if r>3 else 8
                for z in range(top,top+1+int(3*(1-r/10))):
                    voxels[x,y,z]=surface
                if (dx+2)**2+(dy-3)**2<2:
                    voxels[x,y,z]=10
    # 匣口的柄段按独立圆截面生成，图上被手臂遮住的连接保持短颈。
    grip_a, grip_b = np.array([1272.,375.]), np.array([1349.,332.])
    a = np.array([float((grip_a-origin) @ across)*scale, float((grip_a-origin) @ along)*scale, 0.])
    b = np.array([float((grip_b-origin) @ across)*scale, float((grip_b-origin) @ along)*scale, 0.])
    direction = b-a
    for t in np.linspace(0,1,48):
        center = a+direction*t
        for dx in range(-3,4):
            for dz in range(-3,4):
                if dx*dx+dz*dz <= 8:
                    p = tuple(np.rint(center+[dx,0,dz]).astype(int))
                    voxels[p] = 3 if math.floor(t*8)%2==0 else 5
    return [dict(id='case',title='武器匣 · 太极纹匣体',voxels=voxels,
        features=['依据官方转台宽面逐格取样轮廓及太极、云火纹。',
            '黑色宽面、骨白饰边与朱红侧壁；弯尖与头部不对称冠口。',
            '圆截面柄段、分层侧壁与收薄边缘，含凸起圆晶的最大厚度22格。',
            '厚度和背面封板依据侧视作体积转译，隐藏背纹采用简化封板。'],
        references=['R03','R04','R05','R06','R09','R10'],
        views={'taiji':dict(target=[-9,305,9],radius=40),
            'tip':dict(target=[0,38,3],radius=40),
            'rim':dict(target=[18,175,0],radius=46)})]


if __name__ == '__main__':
    for model in build():
        p=np.asarray(list(model['voxels']))
        print(model['id'],len(p),(p.max(0)-p.min(0)+1).tolist())
