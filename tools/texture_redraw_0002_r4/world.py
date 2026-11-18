# -*- coding: utf-8 -*-
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
DELIVERY = ROOT / 'deliveries/0002贴图材质_审定重绘_R4_20261114'
ASSETS = ROOT / 'src/main/resources/assets/hk3gtl/textures/item'
METAL = ['#191e24', '#414b55', '#737f88', '#b6c0c2', '#f0f1dd']
ARMOR = ['#282b2e', '#6c7477', '#acb4af', '#d9ded2', '#fff8de']
BRASS = ['#3a2920', '#735332', '#ae8449', '#e0bd73', '#fff0bb']
VIOLET = ['#24192f', '#4c305d', '#86539f', '#c991d5', '#f3d3f1']
BLUE = ['#162a34', '#2e4d5d', '#548c9a', '#96c9cc', '#d5f0de']
RUBY = ['#2d101d', '#611b32', '#a3314c', '#e16372', '#ffb8a0']
GREEN = ['#172d24', '#2f5740', '#5b8d59', '#a6c184', '#e5edaf']
COPPER = ['#352019', '#6e3d27', '#ab6338', '#df9859', '#ffcf86']
SOOT = ['#1c2024', '#363e45', '#56626a', '#849196', '#c1c6c1']


class Sprite:
    def __init__(self):
        self.im = Image.new('RGBA', (64, 64))
        self.d = ImageDraw.Draw(self.im)

    def poly(self, points, fill, outline=None):
        self.d.polygon(points, fill=fill, outline=outline)

    def line(self, points, fill, width=1):
        self.d.line(points, fill=fill, width=width)

    def box(self, box, pal=METAL, value=2):
        x,y,r,b = box
        self.d.rectangle(box, fill=pal[value], outline=pal[0])
        self.line([(x+1,b-1),(x+1,y+1),(r-1,y+1)],pal[min(4,value+1)])
        self.line([(r-1,y+2),(r-1,b-1)],pal[1])

    def oval(self, box, pal=METAL, value=2):
        self.d.ellipse(box, fill=pal[value], outline=pal[0])

    def bolt(self,x,y):
        self.d.rectangle((x,y,x+2,y+2),fill=METAL[0])
        self.d.point((x,y),fill=METAL[4])
        self.d.point((x+1,y+1),fill=METAL[2])

    def limb(self,points,pal=METAL,width=4):
        self.line(points,pal[0],width+2)
        self.line(points,pal[2],width)
        self.line([(x-1,y-1) for x,y in points],pal[3])

    def chip(self,points,pal=ARMOR):
        self.poly(points,pal[2],pal[0])
        self.line(points[:3],pal[4])


def spatial_probe():
    s=Sprite()
    s.limb([(32,38),(29,46),(13,56)],METAL,3)
    s.limb([(32,39),(38,44),(50,54)],METAL,3)
    s.limb([(32,39),(34,54),(30,59)],METAL,3)
    s.box((9,54,17,57),METAL,1)
    s.box((46,53,55,56),METAL,1)
    s.box((27,57,34,60),METAL,1)
    s.box((29,30,36,44),BRASS,1)
    for y in (33,38,42):
        s.line([(30,y),(35,y)],BRASS[3])
    s.oval((25,32,39,40),METAL,2)
    s.poly([(23,12),(44,16),(53,23),(32,20)],ARMOR[3],METAL[0])
    s.poly([(32,20),(53,23),(51,34),(31,31)],METAL[1],METAL[0])
    s.poly([(23,12),(32,20),(31,31),(21,25)],ARMOR[2],METAL[0])
    s.line([(24,13),(43,17),(49,21)],ARMOR[4])
    s.poly([(13,17),(23,13),(32,20),(30,33),(21,38),(12,30)],BRASS[2],BRASS[0])
    s.poly([(15,20),(23,17),(28,22),(27,30),(21,34),(15,29)],METAL[0])
    s.poly([(17,21),(23,19),(26,23),(25,29),(21,31),(17,28)],VIOLET[1])
    s.line([(17,22),(20,20),(23,20)],VIOLET[4],2)
    s.line([(20,30),(24,28),(25,25)],VIOLET[2])
    for x,y in ((36,22),(41,23),(46,24)):
        s.line([(x,y),(x+3,y+1),(x+3,y+7)],METAL[3])
    s.limb([(43,16),(47,8),(54,10)],METAL,2)
    s.box((49,6,56,11),BRASS,2)
    s.line([(50,7),(54,8)],ARMOR[4])
    s.box((34,12,41,16),METAL,2)
    s.bolt(30,34)
    s.bolt(21,14)
    return s.im


