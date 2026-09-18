package com.sirin.hk3gtl.common.gaze;



import com.sirin.hk3gtl.common.event.Hk3EventService;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;

/**
 * 注视阈值观察器：当注视跨越关键阈值时推送提醒，并触发与阈值绑定的核心事件。
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
            player.sendSystemMessage(
                    Component.literal("§d[崩坏三-GTL] §6")
                            .append(Component.translatable("hk3gtl.gaze.threshold." + threshold)));
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
