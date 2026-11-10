"""修订71：保留既有工艺成本与门槛，增加交叠系列配方和等级通用输入。"""
import re
from implement_circuits71 import ROOT, JAVA, ENTRIES, FORMS, STAMP, write, note

GROUPS = {'ABYSS': 15, 'IMAGINARY': 19, 'QUANTUM': 23, 'FINALITY': 27}
REF = r'(?:Abyss|Imaginary|Quantum|Finality)CircuitItems\.CIRCUIT_(ABYSS|IMAGINARY|QUANTUM|FINALITY)_([1-4])\.get\(\)'
INPUT = re.compile(r'\.inputItems\(new ItemStack\(' + REF + r'(?:,\s*(\d+))?\)\)')

def main():
    sources = [JAVA/'common/recipe/Hk3RecipeAdderImpl.java',
        JAVA/'common/recipe/imaginary/ImaginaryCircuitRecipes.java',
        JAVA/'common/recipe/quantum/QuantumStageRecipes.java',
        JAVA/'common/recipe/finality/FinalityStageRecipes.java']
    imports = set()
    variants = []
    for path in sources:
        text = path.read_text(encoding='utf-8')
        imports.update(re.findall(r'^import .+;', text, re.M))
        for match in re.finditer(r'(?m)^        (\w+\.\w+)\.recipeBuilder\("([^"]+)"\)([\s\S]*?)\.save\(provider\);', text):
            if match[2] == 'finality_seed_chip':
                continue
            output = re.search(r'\.outputItems\(new ItemStack\(' + REF + r',\s*(\d+)\)\)', match[3])
            if not output:
                continue
            tier = GROUPS[output[1]] + int(output[2]) - 1
            extras = [e for e in ENTRIES if e['tier'] == tier and not e['primary']]
            for entry in extras:
                body = match[3]
                body = body[:output.start()] + '.outputItems(new ItemStack(Hk3CircuitItems.DETAILED_CIRCUITS.get("' + entry['id'] + '").get(), ' + output[3] + '))' + body[output.end():]
                def input_replacement(m):
                    count = m[3] or '1'
                    if entry['form'] > 0:
                        previous = entry['family']+'_'+FORMS[entry['form']-1]
                        return '.inputItems(new ItemStack(Hk3CircuitItems.DETAILED_CIRCUITS.get("'+previous+'").get(), '+count+'))'
                    return '.inputItems(Hk3CircuitCatalog.tag('+str(tier-1)+'), '+count+')'
                body = INPUT.sub(input_replacement, body)
                body = re.sub(r'\.EUt\(\w+\)', '.EUt(Hk3Values.VA_LONG['+str(tier if tier>=19 else 15)+'])', body)
                recipe_id = 'hk3gtl_series_'+entry['id']
                if match[2].endswith('_schicksal'):recipe_id += '_schicksal'
                if match[2].endswith('_anti_entropy'):recipe_id += '_anti_entropy'
                tail=text[match.end():]
                gate = re.match(r'\s*Hk3RecipeResearchGate.bind\(([^,]+),\s*"'+re.escape(match[2])+r'",\s*"([^"]+)"\);',tail)
                gate_line=''
                if gate:
                    recipe_type = '"imaginary_circuit_computation"' if gate[1]=='RT' else gate[1]
                    gate_line='\n        Hk3RecipeResearchGate.bind('+recipe_type+', "'+recipe_id+'", "'+gate[2]+'");'
                variants.append('        '+match[1]+'.recipeBuilder("'+recipe_id+'")'+body+'.save(provider);'+gate_line)
    assert len(variants)==14, len(variants)
    imports.update(['import com.sirin.hk3gtl.common.item.Hk3CircuitItems;', 'import com.sirin.hk3gtl.common.item.Hk3CircuitCatalog;'])
    source='package com.sirin.hk3gtl.common.recipe;\n\n'+'\n'.join(sorted(imports))+'\n\n'+f'''/**
 * 【变更记录 #1】{STAMP}（第 1 次备注 · 内测5修订71）
 * 删除：交叠等级只能使用一个电路系列的限制。新增：三组系列共12个物品的14条工艺路线。
 * 修改：沿用同级既有工艺、材料、产量和研究门槛；系列内逐形态组装，系列入口消耗前一级标签。
 * 用途：让新系列可生产且不会通过无门槛兑换绕过研究；通用设备输入统一按电压标签。
 */
public final class Hk3CircuitSeriesRecipes {{
    private Hk3CircuitSeriesRecipes() {{}}
    public static void register(Consumer<FinishedRecipe> provider) {{
'''+ '\n\n'.join(variants)+'\n    }\n}\n'
    write(JAVA/'common/recipe/Hk3CircuitSeriesRecipes.java',source)
    count = 0
    for path in (JAVA/'common/recipe').rglob('*.java'):
        if path.name=='Hk3CircuitSeriesRecipes.java':continue
        original=path.read_text(encoding='utf-8')
        def repl(m):
            return '.inputItems(com.sirin.hk3gtl.common.item.Hk3CircuitCatalog.tag('+str(GROUPS[m[1]]+int(m[2])-1)+'), '+(m[3] or '1')+')'
        changed,n=INPUT.subn(repl,original)
        count+=n
        if path.name=='Hk3RecipeAdderImpl.java' and 'Hk3CircuitSeriesRecipes.register(provider);' not in changed:
            changed=changed.replace('        addCircuitRecipes(provider);','        addCircuitRecipes(provider);\n        Hk3CircuitSeriesRecipes.register(provider);')
        if changed!=original:write(path,note(changed,'电路输入使用本等级标签，允许不同系列替代；输出、材料成本及研究门槛保持明确。'))
    print('新增配方',len(variants),'；等级输入替换',count)

if __name__=='__main__':main()
