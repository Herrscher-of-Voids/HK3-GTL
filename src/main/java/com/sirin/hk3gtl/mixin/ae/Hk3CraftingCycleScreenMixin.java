package com.sirin.hk3gtl.mixin.ae;

import appeng.client.gui.AEBaseScreen;
import appeng.client.gui.Icon;
import appeng.client.gui.me.crafting.CraftConfirmScreen;
import appeng.client.gui.style.ScreenStyle;
import appeng.menu.me.crafting.CraftConfirmMenu;
import com.sirin.hk3gtl.common.integration.ae.Hk3CraftingCycleFlag;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.player.Inventory;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

import java.util.List;

@Mixin(value = CraftConfirmScreen.class, remap = false)
public abstract class Hk3CraftingCycleScreenMixin extends AEBaseScreen<CraftConfirmMenu> {
    protected Hk3CraftingCycleScreenMixin(CraftConfirmMenu menu, Inventory inventory,
                                        Component title, ScreenStyle style) {
        super(menu, inventory, title, style);
    }

    @Inject(method = "drawFG", at = @At("TAIL"))
    private void hk3gtl$drawCycle(GuiGraphics graphics, int offsetX, int offsetY,
                                 int mouseX, int mouseY, CallbackInfo ci) {
        var plan = getMenu().getPlan();
        if (plan == null || !((Hk3CraftingCycleFlag) plan).hk3gtl$hasCycles()) return;
        var label = Component.translatable("hk3gtl.ae.cycle.present");
        int labelWidth = font.width(label);
        int x = imageWidth - labelWidth - 24;
        Icon.SCHEDULING_ROUND_ROBIN.getBlitter().dest(x, 2).blit(graphics);
        graphics.drawString(font, label, x + 18, 6, 0x404040, false);
        int localMouseX = mouseX - offsetX;
        int localMouseY = mouseY - offsetY;
        if (localMouseX >= x && localMouseX < imageWidth - 6 && localMouseY >= 2 && localMouseY < 18) {
            graphics.pose().pushPose();
            graphics.pose().translate(-offsetX, -offsetY, 0);
            drawTooltipWithHeader(graphics, mouseX, mouseY, List.of(
                    Component.translatable("hk3gtl.ae.cycle.present"),
                    Component.translatable("hk3gtl.ae.cycle.description")));
            graphics.pose().popPose();
        }
    }
}
