package com.sirin.hk3gtl.common.machine.energy;

import com.gregtechceu.gtceu.api.capability.recipe.IO;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.gregtechceu.gtceu.common.data.GTMaterials;
import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import com.gregtechceu.gtceu.data.recipe.builder.GTRecipeBuilder;
import com.lowdragmc.lowdraglib.side.fluid.FluidStack;
import com.sirin.hk3gtl.common.registration.Hk3IndustrialFluids;
import net.minecraft.resources.ResourceLocation;
import org.gtlcore.gtlcore.api.recipe.RecipeCacheStrategy;
import org.gtlcore.gtlcore.api.recipe.RecipeRunnerHelper;
import org.gtlcore.gtlcore.common.data.GTLMaterials;

import java.util.Map;

public final class Hk3ReactorCooling {
    private Hk3ReactorCooling() {}

    public enum Coolant {
        INDUSTRIAL("honkai_coolant", 24, 480),
        PURIFIED_16("grade_16_purified_water", 18, 320),
        PURIFIED_8("grade_8_purified_water", 12, 240),
        DISTILLED("distilled_water", 9, 200),
        WATER("water", 6, 160);

        private final String id;
        private final int heatPerMb;
        private final int capacityPerCycle;

        Coolant(String id, int heatPerMb, int capacityPerCycle) {
            this.id = id;
            this.heatPerMb = heatPerMb;
            this.capacityPerCycle = capacityPerCycle;
        }

        public String id() { return id; }
        public int heatPerMb() { return heatPerMb; }
        public int capacityPerCycle() { return capacityPerCycle; }

        public FluidStack input(int amount) {
            return switch (this) {
                case INDUSTRIAL -> Hk3IndustrialFluids.materials().get("honkai_coolant").getFluid(amount);
                case PURIFIED_16 -> GTLMaterials.GradePurifiedWater16.getFluid(amount);
                case PURIFIED_8 -> GTLMaterials.GradePurifiedWater8.getFluid(amount);
                case DISTILLED -> GTMaterials.DistilledWater.getFluid(amount);
                case WATER -> GTMaterials.Water.getFluid(amount);
            };
        }

        public FluidStack output(int amount) {
            return this == INDUSTRIAL
                    ? Hk3IndustrialFluids.materials().get("hot_honkai_coolant").getFluid(amount)
                    : GTMaterials.Steam.getFluid(amount * 160);
        }
    }

    public static double cool(Hk3ReactorMachine machine, boolean highGrade, double heat,
                              int rodsPerBatch, int activityMultiplier) {
        for (var coolant : Coolant.values()) {
            if (highGrade && coolant != Coolant.INDUSTRIAL) continue;
            double cooling = Math.min(heat, coolant.capacityPerCycle() * rodsPerBatch * 16 * activityMultiplier);
            int low = 0, high = (int) Math.ceil(cooling / coolant.heatPerMb());
            while (low < high) {
                int amount = (low + high + 1) / 2;
                if (exchange(machine, coolant.input(amount), coolant.output(amount), true)) low = amount;
                else high = amount - 1;
            }
            if (low == 0) continue;
            exchange(machine, coolant.input(low), coolant.output(low), false);
            return Math.min(cooling, low * coolant.heatPerMb());
        }
        return 0;
    }

    private static boolean exchange(Hk3ReactorMachine machine, FluidStack input, FluidStack output, boolean simulate) {
        var recipe = new GTRecipeBuilder(new ResourceLocation("hk3gtl", "reactor_runtime_cooling"),
                GTRecipeTypes.DUMMY_RECIPES).inputFluids(input).outputFluids(output).buildRawRecipe();
        return transfer(machine, recipe, IO.IN, simulate) && transfer(machine, recipe, IO.OUT, simulate);
    }

    private static boolean transfer(Hk3ReactorMachine machine, GTRecipe recipe, IO io, boolean simulate) {
        return RecipeRunnerHelper.handleRecipe(io, machine, io == IO.IN ? recipe.inputs : recipe.outputs,
                Map.of(), false, recipe, simulate, RecipeCacheStrategy.NO_CACHE).isSuccess();
    }
}
