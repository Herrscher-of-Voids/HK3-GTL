package com.sirin.hk3gtl.mixin.gtmthings;

import com.hepdd.gtmthings.common.item.AdvancedTerminalBehavior;
import com.lowdragmc.lowdraglib.gui.widget.Widget;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;
import org.spongepowered.asm.mixin.gen.Invoker;

 
@Mixin(value=AdvancedTerminalBehavior.class,remap=false)
public interface Hk3AdvancedTerminalSettingsAccess {
    @Accessor("itemStack") void hk3gtl$setItemStack(ItemStack stack);
    @Accessor("autoBuildSetting") void hk3gtl$setAutoBuildSetting(AdvancedTerminalBehavior.AutoBuildSetting settings);
    @Invoker("createWidget") Widget hk3gtl$createWidget();
}
