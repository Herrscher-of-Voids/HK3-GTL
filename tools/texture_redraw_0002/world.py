from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import random

IDS = ['spatial_probe', 'industrial_work_drone', 'worn_resource_probe', 'worn_work_drone',
       'drone_disassembly_scrap', 'empty_bubble_containment_vessel', 'unstable_simulated_world_bubble',
       'stable_simulated_world_bubble', 'world_model_carrier', 'world_matter_seed',
       'bubble_termination_charge', 'bubble_container_remnant', 'failed_containment_shell',
       'reverse_engineering_specimen', 'failed_engineering_specimen',
       'ship_engineering_archive', 'erosion_research_module']

EDGE = '#34383c'
SHADOW = '#4c5359'
IRON = '#7b858b'
STEEL = '#a4adb0'
LIT = '#d5d9ce'
WHITE = '#f0eee0'
COPPER = '#a57449'
GOLD = '#d6b96f'
BRASS = '#725b3b'
BLUE = '#417d99'
CYAN = '#74b0b4'
PALE = '#b7d8cf'
VIOLET = '#7b568b'
LILAC = '#b290c3'
DARKV = '#44384f'


def canvas():
    im = Image.new('RGBA', (64, 64))
    return im, ImageDraw.Draw(im)


def surface(im, points, colors, seed=1):
    mask = Image.new('1', im.size)
    ImageDraw.Draw(mask).polygon(points, fill=1)
    d = ImageDraw.Draw(im)
    d.polygon(points, fill=colors[1])
    rng = random.Random(seed)
    x0, y0, x1, y1 = mask.getbbox()
    for y in range(y0 + 1, y1 - 1, 2):
        for x in range(x0 + 1, x1 - 1, 3):
            if mask.getpixel((x, y)) and rng.random() < .22:
                col = colors[0] if rng.random() < .6 else colors[2]
                for px, py in [(x, y), (x + 1, y), (x, y + 1)]:
                    if mask.getpixel((px, py)):
                        im.putpixel((px, py), Image.new('RGBA', (1, 1), col).getpixel((0, 0)))


def bolt(d, x, y):
    d.rectangle((x, y, x + 2, y + 2), fill=EDGE)
    d.line((x, y, x + 1, y), fill=LIT)
    d.point((x + 1, y + 1), fill=IRON)


def lens(d, x, y, r=6, purple=False):
    dark, mid, bright = (DARKV, VIOLET, LILAC) if purple else ('#314b5b', BLUE, CYAN)
    d.ellipse((x-r-2, y-r-2, x+r+2, y+r+2), fill=EDGE)
    d.ellipse((x-r-1, y-r-1, x+r+1, y+r+1), fill=IRON)
    d.ellipse((x-r, y-r, x+r, y+r), fill=dark)
    d.arc((x-r, y-r, x+r, y+r), 145, 300, fill=bright, width=2)
    d.ellipse((x-r+2, y-r+2, x+r-2, y+r-2), fill=mid)
    d.rectangle((x-r+3, y-r+2, x-r+5, y-r+4), fill=PALE)
    d.line((x+1, y+2, x+3, y+2), fill=dark)


def spatial_probe():
    im, d = canvas()
    d.line((30, 6, 30, 49), fill=EDGE, width=5)
    d.line((29, 6, 29, 45), fill=STEEL, width=2)
    d.rectangle((28, 3, 31, 7), fill=IRON)
    d.point((28, 3), fill=WHITE)
    d.polygon([(8,13),(12,10),(15,16),(22,21),(31,23),(41,20),(48,14),(51,17),(48,25),(39,30),(22,30),(13,24)], fill=EDGE)
    surface(im, [(11,14),(15,18),(23,23),(32,25),(41,22),(48,17),(46,24),(38,28),(22,28),(15,23)], [IRON,STEEL,LIT], 7)
    d.line([(11,13),(16,19),(23,22),(32,24),(41,21),(49,15)], fill=WHITE, width=1)
    d.line([(18,17),(24,20),(32,21),(39,19)], fill=IRON)
    d.line((30,14,30,23), fill=EDGE, width=3)
    d.line((29,14,29,22), fill=GOLD)
    d.rectangle((26,11,33,15), fill=SHADOW)
    d.rectangle((27,11,32,12), fill=STEEL)
    d.polygon([(23,32),(36,32),(40,36),(39,48),(33,52),(22,48),(19,39)], fill=EDGE)
    surface(im, [(24,33),(35,33),(38,37),(37,45),(32,49),(23,46),(21,39)], [IRON,STEEL,LIT], 9)
    d.polygon([(23,36),(29,34),(34,36),(33,43),(26,45),(23,42)], fill=BRASS)
    lens(d, 28,39,4)
    for x,y in [(23,33),(35,35),(23,45)]: bolt(d,x,y)
    d.line([(21,40),(14,40),(11,45),(7,45)], fill=EDGE, width=3)
    d.line([(21,39),(14,39),(11,44),(7,44)], fill=COPPER)
    d.polygon([(26,50),(34,50),(33,55),(30,60),(27,55)], fill=SHADOW)
    d.line((28,51,30,57), fill=STEEL)
    d.line((42,34,48,31), fill=EDGE, width=2)
    d.rectangle((47,27,50,34), fill=GOLD)
    d.line((48,28,48,32), fill=WHITE)
    return im


