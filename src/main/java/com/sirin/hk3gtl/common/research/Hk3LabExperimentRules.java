package com.sirin.hk3gtl.common.research;



/**
 * 【文件职责／本轮边界】只定义获批ALE及ERM两阶段固定实验，不把缺完整生产账本的OPR作为已接通实验。
 * 【变更记录 #1】2026-09-29 21:06:40（第 1 次编号备注 · 内测5修订100）
 * 删除：取消已被批准规则替代的研究个人独占、旧数值或在线限定分支；历史备注与其他系统保留。
 * 新增／修改：只定义获批ALE及ERM两阶段固定实验，不把缺完整生产账本的OPR作为已接通实验。
 * 用途：接通实际证据→付款→研究完成与权限检查；不授予缺真实证据的课题。
 * 边界：编译和账本测试不代表游戏验收；S02至S05正式结构及未接线课题仍未完成。
 * 追溯：logs/research-mainline-r100；R100_FINAL_RECORD。
 */

/** 修订100 · 2026-09-29：批准的研究所固定实验；与正式研究共用队列和槽位。 */
/**
 * 【变更记录 #2】2026-09-29 23:37:35（内测5修订101）
 * 删除：本轮被替代的单前置或旧提示分支；其余历史保留。
 * 新增／修改：加入S01的OPR固定实验，保持ALE和ERM规则。
 * 用途：补足研究接线并如实保留未接物理执行器及结构审批边界。
 * 追溯：logs/research-mainline-r101；R101_FINAL_RECORD。
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
