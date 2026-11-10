package com.sirin.hk3gtl.mixin.ae;
import appeng.menu.slot.CraftingTermSlot;
import appeng.api.storage.MEStorage;
import appeng.api.stacks.KeyCounter;
import net.minecraft.world.entity.player.Player;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
@Mixin(value=CraftingTermSlot.class,remap=false)
/** 【变更记录 #1】2026-10-01 05:24:14（修订128）：删除无；新增真实配方扣料完成返回非空结果后核验原生合成终端；修改无；用途：原条件的只读观察，不改物品与权限。 */
public abstract class Hk3EggCraftingMixin {
    @Inject(method="craftItem",at=@At("RETURN"))
    private void hk3gtl$crafted(Player player,MEStorage storage,KeyCounter keys,CallbackInfoReturnable<ItemStack> cir){
        if(player instanceof ServerPlayer p&&!cir.getReturnValue().isEmpty())com.sirin.hk3gtl.common.easter.Hk3EggAeMenus.crafted(p);
    }
}
