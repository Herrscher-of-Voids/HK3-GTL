package com.sirin.hk3gtl.common.civ;


/**
 * 【文件职责】
 * - 维护 Hk3CivExchange 的核心功能实现。
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
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;

/**
 * 文明交流等级（0~3）统计与存储。
 */
public final class Hk3CivExchange {

    public static final String TAG_CIV_LEVEL = "hk3gtl_civ_level";
    private static final String EVENT_PREFIX = "hk3gtl_evt_";
    private static final String[] FACTION_PREFIXES = {
            "E-OT-", "E-HQ-", "E-WL-", "E-EL-", "E-WS-", "E-AE-",
            "E-SF-", "E-FM-", "E-BR-", "E-SA-", "E-MB-", "E-KI-",
            "E-LB-", "E-TS-", "E-FH-"
    };

    private Hk3CivExchange() {}

    public static int recountLevel(ServerPlayer player) {
        CompoundTag data = player.getPersistentData();
        int touched = 0;
        for (String factionPrefix : FACTION_PREFIXES) {
            if (hasFactionEvent(data, factionPrefix)) {
                touched++;
            }
        }
        int level = toLevel(touched);
        data.putInt(TAG_CIV_LEVEL, level);
        return level;
    }

    public static int getLevel(Player player) {
        return Math.max(0, Math.min(3, player.getPersistentData().getInt(TAG_CIV_LEVEL)));
    }

    private static int toLevel(int touchedFactionCount) {
        if (touchedFactionCount >= 9) return 3;
        if (touchedFactionCount >= 6) return 2;
        if (touchedFactionCount >= 3) return 1;
        return 0;
    }

    private static boolean hasFactionEvent(CompoundTag data, String factionPrefix) {
        String fullPrefix = EVENT_PREFIX + factionPrefix;
        for (String key : data.getAllKeys()) {
            if (key.startsWith(fullPrefix) && data.getBoolean(key)) {
                return true;
            }
        }
        return false;
    }
}