def fan(s,cx,cy,broken=False):
    s.oval((cx-10,cy-7,cx+10,cy+7),METAL,2)
    s.d.arc((cx-9,cy-6,cx+9,cy+6),180,320,fill=ARMOR[4])
    s.oval((cx-7,cy-4,cx+7,cy+4),METAL,0)
    s.line([(cx-5,cy-2),(cx+5,cy+2)],METAL[2],2)
    s.line([(cx+4,cy-2),(cx-4,cy+2)],METAL[1],2)
    s.oval((cx-2,cy-2,cx+2,cy+2),BRASS,2)
    if broken:
        s.poly([(cx-11,cy),(cx-4,cy+1),(cx-2,cy+8),(cx-11,cy+8)],(0,0,0,0))
        s.line([(cx-8,cy-1),(cx-4,cy+1)],COPPER[2],2)


def industrial_drone(worn=False):
    s=Sprite()
    s.limb([(15,16),(26,24),(31,29)],METAL,4)
    s.limb([(47,13),(37,22),(31,29)],METAL,4)
    s.limb([(11,38),(25,33),(31,29)],METAL,4)
    s.limb([(49,37),(38,33),(31,29)],METAL,4)
    fan(s,14,15)
    fan(s,48,12)
    fan(s,11,38,worn)
    fan(s,50,37)
    s.poly([(22,20),(34,17),(43,25),(40,37),(29,42),(21,32)],ARMOR[2],METAL[0])
    s.poly([(22,20),(34,17),(43,25),(31,29)],ARMOR[3],METAL[0])
    s.poly([(31,29),(43,25),(40,37),(29,42)],METAL[1],METAL[0])
    s.poly([(25,21),(32,19),(37,23),(30,26)],BRASS[2],BRASS[0])
    s.line([(26,21),(32,20),(35,23)],BRASS[4])
    s.box((22,28,29,34),METAL,0)
    s.box((24,29,27,32),VIOLET,2)
    s.line([(34,32),(39,30)],METAL[3])
    s.line([(33,35),(38,33)],METAL[2])
    s.box((27,40,35,45),BRASS,1)
    s.oval((27,42,35,48),METAL,2)
    if worn:
        s.limb([(29,46),(24,49),(18,47)],METAL,3)
        s.limb([(33,46),(37,51),(39,51)],METAL,3)
        s.line([(19,46),(16,50),(19,52)],COPPER[2],2)
        s.poly([(36,20),(42,24),(40,29),(37,27)],METAL[0])
        s.line([(37,21),(40,24)],ARMOR[4])
        s.line([(23,23),(26,25),(25,29)],COPPER[0],2)
        s.line([(32,37),(35,35),(37,36)],COPPER[2])
        s.line([(7,34),(12,36)],COPPER[2])
        s.bolt(36,23)
    else:
        s.limb([(29,46),(24,50),(24,56),(28,57)],METAL,3)
        s.limb([(33,46),(38,50),(38,56),(34,57)],METAL,3)
        s.poly([(22,53),(26,53),(29,56),(27,59),(22,56)],BRASS[2],BRASS[0])
        s.poly([(36,53),(40,53),(40,56),(35,59),(33,56)],BRASS[2],BRASS[0])
    s.bolt(22,23)
    s.bolt(37,27)
    return s.im


