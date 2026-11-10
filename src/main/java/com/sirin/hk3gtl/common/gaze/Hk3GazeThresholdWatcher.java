package com.sirin.hk3gtl.common.gaze;


/**
 * 【文件职责】
 * - 维护 Hk3GazeThresholdWatcher 的核心功能实现。
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
 * 【段内说明】
 * - 复杂方法补充“干什么 / 边界 / 线程侧”精简中文注释。
 */
import com.sirin.hk3gtl.common.event.Hk3EventService;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;

/**
 * 注视阈值观察器：当注视跨越关键阈值时推送提醒，并触发与阈值绑定的核心事件。
 */
/**
 * 【变更记录 #1】2026-09-30 16:20:43（内测5修订110）
 * 删除：被新版通知读取流程替代的旧分支，历史备注保留。
 * 新增／修改：注视阈值提示转入通知与收件箱，原阈值去重和事件触发保持。
 * 用途：通知与业务结果分离，服务端授权和个人持久化；不改结构、贴图和贸易。
 */
public final class Hk3GazeThresholdWatcher {

    private static final int[] THRESHOLDS = {50, 100, 200, 300, 500, 700, 800, 900, 1000};

    private Hk3GazeThresholdWatcher() {}

    public static void onGazeChanged(ServerPlayer player, int oldValue, int newValue) {
        if (newValue <= oldValue) {
            return;
        }
        for (int threshold : THRESHOLDS) {
            if (oldValue >= threshold || newValue < threshold) {
                continue;
            }
            String tag = "hk3gtl_gaze_threshold_" + threshold;
            if (player.getPersistentData().getBoolean(tag)) {
                continue;
            }
            player.getPersistentData().putBoolean(tag, true);
            com.sirin.hk3gtl.common.phone.Hk3PhoneService.notify(player,"gaze_threshold_"+threshold,
                    "注视发生变化",Component.translatable("hk3gtl.gaze.threshold."+threshold).getString());
            triggerThresholdEvent(player, threshold);
        }
    }

    private static void triggerThresholdEvent(ServerPlayer player, int threshold) {
        switch (threshold) {
            case 100 -> Hk3EventService.tryTriggerFirstTime(player, "E-SF-002", "hk3gtl.event.sf002");
            case 500 -> Hk3EventService.tryTriggerFirstTime(player, "E-SA-001", "hk3gtl.event.sa001");
            case 800 -> Hk3EventService.tryTriggerFirstTime(player, "E-HQ-001", "hk3gtl.event.hq001");
            default -> {
            }
        }
    }
}
