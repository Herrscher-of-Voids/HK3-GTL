package com.sirin.hk3gtl.common.machine.research;

/** 【变更记录 #3】2026-10-01 00:14:30（修订122）：删除无；新增/修改：首次光谱实际输出后保存交流收支快照，不靠研究标记倒填；用途：真实成果、团队授权与个人阅读分离，不开放贸易或免费完成研究。 */

/**
 * 【文件职责／本轮边界】I02真实光谱输出按固定团队记证据，离线读取既有观察资料。
 * 【变更记录 #2】2026-09-29 21:06:40（第 2 次编号备注 · 内测5修订100）
 * 删除：取消已被批准规则替代的研究个人独占、旧数值或在线限定分支；历史备注与其他系统保留。
 * 新增／修改：I02真实光谱输出按固定团队记证据，离线读取既有观察资料。
 * 用途：接通实际证据→付款→研究完成与权限检查；不授予缺真实证据的课题。
 * 边界：编译和账本测试不代表游戏验收；S02至S05正式结构及未接线课题仍未完成。
 * 追溯：logs/research-mainline-r100；R100_FINAL_RECORD。
 */

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
import com.sirin.hk3gtl.common.recipe.Hk3RecipeTypesImpl;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import org.gtlcore.gtlcore.api.recipe.RecipeRunnerHelper;

/** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
/** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
/** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
/** 中文说明：该处说明已按当前代码行为整理。*/
/**
 * 【变更记录 #1】2026-09-24 16:42:00（内测5修订66）
 * 删除：后续实验没有生产结算入口的行为。新增：起步电路适配实验结算。
 * 修改：沿用初始光谱的固定批次，其他配方接入工业结算；用途：I02结构完全不变。
 */
public final class Hk3SpectrumAnalysisMachine extends Hk3LiquidProcessMachine {
    /** 内测5光谱分析类型下的初始实验完整配方ID。 */
    public static final ResourceLocation INITIAL = new ResourceLocation(
            "hk3gtl", "industrial_honkai_spectrum_analysis/industrial_initial_spectrum");
    public Hk3SpectrumAnalysisMachine(IMachineBlockEntity holder) { super(holder); }
    /** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
    @Override public boolean keepSubscribing() { return true; }
    /** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
    @Override public GTRecipe fullModifyRecipe(GTRecipe recipe, OCParams params, OCResult result) {
        if (!INITIAL.equals(recipe.id)) return super.fullModifyRecipe(recipe, params, result);
        GTRecipe bounded=recipe.copy().trimRecipeOutputs(getOutputLimits());
        for (var part:getParts()) { bounded=part.modifyRecipe(bounded); if(bounded==null) return null; }
        result.init(com.sirin.hk3gtl.common.constants.Hk3Values.VA_LONG[com.gregtechceu.gtceu.api.GTValues.MAX],bounded.duration,1,0);
        return bounded;
    }

    /** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
    @Override protected ServerPlayer informedOwner() {
        if (getLevel() == null || isRemote() || getOwnerUUID() == null || getLevel().getServer() == null) return null;
        var player = getLevel().getServer().getPlayerList().getPlayer(getOwnerUUID());
        return player != null && Hk3CommunicationData.get(player).state(player.getUUID()).hasObservationData() ? player : null;
    }

    /** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
    @Override protected GTRecipe getRealRecipe(GTRecipe recipe, OCParams params, OCResult result) {
        return INITIAL.equals(recipe.id) ? recipe.copy() : super.getRealRecipe(recipe, params, result);
    }

    /** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
    @Override public boolean beforeWorking(GTRecipe recipe) {
        return (!INITIAL.equals(recipe.id) || hasObservationData()) && super.beforeWorking(recipe);
    }

    /** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
    public void onSpectrumOutputSettled(GTRecipe recipe) {
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

    /** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
    @Override protected RecipeLogic createRecipeLogic(Object... args) {
        return new ProcessLogic(this) {
            @Override public void findAndHandleRecipe() {
                if (hasObservationData()) {
                    var recipe = Hk3IndustrialRecipeTypes.SPECTRUM_ANALYSIS.getRecipe(getLevel().getServer().getRecipeManager(), INITIAL);
                    if (recipe != null && RecipeRunnerHelper.matchRecipe(Hk3SpectrumAnalysisMachine.this, recipe)
                            && checkMatchedRecipeAvailable(recipe)) { recipeDirty = false; return; }
                }
                super.findAndHandleRecipe();
            }
            /** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
            @Override protected java.util.Set<GTRecipe> lookupRecipeSet() {
                var candidates = new java.util.LinkedHashSet<>(super.lookupRecipeSet());
                candidates.removeIf(recipe -> INITIAL.equals(recipe.id));
                return candidates;
            }
            /** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
            @Override protected boolean handleTickRecipeIO(GTRecipe recipe, IO io) {
                if (INITIAL.equals(recipe.id) && !hasObservationData()) return false;
                return super.handleTickRecipeIO(recipe, io);
            }
            /** 中文维护备注：历史变更说明已整理；当前实现以代码为准。 */
            @Override protected boolean handleRecipeIO(GTRecipe recipe, IO io) {
                boolean settled = super.handleRecipeIO(recipe, io);
                if (settled && io == IO.OUT) onSpectrumOutputSettled(recipe);
                return settled;
            }
        };
    }
    @Override protected void onProcessOutput(GTRecipe recipe) { super.onProcessOutput(recipe); }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
