package com.sirin.hk3gtl.common.research;

import java.util.List;

/**
 * 研究节点；事件ID可空，tier允许小数，requiredCivLevel限定0~3。
 * 空列表表示无前置或提交物。
 */
public record Hk3ResearchNode(
        String id,
        Hk3ResearchType type,
        double tier,
        String nameKey,
        String effectKey,
        String unlockDescriptionKey,
        List<String> prerequisites,
        String requiredEventId,
        String autoCompleteEventId,
        List<Hk3ResearchRequirement> requirements,
        int requiredCivLevel) {

    public Hk3ResearchNode {
        prerequisites = List.copyOf(prerequisites);
        requirements = List.copyOf(requirements);
        requiredCivLevel = Math.max(0, Math.min(3, requiredCivLevel));
    }

    public Hk3ResearchNode(
            String id,
            Hk3ResearchType type,
            double tier,
            String nameKey,
            String effectKey,
            String unlockDescriptionKey,
            List<String> prerequisites,
            String requiredEventId,
            String autoCompleteEventId,
            List<Hk3ResearchRequirement> requirements) {
        this(id, type, tier, nameKey, effectKey, unlockDescriptionKey, prerequisites, requiredEventId, autoCompleteEventId, requirements, 0);
    }

    /** 是否为自动完成型节点（事件触发后自动标记完成，无需手动提交物品） */
    public boolean isAutoComplete() {
        return autoCompleteEventId != null && !autoCompleteEventId.isBlank();
    }

    public boolean isManualResearch() {
        return !isAutoComplete();
    }

    /** 是否需要前置事件（如研究矩阵激活）才能推进 */
    public boolean requiresEvent() {
        return requiredEventId != null && !requiredEventId.isBlank();
    }

    public String typeDisplayKey() {
        return "hk3gtl.research.type." + type.name().toLowerCase();
    }
}
