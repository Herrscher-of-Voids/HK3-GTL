package com.sirin.hk3gtl.common.event;

import com.sirin.hk3gtl.common.bootstrap.Hk3ModHealthReport;
import com.sirin.hk3gtl.common.constants.Hk3Constants;
import com.sirin.hk3gtl.common.network.Hk3Network;
import com.sirin.hk3gtl.common.network.ModWelcomeS2CPacket;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.ModList;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.network.PacketDistributor;


@Mod.EventBusSubscriber(modid = Hk3Constants.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class Hk3ModWelcomeHandler {

    private static final String SEEN_VERSION_TAG = "hk3gtl_seen_welcome_version";

    private Hk3ModWelcomeHandler() {}

    @SubscribeEvent
    public static void onPlayerLoggedIn(PlayerEvent.PlayerLoggedInEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer player)) {
            return;
        }
        // 登录即同步一次注视度，保证 HUD 在进世界时立刻显示正确初值。
        com.sirin.hk3gtl.common.gaze.Hk3GazeManager.syncToClient(player);

        String current = ModList.get().getModContainerById(Hk3Constants.MOD_ID)
                .map(c -> c.getModInfo().getVersion().toString())
                .orElse("0.0.0");

        CompoundTag data = player.getPersistentData();
        String seen = data.getString(SEEN_VERSION_TAG);
        if (current.equals(seen)) {
            return;
        }
        data.putString(SEEN_VERSION_TAG, current);

        Hk3Network.CHANNEL.send(
                PacketDistributor.PLAYER.with(() -> player),
                new ModWelcomeS2CPacket(current, Hk3ModHealthReport.toStatusLines(current)));
    }
}
