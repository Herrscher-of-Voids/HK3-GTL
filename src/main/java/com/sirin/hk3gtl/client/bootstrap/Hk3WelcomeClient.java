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

/**
 * 欢迎包只登记待显示内容，由客户端主线程在可阅读时打开。
 * 【变更记录 #1】2026-10-01 16:11:00（修订133）
 * 删除：无；新增：登录延迟展示、手动重读返回原界面、断线清理。
 * 修改：替代包到达时直接抢屏；用途：等待加载完成并保留正在进行的阅读。
 * 【变更记录 #2】2026-10-31 15:36:22（第2次备注 · 修订188）
 * - 删除：无。
 * - 新增：欢迎包携带网络连接身份进入客户端队列，客户端 tick 使用当前连接身份取出。
 * - 修改：旧连接的延迟包不再被新服务器会话接收；连续手动重读保留原返回屏幕。
 * - 用途：隔离断线竞态，避免旧服说明在新服登录后抢屏或污染已读确认。
 */
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
