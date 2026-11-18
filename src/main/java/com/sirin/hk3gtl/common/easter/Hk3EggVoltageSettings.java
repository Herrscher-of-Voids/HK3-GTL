package com.sirin.hk3gtl.common.easter;

import com.gregtechceu.gtceu.api.machine.trait.NotifiableItemStackHandler;
import com.gtlsupb.gtlsupb.common.machine.multiblock.UniversalVoltageRegulator;
import com.lowdragmc.lowdraglib.gui.modular.ModularUIContainer;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.entity.BlockEntity;

public final class Hk3EggVoltageSettings {
    public interface Access { NotifiableItemStackHandler hk3gtl$circuits(); }
    public record Snapshot(UniversalVoltageRegulator machine,int tier,ItemStack first,ItemStack second) {}
    private static final String PENDING="hk3EggManualVoltage";
    private Hk3EggVoltageSettings() {}

    public static Snapshot before(ServerPlayer player,AbstractContainerMenu menu){
        if(player.containerMenu!=menu||!menu.stillValid(player)||!(menu instanceof ModularUIContainer ui)
                ||!(ui.getModularUI().holder instanceof UniversalVoltageRegulator machine)
                ||!player.getUUID().equals(machine.uuid))return null;
        var inventory=((Access)machine).hk3gtl$circuits();
        return new Snapshot(machine,machine.getCurrentUnlockedTier(),inventory.getStackInSlot(0).copy(),inventory.getStackInSlot(1).copy());
    }

    public static void after(ServerPlayer player,AbstractContainerMenu menu,Snapshot before){
        if(before==null||player.containerMenu!=menu||!menu.stillValid(player)||!player.getUUID().equals(before.machine().uuid))return;
        var inventory=((Access)before.machine()).hk3gtl$circuits();
        var first=inventory.getStackInSlot(0);var second=inventory.getStackInSlot(1);
        if(ItemStack.matches(first,before.first())&&ItemStack.matches(second,before.second()))return;
        var pending=new CompoundTag();
        pending.putUUID("By",player.getUUID());pending.putInt("TierBefore",before.tier());
        pending.put("First",first.save(new CompoundTag()));pending.put("Second",second.save(new CompoundTag()));
        var block=(BlockEntity)before.machine().getHolder();block.getPersistentData().put(PENDING,pending);block.setChanged();
    }

    public static void updated(UniversalVoltageRegulator machine){
        if(machine.isRemote())return;
        var block=(BlockEntity)machine.getHolder();var tag=block.getPersistentData();
        if(!tag.contains(PENDING))return;
        var pending=tag.getCompound(PENDING);var inventory=((Access)machine).hk3gtl$circuits();
        int tier=machine.getCurrentUnlockedTier();
        if(pending.getUUID("By").equals(machine.uuid)&&tier>=0&&tier!=pending.getInt("TierBefore")
                &&ItemStack.matches(inventory.getStackInSlot(0),ItemStack.of(pending.getCompound("First")))
                &&ItemStack.matches(inventory.getStackInSlot(1),ItemStack.of(pending.getCompound("Second"))))
            Hk3EggEnergy.voltageChanged(machine,machine.uuid);
        tag.remove(PENDING);block.setChanged();
    }
}