def drone(worn=False):
    im,d=canvas()
    for points, col in [([(7,17),(19,21),(20,32),(9,31),(4,26)],SHADOW), ([(46,17),(57,18),(60,25),(55,32),(44,31)],IRON)]:
        d.polygon(points,fill=EDGE)
        d.polygon([(x,y-1) for x,y in points[1:-1]],fill=col)
    for x in (7,47):
        d.rectangle((x,18,x+9,21),fill=STEEL)
        d.rectangle((x+1,22,x+8,26),fill=SHADOW)
        for a in range(x+2,x+8,3): d.line((a,23,a,26),fill=IRON)
        d.line((x+2,29,x+7,29),fill=BLUE)
        d.rectangle((x+1,15,x+8,17),fill=EDGE)
        d.line((x,14,x+10,14),fill=STEEL,width=2)
    d.polygon([(21,13),(36,11),(45,18),(45,34),(35,43),(20,39),(16,27)],fill=EDGE)
    surface(im,[(21,15),(35,13),(42,19),(40,31),(30,35),(19,30),(18,25)],[IRON,STEEL,LIT],13)
    d.polygon([(19,31),(30,36),(40,32),(42,33),(34,41),(22,37)],fill=SHADOW)
    d.line([(20,16),(28,14),(35,14),(41,19)],fill=WHITE)
    d.polygon([(24,17),(33,16),(38,20),(36,24),(25,25),(21,22)],fill=BRASS)
    d.line([(25,18),(33,17),(36,20)],fill=GOLD)
    lens(d,29,28,5)
    d.rectangle((36,25,40,29),fill=EDGE)
    d.line((37,26,39,26),fill=GOLD)
    for x,y in [(20,23),(38,19),(23,35)]: bolt(d,x,y)
    for p in [[(23,39),(19,45),(20,50),(15,55),(11,53)],[(35,41),(40,45),(39,50),(45,54),(49,50)]]:
        d.line(p,fill=EDGE,width=5)
        d.line([(x-1,y-1) for x,y in p],fill=IRON,width=2)
    d.rectangle((18,44,22,47),fill=COPPER)
    d.rectangle((37,44,41,47),fill=COPPER)
    d.line([(12,53),(13,57),(17,57)],fill=STEEL,width=2)
    d.line([(48,51),(50,55),(47,58)],fill=STEEL,width=2)
    if worn:
        d.rectangle((45,9,63,24),fill=(0,0,0,0))
        d.line([(45,25),(50,22),(54,23)],fill=COPPER,width=2)
        d.line([(47,25),(50,28),(54,26)],fill=GOLD)
        d.polygon([(31,14),(34,16),(32,21),(35,25),(32,28),(34,33),(31,31),(30,25),(28,22)],fill=SHADOW)
        d.line([(31,16),(31,20),(33,23)],fill=EDGE)
        d.rectangle((28,25,31,29),fill='#925347')
        d.point((28,25),fill='#d9956d')
        d.rectangle((44,51,52,60),fill=(0,0,0,0))
        d.line((42,52,45,55),fill=COPPER)
        for p in [(21,18),(35,35),(25,36),(10,21)]: d.line((*p,p[0]+2,p[1]+1),fill='#8b7257')
    return im


