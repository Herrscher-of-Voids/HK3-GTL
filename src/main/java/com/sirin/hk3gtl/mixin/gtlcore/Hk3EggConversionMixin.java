package com.sirin.hk3gtl.mixin.gtlcore;
import org.gtlcore.gtlcore.common.machine.multiblock.electric.BlockConversionRoomMachine;
import com.lowdragmc.lowdraglib.misc.ItemStackTransfer;
import net.minecraft.world.item.ItemStack;
import net.minecraft.core.registries.BuiltInRegistries;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
@Mixin(value=BlockConversionRoomMachine.class,remap=false)
 
 
public abstract class Hk3EggConversionMixin {
    @Redirect(method="onWorking",at=@At(value="INVOKE",target="Lcom/lowdragmc/lowdraglib/misc/ItemStackTransfer;setStackInSlot(ILnet/minecraft/world/item/ItemStack;)V"))
    private void hk3gtl$converted(ItemStackTransfer inventory,int slot,ItemStack result){
        ItemStack before=inventory.getStackInSlot(slot).copy();inventory.setStackInSlot(slot,result);var machine=(BlockConversionRoomMachine)(Object)this;
        if(!before.isEmpty()&&!result.isEmpty()&&!before.is(result.getItem())&&ItemStack.matches(inventory.getStackInSlot(slot),result)&&BuiltInRegistries.ITEM.getKey(machine.getMachineStorageItem().getItem()).toString().equals("gtlcore:conversion_simulate_card"))com.sirin.hk3gtl.common.easter.Hk3EggProduction.receipt(machine,245);
    }
}
