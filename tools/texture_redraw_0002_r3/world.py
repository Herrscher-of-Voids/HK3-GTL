# -*- coding: utf-8 -*-
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .common import Pixel, STEEL, WHITE, GOLD, COPPER, VIOLET, BLUE, BLACK


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'deliveries/0002贴图材质_工艺重构_R3_20261114'
SRC = ROOT / 'src/main/resources/assets/hk3gtl/textures/item'
PROCESS = 'src/main/resources/data/hk3gtl/research/industrial_processes.json'
WONDER = 'src/main/resources/data/hk3gtl/research/wonder_processes.json'
RUST = ['#362723', '#6b4030', '#a36b45', '#d59a67', '#efd1a0']
RED = ['#391e2c', '#6c2d40', '#a74f58', '#e38b81', '#ffceac']
GLASS = ['#202c46', '#3d566d', '#658b9a', '#a6c8cc', '#e4efdf']


def line(p, points, color, width=1):
    p.d.line(points, fill=color, width=width)


def poly(p, points, color, outline=None):
    p.d.polygon(points, fill=color, outline=outline)


def ellipse(p, area, pal, shade=2):
    p.d.ellipse(area, fill=pal[shade], outline=pal[0])


def disc(p, cx, cy, rx, ry, pal=STEEL):
    ellipse(p, (cx-rx, cy-ry, cx+rx, cy+ry), pal, 2)
    p.d.arc((cx-rx+1, cy-ry+1, cx+rx-1, cy+ry-1), 185, 335, fill=pal[4])
    p.d.arc((cx-rx+1, cy-ry+1, cx+rx-1, cy+ry-1), 5, 150, fill=pal[1])


def bevel(p, points, pal=STEEL, shade=2):
    poly(p, points, pal[shade], pal[0])
    line(p, points[:3], pal[min(4, shade+1)])


def iso_block(p, x, y, w, h, depth, pal=STEEL):
    poly(p, [(x,y),(x+w,y-5),(x+w+depth,y),(x+depth,y+5)], pal[3], pal[0])
    poly(p, [(x,y),(x+depth,y+5),(x+depth,y+h+5),(x,y+h)], pal[2], pal[0])
    poly(p, [(x+depth,y+5),(x+w+depth,y),(x+w+depth,y+h),(x+depth,y+h+5)], pal[1], pal[0])
    line(p, [(x+1,y),(x+depth,y+4),(x+w+depth-1,y)], pal[4])


def scratch(p, x, y):
    line(p, [(x,y),(x+3,y-1),(x+5,y-1)], RUST[0], 2)
    line(p, [(x+1,y+2),(x+4,y)], RUST[3])


def lens(p, area, pal=VIOLET):
    ellipse(p, area, BLACK, 0)
    x,y,r,b=area
    ellipse(p, (x+2,y+2,r-2,b-2), pal, 1)
    p.d.arc((x+2,y+2,r-2,b-2), 150, 285, fill=pal[3], width=2)
    p.d.rectangle((x+3,y+3,x+5,y+4),fill=pal[4])
    p.d.point((r-3,b-3),fill=pal[2])


def spatial_probe():
    p=Pixel()
    bevel(p, [(12,44),(16,41),(23,48),(19,53),(12,56),(8,52)], BLACK)
    bevel(p, [(15,39),(35,19),(43,27),(23,48)], WHITE)
    poly(p, [(23,45),(41,27),(43,28),(25,48)], STEEL[1], STEEL[0])
    line(p, [(18,39),(36,21)], WHITE[4],2)
    for k in range(4):
        line(p, [(19+k*4,41-k*4),(23+k*4,45-k*4)], GOLD[1],3)
        line(p, [(19+k*4,40-k*4),(23+k*4,44-k*4)], GOLD[3])
    bevel(p, [(28,24),(27,12),(32,7),(37,19)], STEEL)
    bevel(p, [(42,31),(55,32),(59,27),(47,23)], STEEL)
    line(p, [(30,14),(33,11),(35,18)], GOLD[3],2)
    line(p, [(48,26),(55,28)], GOLD[3],2)
    bevel(p, [(32,18),(40,10),(50,13),(55,22),(47,30),(40,27)], GOLD)
    bevel(p, [(35,17),(41,12),(48,15),(52,22),(46,27),(40,24)], WHITE)
    poly(p, [(39,17),(43,14),(48,17),(49,21),(45,25),(41,22)], VIOLET[0])
    poly(p, [(40,17),(43,16),(47,18),(47,21),(44,23),(41,21)], VIOLET[2])
    line(p, [(40,17),(43,16),(46,18)], VIOLET[4],2)
    line(p, [(49,12),(55,6),(57,6)], BLACK[0],3)
    line(p, [(49,11),(55,5),(57,5)], STEEL[3])
    p.bolt(13,47)
    return p.im