def resource_probe():
    s=Sprite()
    s.poly([(13,39),(20,34),(39,35),(44,42),(40,51),(19,54),(12,48)],METAL[0])
    s.oval((12,41,27,53),METAL,1)
    s.oval((32,39,46,51),METAL,1)
    s.oval((15,44,23,50),METAL,3)
    s.oval((35,42,43,48),METAL,2)
    s.oval((18,46,20,48),METAL,0)
    s.oval((38,44,40,46),METAL,0)
    s.poly([(17,31),(36,27),(48,34),(29,40)],ARMOR[3],METAL[0])
    s.poly([(29,40),(48,34),(47,45),(29,50)],METAL[1],METAL[0])
    s.poly([(17,31),(29,40),(29,50),(16,42)],ARMOR[2],METAL[0])
    s.poly([(20,33),(25,31),(32,34),(28,37)],BRASS[2],BRASS[0])
    s.line([(32,42),(43,39)],BRASS[2],2)
    s.line([(31,46),(42,43)],METAL[3])
    s.box((32,17,37,31),METAL,1)
    s.limb([(35,18),(31,10),(34,5)],METAL,2)
    s.poly([(20,9),(31,5),(40,9),(30,15)],BRASS[2],BRASS[0])
    s.poly([(22,9),(30,7),(36,9),(29,12)],METAL[0])
    s.line([(24,9),(29,8)],BLUE[3])
    s.limb([(18,34),(12,28),(7,29)],METAL,3)
    s.poly([(5,23),(13,23),(16,30),(12,36),(5,34),(3,29)],METAL[2],METAL[0])
    s.poly([(6,26),(11,25),(13,29),(10,32),(6,31)],BLUE[1],BLUE[0])
    s.line([(6,26),(10,26)],BLUE[4])
    s.line([(9,27),(8,30),(12,31)],METAL[0],2)
    s.poly([(47,27),(52,30),(54,41),(49,46),(47,40)],BRASS[2],BRASS[0])
    s.line([(51,35),(55,39),(53,45),(57,48)],COPPER[2],2)
    s.line([(34,30),(38,31),(37,35)],COPPER[0],2)
    s.line([(35,30),(38,31)],COPPER[3])
    s.poly([(16,47),(22,45),(25,48),(21,52),(17,51)],COPPER[1],METAL[0])
    s.bolt(40,34)
    s.bolt(19,39)
    return s.im


def drone_scrap():
    s=Sprite()
    s.poly([(9,42),(17,32),(30,31),(40,36),(52,40),(48,51),(31,57),(15,53)],METAL[0])
    s.poly([(8,37),(15,31),(24,32),(27,39),(23,47),(14,48),(7,43)],METAL[2],METAL[0])
    s.poly([(12,38),(16,35),(21,36),(22,40),(18,43),(13,42)],(0,0,0,0))
    s.poly([(8,38),(12,36),(15,40),(13,45),(8,44)],ARMOR[3],METAL[0])
    s.limb([(26,34),(33,42),(45,42)],METAL,4)
    s.poly([(26,21),(38,19),(42,24),(37,35),(30,34),(26,28)],ARMOR[2],METAL[0])
    s.poly([(29,22),(37,21),(39,24),(34,27),(29,26)],ARMOR[4])
    s.poly([(32,28),(35,29),(34,34),(30,33)],METAL[0])
    s.line([(32,28),(35,29),(34,34)],COPPER[2])
    s.oval((34,37,48,50),METAL,1)
    s.oval((37,39,45,47),COPPER,2)
    s.oval((39,41,43,45),METAL,0)
    s.box((19,43,29,51),METAL,1)
    s.box((21,45,26,49),VIOLET,1)
    for x in (20,24,28):
        s.line([(x,51),(x,54)],BRASS[3])
    s.limb([(43,28),(49,25),(53,30),(50,34)],METAL,2)
    s.line([(18,32),(16,26),(21,23),(24,27)],COPPER[3],2)
    s.line([(45,49),(53,45),(56,48)],COPPER[2],2)
    s.bolt(10,40)
    return s.im


