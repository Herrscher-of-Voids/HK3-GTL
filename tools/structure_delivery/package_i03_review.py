# -*- coding: utf-8 -*-
"""打包 I03 建筑评审样例与本地材质证据，不修改游戏代码、配方或存档。

输入为确定性的逐格 JSON 和指定实例资源；输出 Sponge v2、材质、验收清单。
坐标单位为方块，顺序为 X/Y/Z。失败立即中止，禁止缺失资源静默换成原版。
"""
from pathlib import Path
import base64
import collections
import gzip
import hashlib
import io
import json
import os
import re
import zipfile
import nbtlib as nbt
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(os.environ.get('HK3_REVIEW_OUT', str(ROOT / 'doc/HK3GTL-内测5/03_机器结构/I03分馏中心实物样例_v1')))
INSTANCE = Path.home() / 'AppData/Roaming/PrismLauncher/instances/GregTech-Leisure-1.4.5.2/minecraft'
CLIENT = Path.home() / 'AppData/Roaming/PrismLauncher/libraries/com/mojang/minecraft/1.20.1/minecraft-1.20.1-client.jar'
NAME = os.environ.get('HK3_REVIEW_NAME', 'hk3gtl-i03-fractionation-review-v1')
FACES = ['east', 'west', 'up', 'down', 'south', 'north']


# 变更 #1 2026-09-25 04:25:06 修订72: 统一材质解析
from material_resources import Resources


def write_sponge(data):
    """Sponge v2 按 Y/Z/X 顺序遍历，空气固定索引零，压缩等级九。"""
    w,h,d = data['size']
    palette = ['minecraft:air'] + sorted({b['state'] for b in data['blocks']})
    indices = {v:i for i,v in enumerate(palette)}
    dense = [0] * (w*h*d)
    for b in data['blocks']:
        x,y,z = b['pos']; dense[(y*d+z)*w+x] = indices[b['state']]
    encoded = []
    for value in dense:
        while value > 127:
            encoded.append((value & 127) | 128); value >>= 7
        encoded.append(value)
    root = nbt.File({
        'Version': nbt.Int(2), 'DataVersion': nbt.Int(3465),
        'Width': nbt.Short(w), 'Height': nbt.Short(h), 'Length': nbt.Short(d),
        'Offset': nbt.IntArray([0,0,0]),
        'PaletteMax': nbt.Int(len(palette)),
        'Palette': nbt.Compound({k:nbt.Int(v) for k,v in indices.items()}),
        'BlockData': nbt.ByteArray([v if v<128 else v-256 for v in encoded]),
        'BlockEntities': nbt.List[nbt.Compound]([]),
        'Metadata': nbt.Compound({'Name': nbt.String(data.get('title','I03 分馏中心')+' · 建筑评审样例'),
                                'Author': nbt.String('HK3GTL')})
    }, root_name='Schematic')
    stream=io.BytesIO(); root.write(stream)
    path = OUT / (NAME + '.schem')
    path.write_bytes(gzip.compress(stream.getvalue(), compresslevel=9, mtime=0))
    decoded = nbt.load(path)
    assert decoded.root_name == 'Schematic' and int(decoded['Version'])==2
    values=[]; value=shift=0
    for signed in decoded['BlockData']:
        byte=int(signed)&255;value|=(byte&127)<<shift
        if byte&128:shift+=7
        else:values.append(value);value=shift=0
    assert values==dense and len(values)==w*h*d
    return path, palette, dense


