package com.sirin.hk3gtl.client.ae;

import java.math.BigInteger;
import java.util.Optional;

public interface Hk3NexusNumberEntry {
    void hk3gtl$enableExact();
    Optional<BigInteger> hk3gtl$exactValue();
    void hk3gtl$setExactValue(BigInteger amount);
}
