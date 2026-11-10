import json,re
from pathlib import Path
# Change #2 2026-09-24 00:09:00 revision63: preserve the draft below, delegate the entry point.
# 入口统一至审核蓝图生成器，避免旧层序与能源仓要求重新覆盖修正结果。
if __name__ == '__main__':
    import runpy
    runpy.run_path(str(Path(__file__).with_name('generate_approved_structures.py')), run_name='__main__')
    raise SystemExit(0)
p=Path('doc/HK3GTL-内测5/03_机器结构/I02结构审核_v1/blueprint.json')
data=json.loads(p.read_text(encoding='utf-8'))
W,H,D=data['size']
blocks={tuple(b['pos']):b['block'] for b in data['blocks']}
def bid(s): return s.split('[',1)[0]
ids=[]
for v in blocks.values():
    x=bid(v)
    if x not in ids: ids.append(x)
print(W,H,D,len(ids),ids)
# symbols from project pool
pool=list('ABCDEFGIJKLMNOPQRTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@$%&+')
reserved=set('SH#')
syms=[c for c in pool if c not in reserved]
mp=dict(zip(ids,syms))
print(mp)
controller=tuple(data['ports']['controller']); hatches={tuple(data['ports']['input']),tuple(data['ports']['output']),*(tuple(x) for x in data['ports']['rearServices'])}
grid=[]
for z in range(D):
  rows=[]
  for y in range(H):
    row=''
    for x in range(W):
      pos=(x,y,z)
      if pos==controller: ch='S'
      elif pos in hatches: ch='H'
      elif pos in blocks: ch=mp[bid(blocks[pos])]
      else: ch='#'
      row+=ch
    rows.append(row)
  grid.append(rows)
assert all(len(r)==W for a in grid for r in a)
print('controller char',grid[controller[2]][controller[1]][controller[0]])
print('hatches',[(q,grid[q[2]][q[1]][q[0]]) for q in hatches])
# generate source
imports=['com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition','com.gregtechceu.gtceu.api.pattern.BlockPattern','com.gregtechceu.gtceu.api.pattern.FactoryBlockPattern','com.gregtechceu.gtceu.api.pattern.Predicates','net.minecraft.core.registries.BuiltInRegistries','net.minecraft.resources.ResourceLocation']
out=['package com.sirin.hk3gtl.common.multiblock.pattern;','',*['import '+i+';' for i in imports],'', '/**',' * I02 样本光谱分析阵列的 GTCEu Pattern。',' * I02 sample-spectrum analysis array GTCEu Pattern.',' *',' * 尺寸 / Size: 17 x 17 x 21 (X x Y x Z).',' * 审核通过的建筑蓝图转换为逐方块类型匹配；控制器、仓位采用能力谓词。',' * The approved blueprint is converted into block-type predicates; controller and hatch positions use ability predicates.',' */','public final class Hk3I02SpectrumPatternImpl {','    private Hk3I02SpectrumPatternImpl() {}','', '    public static BlockPattern createPattern(MultiblockMachineDefinition definition) {','        return FactoryBlockPattern.start()']
for z in range(D):
  out.append('                .aisle(')
  for yi,y in enumerate(range(H-1,-1,-1)):
    comma=',' if yi < H-1 else ''
    out.append('                        "'+grid[z][y]+'"'+comma)
  out.append('                )')
out += ["                .where('S', Predicates.controller(Predicates.blocks(definition.getBlock())))", "                .where('H', Predicates.autoAbilities(definition.getRecipeTypes())", "                        .or(Predicates.autoAbilities(true, false, false)))", "                .where('#', Predicates.air())"]
for id,ch in mp.items():
  ns,path=id.split(':',1)
  out.append(f'                .where(\'{ch}\', Predicates.blocks(BuiltInRegistries.BLOCK.get(new ResourceLocation("{ns}", "{path}"))))')
out += ['                .build();','    }','}','']
Path('src/main/java/com/sirin/hk3gtl/common/multiblock/pattern/Hk3I02SpectrumPatternImpl.java').write_text('\n'.join(out),encoding='utf-8')
fac='''package com.sirin.hk3gtl.common.multiblock.pattern;\n\n/**\n * I02 样本光谱分析阵列 Pattern 门面。\n * I02 sample-spectrum analysis array Pattern facade.\n */\npublic final class Hk3I02SpectrumPattern extends Hk3I02SpectrumPatternImpl {\n    private Hk3I02SpectrumPattern() {}\n}\n'''
# change impl final/private to allow facade
s=Path('src/main/java/com/sirin/hk3gtl/common/multiblock/pattern/Hk3I02SpectrumPatternImpl.java').read_text(encoding='utf-8').replace('public final class Hk3I02SpectrumPatternImpl','public class Hk3I02SpectrumPatternImpl').replace('    private Hk3I02SpectrumPatternImpl() {}','    protected Hk3I02SpectrumPatternImpl() {}')
Path('src/main/java/com/sirin/hk3gtl/common/multiblock/pattern/Hk3I02SpectrumPatternImpl.java').write_text(s,encoding='utf-8')
Path('src/main/java/com/sirin/hk3gtl/common/multiblock/pattern/Hk3I02SpectrumPattern.java').write_text(fac,encoding='utf-8')
Path('doc/HK3GTL-内测5/03_机器结构/I02结构审核_v1/i02-pattern-legend.json').write_text(json.dumps({'size':data['size'],'blocks':mp,'controller':data['ports']['controller'],'hatches':list(hatches),'air':'#'},ensure_ascii=False,indent=2),encoding='utf-8')
