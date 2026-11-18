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
public abstract class Hk3EggPortalTripMixin {
    @Unique private ServerLevel hk3gtl$from;@Unique private BlockPos hk3gtl$origin;@Unique private boolean hk3gtl$valid;
    @Inject(method="changeDimension(Lnet/minecraft/server/level/ServerLevel;Lnet/minecraftforge/common/util/ITeleporter;)Lnet/minecraft/world/entity/Entity;",remap=false,at=@At("HEAD"))private void hk3gtl$before(ServerLevel destination,ITeleporter teleporter,CallbackInfoReturnable<Entity> ci){var p=(ServerPlayer)(Object)this;hk3gtl$from=p.serverLevel();hk3gtl$origin=p.blockPosition();hk3gtl$valid=teleporter.isVanilla()&&(p.level().getBlockState(p.blockPosition()).is(Blocks.NETHER_PORTAL)||p.level().getBlockState(p.blockPosition().above()).is(Blocks.NETHER_PORTAL));}
    @Inject(method="changeDimension(Lnet/minecraft/server/level/ServerLevel;Lnet/minecraftforge/common/util/ITeleporter;)Lnet/minecraft/world/entity/Entity;",remap=false,at=@At("RETURN"))private void hk3gtl$after(ServerLevel destination,ITeleporter teleporter,CallbackInfoReturnable<Entity> ci){var p=(ServerPlayer)(Object)this;if(ci.getReturnValue()==p&&hk3gtl$from!=null)com.sirin.hk3gtl.common.easter.Hk3EggExploration.portal(p,hk3gtl$from,hk3gtl$origin,hk3gtl$valid);hk3gtl$from=null;hk3gtl$origin=null;hk3gtl$valid=false;}
}
