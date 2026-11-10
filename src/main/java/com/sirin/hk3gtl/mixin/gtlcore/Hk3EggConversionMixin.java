package com.sirin.hk3gtl.mixin.gtlcore;
import org.gtlcore.gtlcore.common.machine.multiblock.electric.BlockConversionRoomMachine;
import com.lowdragmc.lowdraglib.misc.ItemStackTransfer;
import net.minecraft.world.item.ItemStack;
import net.minecraft.core.registries.BuiltInRegistries;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
@Mixin(value=BlockConversionRoomMachine.class,remap=false)
/** 【变更记录 #1】2026-10-01 13:31:18（修订128）：删除：无；新增/修改：模拟卡在方块转换室实际将输入方块转换为对应产物后授245；只插卡或无转换不计；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #2】2026-10-01 13:31:54（修订128）：删除：无；新增/修改：使用依赖源码中ItemStackTransfer实际所在misc包，修复编译和调用点签名；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public abstract class Hk3EggConversionMixin {
    @Redirect(method="onWorking",at=@At(value="INVOKE",target="Lcom/lowdragmc/lowdraglib/misc/ItemStackTransfer;setStackInSlot(ILnet/minecraft/world/item/ItemStack;)V"))
    private void hk3gtl$converted(ItemStackTransfer inventory,int slot,ItemStack result){
        ItemStack before=inventory.getStackInSlot(slot).copy();inventory.setStackInSlot(slot,result);var machine=(BlockConversionRoomMachine)(Object)this;
        if(!before.isEmpty()&&!result.isEmpty()&&!before.is(result.getItem())&&ItemStack.matches(inventory.getStackInSlot(slot),result)&&BuiltInRegistries.ITEM.getKey(machine.getMachineStorageItem().getItem()).toString().equals("gtlcore:conversion_simulate_card"))com.sirin.hk3gtl.common.easter.Hk3EggProduction.receipt(machine,245);
    }
}
