package com.sirin.hk3gtl.mixin.gtlcore;

import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.gregtechceu.gtceu.api.machine.feature.IMachineModifyDrops;
import com.gregtechceu.gtceu.integration.ae2.machine.MEInputBusPartMachine;
import com.gregtechceu.gtceu.integration.ae2.machine.MEInputHatchPartMachine;
import com.sirin.hk3gtl.common.integration.ae.Hk3StockingCraftingCard;
import net.minecraft.world.item.ItemStack;
import org.gtlcore.gtlcore.common.machine.multiblock.part.MEDualHatchStockPartMachine;
import org.gtlcore.gtlcore.common.machine.multiblock.part.ae.MEStockingPatternBufferPartMachine;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

import java.util.List;

@Mixin(value = {MEInputBusPartMachine.class, MEInputHatchPartMachine.class,
        MEDualHatchStockPartMachine.class, MEStockingPatternBufferPartMachine.class}, remap = false)
public abstract class Hk3StockingCraftingCardMixin implements IMachineModifyDrops {
    @Unique private Hk3StockingCraftingCard hk3gtl$craftingCard;

    @Inject(method = "<init>", at = @At("RETURN"))
    private void hk3gtl$addCraftingCard(CallbackInfo ci) {
        hk3gtl$craftingCard = new Hk3StockingCraftingCard((MetaMachine) (Object) this);
    }

    @Override public void onDrops(List<ItemStack> drops) {
        hk3gtl$craftingCard.drops(drops);
    }
}
