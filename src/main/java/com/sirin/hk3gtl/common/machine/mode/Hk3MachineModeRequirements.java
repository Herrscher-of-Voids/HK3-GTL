package com.sirin.hk3gtl.common.machine.mode;



import java.util.List;

/**
 * 多方块模式需求表（对照 GTLCore 多模式体系的项目内落地清单）。
 *
 * <p>参考对象：
 * GTLCore 的 WorkableElectricMultipleRecipesMachine / MultipleRecipesLogic /
 * MachineModeConfigurator。</p>
 *
 * <p>当前结论：
 * HK3GTL 的 60 台机器在 v0.3 设计中仍采用“一机一配方类型”，
 * 现阶段没有硬性要求切换为运行时多模式；本表用于后续扩展附属模组时快速识别候选机型。</p>
 */
public final class Hk3MachineModeRequirements {

    private static final List<ModeCandidate> CANDIDATES = List.of(
            // 休伯利安相关 4 台目前按独立控制器实现；若后续要求“单控制器多工位切换”，可合并到 hyperion_flagship。
            new ModeCandidate("hyperion_flagship", false, "当前已有 shipboard 四机分治，无硬性多模式需求"),
            // 量子/终焉/奇观均为一机一 recipeType，研究门槛与事件绑定清晰，保持低耦合更稳妥。
            new ModeCandidate("quantum_entanglement_computer", false, "量子阶段流程已闭环，模式切换收益低于复杂度"),
            new ModeCandidate("civilization_validation_matrix", false, "终焉阶段按研究分段推进，不建议并机"),
            new ModeCandidate("grand_convergence_altar", false, "奇观阶段以叙事节点驱动，保持独立机器更可维护")
    );

    private Hk3MachineModeRequirements() {}

    public static List<ModeCandidate> all() {
        return CANDIDATES;
    }

    public static boolean requiresRuntimeMode(String machineId) {
        for (ModeCandidate candidate : CANDIDATES) {
            if (candidate.machineId().equals(machineId) && candidate.requiredNow()) {
                return true;
            }
        }
        return false;
    }

    public record ModeCandidate(String machineId, boolean requiredNow, String reason) {}
}
