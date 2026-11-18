import base64
import gzip
import json
from pathlib import Path
import shutil

from package_0005_w12_author_blueprint_20261116 import digest, save


ROOT = Path(__file__).resolve().parents[2]
OLD = ROOT / 'deliveries/0005_W12_三环分层扩腔_A2_20261116'
OUT = ROOT / 'deliveries/0005_W12_三环翻转_A3_20261116'
LOG = ROOT / 'logs/0005-w12-flip-a3-20261116'
AXES = ([0, 1, 0], [0, 0, 1], [1, 0, 0])
NORMALS = ([1, 0, 0], [0, 1, 0], [0, 0, 1])
OUT.mkdir(parents=True, exist_ok=True)
(OUT / '生成脚本').mkdir(exist_ok=True)
LOG.mkdir(parents=True, exist_ok=True)
payload = json.loads((OLD / 'data.js').read_text('utf8').split('=', 1)[1].rstrip(';\n'))
config = json.loads(gzip.decompress(base64.b64decode(payload)))
geometry = json.loads((OLD / 'geometry.json').read_text('utf8'))
motions = []
for index, (axis, normal) in enumerate(zip(AXES, NORMALS), 1):
    name = f'core_gyroscope_{index}'
    metadata = geometry['components'][name]['metadata']
    metadata.update(motion_axis=axis, ring_normal=normal, motion_kind='绕球心直径翻转')
    next(part for part in config['parts'] if part['id'] == name)['metadata'] = metadata
    motions.append(dict(component=name, center=metadata['pivot'], normal_at_zero=normal,
        flip_axis=axis, angular_speed=metadata['motion_speed']))
config['data']['candidate'] = 'A3'
geometry.update(candidate='A3', stage='三环绕球心翻转预览待审',
    parent_candidate=str(OLD.relative_to(ROOT)), coordinate_geometry_changed=False,
    changed_components=[item['component'] for item in motions])
geometry['source_notes'] = ['三环分别绕穿过共同球心的Y、Z、X直径轴翻转，环面初始法线为X、Y、Z，转速沿用A2；无环内自转叠加。',
    '静态方块坐标、材质、25/36/47半径及110格名义空腔沿用A2。径向球壳证明适用于围绕共同球心的任意旋转，连续净空下界沿用A2。'] + geometry['source_notes'][1:]
encoded = base64.b64encode(gzip.compress(json.dumps(config, ensure_ascii=False, separators=(',', ':')).encode(), compresslevel=6)).decode()
(OUT / 'data.js').write_text('window.W12_STATIC_PAYLOAD=' + json.dumps(encoded) + ';\n', 'utf8')
save(OUT / 'geometry.json', geometry)
save(OUT / 'motion.json', dict(candidate='A3', formula='q_i(t)=axisAngle(flip_axis_i,angular_speed_i*flow)，flow在工作态为时间的1.8倍。', rings=motions))
for name in ('materials.json', 'style.css', '原文.txt', '修订构件数据.npz'):
    shutil.copy2(OLD / name, OUT / name)
shutil.copy2(OLD / 'W12-全域能量约束壁-A2.nbt', OUT / 'W12-全域能量约束壁-A3.nbt')
shutil.copy2(OLD / '生成脚本/effects.mjs', OUT / '生成脚本/effects.mjs')
source = (OLD / '生成脚本/viewer.mjs').read_text('utf8').replace('全域能量约束壁-A2.png', '全域能量约束壁-A3.png')
source = source.replace('speed:part.metadata.motion_speed,id:part.id,', 'speed:part.metadata.motion_speed,normal:new THREE.Vector3(...(part.metadata.ring_normal||part.metadata.motion_axis)).normalize(),id:part.id,')
source = source.replace('motions.map(({id,pivot,axis,speed})=>({id,speed,quaternion:pivot.quaternion.toArray(),normal:axis.clone().applyQuaternion(pivot.quaternion).toArray()}))', 'motions.map(({id,pivot,axis,speed,normal})=>({id,speed,axis:axis.toArray(),quaternion:pivot.quaternion.toArray(),normal:normal.clone().applyQuaternion(pivot.quaternion).toArray()}))')
source = source.replace("setScene('all');setTime(0);window.W12_STATIC_READY=true;", "setScene('core');setView('core');setTime(0);window.W12_STATIC_READY=true;")
(OUT / '生成脚本/viewer.mjs').write_text(source, 'utf8')
html = (OLD / 'index.html').read_text('utf8').replace('A2', 'A3').replace('LAYERED RINGS', 'FLIPPING RINGS').replace('三环分层 A3', '三环翻转 A3')
html = html.replace('三环半径25／36／47格，核心名义球腔直径110格。', '三环绕球心直径轴持续翻转，环面朝向随时间改变。半径25／36／47格，核心名义球腔直径110格。')
html = html.replace('实体锁链逐节穿扣，独立分组可隐藏', '三环绕球心翻转，可暂停并拖动时间查看')
html = html.replace('旋转陀螺环与奇点使用参考姿态导出', '翻转三环与奇点使用零秒姿态导出')
html = html.replace('<a href="changes.json">本版修改</a>', '<a href="motion.json">三环翻转参数</a>')
(OUT / 'index.html').write_text(html, 'utf8')
clearance = json.loads((OLD / 'continuous-clearance.json').read_text('utf8'))
clearance.update(candidate='W12 A3', inherited_geometry_from=str(OLD.relative_to(ROOT)),
    motion_change='三环转轴改为各自环面内的直径轴，全部旋转仍围绕原共同球心；所有球壳半径保持。',
    source={str((OUT / name).relative_to(ROOT)).replace('\\', '/'): dict(bytes=(OUT / name).stat().st_size,
        sha256=digest(OUT / name)) for name in ('geometry.json', '修订构件数据.npz')})
save(OUT / 'continuous-clearance.json', clearance)
save(LOG / 'continuous-clearance.json', clearance)
capture = (OLD / '生成脚本/capture.mjs').read_text('utf8').replace(OLD.name, OUT.name)
start = capture.index('const views=[')
end = capture.index('\nfor(const pose', start)
capture = capture[:start] + '''const views=[
  {scene:'core',view:'coreClose',effects:false,time:0,file:'核心翻转_00秒.png'},
  {scene:'core',view:'coreClose',effects:false,time:15,file:'核心翻转_15秒.png'},
  {scene:'core',view:'coreClose',effects:false,time:30,file:'核心翻转_30秒.png'},
  {scene:'core',view:'coreClose',effects:false,time:60,file:'核心翻转_60秒.png'},
  {scene:'all',view:'coreClose',effects:false,time:30,file:'核心与邻件_30秒.png'},
  {scene:'core',view:'core',mode:'work',time:18,file:'核心翻转_工作18秒.png'},
  {scene:'all',view:'front',effects:false,file:'整体_前斜视.png'},
];''' + capture[end:]
(OUT / '生成脚本/capture.mjs').write_text(capture, 'utf8')
shutil.copy2(Path(__file__), OUT / '生成脚本' / Path(__file__).name)
print(json.dumps(dict(candidate='A3', motion=motions, blocks=geometry['blocks'])))
