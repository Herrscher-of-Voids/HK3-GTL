package com.sirin.hk3gtl.common.recipe;

import com.gregtechceu.gtceu.api.GTValues;
import com.gregtechceu.gtceu.api.data.tag.TagPrefix;
import com.gregtechceu.gtceu.api.recipe.GTRecipeType;
import com.gregtechceu.gtceu.common.data.GTItems;
import com.gregtechceu.gtceu.common.data.GTMaterials;
import com.gregtechceu.gtceu.api.data.chemical.material.MarkerMaterials.Color;
import com.gregtechceu.gtceu.api.machine.multiblock.CleanroomType;
import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.item.Hk3ElectronicItems;
import com.sirin.hk3gtl.common.item.honkai.HonkaiMaterialItems;
import com.sirin.hk3gtl.common.item.main.Hk3MainMaterialItems;
import com.sirin.hk3gtl.common.recipe.power.Hk3RecipePower;
import java.util.function.Consumer;
import net.minecraft.data.recipes.FinishedRecipe;
import net.minecraft.world.item.ItemStack;

import com.gregtechceu.gtceu.data.recipe.builder.GTRecipeBuilder;
import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate;
import org.gtlcore.gtlcore.common.data.GTLMaterials;
import static com.sirin.hk3gtl.common.recipe.honkai.Hk3LiquidLineRecipes.item;
import static com.sirin.hk3gtl.common.recipe.honkai.Hk3LiquidLineRecipes.fluid;

/**
 * 【变更记录 #1】2026-09-25 04:30:00（第 1 次备注 · 内测5修订72）
 * 删除：无。新增：四平台四十种电子部件的制造入口。
 * 修改：前代设备制造新平台部件；CPU封装消耗RAM及五种贴片元件。
 * 用途：为系列电路提供真实生产链；各配方不超过六种物品输入，不依赖待产电路。
 */
/**
 * 【变更记录 #2】2026-09-25 04:48:31（第 2 次备注 · 内测5修订72）
 * 删除：系列升级使用同级通用标签的混用入口。新增：电子部件制造链的明确输入。
 * 修改：PCB增加贴片电阻；CPU使用PCB、RAM和其余四类贴片元件，使十种部件均接入制造链且维持六格物品输入。
 * 用途：让完整电路逐系列组装；保留原配方研究门槛、数量和电压，输入不超过现有槽位。
 */
/**
 * 【变更记录 #3】2026-09-25 05:06:38（第 3 次备注 · 内测5修订73）
 * 删除：无机器使用的纳米制造类型引用。新增：现役精密装配工坊的部件生产入口。
 * 修改：量子相干部件改用海渊精密装配类型，保留前代电压与现有参数。
 * 用途：修复部件配方已注册但没有机器可执行的断链；后续原版配方映射沿用此入口。
 */
/**
 * 【变更记录 #4】2026-09-25 05:07:48（第 4 次备注 · 内测5修订73）
 * 删除：自行拼接的基板、贴片与CPU配方。新增：GTCEu 1.4.4原配方的四平台映射。
 * 修改：保留原版数量、耗时及洁净室条件；电压沿用已确认前代平台值，全部接入现役自有类型。
 * 用途：部件制造以格雷工艺为依据，避免无设备类型和CPU封装的虚构材料依赖。
 */
/**
 * 【变更记录 #5】2026-09-26 01:58:37（第 5 次备注 · 内测5修订74）
 * 删除：普通纤维板、绿透镜RAM放大和纳米CPU直接改名的40条映射。
 * 新增：64条平台工艺、9条工业输入工艺及前级种子路线；复用既有魂钢载体、蚀刻层、封装件和复合材料。
 * 修改：层压→蚀刻、外延→光刻→切割→裸片封装分工；全部输出均有消耗端，贴片阵列包含五种元件。
 * 用途：RN-BCE完成后的MAX设备启动，后续平台使用18/22/26前级工坊；每条最多六种物品输入与一种工坊流体。
 */
/**
 * 【变更记录 #6】2026-09-30 02:17:47（第6次备注 · 内测5修订107）
 * 删除：本文件可执行代码中的旧电压键及常量引用，不保留旧键注册别名。
 * 新增：16档正式缩写作为唯一电压标识；逐文件映射见logs/voltage-keys-r107。
 * 修改：注册、配方、查询或标签引用按原tier序号一一迁移；数值、层级与资源内容保持原义。
 * 用途：避免显示名与实际注册键不一致；历史备注保留，旧存档不自动改写。
 */
