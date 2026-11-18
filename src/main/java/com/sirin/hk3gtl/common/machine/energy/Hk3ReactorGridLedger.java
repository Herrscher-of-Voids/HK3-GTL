package com.sirin.hk3gtl.common.machine.energy;

import java.math.BigInteger;
import java.util.UUID;

/** 反应堆累计产电与原生无线EU余额共用一份存档。 */
public interface Hk3ReactorGridLedger {
    BigInteger hk3gtl$creditReactor(UUID stream, UUID account, BigInteger cumulative);
}
