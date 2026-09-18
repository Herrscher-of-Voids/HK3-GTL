package com.sirin.hk3gtl.common.research;



import java.util.List;
import java.util.Objects;

/**
 * 研究节点数据定义（不可变 record）。
 *
 * <h3>职责</h3>
 * 定义单个研究节点的全部属性，包括前置条件、提交物和解锁效果。
 * 节点实例统一在 {@link Hk3ResearchNodes} 中注册，本类不包含注册逻辑。
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>新增字段 → 在 record 参数列表末尾追加，同步修改 {@link Hk3ResearchNodes#reg} 工厂方法</li>
 *   <li>修改节点类型枚举 → 见 {@link Hk3ResearchType}</li>
 *   <li>修改提交物结构 → 见 {@link Hk3ResearchRequirement}</li>
 *   <li>翻译键格式 → "hk3gtl.research.r_ab_xxx.name/effect/unlock"，需同步 zh_cn.json / en_us.json</li>
 * </ul>
 *
 * <h3>字段说明</h3>
 * @param id                  节点唯一编号，如 "R-AB-004"
 * @param type                节点类型（THEORY/MATERIAL/VOLTAGE/CIRCUIT/STRUCTURE/EVENT/CERTIFICATION）
 * @param tier                科技等级（15.0 = 海渊I 入口，16.5 = 海渊II 中期，18.5 = 海渊出口认证）
 * @param nameKey             名称翻译键
 * @param effectKey           效果描述翻译键（解锁了什么）
 * @param unlockDescriptionKey 详细解锁说明翻译键
 * @param prerequisites       前置研究节点 ID 列表（全部完成才可推进）
 * @param requiredEventId     前置事件 ID（如 "E-FB-007" = 研究矩阵已激活），null 表示无事件前置
 * @param autoCompleteEventId 自动完成触发事件 ID，非 null 时为自动完成型节点（无需手动提交）
 * @param requirements        手动提交型节点的提交物清单（自动完成型为空列表）
 * @param requiredCivLevel    所需文明交流等级（0~3，默认 0 = 不设门槛）
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

    /** 紧凑构造器：校验必填字段，防御性复制列表 */
    public Hk3ResearchNode {
        Objects.requireNonNull(id, "id");
        Objects.requireNonNull(type, "type");
        Objects.requireNonNull(nameKey, "nameKey");
        Objects.requireNonNull(effectKey, "effectKey");
        Objects.requireNonNull(unlockDescriptionKey, "unlockDescriptionKey");
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

    /** 是否为手动提交型节点（需要玩家提交指定物品） */
    public boolean isManualResearch() {
        return !isAutoComplete();
    }

    /** 是否需要前置事件（如研究矩阵激活）才能推进 */
    public boolean requiresEvent() {
        return requiredEventId != null && !requiredEventId.isBlank();
    }

    /** 获取研究类型的翻译键，用于 GUI 显示。翻译在 zh_cn.json 中维护 */
    public String typeDisplayKey() {
        return "hk3gtl.research.type." + type.name().toLowerCase();
    }
}