def specimen(failed=False):
    s=Sprite()
    if failed:
        s.poly([(9,36),(17,25),(26,27),(28,40),(20,47),(11,44)],METAL[2],METAL[0])
        s.poly([(12,35),(18,29),(22,30),(22,37),(18,41),(13,39)],METAL[0])
        s.poly([(11,44),(20,47),(23,53),(16,56),(7,51)],ARMOR[2],METAL[0])
        s.poly([(33,31),(46,22),(54,30),(49,43),(40,46),(33,41)],METAL[1],METAL[0])
        s.poly([(40,30),(46,26),(50,30),(46,37),(40,38)],METAL[0])
        s.limb([(18,34),(28,31),(33,37),(41,34)],METAL,3)
        s.poly([(25,29),(29,25),(34,28),(35,34),(30,36),(26,33)],COPPER[1],COPPER[0])
        s.line([(26,30),(29,28),(31,30)],COPPER[3])
        s.line([(28,36),(27,42),(33,47),(36,43)],COPPER[2],2)
        s.poly([(24,47),(28,41),(33,43),(32,49),(27,52)],VIOLET[1],VIOLET[0])
        s.line([(27,43),(30,44)],VIOLET[3])
        s.poly([(40,45),(44,42),(49,45),(47,50),(43,49)],ARMOR[2],METAL[0])
        s.box((45,49,51,53),BRASS,1)
        s.bolt(14,47)
        s.bolt(47,24)
        return s.im
    s.poly([(10,34),(18,25),(26,29),(22,41),(14,45),(8,40)],METAL[1],METAL[0])
    s.poly([(10,34),(18,28),(23,31),(18,38),(13,39)],ARMOR[3],METAL[0])
    s.poly([(13,45),(21,40),(27,47),(19,53),(9,51)],METAL[2],METAL[0])
    s.poly([(38,22),(47,17),(55,23),(54,39),(46,45),(38,39)],ARMOR[2],METAL[0])
    s.poly([(41,24),(47,21),(51,24),(50,35),(45,39),(41,35)],METAL[0])
    s.limb([(19,33),(45,29)],METAL,5)
    s.poly([(23,26),(33,22),(40,27),(39,38),(30,43),(23,37)],COPPER[2],COPPER[0])
    for x,y in ((25,27),(29,26),(33,25)):
        s.line([(x,y),(x+3,y+3),(x+3,y+11)],COPPER[4])
    s.poly([(30,25),(35,24),(39,27),(38,37),(33,40),(30,37)],VIOLET[1],VIOLET[0])
    s.line([(32,27),(35,26),(36,28),(36,34)],VIOLET[3],2)
    s.poly([(27,19),(35,16),(41,21),(33,25)],ARMOR[3],METAL[0])
    s.poly([(18,39),(25,35),(31,41),(24,45)],BRASS[2],BRASS[0])
    s.box((40,42,49,48),METAL,2)
    for x in (41,44,47):
        s.line([(x,47),(x,51)],BRASS[3])
    s.bolt(16,45)
    s.bolt(46,18)
    s.bolt(49,37)
    return s.im


def erosion_module():
    s=Sprite()
    s.poly([(19,11),(39,6),(51,15),(31,21)],ARMOR[3],METAL[0])
    s.poly([(31,21),(51,15),(51,45),(31,53)],METAL[1],METAL[0])
    s.poly([(19,11),(31,21),(31,53),(19,43)],ARMOR[2],METAL[0])
    s.poly([(22,16),(28,21),(28,44),(22,40)],METAL[0])
    s.poly([(33,23),(47,19),(47,42),(33,48)],METAL[0])
    s.poly([(36,26),(43,24),(45,27),(45,37),(41,41),(36,39)],VIOLET[1],VIOLET[0])
    s.poly([(37,27),(40,26),(42,29),(42,36),(39,38),(37,36)],VIOLET[2])
    s.line([(38,27),(40,28),(40,34)],VIOLET[4])
    for x,y in ((32,23),(44,19),(32,42),(44,38)):
        s.box((x,y,x+4,y+4),BRASS,1)
        s.d.rectangle((x+1,y+1,x+2,y+2),fill=BLUE[3])
    for y in (23,34):
        s.poly([(17,y),(22,y-2),(26,y+1),(26,y+6),(21,y+8),(17,y+5)],METAL[2],METAL[0])
        s.poly([(18,y+1),(21,y),(24,y+2),(24,y+4),(21,y+6),(18,y+4)],METAL[0])
        s.d.point((20,y+2),fill=VIOLET[3])
    for y in (24,29,34,39):
        s.line([(48,y),(52,y-1),(52,y+1),(48,y+2)],METAL[3])
    for x in (33,40):
        s.poly([(x,50),(x+5,48),(x+5,55),(x,57)],BRASS[2],BRASS[0])
        s.line([(x+2,51),(x+2,55)],BRASS[4])
    s.box((26,8,35,12),METAL,2)
    s.line([(27,9),(33,9)],VIOLET[2])
    s.bolt(20,13)
    s.bolt(47,15)
    s.bolt(20,40)
    return s.im


