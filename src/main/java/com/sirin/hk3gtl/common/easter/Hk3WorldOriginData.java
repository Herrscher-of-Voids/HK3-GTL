package com.sirin.hk3gtl.common.easter;

/**
 * 【文件职责】仅在原生世界数据实例暴露只读创建记录；不提供客户端修改入口。
 * 【变更记录 #1】2026-11-05 19:08:32（修订210）：删除无；新增读取接口；修改无；用途：隔离世界生日与高度合同。
 */
public interface Hk3WorldOriginData {
    Hk3WorldOrigin hk3gtl$getWorldOrigin();
}
