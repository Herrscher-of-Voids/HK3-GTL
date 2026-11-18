package com.sirin.hk3gtl.common.integration.ae.nexus.crafting;

import appeng.api.stacks.AEKey;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;

import java.math.BigInteger;
import java.util.LinkedHashMap;
import java.util.Map;

final class Hk3NexusLedger {
    static final BigInteger LONG_MAX = BigInteger.valueOf(Long.MAX_VALUE);

    private Hk3NexusLedger() {}

    static long project(BigInteger value) { return value.min(LONG_MAX).longValue(); }

    static void add(Map<AEKey, BigInteger> values, AEKey key, BigInteger amount) {
        if (values.merge(key, amount, BigInteger::add).signum() == 0) values.remove(key);
    }

    static ListTag write(Map<AEKey, BigInteger> values) {
        ListTag list = new ListTag();
        values.forEach((key, value) -> {
            CompoundTag row = key.toTagGeneric();
            row.putByteArray("hk3Amount", value.toByteArray());
            list.add(row);
        });
        return list;
    }

    static Map<AEKey, BigInteger> read(ListTag list) {
        Map<AEKey, BigInteger> values = new LinkedHashMap<>();
        for (Tag item : list) {
            CompoundTag row = (CompoundTag) item;
            values.put(AEKey.fromTagGeneric(row), new BigInteger(row.getByteArray("hk3Amount")));
        }
        return values;
    }
}
