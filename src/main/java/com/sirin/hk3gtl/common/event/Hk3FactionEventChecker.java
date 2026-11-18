package com.sirin.hk3gtl.common.event;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
/**
 * 阵营事件检查器：处理 15 个阵营共 65 个事件的触发逻辑。
 *
 * <h3>触发方式分类</h3>
 * <ul>
 *   <li><b>里程碑依赖</b>：{@link #checkFactionEvents} 每秒轮询，检查相关里程碑是否已触发</li>
 *   <li><b>注视度阈值</b>：{@link #checkFactionEvents} 每秒轮询，读取 persistentData 中的注视度</li>
 *   <li><b>多方块建成</b>：{@link #onMultiblockFormedFaction} 由 Hk3EventManagerImpl 在成型时调用</li>
 *   <li><b>研究完成</b>：{@link #onResearchCompleted} 由 Hk3ResearchManager 在研究完成时调用</li>
 *   <li><b>外部触发</b>：{@link #triggerFactionEvent} 由其他系统（毕业、特殊条件）直接调用</li>
 * </ul>
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>新增阵营事件 → 按触发类型添加到对应方法中</li>
 *   <li>新增研究触发 → 在 {@link #onResearchCompleted} 的 switch 中添加 case</li>
 *   <li>新增多方块触发 → 在 {@link #onMultiblockFormedFaction} 的 switch 中添加 case</li>
 *   <li>所有 lang key 格式 → "hk3gtl.event.{prefix}{number}"，如 "hk3gtl.event.ot002"</li>
 * </ul>
 *
 * @see Hk3EventManagerImpl 里程碑与 FB 事件管理器
 */
public class Hk3FactionEventChecker {
    private Hk3FactionEventChecker() {}
    /** 正式故事由独立服务登录及每100tick补投，避免旧每秒轮询重复扫描。 */
    public static void checkFactionEvents(ServerPlayer player) {}
    public static void onMultiblockFormedFaction(ServerPlayer player,String machineId) {
        com.sirin.hk3gtl.common.narrative.Hk3LegacyArchiveService.ensure(player);
    }
    public static void onResearchCompleted(ServerPlayer player,String researchId) {
        com.sirin.hk3gtl.common.narrative.Hk3LegacyArchiveService.ensure(player);
    }
    /** 旧调用者只能请求重核，不能以eventId或langKey替代真实现行事实。 */
    public static void triggerFactionEvent(ServerPlayer player,String eventId,String langKey) {
        if(com.sirin.hk3gtl.common.narrative.Hk3LegacyArchiveMigration.all().containsKey(eventId))
            com.sirin.hk3gtl.common.narrative.Hk3LegacyArchiveService.ensure(player);
        else Hk3EventService.tryTriggerFirstTime(player,eventId,langKey);
    }
    public static void onFinaleDialogueStarted(ServerPlayer player) {
        triggerFactionEvent(player,"E-HQ-005","hk3gtl.event.hq005");
        Hk3EasterEggChecker.onFinaleDialogueOpened(player);
    }
    public static void triggerPreGraduationCertification(ServerPlayer player) {
        com.sirin.hk3gtl.common.narrative.Hk3LegacyArchiveService.ensure(player);
    }
    public static void triggerGraduationComplete(ServerPlayer player) {
        Hk3EventService.tryTriggerFirstTime(player,"E-MS-015","hk3gtl.event.ms015");
        Hk3EasterEggChecker.onGraduationComplete(player);
    }
}