def eden():
    s=Sprite()
    s.poly([(17,13),(22,8),(32,7),(40,11),(38,18),(27,17)],BRASS[2],BRASS[0])
    s.poly([(9,24),(14,15),(20,16),(20,24),(15,31),(9,31)],METAL[2],METAL[0])
    s.poly([(41,39),(52,32),(57,38),(53,49),(43,56),(36,53),(36,46)],METAL[1],METAL[0])
    s.line([(43,44),(52,38),(54,40)],METAL[3],2)
    s.poly([(18,18),(27,13),(38,14),(47,21),(51,32),(48,43),(40,50),(28,52),(18,47),(11,38),(11,27)],RUBY[1],RUBY[0])
    s.poly([(18,18),(27,14),(37,15),(40,22),(30,29),(17,28),(12,32),(13,26)],RUBY[3])
    s.poly([(17,29),(30,28),(40,22),(46,24),(48,34),(41,40),(29,39),(20,44),(14,37)],RUBY[2])
    s.poly([(29,40),(41,40),(48,34),(47,42),(40,48),(29,50),(21,46)],RUBY[0])
    s.poly([(18,20),(25,17),(31,17),(32,20),(24,23),(18,23)],RUBY[4])
    s.poly([(28,16),(34,14),(41,18),(45,24),(42,29),(37,24),(35,20)],BRASS[2],BRASS[0])
    s.line([(30,16),(35,16),(40,20),(43,25)],BRASS[4],2)
    s.poly([(11,28),(16,26),(22,34),(30,41),(39,45),(40,50),(31,48),(21,42),(14,35)],BRASS[2],BRASS[0])
    s.line([(13,29),(18,34),(24,40),(33,45)],BRASS[4],2)
    s.poly([(21,49),(26,44),(32,46),(34,53),(28,57),(21,54)],BRASS[2],BRASS[0])
    s.poly([(44,21),(50,18),(55,23),(55,30),(49,32),(46,28)],BRASS[2],BRASS[0])
    s.line([(48,22),(51,21),(53,24)],BRASS[4])
    s.bolt(24,49)
    s.bolt(48,24)
    s.bolt(12,22)
    return s.im


def judah():
    s=Sprite()
    shape=[(21,5),(31,3),(36,17),(49,14),(54,25),(40,29),(47,50),(36,57),(27,33),(12,37),(7,25),(23,21)]
    s.poly([(x+4,y+3) for x,y in shape],BRASS[1],BRASS[0])
    for a,b in ((0,1),(2,3),(4,5),(6,7),(8,9),(10,11)):
        pa,pb=shape[a],shape[b]
        s.poly([pa,pb,(pb[0]+4,pb[1]+3),(pa[0]+4,pa[1]+3)],BRASS[1],BRASS[0])
    s.poly(shape,BRASS[2],BRASS[0])
    s.line([(22,6),(29,5),(34,20),(48,17),(51,23)],BRASS[4],2)
    s.poly([(24,8),(28,7),(42,48),(37,51)],METAL[0])
    s.poly([(27,12),(29,11),(40,45),(38,47)],BRASS[3])
    s.poly([(11,26),(25,23),(29,31),(14,34)],METAL[0])
    s.poly([(36,20),(48,17),(50,23),(39,26)],METAL[0])
    s.line([(13,27),(24,25)],BRASS[3],2)
    s.line([(39,21),(47,19)],BRASS[3],2)
    s.poly([(25,23),(32,20),(38,27),(34,35),(28,36),(24,30)],ARMOR[2],METAL[0])
    s.poly([(28,25),(32,24),(35,28),(33,32),(29,33),(27,29)],GREEN[1],GREEN[0])
    s.line([(29,26),(31,25),(33,28)],GREEN[4])
    s.line([(30,32),(33,30)],GREEN[2])
    s.poly([(34,39),(38,38),(42,49),(38,52)],BRASS[1],BRASS[0])
    s.line([(36,41),(39,48)],BRASS[4])
    for x,y in ((18,31),(20,36),(17,41),(19,46),(24,48),(28,45)):
        s.d.ellipse((x-2,y-2,x+2,y+3),fill=BRASS[0],outline=BRASS[3])
    s.poly([(44,26),(48,26),(55,43),(52,47)],METAL[1],METAL[0])
    s.line([(46,28),(53,43)],ARMOR[3])
    for x,y in ((24,8),(47,18),(13,28),(37,48)):
        s.bolt(x,y)
    return s.im


