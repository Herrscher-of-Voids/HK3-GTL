package com.sirin.hk3gtl.common.narrative;



/**
 * 世界文本叙事系统的阵营分类（对齐设计文档 v0.2 的事件前缀规范）。
 *
 * <h3>职责</h3>
 * 用于在 GUI 里把 {@link Hk3NarrativeNode} 分章节组织，同时给玩家一个"阅读顺序线索"。
 *
 * <h3>前缀映射</h3>
 * 每个阵营对应一组 {@code E-XX-} 事件编号（如 HQ → E-HQ-xxx）。
 * 新增阵营请同时在此枚举、语言键（{@code hk3gtl.narrative.faction.xxx}）与
 * {@link Hk3NarrativeNodes} 注册位置添加对应条目。
 */
public enum Hk3NarrativeFaction {
    /** 阶段里程碑：E-MS-xxx，属于"玩家自己的成就故事"，没有特定阵营 */
    MILESTONE("milestone", "hk3gtl.narrative.faction.milestone"),
    /** 空之律者·西琳：E-HQ-xxx，全模组终局叙事主线 */
    HONKAI_QUEEN("honkai_queen", "hk3gtl.narrative.faction.honkai_queen"),
    /** 奥托/天命：E-OT-xxx，中期文明交流推动方 */
    OTTO_SCHICKSAL("otto_schicksal", "hk3gtl.narrative.faction.otto_schicksal"),
    /** 瓦尔特/理之律者：E-WL-xxx，科学理性的代言 */
    WALTER_REASON("walter_reason", "hk3gtl.narrative.faction.walter_reason"),
    /** 世界蛇：E-WS-xxx，高风险技术交易商 */
    WORLD_SERPENT("world_serpent", "hk3gtl.narrative.faction.world_serpent"),
    /** 逆熵：E-AE-xxx，工程理性同路人 */
    ANTI_ENTROPY("anti_entropy", "hk3gtl.narrative.faction.anti_entropy"),
    /** 符华：E-FH-xxx，古老智慧与历史视角 */
    FU_HUA("fu_hua", "hk3gtl.narrative.faction.fu_hua"),
    /** 爱莉希雅：E-EL-xxx，人性温暖与文明意义的反思 */
    ELYSIA("elysia", "hk3gtl.narrative.faction.elysia"),
    /** 琪亚娜：E-KI-xxx，终局门前的回应与注视 */
    KIANA("kiana", "hk3gtl.narrative.faction.kiana"),
    /** 布洛妮娅：E-BR-xxx，量子计算与数据支援 */
    BRONYA("bronya", "hk3gtl.narrative.faction.bronya"),
    /** 梅比乌斯：E-MB-xxx，危险知识与进化实验 */
    MOBIUS("mobius", "hk3gtl.narrative.faction.mobius"),
    /** 娑：E-SA-xxx，观测与审判相关事件 */
    SA("sa", "hk3gtl.narrative.faction.sa"),
    /** 特斯拉/爱因斯坦：E-TS-xxx，科学组工程反馈 */
    TESLA("tesla", "hk3gtl.narrative.faction.tesla"),
    /** 圣芙蕾雅：E-SF-xxx，学院支援与提醒 */
    SF("sf", "hk3gtl.narrative.faction.sf"),
    /** 逐火之蛾：E-FM-xxx，前文明记录与遗言 */
    FM("fm", "hk3gtl.narrative.faction.fm"),
    /** 月球基地：E-LB-xxx，权限校验与终局认证 */
    LUNAR_BASE("lunar_base", "hk3gtl.narrative.faction.lunar_base"),
    /** 彩蛋/隐藏：E-EG-xxx，为考据玩家准备的小料 */
    EASTER_EGG("easter_egg", "hk3gtl.narrative.faction.easter_egg");

    /** 持久化时使用的字符串 ID（放在 NBT 里的 key 片段） */
    public final String id;
    /** 翻译键，用于 GUI 分类标题显示 */
    public final String titleKey;

    Hk3NarrativeFaction(String id, String titleKey) {
        this.id = id;
        this.titleKey = titleKey;
    }
}
