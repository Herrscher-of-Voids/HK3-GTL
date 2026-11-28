package com.sirin.hk3gtl.common.research;

import com.gregtechceu.gtceu.api.capability.recipe.FluidRecipeCapability;
import com.gregtechceu.gtceu.api.capability.recipe.ItemRecipeCapability;
import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.gregtechceu.gtceu.api.machine.feature.IRecipeLogicMachine;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.mojang.logging.LogUtils;
import com.sirin.hk3gtl.common.easter.Hk3EggProduction;
import com.sirin.hk3gtl.common.machine.research.Hk3HonkaiAbsorptionMachine;
import com.sirin.hk3gtl.common.machine.research.Hk3LiquidProcessMachine;
import com.sirin.hk3gtl.common.machine.research.Hk3SpectrumAnalysisMachine;
import com.sirin.hk3gtl.common.narrative.story.Hk3StoryProduction;

public final class Hk3ProductionOutput {
    private Hk3ProductionOutput() {}

    public static void isolatedSettled(MetaMachine machine, GTRecipe recipe) {
        recordOutput((IRecipeLogicMachine) machine, recipe);
        Hk3OutputReceiptDispatch.dispatch(true, () -> Hk3ResearchRecipeRuntime.isolatedSettled(machine, recipe),
                failure -> LogUtils.getLogger().error("HK3GTL 隔离订单交付后的工艺记录失败", failure));
    }

    private static void recordOutput(IRecipeLogicMachine machine, GTRecipe recipe) {
        Hk3OutputReceiptDispatch.dispatch(true, () -> Hk3CircuitTechnology.settled(machine, recipe),
                failure -> LogUtils.getLogger().error("HK3GTL电路制造记录失败", failure));
        Hk3OutputReceiptDispatch.dispatch(true, () -> Hk3StoryProduction.settled(machine, recipe),
                failure -> LogUtils.getLogger().error("HK3GTL剧情生产记录失败", failure));
    }

    public static void settled(IRecipeLogicMachine machine, GTRecipe recipe) {
        if (machine instanceof com.sirin.hk3gtl.common.machine.Hk3WorkableMultiblockMachine load) {
            com.sirin.hk3gtl.common.dispatch.Hk3EnergyDispatch.settled(load, recipe);
            Hk3CrossMachineOrders.settled(load, recipe);
        }
        recordOutput(machine, recipe);
        Hk3OutputReceiptDispatch.dispatch(true, () -> Hk3EggProduction.settled(machine, recipe),
                failure -> LogUtils.getLogger().error("HK3GTL真实输出后的工业彩蛋记录失败", failure));
        if (machine instanceof Hk3HonkaiAbsorptionMachine tower) tower.onSamplingOutputSettled(recipe);
        if (machine instanceof Hk3SpectrumAnalysisMachine analyzer) analyzer.onSpectrumOutputSettled(recipe);
        if (machine instanceof Hk3LiquidProcessMachine process) process.onLiquidOutputSettled(recipe);
        else if ((recipe.getOutputContents(ItemRecipeCapability.CAP).isEmpty() || !machine.canVoidRecipeOutputs(ItemRecipeCapability.CAP))
                && (recipe.getOutputContents(FluidRecipeCapability.CAP).isEmpty() || !machine.canVoidRecipeOutputs(FluidRecipeCapability.CAP)))
            Hk3OutputReceiptDispatch.dispatch(true, () -> Hk3ResearchRecipeRuntime.settled(machine.self(), recipe),
                    failure -> LogUtils.getLogger().error("HK3GTL原生GT工艺成功输出后的批次回执记录失败", failure));
    }
}