def worn_probe():
    im,d=canvas()
    d.polygon([(8,48),(13,53),(49,18),(44,13)],fill=EDGE)
    d.polygon([(10,47),(13,49),(46,17),(44,16)],fill=IRON)
    d.line((11,47,44,14),fill=STEEL)
    d.polygon([(6,12),(10,8),(28,25),(22,32),(12,24)],fill=EDGE)
    surface(im,[(8,13),(11,11),(25,25),(21,28),(13,23)],[SHADOW,'#666880','#9092a5'],17)
    for x,y in [(10,14),(14,18),(18,22)]:
        d.line((x,y,x+4,y-3),fill=COPPER)
        d.line((x+1,y+2,x+5,y-1),fill='#b3a08b')
    d.polygon([(34,40),(41,34),(56,47),(56,52),(51,57),(45,51),(43,47),(38,47)],fill=EDGE)
    surface(im,[(37,40),(41,37),(53,48),(50,53),(45,48),(42,45),(39,45)],[SHADOW,'#676b80',STEEL],18)
    d.line([(39,40),(44,44),(48,44),(48,48),(52,50)],fill=COPPER)
    d.polygon([(39,9),(44,6),(54,13),(56,20),(49,26),(42,22),(37,16)],fill=EDGE)
    surface(im,[(40,10),(44,9),(51,13),(53,19),(48,23),(43,20),(40,16)],[IRON,STEEL,LIT],19)
    lens(d,47,15,4,True)
    d.line([(39,25),(36,27),(37,31),(32,32)],fill=COPPER,width=2)
    d.line([(38,25),(34,25),(33,29),(30,30)],fill=GOLD)
    d.polygon([(7,48),(12,52),(10,56),(5,59),(4,54)],fill=SHADOW)
    d.line((7,50,9,53),fill=STEEL)
    d.line([(17,22),(19,23),(18,27),(22,29)],fill=EDGE)
    return im


def scrap():
    im,d=canvas()
    d.ellipse((6,8,35,27),fill=EDGE)
    d.ellipse((8,9,33,24),fill=STEEL)
    d.ellipse((12,12,30,21),fill=(0,0,0,0))
    d.polygon([(24,8),(37,8),(37,24),(29,24),(32,18),(27,15)],fill=(0,0,0,0))
    d.line([(9,18),(14,23),(22,24)],fill=IRON,width=2)
    d.polygon([(28,23),(40,20),(53,30),(50,41),(34,45),(22,36)],fill=EDGE)
    surface(im,[(29,25),(39,23),(49,31),(45,36),(33,38),(25,33)],[IRON,STEEL,LIT],22)
    d.polygon([(34,29),(41,27),(45,32),(42,37),(34,35)],fill=BRASS)
    d.rectangle((36,29,39,33),fill=SHADOW)
    d.line([(10,32),(7,39),(14,45),(23,44),(28,48),(35,48)],fill=BRASS,width=3)
    d.line([(10,32),(8,39),(14,43),(23,43),(28,46),(35,46)],fill=COPPER)
    d.line([(16,35),(13,39),(16,41),(22,39),(26,42)],fill=GOLD)
    d.polygon([(5,49),(16,47),(23,54),(18,59),(7,57)],fill=EDGE)
    d.polygon([(7,50),(15,49),(20,54),(17,56),(9,55)],fill=IRON)
    d.line((8,50,15,50),fill=LIT)
    d.polygon([(43,48),(53,45),(59,49),(55,56),(45,57)],fill=SHADOW)
    d.line([(44,49),(52,47),(56,49)],fill=STEEL)
    d.rectangle((30,53,38,56),fill='#486b5d')
    for x in (30,33,36): d.line((x,57,x,59),fill=GOLD)
    bolt(d,48,33)
    return im


