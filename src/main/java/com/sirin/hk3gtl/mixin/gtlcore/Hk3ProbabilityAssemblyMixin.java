package com.sirin.hk3gtl.mixin.gtlcore;

import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ProbabilityAssemblyIdentity;
import net.minecraft.nbt.CompoundTag;
import org.gtlcore.gtlcore.common.machine.multiblock.part.ae.MEPatternBufferPartMachineBase;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

import java.util.UUID;

@Mixin(value = MEPatternBufferPartMachineBase.class, remap = false)
public abstract class Hk3ProbabilityAssemblyMixin implements Hk3ProbabilityAssemblyIdentity {
    @Unique private UUID hk3gtl$probabilityIdentity = UUID.randomUUID();

    @Override public UUID hk3gtl$probabilityIdentity() { return hk3gtl$probabilityIdentity; }

    @Inject(method = "saveCustomPersistedData", at = @At("RETURN"), remap = false)
    private void hk3gtl$saveIdentity(CompoundTag tag, boolean forDrop, CallbackInfo callback) {
        tag.putUUID("hk3ProbabilityAssemblyIdentity", hk3gtl$probabilityIdentity);
    }

    @Inject(method = "loadCustomPersistedData", at = @At("RETURN"), remap = false)
    private void hk3gtl$loadIdentity(CompoundTag tag, CallbackInfo callback) {
        if (tag.hasUUID("hk3ProbabilityAssemblyIdentity")) hk3gtl$probabilityIdentity = tag.getUUID("hk3ProbabilityAssemblyIdentity");
    }
}