def work_drone(worn=False):
    p=Pixel()
    for x in (10,44):
        p.box((x,17,x+10,38), BLACK)
        disc(p,x+5,19,7,5,STEEL)
        ellipse(p,(x+1,17,x+9,21),BLACK,0)
        line(p,[(x+3,18),(x+7,20)],STEEL[2])
        p.box((x+2,29,x+8,35),GOLD,1)
        line(p,[(x+3,31),(x+7,31)],GOLD[3])
    p.box((17,25,46,33),STEEL,1)
    bevel(p,[(20,18),(33,12),(47,19),(43,37),(29,42),(18,34)],WHITE)
    poly(p,[(20,18),(33,12),(47,19),(33,25)],WHITE[3],STEEL[0])
    poly(p,[(33,25),(47,19),(43,37),(29,42)],STEEL[1],STEEL[0])
    line(p,[(21,19),(33,14),(43,19)],WHITE[4])
    bevel(p,[(25,18),(33,15),(39,18),(32,21)],GOLD)
    p.box((22,26,30,33),BLACK,0)
    p.box((24,28,28,31),VIOLET,2 if not worn else 1)
    line(p,[(35,28),(42,25)],STEEL[3])
    line(p,[(35,31),(42,28)],STEEL[2])
    line(p,[(35,34),(41,31)],STEEL[2])
    for pts in ([23,36,19,43,20,49],[38,38,43,43,43,49]):
        line(p,pts,BLACK[0],5)
        line(p,pts,STEEL[2],3)
    for x in (18,41):
        p.box((x,46,x+5,51),GOLD)
    line(p,[(18,50),(15,54),(15,57),(20,57)],BLACK[0],3)
    line(p,[(23,50),(26,54),(26,57),(22,57)],BLACK[0],3)
    line(p,[(41,50),(38,54),(38,57),(42,57)],BLACK[0],3)
    line(p,[(46,50),(49,54),(49,57),(45,57)],BLACK[0],3)
    line(p,[(17,51),(15,54),(15,56),(19,56)],STEEL[3])
    line(p,[(23,51),(25,54),(25,56),(22,56)],STEEL[3])
    line(p,[(40,51),(38,54),(38,56),(41,56)],STEEL[3])
    line(p,[(46,51),(48,54),(48,56),(45,56)],STEEL[3])
    p.bolt(20,23)
    p.bolt(39,19)
    if worn:
        poly(p,[(42,20),(47,19),(46,27),(43,30),(42,26)],BLACK[0])
        line(p,[(44,23),(45,21)],RUST[3])
        scratch(p,25,23)
        scratch(p,35,36)
        p.d.rectangle((46,53,51,59),fill=(0,0,0,0))
        line(p,[(47,49),(50,51),(48,54)],COPPER[2],2)
        p.box((9,27,15,32),RUST,1)
        line(p,[(10,27),(13,30)],RUST[3])
        line(p,[(28,16),(31,18),(30,22),(33,24)],BLACK[1])
    return p.im


def resource_probe():
    p=Pixel()
    line(p,[(29,13),(27,5),(24,3)],BLACK[0],3)
    line(p,[(29,12),(27,5),(24,3)],STEEL[3])
    line(p,[(27,6),(34,5),(38,8)],BLACK[0],2)
    p.box((25,11,34,17),GOLD,1)
    bevel(p,[(18,18),(32,12),(44,18),(43,38),(29,46),(16,37)],STEEL)
    poly(p,[(18,18),(32,12),(44,18),(30,25)],WHITE[2],STEEL[0])
    poly(p,[(30,25),(44,18),(43,38),(29,46)],BLACK[2],STEEL[0])
    lens(p,(18,24,29,35),BLUE)
    line(p,[(33,27),(40,24)],GOLD[2],2)
    line(p,[(33,31),(40,28)],GOLD[2],2)
    line(p,[(33,35),(40,32)],GOLD[1],2)
    p.box((19,38,26,43),GOLD,1)
    line(p,[(19,40),(12,47),(10,53)],BLACK[0],5)
    line(p,[(39,39),(45,46),(46,52)],BLACK[0],5)
    line(p,[(30,44),(30,53)],BLACK[0],4)
    line(p,[(19,40),(12,47),(10,53)],STEEL[2],2)
    line(p,[(39,39),(45,46),(46,52)],STEEL[2],2)
    bevel(p,[(5,52),(12,51),(14,55),(5,57)],RUST)
    bevel(p,[(42,52),(50,51),(54,54),(44,57)],STEEL)
    bevel(p,[(27,51),(33,51),(34,56),(26,57)],STEEL)
    bevel(p,[(38,12),(42,11),(47,16),(47,22),(43,23)],GOLD)
    line(p,[(44,21),(50,28),(49,31)],BLACK[0],3)
    line(p,[(44,21),(50,28),(49,31)],COPPER[2])
    scratch(p,31,19)
    scratch(p,35,39)
    line(p,[(21,19),(24,21),(23,25)],BLACK[0])
    line(p,[(19,34),(22,32),(24,34)],BLUE[0],2)
    return p.im