def anchor_component():
    s=Sprite()
    s.poly([(15,39),(39,15),(45,21),(21,45)],METAL[1],METAL[0])
    s.line([(18,39),(40,17)],METAL[3],2)
    s.poly([(32,17),(40,9),(50,13),(56,22),(48,30),(39,27)],METAL[2],METAL[0])
    s.poly([(36,17),(41,12),(48,15),(52,21),(47,26),(41,24)],ARMOR[3],METAL[0])
    s.poly([(41,16),(45,15),(49,20),(46,23),(42,21)],METAL[0])
    for i in range(4):
        x=24+i*4
        y=35-i*4
        s.line([(x-3,y-3),(x+3,y+3)],METAL[0],3)
        s.line([(x-3,y-4),(x+3,y+2)],BRASS[3])
    s.poly([(10,35),(18,28),(26,36),(22,40),(15,38),(16,45),(11,49),(6,43)],ARMOR[2],METAL[0])
    s.poly([(22,40),(27,36),(34,43),(29,51),(20,56),(13,52),(17,47),(24,47)],METAL[2],METAL[0])
    s.line([(8,39),(11,36),(15,39)],ARMOR[4],2)
    s.line([(19,51),(27,48),(30,44)],METAL[4])
    s.poly([(30,21),(35,18),(41,23),(36,28)],VIOLET[1],METAL[0])
    s.line([(32,21),(35,20),(38,23)],VIOLET[3])
    s.poly([(34,32),(40,27),(46,32),(41,37)],BRASS[2],BRASS[0])
    s.line([(37,31),(40,29),(43,32)],BRASS[4])
    s.bolt(12,39)
    s.bolt(24,48)
    return s.im


def gas_impurity():
    s=Sprite()
    s.poly([(9,42),(13,34),(21,35),(27,29),(37,31),(46,26),(53,32),(50,39),(56,44),(46,49),(34,47),(24,54),(14,49)],SOOT[1],SOOT[0])
    s.poly([(13,38),(18,31),(25,33),(32,30),(38,35),(33,39),(25,37),(20,43),(14,43)],SOOT[3],SOOT[0])
    s.line([(14,37),(19,32),(24,34),(30,32),(36,36)],SOOT[4])
    s.poly([(23,40),(29,36),(37,38),(41,34),(48,37),(47,43),(40,45),(33,42),(27,47),(20,45)],SOOT[2],SOOT[0])
    s.line([(23,41),(28,38),(34,40),(39,37),(45,39)],SOOT[4])
    s.poly([(36,32),(42,28),(49,31),(47,35),(41,36)],SOOT[3],SOOT[0])
    for x,y in ((16,38),(22,36),(27,42),(34,39),(40,42),(46,39),(19,46),(37,32),(49,43)):
        s.d.rectangle((x,y,x+2,y+1),fill=SOOT[0])
        s.d.point((x,y-1),fill=SOOT[4])
    for x,y in ((17,44),(23,31),(35,45),(44,32)):
        s.poly([(x,y),(x+3,y-1),(x+5,y+2),(x+2,y+4)],COPPER[1],COPPER[0])
        s.d.point((x+2,y),fill=COPPER[3])
    s.poly([(9,49),(13,47),(17,50),(15,54),(10,53)],SOOT[2],SOOT[0])
    s.poly([(50,47),(54,45),(58,49),(55,53),(51,52)],SOOT[2],SOOT[0])
    s.d.rectangle((21,55,24,57),fill=SOOT[2])
    s.d.rectangle((42,53,45,55),fill=SOOT[1])
    return s.im


