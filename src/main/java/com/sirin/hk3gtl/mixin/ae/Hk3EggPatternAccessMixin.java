package com.sirin.hk3gtl.mixin.ae;
import appeng.menu.implementations.PatternAccessTermMenu;
import appeng.helpers.InventoryAction;
import net.minecraft.server.level.ServerPlayer;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
@Mixin(value=PatternAccessTermMenu.class,remap=false)
/** 【变更记录 #1】2026-10-01 05:24:14（修订128）：删除无；新增样板访问界面真实操作前后本人持有样板数量核对，排除创造复制；修改无；用途：原条件的只读观察，不改物品与权限。 */
public abstract class Hk3EggPatternAccessMixin {
    @Unique private long hk3gtl$patterns;
    @Inject(method="doAction",at=@At("HEAD"))
    private void hk3gtl$before(ServerPlayer p,InventoryAction action,int slot,long id,CallbackInfo ci){hk3gtl$patterns=com.sirin.hk3gtl.common.easter.Hk3EggAeMenus.patterns(p);}
    @Inject(method="doAction",at=@At("RETURN"))
    private void hk3gtl$after(ServerPlayer p,InventoryAction action,int slot,long id,CallbackInfo ci){
        if(action!=InventoryAction.CREATIVE_DUPLICATE&&com.sirin.hk3gtl.common.easter.Hk3EggAeMenus.patterns(p)>hk3gtl$patterns)com.sirin.hk3gtl.common.easter.Hk3EggVanilla.caseEvent(p,200);
    }
}
