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
public abstract class Hk3EggCraftingMixin {
    @Inject(method="craftItem",at=@At("RETURN"))
    private void hk3gtl$crafted(Player player,MEStorage storage,KeyCounter keys,CallbackInfoReturnable<ItemStack> cir){
        if(player instanceof ServerPlayer p&&!cir.getReturnValue().isEmpty())com.sirin.hk3gtl.common.easter.Hk3EggAeMenus.crafted(p);
    }
}