def drone_scrap():
    p=Pixel()
    bevel(p,[(9,43),(20,37),(31,42),(27,54),(14,57),(6,50)],BLACK)
    bevel(p,[(13,42),(19,40),(25,43),(22,49),(14,51)],STEEL)
    poly(p,[(20,37),(23,27),(35,24),(36,33),(31,35),(33,43)],WHITE[2],WHITE[0])
    line(p,[(23,29),(33,26),(34,30),(28,33)],WHITE[4],2)
    poly(p,[(28,44),(38,36),(50,39),(54,49),(43,55),(36,51)],STEEL[1],STEEL[0])
    line(p,[(38,38),(47,41),(50,48)],STEEL[3],2)
    disc(p,44,29,9,7,BLACK)
    disc(p,44,29,5,4,COPPER)
    ellipse(p,(42,27,46,31),BLACK,0)
    line(p,[(17,39),(13,31),(17,24),(23,23)],BLACK[0],4)
    line(p,[(17,39),(13,31),(17,24),(23,23)],COPPER[2],2)
    line(p,[(14,33),(19,34),(20,29)],COPPER[3])
    bevel(p,[(31,49),(36,45),(43,47),(41,52),(35,55)],GOLD)
    p.box((25,16,34,22),BLACK)
    for x in (26,29,32):
        line(p,[(x,22),(x,25)],GOLD[3])
    line(p,[(48,17),(46,21),(49,25),(54,25)],STEEL[0],4)
    line(p,[(48,17),(46,21),(49,25),(54,25)],STEEL[3],2)
    scratch(p,15,45)
    scratch(p,42,43)
    return p.im


def vessel_frame(p, broken=False, failed=False):
    disc(p,32,48,19,8,BLACK)
    disc(p,32,46,19,7,STEEL)
    disc(p,32,43,16,5,GOLD)
    poly(p,[(17,20),(23,16),(42,17),(47,22),(46,43),(41,47),(23,47),(17,42)],GLASS[1],GLASS[0])
    poly(p,[(20,22),(25,19),(27,43),(23,44)],GLASS[2])
    line(p,[(21,23),(22,35)],GLASS[4],2)
    line(p,[(42,22),(43,40)],GLASS[2])
    disc(p,32,18,19,7,BLACK)
    disc(p,32,16,19,7,STEEL)
    disc(p,32,16,14,4,BLACK)
    for x in (14,45):
        p.box((x,17,x+4,45),GOLD,2)
        line(p,[(x+2,21),(x+2,41)],GOLD[4])
        p.bolt(x+1,16)
        p.bolt(x+1,43)
    p.box((27,46,38,51),WHITE,2)
    p.box((30,47,35,49),VIOLET,1)
    if failed:
        line(p,[(19,12),(24,15),(23,20),(27,23),(25,31)],BLACK[0],2)
        line(p,[(20,12),(25,15)],STEEL[4])
        p.d.rectangle((45,26,49,35),fill=(0,0,0,0))
        line(p,[(47,25),(51,29),(48,34)],COPPER[2],2)
        p.box((27,46,38,51),RUST,1)
        line(p,[(28,47),(34,48),(35,50)],RUST[3])
        scratch(p,18,42)
    if broken:
        poly(p,[(10,4),(57,4),(57,33),(47,29),(40,33),(37,25),(30,30),(25,23),(20,30),(13,27)],(0,0,0,0))
        line(p,[(17,28),(22,27),(25,31),(28,27),(30,31)],GLASS[3])
        line(p,[(39,31),(42,34),(46,30)],GLASS[4])
        line(p,[(14,28),(18,32),(18,41)],GOLD[3],2)
        poly(p,[(46,45),(53,38),(57,47),(53,52)],GLASS[2],GLASS[0])
        line(p,[(53,40),(55,46)],GLASS[4])
        scratch(p,24,45)


