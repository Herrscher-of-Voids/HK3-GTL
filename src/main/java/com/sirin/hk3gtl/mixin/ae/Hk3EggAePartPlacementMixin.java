package com.sirin.hk3gtl.mixin.ae;
import appeng.parts.AEBasePart;
import net.minecraft.world.entity.player.Player;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
@Mixin(value=AEBasePart.class,remap=false)
/** 【变更记录 #1】2026-10-01 06:31:11（修订128）：删除无；新增联动真实安装/传输观察；修改无；用途：模拟、仅持有与空过滤不冒充成功，按本人安装归属。 */
public abstract class Hk3EggAePartPlacementMixin {
    @Inject(method="onPlacement",at=@At("RETURN"))private void hk3gtl$clear(Player p,CallbackInfo ci){if(!p.level().isClientSide)com.sirin.hk3gtl.common.easter.Hk3EggAeUpgrades.cleared((AEBasePart)(Object)this);}
}
