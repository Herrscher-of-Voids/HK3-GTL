# -*- coding: utf-8 -*-
"""69座独立预览交付：逐格数据、实际材质图、NBT及Sponge同源导出。
变更#1 2026-09-28 03:21:36：新增流式NBT写入与逐台释放；不启动游戏，不替换正式文件。
复用Minecraft Builder流程的数据合同；大型候选采用标准NBT流式编码避免大量对象常驻。
"""
from pathlib import Path
import sys,json,gzip,struct,base64,collections,hashlib,datetime,io,os
import numpy as np
import nbtlib
from PIL import Image,ImageDraw,ImageFont
from redesign69_geometry import build,P,ROOT
from structure_size_baseline import require
from material_resources import Resources

OUT=ROOT/'doc/HK3GTL-内测5/03_机器结构/69座重设计_实体预览01'
LOG=ROOT/'logs/structure-redesign-20260928/preview01'

def string(s):
 b=s.encode('utf-8');return struct.pack('>H',len(b))+b
def tag(t,name):return bytes([t])+string(name)
def integer(name,v):return tag(3,name)+struct.pack('>i',v)
def listint(name,values):return tag(9,name)+bytes([3])+struct.pack('>i',len(values))+struct.pack('>'+str(len(values))+'i',*values)
def palette_nbt(state):
 name=state.split('[')[0];raw=tag(8,'Name')+string(name)
 if '[' in state:
  raw+=tag(10,'Properties')
  for k,v in sorted(dict(__import__('re').findall(r'(\w+)=([^,\]]+)',state)).items()):raw+=tag(8,k)+string(v)
  raw+=b'\x00'
 return raw+b'\x00'
def export(data,out,validator=require):
 validator(data)
 states=sorted({b['state'] for b in data['blocks']});ids={s:i for i,s in enumerate(states)};w,h,d=data['size']
 nbt=out/(data['name']+'.nbt')
 with gzip.open(nbt,'wb',compresslevel=9) as f:
  f.write(tag(10,'')+integer('DataVersion',3465)+listint('size',[w,h,d]))
  f.write(tag(9,'palette')+b'\x0a'+struct.pack('>i',len(states)))
  for s in states:f.write(palette_nbt(s))
  f.write(tag(9,'blocks')+b'\x0a'+struct.pack('>i',len(data['blocks'])))
  buffer=bytearray()
  for b in data['blocks']:
   buffer+=listint('pos',b['pos'])+integer('state',ids[b['state']])+b'\x00'
   if len(buffer)>1048576:f.write(buffer);buffer.clear()
  f.write(buffer);f.write(tag(9,'entities')+b'\x0a'+struct.pack('>i',0)+b'\x00')
 dense=np.zeros(w*h*d,dtype=np.uint8);groups=[[] for _ in states]
 assert len(states)<127
 for b in data['blocks']:
  x,y,z=b['pos'];index=(y*d+z)*w+x;mid=ids[b['state']];dense[index]=mid+1;groups[mid].append(index)
 schem=out/(data['name']+'.schem')
 with gzip.open(schem,'wb',compresslevel=9) as f:
  f.write(tag(10,'Schematic')+integer('Version',2)+integer('DataVersion',3465))
  for k,v in zip(('Width','Height','Length'),(w,h,d)):f.write(tag(2,k)+struct.pack('>h',v))
  f.write(tag(11,'Offset')+struct.pack('>i3i',3,0,0,0)+integer('PaletteMax',len(states)+1)+tag(10,'Palette'))
  f.write(integer('minecraft:air',0))
  for s,i in ids.items():f.write(integer(s,i+1))
  f.write(b'\x00'+tag(7,'BlockData')+struct.pack('>i',dense.size));f.write(dense.tobytes());f.write(b'\x00')
 # 回读所有标准NBT与Sponge；按实际位置比较，不只检查文件存在。
 loaded=nbtlib.load(nbt);assert list(map(int,loaded['size']))==[w,h,d]
 assert len(loaded['blocks'])==len(data['blocks'])
 for expected,saved in zip(data['blocks'],loaded['blocks']):
  assert list(map(int,saved['pos']))==expected['pos'] and int(saved['state'])==ids[expected['state']]
 for expected,saved in zip(states,loaded['palette']):
  assert str(saved['Name'])==expected.split('[')[0]
  props=dict(__import__('re').findall(r'(\w+)=([^,\]]+)',expected))
  assert {str(k):str(v) for k,v in saved.get('Properties',{}).items()}==props
 del loaded
 loaded=nbtlib.load(schem);assert int(loaded['Version'])==2 and int(loaded['DataVersion'])==3465
 assert [int(loaded[k]) for k in ('Width','Height','Length')]==[w,h,d]
 assert {str(k):int(v) for k,v in loaded['Palette'].items()}=={'minecraft:air':0,**{s:i+1 for s,i in ids.items()}}
 assert np.array_equal(np.asarray(loaded['BlockData']).view(np.uint8),dense)
 del loaded,dense
 return states,groups,{'nbt':hashlib.sha256(nbt.read_bytes()).hexdigest(),'schem':hashlib.sha256(schem.read_bytes()).hexdigest()}

def render(data,materials,out,round_spheres=False):
 # 复用已经校正方向的逐面贴图投影；大尺寸限制画布，避免十万像素级图片。
 module=ROOT/'tools/structure_delivery/package_l1_review89.py'
 source=module.read_text(encoding='utf-8').split('def render_iso(data,materials,out):',1)[1].split('\ndef main(',1)[0]
 source='def render_iso(data,materials,out):'+source
 projection = "sy=scale/2;sz=scale"
 if round_spheres:
  projection = "sy=scale*0.57735;sz=scale*1.1547"
 source=source.replace('scale=16;sy=8;sz=16',"scale=min(12,1900/(data['size'][0]+data['size'][2]));"+projection)
 scope={};exec('from PIL import Image,ImageDraw,ImageEnhance\nimport io,base64\n'+source,scope)
 return scope['render_iso'](data,materials,out)

