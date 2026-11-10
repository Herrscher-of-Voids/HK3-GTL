package com.sirin.hk3gtl.mixin;
import net.minecraft.server.level.*;
import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.block.Blocks;
import net.minecraftforge.common.util.ITeleporter;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
@Mixin(ServerPlayer.class)
/** 【变更记录 #1】2026-10-01 12:18:50（修订128）：删除：无；新增/修改：只认原版下界门传送的实际返回结果与同一对入口位置，不把命令传送计入；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #2】2026-10-01 12:30:49（修订128）：删除：无；新增/修改：Forge新增的双参数传送方法不参与Mojang混淆映射，显式锁定重载避免误绑原版入口；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public abstract class Hk3EggPortalTripMixin {
    @Unique private ServerLevel hk3gtl$from;@Unique private BlockPos hk3gtl$origin;@Unique private boolean hk3gtl$valid;
    @Inject(method="changeDimension(Lnet/minecraft/server/level/ServerLevel;Lnet/minecraftforge/common/util/ITeleporter;)Lnet/minecraft/world/entity/Entity;",remap=false,at=@At("HEAD"))private void hk3gtl$before(ServerLevel destination,ITeleporter teleporter,CallbackInfoReturnable<Entity> ci){var p=(ServerPlayer)(Object)this;hk3gtl$from=p.serverLevel();hk3gtl$origin=p.blockPosition();hk3gtl$valid=teleporter.isVanilla()&&(p.level().getBlockState(p.blockPosition()).is(Blocks.NETHER_PORTAL)||p.level().getBlockState(p.blockPosition().above()).is(Blocks.NETHER_PORTAL));}
    @Inject(method="changeDimension(Lnet/minecraft/server/level/ServerLevel;Lnet/minecraftforge/common/util/ITeleporter;)Lnet/minecraft/world/entity/Entity;",remap=false,at=@At("RETURN"))private void hk3gtl$after(ServerLevel destination,ITeleporter teleporter,CallbackInfoReturnable<Entity> ci){var p=(ServerPlayer)(Object)this;if(ci.getReturnValue()==p&&hk3gtl$from!=null)com.sirin.hk3gtl.common.easter.Hk3EggExploration.portal(p,hk3gtl$from,hk3gtl$origin,hk3gtl$valid);hk3gtl$from=null;hk3gtl$origin=null;hk3gtl$valid=false;}
}
