package com.sirin.hk3gtl.mixin.ae;

import appeng.client.gui.AEBaseScreen;
import appeng.client.gui.me.crafting.CraftConfirmScreen;
import appeng.client.gui.style.ScreenStyle;
import appeng.core.localization.GuiText;
import appeng.menu.me.crafting.CraftConfirmMenu;
import com.sirin.hk3gtl.common.integration.ae.nexus.crafting.Hk3NexusNativeMenus;
import com.sirin.hk3gtl.common.integration.ae.nexus.crafting.Hk3NexusPlanSummary;
import com.sirin.hk3gtl.common.integration.ae.Hk3AeAmountFormatter;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.player.Inventory;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(value = CraftConfirmScreen.class, priority = 900, remap = false)
public abstract class Hk3NexusConfirmScreenMixin extends AEBaseScreen<CraftConfirmMenu> {
    protected Hk3NexusConfirmScreenMixin(CraftConfirmMenu menu, Inventory inventory, Component title, ScreenStyle style) {
        super(menu, inventory, title, style);
    }

    @Inject(method = "updateBeforeRender", at = @At("TAIL"))
    private void hk3gtl$showExactPlan(CallbackInfo ci) {
        boolean nexus = Hk3NexusNativeMenus.isNexusCpu(getMenu().cpuName);
        if (getMenu().getPlan() instanceof Hk3NexusPlanSummary plan) {
            setTextContent("dialog_title", GuiText.CraftingPlan.text(Component.translatable(
                    "hk3gtl.nexus.byte_count", Hk3AeAmountFormatter.compact(plan.exactBytes))));
            if (plan.batched) setTextContent("cpu_status", Component.literal("分批总字节："
                    + Hk3AeAmountFormatter.compact(plan.exactBytes)));
            else if (nexus) setTextContent("cpu_status", GuiText.ConfirmCraftCpuStatus.text("∞", "∞"));
        } else if (nexus && getMenu().getPlan() != null && !getMenu().getPlan().isSimulation()) {
            setTextContent("cpu_status", GuiText.ConfirmCraftCpuStatus.text("∞", "∞"));
        }
    }
}
