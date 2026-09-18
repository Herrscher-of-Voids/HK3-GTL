package com.sirin.hk3gtl.common.dialogue;



import com.sirin.hk3gtl.common.dialogue.definition.SirinDialogueDefinitions;
import com.sirin.hk3gtl.common.dialogue.handler.IDialogueEndHandler;
import com.sirin.hk3gtl.common.network.DialogueAbortS2CPacket;
import com.sirin.hk3gtl.common.event.Hk3EasterEggChecker;
import com.sirin.hk3gtl.common.network.DialogueAdvanceS2CPacket;
import com.sirin.hk3gtl.common.network.DialogueOpenS2CPacket;
import com.sirin.hk3gtl.common.network.Hk3Network;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.network.PacketDistributor;
import org.slf4j.Logger;
import com.mojang.logging.LogUtils;

import javax.annotation.Nullable;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 对话会话管理器 —— 跟踪服务端所有活跃的对话会话。
 * <p>
 * 线程安全：内部使用 ConcurrentHashMap，网络包回调通过 enqueueWork 在主线程执行。
 */
public final class DialogueSessionManager {

    private static final Logger LOGGER = LogUtils.getLogger();

    /** 活跃会话: 玩家UUID -> 当前对话会话 */
    private static final ConcurrentHashMap<UUID, DialogueSession> ACTIVE_SESSIONS = new ConcurrentHashMap<>();

    private DialogueSessionManager() {}

    /** 关闭会话并通知客户端关界面（不触发结束处理器） */
    private static void abortDialogueWithNotify(ServerPlayer player, String dialogueId, String messageKey) {
        UUID uuid = player.getUUID();
        DialogueSession s = ACTIVE_SESSIONS.get(uuid);
        if (s == null || !s.dialogueId().equals(dialogueId)) {
            return;
        }
        ACTIVE_SESSIONS.remove(uuid);
        Hk3Network.CHANNEL.send(
                PacketDistributor.PLAYER.with(() -> player),
                new DialogueAbortS2CPacket(dialogueId, messageKey)
        );
    }

    /**
     * 启动对话 —— 向目标玩家发送对话开始包并创建服务端会话。
     *
     * @param player     目标玩家
     * @param dialogueId 对话ID（需已在 DialogueRegistry 注册）
     * @return true 启动成功, false 对话未注册或玩家已有活跃对话
     */
    public static boolean startDialogue(ServerPlayer player, String dialogueId) {
        return startDialogue(player, dialogueId, 0);
    }

    /**
     * 启动对话（带附加数据）。
     *
     * @param extraData 附加数据（如西琳的 availableMask）
     */
    public static boolean startDialogue(ServerPlayer player, String dialogueId, int extraData) {
        DialogueDefinition def = DialogueRegistry.getDialogue(dialogueId);
        if (def == null) {
            LOGGER.warn("[HK3GTL] 尝试启动未注册的对话: {}", dialogueId);
            return false;
        }

        UUID uuid = player.getUUID();
        if (ACTIVE_SESSIONS.containsKey(uuid)) {
            LOGGER.debug("[HK3GTL] 玩家 {} 已有活跃对话，忽略新请求", player.getName().getString());
            return false;
        }

        DialogueSession session = new DialogueSession(dialogueId, def.startSegmentId(), extraData);
        ACTIVE_SESSIONS.put(uuid, session);

        Hk3Network.CHANNEL.send(
                PacketDistributor.PLAYER.with(() -> player),
                new DialogueOpenS2CPacket(dialogueId, def.startSegmentId(), extraData)
        );

        LOGGER.info("[HK3GTL] 对话启动: {} -> 玩家 {}", dialogueId, player.getName().getString());
        return true;
    }