def keel_segment():
    s=Sprite()
    def v(t,w,h=0):
        return (round(12+t*.88+w*.6),round(49-t*.58+w*.32-h))
    def beam(a,b,pal=METAL,width=3):
        s.limb([v(*a),v(*b)],pal,width)
    for w in (-9,9):
        beam((0,w),(44,w),METAL,4)
        beam((0,w,12),(44,w,12),ARMOR,3)
    beam((0,0),(44,0),BLUE,5)
    for t in (44,29,14,0):
        pts=[v(t,-10),v(t,-10,10),v(t,-6,15),v(t,6,15),v(t,10,10),v(t,10)]
        s.limb(pts,METAL,4)
        s.line([v(t,-10,9),v(t,-6,14),v(t,6,14),v(t,10,9)],ARMOR[4])
        for w in (-9,9):
            x,y=v(t,w,1)
            s.bolt(x-1,y-1)
    for w in (-9,9):
        for t in (0,14,29):
            beam((t,w,1),(t+14,w,11),METAL,2)
    s.poly([v(-3,-6),v(-3,6),v(0,7),v(0,-7)],METAL[1],METAL[0])
    s.line([v(-2,-4),v(-2,4)],ARMOR[3])
    s.poly([v(44,-6),v(48,-6),v(48,6),v(44,6)],ARMOR[2],METAL[0])
    s.line([v(45,-4),v(47,-4),v(47,3)],ARMOR[4])
    return s.im


IDS = (
    'spatial_probe','industrial_work_drone','worn_resource_probe','worn_work_drone',
    'drone_disassembly_scrap','reverse_engineering_specimen','failed_engineering_specimen',
    'erosion_research_module','imitation_star_of_eden','imitation_oath_of_judah',
    'soulium_anchor_component','process_gas_impurity','hyperion_keel_segment',
)
NAMES = (
    '空间观测探针','工业作业无人机','磨损的资源探测器','磨损的作业无人机',
    '无人设备拆解废料','逆向工程复现样本','失败工程样本','侵蚀研究模块',
    '仿制的伊甸之星','仿制的犹大的誓约','魂钢锚定组件','工艺气体杂质','仿制休伯利安龙骨段',
)
DRAW = (
    spatial_probe,industrial_drone,resource_probe,lambda:industrial_drone(True),
    drone_scrap,specimen,lambda:specimen(True),erosion_module,eden,judah,
    anchor_component,gas_impurity,keel_segment,
)


def draw(ident):
    return DRAW[IDS.index(ident)]()


FACTS = (
    ('魂钢数据基底、电路封装组件与仿制空之核心装配；参与量子观测、坐标解算和虚数观测。','industrial_spatial_probe / industrial_quantum_observation / industrial_coordinate_solution / industrial_imaginary_observation','三脚部署架承托横置光学探头，前端为紫色分光物镜，后部带校准天线和金属散热片。'),
    ('八份魂钢数据基底、四件电路封装及两份受控纳米群通过焊料装配；耐久作业后返回磨损机。','industrial_drone_assembly / industrial_drone_endurance_trial','四个真实涵道风扇由承力臂连接装甲机身，下吊单组可开合工具钳，构成完整无人飞行作业设备。'),
    ('无人资源探测器由空间探针、数据基底、电路封装及纳米群装配；参与无人采掘派遣后返回磨损探测器，可修复。','industrial_unmanned_resource_probe / industrial_unmanned_mining_dispatch / industrial_resource_probe_repair','低位四轮探测底盘携带伸出式取样镜头、折损测量天线和侧置信号组件；缺损轮皮、镜片裂口和铜线体现返航磨损。'),
    ('工业作业无人机经历钢板与润滑剂耐久工艺后成为磨损机；以纳米构筑单元、封装组件和焊料修复，并拆出废料。','industrial_drone_endurance_trial / industrial_drone_repair','本轮四涵道无人机的独立破损姿态：左前涵道缺口、下吊钳折断、装甲破口及断开的内部导线。'),
    ('无人作业设备维修及采掘派遣产生；分离滤芯与分析试剂可回收其中的电路封装组件。','industrial_drone_repair / industrial_unmanned_mining_dispatch / industrial_recovery_drone_scrap','半个断裂涵道、被拆开的铜绕组电机、折断承力臂、剥开的装甲与带针脚封装散落成拆解堆。'),
    ('真实采掘遗留资料、魂钢数据基底和参考样本经分析试剂处理产出；虚数观测也可制得。','industrial_reverse_engineering_specimen / industrial_imaginary_observation','带固定耳与外接插针的半剖封装样机，壳体开口露出铜绕组、轴芯和紫色结构层；具体器械形制是美术推导。'),
    ('多项研究实验会产出；虚数锚定工艺消耗锚定组件、校准模块与稳定介质后亦产出此件。','industrial_experiment_wcp / industrial_imaginary_anchor','裂成两半的实体封装与弯折轴芯，烧蚀绕组、碎裂紫色层和歪斜接脚外露；不以警告图案代替失败结构。'),
    ('HDV四电路、四传感器、两发射器、八板、十六细线、四封装组件与1152mB焊料装配；可安装到研究所。','Hk3ControllerRecipes.java:100–114 / Hk3ResearchInstituteMachine.java:100–116','厚壁插拔仪器盒带双发射端口、四个观察传感件、侧散热鳍片及双金属插舌；紫色受屏蔽测试元件可由观察窗看见。'),
    ('神之键封装框架与仿制岩之核心在I33工艺中装配出仿制的伊甸之星。','industrial_imitation_star_of_eden','以不透明红色球面实体为中心，三维金色约束抱带、后侧黑钢机械挂座及下方锁紧件形成球体封装；形制由名称与装配关系推导。'),
    ('神之键封装框架与仿制约束核心在I33工艺中装配；现实稳定锚定机检测投入总线中的该模块。','industrial_imitation_oath_of_judah / Hk3RealityStabilityAnchorMachine.java:44–48','斜置厚重十字形兵装匣，主体有独立侧壁、金色装甲嵌条、绿色约束核心窗、附属枪杆与金属锁链。'),
    ('八片钨钢板、四份铂箔与两件崩坏能适配电路基板装配；用于采集、虚数锚定和世界维系工艺。','industrial_anchor_component / industrial_imaginary_anchor / industrial_world_maintenance','楔锁式膨胀锚栓：粗轴、分段锁齿、两片可张开的金属楔足及带紫色绝缘段的铂触点，实体机械结构承担锚定含义。'),
    ('工艺气体滤芯处理1000mB废魂钢工艺气，同时得到失效滤芯、两份杂质、保护气和高温尾气。','industrial_gas_purification','从滤芯分离出的多孔灰黑沉积层片，断面呈纤维层和焦结孔隙，夹杂少量铜褐凝结颗粒。'),
    ('魂钢数据基底、电路封装、涂层纳米群经冷却装配产出；八件龙骨段投入H01舰载工程。','industrial_ship_components / hyperion_shipboard_engineering','开放船体骨架段由双纵梁、中央深色龙骨、四道带大孔的横肋、斜撑和端部拼装接头构成；不画成整舰或封闭装甲块。'),
)


