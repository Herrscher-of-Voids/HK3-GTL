"""修订87一次性应用器：备份后落实已批准的L1数量配平、除杂母液回流及采集标准件。"""
from pathlib import Path
from datetime import datetime
import hashlib
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / 'logs/revision87'
STAMP = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
BASE = 'src/main/java/com/sirin/hk3gtl/'
changes = []
assert not (LOG / 'application.json').exists(), '本修订已经应用，禁止重复覆盖'
assert json.loads((ROOT / 'src/main/resources/assets/hk3gtl/changelog.json').read_text(encoding='utf-8'))['entries'][0]['revision'] == 86

def put(rel, value):
    p = ROOT / rel
    before = None
    if p.exists():
        before = hashlib.sha256(p.read_bytes()).hexdigest()
        backup = LOG / 'backup' / rel
        backup.parent.mkdir(parents=True, exist_ok=True)
        assert not backup.exists(), f'已有备份，请先检查：{rel}'
        shutil.copy2(p, backup)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(value, encoding='utf-8')
    changes.append({'path': rel, 'before': before, 'after': hashlib.sha256(p.read_bytes()).hexdigest()})

def note(text, name, number, added, modified, purpose):
    block = f'''/**
 * 【变更记录 #{number}】{STAMP}（第 {number} 次备注 · 内测5修订87）
 * 删除：无，保留历史备注、稳定注册键和不相关工艺。
 * 新增：{added}
 * 修改：{modified}
 * 用途：{purpose}
 */
'''
    assert f'public final class {name}' in text
    return text.replace(f'public final class {name}', block + f'public final class {name}', 1)

rel = BASE + 'common/recipe/honkai/HonkaiRecipes.java'
s = (ROOT / rel).read_text(encoding='utf-8')
old = '.inputItems(betaItem("honkai_reference_sample", 4))'
assert s.count(old) == 1
s = s.replace(old, '.notConsumable(betaItem("honkai_reference_sample", 4))')
s = note(s, 'HonkaiRecipes', 3, '无新增采集配方。', 'I01高效采集的4份参考样本改为不消耗标准件；探测器、钨钢板、铂线、EU及研究门槛不变。', '采集仍要求样本到位，但连续生产不再逐批销毁样本；I07校准与探测器制造不受影响。')
put(rel, s)

rel = BASE + 'common/recipe/honkai/Hk3LiquidLineRecipes.java'
s = (ROOT / rel).read_text(encoding='utf-8')
edits = [
    ('private static GTRecipeBuilder recipe(', 'static GTRecipeBuilder recipe('),
    ('fluid("unrecoverable_process_effluent",250))', 'fluid("unrecoverable_process_effluent",250),fluid("clarified_honkai_mother_liquor",500))'),
    ('HonkaiMaterialItems.RAW_HONKAI_PARTICLE.get(),256', 'HonkaiMaterialItems.RAW_HONKAI_PARTICLE.get(),320'),
    ('item("separation_residue",16),item("concentrated_honkai_impurity",8),item("fuel_matrix",4)', 'item("separation_residue",8),item("concentrated_honkai_impurity",4),item("fuel_matrix",4)'),
    ('        recovery(provider);', '        Hk3LiquidLoopRecipes.register(provider);\n        recovery(provider);'),
]
for old, new in edits:
    assert s.count(old) == 1, old
    s = s.replace(old, new, 1)
s = note(s, 'Hk3LiquidLineRecipes', 2, '净化附产500mB独立除杂母液；调用Hk3LiquidLoopRecipes注册化工补充、回流与排污。', '净化粒子256→320；每次介质再生残渣16→8、杂质8→4；5000mB粗液和800mB稳定液不变。', '使4批分馏供5批稳定化的80晶种，消除再生耗材赤字；新鲜启动不依赖I05回收或回流库存。')
put(rel, s)

rel = BASE + 'common/registration/Hk3IndustrialFluids.java'
s = (ROOT / rel).read_text(encoding='utf-8')
anchor = '        add("honkai_mother_liquor", false);'
assert s.count(anchor) == 1
s = s.replace(anchor, '        add("clarified_honkai_mother_liquor", false); // 净化附产，须与新采液共同回流。\n' + anchor, 1)
s = note(s, 'Hk3IndustrialFluids', 1, 'clarified_honkai_mother_liquor除杂母液，沿现有GT材质流体注册及纹理生成方式注册。', '原含能母液保留为晶种提取原料，不以同一ID同时表示净化前后流体。', '隔离脏母液与回流液，避免旁路净化复制产物；实际使用受配方新采液和耗材约束。')
put(rel, s)

