package com.sirin.hk3gtl.common.machine.research;

 

 









/** 修订100 · 2026-09-29：接通团队研究归属、个人付款及真实实验来源。 */

import com.sirin.hk3gtl.common.recipe.Hk3IndustrialRecipeTypes;

import com.gregtechceu.gtceu.api.capability.recipe.IO;
import com.gregtechceu.gtceu.api.machine.IMachineBlockEntity;
import com.gregtechceu.gtceu.api.machine.trait.RecipeLogic;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.gregtechceu.gtceu.api.recipe.logic.OCParams;
import com.gregtechceu.gtceu.api.recipe.logic.OCResult;
import com.sirin.hk3gtl.common.communication.Hk3CommunicationData;
import com.sirin.hk3gtl.common.machine.Hk3MultiRecipeLogic;
import com.sirin.hk3gtl.common.machine.Hk3WorkableMultiblockMachine;
import com.sirin.hk3gtl.common.research.Hk3ResearchData;
import com.sirin.hk3gtl.common.research.Hk3OutputReceiptDispatch;
import com.sirin.hk3gtl.common.recipe.Hk3RecipeTypesImpl;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import org.gtlcore.gtlcore.api.recipe.RecipeRunnerHelper;

 




public final class Hk3SpectrumAnalysisMachine extends Hk3LiquidProcessMachine {
    /** 内测5光谱分析类型下的初始实验完整配方ID。 */
    public static final ResourceLocation INITIAL = new ResourceLocation(
            "hk3gtl", "industrial_honkai_spectrum_analysis/approved_hbv_r13");
    public Hk3SpectrumAnalysisMachine(IMachineBlockEntity holder) { super(holder); }
    @Override public boolean keepSubscribing() { return true; }
    @Override public GTRecipe fullModifyRecipe(GTRecipe recipe, OCParams params, OCResult result) {
        if (!INITIAL.equals(recipe.id)) return super.fullModifyRecipe(recipe, params, result);
        GTRecipe bounded=recipe.copy().trimRecipeOutputs(getOutputLimits());
        for (var part:getParts()) { bounded=part.modifyRecipe(bounded); if(bounded==null) return null; }
        result.init(com.sirin.hk3gtl.common.constants.Hk3Values.VA_LONG[com.gregtechceu.gtceu.api.GTValues.MAX],bounded.duration,1,0);
        return bounded;
    }

    @Override protected ServerPlayer informedOwner() {
        if (getLevel() == null || isRemote() || getOwnerUUID() == null || getLevel().getServer() == null) return null;
        var player = getLevel().getServer().getPlayerList().getPlayer(getOwnerUUID());
        return player != null && Hk3CommunicationData.get(player).state(player.getUUID()).hasObservationData() ? player : null;
    }

    @Override protected GTRecipe getRealRecipe(GTRecipe recipe, OCParams params, OCResult result) {
        return INITIAL.equals(recipe.id) ? recipe.copy() : super.getRealRecipe(recipe, params, result);
    }

    @Override public boolean beforeWorking(GTRecipe recipe) {
        return (!INITIAL.equals(recipe.id) || hasObservationData()) && super.beforeWorking(recipe);
    }

    public void onSpectrumOutputSettled(GTRecipe recipe) {
        Hk3OutputReceiptDispatch.dispatch(true, () -> recordSpectrumOutput(recipe),
                failure -> com.mojang.logging.LogUtils.getLogger().error("HK3GTL光谱已输出，但实验或交流回执记录失败：{}",getPos(),failure));
    }

    private void recordSpectrumOutput(GTRecipe recipe) {
        if (recipe == null || !INITIAL.equals(recipe.id) || !isFormed()) return;
        if(hasObservationData()&&getResearchTeamUUID()!=null){
            var receipt=com.sirin.hk3gtl.common.research.Hk3ProcessReceipts.settle(com.sirin.hk3gtl.common.research.Hk3ProcessReceipts.snapshot(recipe),getLevel().dimension().location()+"@"+getPos(),getLevel().getGameTime());
            com.sirin.hk3gtl.common.communication.Hk3CommunicationEvidence.get(getLevel().getServer()).record(getResearchTeamUUID(),"spectrum",receipt);
        }
        var player = informedOwner();
        if (hasObservationData() && getResearchTeamUUID()!=null && Hk3ResearchData.get(getLevel().getServer()).recordExperiment(getResearchTeamUUID(), "RN-HSA",getLevel().dimension().location()+"@"+getPos()+"/"+recipe.id) && player!=null) {
            player.sendSystemMessage(Component.translatable("hk3gtl.research.spectrum_recorded"));
            com.mojang.logging.LogUtils.getLogger().info("[HK3-RESEARCH] RN-HSA spectrum settled at {} for {}", getPos(), player.getUUID());
        }
    }

    @Override protected RecipeLogic createRecipeLogic(Object... args) {
        return new ProcessLogic(this) {
            @Override public void findAndHandleRecipe() {
                if (dispatchProbabilityOrder()) return;
                if (hasObservationData()) {
                    var recipe = Hk3IndustrialRecipeTypes.SPECTRUM_ANALYSIS.getRecipe(getLevel().getServer().getRecipeManager(), INITIAL);
                    if (recipe != null && RecipeRunnerHelper.matchRecipe(Hk3SpectrumAnalysisMachine.this, recipe)
                            && checkMatchedRecipeAvailable(recipe)) { recipeDirty = false; return; }
                }
                super.findAndHandleRecipe();
            }
            @Override protected java.util.Set<GTRecipe> lookupRecipeSet() {
                var candidates = new java.util.LinkedHashSet<>(super.lookupRecipeSet());
                candidates.removeIf(recipe -> INITIAL.equals(recipe.id));
                return candidates;
            }
            @Override protected boolean handleTickRecipeIO(GTRecipe recipe, IO io) {
                if (INITIAL.equals(recipe.id) && !hasObservationData()) return false;
                return super.handleTickRecipeIO(recipe, io);
            }
            @Override protected boolean handleRecipeIO(GTRecipe recipe, IO io) {
                boolean settled = super.handleRecipeIO(recipe, io);
                if (settled && io == IO.OUT) onSpectrumOutputSettled(recipe);
                return settled;
            }
        };
    }
    @Override protected void onProcessOutput(GTRecipe recipe) { super.onProcessOutput(recipe); }
}

 
