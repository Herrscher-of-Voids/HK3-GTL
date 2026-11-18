package com.sirin.hk3gtl.common.research;

import com.gregtechceu.gtceu.api.machine.MetaMachine;
import net.minecraft.server.level.ServerPlayer;

public final class Hk3RecipeEnvironment {
    private Hk3RecipeEnvironment() {}
    public static boolean throttlesByGaze(MetaMachine machine) {
        var level = machine.getLevel(); var pos = machine.getPos();
        if (level == null || level.isClientSide() || pos == null) return false;
        var nearest = level.getNearestPlayer(pos.getX() + 0.5, pos.getY() + 0.5, pos.getZ() + 0.5, 64, false);
        if (!(nearest instanceof ServerPlayer player)) return false;
        double gaze = Hk3ResearchTeams.gaze(player.server,
                Hk3ResearchTeams.scope(player.server, player.getUUID()));
        return Hk3IndustrialGazeSchedule.throttles(gaze, level.getGameTime(), pos.asLong());
    }
}
