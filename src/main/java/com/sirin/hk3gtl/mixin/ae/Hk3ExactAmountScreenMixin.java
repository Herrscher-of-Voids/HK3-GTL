package com.sirin.hk3gtl.mixin.ae;

import appeng.client.gui.AEBaseScreen;
import appeng.client.gui.me.crafting.CraftAmountScreen;
import appeng.client.gui.style.ScreenStyle;
import appeng.client.gui.widgets.NumberEntryWidget;
import appeng.menu.me.crafting.CraftAmountMenu;
import com.sirin.hk3gtl.client.ae.Hk3NexusNumberEntry;
import com.sirin.hk3gtl.client.ae.Hk3ProbabilityAmountScreen;
import com.sirin.hk3gtl.common.integration.ae.nexus.crafting.Hk3NexusNativeMenus;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.player.Inventory;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ProbabilitySupport;

import java.math.BigInteger;

// 同一 HEAD 的回调按低优先级先执行，超 Long 数量必须先于 Core 提交。
@Mixin(value = CraftAmountScreen.class, priority = 900, remap = false)
public abstract class Hk3ExactAmountScreenMixin extends AEBaseScreen<CraftAmountMenu> {
    @Shadow @Final private NumberEntryWidget amountToCraft;
    @Shadow @Final private Button next;
    @Shadow private boolean amountInitialized;
    @Unique private Button hk3gtl$probabilityButton;
    @Unique private boolean hk3gtl$amountRestored;

    protected Hk3ExactAmountScreenMixin(CraftAmountMenu menu, Inventory inventory,
                                         Component title, ScreenStyle style) {
        super(menu, inventory, title, style);
    }

    @Inject(method = "updateBeforeRender", at = @At("HEAD"))
    private void hk3gtl$enableExactAmount(CallbackInfo ci) {
        ((Hk3NexusNumberEntry) amountToCraft).hk3gtl$enableExact();
    }

    @Inject(method = "updateBeforeRender", at = @At("TAIL"))
    private void hk3gtl$restoreAmountAndProbabilityEntry(CallbackInfo ci) {
        if (amountInitialized && !hk3gtl$amountRestored) {
            String initialAmount = ((Hk3NexusNativeMenus.Amount) getMenu()).hk3gtl$initialAmount();
            if (!initialAmount.isEmpty())
                ((Hk3NexusNumberEntry) amountToCraft).hk3gtl$setExactValue(new BigInteger(initialAmount));
            hk3gtl$amountRestored = true;
        }
        next.active = ((Hk3NexusNumberEntry) amountToCraft).hk3gtl$exactValue()
                .filter(amount -> amount.signum() > 0).isPresent();
        if (Hk3ProbabilitySupport.AVAILABLE) {
            if (hk3gtl$probabilityButton == null)
                hk3gtl$probabilityButton = Button.builder(Component.literal("概率订单"), button ->
                        switchToScreen(new Hk3ProbabilityAmountScreen((CraftAmountScreen) (Object) this, getMenu())))
                        .bounds(0, 0, 104, 20).build();
            if (!children().contains(hk3gtl$probabilityButton)) addRenderableWidget(hk3gtl$probabilityButton);
            hk3gtl$probabilityButton.setX(Math.max(2, (width - 104) / 2));
            hk3gtl$probabilityButton.setY(Math.max(4, getGuiTop() - 24));
        }
    }

    @Inject(method = "confirm", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$confirmExactAmount(CallbackInfo ci) {
        ((Hk3NexusNumberEntry) amountToCraft).hk3gtl$enableExact();
        var amount = ((Hk3NexusNumberEntry) amountToCraft).hk3gtl$exactValue();
        var menu = (Hk3NexusNativeMenus.Amount) getMenu();
        if (amount.isPresent() && amount.get().compareTo(BigInteger.valueOf(Long.MAX_VALUE)) > 0) {
            menu.hk3gtl$confirmAmount(amount.get(), amountToCraft.startsWithEquals(), Screen.hasShiftDown());
            ci.cancel();
        }
    }
}
