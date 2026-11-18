package com.sirin.hk3gtl.mixin.ae;
import appeng.menu.me.items.PatternEncodingTermMenu;
import appeng.menu.slot.RestrictedInputSlot;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
@Mixin(value=PatternEncodingTermMenu.class,remap=false)
public abstract class Hk3EggEncodeMixin {
    @Inject(method="clear",at=@At("RETURN"))private void hk3gtl$cancel(CallbackInfo ci){var menu=(PatternEncodingTermMenu)(Object)this;if(menu.getPlayer() instanceof ServerPlayer p&&p.containerMenu==menu&&menu.stillValid(p))com.sirin.hk3gtl.common.easter.Hk3EggAeMenus.cancelled(p,menu);}
    @Shadow @Final private RestrictedInputSlot encodedPatternSlot;
    @Unique private ItemStack hk3gtl$old=ItemStack.EMPTY;
    @Inject(method="encode",at=@At("HEAD"),remap=false)
    private void hk3gtl$before(CallbackInfo ci){hk3gtl$old=encodedPatternSlot.getItem().copy();var menu=(PatternEncodingTermMenu)(Object)this;if(menu.getPlayer() instanceof ServerPlayer p)com.sirin.hk3gtl.common.easter.Hk3EggAeMenus.encoding(p);}
    @Inject(method="encode",at=@At("RETURN"),remap=false)
    private void hk3gtl$after(CallbackInfo ci){
        var menu=(PatternEncodingTermMenu)(Object)this;
        if(menu.getPlayer() instanceof ServerPlayer p&&p.containerMenu==menu&&menu.stillValid(p))com.sirin.hk3gtl.common.easter.Hk3EggAe.encoded(p,hk3gtl$old,encodedPatternSlot.getItem());
        hk3gtl$old=ItemStack.EMPTY;
    }
}
