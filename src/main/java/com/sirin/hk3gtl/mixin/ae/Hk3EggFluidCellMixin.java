package com.sirin.hk3gtl.mixin.ae;
import appeng.me.cells.BasicCellInventory;
import appeng.api.stacks.*;
import appeng.api.config.Actionable;
import appeng.api.networking.security.IActionSource;
import net.minecraft.world.item.ItemStack;
import net.minecraft.core.registries.BuiltInRegistries;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
@Mixin(value=BasicCellInventory.class,remap=false)
/** 【变更记录 #1】2026-10-01 06:31:11（修订128）：删除无；新增联动真实安装/传输观察；修改无；用途：模拟、仅持有与空过滤不冒充成功，按本人安装归属。 */
public abstract class Hk3EggFluidCellMixin {
    @Shadow @Final private ItemStack i;
    @Inject(method="innerInsert",at=@At("RETURN"))private void hk3gtl$inserted(AEKey what,long amount,Actionable mode,CallbackInfoReturnable<Long> ci){
        if(mode!=Actionable.MODULATE||ci.getReturnValue()<=0||!(what instanceof AEFluidKey)||!BuiltInRegistries.ITEM.getKey(i.getItem()).toString().equals("gtlcore:fluid_storage_cell_1m")||i.getTag()==null||!i.getTag().hasUUID("hk3EggCellInstaller"))return;
        var server=net.minecraftforge.server.ServerLifecycleHooks.getCurrentServer();if(server!=null&&server.isSameThread())com.sirin.hk3gtl.common.easter.Hk3EggProductionData.get(server).produced(i.getTag().getUUID("hk3EggCellInstaller"),"receipt:248",1);
    }
}
