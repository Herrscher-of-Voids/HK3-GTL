package com.sirin.hk3gtl.common.research;



/**
 * 【文件职责／本轮边界】HK3归属机器的RN配方权限读取固定团队账本，绑定人离线不自动丢失已完成知识。
 * 【变更记录 #2】2026-09-29 21:06:40（第 2 次编号备注 · 内测5修订100）
 * 删除：取消已被批准规则替代的研究个人独占、旧数值或在线限定分支；历史备注与其他系统保留。
 * 新增／修改：HK3归属机器的RN配方权限读取固定团队账本，绑定人离线不自动丢失已完成知识。
 * 用途：接通实际证据→付款→研究完成与权限检查；不授予缺真实证据的课题。
 * 边界：编译和账本测试不代表游戏验收；S02至S05正式结构及未接线课题仍未完成。
 * 追溯：logs/research-mainline-r100；R100_FINAL_RECORD。
 */

/** 修订100 · 2026-09-29：接通团队研究归属、个人付款及真实实验来源。 */

import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.sirin.hk3gtl.common.machine.Hk3WorkableMultiblockMachine;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.level.ServerPlayer;
import java.util.ArrayList;
import java.util.List;

/**
 * 【变更记录 #1】2026-09-27 23:52:00（内测5修订91）
 * 删除：无。新增：原配方执行器与增强版条件入口共用的无扣费研究检查。
 * 修改：沿用HK3控制器所有者、其他机器64格内最近玩家的既有规则，不映射研究ID。
 * 用途：增强版替换执行器后仍核对研究；无门槛立即返回，异常交由入口保守拒绝。
 */
/**
 * 【变更记录 #3】2026-09-29 23:37:35（内测5修订101）
 * 删除：本轮被替代的单前置或旧提示分支；其余历史保留。
 * 新增／修改：校验全部前置研究，固定团队知识不依赖绑定人在线。
 * 用途：补足研究接线并如实保留未接物理执行器及结构审批边界。
 * 追溯：logs/research-mainline-r101；R101_FINAL_RECORD。
 */
/**
 * 【变更记录 #5】2026-11-04 00:17:21（第5次备注 · 内测5修订193）
 * 删除：旧合并批次缺少完整权限快照时退回首配方门槛的放行路径。
 * 新增：合并标记存在且权限列表缺失时判定元数据无效；合法空列表仍允许无门槛批次。
 * 修改：读档与运行共用保守拒绝；用途：暂停无法追溯全部原方的旧在途批次，不退款、不清除数据，不改变归属或工业审批。
 */
public final class Hk3RecipeAccess {
    private Hk3RecipeAccess() {}

    /**
     * 【变更记录 #4】2026-10-17 15:07:22（内测5修订163）
     * 新增：注册表与合并批次门槛共用严格读取；未知、旧ID和错误NBT类型保守拒绝。
     * 修改：保留固定团队归属与第三方机器64格最近玩家规则，不凭空推断所有者。
     */
    public static Hk3ResearchRequirementPolicy.Requirements effectiveRequirements(GTRecipe recipe) {
        if (recipe == null) return Hk3ResearchRequirementPolicy.collect(
                List.of(), List.of(), false, Hk3RecipeResearchGate::isCurrentResearchId);
        var batch = new ArrayList<Object>();
        boolean malformed = recipe.data != null && recipe.data.getBoolean("hk3gtlMergedPlan")
                && !recipe.data.contains(Hk3ResearchRequirementPolicy.METADATA_KEY);
        if (recipe.data != null && recipe.data.contains(Hk3ResearchRequirementPolicy.METADATA_KEY)) {
            var raw = recipe.data.get(Hk3ResearchRequirementPolicy.METADATA_KEY);
            if (raw instanceof ListTag list) {
                if (list.getElementType() != Tag.TAG_END && list.getElementType() != Tag.TAG_STRING)
                    malformed = true;
                for (var tag : list) {
                    if (tag.getId() == Tag.TAG_STRING) batch.add(tag.getAsString());
                    else malformed = true;
                }
            } else malformed = true;
        }
        return Hk3ResearchRequirementPolicy.collect(Hk3RecipeResearchGate.getAllRequiredResearch(recipe.id),
                batch, malformed, Hk3RecipeResearchGate::isCurrentResearchId);
    }

    public static boolean blocks(GTRecipe recipe, MetaMachine machine) {
        if (recipe == null) return false;
        var requirements = effectiveRequirements(recipe);
        if (!requirements.valid()) return true;
        if (requirements.requirements().isEmpty()) return false;
        if (machine == null) return true;
        return !Hk3ResearchRequirementPolicy.evaluate(requirements,
                research -> !blocksResearch(research, machine)).allowed();
    }
    private static boolean blocksResearch(String research, MetaMachine machine) {
        if (!Hk3RecipeResearchGate.isCurrentResearchId(research)) return true;
        var level = machine.getLevel();
        if (level == null) return true;
        if (level.isClientSide()) return false;
        ServerPlayer player;
        if (machine instanceof Hk3WorkableMultiblockMachine owned) {
            if (owned.getOwnerUUID() == null || level.getServer() == null) return true;
            var scope=owned.getResearchTeamUUID();
            return scope==null || !Hk3ResearchData.get(level.getServer()).permits(scope,research);
        } else {
            var pos = machine.getPos();
            if (pos == null) return true;
            var nearest = level.getNearestPlayer(pos.getX() + 0.5, pos.getY() + 0.5, pos.getZ() + 0.5, 64, false);
            player = nearest instanceof ServerPlayer serverPlayer ? serverPlayer : null;
        }
        return player == null || !Hk3ResearchManager.isCompleted(player, research);
    }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
