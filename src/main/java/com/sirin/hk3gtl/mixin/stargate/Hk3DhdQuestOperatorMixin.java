package com.sirin.hk3gtl.mixin.stargate;

import com.sirin.hk3gtl.common.compat.stargate.Hk3StargateQuestEvents;
import java.util.function.Supplier;
import net.minecraftforge.network.NetworkEvent;
import net.povstalec.sgjourney.common.block_entities.dhd.AbstractDHDEntity;
import net.povstalec.sgjourney.common.packets.ServerboundDHDUpdatePacket;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

@Mixin(value = ServerboundDHDUpdatePacket.class, remap = false)
public abstract class Hk3DhdQuestOperatorMixin {
    @Redirect(method = "lambda$handle$0", at = @At(value = "INVOKE",
            target = "Lnet/povstalec/sgjourney/common/block_entities/dhd/AbstractDHDEntity;engageChevron(I)V"))
    private void hk3gtl$pressed(AbstractDHDEntity dhd, int symbol, Supplier<NetworkEvent.Context> context) {
        Hk3StargateQuestEvents.press(context.get().getSender(), dhd, symbol);
    }
}
