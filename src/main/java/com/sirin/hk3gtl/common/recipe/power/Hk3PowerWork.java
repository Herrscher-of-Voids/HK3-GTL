package com.sirin.hk3gtl.common.recipe.power;

/**
 * 标识标准GT工作循环已经接入HK工况能源事务；不授予自定义执行器隐式权限。
 */
public interface Hk3PowerWork {
    interface Suprachronal extends Hk3PowerWork {
        boolean hk3gtl$usesFixedSuprachronalPower();
    }
}
