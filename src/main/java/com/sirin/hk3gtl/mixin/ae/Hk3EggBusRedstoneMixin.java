package com.sirin.hk3gtl.mixin.ae;
import appeng.parts.automation.IOBusPart;
import appeng.core.definitions.AEItems;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.core.BlockPos;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
@Mixin(value=IOBusPart.class,remap=false)
/** 【变更记录 #1】2026-10-01 06:31:11（修订128）：删除无；新增联动真实安装/传输观察；修改无；用途：模拟、仅持有与空过滤不冒充成功，按本人安装归属。 */
/** 【变更记录 #2】2026-10-01 06:35:47（修订128）：删除：无；新增/修改：红石回调发生时电平已变化，改用先前真实电平基线，避免前后同读新电平导致永不触发；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public abstract class Hk3EggBusRedstoneMixin {
    @Shadow protected abstract boolean isSleeping();
    @Unique private boolean hk3gtl$known,hk3gtl$power,hk3gtl$changed;
    @Inject(method="addToWorld",at=@At("RETURN"))private void hk3gtl$baseline(CallbackInfo ci){var part=(IOBusPart)(Object)this;hk3gtl$power=part.getHost().hasRedstone();hk3gtl$known=true;}

    @Inject(method="onNeighborChanged",at=@At("HEAD"))private void hk3gtl$before(BlockGetter level,BlockPos pos,BlockPos neighbor,CallbackInfo ci){var part=(IOBusPart)(Object)this;boolean power=part.getHost().hasRedstone();hk3gtl$changed=hk3gtl$known&&power!=hk3gtl$power;hk3gtl$power=power;hk3gtl$known=true;}
    @Inject(method="onNeighborChanged",at=@At("RETURN"))private void hk3gtl$after(BlockGetter level,BlockPos pos,BlockPos neighbor,CallbackInfo ci){var part=(IOBusPart)(Object)this;if(hk3gtl$changed&&part.getMainNode().isActive()&&part.getUpgrades().isInstalled(AEItems.REDSTONE_CARD)&&!part.getRSMode().name().equals("IGNORE")&&(!part.getRSMode().name().equals("SIGNAL_PULSE")||hk3gtl$power))com.sirin.hk3gtl.common.easter.Hk3EggAeUpgrades.receipt(part,1,205,false);}
}
