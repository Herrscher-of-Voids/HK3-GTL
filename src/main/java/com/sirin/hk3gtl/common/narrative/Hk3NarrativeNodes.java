package com.sirin.hk3gtl.common.narrative;



import javax.annotation.Nullable;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * 世界文本叙事系统首批叙事节点注册表（22 个节点，对齐设计文档 v0.2）。
 *
 * <h3>节点来源</h3>
 * <ul>
 *   <li>阶段里程碑 E-MS-001~004 → 5 个节点（玩家的"我做到了"视角）</li>
 *   <li>空之律者 E-HQ-001~005 → 5 个节点（终局叙事主线）</li>
 *   <li>奥托/天命 E-OT-001~003 → 3 个</li>
 *   <li>瓦尔特 E-WL-001~002 → 2 个</li>
 *   <li>符华 E-FH-001 → 1 个</li>
 *   <li>爱莉希雅 E-EL-001~002 → 2 个</li>
 *   <li>世界蛇 E-WS-001 → 1 个</li>
 *   <li>逆熵 E-AE-001 → 1 个</li>
 *   <li>彩蛋 E-EG-001~002 → 2 个</li>
 * </ul>
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>新增节点 → 使用 {@link #reg} 工厂方法，同时在 lang 文件补 title/body/author 翻译键</li>
 *   <li>修改节点内容 → 只改语言文件即可，本类的结构不应变动</li>
 *   <li>绝对不要修改节点 id —— 已写入玩家存档，改 id 等于让所有玩家档案清零</li>
 *   <li>eventId 映射变化 → 同步检查 Hk3EventManagerImpl，确认该 eventId 仍在被触发</li>
 * </ul>
 *
 * <h3>变更记录（2026-05-19）</h3>
 * <ul>
 *   <li>删除：彩蛋叙事仅覆盖 E-EG-001~030 的上限</li>
 *   <li>新增：E-EG-001~100 全量叙事节点注册，并为彩蛋节点挂 conditionKey</li>
 *   <li>修改：regEvent 支持自动派生 hk3gtl.event.egxxx.condition</li>
 *   <li>用途：让文明档案卷轴可完整展示 100 彩蛋条目与触发条件</li>
 * </ul>
 */
public final class Hk3NarrativeNodes {

    /** 节点顺序表；LinkedHashMap 保证 GUI 显示顺序稳定 */
    private static final Map<String, Hk3NarrativeNode> NODES = new LinkedHashMap<>();
    /** 事件 ID → 节点列表索引，允许同事件解锁多个条目（旧摘要 + 新事件档案并存） */
    private static final Map<String, List<Hk3NarrativeNode>> BY_EVENT = new LinkedHashMap<>();

    private Hk3NarrativeNodes() {}

    // ═══════════════════════════════════════════════════
    //  阶段里程碑（MS）—— 玩家自己的成就故事
    // ═══════════════════════════════════════════════════
    public static final Hk3NarrativeNode MS_001 = reg("MS-001", Hk3NarrativeFaction.MILESTONE, 1,
            null, 3, "E-MS-001");
    public static final Hk3NarrativeNode MS_002 = reg("MS-002", Hk3NarrativeFaction.MILESTONE, 2,
            null, 3, "E-MS-002");
    public static final Hk3NarrativeNode MS_003 = reg("MS-003", Hk3NarrativeFaction.MILESTONE, 3,
            null, 3, "E-MS-003");
    public static final Hk3NarrativeNode MS_004 = reg("MS-004", Hk3NarrativeFaction.MILESTONE, 4,
            null, 3, "E-MS-004");
    public static final Hk3NarrativeNode MS_005 = reg("MS-005", Hk3NarrativeFaction.MILESTONE, 5,
            null, 3, "E-MS-005");

    // ═══════════════════════════════════════════════════
    //  空之律者·西琳（HQ）—— 终局叙事主线
    //  HQ-001~004 是前期伏笔，HQ-005 是终局对话（游戏里已有 d01~d52 完整版）
    // ═══════════════════════════════════════════════════
    public static final Hk3NarrativeNode HQ_001 = reg("HQ-001", Hk3NarrativeFaction.HONKAI_QUEEN, 1,
            "hk3gtl.narrative.author.sirin", 4, "E-HQ-001");
    public static final Hk3NarrativeNode HQ_002 = reg("HQ-002", Hk3NarrativeFaction.HONKAI_QUEEN, 2,
            "hk3gtl.narrative.author.sirin", 5, "E-HQ-002");
    public static final Hk3NarrativeNode HQ_003 = reg("HQ-003", Hk3NarrativeFaction.HONKAI_QUEEN, 3,
            "hk3gtl.narrative.author.sirin", 5, "E-HQ-003");
    public static final Hk3NarrativeNode HQ_004 = reg("HQ-004", Hk3NarrativeFaction.HONKAI_QUEEN, 4,
            "hk3gtl.narrative.author.sirin", 2, "E-HQ-004");
    // HQ-005 节点摘要；完整 52 句由 Hk3DialogueScreen 播放 hk3gtl.dialogue.sirin.dXX
    public static final Hk3NarrativeNode HQ_005 = reg("HQ-005", Hk3NarrativeFaction.HONKAI_QUEEN, 5,
            "hk3gtl.narrative.author.sirin", 3, "E-HQ-005");

    // ═══════════════════════════════════════════════════
    //  奥托/天命（OT）—— 中期推动者
    // ═══════════════════════════════════════════════════
    public static final Hk3NarrativeNode OT_001 = reg("OT-001", Hk3NarrativeFaction.OTTO_SCHICKSAL, 1,
            "hk3gtl.narrative.author.otto", 3, "E-OT-001");
    public static final Hk3NarrativeNode OT_002 = reg("OT-002", Hk3NarrativeFaction.OTTO_SCHICKSAL, 2,
            "hk3gtl.narrative.author.otto", 3, "E-OT-002");
    public static final Hk3NarrativeNode OT_003 = reg("OT-003", Hk3NarrativeFaction.OTTO_SCHICKSAL, 3,
            "hk3gtl.narrative.author.otto", 3, "E-OT-003");

    // ═══════════════════════════════════════════════════
    //  瓦尔特/理之律者（WL）—— 科学理性之声
    // ═══════════════════════════════════════════════════
    public static final Hk3NarrativeNode WL_001 = reg("WL-001", Hk3NarrativeFaction.WALTER_REASON, 1,
            "hk3gtl.narrative.author.walter", 3, "E-WL-001");
    public static final Hk3NarrativeNode WL_002 = reg("WL-002", Hk3NarrativeFaction.WALTER_REASON, 2,
            "hk3gtl.narrative.author.walter", 3, "E-WL-002");

    // ═══════════════════════════════════════════════════
    //  符华（FH）—— 古老智慧
    // ═══════════════════════════════════════════════════
    public static final Hk3NarrativeNode FH_001 = reg("FH-001", Hk3NarrativeFaction.FU_HUA, 1,
            "hk3gtl.narrative.author.fuhua", 3, "E-FH-001");

    // ═══════════════════════════════════════════════════
    //  爱莉希雅（EL）—— 人性温暖
    // ═══════════════════════════════════════════════════
    public static final Hk3NarrativeNode EL_001 = reg("EL-001", Hk3NarrativeFaction.ELYSIA, 1,
            "hk3gtl.narrative.author.elysia", 3, "E-EL-001");
    public static final Hk3NarrativeNode EL_002 = reg("EL-002", Hk3NarrativeFaction.ELYSIA, 2,
            "hk3gtl.narrative.author.elysia", 3, "E-EL-002");

    // ═══════════════════════════════════════════════════
    //  世界蛇（WS）—— 高风险交易商
    // ═══════════════════════════════════════════════════
    public static final Hk3NarrativeNode WS_001 = reg("WS-001", Hk3NarrativeFaction.WORLD_SERPENT, 1,
            "hk3gtl.narrative.author.serpent", 3, "E-WS-001");

    // ═══════════════════════════════════════════════════
    //  逆熵（AE）—— 工程师同路人
    // ═══════════════════════════════════════════════════
    public static final Hk3NarrativeNode AE_001 = reg("AE-001", Hk3NarrativeFaction.ANTI_ENTROPY, 1,
            "hk3gtl.narrative.author.anti_entropy", 3, "E-AE-001");

    // ═══════════════════════════════════════════════════
    //  彩蛋（EG）—— 考据党专属 + 非酋向
    // ═══════════════════════════════════════════════════
    public static final Hk3NarrativeNode EG_001 = reg("EG-001", Hk3NarrativeFaction.EASTER_EGG, 1,
            null, 2, "E-EG-001");
    public static final Hk3NarrativeNode EG_002 = reg("EG-002", Hk3NarrativeFaction.EASTER_EGG, 2,
            null, 2, "E-EG-002");
    /**
     * EG-003 / 非酋日志：累计研究失败 10 次解锁。
     * 由 {@code E-EGG-001}（{@link com.sirin.hk3gtl.common.event.Hk3EventService#tryTriggerFirstTime}）触发。
     */
    public static final Hk3NarrativeNode EG_003 = reg("EG-003", Hk3NarrativeFaction.EASTER_EGG, 3,
            null, 3, "E-EGG-001");
    /** 动态事件节点注册标记：保留旧 23 节点，并扩展 65 阵营事件 + 30 彩蛋事件。 */
    @SuppressWarnings("unused")
    private static final boolean EVENT_NODES_REGISTERED = registerEventNarratives();

    // ═══════════════════════════════════════════════════
    //  查询 API
    // ═══════════════════════════════════════════════════

    /** 按 ID 查询；不存在返回 null */
    @Nullable
    public static Hk3NarrativeNode byId(String id) {
        return NODES.get(id);
    }

    /** 按事件 ID 查询绑定节点；不存在返回 null */
    @Nullable
    public static Hk3NarrativeNode byEventId(String eventId) {
        List<Hk3NarrativeNode> nodes = BY_EVENT.get(eventId);
        return (nodes == null || nodes.isEmpty()) ? null : nodes.get(0);
    }

    /** 按事件 ID 查询全部绑定节点；用于同一事件解锁多条档案。 */
    public static List<Hk3NarrativeNode> byEventIdAll(String eventId) {
        List<Hk3NarrativeNode> nodes = BY_EVENT.get(eventId);
        return nodes == null ? List.of() : Collections.unmodifiableList(nodes);
    }

    /** 返回全部节点（按注册顺序） */
    public static Collection<Hk3NarrativeNode> all() {
        return Collections.unmodifiableCollection(NODES.values());
    }

    /** 返回指定阵营的全部节点（按 order 升序） */
    public static List<Hk3NarrativeNode> byFaction(Hk3NarrativeFaction faction) {
        return NODES.values().stream()
                .filter(n -> n.faction() == faction)
                .sorted(java.util.Comparator.comparingInt(Hk3NarrativeNode::order))
                .collect(Collectors.toList());
    }

    /** 节点总数（含未解锁） */
    public static int totalCount() {
        return NODES.size();
    }

    // ═══════════════════════════════════════════════════
    //  内部辅助
    // ═══════════════════════════════════════════════════

    /**
     * 节点注册工厂：自动按约定生成 titleKey / bodyKeys / authorKey 的翻译键位置。
     * <p>翻译键约定：</p>
     * <ul>
     *   <li>标题 {@code hk3gtl.narrative.<id>.title}</li>
     *   <li>正文段 {@code hk3gtl.narrative.<id>.body.1 ~ .body.N}</li>
     *   <li>署名由 authorKey 参数显式传入（允许多个节点共享同一署名）</li>
     * </ul>
     *
     * @param id 节点 ID（如 "HQ-001"），持久化 key 片段
     * @param faction 所属阵营分类
     * @param order 同阵营内显示排序
     * @param authorKey 署名翻译键；没有作者传 null
     * @param paragraphs 段落数（自动生成 body.1 ~ body.N 翻译键列表）
     * @param unlockEventId 该节点由哪个事件 ID 解锁
     */
    private static Hk3NarrativeNode reg(String id, Hk3NarrativeFaction faction, int order,
                                        @Nullable String authorKey, int paragraphs,
                                        String unlockEventId) {
        String keyBase = "hk3gtl.narrative." + id.toLowerCase().replace('-', '_');
        String titleKey = keyBase + ".title";
        java.util.ArrayList<String> bodies = new java.util.ArrayList<>(paragraphs);
        for (int i = 1; i <= paragraphs; i++) {
            bodies.add(keyBase + ".body." + i);
        }
        Hk3NarrativeNode node = new Hk3NarrativeNode(id, faction, order, titleKey, authorKey, bodies, null, unlockEventId);
        NODES.put(id, node);
        BY_EVENT.computeIfAbsent(unlockEventId, k -> new ArrayList<>()).add(node);
        return node;
    }

    /**
     * 事件直连节点：正文直接引用现有事件翻译键，减少重复文案维护。
     * 标题键为 {@code hk3gtl.narrative.e_xx_yyy.title}，由 lang 文件统一补齐。
     */
    private static Hk3NarrativeNode regEvent(String eventId, Hk3NarrativeFaction faction) {
        String normalized = eventId.toLowerCase().replace('-', '_');
        String titleKey = "hk3gtl.narrative." + normalized + ".title";
        String shortCode = eventId.substring(2).toLowerCase().replace("-", "");
        String bodyKey = "hk3gtl.event." + shortCode;
        String conditionKey = eventId.startsWith("E-EG-") ? bodyKey + ".condition" : null;
        int order = parseOrder(eventId);
        Hk3NarrativeNode node = new Hk3NarrativeNode(eventId, faction, order, titleKey, null, List.of(bodyKey), conditionKey, eventId);
        NODES.put(eventId, node);
        BY_EVENT.computeIfAbsent(eventId, k -> new ArrayList<>()).add(node);
        return node;
    }

    private static int parseOrder(String eventId) {
        int dash = eventId.lastIndexOf('-');
        if (dash < 0 || dash + 1 >= eventId.length()) {
            return 0;
        }
        try {
            return Integer.parseInt(eventId.substring(dash + 1));
        } catch (NumberFormatException ignored) {
            return 0;
        }
    }

    private static void regEvents(Hk3NarrativeFaction faction, String... eventIds) {
        for (String eventId : eventIds) {
            regEvent(eventId, faction);
        }
    }

    private static boolean registerEventNarratives() {
        regEvents(Hk3NarrativeFaction.OTTO_SCHICKSAL, "E-OT-001", "E-OT-002", "E-OT-003", "E-OT-004", "E-OT-005");
        regEvents(Hk3NarrativeFaction.HONKAI_QUEEN, "E-HQ-001", "E-HQ-002", "E-HQ-003", "E-HQ-004", "E-HQ-005");
        regEvents(Hk3NarrativeFaction.WALTER_REASON, "E-WL-001", "E-WL-002", "E-WL-003", "E-WL-004");
        regEvents(Hk3NarrativeFaction.FU_HUA, "E-FH-001", "E-FH-002", "E-FH-003", "E-FH-004", "E-FH-005");
        regEvents(Hk3NarrativeFaction.ELYSIA, "E-EL-001", "E-EL-002", "E-EL-003");
        regEvents(Hk3NarrativeFaction.WORLD_SERPENT, "E-WS-001", "E-WS-002", "E-WS-003", "E-WS-004", "E-WS-005", "E-WS-006");
        regEvents(Hk3NarrativeFaction.ANTI_ENTROPY, "E-AE-001", "E-AE-002", "E-AE-003", "E-AE-004", "E-AE-005");
        regEvents(Hk3NarrativeFaction.SF, "E-SF-001", "E-SF-002", "E-SF-003", "E-SF-004");
        regEvents(Hk3NarrativeFaction.FM, "E-FM-001", "E-FM-002", "E-FM-003", "E-FM-004", "E-FM-005");
        regEvents(Hk3NarrativeFaction.BRONYA, "E-BR-001", "E-BR-002", "E-BR-003", "E-BR-004");
        regEvents(Hk3NarrativeFaction.SA, "E-SA-001", "E-SA-002", "E-SA-003", "E-SA-004");
        regEvents(Hk3NarrativeFaction.MOBIUS, "E-MB-001", "E-MB-002", "E-MB-003", "E-MB-004");
        regEvents(Hk3NarrativeFaction.KIANA, "E-KI-001", "E-KI-002", "E-KI-003", "E-KI-004");
        regEvents(Hk3NarrativeFaction.LUNAR_BASE, "E-LB-001", "E-LB-002", "E-LB-003", "E-LB-004");
        regEvents(Hk3NarrativeFaction.TESLA, "E-TS-001", "E-TS-002", "E-TS-003");
        for (int i = 1; i <= 100; i++) {
            regEvent(String.format("E-EG-%03d", i), Hk3NarrativeFaction.EASTER_EGG);
        }
        return true;
    }
}
