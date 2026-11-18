package com.sirin.hk3gtl.mixin;
import net.minecraft.world.entity.item.ItemEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;
@Mixin(ItemEntity.class)
public interface Hk3EggItemThrowerAccessor { @Accessor("thrower") java.util.UUID hk3gtl$thrower(); }
