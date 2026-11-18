package com.sirin.hk3gtl.common.integration.ae.exact;

import appeng.api.stacks.AEKey;

/** 收尾时优先核对程序保留的实物，而非把循环回流误认成品。 */
public interface Hk3ExactProgramHost {
    boolean hk3gtl$hasProgram();
    long hk3gtl$programProduced(boolean success, long original, AEKey target);
}