def validate_paths(data):
    """校验双向通道、端口访问面和从正面到各端口的两格高步行路线。"""
    occupied={tuple(b['pos']) for b in data['blocks']}
    for path in data['paths']:
        lo,hi=path['min'],path['max']
        assert all((x,y,z) not in occupied for x in range(lo[0],hi[0]+1) for y in range(lo[1],hi[1]+1) for z in range(lo[2],hi[2]+1)),path
    floor={(x,z) for x in range(data['size'][0]) for z in range(data['size'][2]) if (x,0,z) in occupied and (x,1,z) not in occupied and (x,2,z) not in occupied}
    reached={tuple(data.get('entrance',[16,0]))}; queue=collections.deque(reached)
    while queue:
        x,z=queue.popleft()
        for p in [(x-1,z),(x+1,z),(x,z-1),(x,z+1)]:
            if p in floor and p not in reached: reached.add(p);queue.append(p)
    delta={'west':(-1,0),'east':(1,0),'north':(0,-1),'south':(0,1)}
    for port in data['ports']:
        x,y,z=port['pos'];dx,dz=delta[port['face']]
        assert (x+dx,z+dz) in reached, ('接口不可步行到达',port)
    assert (data['controller'][0],data['controller'][2]-1) in reached, '主控前方不可达'
    return len(reached)


def collect_evidence(states):
    """扫描实例脚本与数据文件中的精确 ID，不把静态命中当作最终配方证明。"""
    blocks=[s.split('[')[0] for s in states if not s.startswith('minecraft:')]
    matches={b:[] for b in blocks}
    files=[]
    for base in [INSTANCE/'kubejs', INSTANCE/'config', INSTANCE/'datapacks']:
        if base.exists():files.extend(p for p in base.rglob('*') if p.is_file() and p.suffix in {'.js','.json','.json5','.toml'})
    for p in files:
        if p.stat().st_size>12_000_000:continue
        try:lines=p.read_text(encoding='utf-8').splitlines()
        except (UnicodeError,OSError):continue
        for i,line in enumerate(lines):
            for b in blocks:
                if b in line and len(matches[b])<24:matches[b].append({'file':str(p.relative_to(INSTANCE)),'line':i+1,'text':line.strip()[:650]})
    return {'scanned_files':len(files),'matches':matches,
        'status':'已核对静态资源、脚本引用与完整模型。未取得最终运行时配方导出；全部候选材料的递归前置和阶段可达性尚未完整验证。不得据此作为已验收的生存开线清单。'}


def main():
    data=json.loads((OUT/'blueprint.json').read_text(encoding='utf-8'))
    assert all(not b['state'].startswith('hk3gtl:') for b in data['blocks'])
    resources=Resources()
    states=sorted({b['state'] for b in data['blocks']})
    materials=[resources.material(s) for s in states]
    path,palette,dense=write_sponge(data)
    counts=collections.Counter(b['state'] for b in data['blocks'])
    assert counts['minecraft:diamond_block']==1 and counts['minecraft:diamond_ore']==len(data['ports'])
    vanilla=nbt.load(OUT/(NAME+'.nbt'))
    check={tuple(map(int,b['pos'])):str(vanilla['palette'][int(b['state'])]['Name'])+(
        '['+','.join(f'{k}={v}' for k,v in vanilla['palette'][int(b['state'])].get('Properties',{}).items())+']'
        if vanilla['palette'][int(b['state'])].get('Properties') else '') for b in vanilla['blocks']}
    assert check=={tuple(b['pos']):b['state'] for b in data['blocks']}, '原版结构与逐格定义不一致'
    report={'dimensions_xyz':data['size'],'footprint':data['size'][0]*data['size'][2],'non_air_blocks':len(data['blocks']),
        'palette':counts,'paths_accessible_cells':validate_paths(data),'ports':data['ports'],
        'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'checks':['Sponge v2 根标签、类型与体积正确','varint 全量回读一致','原版 NBT 与逐格数据一致','完整模型已逐项解析','无旧版 HK3GTL 材料','双向通道净空通过','全部接口及主控可由前入口步行到达'],
        'height_at_y_minus_60':[-60,-60+data['size'][1]-1],
        'not_verified':['尚未接入 Java Pattern，不代表机器可成型或运行','运行时配方与材料递归前置未完成','预览使用实际纹理首帧，未模拟游戏动态染色及光照'],
        'material_evidence':collect_evidence(states),'resource_sources':resources.sources}
    for name,obj in [('materials.json',materials),('audit.json',report)]:
        (OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ['dimensions_xyz','non_air_blocks','paths_accessible_cells','sha256','checks']},ensure_ascii=False))


if __name__=='__main__':main()
