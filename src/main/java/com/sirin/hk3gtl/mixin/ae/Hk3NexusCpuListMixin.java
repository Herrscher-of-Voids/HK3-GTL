package com.sirin.hk3gtl.mixin.ae;

import appeng.client.gui.widgets.CPUSelectionList;
import appeng.core.localization.ButtonToolTips;
import appeng.menu.me.crafting.CraftingStatusMenu;
import com.llamalad7.mixinextras.injector.ModifyExpressionValue;
import com.llamalad7.mixinextras.sugar.Local;
import com.sirin.hk3gtl.common.integration.ae.nexus.crafting.Hk3NexusNativeMenus;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyArg;
import org.spongepowered.asm.mixin.injection.ModifyVariable;

import java.util.List;

@Mixin(value = CPUSelectionList.class, remap = false)
public abstract class Hk3NexusCpuListMixin {
    @ModifyExpressionValue(method = "drawBackgroundLayer", at = @At(value = "INVOKE",
            target = "Lappeng/client/gui/widgets/CPUSelectionList;formatStorage(Lappeng/menu/me/crafting/CraftingStatusMenu$CraftingCpuListEntry;)Ljava/lang/String;"))
    private String hk3gtl$storage(String value, @Local(name = "cpu") CraftingStatusMenu.CraftingCpuListEntry cpu) {
        return Hk3NexusNativeMenus.isNexusCpu(cpu.name()) ? "∞" : value;
    }

    @ModifyVariable(method = "drawBackgroundLayer", at = @At("STORE"), name = "coProcessorCount")
    private String hk3gtl$parallel(String value, @Local(name = "cpu") CraftingStatusMenu.CraftingCpuListEntry cpu) {
        return Hk3NexusNativeMenus.isNexusCpu(cpu.name()) ? "∞" : value;
    }

    @ModifyArg(method = "getTooltip", at = @At(value = "INVOKE",
            target = "Lappeng/client/gui/Tooltip;<init>(Ljava/util/List;)V"), index = 0)
    private List<Component> hk3gtl$tooltip(List<Component> lines) {
        if (Hk3NexusNativeMenus.isNexusCpu(lines.get(0))) {
            lines.set(1, ButtonToolTips.CpuStatusStorage.text(Component.literal("∞")).withStyle(ChatFormatting.GRAY));
            lines.set(2, ButtonToolTips.CpuStatusCoProcessors.text(Component.literal("∞")).withStyle(ChatFormatting.GRAY));
        }
        return lines;
    }
}
