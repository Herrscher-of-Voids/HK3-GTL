package com.sirin.hk3gtl.client;

import net.minecraft.client.Minecraft;
import net.minecraft.network.chat.Component;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.InputEvent;
import net.minecraftforge.event.entity.player.ItemTooltipEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.gtlcore.gtlcore.common.item.UltimateTerminalBehavior;
import org.lwjgl.glfw.GLFW;

@Mod.EventBusSubscriber(modid = "hk3gtl", value = Dist.CLIENT)
public final class Hk3BuildTaskKeys {
    @SubscribeEvent public static void mouse(InputEvent.MouseButton.Pre event) {
        if (event.getAction() != GLFW.GLFW_PRESS || event.getButton() != GLFW.GLFW_MOUSE_BUTTON_LEFT) return;
        int modifiers = event.getModifiers();
        if ((modifiers & (GLFW.GLFW_MOD_SHIFT | GLFW.GLFW_MOD_CONTROL)) == 0) return;

        var mc = Minecraft.getInstance();
        if (mc.screen != null || mc.player == null
                || !UltimateTerminalBehavior.isUltimateTerminal(mc.player.getMainHandItem())) return;
        event.setCanceled(true);
        mc.player.connection.sendCommand((modifiers & GLFW.GLFW_MOD_SHIFT) != 0 ? "hk3build resume" : "hk3build cancel");
    }

    @SubscribeEvent public static void tooltip(ItemTooltipEvent event) {
        if (UltimateTerminalBehavior.isUltimateTerminal(event.getItemStack()))
            event.getToolTip().add(Component.translatable("hk3gtl.build_task.controls"));
    }
}
