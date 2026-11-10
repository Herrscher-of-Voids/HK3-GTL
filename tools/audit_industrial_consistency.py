"""内测5可重复静态检查；只读取源码/资源，输出JSON，不改游戏或存档。
变更记录 #1 · 2026-09-27 04:20:00 · 修订90。
删除：无。新增：52电路映射、192等级别名标签、64电子部件、研究入口、机器/门槛、材料和资源检查。
用途：明确错误返回非零；未定位来源列为待核对，不能把静态扫描当成运行注册或可玩性证明。
调用：python tools/audit_industrial_consistency.py --output logs/revision90/audit.json
变更记录 #2 · 2026-09-27 04:26:03 · 修订90：补查辅助函数中的具体电路、物料注册及机器IO。
校正：第1条所称192组应为96组（16等级×2命名空间×3别名）；不改游戏数据。
"""
from pathlib import Path
import argparse, collections, datetime, hashlib, json, re, sys

ROOT = Path(__file__).resolve().parents[1]
def read(p): return p.read_text(encoding='utf-8-sig')
def stripped(text):
    return re.sub(r'"(?:\\.|[^"\\])*"|/\*.*?\*/|//[^\n]*',
                  lambda m: m[0] if m[0].startswith('"') else '\n'*m[0].count('\n'), text, flags=re.S)
def strings(text): return re.findall(r'"([^"\n]+)"', text)
def array(text, name):
    m = re.search(r'\b'+re.escape(name)+r'\s*=\s*(?:List\.of\((.*?)\)|\{(.*?)\})\s*;', text, re.S)
    if not m: raise ValueError('无法解析数组：'+name)
    return strings(m[1] or m[2])

