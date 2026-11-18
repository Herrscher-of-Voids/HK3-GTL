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
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.Ingredient;

import com.gregtechceu.gtceu.data.recipe.builder.GTRecipeBuilder;
import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate;
import org.gtlcore.gtlcore.common.data.GTLMaterials;
import static com.sirin.hk3gtl.common.recipe.honkai.Hk3LiquidLineRecipes.item;
import static com.sirin.hk3gtl.common.recipe.honkai.Hk3LiquidLineRecipes.fluid;

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

    private static ItemStack precursor(int platform, String part, String maxItem, int count) {
        return platform == 0
                ? new ItemStack(BuiltInRegistries.ITEM.get(new ResourceLocation("kubejs", maxItem)), count)
                : part(platform - 1, part, count);
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
                .inputItems(precursor(p, "circuit_substrate", "supracausal_circuit_board", 2))
                .inputItems(precursor(p, "printed_circuit_board", "supracausal_printed_circuit_board", 2))
                .inputFluids(fluid("circuit_growth_medium", 500 * (p + 1)))
                .outputItems(part(p, "circuit_substrate", 2)).save(provider);
        process(p, GTRecipeTypes.CHEMICAL_BATH_RECIPES, "printed_circuit_board", 600 + p * 200)
                .inputItems(part(p, "circuit_substrate", 1))
                .inputFluids(fluid("honkai_circuit_etchant", 500 * (p + 1)))
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
        if (p == 0) memory.inputItems(precursor(p, "ram_wafer", "supracausal_ram_wafer", 4));
        else memory.inputItems(part(p - 1, "ram_wafer", 1));
        memory.outputItems(part(p, "ram_wafer", 1)).save(provider);
        process(p, GTRecipeTypes.CUTTER_RECIPES, "ram_chip", 800 + p * 200)
                .inputItems(part(p, "ram_wafer", 1)).inputFluids(fluid("honkai_coolant", 250))
                .outputItems(part(p, "ram_chip", 16)).save(provider);
        var cpu = process(p, GTRecipeTypes.ASSEMBLER_RECIPES, "cpu", 1000 + p * 300)
                .inputItems(part(p, "logic_die", 2)).inputItems(part(p, "smd_array", 1))
                .inputItems(part(p, "ram_chip", 4)).inputItems(part(p, "interconnect_mesh", 2))
                .inputItems(item("circuit_encapsulation_part", 1));
        if (p == 0) cpu.inputItems(Ingredient.of(
                new ItemStack(BuiltInRegistries.ITEM.get(new ResourceLocation("kubejs", "supracausal_mainframe"))),
                new ItemStack(BuiltInRegistries.ITEM.get(new ResourceLocation("kubejs", "suprachronal_max")))));
        else cpu.inputItems(part(p - 1, "cpu", 1));
        cpu.inputFluids(fluid("circuit_growth_medium", 250 * (p + 1)))
                .outputItems(part(p, "cpu", 1)).save(provider);
    }

    /** 各元件保留电学材料用途；平台成本来自上游介电层、互连和HK3工业工况。 */
    private static void registerComponents(int p, Consumer<FinishedRecipe> provider) {
        String[] names = {"smd_capacitor", "smd_diode", "smd_resistor", "smd_transistor", "smd_inductor"};
        for (int component = 0; component < names.length; component++) {
            var builder = process(p, GTRecipeTypes.ASSEMBLER_RECIPES, names[component], 300 + p * 100)
                    .inputItems(part(p, "dielectric_film", 2)).inputItems(part(p, "interconnect_mesh", 2))
                    .inputItems(precursor(p, names[component], names[component] + "_supracausal", 8));
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

