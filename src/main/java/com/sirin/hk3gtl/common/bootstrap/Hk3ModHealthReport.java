package com.sirin.hk3gtl.common.bootstrap;

import com.sirin.hk3gtl.common.block.Hk3Blocks;
import com.sirin.hk3gtl.common.item.Hk3Items;
import com.sirin.hk3gtl.common.item.honkai.HonkaiMaterialItems;
import net.minecraft.world.level.material.Fluid;
import com.sirin.hk3gtl.common.machine.Hk3Machines;
import com.sirin.hk3gtl.common.machine.Hk3MachinesImpl;
import com.sirin.hk3gtl.common.machine.Hk3MachinesAbyssStage;
import com.sirin.hk3gtl.common.machine.Hk3MachinesMaxStage;
import com.sirin.hk3gtl.common.material.Hk3Materials;
import com.sirin.hk3gtl.common.recipe.Hk3RecipeTypes;
import net.minecraftforge.fml.ModList;
import net.minecraftforge.registries.ForgeRegistries;

import java.util.ArrayList;
import java.util.List;

 






















 
 





public final class Hk3ModHealthReport {

    private static volatile Snapshot cached = Snapshot.empty();

    private Hk3ModHealthReport() {}

    public static void refresh() {
        cached = collect();
    }

    public static Snapshot snapshot() {
        return cached;
    }

    public static List<String> toStatusLines(String modVersion) {
        Snapshot s = cached;
        List<String> lines = new ArrayList<>();
        lines.add("version:" + modVersion);
        lines.add("items:" + (s.itemsOk ? "ok" : "fail") + ":" + s.itemCount);
        lines.add("blocks:" + (s.blocksOk ? "ok" : "fail") + ":" + s.blockCount);
        lines.add("fluids:" + (s.fluidsOk ? "ok" : "fail") + ":" + s.fluidCount);
        lines.add("industrial_machines:" + (s.industrialMachinesOk ? "ok" : "fail"));
        lines.add("recipe_types:" + (s.recipeTypesOk ? "ok" : "fail"));
        lines.add("gtceu:" + (s.gtceuLoaded ? "ok" : "fail"));
        return lines;
    }

    private static Snapshot collect() {
        int itemCount = countDeferred(Hk3Items.ITEMS);
        int blockCount = countDeferred(Hk3Blocks.BLOCKS);
        // 精确查询本批流体ID，气态不通过默认液体槽推测。 / Query exact IDs, including gases.
        int industrialFluidCount = (int) com.sirin.hk3gtl.common.registration.Hk3IndustrialFluids.materials().keySet().stream()
                .filter(id -> ForgeRegistries.FLUIDS.containsKey(new net.minecraft.resources.ResourceLocation("hk3gtl", id)))
                .count();
        int fluidCount = (fluidsRegistered() ? 1 : 0) + industrialFluidCount;

        boolean itemsOk = itemCount > 0 && HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL != null;
        boolean blocksOk = blockCount > 0;
        boolean fluidsOk = isFluidRegistered(Hk3Materials.LIQUID_HONKAI_ENERGY)
                && industrialFluidCount == com.sirin.hk3gtl.common.registration.Hk3IndustrialFluids.materials().size()
                && industrialFluidCount > 0;

        // 内测5活动入口与液态工业线必须同时注册，避免只注册配方类型却没有可用主机。
        boolean industrialOk = Hk3Machines.ABYSS_RESEARCH_ANALYSIS_MATRIX != null
                && Hk3MachinesMaxStage.HONKAI_NETWORK_INJECTOR != null
                && Hk3MachinesImpl.I01_HONKAI_COLLECTION_TOWER != null
                && Hk3MachinesAbyssStage.I02_SPECTRUM_ANALYSIS_ARRAY != null
                && Hk3MachinesImpl.LIQUID_HONKAI_FRACTIONATION_CENTER != null
                && Hk3MachinesImpl.LIQUID_HONKAI_STABILIZATION_TOWER != null
                && Hk3MachinesImpl.STABILIZATION_MEDIUM_REGENERATION_TOWER != null
                && Hk3MachinesImpl.HONKAI_FUEL_BLENDING_PLANT != null
                && Hk3MachinesImpl.HONKAI_DETECTOR_CALIBRATION_BENCH != null
                && Hk3MachinesImpl.HONKAI_FUEL_CONCENTRATION_PLANT != null;

        boolean recipeOk = com.sirin.hk3gtl.common.recipe.Hk3IndustrialRecipeTypes.COLLECTION != null
                && com.sirin.hk3gtl.common.recipe.Hk3IndustrialRecipeTypes.LIQUID_REFINING != null
                && com.sirin.hk3gtl.common.recipe.Hk3IndustrialRecipeTypes.SPECTRUM_ANALYSIS != null
                && com.sirin.hk3gtl.common.recipe.Hk3IndustrialRecipeTypes.NETWORK_INJECTION != null
                && com.sirin.hk3gtl.common.recipe.Hk3IndustrialRecipeTypes.STABILIZATION != null
                && com.sirin.hk3gtl.common.recipe.Hk3IndustrialRecipeTypes.REGENERATION != null
                && com.sirin.hk3gtl.common.recipe.Hk3IndustrialRecipeTypes.FUEL_BLENDING != null
                && com.sirin.hk3gtl.common.recipe.Hk3IndustrialRecipeTypes.CALIBRATION != null
                && com.sirin.hk3gtl.common.recipe.Hk3IndustrialRecipeTypes.CONCENTRATION != null
                && Hk3RecipeTypes.ABYSS_RESEARCH_ANALYSIS_RECIPES != null;

        boolean gtceu = ModList.get().isLoaded("gtceu");

        return new Snapshot(
                itemsOk, blocksOk, fluidsOk, industrialOk, recipeOk, gtceu,
                itemCount, blockCount, fluidCount);
    }

    private static int countDeferred(net.minecraftforge.registries.DeferredRegister<?> registry) {
        int n = 0;
        for (var holder : registry.getEntries()) {
            if (holder.isPresent()) {
                n++;
            }
        }
        return n;
    }

    private static boolean fluidsRegistered() {
        return isFluidRegistered(Hk3Materials.LIQUID_HONKAI_ENERGY);
    }

    /** GT 材料流体是否已进入 Forge 流体注册表 */
    private static boolean isFluidRegistered(com.gregtechceu.gtceu.api.data.chemical.material.Material material) {
        if (material == null) {
            return false;
        }
        Fluid fluid = material.getFluid();
        return fluid != null && ForgeRegistries.FLUIDS.getKey(fluid) != null;
    }

    public record Snapshot(
            boolean itemsOk,
            boolean blocksOk,
            boolean fluidsOk,
            boolean industrialMachinesOk,
            boolean recipeTypesOk,
            boolean gtceuLoaded,
            int itemCount,
            int blockCount,
            int fluidCount) {

        static Snapshot empty() {
            return new Snapshot(false, false, false, false, false, false, 0, 0, 0);
        }

        public boolean allCriticalOk() {
            return itemsOk && blocksOk && fluidsOk && industrialMachinesOk
                    && recipeTypesOk && gtceuLoaded;
        }
    }
}

 

 
