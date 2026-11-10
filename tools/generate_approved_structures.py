"""变更记录 #1 · 2026-09-24 00:04:00 · 内测5修订63。
从审核蓝图生成逐格GT Pattern、带控制器NBT及原创16px面板；不修改存档。
Generate deterministic GT Patterns, controller-equipped NBT and original 16px panels.
坐标单位为方块，源为XYZ而占地表为XZY；未知ID由游戏注册表严格校验。
Coordinates are blocks: source XYZ versus atlas XZY. Runtime rejects unknown IDs.
"""
from pathlib import Path
import json, hashlib, gzip, io
import nbtlib as n
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / 'doc/HK3GTL-内测5/03_机器结构'
JAVA = ROOT / 'src/main/java/com/sirin/hk3gtl/common/multiblock/pattern'
RES = ROOT / 'src/main/resources'
SPECS = [
    dict(key='i01', atlas='I01-1', cls='Hk3I01CollectionPatternImpl', source=DOC/'游戏内验收/i01-layer-pack/blueprint-revision-01.json',
         controller=(8,2,14), front='south', axes='LEFT, UP, FRONT', machine='i01_honkai_collection_tower',
         ports={(6,1,15):('i','IMPORT_ITEMS','lv_input_bus'), (10,1,15):('o','EXPORT_FLUIDS','lv_output_hatch'),
                (7,1,15):('h','EXPORT_ITEMS','lv_output_bus')}),
    dict(key='i02', atlas='I02', cls='Hk3I02SpectrumPatternImpl', source=DOC/'I02结构审核_v1/blueprint.json',
         controller=(8,3,5), front='north', axes='RIGHT, UP, BACK', machine='i02_spectrum_analysis_array',
         ports={(4,3,2):('i','IMPORT_ITEMS','lv_input_bus'), (12,3,2):('o','EXPORT_ITEMS','lv_output_bus'),
                (4,3,19):('h','IMPORT_ITEMS','lv_input_bus'), (12,3,19):('k','EXPORT_ITEMS','lv_output_bus')})
]

def state_tag(value):
    """完整方块状态转NBT；不改变楼梯/活板门等审核状态。 / Preserve explicit architectural states in NBT."""
    block, _, props = value.partition('[')
    tag = n.Compound({'Name': n.String(block)})
    if props:
        tag['Properties'] = n.Compound({k:n.String(v) for k,v in (p.split('=') for p in props.rstrip(']').split(','))})
    return tag

