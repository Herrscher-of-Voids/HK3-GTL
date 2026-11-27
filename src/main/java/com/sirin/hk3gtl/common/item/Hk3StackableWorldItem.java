package com.sirin.hk3gtl.common.item;

import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

public final class Hk3StackableWorldItem extends Item {
    public Hk3StackableWorldItem() {
        super(new Properties());
    }

    @Override
    public void inventoryTick(ItemStack stack, Level level, Entity entity, int slot, boolean selected) {
        if (!level.isClientSide && entity instanceof Player) stack.removeTagKey("Source");
    }
}
