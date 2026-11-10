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
 * 坏结局客户端过渡状态机 —— 抓取演出计时，最终黑屏后退出到游戏主标题画面。
 *
 * <p>退出流程与原版「保存并退出到标题」一致：断开世界 → 集成服务端存盘 → 返回 {@link TitleScreen}，
 * 保证世界数据（含"已被抹除"改名）正常落盘。</p>
 *
 * <p>状态仅存在于客户端内存；所有字段仅在客户端主线程读写（网络包 handle 通过 enqueueWork 投递到主线程）。</p>
 */
@Mod.EventBusSubscriber(modid = Hk3Constants.MOD_ID, value = Dist.CLIENT)
public final class Hk3BadEndingClientState {

    private static boolean active = false;
    private static int fadeTicks = 100;
    private static int holdTicks = 35;
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

    /** Continuous cinematic progress, including partial ticks for smooth HUD animation. */
    public static float getProgress(float partialTick) {
        if (!active) return 0.0F;
        return Mth.clamp((elapsed + partialTick) / fadeTicks, 0.0F, 1.0F);
    }

    /** Black curtain rises after the impact rather than hiding the entire grab. */
    public static float getAlpha(float partialTick) {
        float progress = getProgress(partialTick);
        if (progress < 0.72F) return 0.48F * Math.min(1.0F, progress / 0.55F);
        return Mth.clamp(0.48F + (progress - 0.72F) / 0.28F * 0.52F, 0.0F, 1.0F);
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