def save():
    dest=DELIVERY/'textures/item'
    dest.mkdir(parents=True,exist_ok=True)
    font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',14)
    small=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',10)
    sheet=Image.new('RGB',(4*250,4*251),'#20252b')
    d=ImageDraw.Draw(sheet)
    for i,(ident,name) in enumerate(zip(IDS,NAMES)):
        im=draw(ident)
        im.save(ASSETS/(ident+'.png'))
        im.save(dest/(ident+'.png'))
        x,y=(i%4)*250,(i//4)*251
        d.rectangle((x+4,y+4,x+245,y+246),fill='#303940',outline='#5c6668')
        large=im.resize((192,192),Image.Resampling.NEAREST)
        sheet.paste(large,(x+28,y+8),large)
        d.text((x+10,y+205),name,font=font,fill='#e6e8dd')
        d.text((x+10,y+229),ident,font=small,fill='#a7b7ba')
    sheet.save(DELIVERY/'world-r4-sheet.png')
    items=[]
    base='src/main/resources/data/hk3gtl/research/'
    for ident,name,(fact,locator,art) in zip(IDS,NAMES,FACTS):
        paths=[base+'industrial_processes.json']
        if ident=='hyperion_keel_segment':
            paths.append(base+'wonder_processes.json')
        if ident=='erosion_research_module':
            paths=['src/main/java/com/sirin/hk3gtl/common/recipe/machine/Hk3ControllerRecipes.java','src/main/java/com/sirin/hk3gtl/common/machine/research/Hk3ResearchInstituteMachine.java']
        if ident=='imitation_oath_of_judah':
            paths.append('src/main/java/com/sirin/hk3gtl/common/machine/research/Hk3RealityStabilityAnchorMachine.java')
        items.append({'id':ident,'name':name,'function_process_facts':fact,'text_evidence_paths':paths,'text_evidence_locator':locator,'new_visual_interpretation':art})
    (DELIVERY/'design-world.json').write_text(json.dumps({'revision':'R4','items':items},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':
    save()
