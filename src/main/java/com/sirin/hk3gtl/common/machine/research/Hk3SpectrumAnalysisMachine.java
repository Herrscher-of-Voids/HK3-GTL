package com.sirin.hk3gtl.common.machine.research;


/**
 * 【文件职责／本轮边界】I02真实光谱输出按固定团队记证据，离线读取既有观察资料。
 */


import com.sirin.hk3gtl.common.recipe.Hk3IndustrialRecipeTypes;

import com.gregtechceu.gtceu.api.capability.recipe.IO;
import com.gregtechceu.gtceu.api.machine.IMachineBlockEntity;
import com.gregtechceu.gtceu.api.machine.trait.RecipeLogic;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.gregtechceu.gtceu.api.recipe.logic.OCParams;
import com.gregtechceu.gtceu.api.recipe.logic.OCResult;
import com.sirin.hk3gtl.common.communication.Hk3CommunicationData;
import com.sirin.hk3gtl.common.research.Hk3RecipeAccess;
import com.sirin.hk3gtl.common.research.Hk3ResearchRecipeRuntime;
import com.sirin.hk3gtl.common.research.Hk3ResearchData;
import com.sirin.hk3gtl.common.research.Hk3OutputReceiptDispatch;
import com.sirin.hk3gtl.common.research.Hk3ProcessReceipts;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.ComponentUtils;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import org.gtlcore.gtlcore.api.recipe.RecipeRunnerHelper;
import org.gtlcore.gtlcore.api.recipe.RecipeResult;
import org.gtlcore.gtlcore.api.machine.trait.IRecipeStatus;

import java.util.LinkedHashSet;
import java.util.Locale;

public final class Hk3SpectrumAnalysisMachine extends Hk3LiquidProcessMachine {
    /** 内测5光谱分析类型下的初始实验完整配方ID。 */
    public static final ResourceLocation INITIAL = new ResourceLocation(
            "hk3gtl", "industrial_honkai_spectrum_analysis/approved_hbv_r13");
    public Hk3SpectrumAnalysisMachine(IMachineBlockEntity holder) { super(holder); }
    @Override public boolean keepSubscribing() { return true; }
    private boolean initialExperimentCompleted() {
        return getResearchTeamUUID() != null && Hk3ResearchData.get(getLevel().getServer())
                .hasExperiment(getResearchTeamUUID(), "RN-HSA");
    }
    @Override public GTRecipe fullModifyRecipe(GTRecipe recipe, OCParams params, OCResult result) {
        if (!INITIAL.equals(recipe.id) || initialExperimentCompleted()) return super.fullModifyRecipe(recipe, params, result);
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
        return INITIAL.equals(recipe.id) && !initialExperimentCompleted()
                ? recipe.copy() : super.getRealRecipe(recipe, params, result);
    }

    @Override public boolean beforeWorking(GTRecipe recipe) {
        return (!INITIAL.equals(recipe.id) || hasObservationData()) && super.beforeWorking(recipe);
    }

    public void onSpectrumOutputSettled(GTRecipe recipe) {
        Hk3OutputReceiptDispatch.dispatch(true, () -> recordSpectrumOutput(recipe),
                failure -> com.mojang.logging.LogUtils.getLogger().error("HK3GTL光谱已输出，但实验或交流回执记录失败：{}",getPos(),failure));
    }

    private void recordSpectrumOutput(GTRecipe recipe) {
        if (recipe == null || !isFormed()) return;
        var snapshot = Hk3ProcessReceipts.findSnapshot(recipe, INITIAL);
        if (snapshot == null) return;
        if(hasObservationData()&&getResearchTeamUUID()!=null){
            var receipt=Hk3ProcessReceipts.settle(snapshot,getLevel().dimension().location()+"@"+getPos(),getLevel().getGameTime());
            com.sirin.hk3gtl.common.communication.Hk3CommunicationEvidence.get(getLevel().getServer()).record(getResearchTeamUUID(),"spectrum",receipt);
        }
        var player = informedOwner();
        if (hasObservationData() && getResearchTeamUUID()!=null && Hk3ResearchData.get(getLevel().getServer()).recordExperiment(getResearchTeamUUID(), "RN-HSA",getLevel().dimension().location()+"@"+getPos()+"/"+snapshot.getString("Recipe")) && player!=null) {
            player.sendSystemMessage(Component.translatable("hk3gtl.research.spectrum_recorded"));
            com.mojang.logging.LogUtils.getLogger().info("[HK3-RESEARCH] RN-HSA spectrum settled at {} for {}", getPos(), player.getUUID());
        }
    }