def empty_vessel(failed=False):
    p=Pixel()
    vessel_frame(p,failed=failed)
    if not failed:
        line(p,[(26,30),(38,30)],GLASS[2])
        line(p,[(32,26),(32,35)],GLASS[2])
    return p.im


def simulated_world(stable):
    p=Pixel()
    vessel_frame(p)
    if stable:
        disc(p,32,34,12,6,VIOLET)
        ellipse(p,(22,24,42,42),BLUE,1)
        poly(p,[(25,28),(29,25),(35,26),(39,31),(36,35),(32,35),(30,39),(26,36)],VIOLET[2])
        poly(p,[(26,28),(30,27),(34,28),(33,31),(28,32)],WHITE[3])
        poly(p,[(33,34),(38,32),(38,36),(35,39),(32,38)],WHITE[2])
        line(p,[(24,26),(27,24),(32,24)],BLUE[4],2)
        p.d.arc((20,22,43,43), 20, 160, fill=GOLD[3],width=2)
        for x,y in ((20,31),(40,31),(30,21),(30,41)):
            p.box((x,y,x+4,y+4),GOLD,2)
        p.box((30,47,35,49),BLUE,3)
    else:
        poly(p,[(24,24),(31,21),(39,25),(40,32),(36,37),(28,39),(22,32)],VIOLET[0])
        iso_block(p,25,28,9,5,5,VIOLET)
        iso_block(p,33,34,6,3,3,BLUE)
        iso_block(p,23,39,5,3,3,STEEL)
        iso_block(p,36,24,5,3,3,WHITE)
        line(p,[(20,31),(24,29),(27,31),(31,24),(36,22),(41,26)],VIOLET[3])
        line(p,[(23,38),(30,40),(34,37),(40,39),(44,35)],VIOLET[4])
        line(p,[(29,23),(31,27),(29,32),(33,35)],VIOLET[4],2)
        p.box((30,47,35,49),RED,2)
        line(p,[(39,15),(41,18),(40,22)],BLACK[0])
    return p.im


def world_model():
    p=Pixel()
    bevel(p,[(11,18),(39,8),(53,18),(53,47),(25,57),(11,48)],WHITE)
    poly(p,[(25,28),(53,18),(53,47),(25,57)],STEEL[1],STEEL[0])
    poly(p,[(11,18),(39,8),(53,18),(25,28)],WHITE[3],STEEL[0])
    line(p,[(13,18),(39,10),(49,17)],WHITE[4])
    bevel(p,[(18,25),(38,18),(45,23),(45,42),(25,49),(18,44)],BLACK)
    poly(p,[(21,27),(37,21),(42,24),(42,39),(27,44),(21,40)],VIOLET[0])
    for y in (27,32,37):
        poly(p,[(24,y),(35,y-4),(40,y-1),(29,y+3)],VIOLET[2],VIOLET[0])
        line(p,[(25,y),(35,y-3),(38,y-1)],VIOLET[4])
        line(p,[(24,y+1),(29,y+4),(39,y)],VIOLET[1])
    for x in (15,19,23):
        line(p,[(x,47),(x+3,49),(x+3,52)],GOLD[3],2)
    p.bolt(13,22)
    p.bolt(46,20)
    p.bolt(46,43)
    p.box((29,12,37,15),GOLD,2)
    line(p,[(31,13),(35,13)],GOLD[4])
    return p.im


def matter_seed():
    p=Pixel()
    bevel(p,[(9,39),(21,27),(43,28),(55,41),(43,55),(23,56)],BLACK)
    poly(p,[(10,39),(21,34),(32,41),(23,54)],STEEL[2],STEEL[0])
    poly(p,[(32,41),(45,34),(55,41),(43,55),(23,56)],STEEL[1],STEEL[0])
    disc(p,32,39,14,8,GOLD)
    bevel(p,[(24,34),(23,21),(31,11),(40,20),(41,33),(32,43)],VIOLET)
    poly(p,[(31,11),(32,30),(24,34),(23,21)],VIOLET[3],VIOLET[0])
    poly(p,[(31,11),(40,20),(41,33),(32,30)],VIOLET[1],VIOLET[0])
    poly(p,[(24,34),(32,30),(41,33),(32,43)],VIOLET[2],VIOLET[0])
    line(p,[(26,22),(30,16),(30,27)],VIOLET[4],2)
    for pts in ([(17,32),(17,22),(21,18),(24,27),(23,36)],[(41,25),(46,20),(49,25),(46,36),(41,37)],[(27,45),(29,35),(33,31),(36,37),(34,45)]):
        bevel(p,pts,WHITE,3)
    bevel(p,[(16,38),(18,33),(25,35),(27,43),(23,46)],GOLD)
    bevel(p,[(38,42),(42,33),(49,34),(49,41),(43,47)],GOLD)
    p.bolt(17,39)
    p.bolt(43,40)
    line(p,[(27,50),(35,50),(39,47)],STEEL[3])
    return p.im