    /**
     * 处理玩家选择（由 DialoguePlayerChoiceC2SPacket 调用）。
     */
    public static void onPlayerChoice(ServerPlayer player, String dialogueId, int choiceIndex) {
        UUID uuid = player.getUUID();
        DialogueSession session = ACTIVE_SESSIONS.get(uuid);
        if (session == null || !session.dialogueId().equals(dialogueId)) {
            LOGGER.warn("[HK3GTL] 收到无效选择: 玩家={}, dialogue={}", player.getName().getString(), dialogueId);
            return;
        }

        DialogueDefinition def = DialogueRegistry.getDialogue(dialogueId);
        if (def == null) return;

        var segments = def.segments();
        var currentLines = segments.get(session.currentSegmentId());
        if (currentLines == null) return;

        // 找到当前 segment 中带 choices 的最后一行
        DialogueLine choiceLine = null;
        for (DialogueLine line : currentLines) {
            if (line.choices() != null && !line.choices().isEmpty()) {
                choiceLine = line;
            }
        }

        if (choiceLine == null || choiceIndex < 0 || choiceIndex >= choiceLine.choices().size()) {
            LOGGER.warn("[HK3GTL] 无效选项索引: {}", choiceIndex);
            return;
        }

        // 西琳 intro：校验掩码并记录已读 IF（防伪造 C2S；与客户端过滤一致）
        if (SirinDialogueDefinitions.DIALOGUE_ID.equals(dialogueId) && "intro".equals(session.currentSegmentId())) {
            int mask = session.extraData() != 0 ? session.extraData() : (1 << SirinDialogueDefinitions.IF_BRANCH_COUNT) - 1;
            if ((mask & (1 << choiceIndex)) == 0) {
                LOGGER.warn("[HK3GTL] 西琳选项不可用: choiceIndex={}, mask={}", choiceIndex, mask);
                abortDialogueWithNotify(player, dialogueId, "hk3gtl.dialogue.sirin.error.invalid_choice");
                return;
            }
            if (!SirinIfProgressStore.markUsed(player, choiceIndex)) {
                LOGGER.warn("[HK3GTL] 西琳 IF 记录冲突: choiceIndex={}", choiceIndex);
                abortDialogueWithNotify(player, dialogueId, "hk3gtl.dialogue.sirin.error.if_already_used");
                return;
            }
        }

        Hk3EasterEggChecker.onDialogueSpamClick(player);

        DialogueChoice choice = choiceLine.choices().get(choiceIndex);
        String nextSegment = choice.targetSegmentId();

        DialogueSession next = new DialogueSession(dialogueId, nextSegment, session.extraData());
        ACTIVE_SESSIONS.put(uuid, next);

        Hk3Network.CHANNEL.send(
                PacketDistributor.PLAYER.with(() -> player),
                new DialogueAdvanceS2CPacket(dialogueId, nextSegment, next.extraData())
        );

        LOGGER.debug("[HK3GTL] 对话分支: {} -> segment {}", dialogueId, nextSegment);
    }

    /**
     * 处理对话结束（由 DialogueCloseC2SPacket 调用）。
     */
    public static void onDialogueEnd(ServerPlayer player, String dialogueId) {
        UUID uuid = player.getUUID();
        DialogueSession session = ACTIVE_SESSIONS.get(uuid);
        if (session == null || !session.dialogueId().equals(dialogueId)) return;

        if (SirinDialogueDefinitions.DIALOGUE_ID.equals(dialogueId)
                && !session.currentSegmentId().startsWith("if_")) {
            LOGGER.warn("[HK3GTL] 拒绝提前关闭终局对话: 玩家={}, segment={}",
                    player.getName().getString(), session.currentSegmentId());
            return;
        }

        ACTIVE_SESSIONS.remove(uuid);
        DialogueDefinition def = DialogueRegistry.getDialogue(dialogueId);
        if (def == null) return;

        // 调用结束处理器
        if (def.endHandlerKey() != null) {
            IDialogueEndHandler handler = DialogueRegistry.getEndHandler(def.endHandlerKey());
            if (handler != null) {
                handler.onDialogueEnd(player, dialogueId, session.extraData());
            }
        }

        LOGGER.info("[HK3GTL] 对话结束: {} -> 玩家 {}", dialogueId, player.getName().getString());
    }

    /**
     * 玩家断线清理。
     */
    public static void onPlayerDisconnect(UUID playerUuid) {
        ACTIVE_SESSIONS.remove(playerUuid);
    }

    /**
     * 查询玩家当前是否有活跃对话。
     */
    public static boolean hasActiveDialogue(UUID playerUuid) {
        return ACTIVE_SESSIONS.containsKey(playerUuid);
    }

    @Nullable
    public static DialogueSession getSession(UUID playerUuid) {
        return ACTIVE_SESSIONS.get(playerUuid);
    }

    /**
     * 对话会话状态（不可变）。
     */
    public record DialogueSession(String dialogueId, String currentSegmentId, int extraData) {}
}
