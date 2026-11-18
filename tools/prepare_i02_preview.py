# -*- coding: utf-8 -*-
"""Change #1 2026-09-23: I02 local textured Lodestone preview and review artifacts.
只在本机复用已安装模组的贴图；NBT保留模组ID，不把浏览器资源适配当作注册或许可授权。
"""
from pathlib import Path
from datetime import datetime
from PIL import Image
import json,zipfile,shutil,io,hashlib
root=Path(__file__).resolve().parents[1]
skill=Path('C:/Users/OWNER/.codex/skills/minecraft-builder-skill')
out=root/'doc/HK3GTL-内测5/03_机器结构/I02结构审核_v1'
viewer=out/'viewer'
shutil.copytree(skill/'assets/viewer',viewer,dirs_exist_ok=True)
pack=viewer/'public/pack'
shutil.copytree(skill/'node_modules/@mattzh72/lodestone/assets/default-pack',pack,dirs_exist_ok=True)
for name in ['LICENSE','LICENSE.md','LICENSE.txt']:
    if (skill/name).exists():shutil.copy2(skill/name,out/('skill-'+name))
jar=Path('C:/Users/OWNER/AppData/Roaming/PrismLauncher/instances/GregTech-Leisure-1.4.5.2/minecraft/mods/gtceu-1.20.1-1.4.4.jar')
z=zipfile.ZipFile(jar)
assets=json.loads((pack/'assets.json').read_text())
atlas=Image.open(pack/'atlas.png').convert('RGBA')
mapping={'gtceu:clean_machine_casing':'white_concrete','gtceu:solid_machine_casing':'gray_concrete',
         'gtceu:steel_pipe_casing':'orange_concrete','gtceu:tempered_glass':'light_blue_stained_glass',
         'gtceu:yellow_stripes_block_a':'yellow_concrete'}
evidence=[]
blueprint=json.loads((out/'blueprint.json').read_text(encoding='utf-8'))
actual_ids={cell['block'].split('[')[0] for cell in blueprint['blocks']}
assert not actual_ids.intersection('minecraft:'+v for v in mapping.values()), 'Preview alias collides with an actual vanilla block'
assert all(i.startswith('minecraft:') or i in mapping for i in actual_ids), 'Unmapped mod block would be invisible'
for block,proxy in mapping.items():
    name=block.split(':')[1]
    state=json.loads(z.read('assets/gtceu/blockstates/'+name+'.json'))
    model=json.loads(z.read('assets/gtceu/models/block/'+name+'.json'))
    textures={}
    for face,texture in model['textures'].items():
        # Distinct unused vanilla atlas cells retain the steel casing's three actual face textures.
        # 钢机壳顶底侧各用不同图集格，保持原模型面向，不以单一侧面冒充整块贴图。
        slot=('black_concrete' if face=='top' else 'brown_concrete' if face=='bottom' else proxy)
        key='block/'+slot
        x,y,w,h=assets['textures'][key]
        texture_path='assets/'+texture.replace(':','/textures/')+'.png'
        image=Image.open(io.BytesIO(z.read(texture_path))).convert('RGBA')
        image=image.crop((0,0,image.width,image.width)).resize((w,h),Image.Resampling.NEAREST)
        atlas.paste(image,(x,y))
        textures[face]='minecraft:'+key
    assets['models']['block/'+proxy]={'parent':model['parent'],'textures':textures}
    evidence.append({'id':block,'jar':jar.name,'model':state,'textures':model['textures'],'previewAlias':'minecraft:'+proxy})
atlas.save(pack/'atlas.png')
(pack/'assets.json').write_text(json.dumps(assets,separators=(',',':')),encoding='utf-8')
(out/'palette-sources.json').write_text(json.dumps({'jarSHA256':hashlib.sha256(jar.read_bytes()).hexdigest(),
    'note':'Local preview only. Actual IDs remain in NBT. Forge connected textures and lighting can differ.',
    'blocks':evidence},ensure_ascii=False,indent=2),encoding='utf-8')
