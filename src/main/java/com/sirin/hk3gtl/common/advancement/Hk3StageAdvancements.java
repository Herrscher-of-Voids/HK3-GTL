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
 * 
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
 */
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
