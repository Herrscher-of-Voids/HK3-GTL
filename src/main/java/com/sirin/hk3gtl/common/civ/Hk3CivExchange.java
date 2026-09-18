package com.sirin.hk3gtl.common.civ;



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
