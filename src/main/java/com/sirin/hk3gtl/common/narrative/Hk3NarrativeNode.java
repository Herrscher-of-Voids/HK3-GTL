package com.sirin.hk3gtl.common.narrative;



import java.util.List;
import java.util.Objects;

import javax.annotation.Nullable;

/**
 * 世界文本叙事系统的单个节点（record）。
 *
 * <h3>定位</h3>
 * 一个节点 = 一段"剧情 / 通讯 / 档案摘录"。它被某个事件 ID 解锁后写入玩家的
 * {@link Hk3NarrativeLog}，玩家通过《文明档案卷轴》GUI 查看。
 *
 * <h3>内容组织</h3>
 * <ul>
 *   <li>{@link #bodyKeys} 是**按段落**拆开的翻译键列表 —— 一段一个 key，方便换行 / 着色
 *       独立维护，也便于未来做"逐段打字机"式阅读界面</li>
 *   <li>{@link #author} 可选，显示为档案条目的署名（如"空之律者·西琳"/"瓦尔特"）</li>
 *   <li>{@link #unlockEventId} 关键字段：研究 / 事件触发器会查询它来判断"解锁哪条"</li>
 * </ul>
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>新增节点 → 在 {@link Hk3NarrativeNodes} 中用 {@link Hk3NarrativeNodes#reg} 注册</li>
 *   <li>语言键格式：{@code hk3gtl.narrative.<id>.title / .body.1 / .body.2 / ...}</li>
 *   <li>一个 eventId 只能关联一个节点，多对多关系请拆成多个节点</li>
 *   <li>id 一旦确定不要改，持久化在玩家 NBT 里</li>
 * </ul>
 *
 * @param id            节点唯一 ID（如 "HQ-001" 对应 E-HQ-001）
 * @param faction       分类阵营
 * @param order         同一阵营内的显示排序（升序），建议用事件编号数字
 * @param titleKey      GUI 显示的标题翻译键
 * @param authorKey     署名翻译键；无则传 null
 * @param bodyKeys      正文段落翻译键列表（至少 1 段）
 * @param conditionKey  触发条件翻译键；无则传 null
 * @param unlockEventId 该节点由哪个事件触发解锁（对齐 Hk3EventManagerImpl 的 eventId 前缀 E-XX-XXX）
 */
public record Hk3NarrativeNode(
        String id,
        Hk3NarrativeFaction faction,
        int order,
        String titleKey,
        @Nullable String authorKey,
        List<String> bodyKeys,
        @Nullable String conditionKey,
        String unlockEventId) {

    /** 紧凑构造器：做必填校验与防御性复制，避免外部篡改 */
    public Hk3NarrativeNode {
        Objects.requireNonNull(id, "id");
        Objects.requireNonNull(faction, "faction");
        Objects.requireNonNull(titleKey, "titleKey");
        Objects.requireNonNull(unlockEventId, "unlockEventId");
        if (bodyKeys == null || bodyKeys.isEmpty()) {
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