def termination_charge():
    p=Pixel()
    bevel(p,[(15,20),(35,10),(50,19),(50,45),(28,55),(15,46)],STEEL)
    poly(p,[(15,20),(35,10),(50,19),(29,29)],WHITE[2],STEEL[0])
    poly(p,[(29,29),(50,19),(50,45),(28,55)],BLACK[2],BLACK[0])
    p.box((19,25,27,42),GOLD,1)
    for y in (29,34,39):
        line(p,[(20,y),(25,y)],GOLD[3],2)
    bevel(p,[(33,30),(43,25),(46,29),(46,41),(35,46),(32,42)],VIOLET)
    line(p,[(35,33),(42,30),(42,38),(36,41)],VIOLET[4],2)
    bevel(p,[(21,19),(36,12),(41,15),(26,23)],RED)
    line(p,[(24,18),(35,13),(38,15)],RED[4])
    for x,y in ((18,17),(30,11)):
        p.cylinder((x,y-6,x+6,y+4),GOLD)
        ellipse(p,(x+1,y-6,x+5,y-3),BLACK,0)
    line(p,[(48,24),(55,26),(56,39),(52,42)],BLACK[0],4)
    line(p,[(48,24),(55,26),(56,39),(52,42)],COPPER[2],2)
    p.box((49,39,56,45),BLACK)
    for x in (50,53):
        line(p,[(x,44),(x,48)],GOLD[3])
    p.bolt(17,43)
    p.bolt(44,21)
    p.bolt(32,48)
    return p.im


def vessel_remnant():
    p=Pixel()
    vessel_frame(p,broken=True)
    disc(p,31,44,9,3,BLACK)
    poly(p,[(26,43),(29,35),(33,39),(36,33),(38,43)],VIOLET[1],VIOLET[0])
    line(p,[(29,38),(30,41)],VIOLET[3])
    return p.im


def engineering_specimen(failed=False):
    p=Pixel()
    bevel(p,[(8,41),(34,29),(57,41),(31,56)],STEEL)
    poly(p,[(8,41),(31,52),(57,41),(57,46),(31,60),(8,47)],BLACK[1],STEEL[0])
    poly(p,[(10,40),(34,31),(54,41),(30,52)],WHITE[2],STEEL[0])
    line(p,[(12,41),(30,49),(51,41)],WHITE[4])
    if failed:
        poly(p,[(20,38),(26,31),(37,31),(45,39),(35,46),(26,45)],BLACK[0],RUST[0])
        iso_block(p,22,35,7,5,4,BLACK)
        iso_block(p,34,38,6,3,4,RUST)
        poly(p,[(25,32),(29,31),(32,34),(29,37),(25,35)],VIOLET[1],VIOLET[0])
        line(p,[(25,32),(28,32),(29,34)],VIOLET[3])
        bevel(p,[(19,25),(26,21),(31,27),(40,25),(41,28),(31,31),(25,26),(20,29)],GOLD,1)
        line(p,[(20,25),(26,23),(30,28)],GOLD[3])
        line(p,[(21,27),(21,33),(24,38)],STEEL[0],3)
        line(p,[(21,27),(21,33),(24,38)],STEEL[3])
        line(p,[(41,29),(39,33)],STEEL[0],3)
        line(p,[(41,29),(39,33)],STEEL[3])
        line(p,[(33,35),(40,40),(44,39)],STEEL[0],4)
        line(p,[(33,35),(40,40),(44,39)],STEEL[2],2)
        line(p,[(21,40),(24,36),(28,39),(28,44)],COPPER[2],2)
        line(p,[(38,35),(44,33),(46,36)],COPPER[3])
        p.box((43,39,48,44),BLACK,1)
        line(p,[(44,44),(44,46)],GOLD[3])
        line(p,[(47,44),(47,46)],GOLD[3])
        p.box((11,43,17,47),RED,1)
    else:
        for x,y in ((23,34),(30,30),(37,34)):
            iso_block(p,x,y,6,7,4,BLACK)
            poly(p,[(x+1,y),(x+6,y-3),(x+9,y),(x+4,y+3)],VIOLET[2],VIOLET[0])
            line(p,[(x+2,y),(x+6,y-2),(x+8,y)],VIOLET[4])
        bevel(p,[(20,25),(31,19),(43,25),(43,29),(31,23),(20,29)],GOLD)
        for pts in ([(21,26),(21,37)],[(31,22),(31,32)],[(42,26),(42,38)]):
            line(p,pts,STEEL[0],3)
            line(p,pts,WHITE[3])
        line(p,[(23,37),(32,42),(41,38)],GOLD[3],2)
        p.box((11,43,17,47),BLUE,2)
    for x,y in ((13,40),(30,52),(50,40)):
        p.bolt(x,y)
    return p.im


