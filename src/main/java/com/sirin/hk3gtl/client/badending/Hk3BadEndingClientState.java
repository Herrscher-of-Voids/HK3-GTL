package com.sirin.hk3gtl.client.badending;

import com.sirin.hk3gtl.common.constants.Hk3Constants;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.screens.GenericDirtMessageScreen;
import net.minecraft.client.gui.screens.TitleScreen;
import net.minecraft.network.chat.Component;
import net.minecraft.util.Mth;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/**
 * 坏结局黑屏客户端状态机 —— 淡入计时 + 黑屏完成后退出到游戏主标题画面。
 *
 * <p>退出流程与原版「保存并退出到标题」一致：断开世界 → 集成服务端存盘 → 返回 {@link TitleScreen}，
 * 保证世界数据（含"已被抹除"改名）正常落盘。</p>
 *
 * <p>状态仅存在于客户端内存；所有字段仅在客户端主线程读写（网络包 handle 通过 enqueueWork 投递到主线程）。</p>
 */
@Mod.EventBusSubscriber(modid = Hk3Constants.MOD_ID, value = Dist.CLIENT)
public final class Hk3BadEndingClientState {

    private static boolean active = false;
    private static int fadeTicks = 60;
    private static int holdTicks = 30;
    private static int elapsed = 0;
    private static boolean returnToTitle = false;
    private static boolean exitIssued = false;

    private Hk3BadEndingClientState() {}

    /** 由 BadEndingBlackoutS2CPacket 在客户端主线程调用。 */
    public static void startBlackout(int fade, int hold, boolean returnToTitleAfter) {
        fadeTicks = Math.max(1, fade);
        holdTicks = Math.max(0, hold);
        returnToTitle = returnToTitleAfter;
        elapsed = 0;
        exitIssued = false;
        active = true;
    }

    public static boolean isActive() {
        return active;
    }

    /** 当前黑屏不透明度 0..1（淡入期间线性递增，之后保持全黑）。 */
    public static float getAlpha() {
        if (!active) return 0.0F;
        return Mth.clamp((float) elapsed / (float) fadeTicks, 0.0F, 1.0F);
    }

    @SubscribeEvent
    public static void onClientTick(TickEvent.ClientTickEvent event) {
        if (event.phase != TickEvent.Phase.END || !active || exitIssued) return;
        elapsed++;
        if (returnToTitle && elapsed >= fadeTicks + holdTicks) {
            exitIssued = true;
            active = false;
            exitToTitleScreen();
        }
    }

    /** 叙事层打击：按原版「保存并退出到标题」路径断开世界并回到主标题画面。 */
    private static void exitToTitleScreen() {
        Minecraft mc = Minecraft.getInstance();
        if (mc.level == null) return;
        boolean singleplayer = mc.isLocalServer();
        mc.level.disconnect();
        if (singleplayer) {
            // 集成服务端：走存盘界面，确保世界改名等数据落盘
            mc.clearLevel(new GenericDirtMessageScreen(Component.translatable("menu.savingLevel")));
        } else {
            mc.clearLevel();
        }
        mc.setScreen(new TitleScreen());
    }
}
