# -*- coding: utf-8 -*-
"""I14 V3最终只读核验：NBT/Sponge逐格、材质、边界与压铸构图合同。"""
import base64,gzip,hashlib,json,re,zipfile
from pathlib import Path
import nbtlib
def read_structure(path):
 r=nbtlib.load(path); pal=[]
 for q in r['palette']:
  props=q.get('Properties',{}); suffix='['+','.join(f'{k}={v}' for k,v in sorted(props.items()))+']' if props else ''
  pal.append(str(q['Name'])+suffix)
 return {tuple(map(int,q['pos'])):pal[int(q['state'])] for q in r['blocks']}
from i14_press_v3 import build
from structure_size_baseline import require
from build_i14_press_v3 import OUT
from build_i07_calibration_preview import audit_geometry

def sponge(path):
 r=nbtlib.load(path);assert r.root_name=='Schematic' and int(r['Version'])==2 and int(r['DataVersion'])==3465
 w,h,d=[int(r[k]) for k in ('Width','Height','Length')];pal={int(v):str(k) for k,v in r['Palette'].items()}
 raw=bytes(int(v)&255 for v in r['BlockData']);vals=[];v=shift=0
 for b in raw:
  v|=(b&127)<<shift
  if b&128:shift+=7
  else:vals.append(v);v=shift=0
 assert len(vals)==w*h*d and shift==0
 return {(i%w,i//(w*d),i//w%d):pal[q] for i,q in enumerate(vals) if pal[q]!='minecraft:air'}

def main():
 d=build(); p=OUT/'i14-soulium-press-v3.nbt'; s=OUT/'i14-soulium-press-v3.schem'
 blueprint={tuple(q['pos']):q['state'] for q in json.loads((OUT/'blueprint.json').read_text(encoding='utf-8'))['blocks']}
 nbt=read_structure(p); saved=sponge(s); assert nbt==saved==blueprint
 assert nbt=={tuple(q['pos']):q['state'] for q in d['blocks']}
 audit_geometry(d)
 a=json.loads((OUT/'设计与检查.json').read_text(encoding='utf-8'))['audit']; assert a['size_baseline']['passed']
 assert a['design_markers']=={'minecraft:diamond_block':1,'hk3gtl:industrial_port_casing':6}
 assert a['hashes']=={'nbt':hashlib.sha256(p.read_bytes()).hexdigest(),'schem':hashlib.sha256(s.read_bytes()).hexdigest()}
 encoded=json.loads((OUT/'data.js').read_text(encoding='utf-8').split('=',1)[1].rstrip(';'))
 payload=json.loads(gzip.decompress(base64.b64decode(encoded)))
 assert all(q['complete_cube'] for q in payload['materials']) and payload['audit']==a
 assert sum(map(len,payload['groups']))==len(nbt)
 for path in d['paths']:
  lo,hi=path['min'],path['max']
  assert all((x,lo[1]-1,z) in nbt for x in range(lo[0],hi[0]+1) for z in range(lo[2],hi[2]+1))
 assert all((x,y,z) not in nbt for x in range(22,29) for y in (11,12) for z in range(21,28))
 for page in OUT.glob('*.html'):
  for href in re.findall(r'(?:href|src)="([^"]+)"',page.read_text(encoding='utf-8')):
   if not href.startswith(('http:','https:','#','data:')):assert (page.parent/href).is_file(),href
 archive=OUT/'I14_V3_结构与预览.zip'; z=zipfile.ZipFile(archive); assert z.testzip() is None
 assert all(z.read(n)==(OUT/n).read_bytes() for n in z.namelist())
 out={'passed':True,'nbt_schem_blueprint_equal':True,'size_baseline':a['size_baseline'],'blocks':len(nbt),
      'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'archive_bytes':archive.stat().st_size,
      'status':'外观候选，未批准、未接入正式Pattern、未进行游戏成型运行验收'}
 (Path('logs/i14-press-v3')/'verification.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(out,ensure_ascii=False))
if __name__=='__main__':main()
