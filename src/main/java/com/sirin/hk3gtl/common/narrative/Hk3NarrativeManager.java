package com.sirin.hk3gtl.common.narrative;


/**
 * 【文件职责】
 * - 管理 Hk3NarrativeManager 叙事节点与档案显示数据。
 * - 关键调用链：由上层系统入口调用 -> 本文件核心方法 -> 下游模块。
 *
 * 【变更记录】2026-05-19
 * - 修改：
 *   1) 文明档案卷轴打开提示仅在玩家生涯首次解锁档案时显示一次（hk3gtl_codex_hint_shown）。
 * - 用途：
 *   1) 帮助维护者快速理解文件职责、变更背景与风险点。
 *
 * 【段内说明】
 * - 复杂方法补充“干什么 / 边界 / 线程侧”精简中文注释。
 */
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
/**
 * 【变更记录 #1】2026-09-30 16:20:43（内测5修订110）
 * 删除：被新版通知读取流程替代的旧分支，历史备注保留。
 * 新增／修改：已解锁档案的完整原文进入收件箱，仍引用原叙事节点与正文键；阅读不再次解锁或发奖。
 * 用途：通知与业务结果分离，服务端授权和个人持久化；不改结构、贴图和贸易。
 */
/** 【变更记录 #2】2026-10-01 01:54:14（修订127）：删除：被替代的旧分支；新增/修改：统一分类和正文投递，研究失败残篇同样低优先，重复事件不重复通知；用途：个人收藏与正式资格分离，保留历史记录。 */
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
        var receipt=Hk3CollectionRecords.record(player.getPersistentData(),
                com.sirin.hk3gtl.common.phone.Hk3PhoneData.get(player),player.getUUID(),node,System.currentTimeMillis(),
                key->Component.translatable(key).getString());
        if(receipt.unlocked())LOGGER.info("[HK3GTL] 叙事节点解锁: {} ({})",node.id(),node.faction().id);
        if(receipt.delivered())com.sirin.hk3gtl.common.phone.Hk3PhoneService.toast(player,"narrative_"+node.id(),
                receipt.title(),receipt.body(),receipt.kind(),Hk3CollectionCatalog.optional(node.id())?0:1);
        player.getPersistentData().putBoolean(CODEX_HINT_SHOWN_TAG,true);
        return receipt.unlocked();
    }
}