def ship_archive():
    p=Pixel()
    bevel(p,[(9,16),(39,8),(55,16),(55,48),(25,57),(9,49)],BLACK)
    poly(p,[(12,19),(39,12),(51,18),(51,45),(25,53),(12,46)],WHITE[2],STEEL[0])
    poly(p,[(15,17),(39,10),(51,16),(51,43),(27,51),(15,44)],GOLD[4],GOLD[0])
    poly(p,[(39,10),(39,17),(51,16)],GOLD[2],GOLD[1])
    line(p,[(17,19),(35,14)],GOLD[1])
    line(p,[(18,22),(32,18)],GOLD[2])
    poly(p,[(21,31),(35,24),(45,25),(39,29),(47,32),(40,35),(28,39),(20,38),(27,34)],BLUE[1])
    line(p,[(22,32),(35,26),(42,26)],BLUE[3])
    line(p,[(28,29),(28,37),(38,33),(38,28)],BLUE[0])
    line(p,[(32,27),(34,25),(34,34)],BLUE[2])
    line(p,[(22,42),(43,36)],GOLD[1])
    line(p,[(22,45),(36,41)],GOLD[2])
    poly(p,[(9,16),(15,17),(15,49),(10,48)],STEEL[2],STEEL[0])
    line(p,[(11,18),(11,45)],STEEL[4])
    p.box((11,24,18,29),GOLD)
    p.box((11,39,18,44),GOLD)
    p.box((45,20,54,27),STEEL,1)
    p.bolt(48,22)
    line(p,[(29,51),(48,46)],WHITE[4])
    line(p,[(30,54),(48,49)],BLACK[3])
    return p.im


