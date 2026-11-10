"""Generate beta5 registrations and original 16px pixel art from the reviewed catalog.

Change #1 (2026-09-22, batch7): deterministic geometry, models, bilingual names,
block drops and registry manifest. Existing files are backed up once before editing.
Inputs: industrial_content_catalog.py. Outputs: Java, resources, HTML inventory and PNG sheet.
Never generates recipes, completed research evidence, machine Patterns or saved worlds.
"""
from pathlib import Path
from datetime import datetime
import json, hashlib, shutil, math, re, html
from PIL import Image, ImageDraw, ImageFont
from industrial_content_catalog import CATALOG

ROOT=Path(__file__).resolve().parents[1]
RES=ROOT/'src/main/resources'
JAVA=ROOT/'src/main/java/com/sirin/hk3gtl'
ART=RES/'assets/hk3gtl'
BACK=ROOT/'archive/beta5-batch7-before'
STAMP=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
CHANGED=[]
def save(path,content):
    path=Path(path); rel=path.relative_to(ROOT)
    if path.exists() and not (BACK/rel).exists():
        (BACK/rel).parent.mkdir(parents=True,exist_ok=True); shutil.copy2(path,BACK/rel)
    path.parent.mkdir(parents=True,exist_ok=True)
    if isinstance(content,bytes): path.write_bytes(content)
    else: path.write_text(content,encoding='utf-8')
    CHANGED.append(str(rel).replace('\\','/'))
