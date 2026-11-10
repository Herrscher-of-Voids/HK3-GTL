"""修订75：负责人确认的13系列逐级交叠与九套GT/GTL原图轮用。

变更记录 #1：执行时间写入备注；保留旧注册ID、电压映射、历史记录及原图动画。
新增六系列24件及具体前形态配方；通用机器输入标签继续只含同级物品。
"""
from pathlib import Path
from datetime import datetime
from io import BytesIO
import json,re,zipfile,hashlib,shutil
from PIL import Image
from apply_confirmed_parts74 import whole_tint

ROOT=Path(__file__).resolve().parents[1]
RES=ROOT/'src/main/resources'
JAVA=ROOT/'src/main/java/com/sirin/hk3gtl'
LOG=ROOT/'logs/revision75'
INSTANCE=Path('C:/Users/OWNER/AppData/Roaming/PrismLauncher/instances/GregTech-Leisure-1.4.5.2/minecraft')
STAMP=datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S')
FORMS=['processor','assembly','computer','processor_mainframe']
ZH_FORMS=['处理器','处理器组装件','超级计算机','处理器主机']
EN_FORMS=['Processor','Processor Assembly','Supercomputer','Processor Mainframe']
NEW=[('rhythmic_coupling','律动耦合','Rhythmic Coupling',16,0),
     ('quantum_bridge','量子桥接','Quantum Bridge',18,0),
     ('quantum_interference','量子干涉','Quantum Interference',20,1),
     ('imaginary_anchoring','虚数锚定','Imaginary Anchoring',22,1),
     ('causal_reconstruction','因果重构','Causal Reconstruction',24,2),
     ('terminal_computation','终序演算','Terminal Computation',26,2)]
COLORS=['#A45BDA','#DB70A5','#CC68F1','#62B5D5','#22BCD2','#55D9A2','#4784EA',
        '#7695DD','#EBA630','#F0C759','#BFD57E','#C986DB','#DC456F']
SOURCES=[('gtceu','nano'),('gtceu','quantum'),('gtceu','crystal'),('gtceu','wetware'),
         ('kubejs','bioware'),('kubejs','optical'),('kubejs','exotic'),('kubejs','cosmic'),('kubejs','supracausal')]


def write(path,data):
    if isinstance(data,str):data=data.encode('utf8')
    if path.exists():
        if path.read_bytes()==data:return
        backup=LOG/'backup'/path.relative_to(ROOT)
        if not backup.exists():backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,backup)
    path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)


def save(path,data):write(path,json.dumps(data,ensure_ascii=False,indent=2)+'\n')


def patch(rel,fn,message):
    path=JAVA/rel;old=path.read_text('utf8');new=fn(old)
    if old==new:return
    n=max([int(x) for x in re.findall(r'变更记录\s*#(\d+)',old)],default=0)+1
    block=f'/**\n * 【变更记录 #{n}】{STAMP}（第 {n} 次备注 · 内测5修订75）\n * {message}\n */\n'
    new=re.sub(r'(?m)^public (?:final )?class ',lambda m:block+m[0],new,count=1)
    write(path,new)


