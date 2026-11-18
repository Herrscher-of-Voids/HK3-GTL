package com.sirin.hk3gtl.common.research;



/**
 * 【文件职责／本轮边界】只定义获批ALE及ERM两阶段固定实验，不把缺完整生产账本的OPR作为已接通实验。
 */

public final class Hk3LabExperimentRules {
    private Hk3LabExperimentRules() {}
    public record Spec(String id, String research, int lab, long ticks, boolean baseline) {}
    public static Spec get(String id) {
        return switch (id) {
            case "LAB-ALE" -> new Spec(id,"RN-ALE",1,2400,false);
            case "LAB-OPR" -> new Spec(id,"RN-OPR",1,1800,false);
            case "LAB-ERM-BASE" -> new Spec(id,"RN-ERM",2,6000,true);
            case "LAB-ERM-AID" -> new Spec(id,"RN-ERM",2,6000,false);
            default -> null;
        };
    }
    public static String next(String research, boolean baseline) {
        return switch (research) {
            case "RN-ALE" -> "LAB-ALE";
            case "RN-OPR" -> "LAB-OPR";
            case "RN-ERM" -> baseline?"LAB-ERM-AID":"LAB-ERM-BASE";
            default -> "";
        };
    }
}
