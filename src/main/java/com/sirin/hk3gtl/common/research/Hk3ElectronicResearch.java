package com.sirin.hk3gtl.common.research;

import java.util.List;

/** 【变更记录 #1】2026-10-01 20:58:37（修订149）：删除无；新增四平台电子部件与电路共同的新版知识门槛；修改不重定向其他旧设备研究；用途：消除旧电路节点锁定，种子路线不要求自身产物与后级研究。 */
public final class Hk3ElectronicResearch {
    private Hk3ElectronicResearch() {}
    public static List<String> requirements(int platform) {
        return switch(platform) {
            case 0 -> List.of("RN-BCE");
            case 1 -> List.of("RN-MCE");
            case 2 -> List.of("RN-CQS", "RN-WCP");
            case 3 -> List.of("RN-CQS", "RN-IAA");
            default -> throw new IllegalArgumentException("未知电子平台："+platform);
        };
    }
}