def js(path,data): save(path,json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def note(n,what):
    return f'''/**
 * 【变更记录 #{n}】{STAMP}（内测5第7次代码更新 / Beta5 batch 7）
 * 删除：无，旧实现已备份。新增/修改：{what}。
 * 用途：补全物理内容注册与外观；不把持有物品视作研究或审判资格。
 * No deletion; backed up existing sources. Register physical content without granting progression.
 */
'''
def inject(path,old,new,what):
    s=path.read_text(encoding='utf-8')
    if new in s: return
    assert old in s,(path,old)
    s=s.replace(old,new,1)
    n=max([int(x) for x in re.findall(r'变更记录\s*#(\d+)',s)]+[1])+1
    at=s.index('public class ') if 'public class ' in s else s.index('public final class ')
    s=s[:at]+note(n,what)+s[at:]; save(path,s)

items=[r for r in CATALOG if r['kind']=='item' and not r.get('reuse')]
blocks=[r for r in CATALOG if r['kind']=='block']
fluids=[r for r in CATALOG if r['kind']=='fluid' and not r.get('reuse')]
head='package com.sirin.hk3gtl.common.registration;\n\n'
source=head+'''import com.sirin.hk3gtl.common.item.Hk3Items;
import com.sirin.hk3gtl.common.block.Hk3Blocks;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraftforge.registries.RegistryObject;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.Map;

'''+note(1,'新增内测5工业中间件、核心和结构材料，保持原ID不重复注册')+'''public final class Hk3IndustrialContent {
    // 注册线程写入，完成后只读；保持目录顺序，不允许调用方修改。
    // Registration-thread writes only; expose immutable views in deterministic catalog order.
    private static final Map<String, RegistryObject<Item>> ITEMS = new LinkedHashMap<>();
    private static final Map<String, RegistryObject<Block>> BLOCKS = new LinkedHashMap<>();
    private Hk3IndustrialContent() {}

    /** 注册真实物品，工具/核心/容器堆叠1，其余64；不产生任何解锁副作用。
     * Register physical items, stack limit 1 for tools/cores/containers, otherwise 64; no unlock effects.
     */
    public static void registerItems() {
'''
for r in items:
    stack=1 if r['family'] in ('detector','core','key','bubble') else 64
    source+=f'        item("{r["id"]}", {stack}); // {r["zh"]} / {r["en"]}; {r["source"]}\n'
source+='''    }

    /** 结构材料不是控制器，不含虚假成型或配方能力。硬度5，抗爆10。
     * Structural materials, not controllers; no fake formation or recipes. Hardness 5, resistance 10.
     */
    public static void registerBlocks() {
'''
for r in blocks: source+=f'        block("{r["id"]}"); // {r["zh"]} / {r["en"]}; {r["source"]}\n'
source+='''    }

    /** @param id 稳定路径 / stable registry path; @param stack 最大件数 / maximum stack count. */
    private static void item(String id, int stack) {
        if (ITEMS.containsKey(id)) throw new IllegalStateException("Duplicate industrial item: " + id);
        ITEMS.put(id, Hk3Items.ITEMS.register(id, () -> new Item(new Item.Properties().stacksTo(stack))));
    }
    /** @param id 方块与物品共用路径 / shared block and BlockItem registry path. */
    private static void block(String id) {
        if (BLOCKS.containsKey(id)) throw new IllegalStateException("Duplicate industrial block: " + id);
        BLOCKS.put(id, Hk3Blocks.registerBlock(id, () -> new Block(BlockBehaviour.Properties.of()
                .strength(5.0F, 10.0F).sound(SoundType.METAL).requiresCorrectToolForDrops())));
    }
    /** 返回只读物品索引，不提前解引用注册对象。 / Return an immutable index without resolving suppliers. */
    public static Map<String, RegistryObject<Item>> items() { return Collections.unmodifiableMap(ITEMS); }
    /** 返回只读方块索引。 / Return an immutable structural-block index. */
    public static Map<String, RegistryObject<Block>> blocks() { return Collections.unmodifiableMap(BLOCKS); }
}
'''
save(JAVA/'common/registration/Hk3IndustrialContent.java',source)
source=head+'''import com.gregtechceu.gtceu.api.data.chemical.material.Material;
import com.gregtechceu.gtceu.api.data.chemical.material.info.MaterialIconSet;
import com.gregtechceu.gtceu.api.fluids.FluidBuilder;
import com.gregtechceu.gtceu.api.fluids.FluidState;
import com.gregtechceu.gtceu.api.fluids.store.FluidStorageKeys;
import net.minecraft.resources.ResourceLocation;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.Map;

'''+note(1,'按GT材料事件注册独立工艺流体，专用静态与流动贴图，不注册能量账本为流体')+'''public final class Hk3IndustrialFluids {
    private static final Map<String, Material> MATERIALS = new LinkedHashMap<>();
    private Hk3IndustrialFluids() {}
    /** 仅在GT MaterialEvent调用一次，固定目录顺序；无自动工艺配方。
     * Called once during GT MaterialEvent, in fixed catalog order; no automatic processing recipes.
     */
    public static void register() {
'''
for r in fluids: source+=f'        add("{r["id"]}", {str(r["family"]=="gas").lower()}); // {r["zh"]} / {r["en"]}\n'
source+='''    }
    /** ID明确保持不加gas前缀；温度300K或热介质600K，纯展示属性，不表示配方平衡。
     * Explicit names avoid gas prefixes; 300 K, or 600 K for hot media. Properties do not define recipe balance.
     * @param id 稳定材料/流体ID / stable material and fluid ID
     * @param gas 是否使用气态存储 / whether gas storage is used
     */
    private static void add(String id, boolean gas) {
        if (MATERIALS.containsKey(id)) throw new IllegalStateException("Duplicate industrial fluid: " + id);
        FluidBuilder fluid = new FluidBuilder().name(id).translation("material.hk3gtl." + id)
                .textures(true, true).temperature(id.startsWith("hot_") ? 600 : 300)
                .state(gas ? FluidState.GAS : FluidState.LIQUID);
        Material material = new Material.Builder(new ResourceLocation("hk3gtl", id))
                .fluid(gas ? FluidStorageKeys.GAS : FluidStorageKeys.LIQUID, fluid)
                .color(0xB68CEC).iconSet(MaterialIconSet.FLUID).buildAndRegister();
        MATERIALS.put(id, material);
    }
    /** 只读物理流体索引；HKE账本不在此表。 / Read-only physical-fluid index; excludes HKE account state. */
    public static Map<String, Material> materials() { return Collections.unmodifiableMap(MATERIALS); }
}
'''
save(JAVA/'common/registration/Hk3IndustrialFluids.java',source)
inject(JAVA/'common/item/Hk3Items.java','        HonkaiMaterialItems.register();','        com.sirin.hk3gtl.common.registration.Hk3IndustrialContent.registerItems();\n        HonkaiMaterialItems.register();','接入内测5物品注册')
inject(JAVA/'common/block/Hk3Blocks.java','        CasingBlocks.register();','        com.sirin.hk3gtl.common.registration.Hk3IndustrialContent.registerBlocks();\n        CasingBlocks.register();','接入内测5结构方块注册')
inject(JAVA/'common/material/Hk3Materials.java','        SouliumMaterial.register();','        com.sirin.hk3gtl.common.registration.Hk3IndustrialFluids.register();\n        SouliumMaterial.register();','接入内测5工艺流体注册')
inject(JAVA/'common/material/Hk3Materials.java','                .fluid()','                .fluid(com.gregtechceu.gtceu.api.fluids.store.FluidStorageKeys.LIQUID,\n                        new com.gregtechceu.gtceu.api.fluids.FluidBuilder().textures(true, true))','为既有液态崩坏能绑定专用动态贴图')
# The creative tab previously excluded every registered block, including blocks absent from BLOCK_ORDER.
inject(JAVA/'common/registration/Hk3CreativeTabsImpl.java',
       '        Set<String> excludedPaths = collectExcludedItemPaths();',
       '        com.sirin.hk3gtl.common.registration.Hk3IndustrialContent.blocks().keySet().forEach(path -> addItem(items, path));\n        Set<String> excludedPaths = collectExcludedItemPaths();',
       '将新增结构材料加入创造页，避免被旧BLOCK_ORDER排除')
inject(JAVA/'common/bootstrap/Hk3ModHealthReport.java',
       '        int fluidCount = fluidsRegistered() ? 1 : 0;',
       '''        // 精确查询本批流体ID，气态不通过默认液体槽推测。 / Query exact IDs, including gases.
        int industrialFluidCount = (int) com.sirin.hk3gtl.common.registration.Hk3IndustrialFluids.materials().keySet().stream()
                .filter(id -> ForgeRegistries.FLUIDS.containsKey(new net.minecraft.resources.ResourceLocation("hk3gtl", id)))
                .count();
        int fluidCount = (fluidsRegistered() ? 1 : 0) + industrialFluidCount;''',
       '修复欢迎界面流体数量硬编码1，核对新增气液工艺流体')
inject(JAVA/'common/bootstrap/Hk3ModHealthReport.java',
       'boolean fluidsOk = fluidCount > 0 && isFluidRegistered(Hk3Materials.LIQUID_HONKAI_ENERGY);',
       '''boolean fluidsOk = isFluidRegistered(Hk3Materials.LIQUID_HONKAI_ENERGY)
                && industrialFluidCount == com.sirin.hk3gtl.common.registration.Hk3IndustrialFluids.materials().size()
                && industrialFluidCount > 0;''',
       '新增任一工艺流体缺失即自检失败，避免部分成功显示全绿')

def palette(r):
    digest=hashlib.sha256(r['id'].encode()).digest()
    colors=[(153,91,239),(56,175,223),(223,162,68),(75,208,179),(223,99,152),(132,163,226)]
    c=colors[digest[0]%len(colors)]
    return c,tuple(min(255,int(x*.5+125)) for x in c),tuple(int(x*.38) for x in c),digest
def texture(r):
    im=Image.new('RGBA',(16,16),(0,0,0,0)); d=ImageDraw.Draw(im)
    c,light,dark,h=palette(r); edge=(22,26,43); metal=(155,173,193); white=(234,240,250)
    f=r['family']; ident=r['id']
    if ident=='narrative_codex':
        d.rectangle((4,2,11,13),fill=(211,202,175)); d.rectangle((2,1,13,3),fill=metal)
        d.rectangle((2,12,13,14),fill=metal); d.line((6,5,10,5,10,9,6,9),fill=c)
        d.point((7,7),fill=dark)
    elif 'blueprint' in ident or 'mask' in ident or 'rule_carrier' in ident:
        d.rectangle((2,2,13,13),fill=(35,65,103),outline=metal)
        d.line((4,10,6,5,10,4,11,8,7,10,4,10),fill=light)
        d.line((4,12,10,12),fill=white)
    elif ('probe' in ident or 'drone' in ident) and 'scrap' not in ident:
        d.rectangle((5,5,10,10),fill=metal,outline=dark); d.rectangle((7,6,9,8),fill=c)
        for x,y in ((1,2),(11,2),(1,11),(11,11)):
            d.line((x+1,y+1,7,7),fill=metal); d.ellipse((x,y,x+3,y+2),outline=light)
        if 'worn' in ident: d.line((6,5,8,8,6,10),fill=edge)
    elif 'filter' in ident:
        d.rectangle((3,2,12,13),fill=metal,outline=edge)
        for y in range(4,12,2): d.line((5,y,10,y),fill=dark)
        d.rectangle((3,1,12,2),fill=c)
        if 'depleted' in ident: d.line((5,4,10,11),fill=(100,69,49),width=2)
    elif 'scrap' in ident or 'residue' in ident or 'swarf' in ident or 'offcut' in ident:
        for x,y in ((2,9),(6,5),(9,9),(5,11)):
            d.polygon([(x,y),(x+3,y-2),(x+4,y+2),(x+1,y+3)],fill=dark,outline=metal)
        d.point((8,6),fill=c)
    elif r['kind']=='block':
        d.rectangle((0,0,15,15),fill=edge); d.rectangle((1,1,14,14),fill=dark)
        d.line((1,14,1,1,14,1),fill=metal); d.line((14,1,14,14,1,14),fill=(52,61,80))
        if 'support' in ident or 'frame' in ident:
            d.line((3,3,12,12),fill=metal,width=3); d.line((12,3,3,12),fill=metal,width=3)
        elif 'interface' in ident or 'panel' in ident or 'array' in ident:
            d.rectangle((3,3,12,10),fill=edge)
            for y in (4,6,8): d.line((4,y,7+h[y]%5,y),fill=light)
            d.rectangle((4,12,5,12),fill=c); d.point((10,12),fill=white)
        elif 'core_mount' in ident or 'coil' in ident or 'ring' in ident:
            d.ellipse((2,2,13,13),outline=metal,width=2); d.ellipse((5,5,10,10),fill=c)
            d.rectangle((7,6,8,9),fill=light)
        elif 'nozzle' in ident or 'heat' in ident:
            for y in range(3,14,3): d.rectangle((3,y,12,y+1),fill=metal)
        else:
            d.polygon([(3,4),(8,2),(12,5),(12,11),(7,13),(3,10)],outline=c)
            d.line((5,6,10,6,10,9,5,9),fill=light)
        for x,y in [(2,2),(13,2),(2,13),(13,13)]: d.point((x,y),fill=white)
    elif f=='detector':
        d.rectangle((4,5,11,14),fill=edge); d.rectangle((5,6,10,13),fill=metal)
        d.rectangle((6,7,9,10),fill=dark); d.line((6,9,7,8,8,9,9,7),fill=light)
        d.line((7,5,7,2,11,2),fill=metal); d.ellipse((10,1,12,3),fill=c)
        d.rectangle((6,12,7,12),fill=c); d.point((9,12),fill=white)
    elif f in ('core','crystal'):
        if f=='core': d.ellipse((1,2,14,13),outline=(218,171,68),width=2)
        d.polygon([(8,1),(12,6),(10,12),(7,15),(3,9),(4,5)],fill=dark,outline=c)
        d.polygon([(8,2),(8,11),(4,8)],fill=light); d.polygon([(8,2),(11,6),(8,11)],fill=c)
        d.line((8,3,6,7),fill=white)
    elif f=='rod':
        d.rectangle((5,1,10,14),fill=edge); d.rectangle((6,3,9,12),fill=c)
        for y in (1,5,9,13): d.rectangle((4,y,11,y+1),fill=metal)
        if any(x in ident for x in ('broken','depleted','rejected')):
            d.line((8,2,6,6,9,8,7,13),fill=edge,width=2)
    elif f=='nano':
        for x,y in ((3,3),(10,3),(6,9)):
            d.line((x,y,x+2,y+3,8,8),fill=metal); d.rectangle((x,y,x+3,y+3),fill=dark,outline=c)
            d.point((x+1,y+1),fill=white)
    elif f=='circuit':
        d.rectangle((2,3,13,12),fill=dark,outline=metal)
        for x in range(3,14,3): d.line((x,1,x,4),fill=(216,181,88)); d.line((x,11,x,14),fill=(216,181,88))
        d.rectangle((5,5,10,10),fill=edge,outline=c); d.line((6,6,9,6,9,8),fill=light)
    elif f=='bubble':
        d.ellipse((2,1,13,12),fill=dark,outline=metal); d.ellipse((4,3,11,10),fill=c)
        d.arc((5,4,10,9),25,275,fill=light,width=2); d.rectangle((4,12,11,14),fill=metal)
        if 'empty' in ident: d.ellipse((4,3,11,10),fill=edge,outline=light)
        elif 'world_bubble' in ident:
            d.arc((3,4,12,9),0,330,fill=white); d.line((7,3,9,5,7,8,10,10),fill=(64,95,63))
    elif f=='key':
        if 'judah' in ident: d.rectangle((6,1,9,14),fill=(212,162,54)); d.rectangle((2,4,13,7),fill=(232,197,86))
        elif 'eden' in ident: d.ellipse((2,2,13,13),fill=dark,outline=(214,160,58),width=2); d.ellipse((6,5,10,9),fill=c)
        else: d.polygon([(2,3),(7,1),(13,5),(13,12),(8,15),(2,11)],fill=dark,outline=metal); d.line((4,5,10,10,8,12),fill=light,width=2)
    elif f=='ship':
        d.polygon([(1,9),(9,3),(14,6),(11,12),(5,13)],fill=metal,outline=edge)
        d.line((4,9,10,5,11,7,7,10),fill=c,width=2)
    elif f=='component':
        d.polygon([(2,5),(9,2),(14,6),(14,11),(7,14),(2,10)],fill=dark,outline=metal)
        d.line((3,6,8,9,13,7),fill=light,width=2); d.line((8,10,8,12),fill=c)
    else:
        d.rectangle((5,2,10,3),fill=metal); d.polygon([(5,4),(10,4),(12,12),(10,14),(4,14),(3,12)],fill=dark,outline=metal)
        d.rectangle((5,8,10,12),fill=c); d.line((6,5,6,7),fill=white)
    # A small engraved identity code differentiates same-family engineering parts reproducibly.
    if r['kind']!='block':
        for i in range(4):
            if h[1] & (1<<i): d.point((5+i,11),fill=white)
    return im
def png(path,im):
    import io
    stream=io.BytesIO(); im.save(stream,format='PNG'); save(path,stream.getvalue())

sheet=Image.new('RGB',(900,math.ceil(len(CATALOG)/10)*82),(19,23,34)); sd=ImageDraw.Draw(sheet)
try: font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',9)
except OSError: font=ImageFont.load_default()
for index,r in enumerate(CATALOG):
    ident=r['id']; kind=r['kind']
    if kind=='fluid':
        c,light,dark,h=palette(r)
        im=Image.new('RGBA',(16,64)); flow=Image.new('RGBA',(16,64))
        for frame in range(4):
            for y in range(16):
                for x in range(16):
                    v=(math.sin((x+frame*2)*math.pi/8)+math.cos((y-frame*2)*math.pi/8)+2)/4
                    color=tuple(int(dark[i]*(1-v)+light[i]*v) for i in range(3))+(255,)
                    im.putpixel((x,y+frame*16),color)
                    flow.putpixel((x,y+frame*16),tuple(int(dark[i]*(1-v*.7)+light[i]*v*.7) for i in range(3))+(255,))
        for suffix,art in [('',im),('_flow',flow)]:
            p=ART/f'textures/block/fluids/fluid.{ident}{suffix}.png'; png(p,art)
            js(Path(str(p)+'.mcmeta'),{'animation':{'frametime':5,'interpolate':True}})
        # GT buckets use the Forge dynamic model and the registered custom fluid texture.
        js(ART/f'models/item/{ident}_bucket.json',{'parent':'forge:item/bucket','loader':'forge:fluid_container','fluid':f'hk3gtl:{ident}'})
        preview=im.crop((0,0,16,16))
    else:
        im=texture(r); preview=im
        # Preserve the dedicated reason-core illustration authored in batch4.
        if ident=='imitation_reason_core': preview=Image.open(ART/f'textures/item/{ident}.png').convert('RGBA')
        else: png(ART/f'textures/{kind}/{ident}.png',im)
        if kind=='item': js(ART/f'models/item/{ident}.json',{'parent':'minecraft:item/generated','textures':{'layer0':f'hk3gtl:item/{ident}'}})
        else:
            js(ART/f'models/block/{ident}.json',{'parent':'minecraft:block/cube_all','textures':{'all':f'hk3gtl:block/{ident}'}})
            js(ART/f'blockstates/{ident}.json',{'variants':{'':{'model':f'hk3gtl:block/{ident}'}}})
            js(ART/f'models/item/{ident}.json',{'parent':f'hk3gtl:block/{ident}'})
            js(RES/f'data/hk3gtl/loot_tables/blocks/{ident}.json',{'type':'minecraft:block','pools':[{'rolls':1,'entries':[{'type':'minecraft:item','name':f'hk3gtl:{ident}'}],'conditions':[{'condition':'minecraft:survives_explosion'}]}]})
    x=(index%10)*90; y=(index//10)*82
    sheet.paste(preview.resize((48,48),Image.Resampling.NEAREST),(x+20,y),preview.resize((48,48),Image.Resampling.NEAREST))
    label=r['zh']; sd.text((x+2,y+50),label[:9],font=font,fill='white'); sd.text((x+2,y+63),label[9:],font=font,fill='white')
png(ROOT/'doc/HK3GTL-内测5/09_测试发布/内测5注册贴图总览.png',sheet)
for locale in ('zh_cn','en_us'):
    p=ART/f'lang/{locale}.json'; data=json.loads(p.read_text(encoding='utf-8'))
    for r in CATALOG:
        name=r['zh'] if locale=='zh_cn' else r['en']; ident=r['id']
        if r['kind']=='fluid':
            for prefix in ('material','fluid'): data[f'{prefix}.hk3gtl.{ident}']=name
            data[f'item.hk3gtl.{ident}_bucket']=name+('桶' if locale=='zh_cn' else ' Bucket')
        else: data[f'{r["kind"]}.hk3gtl.{ident}']=name
    js(p,data)
for tag in ('mineable/pickaxe','needs_iron_tool'):
    p=RES/f'data/minecraft/tags/blocks/{tag}.json'
    data=json.loads(p.read_text(encoding='utf-8')) if p.exists() else {'replace':False,'values':[]}
    data['values']=list(dict.fromkeys(data['values']+[f'hk3gtl:{r["id"]}' for r in blocks])); js(p,data)
js(RES/'data/hk3gtl/catalog/industrial_content.json',{'revision':45,'entries':CATALOG,'nonphysical':['HKE account balance','research completion','experiment receipts','diplomacy reputation','judgment eligibility']})
rows=''.join(f'<tr><td>{r["source"]}</td><td>{r["kind"]}</td><td>{r["zh"]}</td><td><code>hk3gtl:{r["id"]}</code></td><td>{"沿用" if r.get("reuse") else "新增"}</td></tr>' for r in CATALOG)
report=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>内测5物理内容注册与贴图</title>
<style>body{{background:#121827;color:#e1e9f5;font:16px system-ui;padding:30px}}td,th{{border:1px solid #46516a;padding:8px}}table{{border-collapse:collapse}}code{{color:#a9d4ff}}img{{max-width:100%}}</style>
<h1>内测5物理内容注册与贴图 · 批次7</h1><p>{STAMP} Asia/Hong_Kong</p>
<p>新增物品{len(items)}、工艺流体{len(fluids)}、结构材料方块{len(blocks)}。沿用{len(CATALOG)-len(items)-len(fluids)-len(blocks)}项。液态崩坏能原ID保留。HKE和资格仅是系统状态。</p>
<p>这是材料注册目录。机器控制器、最终Pattern与工艺配方不能由材料注册完成推导；各自验收单独记录。</p>
<p>来源：工业树状图v5、16电压工业能力矩阵v1、工业收口v3、100项研究课题。全部新增贴图由Python程序原创绘制，无第三方图片。来源标记对应工业文档节点。</p>
<p>固态崩坏能沿用honkai_energy_crystal；已有魂钢锭板杆与16电压电路/八大件沿用原注册。检测器不消耗由后续配方notConsumable实现，本批不声称配方已接通。</p>
<img src="内测5注册贴图总览.png"><table><tr><th>来源</th><th>类别</th><th>名称</th><th>ID</th><th>处置</th></tr>{rows}</table>
<h2>变更记录 #1</h2><p>{STAMP} 内测5第7次代码更新：新增清单、Java注册、专用纹理、模型、语言、挖掘标签与掉落表；备份被改文件，不删除旧代码。构建及游戏验证待执行。</p></html>'''
save(ROOT/'doc/HK3GTL-内测5/09_测试发布/物品流体方块注册与贴图_批次7.html',report)
js(ROOT/'tools/industrial_batch7_changed_files.json',CHANGED)
print(f'Generated {len(items)} items, {len(fluids)} fluids, {len(blocks)} blocks; {len(CHANGED)} files.')

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
