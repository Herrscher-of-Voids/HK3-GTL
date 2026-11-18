package com.sirin.hk3gtl.mixin.gtmthings;

import com.hepdd.gtmthings.api.misc.GlobalVariableStorage;
import com.hepdd.gtmthings.data.WirelessEnergySavaedData;
import com.sirin.hk3gtl.common.machine.energy.Hk3ReactorGridLedger;
import com.sirin.hk3gtl.common.util.Hk3LedgerValidation;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.level.ServerLevel;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.math.BigInteger;
import java.util.UUID;

@Mixin(value = WirelessEnergySavaedData.class, remap = false)
public abstract class Hk3ReactorGridLedgerMixin implements Hk3ReactorGridLedger {
    @Unique private CompoundTag hk3gtl$reactorOutputs = new CompoundTag();

    @Inject(method = "<init>(Lnet/minecraft/server/level/ServerLevel;Lnet/minecraft/nbt/CompoundTag;)V", at = @At("RETURN"))
    private void hk3gtl$loadReactorOutputs(ServerLevel level, CompoundTag tag, CallbackInfo ci) {
        Hk3LedgerValidation.optionalType(tag, "hk3gtlReactorOutputs", Tag.TAG_COMPOUND);
        hk3gtl$reactorOutputs = tag.getCompound("hk3gtlReactorOutputs").copy();
        for (String stream : hk3gtl$reactorOutputs.getAllKeys()) {
            Hk3LedgerValidation.uuid(stream);
            Hk3LedgerValidation.type(hk3gtl$reactorOutputs, stream, Tag.TAG_COMPOUND);
            var totals = hk3gtl$reactorOutputs.getCompound(stream);
            for (String account : totals.getAllKeys()) {
                Hk3LedgerValidation.uuid(account);
                Hk3LedgerValidation.type(totals, account, Tag.TAG_STRING);
                Hk3LedgerValidation.require(totals.getString(account).matches("[0-9]+"), "反应堆累计产电");
            }
        }
    }

    @Inject(method = {"save", "m_7176_"}, at = @At("RETURN"))
    private void hk3gtl$saveReactorOutputs(CompoundTag tag, CallbackInfoReturnable<CompoundTag> cir) {
        cir.getReturnValue().put("hk3gtlReactorOutputs", hk3gtl$reactorOutputs.copy());
    }

    @Override
    public BigInteger hk3gtl$creditReactor(UUID stream, UUID account, BigInteger cumulative) {
        var totals = hk3gtl$reactorOutputs.getCompound(stream.toString());
        String key = account.toString();
        BigInteger credited = totals.contains(key) ? new BigInteger(totals.getString(key)) : BigInteger.ZERO;
        BigInteger delta = cumulative.subtract(credited);
        if (delta.signum() <= 0) return BigInteger.ZERO;
        var accounts = GlobalVariableStorage.GlobalEnergy;
        accounts.put(account, accounts.getOrDefault(account, BigInteger.ZERO).add(delta));
        totals.putString(key, cumulative.toString());
        hk3gtl$reactorOutputs.put(stream.toString(), totals);
        ((WirelessEnergySavaedData) (Object) this).setDirty();
        return delta;
    }
}
