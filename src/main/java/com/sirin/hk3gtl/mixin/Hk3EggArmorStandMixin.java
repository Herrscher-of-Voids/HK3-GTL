package com.sirin.hk3gtl.mixin;
import net.minecraft.world.entity.decoration.ArmorStand;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.InteractionHand;
import net.minecraft.server.level.ServerPlayer;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
@Mixin(ArmorStand.class)
/** 【变更记录 #1】2026-10-01 06:19:47（修订128）：删除无；新增真实操作及连续状态旁注；修改无；用途：只读已加载世界与本人回执，不改游戏结果、不授研究资格。 */
/** 【变更记录 #2】2026-10-01 06:35:47（修订128）：删除：无；新增/修改：盔甲架每一部位成功装卸均回执，拆除同步清除旧归属；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #3】2026-10-01 16:30:04（修订134）：删除设备替换后残留的旧操作者归属；新增setItemSlot尾部清除；修改成功swapItem再写本人记录并回查笔记；用途：支持两种顺序，同时防发射器或他人换装继承旧归属。 */
public abstract class Hk3EggArmorStandMixin {
    @Inject(method="setItemSlot",at=@At("TAIL"))private void hk3gtl$clearOwner(EquipmentSlot slot,ItemStack stack,org.spongepowered.asm.mixin.injection.callback.CallbackInfo ci){
        var stand=(ArmorStand)(Object)this;
        if(!stand.level().isClientSide&&slot.getType()==EquipmentSlot.Type.ARMOR)stand.getPersistentData().remove("hk3_egg_armorer_"+slot.getName());
    }
    @Inject(method="swapItem",at=@At("RETURN"))private void hk3gtl$equipped(Player player,EquipmentSlot slot,ItemStack item,InteractionHand hand,CallbackInfoReturnable<Boolean> ci){if(Boolean.TRUE.equals(ci.getReturnValue())&&player instanceof ServerPlayer p&&slot.getType()==EquipmentSlot.Type.ARMOR)com.sirin.hk3gtl.common.easter.Hk3EggPersonalScenes.armored(p,(ArmorStand)(Object)this,slot);}
}
