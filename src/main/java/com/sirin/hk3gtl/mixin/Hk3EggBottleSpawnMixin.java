package com.sirin.hk3gtl.mixin;
import net.minecraft.core.*;
import net.minecraft.core.dispenser.DefaultDispenseItemBehavior;
import net.minecraft.world.level.Level;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.entity.Entity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
@Mixin(DefaultDispenseItemBehavior.class)

public abstract class Hk3EggBottleSpawnMixin {
    @Redirect(method="execute",at=@At(value="INVOKE",target="Lnet/minecraft/core/dispenser/DefaultDispenseItemBehavior;spawnItem(Lnet/minecraft/world/level/Level;Lnet/minecraft/world/item/ItemStack;ILnet/minecraft/core/Direction;Lnet/minecraft/core/Position;)V"))
    private void hk3gtl$scope(Level level,ItemStack stack,int speed,Direction facing,Position pos,BlockSource source,ItemStack input){com.sirin.hk3gtl.common.easter.Hk3EggDispenser.spawn(source,level,stack,speed,facing,pos);}
    @Redirect(method="spawnItem",at=@At(value="INVOKE",target="Lnet/minecraft/world/level/Level;addFreshEntity(Lnet/minecraft/world/entity/Entity;)Z"))
    private static boolean hk3gtl$eject(Level level,Entity entity){boolean success=level.addFreshEntity(entity);if(success)com.sirin.hk3gtl.common.easter.Hk3EggDispenser.ejected(entity);return success;}
}
