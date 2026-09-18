package com.sirin.hk3gtl.common.dialogue.handler;



import net.minecraft.server.level.ServerPlayer;

/**
 * 对话结束回调接口。
 * <p>
 * 不同对话在结束时执行不同的服务端逻辑（如毕业标记、传送等）。
 */
@FunctionalInterface
public interface IDialogueEndHandler {

    /**
     * 对话正常结束时调用（服务端主线程）。
     *
     * @param player     对话参与的玩家
     * @param dialogueId 对话ID
     * @param extraData  附加数据（由启动时传入）
     */
    void onDialogueEnd(ServerPlayer player, String dialogueId, int extraData);
}
