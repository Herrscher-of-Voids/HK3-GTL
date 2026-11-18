package com.sirin.hk3gtl.common.machine.research;

 



 









/** 修订100 · 2026-09-29：接通团队研究归属、个人付款及真实实验来源。 */

import com.sirin.hk3gtl.common.recipe.Hk3IndustrialRecipeTypes;

import com.gregtechceu.gtceu.api.machine.IMachineBlockEntity;
import com.sirin.hk3gtl.common.machine.Hk3WorkableMultiblockMachine;
import com.sirin.hk3gtl.common.research.Hk3ResearchData;
import com.sirin.hk3gtl.common.research.Hk3OutputReceiptDispatch;
import net.minecraft.server.level.ServerPlayer;
import com.gregtechceu.gtceu.api.machine.trait.RecipeLogic;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.gregtechceu.gtceu.api.recipe.logic.OCParams;
import com.gregtechceu.gtceu.api.recipe.logic.OCResult;
import com.gregtechceu.gtceu.api.capability.recipe.IO;
import com.sirin.hk3gtl.common.communication.Hk3CommunicationData;
import net.minecraft.resources.ResourceLocation;

 






 
public final class Hk3HonkaiAbsorptionMachine extends Hk3LiquidProcessMachine
        implements com.sirin.hk3gtl.common.machine.IMultiTypeRecipeMachine {
    /** 内测5采集类型下的首次液态采样完整配方ID。 */
    public static final ResourceLocation SAMPLING = new ResourceLocation(
            "hk3gtl", "industrial_honkai_collection/approved_hbv_r11");
    public Hk3HonkaiAbsorptionMachine(IMachineBlockEntity holder) { super(holder); }
    /** 注册类型逐阶递增，跨类型搜索仍逐配方检查原有研究门槛和真实输入。 */
    @Override public java.util.List<com.gregtechceu.gtceu.api.recipe.GTRecipeType> getExtendRecipeTypes() {
        return java.util.List.of(getDefinition().getRecipeTypes());
    }
    @Override protected boolean enableMultiRecipe() { return true; }
    @Override public boolean keepSubscribing() { return true; }
    @Override public GTRecipe fullModifyRecipe(GTRecipe recipe, OCParams params, OCResult result) {
        if (!SAMPLING.equals(recipe.id)) return super.fullModifyRecipe(recipe, params, result);
        GTRecipe bounded=recipe.copy().trimRecipeOutputs(getOutputLimits());
        for (var part:getParts()) { bounded=part.modifyRecipe(bounded); if(bounded==null) return null; }
        result.init(com.sirin.hk3gtl.common.constants.Hk3Values.VA_LONG[com.gregtechceu.gtceu.api.GTValues.MAX],bounded.duration,1,0);
        return bounded;
    }
    @Override protected GTRecipe getRealRecipe(GTRecipe recipe, OCParams params, OCResult result) {
        return SAMPLING.equals(recipe.id) ? recipe.copy() : super.getRealRecipe(recipe, params, result);
    }

    @Override protected ServerPlayer informedOwner() {
        if (getLevel() == null || isRemote() || getOwnerUUID() == null || getLevel().getServer() == null) return null;
        var owner = getLevel().getServer().getPlayerList().getPlayer(getOwnerUUID());
        return owner != null && Hk3CommunicationData.get(owner).state(owner.getUUID()).hasObservationData() ? owner : null;
    }
    @Override protected boolean hasObservationData() {
        return getLevel()!=null && !isRemote() && getLevel().getServer()!=null && getOwnerUUID()!=null
                && Hk3CommunicationData.get(getLevel().getServer()).state(getOwnerUUID()).hasObservationData();
    }
    public void onSamplingOutputSettled(GTRecipe recipe) {
        Hk3OutputReceiptDispatch.dispatch(true, () -> recordSamplingOutput(recipe),
                failure -> com.mojang.logging.LogUtils.getLogger().error("HK3GTL采样已输出，但实验或交流回执记录失败：{}",getPos(),failure));
    }

    private void recordSamplingOutput(GTRecipe recipe) {
        if (recipe == null || !SAMPLING.equals(recipe.id)) return;
        // 修订101：采样成功保留原始批次，供SSC核验；持有液体不能补写此回执。
        if(hasObservationData() && getResearchTeamUUID()!=null) {
            var receipt=com.sirin.hk3gtl.common.research.Hk3ProcessReceipts.settle(
                    com.sirin.hk3gtl.common.research.Hk3ProcessReceipts.snapshot(recipe),
                    getLevel().dimension().location()+"@"+getPos(),getLevel().getGameTime());
            Hk3ResearchData.get(getLevel().getServer()).recordProcessFact(getResearchTeamUUID(),"liquid_collection",receipt);
            com.sirin.hk3gtl.common.communication.Hk3CommunicationEvidence.get(getLevel().getServer()).record(getResearchTeamUUID(),"sampling",receipt);
        }
        var owner=informedOwner();
        if (hasObservationData() && getResearchTeamUUID()!=null && Hk3ResearchData.get(getLevel().getServer()).recordExperiment(getResearchTeamUUID(), "RN-HED",getLevel().dimension().location()+"@"+getPos()+"/"+recipe.id) && owner!=null) {
            owner.sendSystemMessage(net.minecraft.network.chat.Component.translatable("hk3gtl.research.sampling_recorded"));
            com.mojang.logging.LogUtils.getLogger().info("[HK3-RESEARCH] RN-HED sample settled at {} for {}",getPos(),owner.getUUID());
        }
    }
    @Override public boolean beforeWorking(GTRecipe recipe) {
        return (!SAMPLING.equals(recipe.id) || hasObservationData()) && super.beforeWorking(recipe);
    }
    @Override protected RecipeLogic createRecipeLogic(Object... args) {
        return new ProcessLogic(this) {
            @Override public void findAndHandleRecipe() {
                if (dispatchProbabilityOrder()) return;
                if (hasObservationData()) {
                    var sample=com.sirin.hk3gtl.common.recipe.Hk3IndustrialRecipeTypes.COLLECTION
                            .getRecipe(getLevel().getServer().getRecipeManager(), SAMPLING);
                    if (sample != null && org.gtlcore.gtlcore.api.recipe.RecipeRunnerHelper
                            .matchRecipe(Hk3HonkaiAbsorptionMachine.this, sample)
                            && checkMatchedRecipeAvailable(sample)) { recipeDirty=false; return; }
                }
                super.findAndHandleRecipe();
            }
            @Override protected java.util.Set<GTRecipe> lookupRecipeSet() {
                var candidates=new java.util.LinkedHashSet<>(super.lookupRecipeSet());
                candidates.removeIf(recipe -> SAMPLING.equals(recipe.id));
                return candidates;
            }
            @Override protected boolean handleTickRecipeIO(GTRecipe recipe, IO io) {
                if (SAMPLING.equals(recipe.id) && !hasObservationData()) return false;
                return super.handleTickRecipeIO(recipe, io);
            }
            @Override protected boolean handleRecipeIO(GTRecipe recipe, IO io) {
                boolean settled = super.handleRecipeIO(recipe, io);
                if (settled && io == IO.OUT) onSamplingOutputSettled(recipe);
                return settled;
            }
        };
    }
}

 
