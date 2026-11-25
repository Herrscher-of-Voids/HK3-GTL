package com.sirin.hk3gtl.mixin.ae;

import appeng.api.config.Actionable;
import appeng.api.networking.security.IActionSource;
import appeng.api.stacks.AEKey;
import com.sirin.hk3gtl.common.integration.ae.nexus.network.Hk3NexusBulkInsert;
import it.unimi.dsi.fastutil.objects.Object2ObjectOpenHashMap;
import org.gtlcore.gtlcore.integration.ae2.storage.FastInfinityCellInventory;
import org.gtlcore.gtlcore.utils.datastructure.Int128;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.math.BigInteger;

@Mixin(value = FastInfinityCellInventory.class, remap = false)
public abstract class Hk3FastNexusBulkInsertMixin {
    @Unique private static final BigInteger hk3gtl$maxStock = Int128.MAX_VALUE.toBigInteger();
    @Shadow protected abstract Object2ObjectOpenHashMap<AEKey, Int128> getCellItems();
    @Shadow protected abstract void saveChanges(double delta);
    @Shadow private void updateDisplayAmount(AEKey key, Int128 amount) {}

    @Inject(method = "insert", at = @At(value = "INVOKE",
            target = "Lorg/gtlcore/gtlcore/integration/ae2/storage/FastInfinityCellInventory;getCellItems()Lit/unimi/dsi/fastutil/objects/Object2ObjectOpenHashMap;"),
            cancellable = true)
    private void hk3gtl$insertExact(AEKey key, long amount, Actionable mode, IActionSource source,
            CallbackInfoReturnable<Long> cir) {
        var items = getCellItems();
        var previous = items.get(key);
        if ((previous == null || previous.getHigh() != Long.MAX_VALUE) && !Hk3NexusBulkInsert.hasExtra(key, source)) return;
        var stored = previous == null ? BigInteger.ZERO : previous.toBigInteger();
        var capacity = hk3gtl$maxStock.subtract(stored);
        var nativeAmount = capacity.min(BigInteger.valueOf(amount));
        var inserted = Hk3NexusBulkInsert.expand(key, nativeAmount, source, capacity);
        if (inserted.signum() > 0) {
            var updated = Int128.fromBigInteger(stored.add(inserted));
            items.put(key, updated);
            updateDisplayAmount(key, updated);
            saveChanges(inserted.doubleValue());
        }
        cir.setReturnValue(nativeAmount.longValueExact());
    }
}