def vessel():
    im,d=canvas()
    d.polygon([(19,5),(43,5),(49,11),(48,49),(43,56),(18,56),(13,49),(13,12)],fill=EDGE)
    d.polygon([(20,10),(43,10),(45,16),(44,46),(40,50),(22,50),(17,45),(17,16)],fill='#374b50')
    d.polygon([(21,12),(41,12),(43,17),(42,44),(38,47),(23,47),(20,44),(20,17)],fill='#5d7b7b')
    d.polygon([(22,14),(26,13),(24,43),(21,41)],fill='#9ebbb1')
    d.line([(23,14),(28,13),(37,13)],fill=PALE)
    d.line((40,18,40,42),fill='#7f9c94')
    d.ellipse((23,32,40,43),outline='#456364',width=2)
    d.line((31,21,31,36),fill='#465c61')
    for y in [16,24,32,40]: d.line((35,y,38,y),fill='#a3b7ac')
    for x in [13,44]:
        d.rectangle((x,14,x+4,47),fill=SHADOW)
        d.line((x,14,x,46),fill=LIT)
        d.line((x+2,15,x+2,46),fill=STEEL)
        d.rectangle((x-1,26,x+5,30),fill=BRASS)
        d.line((x,26,x+4,26),fill=GOLD)
    surface(im,[(18,5),(42,5),(47,10),(44,14),(18,14),(14,11)],[IRON,STEEL,LIT],25)
    d.line([(19,6),(41,6),(44,9)],fill=WHITE)
    surface(im,[(17,47),(44,47),(48,51),(43,57),(18,57),(13,52)],[SHADOW,IRON,STEEL],26)
    d.line((19,49,42,49),fill=LIT)
    d.rectangle((25,51,37,54),fill=BRASS)
    d.line((27,52,35,52),fill=GOLD)
    bolt(d,18,8);bolt(d,40,8)
    return im


def orb(im,box,unstable=False):
    d=ImageDraw.Draw(im)
    x0,y0,x1,y1=box
    d.ellipse(box,fill=DARKV if unstable else '#2d4c5e')
    d.ellipse((x0+2,y0+2,x1-3,y1-3),fill=VIOLET if unstable else BLUE)
    if unstable:
        pts=[(21,18),(28,15),(34,17),(37,22),(31,26),(32,31),(26,34),(24,29),(18,27)]
        d.polygon(pts,fill='#9c779e')
        d.polygon([(35,27),(43,23),(46,28),(44,37),(38,41),(33,37)],fill='#5e526f')
        d.line([(27,14),(30,20),(27,25),(32,30),(29,36),(33,43)],fill='#d4b6d4',width=2)
        d.line([(29,17),(33,21),(31,26)],fill='#f1d9df')
    else:
        d.polygon([(21,19),(27,16),(33,18),(35,21),(31,24),(32,27),(27,29),(25,26),(20,26)],fill='#6f9e8f')
        d.polygon([(37,29),(43,27),(45,31),(43,37),(37,40),(34,35)],fill='#6b9180')
        d.polygon([(20,32),(25,31),(27,34),(24,37),(22,36)],fill='#84ac96')
        d.arc((x0+3,y0+4,x1-3,y1-4),165,295,fill=CYAN)
    d.line([(x0+7,y0+5),(x0+11,y0+3),(x0+16,y0+3)],fill=PALE)
    d.rectangle((x0+6,y0+7,x0+8,y0+10),fill='#bdd1c1')


def stable():
    im,d=canvas()
    d.ellipse((8,8,55,50),fill=EDGE)
    d.ellipse((11,10,52,47),fill=IRON)
    d.ellipse((14,13,49,44),fill=(0,0,0,0))
    d.arc((10,9,53,48),170,310,fill=LIT,width=2)
    orb(im,(16,13,47,44))
    d.arc((9,20,54,42),5,175,fill=EDGE,width=5)
    d.arc((9,18,54,40),5,175,fill=COPPER,width=3)
    d.arc((9,18,54,40),12,155,fill=GOLD)
    for x,y in [(9,27),(49,27),(28,7)]:
        d.rectangle((x,y,x+5,y+6),fill=BRASS)
        d.rectangle((x+1,y,x+4,y+2),fill=GOLD)
        d.point((x+2,y+1),fill=WHITE)
    d.polygon([(24,46),(39,46),(43,52),(43,56),(19,56),(19,52)],fill=EDGE)
    surface(im,[(25,47),(37,47),(40,52),(38,54),(23,54),(22,52)],[SHADOW,IRON,STEEL],30)
    d.rectangle((28,49,34,52),fill='#50685c')
    d.line((29,49,33,49),fill='#a5c79c')
    return im


