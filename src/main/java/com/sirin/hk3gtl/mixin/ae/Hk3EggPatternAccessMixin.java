package com.sirin.hk3gtl.mixin.ae;
import appeng.menu.implementations.PatternAccessTermMenu;
import appeng.helpers.InventoryAction;
import net.minecraft.server.level.ServerPlayer;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
@Mixin(value=PatternAccessTermMenu.class,remap=false)

public abstract class Hk3EggPatternAccessMixin {
    @Unique private long hk3gtl$patterns;
    @Inject(method="doAction",at=@At("HEAD"))
    private void hk3gtl$before(ServerPlayer p,InventoryAction action,int slot,long id,CallbackInfo ci){hk3gtl$patterns=com.sirin.hk3gtl.common.easter.Hk3EggAeMenus.patterns(p);}
    @Inject(method="doAction",at=@At("RETURN"))
    private void hk3gtl$after(ServerPlayer p,InventoryAction action,int slot,long id,CallbackInfo ci){
        if(action!=InventoryAction.CREATIVE_DUPLICATE&&com.sirin.hk3gtl.common.easter.Hk3EggAeMenus.patterns(p)>hk3gtl$patterns)com.sirin.hk3gtl.common.easter.Hk3EggVanilla.caseEvent(p,200);
    }
}
