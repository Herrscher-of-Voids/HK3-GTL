package com.sirin.hk3gtl.common.event;



import com.sirin.hk3gtl.common.advancement.Hk3StageAdvancements;
import com.sirin.hk3gtl.common.narrative.Hk3NarrativeManager;
import com.sirin.hk3gtl.common.research.Hk3ResearchManager;
import com.sirin.hk3gtl.common.civ.Hk3CivExchange;
import com.sirin.hk3gtl.common.gaze.Hk3GazeManager;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;
import org.slf4j.Logger;
import com.mojang.logging.LogUtils;

import javax.annotation.Nullable;

/**
 * 统一事件触发服务：写 {@code hk3gtl_evt_*}、桥接研究与叙事，并推送客户端研究/事件同步。
 * <p>
 * 从 {@link Hk3EventManagerImpl} / {@link Hk3FactionEventChecker} 抽离，供研究失败彩蛋等任意系统复用，
 * 避免重复维护 TAG 前缀与桥接顺序。
 */
public final class Hk3EventService {

    private static final Logger LOGGER = LogUtils.getLogger();

    /** 与历史存档一致，勿改 */
    public static final String EVENT_TAG_PREFIX = "hk3gtl_evt_";

    private Hk3EventService() {}

    public static String eventStorageKey(String eventId) {
        return EVENT_TAG_PREFIX + eventId;
    }

    public static boolean isEventMarked(CompoundTag data, String eventId) {
        return data.getBoolean(eventStorageKey(eventId));
    }

    public static boolean hasTriggered(Player player, String eventId) {
        return isEventMarked(player.getPersistentData(), eventId);
    }

    /**
     * 若该事件尚未触发：写入标记、通知研究自动完成、解锁叙事，并同步客户端事件/研究键。
     *
     * @param eventChatLangKey 非 null 且非空时发送粉色 {@code [崩坏三-GTL]} 前缀聊天行
     * @return true 表示本次为新触发
     */
    public static boolean tryTriggerFirstTime(ServerPlayer player, String eventId, @Nullable String eventChatLangKey) {
        CompoundTag data = player.getPersistentData();
        if (isEventMarked(data, eventId)) {
            return false;
        }
        markEventTriggered(player, data, eventId);
        if (isHighTierFactionEvent(eventId)) {
            Hk3GazeManager.addGaze(player, 15);
        }
        Hk3CivExchange.recountLevel(player);
        String conditionLangKey = easterEggConditionLangKey(eventId);
        if (conditionLangKey != null) {
            player.sendSystemMessage(
                    Component.literal("§d[崩坏三-GTL] §b")
                            .append(Component.translatable("hk3gtl.event.condition_prefix"))
                            .append(Component.literal(" "))
                            .append(Component.translatable(conditionLangKey)));
        }
        if (eventChatLangKey != null && !eventChatLangKey.isEmpty()) {
            player.sendSystemMessage(
                    Component.literal("§d[崩坏三-GTL] §f").append(Component.translatable(eventChatLangKey)));
        }
        // 研究 onEventTriggered 内部可能已 sync；无研究变化时仍需把新事件键推到客户端
        Hk3ResearchManager.syncClientResearchState(player);
        return true;
    }

    private static void markEventTriggered(ServerPlayer player, CompoundTag data, String eventId) {
        data.putBoolean(eventStorageKey(eventId), true);
        LOGGER.info("[HK3GTL] 事件触发: {}", eventId);
        Hk3ResearchManager.onEventTriggered(player, eventId);
        Hk3NarrativeManager.onEventTriggered(player, eventId);
        // 跨阶段里程碑事件同步授予对应原版进度（纯展示成就感，非阶段事件内部直接跳过）
        Hk3StageAdvancements.onStageEvent(player, eventId);
    }

    private static boolean isHighTierFactionEvent(String eventId) {
        return eventId.startsWith("E-OT-")
                || eventId.startsWith("E-HQ-")
                || eventId.startsWith("E-WS-")
                || eventId.startsWith("E-SA-")
                || eventId.startsWith("E-AE-")
                || eventId.startsWith("E-LB-")
                || eventId.startsWith("E-KI-");
    }

    @Nullable
    private static String easterEggConditionLangKey(String eventId) {
        if (!eventId.startsWith("E-EG-") || eventId.length() < 8) {
            return null;
        }
        return "hk3gtl.event.eg" + eventId.substring(5).toLowerCase() + ".condition";
    }
}