def unstable():
    im,d=canvas()
    orb(im,(15,13,48,45),True)
    d.polygon([(33,12),(38,11),(40,15),(36,19),(34,17)],fill=(0,0,0,0))
    d.polygon([(14,26),(20,28),(19,34),(15,32)],fill=(0,0,0,0))
    d.polygon([(14,8),(19,6),(22,10),(19,14),(15,12)],fill=LILAC)
    d.line((15,8,18,7),fill='#e4c8df')
    d.polygon([(47,16),(51,14),(54,18),(52,22),(48,21)],fill=VIOLET)
    d.polygon([(46,42),(50,42),(52,47),(48,49)],fill=LILAC)
    d.point((10,22),fill=GOLD);d.rectangle((52,31,54,33),fill=GOLD)
    for points in [[(9,18),(13,18),(16,41),(24,47),(24,51),(15,47),(11,40)],[(50,25),(55,26),(52,45),(43,52),(39,51),(43,45)]]:
        d.polygon(points,fill=EDGE)
        d.line(points[:-2],fill=IRON,width=2)
    d.line([(11,20),(14,39),(20,45)],fill=GOLD)
    d.line([(52,29),(50,42),(45,47)],fill=COPPER)
    d.polygon([(22,48),(39,48),(43,54),(40,58),(22,58),(18,54)],fill=EDGE)
    d.polygon([(23,49),(37,49),(40,53),(37,55),(23,55),(21,53)],fill=IRON)
    d.rectangle((27,51,34,53),fill='#a27146')
    d.line((28,51,33,51),fill='#e0b564')
    return im


def carrier():
    im,d=canvas()
    d.polygon([(15,11),(45,8),(53,17),(50,48),(41,56),(12,52),(8,43),(10,18)],fill=EDGE)
    surface(im,[(15,13),(44,11),(49,17),(46,45),(40,51),(14,48),(11,42),(13,20)],[SHADOW,IRON,STEEL],32)
    d.polygon([(45,13),(49,18),(46,45),(41,50),(42,41)],fill=SHADOW)
    d.polygon([(18,17),(38,15),(43,20),(40,38),(18,41),(14,35)],fill='#494d55')
    d.polygon([(20,19),(36,17),(40,21),(37,35),(20,38),(17,33)],fill='#69788a')
    d.line([(20,20),(26,19),(27,23),(23,26),(24,31),(20,34)],fill=CYAN)
    d.line([(30,19),(35,19),(37,22),(34,27),(36,30)],fill=STEEL)
    d.line([(23,31),(28,34),(33,33),(35,30)],fill='#9ead97')
    d.polygon([(27,25),(31,23),(34,26),(32,30),(28,30),(26,28)],fill=GOLD)
    d.line((28,25,30,25),fill=WHITE)
    for x,y in [(14,18),(39,13),(13,43),(40,43)]:bolt(d,x,y)
    d.rectangle((20,44,34,47),fill=EDGE)
    for x in range(21,34,3):d.line((x,44,x,46),fill=COPPER)
    d.line([(16,12),(34,10),(43,10)],fill=LIT)
    return im


def seed():
    im,d=canvas()
    d.polygon([(30,7),(38,17),(43,31),(37,46),(29,54),(21,42),(19,27),(24,16)],fill=DARKV)
    d.polygon([(30,9),(34,21),(31,34),(23,42),(21,28),(25,17)],fill='#a58cb0')
    d.polygon([(30,9),(37,18),(40,30),(32,34),(34,21)],fill='#c4b3cc')
    d.polygon([(32,35),(40,31),(35,45),(29,51),(25,42)],fill='#795f90')
    d.line([(29,12),(26,22),(26,30)],fill='#ded0d9')
    d.line([(31,17),(32,24),(29,30)],fill='#f0e3df')
    d.polygon([(28,30),(32,27),(35,32),(31,37),(27,35)],fill='#dcc1d8')
    d.arc((9,22,54,43),176,350,fill=BRASS,width=4)
    d.arc((9,21,54,42),176,350,fill=GOLD,width=2)
    d.arc((9,21,54,42),0,170,fill=BRASS,width=4)
    d.arc((9,20,54,41),0,170,fill=COPPER,width=2)
    for x,y in [(9,29),(48,30),(22,43)]:
        d.rectangle((x,y,x+5,y+4),fill=BRASS)
        d.line((x+1,y,x+4,y),fill=GOLD)
    d.rectangle((48,30,51,32),fill=PALE)
    d.line((13,17,16,17),fill=GOLD);d.point((14,16),fill=WHITE)
    return im