new_java = '''package com.sirin.hk3gtl.common.recipe.honkai;

import com.gregtechceu.gtceu.api.data.tag.TagPrefix;
import com.gregtechceu.gtceu.common.data.GTMaterials;
import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import com.sirin.hk3gtl.common.material.Hk3Materials;
import com.sirin.hk3gtl.common.recipe.Hk3IndustrialRecipeTypes;
import net.minecraft.data.recipes.FinishedRecipe;
import java.util.function.Consumer;
import static com.sirin.hk3gtl.common.recipe.honkai.Hk3LiquidLineRecipes.*;

/**
 * L1配套化工、母液回流与余料处置，沿液态配方唯一入口注册。
 * 【变更记录 #1】@STAMP@（第 1 次备注 · 内测5修订87）
 * 删除：无，不替换L2燃料调配、浓缩或网络注入工艺。
 * 新增：前级GT混合机配制分析试剂；I03使用7500mB新采液和500mB除杂母液回流；I05处理过剩物料。
 * 修改：复用主工艺的MAX电压、研究门禁和注册工具；回流保留与新鲜分馏相同的碳、滤芯、基质及工时。
 * 用途：补足再生试剂和独立排污出口；回收不授予重复实验，不从零库存自启动，不无耗材复制主产物。
 */
public final class Hk3LiquidLoopRecipes {
    private Hk3LiquidLoopRecipes() {}

    public static void register(Consumer<FinishedRecipe> provider) {
        // 碱性醇水试剂来自前级化工原料；无崩坏研究门槛，也不依赖生产线自身的废液。
        recipe(GTRecipeTypes.MIXER_RECIPES,"industrial_fresh_analysis_reagent",3,600,null,null)
                .inputFluids(GTMaterials.DistilledWater.getFluid(750),GTMaterials.Ethanol.getFluid(250))
                .inputItems(TagPrefix.dust,GTMaterials.SodiumHydroxide,2)
                .outputFluids(fluid("honkai_analysis_reagent",1000)).save(provider);

        // 只用除杂后的独立流体替代等量新采液，净化仍完整产出晶种所需粒子。
        recipe(Hk3IndustrialRecipeTypes.LIQUID_REFINING,"industrial_liquid_fractionation_reflux",13,1600,"RN-LSE",null)
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(7500),fluid("clarified_honkai_mother_liquor",500))
                .inputItems(TagPrefix.dust,GTMaterials.Carbon,16)
                .inputItems(item("separation_filter",8),item("directional_crystallization_matrix",4))
                .outputFluids(fluid("crude_honkai_energy",5000),fluid("honkai_mother_liquor",1500),fluid("honkai_analysis_reagent",1000))
                .outputItems(item("concentrated_honkai_impurity",32),item("separation_residue",16)).save(provider);

        // 两种固体分别处理，避免余料比例不同又造成互相等待；全部产物退出含能主线。
        recipe(Hk3IndustrialRecipeTypes.REGENERATION,"industrial_impurity_purge",14,500,"RN-BCE",null)
                .inputItems(item("concentrated_honkai_impurity",16)).inputItems(TagPrefix.dust,GTMaterials.Carbon,4)
                .inputFluids(GTMaterials.Water.getFluid(1000))
                .outputItems(item("inactive_fuel_residue",8)).outputFluids(fluid("unrecoverable_process_effluent",1000)).save(provider);
        recipe(Hk3IndustrialRecipeTypes.REGENERATION,"industrial_separation_residue_purge",15,500,"RN-BCE",null)
                .inputItems(item("separation_residue",16)).inputItems(TagPrefix.dust,GTMaterials.Carbon,4)
                .inputFluids(GTMaterials.Water.getFluid(1000))
                .outputItems(item("inactive_fuel_residue",8)).outputFluids(fluid("unrecoverable_process_effluent",1000)).save(provider);

        // 仅处理储罐中的多余量；正常回路优先回流或制新介质，排污不可再提取崩坏能。
        for (String excess : new String[]{"honkai_mother_liquor", "clarified_honkai_mother_liquor",
                "honkai_separation_medium", "honkai_stabilization_medium"}) {
            recipe(Hk3IndustrialRecipeTypes.REGENERATION,"industrial_purge_"+excess,16,400,"RN-BCE",null)
                    .inputFluids(fluid(excess,1000)).inputItems(TagPrefix.dust,GTMaterials.Carbon,4)
                    .outputFluids(fluid("unrecoverable_process_effluent",1000)).save(provider);
        }
    }
}
'''.replace('@STAMP@', STAMP)
put(BASE + 'common/recipe/honkai/Hk3LiquidLoopRecipes.java', new_java)

