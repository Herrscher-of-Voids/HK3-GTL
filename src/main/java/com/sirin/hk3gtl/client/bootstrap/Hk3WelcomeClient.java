package com.sirin.hk3gtl.client.bootstrap;

import com.sirin.hk3gtl.common.bootstrap.Hk3WelcomePending;
import com.sirin.hk3gtl.common.constants.Hk3Constants;
import net.minecraft.client.Minecraft;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.ClientPlayerNetworkEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.List;

 










@Mod.EventBusSubscriber(modid = Hk3Constants.MOD_ID, value = Dist.CLIENT, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class Hk3WelcomeClient {
    private static final Hk3WelcomePending<Notice> PENDING = new Hk3WelcomePending<>();
    private record Notice(String version, List<String> lines, boolean manual) {}
    private Hk3WelcomeClient() {}

    public static void offer(String version, List<String> lines) {
        var mc = Minecraft.getInstance();
        offer(version, lines, currentConnection(mc));
    }

    /** 网络包调用方传入包所属连接，避免切服期间读取到新的客户端连接。 */
    public static void offer(String version, List<String> lines, Object connection) {
        boolean manual = lines.contains("open:manual");
        PENDING.offer(currentConnection(Minecraft.getInstance()), connection, new Notice(version, List.copyOf(lines), manual), manual);
    }

    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent event) {
        if (event.phase != TickEvent.Phase.END) return;
        var mc = Minecraft.getInstance();
        Notice notice = PENDING.take(currentConnection(mc), mc.player != null && mc.level != null && mc.getOverlay() == null, mc.screen != null);
        if (notice == null) return;
        var parent = notice.manual() ? (mc.screen instanceof Hk3ModWelcomeScreen previous ? previous.returnScreen() : mc.screen) : null;
        mc.setScreen(new Hk3ModWelcomeScreen(notice.version(), notice.lines(), parent));
    }

    @SubscribeEvent public static void logout(ClientPlayerNetworkEvent.LoggingOut event) { PENDING.clear(); }

    private static Object currentConnection(Minecraft mc) {
        var listener = mc.getConnection();
        return listener == null ? null : listener.getConnection();
    }
}
