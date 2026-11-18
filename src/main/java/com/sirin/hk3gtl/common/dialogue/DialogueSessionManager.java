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
        com.sirin.hk3gtl.common.easter.Hk3EggReading.clear(uuid);
        Hk3Network.CHANNEL.send(
                PacketDistributor.PLAYER.with(() -> player),
                new DialogueAbortS2CPacket(dialogueId, messageKey)
        );
    }

    /** 攻击进入坏结局时仅关闭发起人的正常会话，不触发通过或奖励。 */
    public static void interruptForBadEnding(ServerPlayer player) {
        abortDialogueWithNotify(player,SirinDialogueDefinitions.DIALOGUE_ID,"");
        com.sirin.hk3gtl.common.finale.Hk3FinaleAdmission.finish(player,false);
        player.getPersistentData().remove("hk3gtl_finale_checkpoint_v5");
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
        if (def == null) return false;
        String start = def.startSegmentId();
        if (SirinDialogueDefinitions.DIALOGUE_ID.equals(dialogueId)) {
            if(!com.sirin.hk3gtl.common.finale.Hk3FinaleAdmission.requireSession(player))return false;
            String checkpoint = com.sirin.hk3gtl.common.finale.Hk3FinaleAdmission.checkpoint(player);
            if (!checkpoint.isEmpty() && def.segments().containsKey(checkpoint)) start = checkpoint;
            extraData = Hk3FinaleIfData.get(player).selectedMask(player.getUUID());
        }
        return startAt(player, dialogueId, start, extraData);
    }

    /** 仅供服务端内部指定已注册段落；客户端选择只能沿当前段落的合法边前进。 */
    public static boolean startAt(ServerPlayer player, String dialogueId, String start, int extraData) {
        if(com.sirin.hk3gtl.common.review.Hk3ReviewDialogues.formal(dialogueId))return false;
        DialogueDefinition def = DialogueRegistry.getDialogue(dialogueId);
        if (def == null) {
            LOGGER.warn("[HK3GTL] 尝试启动未注册的对话: {}", dialogueId);
            return false;
        }

        if (!def.segments().containsKey(start)) return false;
        UUID uuid = player.getUUID();
        if (hasActiveDialogue(uuid)) {
            LOGGER.debug("[HK3GTL] 玩家 {} 已有活跃对话，忽略新请求", player.getName().getString());
            return false;
        }

        if (SirinDialogueDefinitions.DIALOGUE_ID.equals(dialogueId)) {
            if(!com.sirin.hk3gtl.common.finale.Hk3FinaleAdmission.requireSession(player)
                    ||!start.equals(com.sirin.hk3gtl.common.finale.Hk3FinaleAdmission.checkpoint(player)))return false;
            var bad=com.sirin.hk3gtl.common.badending.Hk3BadEndingData.get(player.serverLevel());
            if(bad.getStage(uuid)!=0||com.sirin.hk3gtl.common.dimension.Hk3GraduationData.get(player.serverLevel()).isGraduated(uuid))return false;
            var meeting=bad.beginEncounter(uuid);
            com.sirin.hk3gtl.common.badending.Hk3FinaleAttackData.get(player).begin(uuid,meeting);
        }
        DialogueSession session = new DialogueSession(dialogueId, start, extraData);
        ACTIVE_SESSIONS.put(uuid, session);

        Hk3Network.CHANNEL.send(
                PacketDistributor.PLAYER.with(() -> player),
                new DialogueOpenS2CPacket(dialogueId, start, extraData, session.nonce())
        );

        com.sirin.hk3gtl.common.easter.Hk3EggDialogue.opened(player,dialogueId,start);
        LOGGER.info("[HK3GTL] 对话启动: {} -> 玩家 {}", dialogueId, player.getName().getString());
        return true;
    }

    /**
     * 处理玩家选择（由 DialoguePlayerChoiceC2SPacket 调用）。
     */
    public static void onPlayerChoice(ServerPlayer player, String dialogueId, String segmentId, int choiceIndex, long nonce) {
        UUID uuid = player.getUUID();
        DialogueSession session = ACTIVE_SESSIONS.get(uuid);
        if (session == null || !session.accepts(dialogueId, nonce) || !session.currentSegmentId().equals(segmentId)) {
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

        Hk3EasterEggChecker.onDialogueSpamClick(player);

        DialogueChoice choice = choiceLine.choices().get(choiceIndex);
        String nextSegment = choice.targetSegmentId();
        if (!segments.containsKey(nextSegment)) return;
        int nextData = session.extraData();
        if (SirinDialogueDefinitions.DIALOGUE_ID.equals(dialogueId)) {
            if(!com.sirin.hk3gtl.common.finale.Hk3FinaleAdmission.hasSession(player))return;
            int index = com.sirin.hk3gtl.common.dialogue.definition.Hk3ApprovedDialogues.ifIndex(nextSegment);
            Hk3FinaleIfData ledger = Hk3FinaleIfData.get(player);
            if (index >= 0 && !ledger.select(uuid, index)) {
                Hk3Network.CHANNEL.send(PacketDistributor.PLAYER.with(() -> player),
                        new DialogueAdvanceS2CPacket(dialogueId, session.currentSegmentId(), ledger.selectedMask(uuid), session.nonce()));
                return;
            }
            nextData = ledger.selectedMask(uuid);
            com.sirin.hk3gtl.common.finale.Hk3FinaleAdmission.advance(player,nextSegment);
        }

        DialogueSession next = new DialogueSession(dialogueId, nextSegment, nextData);
        ACTIVE_SESSIONS.put(uuid, next);

        Hk3Network.CHANNEL.send(
                PacketDistributor.PLAYER.with(() -> player),
                new DialogueAdvanceS2CPacket(dialogueId, nextSegment, next.extraData(), next.nonce())
        );

        com.sirin.hk3gtl.common.easter.Hk3EggDialogue.opened(player,dialogueId,nextSegment);
        LOGGER.debug("[HK3GTL] 对话分支: {} -> segment {}", dialogueId, nextSegment);
    }

    /**
     * 处理对话结束（由 DialogueCloseC2SPacket 调用）。
     */
    /** 网络关闭只接受当前段落令牌；服务端暂停仍走内部入口。 */
    public static void onDialogueEnd(ServerPlayer player, String dialogueId, boolean completed, long nonce) {
        var session = ACTIVE_SESSIONS.get(player.getUUID());
        if (session == null || !session.accepts(dialogueId, nonce)) return;
        onDialogueEnd(player, dialogueId, completed);
    }

    public static void onDialogueEnd(ServerPlayer player, String dialogueId, boolean completed) {
        UUID uuid = player.getUUID();
        DialogueSession session = ACTIVE_SESSIONS.get(uuid);
        if (session == null || !session.dialogueId().equals(dialogueId)) return;

        ACTIVE_SESSIONS.remove(uuid);
        com.sirin.hk3gtl.common.easter.Hk3EggReading.clear(uuid);
        if (SirinDialogueDefinitions.DIALOGUE_ID.equals(dialogueId)) {
            if (!completed || !"FU01".equals(session.currentSegmentId())) {
                String resume = "FP01".equals(session.currentSegmentId()) ? "F06" : session.currentSegmentId();
                com.sirin.hk3gtl.common.finale.Hk3FinaleAdmission.advance(player,resume);
                return;
            }
            player.getPersistentData().remove("hk3gtl_finale_checkpoint_v5");
        }
        DialogueDefinition def = DialogueRegistry.getDialogue(dialogueId);
        if (def == null) return;

        // 调用结束处理器
        if (Hk3DialogueCompletionRules.maySettle(def, session.currentSegmentId(), completed) && def.endHandlerKey() != null) {
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
        com.sirin.hk3gtl.common.easter.Hk3EggReading.clear(playerUuid);
    }

    /** 死亡或维度切换后客户端会关闭屏幕；同步暂停服务端会话，不调用完成奖励。 */
    public static void pauseForTransition(ServerPlayer player) {
        var current=ACTIVE_SESSIONS.get(player.getUUID());
        if(current!=null)onDialogueEnd(player,current.dialogueId(),false);
        onPlayerDisconnect(player.getUUID());
    }

    public static void clearForServerStop() {
        for(UUID player:ACTIVE_SESSIONS.keySet())com.sirin.hk3gtl.common.easter.Hk3EggReading.clear(player);
        ACTIVE_SESSIONS.clear();
    }

    /**
     * 查询玩家当前是否有活跃对话。
     */
    public static boolean hasActiveDialogue(UUID playerUuid) {
        return ACTIVE_SESSIONS.containsKey(playerUuid)||com.sirin.hk3gtl.common.review.Hk3ReviewSessions.active(playerUuid);
    }

    @Nullable
    public static DialogueSession getSession(UUID playerUuid) {
        return ACTIVE_SESSIONS.get(playerUuid);
    }

    /**
     * 对话会话状态（不可变）。
     */
    public record DialogueSession(String dialogueId, String currentSegmentId, int extraData, long nonce) {
        public DialogueSession(String dialogueId, String currentSegmentId, int extraData) {
            this(dialogueId, currentSegmentId, extraData, java.util.concurrent.ThreadLocalRandom.current().nextLong(1, Long.MAX_VALUE));
        }
        public boolean accepts(String id, long token) {
            return token != 0 && nonce == token && dialogueId.equals(id);
        }
    }
}
