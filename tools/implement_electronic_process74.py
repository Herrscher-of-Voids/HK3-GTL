"""修订74：建立HK3高阶电子工序，复用工业材料并增加必要半成品。

原料与配方依据：指定实例GTL高阶板材、层压存储、处理核心及封装链。
本脚本替换已确认错误的低级GT映射，保留历史备注并生成可复查生产目录。
"""
import json
import re
from revision74_support import JAVA, RES, LOG, patch_java, new_java, write, note, save_json

PARTS = ['dielectric_film', 'interconnect_mesh', 'epitaxial_wafer', 'logic_wafer', 'logic_die', 'smd_array']


def main():
    patch_java('common/item/Hk3ElectronicItems.java',
        lambda s: s.replace('"ram_wafer", "ram_chip", "cpu");',
            '"ram_wafer", "ram_chip", "cpu",\n            "dielectric_film", "interconnect_mesh", "epitaxial_wafer", "logic_wafer", "logic_die", "smd_array");'),
        '删除：无注册键。新增：每平台介电膜、互连网、外延晶圆、逻辑晶圆、裸片及贴片阵列，共24个半成品。\n * 修改：原40件保持不变；总计64件，均通过现有注册与创造栏入口展示。\n * 用途：把层压、光刻、切割和封装分开，避免普通纳米CPU直接改名成为高阶CPU。')
    p = JAVA/'common/recipe/Hk3ElectronicRecipes.java'
    old = p.read_text('utf-8')
    # 保留全部既有备注，在原类位置替换错误工艺。
    header = old[:old.index('public final class Hk3ElectronicRecipes')]
    imports = '''import com.gregtechceu.gtceu.data.recipe.builder.GTRecipeBuilder;
import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import com.sirin.hk3gtl.common.item.quantum.QuantumComponentItems;
import com.sirin.hk3gtl.common.item.soulium.SouliumChainItems;
import com.sirin.hk3gtl.common.material.SouliumMaterial;
import com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate;
import org.gtlcore.gtlcore.common.data.GTLMaterials;
import static com.sirin.hk3gtl.common.recipe.honkai.Hk3LiquidLineRecipes.item;
import static com.sirin.hk3gtl.common.recipe.honkai.Hk3LiquidLineRecipes.fluid;

'''
    header = header.replace('/**', imports + '/**', 1)
    body = '''public final class Hk3ElectronicRecipes {
    private static final int[] PREDECESSOR_TIERS = {
            GTValues.MAX, Hk3Tiers.ABYSS_4, Hk3Tiers.IMAGINARY_4, Hk3Tiers.QUANTUM_4};
    private static final String[] GATES = {"RN-BCE", "R-AB-022", "R-IM-004", "R-QT-011"};
    private Hk3ElectronicRecipes() {}

    /** 起步使用已有GT设备，后三平台使用前一个阶段已经能建造的专用工坊。 */
    public static GTRecipeType machine(int platform, GTRecipeType bootstrap) {
        return switch (platform) {
            case 0 -> bootstrap;
            case 1 -> Hk3RecipeTypes.ABYSS_PRECISION_ASSEMBLY_RECIPES;
            case 2 -> Hk3RecipeTypesImaginary.IMAGINARY_CIRCUIT_COMPUTATION;
            case 3 -> Hk3RecipeTypesQuantum.QUANTUM_PRECISION_ASSEMBLY;
            default -> throw new IllegalArgumentException("未知电子平台：" + platform);
        };
    }

    public static int predecessorTier(int platform) { return PREDECESSOR_TIERS[platform]; }
    public static String gate(int platform) { return GATES[platform]; }
    public static ItemStack part(int platform, String part, int count) {
        return Hk3ElectronicItems.stack(Hk3ElectronicItems.PLATFORMS.get(platform), part, count);
    }

    private static GTRecipeBuilder process(int platform, GTRecipeType bootstrap, String output, int ticks) {
        GTRecipeType type = machine(platform, bootstrap);
        String id = "hk3gtl_electronic_" + Hk3ElectronicItems.PLATFORMS.get(platform) + "_" + output;
        Hk3RecipeResearchGate.bind(type.registryName.getPath(), id, GATES[platform]);
        return type.recipeBuilder(id).duration(ticks).EUt(Hk3Values.VA_LONG[PREDECESSOR_TIERS[platform]])
                .cleanroom(CleanroomType.CLEANROOM);
    }

    private static GTRecipeBuilder support(int platform, GTRecipeType bootstrap, String id, int ticks) {
        GTRecipeType type = machine(platform, bootstrap);
        Hk3RecipeResearchGate.bind(type.registryName.getPath(), id, GATES[platform]);
        return type.recipeBuilder(id).duration(ticks).EUt(Hk3Values.VA_LONG[PREDECESSOR_TIERS[platform]]);
    }

    public static void register(Consumer<FinishedRecipe> provider) {
        registerIndustrialInputs(provider);
        for (int platform = 0; platform < Hk3ElectronicItems.PLATFORMS.size(); platform++) {
            registerLayers(platform, provider);
            registerSemiconductors(platform, provider);
            registerComponents(platform, provider);
        }
        Hk3CircuitManufacturing.registerSeeds(provider);
    }

    /** 复用已注册的介质、掩膜、封装件和三类工业材料，补上其真实生产入口。 */
    private static void registerIndustrialInputs(Consumer<FinishedRecipe> provider) {
        support(0, GTRecipeTypes.MIXER_RECIPES, "hk3gtl_electronic_growth_medium", 600)
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 4))
                .inputItems(TagPrefix.dust, GTMaterials.Silicon, 16)
                .inputFluids(fluid("stabilized_liquid_honkai_energy", 1000), GTMaterials.Polybenzimidazole.getFluid(144))
                .outputFluids(fluid("circuit_growth_medium", 1000)).save(provider);
        support(0, GTRecipeTypes.CHEMICAL_RECIPES, "hk3gtl_electronic_etchant", 500)
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 2))
                .inputFluids(GTMaterials.Iron3Chloride.getFluid(1000), GTMaterials.SodiumPersulfate.getFluid(1000))
                .outputFluids(fluid("honkai_circuit_etchant", 2000)).save(provider);
        support(0, GTRecipeTypes.LASER_ENGRAVER_RECIPES, "hk3gtl_electronic_lithography_mask", 800)
                .inputItems(TagPrefix.plate, GTMaterials.Neutronium)
                .notConsumable(TagPrefix.lens, Color.Green)
                .outputItems(item("circuit_lithography_mask", 1)).cleanroom(CleanroomType.CLEANROOM).save(provider);
        support(0, GTRecipeTypes.CHEMICAL_BATH_RECIPES, "hk3gtl_electronic_etched_layer", 600)
                .inputItems(item("honkai_adapted_circuit_substrate", 1))
                .inputFluids(fluid("honkai_circuit_etchant", 250))
                .outputItems(item("etched_circuit_layer", 1)).cleanroom(CleanroomType.CLEANROOM).save(provider);
        support(0, GTRecipeTypes.ASSEMBLER_RECIPES, "hk3gtl_electronic_encapsulation", 400)
                .inputItems(TagPrefix.plate, GTMaterials.Neutronium, 2)
                .inputItems(TagPrefix.foil, GTMaterials.Polybenzimidazole, 8)
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 2))
                .inputFluids(fluid("circuit_growth_medium", 250))
                .outputItems(item("circuit_encapsulation_part", 4)).save(provider);
        support(1, GTRecipeTypes.ASSEMBLER_RECIPES, "hk3gtl_electronic_soulium_carrier", 800)
                .inputItems(TagPrefix.plate, SouliumMaterial.SOULIUM, 4)
                .inputItems(part(0, "printed_circuit_board", 2))
                .inputFluids(fluid("circuit_growth_medium", 500))
                .outputItems(item("soulium_data_substrate", 4)).save(provider);
        support(1, GTRecipeTypes.ASSEMBLER_RECIPES, "hk3gtl_electronic_conducting_composite", 1000)
                .inputItems(TagPrefix.wireFine, SouliumMaterial.SOULIUM, 16)
                .inputItems(new ItemStack(HonkaiMaterialItems.EINSTEIN_RINGMAGNET.get(), 1))
                .inputItems(new ItemStack(HonkaiMaterialItems.STABILIZED_HONKAI_CRYSTAL.get(), 4))
                .inputFluids(fluid("circuit_growth_medium", 500))
                .outputItems(item("conducting_composite", 8)).save(provider);
        support(2, GTRecipeTypes.ASSEMBLER_RECIPES, "hk3gtl_electronic_reconstructing_composite", 1400)
                .inputItems(item("conducting_composite", 4))
                .inputItems(new ItemStack(SouliumChainItems.ORIENTED_SOULIUM_COMPONENT.get(), 2))
                .inputItems(new ItemStack(HonkaiMaterialItems.SCHICKSAL_IMAGINARY_CORE.get(), 1))
                .inputItems(new ItemStack(HonkaiMaterialItems.ANTI_ENTROPY_IMAGINARY_CORE.get(), 1))
                .inputItems(part(1, "logic_die", 4)).inputFluids(fluid("circuit_growth_medium", 1000))
                .outputItems(item("reconstructing_composite", 8)).save(provider);
        support(3, GTRecipeTypes.ASSEMBLER_RECIPES, "hk3gtl_electronic_cognitive_composite", 1800)
                .inputItems(item("reconstructing_composite", 4))
                .inputItems(part(2, "cpu", 2)).inputItems(part(2, "ram_chip", 8))
                .inputItems(new ItemStack(QuantumComponentItems.SENSOR_QUANTUM_2.get(), 1))
                .inputFluids(fluid("circuit_growth_medium", 1000))
                .outputItems(item("cognitive_composite", 8)).save(provider);
    }

    private static ItemStack carrier(int platform, int count) {
        String[] ids = {"honkai_adapted_circuit_substrate", "soulium_data_substrate",
                "reconstructing_composite", "cognitive_composite"};
        return item(ids[platform], count);
    }

    /** 工艺差异由HK3载体与定向材料决定，不再把普通纤维板复制四遍。 */
    private static void registerLayers(int p, Consumer<FinishedRecipe> provider) {
        process(p, GTRecipeTypes.ASSEMBLER_RECIPES, "dielectric_film", 400 + p * 200)
                .inputItems(carrier(p, 1)).inputItems(TagPrefix.foil, GTMaterials.Polybenzimidazole, 8)
                .inputFluids(fluid("stabilized_liquid_honkai_energy", 250 * (p + 1)))
                .outputItems(part(p, "dielectric_film", 8)).save(provider);
        var mesh = process(p, GTRecipeTypes.ASSEMBLER_RECIPES, "interconnect_mesh", 400 + p * 160)
                .inputItems(TagPrefix.wireFine, GTLMaterials.Shirabon, 16)
                .inputItems(part(p, "dielectric_film", 2));
        if (p > 0) mesh.inputItems(item("conducting_composite", p * 2));
        mesh.inputFluids(fluid("circuit_growth_medium", 250)).outputItems(part(p, "interconnect_mesh", 4)).save(provider);
        process(p, GTRecipeTypes.ASSEMBLER_RECIPES, "circuit_substrate", 700 + p * 200)
                .inputItems(carrier(p, 2)).inputItems(part(p, "dielectric_film", 4))
                .inputItems(part(p, "interconnect_mesh", 2)).inputItems(item("etched_circuit_layer", 2))
                .inputFluids(fluid("circuit_growth_medium", 500 * (p + 1)))
                .outputItems(part(p, "circuit_substrate", 2)).save(provider);
        process(p, GTRecipeTypes.CHEMICAL_BATH_RECIPES, "printed_circuit_board", 600 + p * 200)
                .inputItems(part(p, "circuit_substrate", 1)).inputFluids(fluid("honkai_circuit_etchant", 500 * (p + 1)))
                .outputItems(part(p, "printed_circuit_board", 1)).save(provider);
    }

    private static void registerSemiconductors(int p, Consumer<FinishedRecipe> provider) {
        var epitaxy = process(p, GTRecipeTypes.ASSEMBLER_RECIPES, "epitaxial_wafer", 1000 + p * 400)
                .inputItems(GTItems.NEUTRONIUM_WAFER).inputItems(carrier(p, 2))
                .inputItems(part(p, "dielectric_film", 4));
        if (p > 0) epitaxy.inputItems(part(p - 1, "logic_die", 4));
        epitaxy.inputFluids(fluid("circuit_growth_medium", 1000 * (p + 1)))
                .outputItems(part(p, "epitaxial_wafer", 2)).save(provider);
        process(p, GTRecipeTypes.LASER_ENGRAVER_RECIPES, "logic_wafer", 800 + p * 200)
                .inputItems(part(p, "epitaxial_wafer", 1)).notConsumable(item("circuit_lithography_mask", 1))
                .outputItems(part(p, "logic_wafer", 1)).save(provider);
        process(p, GTRecipeTypes.CUTTER_RECIPES, "logic_die", 900 + p * 200)
                .inputItems(part(p, "logic_wafer", 1)).inputFluids(fluid("honkai_coolant", 250))
                .outputItems(part(p, "logic_die", 8)).save(provider);
        var memory = process(p, GTRecipeTypes.FORMING_PRESS_RECIPES, "ram_wafer", 600 + p * 200)
                .inputItems(part(p, "epitaxial_wafer", 1)).notConsumable(item("circuit_lithography_mask", 1));
        if (p == 0) memory.inputItems(GTItems.RANDOM_ACCESS_MEMORY_WAFER);
        else memory.inputItems(part(p - 1, "ram_wafer", 1));
        memory.outputItems(part(p, "ram_wafer", 1)).save(provider);
        process(p, GTRecipeTypes.CUTTER_RECIPES, "ram_chip", 800 + p * 200)
                .inputItems(part(p, "ram_wafer", 1)).inputFluids(fluid("honkai_coolant", 250))
                .outputItems(part(p, "ram_chip", 16)).save(provider);
        process(p, GTRecipeTypes.ASSEMBLER_RECIPES, "cpu", 1000 + p * 300)
                .inputItems(part(p, "logic_die", 2)).inputItems(part(p, "smd_array", 1))
                .inputItems(part(p, "ram_chip", 4)).inputItems(part(p, "interconnect_mesh", 2))
                .inputItems(item("circuit_encapsulation_part", 1))
                .inputFluids(fluid("circuit_growth_medium", 250 * (p + 1)))
                .outputItems(part(p, "cpu", 1)).save(provider);
    }

    /** 各元件保留电学材料用途；平台成本来自上游介电层、互连和HK3工业工况。 */
    private static void registerComponents(int p, Consumer<FinishedRecipe> provider) {
        String[] names = {"smd_capacitor", "smd_diode", "smd_resistor", "smd_transistor", "smd_inductor"};
        for (int component = 0; component < names.length; component++) {
            var builder = process(p, GTRecipeTypes.ASSEMBLER_RECIPES, names[component], 300 + p * 100)
                    .inputItems(part(p, "dielectric_film", 2)).inputItems(part(p, "interconnect_mesh", 2));
            switch (component) {
                case 0 -> builder.inputItems(TagPrefix.foil, GTMaterials.NaquadahAlloy, 4);
                case 1 -> builder.inputItems(TagPrefix.dust, GTMaterials.IndiumGalliumPhosphide, 2);
                case 2 -> builder.inputItems(TagPrefix.dust, GTMaterials.Graphene, 2);
                case 3 -> builder.inputItems(TagPrefix.plate, GTMaterials.Europium, 2);
                case 4 -> builder.inputItems(TagPrefix.ring, GTMaterials.Neutronium, 2);
                default -> throw new IllegalStateException("未知贴片类型");
            }
            builder.inputFluids(fluid("circuit_growth_medium", 125 * (p + 1)))
                    .outputItems(part(p, names[component], 8)).save(provider);
        }
        var array = process(p, GTRecipeTypes.ASSEMBLER_RECIPES, "smd_array", 400 + p * 160);
        for (String part : names) array.inputItems(part(p, part, 4));
        array.inputItems(part(p, "printed_circuit_board", 1)).inputFluids(fluid("circuit_growth_medium", 250))
                .outputItems(part(p, "smd_array", 2)).save(provider);
    }
}
'''
    write(p, note(header + body,
        '删除：普通纤维板、绿透镜RAM放大和纳米CPU直接改名的40条映射。\n * 新增：64条平台工艺、9条工业输入工艺及前级种子路线；复用既有魂钢载体、蚀刻层、封装件和复合材料。\n * 修改：层压→蚀刻、外延→光刻→切割→裸片封装分工；全部输出均有消耗端，贴片阵列包含五种元件。\n * 用途：RN-BCE完成后的MAX设备启动，后续平台使用18/22/26前级工坊；每条最多六种物品输入与一种工坊流体。'))
    new_java('common/recipe/Hk3CircuitManufacturing.java', '''package com.sirin.hk3gtl.common.recipe;

import com.gregtechceu.gtceu.api.GTValues;
import com.gregtechceu.gtceu.api.machine.multiblock.CleanroomType;
import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import com.gregtechceu.gtceu.data.recipe.builder.GTRecipeBuilder;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.item.Hk3CircuitCatalog;
import com.sirin.hk3gtl.common.item.Hk3CircuitItems;
import com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate;
import net.minecraft.data.recipes.FinishedRecipe;
import net.minecraft.world.item.ItemStack;
import java.util.function.Consumer;
import static com.sirin.hk3gtl.common.recipe.Hk3ElectronicRecipes.part;
import static com.sirin.hk3gtl.common.recipe.honkai.Hk3LiquidLineRecipes.item;
import static com.sirin.hk3gtl.common.recipe.honkai.Hk3LiquidLineRecipes.fluid;

public final class Hk3CircuitManufacturing {
    private Hk3CircuitManufacturing() {}

    public static int platform(Hk3CircuitCatalog.Entry entry) {
        return switch (entry.family()) {
            case "soulium_lattice", "honkai_resonance" -> 0;
            case "quantum_coherence", "entanglement_anchor" -> 1;
            case "imaginary_reconstruction", "world_weaving" -> 2;
            case "civilization_endurance" -> 3;
            default -> throw new IllegalArgumentException("未知电路系列：" + entry.family());
        };
    }

    /** 将电子制造成本集中接入原配方入口；同系列升级必须消耗具体上一形态。 */
    public static GTRecipeBuilder assemble(GTRecipeBuilder builder, String id, long eut) {
        var entry = Hk3CircuitCatalog.ENTRIES.stream().filter(e -> e.id().equals(id)).findFirst().orElseThrow();
        int p = platform(entry);
        int form = entry.form();
        int units = 1 << form;
        builder.EUt(eut).duration((600 + p * 240) * (form + 1))
                .inputItems(part(p, "printed_circuit_board", units))
                .inputItems(part(p, "ram_chip", 4 * units))
                .inputItems(part(p, "interconnect_mesh", 2 * units))
                .inputItems(item("circuit_encapsulation_part", units));
        if (form == 0) {
            builder.inputItems(part(p, "cpu", 2)).inputItems(part(p, "smd_array", 2));
        } else {
            var previous = Hk3CircuitCatalog.ENTRIES.stream()
                    .filter(e -> e.family().equals(entry.family()) && e.form() == form - 1).findFirst().orElseThrow();
            builder.inputItems(new ItemStack(Hk3CircuitItems.DETAILED_CIRCUITS.get(previous.id()).get(), 2))
                    .inputItems(part(p, "smd_array", units));
        }
        return builder.inputFluids(fluid("circuit_growth_medium", 500 * units * (p + 1)))
                .outputItems(new ItemStack(Hk3CircuitItems.DETAILED_CIRCUITS.get(id).get(), 1))
                .cleanroom(CleanroomType.CLEANROOM);
    }

    /** 四个平台首枚正式电路可在前级已有机器制造，后续扩产仍走原专用机器。 */
    public static void registerSeeds(Consumer<FinishedRecipe> provider) {
        String[] circuits = {"abyss_1_processor", "imaginary_1_processor", "quantum_1_processor", "finality_1_processor"};
        String[] gates = {"RN-BCE", "R-IM-001", "R-QT-001", "R-FN-001"};
        for (int p = 0; p < circuits.length; p++) {
            var type = Hk3ElectronicRecipes.machine(p, GTRecipeTypes.ASSEMBLER_RECIPES);
            String id = "hk3gtl_electronic_seed_" + circuits[p];
            assemble(type.recipeBuilder(id), circuits[p], Hk3Values.VA_LONG[Hk3ElectronicRecipes.predecessorTier(p)])
                    .duration(2400 * (p + 1)).save(provider);
            Hk3RecipeResearchGate.bind(type.registryName.getPath(), id, gates[p]);
        }
    }
}
''', '删除：无。新增：四形态封装工艺与四平台前级种子配方。\n * 修改：以真实PCB、CPU、RAM、贴片阵列、互连网及封装件组成工艺，不使用铝框/退火铜线冒充终局封装。\n * 用途：复用34条已存在的专用路线及研究绑定，系列升级精确引用前形态；MAX起步不依赖HBV电路或机壳。')
    # 各旧入口只替换完整电路配方块，原研究绑定、非电路配方与历史备注保留。
    changes = []
    for path in (JAVA/'common/recipe').rglob('*.java'):
        if path.name in ['Hk3ElectronicRecipes.java', 'Hk3CircuitManufacturing.java']:
            continue
        source = path.read_text('utf-8')
        def replace(match):
            block = match[0]
            out = re.search(r'\.outputItems\(new ItemStack\(com\.sirin\.hk3gtl\.common\.item\.Hk3CircuitItems\.DETAILED_CIRCUITS\.get\("([^"]+)"\)', block)
            if not out:
                return block
            start = re.search(r'(\S+\.recipeBuilder\("([^"]+)"\))\.EUt\((.*?)\)\.duration\(', block)
            if not start:
                raise ValueError('配方入口无法解析：' + block[:160])
            changes.append({'file': str(path.relative_to(JAVA)), 'recipe': start[2], 'circuit': out[1], 'eut': start[3]})
            return ('        com.sirin.hk3gtl.common.recipe.Hk3CircuitManufacturing.assemble(\n'
                    f'                {start[1]}, "{out[1]}", {start[3]}).save(provider);')
        updated = re.sub(r'(?m)^        [^\n]*\.recipeBuilder\([^;]+?\.save\(provider\);', replace, source)
        if updated != source:
            write(path, note(updated, '删除：本文件完整电路配方中照搬低级纳米电路的输入。\n * 新增：统一高阶封装制造器调用。\n * 修改：只替换正式电路工艺，保留配方ID、设备、电压、既有研究绑定；每批产出一枚，按形态消耗平台部件。\n * 用途：与Hk3ElectronicRecipes形成材料→晶圆→裸片→封装闭环；同系列升级仍限定具体前形态。'))
    assert len(changes) == 34, f'应迁移34条正式电路路线，实际{len(changes)}'
    save_json(LOG/'circuit-migration.json', changes)
    print('已写入64件电子工序、工业输入与前级种子；迁移34条正式电路配方。')


if __name__ == '__main__':
    main()
