package com.sirin.hk3gtl.common.advancement;

import com.sirin.hk3gtl.common.constants.Hk3Constants;
import net.minecraft.advancements.Advancement;
import net.minecraft.advancements.AdvancementProgress;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.PlayerAdvancements;
import net.minecraft.server.level.ServerPlayer;
import org.slf4j.Logger;
import com.mojang.logging.LogUtils;

import javax.annotation.Nullable;
import java.util.HashMap;
import java.util.Map;

/**
 * 【文件职责】
 * - 把“玩家跨越工业阶段”的里程碑事件映射为原版进度（advancement）授予，纯展示成就感。
 * - 关键调用链：Hk3EventService#tryTriggerFirstTime 首次触发某阶段事件 -> 本类 onStageEvent -> 服务端授予对应进度。
 *
 * 【文件背景】
 * - 阶段进度 JSON 位于 data/hk3gtl/advancements/stage/*.json，触发器统一为 minecraft:impossible，
 *   即原版无法自动达成，必须由服务端代码手动授予；这样可复用现有事件系统，避免用 inventory_changed
 *   背包检测（会被创造/掉落绕过）。
 * - 阶段事件与进度映射：
 *   E-MS-001 崩坏能时代 -> stage/era_start
 *   E-MS-003 海渊突破   -> stage/abyss
 *   E-MS-005 虚数觉醒   -> stage/imaginary
 *   E-MS-007 量子跃迁   -> stage/quantum
 *   E-MS-010 终焉降临   -> stage/finality
 *   E-MS-015 文明毕业   -> stage/graduation
 *
 * 【变更记录 #1】2026-07-21 11:00:00（第 1 次备注 · 新增阶段成就展示）
 * - 删除：无。
 * - 新增：
 *   1) 阶段事件 -> 原版进度 的静态映射表 STAGE_EVENT_TO_ADVANCEMENT。
 *   2) onStageEvent()：命中阶段事件时授予对应进度的全部剩余条件（幂等，已完成则跳过）。
 * - 修改：无（独立新增类，不改动既有事件/研究逻辑）。
 * - 用途：
 *   1) 玩家每跨越一个工业阶段弹出成就 toast 并进入成就树，提供阶段性成就感，无任何玩法副作用。
 *   2) 关键风险点：仅在服务端主线程调用；进度不存在时静默跳过，不抛异常影响事件主流程。
 */
/** 【变更记录 #2】2026-10-01 14:10:35（修订129）：删除：无；新增/修改：撤销旧六阶段事件直接授予；旧事件只刷新当前真实研究、文明与本人会面进度；用途：任务和进度只投影真实账本，不授研究、物品或审查资格。 */
public final class Hk3StageAdvancements {

    private Hk3StageAdvancements() {}
    /** 旧事件仅请求真实数据投影，不再凭持物里程碑或旧世界毕业标记授予阶段。 */
    public static void onStageEvent(ServerPlayer player,String eventId){
        if(!eventId.startsWith("E-MS-")||!player.server.isSameThread())return;
        var scope=com.sirin.hk3gtl.common.research.Hk3ResearchTeams.scope(player.server,player.getUUID());
        com.sirin.hk3gtl.common.integration.Hk3GuideAdvancements.sync(player,
                com.sirin.hk3gtl.common.integration.Hk3QuestProgressBridge.facts(player.server,scope));
    }
}
