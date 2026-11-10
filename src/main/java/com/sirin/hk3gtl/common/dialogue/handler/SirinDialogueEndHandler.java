package com.sirin.hk3gtl.common.dialogue.handler;


/**
 * 【文件职责】
 * - 维护 SirinDialogueEndHandler 的核心功能实现。
 * - 关键调用链：由上层系统入口调用 -> 本文件核心方法 -> 下游模块。
 *
 * 【变更记录】2026-05-19
 * - 删除：
 *   1) 初始归档备注：自 v0.3 基线梳理，无本次 diff。
 * - 新增：
 *   1) 新增统一变更备注块，便于后续维护与审计追踪。
 * - 修改：
 *   1) 未改动业务逻辑，仅补充文件级职责与维护注释模板。
 * - 用途：
 *   1) 帮助维护者快速理解文件职责、变更背景与风险点。
 *
 * 【段内说明】
 * - 复杂方法补充“干什么 / 边界 / 线程侧”精简中文注释。
 */
import com.sirin.hk3gtl.common.dimension.Hk3GraduationData;
import com.sirin.hk3gtl.common.event.Hk3FactionEventChecker;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.Level;
import net.minecraft.core.BlockPos;
import org.slf4j.Logger;
import com.mojang.logging.LogUtils;

/**
 * 西琳终局对话结束处理器 —— 标记毕业、传送回主世界。
 */
/** 【变更记录 #1】2026-09-30 23:34:26（修订119）：删除：世界级结果对所有玩家的隐式授权；新增/修改：正常终审只写本人通过记录，重复回调不再重复触发奖励，坏结局不能领取正常通过；用途：个人结算不覆盖其他玩家，未完成的资格采集仍单独接入。 */
/** 【变更记录 #2】2026-10-01 04:21:47（修订128）：删除：旧固定上限或被替代的分支；新增/修改：终审收束完成后独立记录彩蛋，复用已验证完成回调，不改变毕业/回主世界；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #3】2026-10-01 16:49:18（修订135）：删除无资格直接结算路径；新增本人有效快照及FU01检查点校验；修改正式通过后关闭同次会面；用途：调试预览、旧检查点和直接调用不误发毕业，原奖励幂等与返程保持。 */
public class SirinDialogueEndHandler implements IDialogueEndHandler {

    private static final Logger LOGGER = LogUtils.getLogger();
    private static final String DIALOGUE_DONE_TAG = "hk3gtl_dialogue_done";

    @Override
    public void onDialogueEnd(ServerPlayer player, String dialogueId, int extraData) {
        if (!"sirin_finale".equals(dialogueId) || com.sirin.hk3gtl.common.badending.Hk3BadEndingData.get(player.serverLevel()).getStage(player.getUUID()) != 0) return;
        if(!com.sirin.hk3gtl.common.finale.Hk3FinaleAdmission.canSettle(player))return;
        // 只结算当前玩家，旧世界标记不参与；先写入幂等结果，再运行个人奖励事件。
        boolean first = Hk3GraduationData.get(player.serverLevel()).markGraduated(player.getUUID());
        com.sirin.hk3gtl.common.finale.Hk3FinaleAdmission.finish(player,true);
        player.getPersistentData().putBoolean(DIALOGUE_DONE_TAG, true);
        if (first) Hk3FactionEventChecker.triggerGraduationComplete(player);
        com.sirin.hk3gtl.common.easter.Hk3EggRuntime.observe(player,"finale_settled",java.util.Map.of("completed","true"));

        // 传送回主世界出生点
        ServerLevel overworld = player.server.getLevel(Level.OVERWORLD);
        if (overworld != null) {
            BlockPos spawn = overworld.getSharedSpawnPos();
            player.teleportTo(overworld, spawn.getX() + 0.5, spawn.getY(), spawn.getZ() + 0.5,
                    player.getYRot(), player.getXRot());
        }

        LOGGER.info("[HK3GTL] 西琳终局对话完成 - 玩家: {} 已毕业", player.getName().getString());
    }
}
