package com.sirin.hk3gtl.common.recipe;

import com.gregtechceu.gtceu.api.GTValues;
import com.gregtechceu.gtceu.api.machine.multiblock.CleanroomType;
import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import com.gregtechceu.gtceu.data.recipe.builder.GTRecipeBuilder;
import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.item.Hk3CircuitCatalog;
import com.sirin.hk3gtl.common.item.Hk3CircuitItems;
import com.sirin.hk3gtl.common.item.main.Hk3MainMaterialItems;
import com.sirin.hk3gtl.common.recipe.power.Hk3RecipePower;
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
            case "soulium_lattice", "honkai_resonance", "rhythmic_coupling", "quantum_bridge" -> 0;
            case "quantum_coherence", "entanglement_anchor", "quantum_interference", "imaginary_anchoring" -> 1;
            case "imaginary_reconstruction", "world_weaving", "causal_reconstruction", "terminal_computation" -> 2;
            case "civilization_endurance" -> 3;
            default -> throw new IllegalArgumentException("未知电路系列：" + entry.family());
        };
    }

    /** 将电子制造成本集中接入原配方入口；同系列升级必须消耗具体上一形态。 */
    public static GTRecipeBuilder assemble(GTRecipeBuilder builder, String id, long eut) {
        var entry = Hk3CircuitCatalog.ENTRIES.stream().filter(e -> e.id().equals(id)).findFirst().orElseThrow();
        int p = platform(entry);
        Hk3RecipeResearchGate.bindAll(builder.recipeType.registryName.getPath(), builder.id.getPath(),
                com.sirin.hk3gtl.common.research.Hk3ElectronicResearch.requirements(p));
        int form = entry.form();
        int units = 1 << form;
        builder.EUt(eut).duration((600 + p * 240) * (form + 1))
                .inputItems(part(p, "printed_circuit_board", units))
                .inputItems(part(p, "ram_chip", 4 * units))
                .inputItems(part(p, "interconnect_mesh", 2 * units))
                .inputItems(Hk3MainMaterialItems.stack(entry.tier(), form == 0 ? "foil" : "plate", 2 * units));
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

    /** 每种电路首制消耗本阶主材，使用前一阶供电；同系列必须真实生产前一形态。 */
    public static void registerSeeds(Consumer<FinishedRecipe> provider) {
        for (var entry : Hk3CircuitCatalog.ENTRIES) {
            int powerTier = entry.tier() - 1;
            var builder = assemble(GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_main_circuit_" + entry.id()),
                    entry.id(), Hk3Values.VA_LONG[powerTier]);
            if (powerTier > GTValues.MAX) Hk3RecipePower.require(builder, powerTier);
            builder.duration(2400 + (entry.tier() - Hk3Tiers.HBV) * 600).save(provider);
        }
    }
}

