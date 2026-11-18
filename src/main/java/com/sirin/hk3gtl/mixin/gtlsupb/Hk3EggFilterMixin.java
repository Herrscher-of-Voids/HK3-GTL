package com.sirin.hk3gtl.mixin.gtlsupb;
import com.gtlsupb.gtlsupb.common.item.AEWirelessFilterTool;
import com.gtlsupb.gtlsupb.integration.ae2.WirelessAccessPointWirelessManager;
import net.minecraft.core.*;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
@Pseudo
@Mixin(targets="com.gtlsupb.gtlsupb.common.item.AEWirelessFilterTool",remap=false)
public abstract class Hk3EggFilterMixin {
    @Unique private final ThreadLocal<GlobalPos> hk3gtl$bound=new ThreadLocal<>();
    @Unique private final ThreadLocal<Boolean> hk3gtl$blacklisted=new ThreadLocal<>();
    @Inject(method="handleToggleFilter",at=@At("HEAD"))
    private void hk3gtl$before(ServerPlayer p,ItemStack stack,Level level,BlockPos pos,CallbackInfo ci){
        hk3gtl$bound.remove();hk3gtl$blacklisted.remove();
        GlobalPos bound=AEWirelessFilterTool.readBound(stack);if(bound==null)return;
        hk3gtl$bound.set(bound);hk3gtl$blacklisted.set(WirelessAccessPointWirelessManager.isBlacklisted(bound,GlobalPos.of(level.dimension(),pos)));
    }
    @Inject(method="handleToggleFilter",at=@At("RETURN"))
    private void hk3gtl$after(ServerPlayer p,ItemStack stack,Level level,BlockPos pos,CallbackInfo ci){
        GlobalPos bound=hk3gtl$bound.get();Boolean before=hk3gtl$blacklisted.get();hk3gtl$bound.remove();hk3gtl$blacklisted.remove();
        if(bound!=null&&before!=null&&bound.equals(AEWirelessFilterTool.readBound(stack))&&before!=WirelessAccessPointWirelessManager.isBlacklisted(bound,GlobalPos.of(level.dimension(),pos)))com.sirin.hk3gtl.common.easter.Hk3EggVanilla.caseEvent(p,264);
    }
}