s=(viewer/'src/main.js').read_text(encoding='utf-8')
s=s.replace('NbtFile, Structure,','Identifier, NbtFile, Structure,')
s=s.replace('    intensity: 1.15,', '    color: [1,1,1], ambientColor: [0.85,0.91,1], fillColor: [0.8,0.9,1], rimColor: [0.9,0.95,1],\n    emissive: {range:3,intensity:0.12,tint:[0.8,0.95,1]},\n    intensity: 0.65,')
s=s.replace('    exposure: 1.08,','    exposure: 0.85,')
s=s.replace("'/__minecraft_builder__/default-pack/'","'/pack/'")
s=s.replace('  const renderer = new ThreeStructureRenderer(canvas, structure, pack.resources, {', '''  // Change #3: local GTCEu atlas adapter. Preserve actual NBT IDs; remap definitions and flags only.
  // 本地模组材质适配：结构ID不变，仅将方块定义与透明属性导向已贴真实贴图的预览模型。
  const aliases = '''+json.dumps({k:'minecraft:'+v for k,v in mapping.items()})+''';
  const remap = id => Identifier.parse(aliases[id.toString()] ?? id.toString());
  const resources = {...pack.resources,
    getBlockDefinition: id => pack.resources.getBlockDefinition(remap(id)),
    getBlockFlags: id => pack.resources.getBlockFlags(remap(id)),
    getBlockProperties: id => pack.resources.getBlockProperties(remap(id)),
    getDefaultBlockProperties: id => pack.resources.getDefaultBlockProperties(remap(id)),
  };
  const renderer = new ThreeStructureRenderer(canvas, structure, resources, {''')
# StructureProvider filtering keeps original block states and NBT; only the rendered slice changes.
# 截层只过滤显示方块，不改原结构；尺寸、状态与NBT仍来自原件。
s=s.replace('  resize(renderer, canvas);','  resize(renderer, canvas);')
s=s.replace('  resize(renderer, canvas)\n', '''  const slice=document.getElementById('slice');
  let sliceRevision=0;
  slice.oninput=async () => {
    const revision=++sliceRevision, limit=Number(slice.value);
    document.getElementById('slice-label').textContent=limit===16?'完整建筑':'显示至 Y'+limit;
    renderer.setStructure({getSize:()=>size,
      getBlocks:()=>structure.getBlocks().filter(block=>block.pos[1]<=limit),
      getBlock:pos=>pos[1]<=limit?structure.getBlock(pos):null});
    await renderer.whenReady(); if(revision===sliceRevision)requestRender();
  };
  for(const [id,rot] of Object.entries({front:Math.PI,back:0,side:Math.PI/2,top:0.8}))
    document.getElementById('view-'+id).onclick=()=>{camera.yRotation=rot;camera.xRotation=id==='top'?1.48:0.38;requestRender();};
  window.hk3Preview={structure,renderer,camera,resources,ready:false};
  resize(renderer, canvas)
''')
s=s.replace("  loading.classList.add('hidden')", """  loading.classList.add('hidden'); window.hk3Preview.ready=true;
  const initialView=new URLSearchParams(location.search).get('view');
  if(['front','back','side','top'].includes(initialView))document.getElementById('view-'+initialView).click();
  const initialLayer=new URLSearchParams(location.search).get('layer');
  if(initialLayer!==null && Number(initialLayer)>=0 && Number(initialLayer)<=16){slice.value=initialLayer;await slice.oninput();}
""")
(viewer/'src/main.js').write_text(s,encoding='utf-8')
s=(viewer/'index.html').read_text(encoding='utf-8')
s=s.replace('<title>HK3GTL 结构预览</title>','<title>I02 样本光谱分析阵列 · 完整建筑审核</title>')
s=s.replace('<strong id="build-name">', '<label><span id="slice-label">完整建筑</span><input id="slice" type="range" min="0" max="16" value="16"></label><strong id="build-name">')
s=s.replace('<button id="zoom-in"', '<button id="view-front" class="icon-button">正面</button><button id="view-back" class="icon-button">背面</button><button id="view-side" class="icon-button">侧面</button><button id="view-top" class="icon-button">俯视</button><button id="zoom-in"')
s=s.replace('奇观当前是尺寸占位稿，尚未完成独特造型设计。','本页只有I02完整建筑审核稿；尚未注册运行控制器。<br>模组机壳使用实例内真实贴图；连接玻璃和光照以游戏为准。<br>左上滑块可移除上层，检查内部和通道。')
(viewer/'index.html').write_text(s,encoding='utf-8')

# A portable datapack contains the actual NBT but no load/tick commands or automatic world writes.
# 数据包只含真实NBT，不含自动执行入口；不安装或修改用户世界。
data=out/'i02-review-datapack'
(data/'data/hk3gtl_review/structures').mkdir(parents=True,exist_ok=True)
(data/'pack.mcmeta').write_text(json.dumps({'pack':{'pack_format':15,'description':'I02 architectural review only; no automatic placement'}}),encoding='utf-8')
shutil.copy2(out/'i02-spectrum-array-v1.nbt',data/'data/hk3gtl_review/structures/i02_spectrum_array.nbt')
shutil.make_archive(str(out/'i02-review-datapack'),'zip',data)
print('Prepared actual-texture local preview and non-automatic NBT datapack.')
