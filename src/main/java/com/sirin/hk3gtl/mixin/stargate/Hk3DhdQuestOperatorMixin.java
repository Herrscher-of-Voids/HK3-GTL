package com.sirin.hk3gtl.mixin.stargate;

import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import com.sirin.hk3gtl.common.compat.stargate.Hk3StargateQuestEvents;
import java.util.function.Supplier;
import net.minecraftforge.network.NetworkEvent;
import net.povstalec.sgjourney.common.block_entities.dhd.AbstractDHDEntity;
import net.povstalec.sgjourney.common.packets.ServerboundDHDUpdatePacket;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;

@Mixin(value = ServerboundDHDUpdatePacket.class, remap = false)
public abstract class Hk3DhdQuestOperatorMixin {
    @WrapOperation(method = "lambda$handle$0", at = {
            @At(value = "INVOKE", target = "Lnet/povstalec/sgjourney/common/block_entities/dhd/AbstractDHDEntity;engageChevron(I)V"),
            @At(value = "INVOKE", target = "Lnet/povstalec/sgjourney/common/block_entities/dhd/AbstractDHDEntity;pressButton(I)V")
    })
    private void hk3gtl$pressed(AbstractDHDEntity dhd, int symbol, Operation<Void> original,
                                Supplier<NetworkEvent.Context> context) {
        Hk3StargateQuestEvents.press(context.get().getSender(), dhd, () -> original.call(dhd, symbol));
    }
}