def main():
    catalog_path=RES/'data/hk3gtl/catalog/circuit_series.json'
    catalog=json.loads(catalog_path.read_text('utf8'));old=catalog['entries']
    entries=[e for e in old if e['family'] not in {n[0] for n in NEW}]
    for family,zh,en,tier,p in NEW:
        entries.extend(dict(id=family+'_'+form,tier=tier+i,family=family,form=i,primary=False,
                            zh=zh+ZH_FORMS[i],en=en+' '+EN_FORMS[i]) for i,form in enumerate(FORMS))
    starts={e['family']:e['tier']-e['form'] for e in entries}
    entries.sort(key=lambda e:(starts[e['family']],e['form']))
    for e in entries:
        if e['family'] not in {n[0] for n in NEW}:
            e['zh']=re.sub(r'(处理器集群|计算主机)$',lambda m:'处理器组装件' if m[0]=='处理器集群' else '处理器主机',e['zh'])
    assert sorted(starts.values())==list(range(15,28)) and len(entries)==52
    families=list(dict.fromkeys(e['family'] for e in entries))
    for a,b in zip(families,families[1:]):
        assert next(e['tier'] for e in entries if e['family']==a and e['form']==3)==next(e['tier'] for e in entries if e['family']==b and e['form']==2)
    catalog['entries']=entries;catalog['_comment_revision75']=f'变更记录 #1 {STAMP}：六系列补入七系列间隙，13系列逐级交叠；低系列主机与相邻高系列超级计算机同级。'
    save(catalog_path,catalog)
    rows=',\n'.join('            new Entry("{id}", {tier}, "{family}", {form}, {primary})'.format(**{**e,'primary':str(e['primary']).lower()}) for e in entries)
    patch('common/item/Hk3CircuitCatalog.java',lambda s:re.sub(r'(ENTRIES = List.of\(\n).*?(\n    \);)',lambda m:m[1]+rows+m[2],s,flags=re.S),
          '删除：系列起点隔两级留下的交叠空档。新增：六系列24个正式物品映射。\n * 修改：13系列起点连续15至27，四形态覆盖15至30，保留旧28件等级与ID。\n * 用途：注册、标签、配方及WMP共用目录；相邻主机与超级计算机同级。')
    patch('common/recipe/Hk3CircuitManufacturing.java',lambda s:s.replace('"soulium_lattice", "honkai_resonance"','"soulium_lattice", "honkai_resonance", "rhythmic_coupling", "quantum_bridge"')
          .replace('"quantum_coherence", "entanglement_anchor"','"quantum_coherence", "entanglement_anchor", "quantum_interference", "imaginary_anchoring"')
          .replace('"imaginary_reconstruction", "world_weaving"','"imaginary_reconstruction", "world_weaving", "causal_reconstruction", "terminal_computation"')
          .replace('public static void registerSeeds(Consumer<FinishedRecipe> provider) {','public static void registerSeeds(Consumer<FinishedRecipe> provider) {\n        registerSupplemental(provider);')
          .replace('    /** 四个平台首枚', '''    private static void registerSupplemental(Consumer<FinishedRecipe> provider) {
        for(var entry:Hk3CircuitCatalog.ENTRIES) {
            if(!java.util.Set.of("rhythmic_coupling","quantum_bridge","quantum_interference",
                    "imaginary_anchoring","causal_reconstruction","terminal_computation").contains(entry.family())) continue;
            int p=platform(entry);
            var type=p==0?Hk3RecipeTypes.ABYSS_CIRCUIT_FOUNDRY_RECIPES
                    :p==1?Hk3RecipeTypesImaginary.IMAGINARY_CIRCUIT_COMPUTATION
                    :Hk3RecipeTypesQuantum.QUANTUM_PRECISION_ASSEMBLY;
            String id="hk3gtl_supplemental_"+entry.id();
            assemble(type.recipeBuilder(id),entry.id(),Hk3Values.VA_LONG[entry.tier()-1]).save(provider);
            String gate=p==0?"R-AB-012":p==1?"R-IM-002":"R-QT-001";
            Hk3RecipeResearchGate.bind(type.registryName.getPath(),id,gate);
        }
    }

    /** 四个平台首枚'''),
          '删除：无。新增：六个已确认系列24条制造路线与平台映射。\n * 修改：输入仍为平台电子部件与具体前形态；首形态使用前一级电压。\n * 用途：新系列可制造，沿用现役专用机器和研究门槛，不依赖待产电路自身。')
    color_cases='\n'.join(f'            case "{f}" -> 0x{COLORS[i][1:]};' for i,f in enumerate(families))
    patch('common/item/Hk3CircuitItem.java',lambda s:re.sub(r'            case "soulium_lattice".*?(?=            default)',color_cases+'\n',s,flags=re.S),
          '删除：无。新增：六系列主题色。\n * 修改：13系列均使用负责人选择的主题色流动等级提示，保留正式电压名称。\n * 用途：新物品自动显示实际等级；普通机器标签兼容不受提示动画影响。')
    languages={l:json.loads((RES/f'assets/hk3gtl/lang/{l}.json').read_text('utf8')) for l in ['zh_cn','en_us']}
    assets=[]
    with zipfile.ZipFile(INSTANCE/'mods/gtceu-1.20.1-1.4.4.jar') as jar:
        for e in entries:
            index=families.index(e['family']);ns,source_family=SOURCES[index%len(SOURCES)]
            form=['processor','assembly','computer','mainframe'][e['form']]
            name=source_family+('_processor_'+form if ns=='gtceu' and e['form']>0 else '_'+form)
            resource=f'assets/{ns}/textures/item/{name}.png'
            if ns=='gtceu':raw=jar.read(resource);meta=jar.read(resource+'.mcmeta') if resource+'.mcmeta' in jar.namelist() else None
            else:
                source=INSTANCE/'kubejs'/resource;raw=source.read_bytes();mp=source.with_suffix('.png.mcmeta');meta=mp.read_bytes() if mp.exists() else None
            im=Image.open(BytesIO(raw)).convert('RGBA');output=whole_tint(im,COLORS[index],False)
            assert im.getchannel('A').tobytes()==output.getchannel('A').tobytes()
            assert [max(p[:3]) for p in im.getdata()]==[max(p[:3]) for p in output.getdata()]
            target=RES/f'assets/hk3gtl/textures/item/{e["family"]}/circuits/{e["id"]}.png'
            # 旧28件沿原模型路径写入，稳定资源引用不变。
            model_path=RES/f'assets/hk3gtl/models/item/{e["id"]}.json'
            model=json.loads(model_path.read_text('utf8')) if model_path.exists() else {'parent':'minecraft:item/generated','textures':{'layer0':f'hk3gtl:item/{e["family"]}/circuits/{e["id"]}'}}
            target=RES/('assets/hk3gtl/textures/'+model['textures']['layer0'].split(':')[1]+'.png')
            buffer=BytesIO();output.save(buffer,format='PNG');write(target,buffer.getvalue())
            if meta is not None:write(target.with_suffix('.png.mcmeta'),meta)
            elif target.with_suffix('.png.mcmeta').exists():save(target.with_suffix('.png.mcmeta'),{'animation':{'frames':[0],'frametime':20},'_comment_revision75':f'变更记录 #1 {STAMP}：静态原图显示零帧，保留历史文件。'})
            model.setdefault('_history',[]).append(f'变更记录 #1 {STAMP} 修订75：负责人确认九套GT/GTL原图按13系列顺序轮用，仅整体染色，动画和透明度保留。')
            save(model_path,model)
            for l in languages:languages[l]['item.hk3gtl.'+e['id']]=e['zh' if l=='zh_cn' else 'en']
            assets.append({'id':e['id'],'source':resource,'source_sha256':hashlib.sha256(raw).hexdigest(),
                           'destination':target.relative_to(RES).as_posix(),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
                           'size':list(output.size),'family':e['family'],'color':COLORS[index],'alpha_preserved':True,'hsv_value_preserved':True})
    for l,data in languages.items():data['_comment_circuits75']=f'变更记录 #1 {STAMP}：13系列52件正式名称不附带电压；四形态采用处理器、处理器组装件、超级计算机、处理器主机。';save(RES/f'assets/hk3gtl/lang/{l}.json',data)
    # 更新所有已有同级标签别名，保留标签元数据与其他来源成员。
    original_tier={e['id']:e['tier'] for e in old}
    for ns in ['forge','gtceu']:
        for path in (RES/f'data/{ns}/tags/items/circuits').glob('*.json'):
            data=json.loads(path.read_text('utf8'));tiers={original_tier[v.split(':')[1]] for v in data.get('values',[]) if isinstance(v,str) and v.startswith('hk3gtl:') and v.split(':')[1] in original_tier}
            if len(tiers)!=1:continue
            tier=tiers.pop();values=[v for v in data['values'] if not isinstance(v,str) or not v.startswith('hk3gtl:')]
            values.extend('hk3gtl:'+e['id'] for e in entries if e['tier']==tier)
            data['values']=values;data['_comment_revision75']=f'变更记录 #1 {STAMP}：补入本电压新系列，禁止跨级替代。';save(path,data)
    save(RES/'data/hk3gtl/catalog/circuit_art75.json',{'revision':75,'generated_at':STAMP,'entries':assets,'changes':'负责人确认九套原图轮用，52张透明度与HSV明度逐像素一致，保留动画。'})
    data=json.loads((RES/'assets/hk3gtl/changelog.json').read_text('utf8'))
    data['entries'][0]['changes'].extend([f'{STAMP}：新增律动耦合、量子桥接、量子干涉、虚数锚定、因果重构、终序演算；13系列52件逐级交叠。',
        '负责人选择九套GT/GTL原图轮用整体染色，正式电路等级提示使用系列主题色流动。'])
    save(RES/'assets/hk3gtl/changelog.json',data)
    save(LOG/'overlap-verification.json',{'series':len(families),'circuits':len(entries),'adjacent_mainframe_computer_matches':12,
        'legacy_tiers_preserved':all(next(n['tier'] for n in entries if n['id']==e['id'])==e['tier'] for e in old),'assets_verified':len(assets)})
    print('13系列52电路、12组主机/超级计算机同级对应、旧28件等级保留；52张原图换色校验通过。')


if __name__=='__main__':main()
