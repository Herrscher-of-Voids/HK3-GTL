from pathlib import Path
from io import BytesIO
from zipfile import ZipFile
from PIL import Image

def first(pattern,roots):
 for root in roots:
  path=next(root.glob(pattern),None)
  if path:return ZipFile(path)

home=Path.home()
gt=first('*/gtceu-1.20.1-1.4.4.jar',[home/'.gradle/caches/modules-2/files-2.1/com.gregtechceu.gtceu/gtceu-1.20.1/1.4.4'])
core=first('gtlcore-1.2.3.3-fix4.jar',[Path(__file__).resolve().parents[2]/'libs',home/'.codex/builds/HK3GTL-1.3.12-20261127-111219Z/source/libs'])
vanilla=first('*client.jar',[home/'AppData/Roaming/PrismLauncher/libraries/com/mojang/minecraft/1.20.1'])
materials={'graphene':('shiny',0x808080,0x3d3838),'platinum':('shiny',0xfff4ba,0x8d8d71),'sodium_hydroxide':('dull',0xf5feff,0xa4ebf1),'silicon_dioxide':('quartz',0xf2f2f2,0xb2c4c7),'fullerene':('dull',8831672,8831672),'lanthanum_embedded_fullerene':('dull',9552128,9552128),'fullerene_polymer_matrix_pulp':('dull',2302494,2302494),'carbon_nanotubes':('dull',0,0),'steel':('metallic',0xa7a7a7,0x121c37),'naquadah_alloy':('metallic',0x323232,0x301131),'neutronium':('metallic',0xffffff,0),'tritanium':('metallic',0xc35769,0x210840),'tungsten_steel':('metallic',0x687ece,0x03192f)}
def read_image(archive,path):return Image.open(BytesIO(archive.read(path))).convert('RGBA')
def picture(id):
 if id=='minecraft:paper' and vanilla:return read_image(vanilla,'assets/minecraft/textures/item/paper.png')
 if id=='gtlcore:max_sensor' and core:return read_image(core,'assets/gtlcore/textures/item/max_sensor.png')
 if id.startswith('forge:plates/'):
  name,form=id.split('/')[-1],'plate'
 elif id.startswith('gtceu:') and '_' in id:
  name,form=id.split(':')[1].rsplit('_',1)
 else:return
 if not gt or name not in materials or form not in ('foil','plate','dust'):return
 style,primary,secondary=materials[name];result=Image.new('RGBA',(32,32));found=False
 for suffix,colour in [('',primary),('_secondary',secondary),('_overlay',0xffffff)]:
  for typ in (style,'dull'):
   path=f'assets/gtceu/textures/item/material_sets/{typ}/{form}{suffix}.png'
   if path not in gt.NameToInfo:continue
   im=read_image(gt,path);im=im.crop((0,0,im.width,im.width)).resize((32,32),Image.Resampling.NEAREST);ch=im.split();rgb=[ch[i].point(lambda v,f=(colour>>(16-8*i))&255:v*f//255) for i in range(3)];result.alpha_composite(Image.merge('RGBA',(*rgb,ch[3])));found=True;break
 if found:return result
