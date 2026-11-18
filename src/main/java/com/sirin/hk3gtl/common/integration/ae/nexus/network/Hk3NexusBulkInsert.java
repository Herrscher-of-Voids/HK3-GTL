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

    public static BigInteger insert(MEStorage inventory, AEKey key, BigInteger amount, IActionSource source) {
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
        Transfer transfer = CURRENT.get();
        if (transfer == null || transfer.source != source || !transfer.key.equals(key)) return amount;
        BigInteger expanded = amount.add(transfer.extra);
        transfer.accepted = transfer.accepted.add(transfer.extra);
        transfer.extra = BigInteger.ZERO;
        return expanded;
    }
}