def audit(root):
    resources=root/'src/main/resources'; java=root/'src/main/java/com/sirin/hk3gtl'
    errors=[]; observations=[]; checks=[]
    def check(ok, code, detail):
        checks.append({'code':code,'passed':bool(ok),'detail':detail})
        if not ok: errors.append({'code':code,'detail':detail})
    def rel(p): return p.relative_to(root).as_posix()
    def loc(p,t,pos): return {'file':rel(p),'line':t.count('\n',0,pos)+1}
    parsed={}
    for p in resources.rglob('*.json'):
        try: parsed[rel(p)]=json.loads(read(p))
        except Exception as exc: errors.append({'code':'json_parse','file':rel(p),'error':str(exc)})
    def data(name): return parsed['src/main/resources/'+name]
    source={p:stripped(read(p)) for p in java.rglob('*.java')}
    def src(s): return source[java/s]
    entries=data('data/hk3gtl/catalog/circuit_series.json')['entries']
    cat=src('common/item/Hk3CircuitCatalog.java')
    java_entries=[{'id':a,'tier':int(b),'family':c,'form':int(d),'primary':e=='true'} for a,b,c,d,e in
                  re.findall(r'new Entry\("([^"]+)",\s*(\d+),\s*"([^"]+)",\s*(\d+),\s*(true|false)\)',cat)]
    check(java_entries==[{k:e[k] for k in ('id','tier','family','form','primary')} for e in entries],
          'catalog_java_resource','Java目录与资源目录逐条一致')
    check(len(entries)==52 and len({e['id'] for e in entries})==52,'circuit_count','52个唯一正式电路')
    families=collections.defaultdict(list)
    for e in entries: families[e['family']].append(e)
    check(len(families)==13,'family_count','13个系列')
    starts=[]
    for family,items in families.items():
        ordered=sorted(items,key=lambda x:x['form']);start=ordered[0]['tier'];starts.append(start)
        check([x['form'] for x in ordered]==list(range(4)) and [x['tier'] for x in ordered]==list(range(start,start+4)),
              'family_forms',family)
    check(sorted(starts)==list(range(15,28)),'overlap','系列起点每级交叠，覆盖15至30')
    tiers=src('common/constants/Hk3TiersImpl.java');keys=array(tiers,'VOLTAGE_KEYS');symbols=array(tiers,'VOLTAGE_SYMBOLS')
    aliases=[f'{stage}-{roman}' for stage in ['ab','im','qt','fn'] for roman in ['i','ii','iii','iv']]
    tags={};resolved={}
    for ns in ('forge','gtceu'):
        for p in (resources/f'data/{ns}/tags/items/circuits').glob('*.json'):
            tags[f'{ns}:circuits/{p.stem}']=data(f'data/{ns}/tags/items/circuits/{p.name}')['values']
    def expand(key,trail=()):
        if key in trail: raise ValueError('循环标签：'+key)
        values=set()
        for value in tags.get(key,[]):
            value=value if isinstance(value,str) else value['id']
            values.update(expand(value[1:],trail+(key,)) if value.startswith('#') else [value])
        return values
    for n,key in enumerate(keys):
        expected={'hk3gtl:'+e['id'] for e in entries if e['tier']==n+15}
        for ns in ('forge','gtceu'):
            for alias in (key,):
                full=f'{ns}:circuits/{alias}';actual=expand(full);resolved[full]=sorted(actual)
                check(actual==expected,'voltage_tag',full)
    lang={language:data('assets/hk3gtl/lang/'+language+'.json') for language in ['zh_cn','en_us']}
    electronic=src('common/item/Hk3ElectronicItems.java')
    platforms=array(electronic,'PLATFORMS');parts=array(electronic,'PARTS')
    electronic_ids=[p+'_'+part for p in platforms for part in parts]
    check(len(electronic_ids)==64,'electronic_count','实际四平台×16部件；旧40件清单不作为现状')
    model_report=[]
    def local_model(model,trail=()):
        if model in trail: return ['模型继承循环 '+model]
        ns,path=(model.split(':',1) if ':' in model else ('minecraft',model))
        if ns!='hk3gtl': return []
        key=f'assets/{ns}/models/{path}.json'
        if 'src/main/resources/'+key not in parsed: return ['模型缺失 '+model]
        definition=data(key);missing=[]
        if 'parent' in definition: missing+=local_model(definition['parent'],trail+(model,))
        for texture in definition.get('textures',{}).values():
            if texture.startswith('hk3gtl:') and not (resources/'assets/hk3gtl/textures'/ (texture.split(':',1)[1]+'.png')).is_file():
                missing.append('纹理缺失 '+texture)
        return missing
    for id in [e['id'] for e in entries]+electronic_ids:
        issues=local_model('hk3gtl:item/'+id);check(not issues,'item_resource',{'id':id,'issues':issues})
        for language,dictionary in lang.items():check(bool(dictionary.get('item.hk3gtl.'+id)),'item_language',language+':'+id)
        model_report.append({'id':id,'issues':issues})
    for e in entries:
        for language,field in [('zh_cn','zh'),('en_us','en')]:
            check(lang[language].get('item.hk3gtl.'+e['id'])==e[field],'circuit_display',language+':'+e['id'])
    manufacture=src('common/recipe/Hk3CircuitManufacturing.java')
    check('e.family().equals(entry.family()) && e.form() == form - 1' in manufacture
          and 'new ItemStack(Hk3CircuitItems.DETAILED_CIRCUITS.get(previous.id()).get(), 2)' in manufacture,
          'exact_previous_form','统一制造器使用同系列具体上一形态×2')
    check('Hk3CircuitCatalog.tag(' not in manufacture,'no_generic_upgrade','系列内部升级不使用通用电路标签')
    check('TagKey.create(Registries.ITEM, tagId(tier))' in cat
          and '"circuits/" + Hk3Tiers.voltageKey(tier)' in cat,
          'shared_tag_path','实际TagKey使用独立回归覆盖的同一标签路径')
    recipes={p:t for p,t in source.items() if '/recipe/' in p.as_posix()}
    supplemental=set(strings(re.search(r'Set\.of\((.*?)\)\.contains\(entry.family\(\)\)',manufacture,re.S)[1]))
    routes=collections.defaultdict(list)
    for p,t in recipes.items():
        for m in re.finditer(r'Hk3CircuitManufacturing\.assemble\(\s*([\w.]+)\.recipeBuilder\("([^"]+)"\),\s*"([^"]+)"',t):
            routes[m[3]].append({**loc(p,t,m.start()),'type':m[1],'recipe':m[2]})
    circuit_report=[]
    for e in entries:
        row=dict(e);row['previous']=next((x['id'] for x in families[e['family']] if x['form']==e['form']-1),None)
        row['literal_routes']=routes[e['id']];row['supplemental_loop']=e['family'] in supplemental
        check(bool(row['literal_routes'] or row['supplemental_loop']),'manufacturing_route',e['id'])
        circuit_report.append(row)
    root_recipe=src('common/recipe/Hk3RecipeAdderImpl.java')
    for hook in ['Hk3CircuitSeriesRecipes.register(provider)','Hk3ElectronicRecipes.register(provider)','AdvancedControllerRecipes.register(provider)']:
        check(hook in root_recipe,'registration_hook',hook)
    check('Hk3CircuitManufacturing.registerSeeds(provider)' in src('common/recipe/Hk3ElectronicRecipes.java'),
          'seed_hook','平台种子与补充系列注册入口')
    ordinary=src('common/recipe/machine/AdvancedControllerRecipes.java')
    check('.inputItems(com.sirin.hk3gtl.common.item.Hk3CircuitCatalog.tag(circuitTier), 64)' in ordinary,
          'ordinary_controllers','36控制器同级通用标签×64')
    check(len(re.findall(r'build\(provider,',ordinary))==36,'controller_recipe_count','36条调用保留')
    abyss_controllers=src('common/recipe/machine/ControllerRecipes.java')
    check('.inputItems(com.sirin.hk3gtl.common.item.Hk3CircuitCatalog.tag(circuitTier), circuitCount)' in abyss_controllers,
          'ordinary_abyss_controllers','四台海渊控制器保留原等级、16枚数量，改用通用标签')
    direct=[]
    for p,t in recipes.items():
        for m in re.finditer(r'CIRCUIT_(?:ABYSS|IMAGINARY|QUANTUM|FINALITY)_\d+|getDetailedCircuit\(',t):
            direct.append({**loc(p,t,m.start()),'code':m[0]})
    check(not direct,'specific_ordinary_inputs',direct)
    # 材料来源只标注可定位的生产语句，不将配方声明视为已能在生存模式运行。
    material_report=[];all_recipe='\n'.join(recipes.values()); electronic_recipe=src('common/recipe/Hk3ElectronicRecipes.java')
    produced_parts=set(re.findall(r'outputItems\(part\(p,\s*"([^"]+)"',electronic_recipe))|set(array(electronic_recipe,'names'))
    check(set(parts)<=produced_parts,'electronic_sources',sorted(set(parts)-produced_parts))
    beta=data('data/hk3gtl/catalog/industrial_content.json')['entries']
    registrations=src('common/registration/Hk3IndustrialContent.java')
    registered_items=set(re.findall(r'\bitem\("([^"]+)"',registrations))
    registered_fluids=set(re.findall(r'\badd\("([^"]+)"',src('common/registration/Hk3IndustrialFluids.java')))
    # 只检查确实导入此查询器的文件，避免把其他模组同名helper误当本项目注册表。
    for p,t in recipes.items():
        if 'import static com.sirin.hk3gtl.common.recipe.honkai.Hk3LiquidLineRecipes.item;' in t or p.name=='Hk3LiquidLineRecipes.java':
            used=set(re.findall(r'\bitem\("([^"]+)"',t))
            check(used<=registered_items,'registered_item_references',{'file':rel(p),'missing':sorted(used-registered_items)})
        if 'import static com.sirin.hk3gtl.common.recipe.honkai.Hk3LiquidLineRecipes.fluid;' in t or p.name=='Hk3LiquidLineRecipes.java':
            used=set(re.findall(r'\bfluid\("([^"]+)"',t))
            check(used<=registered_fluids,'registered_fluid_references',{'file':rel(p),'missing':sorted(used-registered_fluids)})
    for e in beta:
        id=e['id']; kind=e['kind'];found=[]
        for p,t in recipes.items():
            for m in re.finditer(r'(?:outputItems|outputFluids|chancedOutput)\([^;\n]*?"'+re.escape(id)+r'"',t):
                found.append(loc(p,t,m.start()))
        material_report.append({'id':id,'kind':kind,'design_source_hint':e.get('source'),'located_outputs':found,
                                'status':'定位字面量产出' if found else '未定位字面量产出；需核对生成器/外部脚本/旧物品映射'})
    topics=data('data/hk3gtl/research/research_catalog.json')['topics']; topic_ids={x['id'] for x in topics}
    experiments=collections.defaultdict(list);gates=[];machines=[]
    legacy=set(re.findall(r'\breg\("(R-[^"\n]+)"',src('common/research/Hk3ResearchNodes.java')))
    for p,t in source.items():
        for pattern in [r'recordExperiment\([^;\n]*?"(RN-[A-Z0-9-]+)"',r'\.addData\(Hk3LiquidProcessMachine\.EXPERIMENT,\s*"(RN-[A-Z0-9-]+)"']:
            for m in re.finditer(pattern,t):experiments[m[1]].append(loc(p,t,m.start()))
        if p.name=='Hk3LiquidLineRecipes.java':
            for m in re.finditer(r'recipe\([^\n]*,\s*"(RN-[A-Z0-9-]+)"\)',t):experiments[m[1]].append(loc(p,t,m.start()))
        if p in recipes:
            for m in re.finditer(r'"(R(?:N)?-[A-Z0-9-]+)"',t):
                gates.append({**loc(p,t,m.start()),'id':m[1],'known':m[1] in topic_ids|legacy})
        for m in re.finditer(r'\.multiblock\("([^"\n]+)"',t):
            end=t.find('.register()',m.end());block=t[m.end():end] if end>=0 else ''
            machines.append({**loc(p,t,m.start()),'id':m[1],
                             'recipe_types':re.findall(r'\.recipeType\(([^)]+)\)',block),
                             'generic_pattern':'createGenericMedium' in block})
    check(set(experiments)<=topic_ids,'experiment_ids',sorted(set(experiments)-topic_ids))
    # 完整电路需六种物品输入和一种流体；仅核对类型容量和生产源码中的机器绑定。
    type_definitions={}
    for p,t in recipes.items():
        if 'RecipeTypes' not in p.name: continue
        for m in re.finditer(r'GTRecipeType\s+(\w+)\s*=\s*reg\("([^"]+)",\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+)',t):
            type_definitions[m[1]]={**loc(p,t,m.start()),'id':m[2],'max_io':list(map(int,m.groups()[2:]))}
        for m in re.finditer(r'GTRecipeType\s+(\w+)\s*=\s*GTRecipeTypes\.register\(\s*"([^"]+)"[^;]+?\.setMaxIOSize\((\d+),\s*(\d+),\s*(\d+),\s*(\d+)\)',t,re.S):
            type_definitions[m[1]]={**loc(p,t,m.start()),'id':m[2],'max_io':list(map(int,m.groups()[2:]))}
    required_types={route['type'].split('.')[-1] for items in routes.values() for route in items}
    required_types |= {'ABYSS_PRECISION_ASSEMBLY_RECIPES'}
    type_report=[]
    for name in sorted(required_types):
        found=[m for m in machines if any(x.split('.')[-1]==name for x in m['recipe_types'])]
        definition=type_definitions.get(name)
        check(bool(found),'circuit_machine_binding',name)
        check(definition is not None and definition['max_io'][0]>=6 and definition['max_io'][2]>=1,
              'circuit_machine_io',{'type':name,'definition':definition})
        type_report.append({'type':name,'definition':definition,'literal_machines':found})
    for g in gates:
        if not g['known']: observations.append({'code':'unresolved_research_gate',**g})
    research_report=[{**x,'located_experiment_producers':experiments.get(x['id'],[])} for x in topics]
    missing=[x['id'] for x in research_report if not x['located_experiment_producers']]
    observations.append({'code':'missing_experiment_producer','ids':missing,
                         'action':'保留实验要求；本轮不新造实验或映射旧ID'})
    # 扫描全部项目模型的本地资源引用；旧闲置模型仍列出，是否使用需单独核对。
    resource_findings=[]
    for p in (resources/'assets/hk3gtl/models').rglob('*.json'):
        model='hk3gtl:'+p.relative_to(resources/'assets/hk3gtl/models').with_suffix('').as_posix()
        for issue in local_model(model): resource_findings.append({'file':rel(p),'issue':issue})
    observations += [{'code':'resource_reference',**x} for x in resource_findings]
    language_gaps=[]; units=[]
    for p,t in source.items():
        for m in re.finditer(r'(?:translatable|translate)\("(hk3gtl\.[^"]+)"\s*[,)]',t):
            absent=[language for language,dictionary in lang.items() if m[1] not in dictionary]
            if absent:language_gaps.append({**loc(p,t,m.start()),'key':m[1],'languages':absent})
    for language,dictionary in lang.items():
        for key,value in dictionary.items():
            if re.search(r'\bHKE(?:/t)?\b',str(value)):units.append({'language':language,'key':key,'text':value})
    observations += [{'code':'language_reference',**x} for x in language_gaps]
    check(not units,'display_hw_units',units)
    return {'generated_at':datetime.datetime.now().astimezone().isoformat(),
            'method':'源码与资源静态核对；不执行Forge注册，不替代整包KubeJS加载和游戏验收。未定位不等于绝无来源。',
            'counts':{'json_files':len(parsed),'circuits':len(entries),'families':len(families),'electronic_parts':len(electronic_ids),'voltage_tags':len(resolved),
                      'checks':len(checks),'errors':len(errors),'research_topics':len(topics),'experiment_topics':len(topic_ids&set(experiments)),
                      'literal_multiblocks':len(machines),'material_entries':len(material_report)},
            'errors':errors,'checks':checks,'observations':observations,'circuits':circuit_report,'voltage_tags':resolved,
            'electronics':{'platforms':platforms,'parts':parts,'ids':electronic_ids},'resources':model_report,
            'research':research_report,'research_gate_literals':gates,'machines':machines,'circuit_machine_types':type_report,'material_sources':material_report,
            'source_hashes':{rel(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in source}}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',default='logs/revision90/audit.json')
    args=parser.parse_args(); result=audit(ROOT); out=ROOT/args.output;out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'counts':result['counts'],'errors':result['errors'],'output':str(out)},ensure_ascii=False,indent=2))
    return bool(result['errors'])
if __name__=='__main__': sys.exit(main())

# 变更记录 #107 · 2026-09-30 02:20:26 · 修订107：删除旧电压输出键；修改为16档正式键；用途：防止工具重新生成过期引用。

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
