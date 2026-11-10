package com.sirin.hk3gtl.mixin.gtmthings;
import com.hepdd.gtmthings.common.cover.WirelessEnergyReceiveCover;
import com.gregtechceu.gtceu.api.cover.CoverBehavior;
import com.gregtechceu.gtceu.api.capability.IEnergyContainer;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import com.sirin.hk3gtl.common.easter.Hk3EggCovers;
@Mixin(value=WirelessEnergyReceiveCover.class,priority=1100,remap=false)
/** 【变更记录 #1】2026-10-01 06:19:47（修订128）：删除无；新增真实操作及连续状态旁注；修改无；用途：只读已加载世界与本人回执，不改游戏结果、不授研究资格。 */
/** 【变更记录 #2】2026-10-01 14:27:54（修订130）：删除无；新增GTLCore覆盖兼容优先级1100；修改原1000与GTLCore的1000同级冲突，允许观察覆盖后两条真实接收调用；用途：修复初始化崩溃，保持能源返回值和276彩蛋条件不变。 */
public abstract class Hk3EggWirelessEnergyMixin {
    @Shadow @Final private int tier;
    @Inject(method="onAttached",at=@At("RETURN"))private void hk3gtl$attached(ItemStack stack,ServerPlayer p,CallbackInfo ci){Hk3EggCovers.attached((CoverBehavior)(Object)this,p);}
    @Redirect(method="updateEnergy",at=@At(value="INVOKE",target="Lcom/gregtechceu/gtceu/api/capability/IEnergyContainer;addEnergy(J)J"))
    private long hk3gtl$added(IEnergyContainer energy,long requested){long actual=energy.addEnergy(requested);if(tier==1&&actual>0)Hk3EggCovers.delivered((CoverBehavior)(Object)this,276);return actual;}
    @Redirect(method="updateEnergy",at=@At(value="INVOKE",target="Lcom/gregtechceu/gtceu/api/capability/IEnergyContainer;acceptEnergyFromNetwork(Lnet/minecraft/core/Direction;JJ)J"))
    private long hk3gtl$accepted(IEnergyContainer energy,Direction side,long voltage,long amps){long actual=energy.acceptEnergyFromNetwork(side,voltage,amps);if(tier==1&&voltage>0&&actual>0)Hk3EggCovers.delivered((CoverBehavior)(Object)this,276);return actual;}
}