def charge():
    im,d=canvas()
    d.polygon([(19,8),(41,8),(47,15),(45,48),(38,56),(19,53),(13,45),(14,16)],fill=EDGE)
    surface(im,[(20,10),(39,10),(43,16),(41,45),(36,51),(20,49),(17,44),(18,17)],[SHADOW,IRON,STEEL],38)
    d.rectangle((22,14,37,43),fill=BRASS)
    d.rectangle((24,15,35,41),fill='#5d4549')
    d.rectangle((26,16,33,39),fill='#8d627e')
    for y in (20,28,36):
        d.rectangle((23,y,36,y+3),fill=SHADOW)
        d.line((24,y,35,y),fill=LIT)
    d.line((27,17,27,19),fill='#d5b4cd')
    d.rectangle((20,45,37,48),fill=EDGE)
    for x in [21,26,31]:
        d.polygon([(x,45),(x+2,45),(x+4,48),(x+2,48)],fill=GOLD)
    d.polygon([(9,17),(15,14),(19,19),(19,35),(14,39),(8,35),(11,32),(14,33),(15,23),(11,23)],fill=SHADOW)
    d.line([(10,18),(14,17),(17,20),(17,34),(14,36)],fill=STEEL)
    d.polygon([(44,15),(51,17),(54,22),(52,38),(47,43),(43,40),(47,34),(48,24),(44,23)],fill=EDGE)
    d.line([(46,17),(50,19),(51,23),(49,36),(46,39)],fill=IRON,width=2)
    bolt(d,19,11);bolt(d,37,12);bolt(d,19,49)
    return im


def remnant():
    im,d=canvas()
    d.polygon([(16,18),(19,10),(24,8),(28,11),(25,17),(23,28),(24,41),(19,47),(12,44),(9,34),(11,23)],fill=EDGE)
    surface(im,[(18,19),(20,12),(24,11),(22,18),(20,28),(21,40),(17,43),(13,34),(14,24)],[IRON,STEEL,LIT],42)
    d.polygon([(26,13),(32,16),(36,24),(35,33),(29,37),(26,32),(28,25),(25,21)],fill='#5f8384')
    d.line([(27,15),(30,17),(33,24),(32,29)],fill=PALE)
    d.polygon([(18,44),(39,42),(47,46),(45,52),(37,57),(17,55),(11,50)],fill=EDGE)
    surface(im,[(19,46),(37,44),(43,47),(41,51),(35,54),(18,52),(14,49)],[SHADOW,IRON,STEEL],43)
    d.line((20,46,36,45),fill=LIT)
    d.line([(36,44),(39,36),(43,33),(47,36)],fill=COPPER,width=2)
    d.line([(39,46),(43,40),(47,42)],fill=GOLD)
    d.polygon([(45,18),(51,16),(55,21),(51,29),(46,25)],fill='#66898a')
    d.line((46,19,50,18),fill=PALE)
    d.polygon([(48,49),(55,47),(59,53),(52,56)],fill=SHADOW)
    d.line((49,49,54,49),fill=STEEL)
    bolt(d,21,48)
    return im


def shell():
    im,d=canvas()
    d.polygon([(18,12),(29,7),(46,13),(53,27),(49,44),(37,54),(19,52),(10,40),(9,24)],fill=EDGE)
    surface(im,[(19,15),(29,10),(43,15),(49,27),(45,42),(35,50),(20,48),(14,39),(13,26)],[IRON,STEEL,LIT],44)
    d.polygon([(22,20),(30,16),(40,20),(44,29),(40,39),(32,43),(23,39),(18,31)],fill=EDGE)
    d.polygon([(24,22),(30,19),(37,22),(40,29),(37,36),(31,39),(25,36),(22,30)],fill='#727e7b')
    d.polygon([(25,25),(31,22),(36,25),(37,31),(33,35),(27,33)],fill=(0,0,0,0))
    d.line([(19,15),(27,12),(33,12)],fill=WHITE)
    d.line([(43,15),(45,24),(49,28),(44,32),(45,39),(40,40),(37,48)],fill=SHADOW,width=2)
    d.line([(44,24),(41,28),(44,32)],fill=EDGE)
    d.polygon([(14,37),(20,40),(22,46),(18,46)],fill=COPPER)
    d.line((16,38,20,43),fill=GOLD)
    bolt(d,18,20);bolt(d,30,46);bolt(d,39,16)
    d.polygon([(46,45),(51,45),(54,49),(50,52),(46,49)],fill='#925447')
    return im


