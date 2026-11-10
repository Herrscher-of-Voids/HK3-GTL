package com.sirin.hk3gtl.common.finale;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.GameType;
import com.sirin.hk3gtl.common.dimension.Hk3GraduationData;

/** 修订198：负责人裁定未毕业返程恢复本人入场前模式；键随个人数据跨重登与重生。 */
public final class Hk3FinalePlayerMode {
    private static final String KEY = "hk3gtl_finale_return_mode_v5";
    private Hk3FinalePlayerMode() {}
    public static void remember(CompoundTag data, GameType original) {
        if (!data.contains(KEY)) data.putString(KEY, original.name());
    }
    public static GameType take(CompoundTag data) {
        if (!data.contains(KEY)) return null;
        GameType original = GameType.valueOf(data.getString(KEY));
        data.remove(KEY);
        return original;
    }
    public static boolean hasSavedMode(ServerPlayer player) {
        return player.getPersistentData().contains(KEY);
    }
    public static void enter(ServerPlayer player) {
        remember(player.getPersistentData(), player.gameMode.getGameModeForPlayer());
        player.setGameMode(GameType.ADVENTURE);
    }
    public static void leave(ServerPlayer player) {
        GameType original = take(player.getPersistentData());
        if (Hk3GraduationData.get(player.serverLevel()).isGraduated(player.getUUID())) player.setGameMode(GameType.CREATIVE);
        else if (original != null) player.setGameMode(original);
    }
}
