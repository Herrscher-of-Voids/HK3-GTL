package com.sirin.hk3gtl.common.dialogue;


/**
 * 【文件职责】
 * - 维护 DialogueSessionManager 的核心功能实现。
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
 * 【变更记录 #2】2026-05-31 22:45:00（第 2 次备注 · 内测三第 2 次更新）
 * - 修改：
 *   1) onPlayerChoice 校验掩码的默认值由 0b11111(5 位) 改为 (1<<IF_BRANCH_COUNT)-1，与 10 条 IF 线一致。
 * - 用途：
 *   1) 当 extraData 为 0(无掩码) 时仍允许后 5 条新增 IF 被选中，防止服务端误判“选项不可用”。
 *
 * 【段内说明】
 * - 复杂方法补充“干什么 / 边界 / 线程侧”精简中文注释。
 */
/**
 * 【变更记录 #3】2026-09-29 17:51:46（内测5修订93）
 * - 删除：旧正文活动引用被审核原文替代；保留历史资源和存档。
 * - 新增／修改：正式终审保存段落检查点及每人每存档五选；校验选择的当前段落；仅FU01自然结束可结算，暂停及校对不结算。
 * - 用途：接通审核正文；其他系统触发及归属不据此宣称完成。
 */
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
/** 【变更记录 #4】2026-09-30 20:28:36（修订117）：删除无；新增：所有对话奖励处理器要求正常结束且当前段落没有待选分支；修改许可读取/结算守卫；用途：分开审查与研究，防预览或关闭误授予。 */
/** 【变更记录 #5】2026-09-30 23:34:26（修订119）：删除：世界级结果对所有玩家的隐式授权；新增/修改：正常会面与个人攻击账本绑定；坏结局中止仅删除本人活跃会话，不发完成奖励；用途：个人结算不覆盖其他玩家，未完成的资格采集仍单独接入。 */
/** 【变更记录 #6】2026-10-01 04:34:58（修订128）：删除：旧固定上限或被替代的分支；新增/修改：已验证IF段落附阅读令牌，结束或中止均清理，不改变选择名额；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #7】2026-10-01 16:49:18（修订135）：删除旧个人NBT检查点作为准入依据；新增正式入口/检查点/结算的服务端会面快照校验；修改关闭与断线保留同次快照；用途：物品、预览、手动传送不能授予终审，IF免费阅读入口保持独立。 */
/** 【变更记录 #8】2026-10-01 17:04:49（修订136）：删除无；新增实体重建/跨维度的暂停入口及服务器关闭清理；修改断线同步清理阅读令牌；用途：清理临时会话不授予完成，已确认资格和检查点仍由持久账本保存。 */
/** 【变更记录 #9】2026-10-01 18:42:57（修订140）：删除无；新增正式审查占用检查及入口隔离；修改通用启动不能绕过审查服务创建正式会面；用途：预览和终审保留原逻辑，禁止两类会话同时占用屏幕。 */
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
    /** 修订198：开屏与推进均刷新令牌，拒绝旧会面、旧段落和循环返回后的重放。 */
    public record DialogueSession(String dialogueId, String currentSegmentId, int extraData, long nonce) {
        public DialogueSession(String dialogueId, String currentSegmentId, int extraData) {
            this(dialogueId, currentSegmentId, extraData, java.util.concurrent.ThreadLocalRandom.current().nextLong(1, Long.MAX_VALUE));
        }
        public boolean accepts(String id, long token) {
            return token != 0 && nonce == token && dialogueId.equals(id);
        }
    }
}