def specimen(failed=False):
    im,d=canvas()
    d.polygon([(9,39),(39,30),(55,39),(51,48),(22,58),(7,49)],fill=EDGE)
    surface(im,[(10,40),(38,33),(51,40),(48,46),(22,54),(10,47)],[SHADOW,IRON,STEEL],48)
    d.line([(11,40),(23,48),(50,40)],fill=LIT)
    d.line((24,50,47,43),fill=SHADOW,width=2)
    d.polygon([(20,28),(35,22),(44,28),(44,39),(30,45),(19,39)],fill=EDGE)
    d.polygon([(22,29),(34,25),(41,29),(30,34)],fill=GOLD)
    d.polygon([(21,31),(29,36),(29,42),(21,38)],fill=BRASS)
    d.polygon([(31,36),(41,31),(41,38),(31,42)],fill=COPPER)
    d.rectangle((27,22,34,30),fill=IRON)
    d.line((27,22,33,22),fill=LIT)
    d.polygon([(29,14),(35,13),(39,17),(37,23),(31,24),(27,20)],fill=EDGE)
    d.polygon([(30,15),(34,15),(36,18),(34,21),(30,20)],fill=VIOLET)
    d.line((30,16,32,15),fill=LILAC)
    d.line([(12,35),(12,15),(16,11),(21,11)],fill=EDGE,width=4)
    d.line([(12,34),(12,16),(16,13),(21,13)],fill=STEEL,width=2)
    d.line((17,13,40,13),fill=IRON,width=2)
    d.rectangle((19,10,23,16),fill=SHADOW)
    d.line((19,10,22,10),fill=LIT)
    d.line((40,14,40,23),fill=IRON,width=2)
    d.line((39,23,43,23),fill=STEEL)
    for x,y in [(13,44),(23,50),(45,43)]:bolt(d,x,y)
    if failed:
        d.rectangle((33,10,44,23),fill=(0,0,0,0))
        d.line([(34,14),(37,17),(40,16)],fill=COPPER,width=2)
        d.polygon([(31,23),(35,27),(33,31),(37,35),(34,40),(30,44),(27,40),(29,35),(26,30)],fill=EDGE)
        d.line([(32,25),(31,30),(34,34),(31,40)],fill='#8c5260')
        d.line([(23,28),(25,32),(23,35)],fill='#92856a')
        d.polygon([(45,25),(51,28),(53,34),(49,35),(44,32)],fill=IRON)
        d.line((46,26,50,29),fill=LIT)
        d.line([(18,46),(22,43),(25,44)],fill='#a55545',width=2)
    return im


def archive():
    im,d=canvas()
    d.polygon([(11,6),(42,6),(55,19),(55,54),(49,58),(10,57),(6,50),(7,16)],fill='#514b40')
    surface(im,[(12,8),(41,8),(52,20),(52,52),(48,54),(12,54),(9,49),(10,17)],['#b6a16c','#c7b783','#dfd09f'],52)
    d.polygon([(41,8),(41,21),(53,21)],fill='#8c7f58')
    d.polygon([(42,9),(42,19),(51,19)],fill='#efe0b0')
    d.line((13,10,36,10),fill='#e4d7aa')
    d.line((12,16,18,16),fill='#716e57',width=2)
    d.line((12,20,21,20),fill='#8b815d')
    d.line((13,23,19,23),fill='#8b815d')
    d.polygon([(33,16),(36,24),(42,29),(45,40),(40,39),(38,46),(28,46),(25,39),(20,41),(23,29),(29,24)],fill='#617f83')
    d.polygon([(33,19),(34,28),(38,31),(40,37),(36,36),(35,43),(31,43),(30,36),(26,38),(28,31),(32,28)],fill='#c0bb8f')
    d.line((33,21,33,46),fill='#3f6877')
    d.line((28,34,38,34),fill='#3f6877')
    d.line((26,40,40,40),fill='#3f6877')
    d.line((18,28,18,45),fill='#8b815d')
    for y in (29,35,42):d.line((17,y,20,y),fill='#8b815d')
    d.line((22,49,43,49),fill='#8b815d')
    for x in (23,33,42):d.line((x,48,x,50),fill='#8b815d')
    d.polygon([(9,33),(12,34),(11,48),(8,48)],fill='#9d8b61')
    d.rectangle((44,46,49,51),fill='#857459')
    d.line((45,47,48,50),fill='#c7b783')
    return im


