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
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.EditBox;
import net.minecraft.world.entity.player.Inventory;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(value = CraftConfirmScreen.class, priority = 900, remap = false)
public abstract class Hk3NexusConfirmScreenMixin extends AEBaseScreen<CraftConfirmMenu> {
    @Shadow @Final private Button start;
    @Shadow @Final private Button selectCPU;
    @Unique private EditBox hk3gtl$attempts;
    @Unique private String hk3gtl$shownOdds = "";
    protected Hk3NexusConfirmScreenMixin(CraftConfirmMenu menu, Inventory inventory, Component title, ScreenStyle style) {
        super(menu, inventory, title, style);
    }

    @Inject(method = "updateBeforeRender", at = @At("TAIL"))
    private void hk3gtl$showExactPlan(CallbackInfo ci) {
        String odds = ((Hk3NexusNativeMenus.Confirm) getMenu()).hk3gtl$probabilityHint();
        if (!odds.isEmpty()) {
            if (hk3gtl$attempts == null) {
                var label = Component.literal("总尝试上限");
                hk3gtl$attempts = new EditBox(font, 0, 0, selectCPU.getWidth(), selectCPU.getHeight(), label);
                hk3gtl$attempts.setHint(label);
                hk3gtl$attempts.setMaxLength(256);
                hk3gtl$attempts.setFilter(text -> text.isEmpty() || text.charAt(0) != '0' && text.chars().allMatch(c -> c >= '0' && c <= '9'));
            }
            if (!odds.equals(hk3gtl$shownOdds)) {
                hk3gtl$shownOdds = odds;
                hk3gtl$attempts.setTooltip(net.minecraft.client.gui.components.Tooltip.create(Component.literal(
                        "所有概率批次共用此上限\n" + odds.substring(odds.indexOf('\n') + 1))));
            }
            if (!children().contains(hk3gtl$attempts)) addRenderableWidget(hk3gtl$attempts);
            hk3gtl$attempts.setX(selectCPU.getX());
            hk3gtl$attempts.setY(selectCPU.getY());
            selectCPU.visible = false;
            start.active = getMenu().getPlan() != null && !getMenu().getPlan().isSimulation() && !hk3gtl$attempts.getValue().isEmpty();
            setTextContent("dialog_title", Component.literal("概率合成"));
            setTextContent("cpu_status", Component.literal(odds.lines().findFirst().orElseThrow()));
            return;
        }
        if (hk3gtl$attempts != null) {
            removeWidget(hk3gtl$attempts);
            hk3gtl$attempts = null;
            hk3gtl$shownOdds = "";
            selectCPU.visible = true;
        }
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

    @Inject(method = "start", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$submitBudget(CallbackInfo ci) {
        if (hk3gtl$attempts == null) return;
        ci.cancel();
        ((Hk3NexusNativeMenus.Confirm) getMenu()).hk3gtl$startProbability(hk3gtl$attempts.getValue());
    }
}
