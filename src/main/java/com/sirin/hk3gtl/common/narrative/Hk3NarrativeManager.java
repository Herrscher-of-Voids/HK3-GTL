package com.sirin.hk3gtl.common.narrative;



import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import org.slf4j.Logger;
import com.mojang.logging.LogUtils;

/**
 * 世界文本叙事系统的总调度器。
 *
 * <h3>职责</h3>
 * <ul>
 *   <li>{@link #onEventTriggered}：由 {@code Hk3EventManagerImpl.trigger} 在写完事件标记后调用，
 *       查 {@link Hk3NarrativeNodes} 是否有对应节点，有则解锁并通知玩家</li>
 *   <li>{@link #unlockIfNew}：外部强制解锁入口（命令 / 剧情钩子），静默兼容已解锁情况</li>
 *   <li>通知文案统一在此打印，避免散落在 10+ 处 sendSystemMessage</li>
 * </ul>
 *
 * <h3>为什么要独立出 Manager</h3>
 * <ul>
 *   <li>SRP：{@link Hk3NarrativeLog} 只负责存储读写，{@link Hk3NarrativeNodes} 只负责注册表，
 *       本类负责"政策 / 副作用"—— 当事件触发时要不要同时解锁叙事？要不要发聊天？</li>
 *   <li>方便未来扩展：加成就 / 加音效 / 加弹窗 / 加 FTBQuests 联动时，只改本类</li>
 * </ul>
 *
 * <h3>聊天通知格式</h3>
 * <pre>
 * [空之律者·西琳] 解锁新档案条目：第一次注目
 * 使用"文明档案卷轴"可以查看（/give 或在崩坏三-GTL 创造栏可获取）
 * </pre>
 */
public final class Hk3NarrativeManager {

    private static final Logger LOGGER = LogUtils.getLogger();
    /** 玩家 persistentData：是否已显示过「打开文明档案卷轴」提示 */
    private static final String CODEX_HINT_SHOWN_TAG = "hk3gtl_codex_hint_shown";

    private Hk3NarrativeManager() {}

    /**
     * 事件触发时的解锁挂钩。查找是否有节点绑定到该 eventId，有则解锁。
     * 已解锁过的不会重复发通知，避免玩家聊天栏刷屏。
     *
     * @return true 表示本次新解锁了节点（用于外部打日志 / 触发音效）
     */
    public static boolean onEventTriggered(ServerPlayer player, String eventId) {
        boolean changed = false;
        for (Hk3NarrativeNode node : Hk3NarrativeNodes.byEventIdAll(eventId)) {
            if (unlockIfNew(player, node)) {
                changed = true;
            }
        }
        return changed;
    }

    /**
     * 直接解锁指定节点；常用于调试命令、强制剧情推进。
     * @return true 表示这次是新解锁
     */
    public static boolean unlockIfNew(ServerPlayer player, Hk3NarrativeNode node) {
        if (!Hk3NarrativeLog.unlock(player, node.id())) {
            return false; // 已解锁过，静默
        }

        LOGGER.info("[HK3GTL] 叙事节点解锁: {} ({})", node.id(), node.faction().id);

        // 头行：阵营 + 节点标题
        Component title = Component.translatable(node.titleKey()).withStyle(ChatFormatting.AQUA, ChatFormatting.BOLD);
        Component factionName = Component.translatable(node.faction().titleKey).withStyle(ChatFormatting.GRAY);
        player.sendSystemMessage(Component.literal("§d[档案解锁] ")
                .append(Component.literal("§8[").copy())
                .append(factionName)
                .append(Component.literal("§8] §r"))
                .append(title));

        // 次行：仅生涯首次解锁时提示打开文明档案卷轴
        CompoundTag data = player.getPersistentData();
        if (!data.getBoolean(CODEX_HINT_SHOWN_TAG)) {
            data.putBoolean(CODEX_HINT_SHOWN_TAG, true);
            player.sendSystemMessage(Component.translatable("hk3gtl.narrative.unlock.hint")
                    .withStyle(ChatFormatting.DARK_GRAY, ChatFormatting.ITALIC));
        }
        return true;
    }
}
