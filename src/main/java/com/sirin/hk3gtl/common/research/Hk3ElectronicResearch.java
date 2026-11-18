package com.sirin.hk3gtl.common.research;

import java.util.List;

 
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
