package com.sirin.hk3gtl.common.narrative;

import java.util.List;

import javax.annotation.Nullable;

/** 叙事节点；id用于存档，bodyKeys按段落排列。 */
public record Hk3NarrativeNode(
        String id,
        Hk3NarrativeFaction faction,
        int order,
        String titleKey,
        @Nullable String authorKey,
        List<String> bodyKeys,
        @Nullable String conditionKey,
        String unlockEventId) {

    public Hk3NarrativeNode {
        if (bodyKeys.isEmpty()) {
            throw new IllegalArgumentException("bodyKeys must have at least 1 paragraph for node " + id);
        }
        bodyKeys = List.copyOf(bodyKeys);
    }

    /** 是否带署名（用于 GUI 渲染时决定是否额外画一行作者名） */
    public boolean hasAuthor() {
        return authorKey != null && !authorKey.isBlank();
    }

    /** 是否带触发条件描述（用于卷轴详情页显示“触发条件”栏） */
    public boolean hasCondition() {
        return conditionKey != null && !conditionKey.isBlank();
    }
}
