package com.sirin.hk3gtl.common.machine.research;

/** 【变更记录 #3】2026-10-01 00:14:30（修订122）：删除无；新增/修改：实际采样输出留下限定交流快照，不改配方、结构或能耗；用途：真实成果、团队授权与个人阅读分离，不开放贸易或免费完成研究。 */



/**
 * 【文件职责／本轮边界】I01真实采样成功按固定团队记录证据，已收资料与绑定人离线分开判断。
 * 【变更记录 #1】2026-09-29 21:06:40（第 1 次编号备注 · 内测5修订100）
 * 删除：取消已被批准规则替代的研究个人独占、旧数值或在线限定分支；历史备注与其他系统保留。
 * 新增／修改：I01真实采样成功按固定团队记录证据，已收资料与绑定人离线分开判断。
 * 用途：接通实际证据→付款→研究完成与权限检查；不授予缺真实证据的课题。
 * 边界：编译和账本测试不代表游戏验收；S02至S05正式结构及未接线课题仍未完成。
 * 追溯：logs/research-mainline-r100；R100_FINAL_RECORD。
 */

/** 修订100 · 2026-09-29：接通团队研究归属、个人付款及真实实验来源。 */

import com.sirin.hk3gtl.common.recipe.Hk3IndustrialRecipeTypes;

import com.gregtechceu.gtceu.api.machine.IMachineBlockEntity;
import com.sirin.hk3gtl.common.machine.Hk3WorkableMultiblockMachine;
import com.sirin.hk3gtl.common.research.Hk3ResearchData;
import net.minecraft.server.level.ServerPlayer;
import com.gregtechceu.gtceu.api.machine.trait.RecipeLogic;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.gregtechceu.gtceu.api.recipe.logic.OCParams;
import com.gregtechceu.gtceu.api.recipe.logic.OCResult;
import com.gregtechceu.gtceu.api.capability.recipe.IO;
import com.sirin.hk3gtl.common.communication.Hk3CommunicationData;
import net.minecraft.resources.ResourceLocation;

/** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
/** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
/** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
/** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
/** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
/** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
/** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
/** 中文说明：该处说明已按当前代码行为整理。*/
/**
 * 【变更记录 #2】2026-09-29 23:37:35（内测5修订101）
 * 删除：本轮被替代的单前置或旧提示分支；其余历史保留。
 * 新增／修改：首次真实采样输出提交液态采集批次，不通过库存或旧研究ID授予。
 * 用途：补足研究接线并如实保留未接物理执行器及结构审批边界。
 * 追溯：logs/research-mainline-r101；R101_FINAL_RECORD。
 */
/** 【变更记录 #4】2026-10-15 01:12:48（修订156）：高阶采集复用实际工艺门控和成果结算，首次液态采样特例保留。 */
public final class Hk3HonkaiAbsorptionMachine extends Hk3LiquidProcessMachine
        implements com.sirin.hk3gtl.common.machine.IMultiTypeRecipeMachine {
    /** 内测5采集类型下的首次液态采样完整配方ID。 */
    public static final ResourceLocation SAMPLING = new ResourceLocation(
            "hk3gtl", "industrial_honkai_collection/industrial_liquid_sampling");
    public Hk3HonkaiAbsorptionMachine(IMachineBlockEntity holder) { super(holder); }
    /** 注册类型逐阶递增，跨类型搜索仍逐配方检查原有研究门槛和真实输入。 */
    @Override public java.util.List<com.gregtechceu.gtceu.api.recipe.GTRecipeType> getExtendRecipeTypes() {
        return java.util.List.of(getDefinition().getRecipeTypes());
    }
    /** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
    @Override protected boolean enableMultiRecipe() { return true; }
    /** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
    @Override public boolean keepSubscribing() { return true; }
    /** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
    @Override public GTRecipe fullModifyRecipe(GTRecipe recipe, OCParams params, OCResult result) {
        if (!SAMPLING.equals(recipe.id)) return super.fullModifyRecipe(recipe, params, result);
        GTRecipe bounded=recipe.copy().trimRecipeOutputs(getOutputLimits());
        for (var part:getParts()) { bounded=part.modifyRecipe(bounded); if(bounded==null) return null; }
        result.init(com.sirin.hk3gtl.common.constants.Hk3Values.VA_LONG[com.gregtechceu.gtceu.api.GTValues.MAX],bounded.duration,1,0);
        return bounded;
    }
    @Override protected GTRecipe getRealRecipe(GTRecipe recipe, OCParams params, OCResult result) {
        // 中文维护备注：历史说明已整理；当前实现以代码为准。
        return SAMPLING.equals(recipe.id) ? recipe.copy() : super.getRealRecipe(recipe, params, result);
    }

    /** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
    @Override protected ServerPlayer informedOwner() {
        if (getLevel() == null || isRemote() || getOwnerUUID() == null || getLevel().getServer() == null) return null;
        var owner = getLevel().getServer().getPlayerList().getPlayer(getOwnerUUID());
        return owner != null && Hk3CommunicationData.get(owner).state(owner.getUUID()).hasObservationData() ? owner : null;
    }
    /** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
    @Override protected boolean hasObservationData() {
        return getLevel()!=null && !isRemote() && getLevel().getServer()!=null && getOwnerUUID()!=null
                && Hk3CommunicationData.get(getLevel().getServer()).state(getOwnerUUID()).hasObservationData();
    }
    public void onSamplingOutputSettled(GTRecipe recipe) {
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
    /** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
    @Override public boolean beforeWorking(GTRecipe recipe) {
        return (!SAMPLING.equals(recipe.id) || hasObservationData()) && super.beforeWorking(recipe);
    }
    /** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
    @Override protected RecipeLogic createRecipeLogic(Object... args) {
        return new ProcessLogic(this) {
            /** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
            @Override public void findAndHandleRecipe() {
                if (hasObservationData()) {
                    var sample=com.sirin.hk3gtl.common.recipe.Hk3IndustrialRecipeTypes.COLLECTION
                            .getRecipe(getLevel().getServer().getRecipeManager(), SAMPLING);
                    if (sample != null && org.gtlcore.gtlcore.api.recipe.RecipeRunnerHelper
                            .matchRecipe(Hk3HonkaiAbsorptionMachine.this, sample)
                            && checkMatchedRecipeAvailable(sample)) { recipeDirty=false; return; }
                }
                super.findAndHandleRecipe();
            }
            /** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
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

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
