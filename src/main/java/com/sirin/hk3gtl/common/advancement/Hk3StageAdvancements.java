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


public final class Hk3StageAdvancements {

    private static final Logger LOGGER = LogUtils.getLogger();

    /** 阶段里程碑事件 ID -> 进度资源路径（相对 data/hk3gtl/advancements/）。 */
    private static final Map<String, String> STAGE_EVENT_TO_ADVANCEMENT = new HashMap<>();

    static {
        STAGE_EVENT_TO_ADVANCEMENT.put("E-MS-001", "stage/era_start");
        STAGE_EVENT_TO_ADVANCEMENT.put("E-MS-003", "stage/abyss");
        STAGE_EVENT_TO_ADVANCEMENT.put("E-MS-005", "stage/imaginary");
        STAGE_EVENT_TO_ADVANCEMENT.put("E-MS-007", "stage/quantum");
        STAGE_EVENT_TO_ADVANCEMENT.put("E-MS-010", "stage/finality");
        STAGE_EVENT_TO_ADVANCEMENT.put("E-MS-015", "stage/graduation");
    }

    private Hk3StageAdvancements() {}

    /**
     * 若该事件是阶段里程碑事件，则授予对应原版进度。
     * 边界：非阶段事件直接返回；进度未加载或已完成时静默跳过。
     * 安全点：仅服务端主线程调用；捕获查询异常，避免影响事件触发主流程。
     *
     * @param player   触发事件的服务端玩家
     * @param eventId  事件 ID（如 E-MS-003）
     */
    public static void onStageEvent(ServerPlayer player, String eventId) {
        String path = STAGE_EVENT_TO_ADVANCEMENT.get(eventId);
        if (path == null) {
            return;
        }
        Advancement advancement = findAdvancement(player, path);
        if (advancement == null) {
            LOGGER.warn("[HK3GTL] 阶段进度未找到: {} (事件 {})", path, eventId);
            return;
        }
        PlayerAdvancements tracker = player.getAdvancements();
        AdvancementProgress progress = tracker.getOrStartProgress(advancement);
        if (progress.isDone()) {
            return;
        }
        for (String criterion : progress.getRemainingCriteria()) {
            tracker.award(advancement, criterion);
        }
    }

    @Nullable
    private static Advancement findAdvancement(ServerPlayer player, String path) {
        ResourceLocation id = new ResourceLocation(Hk3Constants.MOD_ID, path);
        return player.server.getAdvancements().getAdvancement(id);
    }
}
