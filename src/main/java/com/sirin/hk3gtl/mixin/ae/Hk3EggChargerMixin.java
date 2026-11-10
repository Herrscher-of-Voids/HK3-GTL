package com.sirin.hk3gtl.mixin.ae;
import appeng.blockentity.misc.ChargerBlockEntity;
import appeng.api.inventories.InternalInventory;
import appeng.core.definitions.AEItems;
import net.minecraft.world.entity.player.Player;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
/** 【变更记录 #1】2026-10-01 04:55:02（修订128）：删除无；新增充能石英实际转化与本人取出配对；用途：外部改写槽位使旧凭据失效，模拟充电不计，回执存于该充能器。 */
@Mixin(value=ChargerBlockEntity.class,remap=false)
public abstract class Hk3EggChargerMixin {
    @Unique private ItemStack hk3gtl$input=ItemStack.EMPTY;
    @Unique private boolean hk3gtl$taking;
    @Inject(method="doWork",at=@At("HEAD"),remap=false)private void hk3gtl$before(int elapsed,CallbackInfo ci){hk3gtl$input=((ChargerBlockEntity)(Object)this).getInternalInventory().getStackInSlot(0).copy();}
    @Inject(method="doWork",at=@At("RETURN"),remap=false)private void hk3gtl$after(int elapsed,CallbackInfo ci){
        var m=(ChargerBlockEntity)(Object)this;if(m.getLevel()!=null&&!m.getLevel().isClientSide&&AEItems.CERTUS_QUARTZ_CRYSTAL.isSameAs(hk3gtl$input)&&AEItems.CERTUS_QUARTZ_CRYSTAL_CHARGED.isSameAs(m.getInternalInventory().getStackInSlot(0))){m.getPersistentData().putBoolean("hk3gtl_egg_charged",true);m.setChanged();}hk3gtl$input=ItemStack.EMPTY;
    }
    @Inject(method="onChangeInventory",at=@At("HEAD"),remap=false)private void hk3gtl$changed(InternalInventory inventory,int slot,CallbackInfo ci){var m=(ChargerBlockEntity)(Object)this;if(m.getPersistentData().getBoolean("hk3gtl_egg_charged")){m.getPersistentData().remove("hk3gtl_egg_charged");m.setChanged();}}
    @Inject(method="activate",at=@At("HEAD"),remap=false)private void hk3gtl$takeBefore(Player p,CallbackInfo ci){var m=(ChargerBlockEntity)(Object)this;hk3gtl$taking=m.getPersistentData().getBoolean("hk3gtl_egg_charged")&&AEItems.CERTUS_QUARTZ_CRYSTAL_CHARGED.isSameAs(m.getInternalInventory().getStackInSlot(0));}
    @Inject(method="activate",at=@At("RETURN"),remap=false)private void hk3gtl$takeAfter(Player p,CallbackInfo ci){var m=(ChargerBlockEntity)(Object)this;if(p instanceof ServerPlayer server&&hk3gtl$taking&&m.getInternalInventory().getStackInSlot(0).isEmpty())com.sirin.hk3gtl.common.easter.Hk3EggVanilla.caseEvent(server,181);hk3gtl$taking=false;}
}