    private Component analysisBlockReason(GTRecipe recipe) {
        if (!hasObservationData()) return Component.translatable("hk3gtl.machine.spectrum.observation");
        var team = getResearchTeamUUID();
        var data = Hk3ResearchData.get(getLevel().getServer());
        var missingResearch = new LinkedHashSet<String>();
        for (String id : Hk3RecipeAccess.effectiveRequirements(recipe).requirements()) {
            if (!data.permits(team, id)) missingResearch.add(id);
        }
        var experiment = Hk3ResearchRecipeRuntime.executionContract(recipe);
        if (experiment != null) {
            for (String id : experiment.prerequisites()) {
                if (!data.completed(team, id)) missingResearch.add(id);
            }
        }
        var separator = Component.translatable("hk3gtl.jei.research_separator");
        if (!missingResearch.isEmpty()) {
            return Component.translatable("hk3gtl.compat.research_team_missing",
                    ComponentUtils.formatList(missingResearch, separator, id ->
                            Component.translatable("hk3gtl.research.topic." + id.toLowerCase(Locale.ROOT))));
        }
        var missingFacts = Hk3ResearchRecipeRuntime.requiredProcessFacts(recipe).stream()
                .filter(fact -> !data.hasProcessFact(team, fact)).toList();
        if (missingFacts.isEmpty()) return Component.translatable("hk3gtl.compat.execution_plan_blocked");
        return Component.translatable("hk3gtl.machine.spectrum.missing_records",
                ComponentUtils.formatList(missingFacts, separator, Hk3ResearchRecipeRuntime::processFactLabel));
    }

    @Override protected RecipeLogic createRecipeLogic(Object... args) {
        return new ProcessLogic(this) {
            private Component blockedReason;

            @Override protected boolean isResearchBlocked(GTRecipe recipe) {
                if (allowed(recipe)) return false;
                if (blockedReason == null && RecipeRunnerHelper.matchRecipeInput(process, recipe)) {
                    blockedReason = analysisBlockReason(recipe);
                }
                return true;
            }

            @Override public void findAndHandleRecipe() {
                if (dispatchProbabilityOrder()) return;
                blockedReason = null;
                var status = (IRecipeStatus) this;
                status.setRecipeStatus(null);
                if (hasObservationData() && !initialExperimentCompleted()) {
                    var recipe = Hk3IndustrialRecipeTypes.SPECTRUM_ANALYSIS.getRecipe(getLevel().getServer().getRecipeManager(), INITIAL);
                    if (recipe != null && RecipeRunnerHelper.matchRecipe(Hk3SpectrumAnalysisMachine.this, recipe)
                            && checkMatchedRecipeAvailable(recipe)) { recipeDirty = false; return; }
                }
                super.findAndHandleRecipe();
                if (getStatus() == Status.IDLE && blockedReason != null
                        && (status.getRecipeStatus() == null || status.getRecipeStatus() == RecipeResult.FAIL_FIND)) {
                    status.setRecipeStatus(RecipeResult.fail(blockedReason.copy().withStyle(ChatFormatting.YELLOW)));
                }
            }
            @Override protected java.util.Set<GTRecipe> lookupRecipeSet() {
                var candidates = new java.util.LinkedHashSet<>(super.lookupRecipeSet());
                if (!initialExperimentCompleted()) candidates.removeIf(recipe -> INITIAL.equals(recipe.id));
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

