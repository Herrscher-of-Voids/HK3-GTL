package com.sirin.hk3gtl.common.easter;

/**
 * 仅在原生世界数据实例暴露只读创建记录；不提供客户端修改入口。
 */
public interface Hk3WorldOriginData {
    Hk3WorldOrigin hk3gtl$getWorldOrigin();
}
