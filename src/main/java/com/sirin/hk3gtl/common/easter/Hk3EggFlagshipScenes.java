package com.sirin.hk3gtl.common.easter;

import com.sirin.hk3gtl.common.machine.hyperion.Hk3HyperionMachine;
import com.sirin.hk3gtl.common.narrative.Hk3NarrativeLog;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.event.entity.living.LivingEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = "hk3gtl")
public final class Hk3EggFlagshipScenes {
    private Hk3EggFlagshipScenes() {}

    @SubscribeEvent
    public static void jump(LivingEvent.LivingJumpEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer player)
                || Hk3NarrativeLog.isUnlocked(player, "E-EG-072")
                || !Hk3HyperionMachine.containsVerifiedInterior(player.serverLevel(), player.blockPosition())) return;
        if (Hk3EggVanilla.increment(player, "flagshipRealJumps", 100) == 100)
            Hk3EggVanilla.caseEvent(player, 72);
    }
}