def main():
 OUT.mkdir(parents=True,exist_ok=True);LOG.mkdir(parents=True,exist_ok=True)
 briefs=json.loads((ROOT/'logs/structure-redesign-20260928/briefs69.json').read_text(encoding='utf-8'))['briefs']
 selected=set(s for s in sys.argv[1:] if not s.startswith('--'));briefs=[b for b in briefs if not selected or b['id'] in selected]
 catalog=json.loads((ROOT/'logs/research-labs-preview-20260928/material-expansion/catalog.json').read_text(encoding='utf-8'))
 mats={x['state']:x['material'] for x in catalog['accepted'] if x['dual_static']}
 r=Resources();other=Resources(Path.home()/'AppData/Roaming/PrismLauncher/instances/GregTech Leisure-增强版「巨构时代」 2.1/minecraft')
 for s in sorted(set(P.values())):
  if s not in mats:mats[s]=r.material(s);other.material(s)
 r.close();other.close()
 for brief in briefs:
  key=brief['id'].lower();out=OUT/key;out.mkdir(exist_ok=True)
  if (out/'complete.json').exists() and '--refresh' not in sys.argv:print(key,'已有完成产物，跳过',flush=True);continue
  data=build(brief);sizeaudit=require(data);used=sorted({b['state'] for b in data['blocks']})
  assert all(s in mats for s in used),[s for s in used if s not in mats]
  palette=collections.Counter(b['state'] for b in data['blocks']);materials=[mats[s] for s in used]
  states,groups,hashes=export(data,out)
  # 验证统一地面、居中控制器、白框面板、全部17个接口及其前方。
  occupied={tuple(b['pos']):b['state'] for b in data['blocks']};c=data['controller'][0]
  assert c==data['size'][0]//2 and occupied[tuple(data['controller'])]==P['controller']
  assert all(s==P['floor'] for (x,y,z),s in occupied.items() if y==0)
  for port in data['ports']:
   x,y,z=port['pos'];assert occupied[(x,y,z)]==P['port'] and (x,y,z-1) not in occupied
  for x in range(c-5,c+6):
   for y in range(1,5):
    if x in (c-5,c+5) or y in (1,4):assert occupied[(x,y,1)]==P['frame']
  namespace=collections.Counter()
  for s,count in palette.items():namespace[s.split(':')[0]]+=count
  audit={'time':datetime.datetime.now().astimezone().isoformat(),'palette':dict(palette),'namespace_counts':dict(namespace),'size_baseline':sizeaudit,'hashes':hashes,
   'checks':['逐轴尺寸及实际方块范围达到69座总表下限','NBT和Sponge回读：尺寸、全部位置与方块状态一致','实际使用材质来自双包静态模型解析库','主控中轴、白框内部17个接口候选、接口前方无遮挡','地板统一白色；低位中央主道3宽4高，生成时预留'],
   'not_verified':['未接入正式Pattern、注册端口能力或工艺配方','未进行游戏成型与运行测试','未进行浏览器交互实测','材质首帧，不完整模拟动态染色、游戏光照或资源包覆盖','分区与连接是建筑表达，不证明机器功能已经实现']}
  # 几何邻接统计仅记录，不把相连误当工艺合理或场约束成立。
  touches=sum(any((p[0]+dx,p[1]+dy,p[2]+dz) in occupied for dx,dy,dz in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))) for p in occupied)
  audit['blocks_with_neighbor']=touches;audit['isolated_blocks']=len(occupied)-touches
  del occupied
  meta={k:v for k,v in data.items() if k!='blocks'}
  meta['construction_notes']={'orientation':'主控正面朝-Z；坐标X从左到右，Z从前到后，Y自底部向上。','support':'各设备由支脚或场柱连接白色基础；内部设备与外部维护空间分开。','routing':'分区坐标和连接折点见下表，可在三维页显示标签与通道。','materials':'本机逐种用量与角色在材料清单中列出；钻石主控与接口标记单列，不计普通建材。','approval':'本轮实体草稿，待用户审阅。建筑命名、功能与正式成型不得由预览擅自定案。'}
  (out/'设计与检查.json').write_text(json.dumps({'data':meta,'audit':audit},ensure_ascii=False,indent=2),encoding='utf-8')
  payload={'data':meta,'palette':states,'groups':groups,'materials':materials,'audit':audit,'names':{}}
  encoded=base64.b64encode(gzip.compress(json.dumps(payload,ensure_ascii=False,separators=(',',':')).encode('utf-8'),compresslevel=9)).decode('ascii')
  (out/'data.js').write_text('/* 完整逐格数据；按需解压，仅当前机器加载。 */\nwindow.HK3_PAYLOAD='+json.dumps(encoded)+';',encoding='utf-8')
  del groups,payload,encoded
  im=render(data,materials,out)
  entry={k:data[k] for k in ('key','name','title','size','description')};entry.update(blocks=len(data['blocks']),materials=len(used),zones=len(data['zones']),size_passed=True)
  (out/'complete.json').write_text(json.dumps(entry,ensure_ascii=False,indent=2),encoding='utf-8')
  print(key,entry['blocks'],'方块',len(used),'材质',len(data['zones']),'分区',flush=True)
  del data,im
 entries=[json.loads(p.read_text(encoding='utf-8')) for p in sorted(OUT.glob('*/complete.json'))]
 (OUT/'manifest.json').write_text(json.dumps(entries,ensure_ascii=False,indent=2),encoding='utf-8')
 print('完成',len(entries),flush=True)
if __name__=='__main__':main()