def generate(spec, atlas):
    """生成单台结构；任何尺寸、重复坐标或接口错位均中止。 / Fail on dimensions, duplicates or misplaced ports."""
    raw=spec['source'].read_bytes(); data=json.loads(raw)
    w,h,d=data['size']; assert [w,d,h]==atlas[spec['atlas']]['size']
    blocks={tuple(b['pos']):b['block'] for b in data['blocks']}
    assert len(blocks)==len(data['blocks'])
    for x,y,z in blocks: assert 0<=x<w and 0<=y<h and 0<=z<d
    assert spec['controller'] in blocks and all(p in blocks for p in spec['ports'])
    ids=sorted({s.split('[')[0] for s in blocks.values()})
    symbols=dict(zip(ids,'ABCDEFGIJKLMNOPQRTUVWXYZ'))
    assert len(symbols)==len(ids)
    grid=[]
    for z in range(d):
        rows=[]
        for y in range(h):
            rows.append(''.join('S' if (x,y,z)==spec['controller'] else spec['ports'][x,y,z][0]
                if (x,y,z) in spec['ports'] else symbols[blocks[x,y,z].split('[')[0]] if (x,y,z) in blocks else '#'
                for x in range(w)))
        grid.append(rows)
    out=['package com.sirin.hk3gtl.common.multiblock.pattern;', '',
         'import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;',
         'import com.gregtechceu.gtceu.api.machine.multiblock.PartAbility;',
         'import com.gregtechceu.gtceu.api.pattern.BlockPattern;',
         'import com.gregtechceu.gtceu.api.pattern.FactoryBlockPattern;',
         'import com.gregtechceu.gtceu.api.pattern.Predicates;',
         'import static com.gregtechceu.gtceu.api.pattern.util.RelativeDirection.*;', '',
         '/**',
         ' * 【变更记录 #1】2026-09-24 00:04:00（内测5修订63）',
         ' * 删除：无历史建筑删除；旧草稿归档。新增：已审核逐格结构及专用接口。',
         ' * 修改：层序自底向上，明确相对方向；空气阻止堵塞通道，端口不要求能源仓。',
         ' * 用途：控制器匹配真实建筑；能源仍由绑定玩家无线电网结算。',
         ' * Preserve archived drafts; bind exact geometry, explicit axes and ports to owner-grid machines.',
         f' * 来源 / Source SHA256: {hashlib.sha256(raw).hexdigest()}',
         f' * 尺寸 / XYZ size in blocks: {w} x {h} x {d}; controller: {spec["controller"]}.',
         ' * 装饰按方块类型校验，朝向状态由NBT保留，允许玩家旋转整台建筑。',
         ' * Match decorative block types; the template preserves states and horizontal rotations remain valid.',
         ' */', f'public class {spec["cls"]} {{',f'    protected {spec["cls"]}() {{}}','',
         '    /** 参数为已注册控制器；返回固定尺寸Pattern，缺失材料立即报错。',
         '     * Registered definition in; fixed-size Pattern out. Missing blocks fail rather than becoming air. */',
         '    public static BlockPattern createPattern(MultiblockMachineDefinition definition) {',
         f'        return FactoryBlockPattern.start({spec["axes"]})']
    for rows in grid:
        out+=['                .aisle(' + ',\n                        '.join('"'+r+'"' for r in rows)+')']
    out+=["                .where('S', Predicates.controller(Predicates.blocks(definition.getBlock())))",
          "                .where('#', Predicates.air())"]
    for id,c in symbols.items():out.append(f'                .where(\'{c}\', Predicates.blocks(Hk3StructureBlocks.require("{id}")))')
    for pos,(c,ability,_) in spec['ports'].items():
        predicate=f'Predicates.abilities(PartAbility.{ability})'
        if c in 'hk':
            predicate=f'Predicates.blocks(Hk3StructureBlocks.require("{blocks[pos].split("[")[0]}"))\n                        .or({predicate}.setPreviewCount(0))'
        out.append(f'                .where(\'{c}\', {predicate})')
    out+=['                .build();','    }','}','']
    (JAVA/(spec['cls']+'.java')).write_text('\n'.join(out),encoding='utf8')
    placed=dict(blocks)
    placed[spec['controller']]='hk3gtl:'+spec['machine']+'[facing='+spec['front']+']'
    for pos,(_,_,id) in spec['ports'].items():placed[pos]='gtceu:'+id+'[facing='+spec['front']+']'
    # 全包围盒带空气，导入命令须先验空，避免残留方块挡住通道。
    # Include air throughout the bounds; the import command preflights an empty volume.
    palette=[];indices={};entries=[]
    for y in range(h):
        for z in range(d):
            for x in range(w):
                state=placed.get((x,y,z),'minecraft:air')
                if state not in indices:indices[state]=len(palette);palette.append(state_tag(state))
                entries.append(n.Compound({'pos':n.List[n.Int]([x,y,z]),'state':n.Int(indices[state])}))
    tag=n.File({'DataVersion':n.Int(3465),'size':n.List[n.Int]([w,h,d]),'palette':n.List[n.Compound](palette),
                'blocks':n.List[n.Compound](entries),'entities':n.List[n.Compound]([])})
    buf=io.BytesIO();tag.write(buf)
    dest=RES/'data/hk3gtl/structures/approved';dest.mkdir(parents=True,exist_ok=True)
    (dest/(spec['key']+'.nbt')).write_bytes(gzip.compress(buf.getvalue(),mtime=0))
    manifest=dict(id=spec['key'],size=[w,h,d],controller=spec['controller'],front=spec['front'],machine=spec['machine'],
                  source=str(spec['source'].relative_to(ROOT)),sha256=hashlib.sha256(raw).hexdigest(),
                  ports=[dict(pos=p,symbol=c,ability=a) for p,(c,a,_) in spec['ports'].items()],
                  blocks=len(blocks),legend={v:k for k,v in symbols.items()},aisles=grid)
    dest=RES/'data/hk3gtl/structures/approved';(dest/(spec['key']+'.json')).write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    # 原创雷达/光谱显示屏覆盖图，透明背景使用GT不锈钢机壳；不拷贝第三方图片。
    # Original radar/spectrum overlay on the GT casing, without copied external artwork.
    tex=RES/'assets/hk3gtl/textures/block/overlay'/spec['key'];tex.mkdir(parents=True,exist_ok=True)
    for suffix,color in [('', '#72d7db'),('_active','#acffff'),('_paused','#dda652')]:
        im=Image.new('RGBA',(16,16));draw=ImageDraw.Draw(im)
        draw.rectangle((2,2,13,13),fill='#303647',outline='#aab3bc');draw.rectangle((3,3,12,11),fill='#101d35')
        if spec['key']=='i01':
            draw.ellipse((4,3,11,10),outline=color);draw.line((7,7,10,4),fill=color);draw.point((5,6),fill='#deb8ff')
        else:
            for x,y in [(4,8),(5,5),(6,7),(7,4),(8,6),(9,9),(10,5),(11,7)]:draw.line((x,10,x,y),fill=color)
        draw.line((4,13,8,13),fill=color);draw.point((11,13),fill='#c4a0ef')
        im.save(tex/('overlay_front'+suffix+'.png'))
    print(spec['key'],data['size'],len(blocks),'blocks; source, Pattern and NBT generated')

if __name__=='__main__':
    page=next(DOC.glob('*69*v2.html')).read_text(encoding='utf8')
    atlas={r['id']:r for r in json.JSONDecoder().raw_decode(page.split('const machines=')[1])[0]}
    for spec in SPECS:generate(spec,atlas)
