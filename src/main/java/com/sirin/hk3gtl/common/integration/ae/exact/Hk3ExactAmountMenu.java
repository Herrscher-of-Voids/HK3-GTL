package com.sirin.hk3gtl.common.integration.ae.exact;

/** 大数页只发送动作，目标、权限和订单身份由服务端复核。 */
public interface Hk3ExactAmountMenu {
    void hk3gtl$exactAction(String action);
}
