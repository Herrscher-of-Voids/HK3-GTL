package com.sirin.hk3gtl.common.dialogue.handler;

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