comment = f'变更记录 #87 {STAMP}（内测5修订87）：删除无；新增除杂母液双语名；对应独立注册流体，不更改原含能母液。'
for lang, name in [('zh_cn', '除杂崩坏能母液'), ('en_us', 'Clarified Honkai Mother Liquor')]:
    rel = f'src/main/resources/assets/hk3gtl/lang/{lang}.json'
    data = json.loads((ROOT / rel).read_text(encoding='utf-8'))
    data['material.hk3gtl.clarified_honkai_mother_liquor'] = name
    data['_comment_revision87'] = comment
    put(rel, json.dumps(data, ensure_ascii=False, indent=2) + '\n')

rel = 'src/main/resources/assets/hk3gtl/changelog.json'
data = json.loads((ROOT / rel).read_text(encoding='utf-8'))
data['entries'].insert(0, {'version': '0.5.0', 'revision': 87, 'codename': 'HK3GTL-内测5', 'date': STAMP[:10], 'time': STAMP[11:],
    'reason': '落实负责人批准的L1主产量不变、母液回流、化工支线和采集不消耗标准样本。',
    'changes': ['变更记录 #87：删除无；修改前逐文件备份，保留全部历史记录。',
    '修改：净化320粒子及500mB除杂母液；介质再生消耗8残渣、4杂质；4分馏对应5稳定化，主产量5000/800mB不变。',
    '新增：7500mB新采液与500mB除杂母液共同分馏，仍投入碳、滤芯、基质及MAX电力。',
    '新增：前级GT混合机的醇水碱性分析试剂，以及I05各类剩余物料有损处置出口。',
    '修改：高效采集4份参考样本为不消耗标准件，I07校准仍正常消耗样本。',
    '边界：I04/I05正式结构仍待审批；静态数量核验与构建单独记录，不表示游戏验收。']})
put(rel, json.dumps(data, ensure_ascii=False, indent=2) + '\n')

rel = 'doc/崩坏三-GTL/00_项目总览/模组全面系统性分析报告_v5.md'
s = (ROOT / rel).read_text(encoding='utf-8')
s += f'''

## 内测5修订87增补：L1配平、母液回流与采集标准件

【变更记录 #1】{STAMP}（内测5修订87）

- 删除：无，保留既有审查历史与L2工艺。
- 修改：净化粒子256→320；4次分馏、4次净化所得1280粒子可制造80晶种，供5次稳定化，仍输出每批5000mB粗液、每次800mB稳定液。
- 新增：净化同时产500mB除杂母液；I03可用7500mB新采液+500mB除杂母液代替8000mB新采液，碳、滤芯、结晶基质、EU和工时不减。除杂母液没有挤占粒子提取原料，起步使用原新鲜分馏路线。
- 修改：I05每次再生消耗残渣8、杂质4。按4分馏/4净化/5稳定/5再生，杂质净余4、残渣净余32；均有独立有损出口，不要求相互配对。
- 新增：GT混合机用750mB蒸馏水、250mB乙醇、2氢氧化钠粉制造1000mB分析试剂，无崩坏研究门槛。4净化的废试剂回收1200mB，而5再生需要2500mB，差额1300mB由化工补充；不是声称试剂闭环零损耗。
- 新增：原母液、除杂母液、分离介质、稳定介质可在I05有损转为不可再生废液；经固化与已有离心配方转为灰。避免晶种产量配平后多余介质堵仓。
- 修改：I01高效采集保留4份参考样本作为不消耗标准件；I07校准及研究支付不变，钨钢板、铂线和EU仍消耗。
- 用途：修复数量赤字与主线逐批依赖谱图样本的问题；最初研究和探测器校准仍需要I02支线。
- 边界：这里的配平是批次供需与有损循环核验，并非真实化学元素守恒；研究解锁前需缓存副产物。I04/I05仍使用待替换旧结构，本条不代表L1实机完成；构建与数量报告见logs/revision87。
'''
put(rel, s)
LOG.mkdir(parents=True, exist_ok=True)
(LOG / 'application.json').write_text(json.dumps({'time': STAMP, 'revision': 87, 'files': changes, 'game_tested': False, 'deployed': False}, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'time': STAMP, 'changed_files': len(changes)}, ensure_ascii=False))

# 变更记录 · 2026-10-17 14:12:52 · 内测5修订161：业务命名与当前资源、类和工具互引同步；历史证据路径及版本说明保留，不执行历史部署。
