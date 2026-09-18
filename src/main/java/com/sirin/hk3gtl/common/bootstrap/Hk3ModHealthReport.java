package com.sirin.hk3gtl.common.bootstrap;

import com.sirin.hk3gtl.common.block.Hk3Blocks;
import com.sirin.hk3gtl.common.item.Hk3Items;
import com.sirin.hk3gtl.common.item.honkai.HonkaiMaterialItems;
import net.minecraft.world.level.material.Fluid;
import com.sirin.hk3gtl.common.machine.Hk3Machines;
import com.sirin.hk3gtl.common.machine.Hk3MachinesAbyssStage;
import com.sirin.hk3gtl.common.machine.Hk3MachinesImaginaryStage;
import com.sirin.hk3gtl.common.machine.Hk3MachinesMaxStage;
import com.sirin.hk3gtl.common.machine.Hk3MachinesQuantumStage;
import com.sirin.hk3gtl.common.material.Hk3Materials;
import com.sirin.hk3gtl.common.recipe.Hk3RecipeTypes;
import com.sirin.hk3gtl.common.recipe.Hk3RecipeTypesImaginary;
import com.sirin.hk3gtl.common.recipe.Hk3RecipeTypesQuantum;
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
        lines.add("p1_machines:" + (s.p1MachinesOk ? "ok" : "fail"));
        lines.add("abyss_machines:" + (s.abyssMachinesOk ? "ok" : "fail"));
        lines.add("imaginary_machines:" + (s.imaginaryMachinesOk ? "ok" : "fail"));
        lines.add("quantum_machines:" + (s.quantumMachinesOk ? "ok" : "fail"));
        lines.add("max_machines:" + (s.maxMachinesOk ? "ok" : "fail"));
        lines.add("recipe_types:" + (s.recipeTypesOk ? "ok" : "fail"));
        lines.add("gtceu:" + (s.gtceuLoaded ? "ok" : "fail"));
        return lines;
    }

    private static Snapshot collect() {
        int itemCount = countDeferred(Hk3Items.ITEMS);
        int blockCount = countDeferred(Hk3Blocks.BLOCKS);
        int fluidCount = fluidsRegistered() ? 1 : 0;

        boolean itemsOk = itemCount > 0 && HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL != null;
        boolean blocksOk = blockCount > 0;
        boolean fluidsOk = fluidCount > 0 && isFluidRegistered(Hk3Materials.LIQUID_HONKAI_ENERGY);

        boolean p1Ok = Hk3Machines.HONKAI_ABSORPTION_TOWER != null
                && Hk3Machines.HONKAI_CRYSTAL_CONDENSER != null
                && Hk3Machines.SOULIUM_SMELTERY != null;

        boolean abyssOk = Hk3MachinesAbyssStage.LARGE_HONKAI_REACTOR != null
                && Hk3MachinesMaxStage.ABYSS_CIRCUIT_FOUNDRY != null
                && Hk3MachinesAbyssStage.ABYSS_PRECISION_WORKSHOP != null;

        boolean imaginaryOk = Hk3MachinesImaginaryStage.IMAGINARY_CIRCUIT_COMPUTATION_SANCTUM != null
                && Hk3MachinesImaginaryStage.IMAGINARY_ANCHOR_DEVICE != null
                && Hk3MachinesImaginaryStage.PRECIVILIZATION_DATABASE_DECODER != null;

        boolean quantumOk = Hk3MachinesQuantumStage.QUANTUM_ENTANGLEMENT_COMPUTER != null
                && Hk3MachinesQuantumStage.QUANTUM_PRECISION_ASSEMBLY_FACTORY != null
                && Hk3MachinesQuantumStage.WORLD_BUBBLE_MELTDOWN_FURNACE != null;

        // 内测四：Max 阶段 + 崩坏能无线网络入口（EU 转换塔 / 网络注入器 / 虚空档案解析室）
        boolean maxOk = Hk3MachinesMaxStage.HONKAI_EU_CONVERTER != null
                && Hk3MachinesMaxStage.HONKAI_NETWORK_INJECTOR != null
                && Hk3MachinesMaxStage.VOID_ARCHIVES_ANALYSIS_CHAMBER != null;

        boolean recipeOk = Hk3RecipeTypes.HONKAI_ABSORPTION_RECIPES != null
                && Hk3RecipeTypes.ABYSS_CIRCUIT_FOUNDRY_RECIPES != null
                && Hk3RecipeTypesImaginary.IMAGINARY_CIRCUIT_COMPUTATION != null
                && Hk3RecipeTypesQuantum.QUANTUM_PRECISION_ASSEMBLY != null
                && Hk3RecipeTypes.HONKAI_NETWORK_INJECTION_RECIPES != null;

        boolean gtceu = ModList.get().isLoaded("gtceu");

        return new Snapshot(
                itemsOk, blocksOk, fluidsOk, p1Ok, abyssOk, imaginaryOk, quantumOk, maxOk, recipeOk, gtceu,
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
            boolean p1MachinesOk,
            boolean abyssMachinesOk,
            boolean imaginaryMachinesOk,
            boolean quantumMachinesOk,
            boolean maxMachinesOk,
            boolean recipeTypesOk,
            boolean gtceuLoaded,
            int itemCount,
            int blockCount,
            int fluidCount) {

        static Snapshot empty() {
            return new Snapshot(false, false, false, false, false, false, false, false, false, false, 0, 0, 0);
        }

        public boolean allCriticalOk() {
            return itemsOk && blocksOk && fluidsOk && p1MachinesOk && abyssMachinesOk
                    && imaginaryMachinesOk && quantumMachinesOk && maxMachinesOk
                    && recipeTypesOk && gtceuLoaded;
        }
    }
}