def erosion():
    im,d=canvas()
    for y in range(17,47,6):
        d.rectangle((7,y,15,y+2),fill=BRASS)
        d.line((7,y,13,y),fill=GOLD)
        d.rectangle((47,y,55,y+2),fill=BRASS)
        d.line((48,y,54,y),fill=GOLD)
    d.polygon([(17,9),(43,9),(50,16),(50,45),(42,54),(17,54),(11,47),(11,17)],fill=EDGE)
    surface(im,[(18,11),(42,11),(47,17),(47,44),(40,51),(18,51),(14,45),(14,18)],['#4c6052','#657966','#819582'],59)
    for p in [[(18,16),(25,16),(25,22)],[(39,15),(41,15),(41,24),(38,24)],[(18,44),(24,44),(24,40)],[(34,46),(41,46),(41,40)]]:
        d.line(p,fill='#b7aa74',width=2)
    for x,y in [(17,16),(39,16),(17,45),(39,46)]:bolt(d,x,y)
    d.rectangle((22,22,41,41),fill=BRASS)
    d.rectangle((24,23,40,39),fill=EDGE)
    d.polygon([(26,25),(35,25),(39,29),(38,36),(33,38),(26,35)],fill=DARKV)
    d.polygon([(27,26),(33,26),(36,29),(34,32),(28,31)],fill=VIOLET)
    d.line([(27,26),(31,26),(33,28)],fill=LILAC)
    d.line([(35,33),(39,36),(38,42),(43,45),(41,49)],fill='#6e4a78',width=2)
    d.line([(26,33),(20,35),(20,40),(17,42)],fill='#78537e',width=2)
    d.line([(35,24),(37,19),(41,19),(43,16)],fill='#634c70',width=2)
    for x in range(25,39,4):
        d.line((x,20,x,22),fill=GOLD)
        d.line((x,40,x,43),fill=COPPER)
    d.rectangle((17,48,20,49),fill=GOLD)
    return im


def draw(ident):
    return {
        'spatial_probe': spatial_probe, 'industrial_work_drone': drone,
        'worn_resource_probe': worn_probe, 'worn_work_drone': lambda: drone(True),
        'drone_disassembly_scrap': scrap, 'empty_bubble_containment_vessel': vessel,
        'unstable_simulated_world_bubble': unstable, 'stable_simulated_world_bubble': stable,
        'world_model_carrier': carrier, 'world_matter_seed': seed,
        'bubble_termination_charge': charge, 'bubble_container_remnant': remnant,
        'failed_containment_shell': shell, 'reverse_engineering_specimen': specimen,
        'failed_engineering_specimen': lambda: specimen(True), 'ship_engineering_archive': archive,
        'erosion_research_module': erosion,
    }[ident]()


if __name__ == '__main__':
    root=Path(__file__).resolve().parents[2]
    out=root/'src/main/resources/assets/hk3gtl/textures/item'
    preview=Image.new('RGB',(5*220,4*248),'#777777')
    pd=ImageDraw.Draw(preview)
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',12)
    for i,ident in enumerate(IDS):
        im=draw(ident)
        im.save(out/f'{ident}.png')
        x,y=(i%5)*220,(i//5)*248
        preview.paste(im.resize((192,192),Image.Resampling.NEAREST),(x+14,y+8),im.resize((192,192),Image.Resampling.NEAREST))
        label=ident.replace('_',' ')
        if len(label)>29:
            cut=label.rfind(' ',0,29)
            label=label[:cut]+'\n'+label[cut+1:]
        pd.text((x+8,y+207),label,font=font,fill='white')
    path=root/'logs/textures-redraw-0002-v2-20261114/world-sheet.png'
    path.parent.mkdir(parents=True,exist_ok=True)
    preview.save(path)
    print(path)
