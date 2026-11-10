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

/**
 * 【文件职责】
 * - 汇总模组注册健康状态，供进世界欢迎弹窗与日志使用。
 * - 调用链：FMLCommonSetupEvent -> refresh() -> PlayerLoggedIn -> ModWelcomeS2CPacket。
 *
 * 【变更记录】2026-05-19
 * - 新增：内测二进世界加载自检（物品/流体/多方块/配方类型）。
 *
 * 【变更记录 #2】2026-06-01 18:00:00（第 2 次备注 · 内测三第 10 次更新）
 * - 新增：
 *   1) 自检页面新增「量子多方块」项 quantumMachinesOk（校验纠缠计算机/精密装配厂/世界泡熔炉非空）。
 *   2) recipeTypesOk 追加校验 QUANTUM_PRECISION_ASSEMBLY，覆盖量子配方类型注册。
 *   3) Snapshot 记录与 allCriticalOk 同步纳入量子项。
 * - 用途：
 *   1) 内测三补全量子工业链后，进世界自检页需反映量子阶段注册健康度。
 *
 * 【变更记录 #3】2026-07-06（第 3 次备注 · 内测四第 1 次更新）
 * - 新增：
 *   1) 自检项「Max 多方块 / 崩坏能网络」maxMachinesOk：校验崩坏能-EU 转换塔、崩坏能网络注入器、虚空档案解析室非空。
 *   2) recipeTypesOk 追加校验 HONKAI_NETWORK_INJECTION_RECIPES（崩坏能充网配方类型）。
 * - 用途：
 *   1) 内测四实装双能源无线网络（崩坏能网 + 注入器）后，自检页需反映其注册健康度。
 */
/** 中文说明：该处说明已按当前代码行为整理。*/
/** 中文说明：该处说明已按当前代码行为整理。*/
/** 中文说明：该处说明已按当前代码行为整理。*/
/** 变更记录 #1 · 2026-09-24 16:38:31 · 内测5修订66：新增七设备及专用类型健康检查；删除遗漏判定，保留原检查；用途为防止半条产线启动。 */
/**
 * 【变更记录 #4】2026-10-01 21:41:57（第4次备注 · 内测5修订151）
 * 删除：内测1—4旧结构相关入口。新增：无替代结构。
 * 修改：自检只检查当前10个内测5注册入口；去掉已删除旧阶段检查项，不以旧机器缺席判启动失败。
 * 用途：落实旧结构全部退役；内测5未审批设备仍待接入，不保留空注册兼容。
 */
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

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。

// 【变更记录 · 修订162】2026-10-17 14:40:05：删除三项退役配方表健康依赖；保留现行工业类型及研究所检查，不为通过检查重新注册旧类型。
