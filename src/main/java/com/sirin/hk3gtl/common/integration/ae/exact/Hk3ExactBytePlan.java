package com.sirin.hk3gtl.common.integration.ae.exact;

import java.math.BigInteger;

/** 让组合计划保持精确字节需求，不能再次退回 long 投影。 */
public interface Hk3ExactBytePlan {
    BigInteger exactBytes();
}