def erosion_module():
    p=Pixel()
    bevel(p,[(10,18),(37,9),(53,17),(53,44),(26,55),(10,46)],STEEL)
    poly(p,[(15,21),(36,14),(47,20),(47,41),(27,49),(15,42)],BLACK[1],BLACK[0])
    for x in (19,23,27,31,35,39,43):
        line(p,[(x,47-(x-19)//3),(x,53-(x-19)//3)],BLACK[0],3)
        line(p,[(x,48-(x-19)//3),(x,52-(x-19)//3)],GOLD[3])
    bevel(p,[(25,22),(34,18),(41,22),(41,35),(32,40),(25,36)],VIOLET)
    poly(p,[(27,24),(34,21),(38,24),(38,33),(32,36),(28,33)],BLACK[0])
    line(p,[(29,25),(33,24),(35,26),(33,29),(36,31),(33,34)],VIOLET[3],2)
    line(p,[(28,29),(31,28),(33,29)],VIOLET[4])
    for x,y in ((17,25),(40,18),(17,36),(40,37)):
        p.box((x,y,x+5,y+5),STEEL,1)
        p.d.rectangle((x+1,y+1,x+3,y+3),fill=VIOLET[2])
        p.d.point((x+1,y+1),fill=VIOLET[4])
    for pts in ([(22,28),(25,28)],[(39,25),(43,25),(43,23)],[(22,39),(26,38)],[(39,34),(43,33),(44,37)]):
        line(p,pts,COPPER[2])
    p.bolt(12,20)
    p.bolt(46,17)
    p.bolt(12,42)
    p.bolt(47,41)
    line(p,[(19,16),(36,11),(49,17)],STEEL[4])
    return p.im


ITEMS = [
    ('spatial_probe','空间观测探针','魂钢数据基底、电路封装及仿制空之核心装配；用于量子观测、坐标解算及虚数观测。','industrial_spatial_probe / industrial_quantum_observation / industrial_coordinate_solution','带准直头、折叠测量翼和虚数观测镜片的斜置探针；钢白外壳、黄铜锁环、紫色光学件。'),
    ('industrial_work_drone','工业作业无人机','魂钢数据基底、电路封装及受控纳米群以焊料装配；耐久作业后产生磨损机。','industrial_drone_assembly / industrial_drone_endurance_trial','双侧涵道推进器、块状装甲机身与两只分节夹爪；工具端头可拆换。'),
    ('worn_resource_probe','磨损的资源探测器','无人资源探测器参与采掘派遣后返回磨损件；以纳米构筑单元、电路封装及焊料修复。','industrial_unmanned_mining_dispatch / industrial_resource_probe_repair','三足部署探测器、镜头筒和折弯天线；漆面露底、裂损光学罩及外露铜缆表示耗损。'),
    ('worn_work_drone','磨损的作业无人机','工业作业无人机经钢板作业及润滑剂耐久工艺后产生；维修时拆出无人设备废料。','industrial_drone_endurance_trial / industrial_drone_repair','沿用本轮完整作业机结构，增加缺失夹爪、开裂装甲、锈蚀接口与破损线缆。'),
    ('drone_disassembly_scrap','无人设备拆解废料','维修两种无人设备时产生；分析回收可取得电路封装组件与分离残渣。','industrial_drone_repair / industrial_resource_probe_repair / industrial_recovery_drone_scrap','拆开的推进轴承、断裂白装甲、黄铜接头与铜线混合成机械废料堆。'),
    ('empty_bubble_containment_vessel','空世界泡收容容器','不合格收容壳经空间校准模块、仿制约束核心及稳定介质校准制得；随后用于真实世界泡捕获。','industrial_vessel_calibration / industrial_world_bubble_capture','空透明观察腔、魂钢上下封盖、两侧金色约束立柱与底部校准插座。'),
    ('unstable_simulated_world_bubble','不稳定模拟世界泡','世界物质种子、魂钢板、数据基底及仿制约束核心在收容介质中构建；尚须锚定稳定。','industrial_simulated_world_construction / industrial_simulated_world_stabilization','同系列收容器内分离的块状地层、错位紫色界面与局部亮裂隙，显示尚未连续的世界。'),
    ('stable_simulated_world_bubble','稳定模拟世界泡','不稳定模拟世界泡加四件魂钢锚定组件，以世界稳定介质和冷却剂稳定。','industrial_simulated_world_stabilization','收容器内连续块面微型世界及四个实物锚定扣；规则金色约束环与整齐蓝紫色表层。'),
    ('world_model_carrier','世界模型载体','空间观测探针与崩坏参考样本经量子观测取得；也用于世界泡观测样本化学浴及远古意志重构。','industrial_quantum_observation；Hk3FunctionalItemRecipes.java:68–76','带实体金属保护壳及接点的可抽换数据盒；凹腔中叠装紫色模型存储薄片。'),
    ('world_matter_seed','世界物质种子','八份魂钢数据基底、四份压缩崩坏核心、八片钨钢板、十六份石英岩粉及稳定液态崩坏能装配。','Hk3FunctionalItemRecipes.java:77–83；industrial_simulated_world_construction','重型钨钢承座夹住压缩紫晶与石英突起，三处黄铜夹具固定，强调装配种子而非天然宝石。'),
    ('bubble_termination_charge','世界泡终止组件','魂钢数据基底、空间校准模块及封装组件，以焊料和冷却剂装配；供真实与模拟世界泡终止工艺使用。','industrial_bubble_termination_component / industrial_world_bubble_termination / industrial_simulated_world_termination','有保护滑扣、双接触柱和插接尾线的封装执行器，中央为屏蔽触发模块。'),
    ('bubble_container_remnant','世界泡容器残件','真实或稳定模拟世界泡终止后产出；模拟终止同时回收世界物质种子。','industrial_world_bubble_termination / industrial_simulated_world_termination','被终止过程拆裂的同系列容器底座、断约束柱及残留玻璃碎片；上部大幅缺损。'),
    ('failed_containment_shell','不合格收容壳体','十六片魂钢板和四件电路封装经冷却成壳；需空间校准、约束核心与稳定介质转为空容器。','industrial_vessel_shell / industrial_vessel_calibration','成形但未校准的观察壳，断开的约束立柱、开裂颈圈及未接线底座；保留可返工的整体结构。'),
    ('reverse_engineering_specimen','逆向工程复现样本','真实采掘遗留资料、魂钢数据基底及参考样本经分析制得；虚数观测也可产出。','industrial_reverse_engineering_specimen / industrial_imaginary_observation','小型检验托盘上固定三组复现晶格、支架和连接梁，体现由资料转为可检验实体。'),
    ('failed_engineering_specimen','失败工程样本','多项研究实验与虚数锚定工艺的实体输出，虚数锚定投入魂钢锚定组件、空间校准模块及稳定介质。','industrial_experiment_wcp / industrial_imaginary_anchor','同类检验托盘上扭曲烧蚀的金属／晶格混合件，错断接脚与熔蚀处直接表示失败。'),
    ('ship_engineering_archive','舰船工程档案','舰载工程投入舰艏龙骨段、推进总成、导航模块、舰桥模块及复合材料后输出；可经分析转为仿制休伯利安图纸。','hyperion_shipboard_engineering / industrial_ship_blueprint_analysis','金属护脊夹装的多页工程档案，米色纸面绘舰体分段工程侧视，黄铜锁扣固定。'),
    ('erosion_research_module','侵蚀研究模块','HDV电路、四个传感器、两个发射器、金属板、细导线和四件电路封装用焊料装配；作为研究所可安装模块。','Hk3ControllerRecipes.java:100–114；Hk3ResearchInstituteMachine.java:100–116','具有金色接触梳的插拔硬件卡匣；四个传感封装围绕紫色受屏蔽运算件，钢框与铜走线外露。'),
]


DRAWERS = {
    'spatial_probe': spatial_probe,
    'industrial_work_drone': work_drone,
    'worn_resource_probe': resource_probe,
    'worn_work_drone': lambda: work_drone(True),
    'drone_disassembly_scrap': drone_scrap,
    'empty_bubble_containment_vessel': empty_vessel,
    'unstable_simulated_world_bubble': lambda: simulated_world(False),
    'stable_simulated_world_bubble': lambda: simulated_world(True),
    'world_model_carrier': world_model,
    'world_matter_seed': matter_seed,
    'bubble_termination_charge': termination_charge,
    'bubble_container_remnant': vessel_remnant,
    'failed_containment_shell': lambda: empty_vessel(True),
    'reverse_engineering_specimen': engineering_specimen,
    'failed_engineering_specimen': lambda: engineering_specimen(True),
    'ship_engineering_archive': ship_archive,
    'erosion_research_module': erosion_module,
}


def draw(ident):
    return DRAWERS[ident]()


def save():
    dest=OUT/'textures/item'
    dest.mkdir(parents=True,exist_ok=True)
    fonts=Path('C:/Windows/Fonts')
    font=ImageFont.truetype(str(fonts/'msyh.ttc'),15)
    small=ImageFont.truetype(str(fonts/'consola.ttf'),10)
    sheet=Image.new('RGB',(5*240,4*254),(27,32,40))
    sd=ImageDraw.Draw(sheet)
    for i,(ident,name,_,_,_) in enumerate(ITEMS):
        im=draw(ident)
        im.save(SRC/(ident+'.png'))
        im.save(dest/(ident+'.png'))
        x=(i%5)*240
        y=(i//5)*254
        sd.rectangle((x+4,y+4,x+235,y+249),fill='#303843',outline='#536171')
        sheet.paste(im.resize((192,192),Image.Resampling.NEAREST),(x+24,y+9),im.resize((192,192),Image.Resampling.NEAREST))
        sd.text((x+10,y+204),name,font=font,fill='#e3e5df')
        parts=ident.split('_')
        middle=len(ident)//2
        split=min(range(1,len(parts)),key=lambda j:abs(len('_'.join(parts[:j]))-middle))
        sd.text((x+10,y+226),'_'.join(parts[:split]),font=small,fill='#9aaabb')
        sd.text((x+10,y+238),'_'.join(parts[split:]),font=small,fill='#9aaabb')
    sheet.save(OUT/'world-sheet.png')
    records=[]
    for ident,name,facts,evidence,design in ITEMS:
        paths=[PROCESS]
        if ident=='ship_engineering_archive':
            paths.append(WONDER)
        if ident in ('world_model_carrier','world_matter_seed'):
            paths.append('src/main/java/com/sirin/hk3gtl/common/recipe/machine/Hk3FunctionalItemRecipes.java')
        if ident=='erosion_research_module':
            paths=['src/main/java/com/sirin/hk3gtl/common/recipe/machine/Hk3ControllerRecipes.java','src/main/java/com/sirin/hk3gtl/common/machine/research/Hk3ResearchInstituteMachine.java']
        records.append({'id':ident,'name':name,'function_process_facts':facts,'text_evidence_paths':paths,'text_evidence_locator':evidence,'new_visual_interpretation':design})
    (OUT/'design-world.json').write_text(json.dumps({'revision':'R3','reference_policy':'只读取物品名称、作用与当前工艺文本；未读取旧PNG、截图或旧绘图脚本。外观描述为本轮创作，不作为代码事实。','native_size':[64,64],'items':records},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':
    save()
