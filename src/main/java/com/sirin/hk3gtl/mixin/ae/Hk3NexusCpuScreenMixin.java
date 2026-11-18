package com.sirin.hk3gtl.mixin.ae;

import appeng.client.gui.me.crafting.CraftingCPUScreen;
import appeng.core.localization.GuiText;
import appeng.menu.me.crafting.CraftingStatus;
import appeng.menu.me.crafting.CraftingStatusMenu;
import com.llamalad7.mixinextras.injector.ModifyExpressionValue;
import com.sirin.hk3gtl.common.integration.ae.nexus.crafting.Hk3NexusNativeMenus;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;

@Mixin(value = CraftingCPUScreen.class, remap = false)
public abstract class Hk3NexusCpuScreenMixin {
    @Shadow private CraftingStatus status;

    @ModifyExpressionValue(method = "updateBeforeRender", at = @At(value = "INVOKE",
            target = "Lorg/apache/commons/lang3/time/DurationFormatUtils;formatDuration(JLjava/lang/String;)Ljava/lang/String;"))
    private String hk3gtl$projectedEta(String value) {
        if (status.getStartItemCount() != Long.MAX_VALUE && status.getRemainingItemCount() != Long.MAX_VALUE)
            return value;
        if (!(((CraftingCPUScreen<?>) (Object) this).getMenu() instanceof CraftingStatusMenu menu)) return value;
        int selected = menu.getSelectedCpuSerial();
        return menu.cpuList.cpus().stream().anyMatch(cpu -> cpu.serial() == selected
                && Hk3NexusNativeMenus.isNexusCpu(cpu.name())) ? GuiText.CalculatingWait.getLocal() : value;
    }
}
