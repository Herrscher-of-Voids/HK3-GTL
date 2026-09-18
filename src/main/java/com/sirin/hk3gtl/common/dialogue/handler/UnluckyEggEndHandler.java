package com.sirin.hk3gtl.common.dialogue.handler;



import net.minecraft.server.level.ServerPlayer;

/**
 * 非酋彩蛋对话结束处理器 —— 纯趣味性对话，无额外逻辑。
 * <p>
 * 失败概率减半已在 Hk3ResearchFailureTracker 中处理，此处无需重复。
 */
public class UnluckyEggEndHandler implements IDialogueEndHandler {

    @Override
    public void onDialogueEnd(ServerPlayer player, String dialogueId, int extraData) {
        // 空操作 —— 概率减半逻辑已在 onResearchFailed 中完成
    }
}
