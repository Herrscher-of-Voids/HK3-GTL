package com.sirin.hk3gtl.common.integration.ae.nexus.network;

import appeng.api.config.Actionable;
import appeng.api.networking.security.IActionSource;
import appeng.api.stacks.AEKey;
import appeng.api.storage.MEStorage;

import java.math.BigInteger;

public final class Hk3NexusBulkInsert {
    private static final BigInteger LONG_MAX = BigInteger.valueOf(Long.MAX_VALUE);
    private static final ThreadLocal<Transfer> CURRENT = new ThreadLocal<>();

    private static final class Transfer {
        final AEKey key;
        final IActionSource source;
        BigInteger extra;
        BigInteger accepted = BigInteger.ZERO;

        Transfer(AEKey key, IActionSource source, BigInteger extra) {
            this.key = key;
            this.source = source;
            this.extra = extra;
        }
    }

    private Hk3NexusBulkInsert() {}

    public static BigInteger insert(MEStorage inventory, AEKey key, BigInteger amount, IActionSource source,
            long deadline) {
        BigInteger remaining = amount;
        for (int batch = 0; batch < 16 && remaining.signum() > 0 && System.nanoTime() < deadline; batch++) {
            var accepted = insertOnce(inventory, key, remaining, source);
            if (accepted.equals(remaining)) return amount;
            remaining = remaining.subtract(accepted);
            if (accepted.compareTo(LONG_MAX) < 0) break;
        }
        return amount.subtract(remaining);
    }

    public static BigInteger insertOnce(MEStorage inventory, AEKey key, BigInteger amount, IActionSource source) {
        long offered = amount.min(LONG_MAX).longValueExact();
        if (amount.compareTo(LONG_MAX) <= 0)
            return BigInteger.valueOf(inventory.insert(key, offered, Actionable.MODULATE, source));
        Transfer previous = CURRENT.get();
        Transfer transfer = new Transfer(key, source, amount.subtract(LONG_MAX));
        CURRENT.set(transfer);
        try {
            long accepted = inventory.insert(key, offered, Actionable.MODULATE, source);
            return BigInteger.valueOf(accepted).add(transfer.accepted);
        } finally {
            if (previous == null) CURRENT.remove();
            else CURRENT.set(previous);
        }
    }

    public static BigInteger expand(AEKey key, BigInteger amount, IActionSource source) {
        var transfer = matchingTransfer(key, source);
        return transfer == null ? amount : addExtra(transfer, amount, transfer.extra);
    }

    public static boolean hasExtra(AEKey key, IActionSource source) {
        var transfer = matchingTransfer(key, source);
        return transfer != null && transfer.extra.signum() > 0;
    }

    public static BigInteger expand(AEKey key, BigInteger amount, IActionSource source, BigInteger capacity) {
        var transfer = matchingTransfer(key, source);
        return transfer == null ? amount : addExtra(transfer, amount, transfer.extra.min(capacity.subtract(amount)));
    }

    private static Transfer matchingTransfer(AEKey key, IActionSource source) {
        var transfer = CURRENT.get();
        return transfer != null && transfer.source == source && transfer.key.equals(key) ? transfer : null;
    }

    private static BigInteger addExtra(Transfer transfer, BigInteger amount, BigInteger extra) {
        transfer.extra = transfer.extra.subtract(extra);
        transfer.accepted = transfer.accepted.add(extra);
        return amount.add(extra);
    }
}
