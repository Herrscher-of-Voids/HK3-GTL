package com.sirin.hk3gtl.common.research;













/** 修订100 · 2026-09-29：批准的研究所固定实验；与正式研究共用队列和槽位。 */







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
