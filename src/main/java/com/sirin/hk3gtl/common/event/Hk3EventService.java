package com.sirin.hk3gtl.common.event;


/**
 * 【文件职责】
 * - 处理 Hk3EventService 相关事件分发与触发。
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
 * 【变更记录 #2】2026-07-21 11:00:00（第 2 次备注 · 新增阶段成就展示）
 * - 删除：无。
 * - 新增：
 *   1) markEventTriggered 内调用 {@link Hk3StageAdvancements#onStageEvent}，
 *      在事件首次触发时同步授予对应原版进度（advancement）。
 * - 修改：无（仅在既有桥接链末尾追加一次授予调用，非阶段事件在被调用方内部直接返回）。
 * - 用途：
 *   1) 玩家每跨越一个工业阶段弹出成就 toast，纯展示成就感，不改变任何玩法状态。
 *   2) 关键风险点：授予逻辑在服务端主线程执行，进度缺失时静默跳过。
 *
 * 【段内说明】
 * - 复杂方法补充“干什么 / 边界 / 线程侧”精简中文注释。
 */
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
/**
 * 【变更记录 #3】2026-09-30 15:49:23（第3次编号备注 · 内测5修订109）
 * 删除：过期的计算或无运行依据的分支；保留历史备注。
 * 新增／修改：原有注视事件增加明确来源键和持久去重；数值与触发条件不变，不追补旧记录，不以此完成新课题。
 * 用途：统一注视与研究联动，服务端判定；不新增结构或贴图。
 */
/**
 * 【变更记录 #4】2026-09-30 16:20:43（内测5修订110）
 * 删除：被新版通知读取流程替代的旧分支，历史备注保留。
 * 新增／修改：统一事件通知和条件说明进入收件箱；彩蛋低优先，业务标记/回调不变，聊天命令输出不拦截。
 * 用途：通知与业务结果分离，服务端授权和个人持久化；不改结构、贴图和贸易。
 */
/** 【变更记录 #5】2026-10-01 01:54:14（修订127）：删除：被替代的旧分支；新增/修改：通知优先级从明确分类目录读取，未知或正式条目不按前缀豁免；用途：个人收藏与正式资格分离，保留历史记录。 */
/** 【变更记录 #6】2026-10-01 03:56:20（修订128）：删除：旧固定上限或被替代的分支；新增/修改：已审核彩蛋目录走单独收藏路径，先投递成功再记账，不调用旧研究自动完成或阶段奖励；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #7】2026-10-01 04:09:54（修订128）：删除：旧固定上限或被替代的分支；新增/修改：关闭旧目录事件直发入口，未迁移条件不再误发新正文；历史收藏不删除；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #8】2026-10-01 22:50:14（第8次备注 · 内测5修订155）：删除玩家展示中的旧电压及开发说明；新增现行正文投影或对应回归；修改仅限呈现与检索，不改变进度、回执、触发条件或权限；用途：统一发布版玩家文案，历史备注保留。 */
/** 【变更记录 #9】2026-11-04 06:12:15（第9次备注 · 内测5修订196）：删除64正式旧条件直接投递/赠研究/注视的执行路径；新增准确新版目录守卫；修改新正式故事由独立服务读取真实来源与本人全文；用途：旧收藏与历史标记保留，HQ005终审自身及彩蛋不受此守卫影响。 */
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
        if(com.sirin.hk3gtl.common.narrative.Hk3LegacyArchiveMigration.all().containsKey(eventId))return false;
        CompoundTag data = player.getPersistentData();
        if (isEventMarked(data, eventId)) {
            return false;
        }
        // 全部500条仅能由服务端事实规则投递；旧调用者没有已审核条件的证明。
        if(com.sirin.hk3gtl.common.easter.Hk3EggCatalog.contains(eventId)) return false;
        markEventTriggered(player, data, eventId);
        if (isHighTierFactionEvent(eventId)) {
            Hk3GazeManager.addGazeOnce(player, 15, "event:" + eventId);
        }
        Hk3CivExchange.recountLevel(player);
        String body=eventChatLangKey==null||eventChatLangKey.isEmpty()?"":Component.translatable(eventChatLangKey).getString();
        boolean coveredByArchive=eventChatLangKey!=null&&com.sirin.hk3gtl.common.narrative.Hk3NarrativeNodes.byEventIdAll(eventId)
                .stream().anyMatch(n->n.bodyKeys().contains(eventChatLangKey));
        if(!body.isBlank()&&!coveredByArchive)com.sirin.hk3gtl.common.phone.Hk3PhoneService.notify(player,"event_"+eventId,
                com.sirin.hk3gtl.common.narrative.Hk3CollectionCatalog.optionalEvent(eventId)?"发现一段额外记录":"收到新的事件记录",body,com.sirin.hk3gtl.common.narrative.Hk3CollectionCatalog.optionalEvent(eventId)?"chatter":"notice");
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