/** 【变更记录 #7】2026-10-01 20:58:37（修订149）：删除本轮电路旧研究绑定；新增/修改：四平台基板、CPU、RAM及配套材料共用与正式电路相同的新版研究前置；用途：新版团队研究一致核验，保留材料、耗时、能耗与历史备注，不代表结构已接通。 */
/** 【变更记录 #8】2026-10-17 16:28:34（修订165）：删除后三平台未接线的注册封锁及通用旧复合材载体；新增四平台64种部件的现役GT工艺配方；修改平台载体/互连改用对应族首阶主材，前级供电调用严格额定门槛；用途：为52种正式电路和128八大件提供主材消费者，不将注册等同于GTL高阶承载验收。 */
/** 【变更记录 #9】2026-10-17 16:57:31（第9次备注 · 修订165）：删除无；新增普通化工辅助配方自动复制至大化工后的同权限绑定；修改support同时登记两个实际配方类型路径；用途：修复电子蚀刻液大化工副本绕过RN-BCE的入口，保留原料、产量、电压及历史备注。 */
/** 【变更记录 #10】2026-10-17 17:03:09（第10次备注 · 修订165）：删除互连网对I40后期conducting_composite的早期依赖；新增无；修改使用本族主材细线、介电膜与生长液，需求功率沿GTL总供电规则，不增加单仓额定限制；用途：解除高级互连网与RN-WMS所需IWV电路之间的循环，覆盖本轮#8的单仓工程假设。 */
/** 【变更记录 #11】2026-10-17 17:47:19（第11次备注 · 修订165）：删除十条光刻自动副本未绑定研究及沿用旧功率数据的旁路；新增本注册器专用FinishedRecipe输出守卫；修改复制后的精确费用和权限由Hk3ElectronicRecipeCopies校验并保留，原工艺不变；用途：补齐真实2.8导出发现的光子/维度聚焦副本条件，不影响第三方配方。 */
public final class Hk3ElectronicRecipes {
    private static final int[] PREDECESSOR_TIERS = {
            GTValues.MAX, Hk3Tiers.HDV, Hk3Tiers.QAV, Hk3Tiers.IWV};
    private Hk3ElectronicRecipes() {}

    /** 复用仍有现行设备承载的GT标准工艺，不恢复已退役的专用类型。 */
    public static GTRecipeType machine(int platform, GTRecipeType bootstrap) {
        if (platform < 0 || platform >= PREDECESSOR_TIERS.length || bootstrap == null)
            throw new IllegalArgumentException("非法电子平台或工艺：" + platform);
        return bootstrap;
    }

    public static int predecessorTier(int platform) { return PREDECESSOR_TIERS[platform]; }
    public static String gate(int platform) { return com.sirin.hk3gtl.common.research.Hk3ElectronicResearch.requirements(platform).get(0); }
    public static ItemStack part(int platform, String part, int count) {
        return Hk3ElectronicItems.stack(Hk3ElectronicItems.PLATFORMS.get(platform), part, count);
    }

    private static GTRecipeBuilder process(int platform, GTRecipeType bootstrap, String output, int ticks) {
        GTRecipeType type = machine(platform, bootstrap);
        String id = "hk3gtl_electronic_" + Hk3ElectronicItems.PLATFORMS.get(platform) + "_" + output;
        Hk3RecipeResearchGate.bindAll(type.registryName.getPath(), id, com.sirin.hk3gtl.common.research.Hk3ElectronicResearch.requirements(platform));
        var builder = type.recipeBuilder(id).duration(ticks).EUt(Hk3Values.VA_LONG[PREDECESSOR_TIERS[platform]])
                .cleanroom(CleanroomType.CLEANROOM);
        return platform == 0 ? builder : Hk3RecipePower.require(builder, PREDECESSOR_TIERS[platform]);
    }

    private static GTRecipeBuilder support(int platform, GTRecipeType bootstrap, String id, int ticks) {
        GTRecipeType type = machine(platform, bootstrap);
        Hk3RecipeResearchGate.bindAll(type.registryName.getPath(), id, com.sirin.hk3gtl.common.research.Hk3ElectronicResearch.requirements(platform));
        if (type == GTRecipeTypes.CHEMICAL_RECIPES) {
            Hk3RecipeResearchGate.bindAll(GTRecipeTypes.LARGE_CHEMICAL_RECIPES.registryName.getPath(), id,
                    com.sirin.hk3gtl.common.research.Hk3ElectronicResearch.requirements(platform));
        }
        return type.recipeBuilder(id).duration(ticks).EUt(Hk3Values.VA_LONG[PREDECESSOR_TIERS[platform]]);
    }

    public static void register(Consumer<FinishedRecipe> provider) {
        provider = Hk3ElectronicRecipeCopies.guard(provider);
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
    }

    private static ItemStack carrier(int platform, int count) {
        return Hk3MainMaterialItems.stack(Hk3Tiers.HBV + 4 * platform, "plate", count);
    }

    /** 工艺差异由HK3载体与定向材料决定，不再把普通纤维板复制四遍。 */
    private static void registerLayers(int p, Consumer<FinishedRecipe> provider) {
        process(p, GTRecipeTypes.ASSEMBLER_RECIPES, "dielectric_film", 400 + p * 200)
                .inputItems(carrier(p, 1)).inputItems(TagPrefix.foil, GTMaterials.Polybenzimidazole, 8)
                .inputFluids(fluid("stabilized_liquid_honkai_energy", 250 * (p + 1)))
                .outputItems(part(p, "dielectric_film", 8)).save(provider);
        var mesh = process(p, GTRecipeTypes.ASSEMBLER_RECIPES, "interconnect_mesh", 400 + p * 160)
                .inputItems(Hk3MainMaterialItems.stack(Hk3Tiers.HBV + 4 * p, "fine_wire", 16))
                .inputItems(part(p, "dielectric_film", 2));
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

// 【变更记录 · 修订162】2026-10-17 14:40:05：删除三个退役工坊路由及其48条平台工艺、4条辅助工艺注册；保留MAX平台16条工艺和5条辅助工艺，不将旧路线擅自改挂新设备。
