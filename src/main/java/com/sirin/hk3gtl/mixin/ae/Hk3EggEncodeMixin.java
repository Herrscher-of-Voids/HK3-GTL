package com.sirin.hk3gtl.mixin.ae;
import appeng.menu.me.items.PatternEncodingTermMenu;
import appeng.menu.slot.RestrictedInputSlot;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
/** 【变更记录 #1】2026-10-01 04:45:29（修订128）：删除无；新增AE样板成功写入前后快照；用途：只读当前本人有效菜单，不把空白清除、权限失效、早退当编码成功。 */
@Mixin(value=PatternEncodingTermMenu.class,remap=false)
/** 【变更记录 #2】2026-10-01 13:26:03（修订128）：删除：无；新增/修改：预览后清空视为主动取消，任何编码尝试清除标记，避免成功编码后关闭误授；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
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
