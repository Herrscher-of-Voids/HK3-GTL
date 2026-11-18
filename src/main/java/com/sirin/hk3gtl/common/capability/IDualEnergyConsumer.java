package com.sirin.hk3gtl.common.capability;

import org.jetbrains.annotations.Nullable;

import java.math.BigInteger;
import java.util.UUID;

 




















public interface IDualEnergyConsumer {

    /** 双能源结算归属的玩家 UUID；null = 未绑定（视为崩坏能不足，机器暂停） */
    @Nullable
    UUID getDualEnergyOwner();

    /**
     * 从绑定玩家的崩坏能无线网络扣除崩坏能。
     *
     * @param amount   请求量（崩坏能单位）
     * @param simulate true 仅模拟不落账
     * @return 实际（可）扣除量
     */
    default long extractHonkaiFromNetwork(long amount, boolean simulate) {
        UUID owner = getDualEnergyOwner();
        if (owner == null) return 0L;
        return HonkaiWirelessNetwork.extract(owner, amount, simulate);
    }

    /** 全额或零扣除，用于每 tick 双能源结算。 */
    default boolean tryExtractHonkaiFromNetwork(BigInteger amount) {
        UUID owner = getDualEnergyOwner();
        return owner != null && HonkaiWirelessNetwork.tryExtractExact(owner, amount);
    }

    /** 向绑定玩家的崩坏能无线网络注入崩坏能（发电/注入类机器用） */
    default long insertHonkaiToNetwork(long amount, boolean simulate) {
        UUID owner = getDualEnergyOwner();
        if (owner == null) return 0L;
        return HonkaiWirelessNetwork.insert(owner, amount, simulate);
    }
}
