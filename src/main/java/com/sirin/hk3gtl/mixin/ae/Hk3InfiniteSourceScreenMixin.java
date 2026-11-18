package com.sirin.hk3gtl.mixin.ae;

import appeng.api.stacks.AEKey;
import appeng.api.stacks.AmountFormat;
import appeng.client.gui.me.common.MEStorageScreen;
import appeng.core.localization.ButtonToolTips;
import appeng.core.localization.Tooltips;
import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import com.sirin.hk3gtl.common.integration.ae.Hk3InfiniteSourceMenu;
import net.minecraft.network.chat.Component;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;

@Mixin(value = MEStorageScreen.class, priority = 900, remap = false)
public abstract class Hk3InfiniteSourceScreenMixin {
    @WrapOperation(method = "renderSlot(Lnet/minecraft/client/gui/GuiGraphics;Lnet/minecraft/world/inventory/Slot;)V",
            remap = true, at = @At(value = "INVOKE", remap = false,
            target = "Lappeng/api/stacks/AEKey;formatAmount(JLappeng/api/stacks/AmountFormat;)Ljava/lang/String;"))
    private String hk3gtl$infiniteAmount(AEKey key, long amount, AmountFormat format, Operation<String> original) {
        return ((Hk3InfiniteSourceMenu) ((MEStorageScreen<?>) (Object) this).getMenu())
                .hk3gtl$infiniteSources().contains(key) ? "\u221e" : original.call(key, amount, format);
    }

    @WrapOperation(method = "renderGridInventoryEntryTooltip", at = @At(value = "INVOKE",
            target = "Lappeng/core/localization/Tooltips;getAmountTooltip(Lappeng/core/localization/ButtonToolTips;Lappeng/api/stacks/AEKey;J)Lnet/minecraft/network/chat/Component;"))
    private Component hk3gtl$infiniteTooltip(ButtonToolTips label, AEKey key, long amount,
                                            Operation<Component> original) {
        return ((Hk3InfiniteSourceMenu) ((MEStorageScreen<?>) (Object) this).getMenu())
                .hk3gtl$infiniteSources().contains(key) ? label.text("\u221e").withStyle(Tooltips.MUTED_COLOR)
                : original.call(label, key, amount);
    }
}
