package com.sirin.hk3gtl.common.event;



import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
/**
 * 阵营事件检查器：处理 15 个阵营共 65 个事件的触发逻辑。
 *
 * <h3>触发方式分类</h3>
 * <ul>
 *   <li><b>里程碑依赖</b>：{@link #checkFactionEvents} 每秒轮询，检查相关里程碑是否已触发</li>
 *   <li><b>注视度阈值</b>：{@link #checkFactionEvents} 每秒轮询，读取 persistentData 中的注视度</li>
 *   <li><b>多方块建成</b>：{@link #onMultiblockFormedFaction} 由 Hk3EventManagerImpl 在成型时调用</li>
 *   <li><b>研究完成</b>：{@link #onResearchCompleted} 由 Hk3ResearchManager 在研究完成时调用</li>
 *   <li><b>外部触发</b>：{@link #triggerFactionEvent} 由其他系统（毕业、特殊条件）直接调用</li>
 * </ul>
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>新增阵营事件 → 按触发类型添加到对应方法中</li>
 *   <li>新增研究触发 → 在 {@link #onResearchCompleted} 的 switch 中添加 case</li>
 *   <li>新增多方块触发 → 在 {@link #onMultiblockFormedFaction} 的 switch 中添加 case</li>
 *   <li>所有 lang key 格式 → "hk3gtl.event.{prefix}{number}"，如 "hk3gtl.event.ot002"</li>
 * </ul>
 *
 * @see Hk3EventManagerImpl 里程碑与 FB 事件管理器
 */
public class Hk3FactionEventChecker {
    /** 注视度在 persistentData 中的存储键（注视度系统写入，本类只读） */
    private static final String GAZE_TAG = "hk3gtl_gaze_level";

    // ═══════════════════════════════════════════════════
    //  每秒轮询入口（由 Hk3EventManagerImpl.onPlayerTick 调用）
    // ═══════════════════════════════════════════════════

    /**
     * 检查里程碑依赖型和注视度阈值型阵营事件。
     * 轮询频率由 Hk3EventManagerImpl.onPlayerTick 控制（每20tick/1秒）。
     */
    public static void checkFactionEvents(ServerPlayer player) {
        CompoundTag data = player.getPersistentData();
        checkMilestoneDependentEvents(player, data);
        checkGazeThresholdEvents(player, data);
    }

    /**
     * 里程碑依赖型事件：当对应里程碑(E-MS-xxx)已触发时，自动触发阵营事件。
     * 用于"进入某阶段即触发对话"类型的事件。
     */
    private static void checkMilestoneDependentEvents(ServerPlayer player, CompoundTag data) {
        // ── 奥托/天命 ──
        // E-OT-004: 天命高级资料库访问 — 虚数阶段入口
        tryMilestoneTrigger(player, data, "E-OT-004", "E-MS-005", "hk3gtl.event.ot004");
        // E-OT-005: 天命终局观察 — 终焉阶段入口
        tryMilestoneTrigger(player, data, "E-OT-005", "E-MS-010", "hk3gtl.event.ot005");

        // ── 瓦尔特 ──
        // E-WL-004: 理之律者的沉默 — 终焉阶段入口
        tryMilestoneTrigger(player, data, "E-WL-004", "E-MS-010", "hk3gtl.event.wl004");

        // ── 世界蛇 ──
        // E-WS-001: 价值确认 — 崩坏能工业稳定运行（海渊突破后）
        tryMilestoneTrigger(player, data, "E-WS-001", "E-MS-003", "hk3gtl.event.ws001");

        // ── 逆熵 ──
        // E-AE-004: 逆熵终局支援 — 终焉阶段入口
        tryMilestoneTrigger(player, data, "E-AE-004", "E-MS-010", "hk3gtl.event.ae004");

        // ── 圣芙蕾雅 ──
        // E-SF-003: 后勤支援 — 虚数阶段入口
        tryMilestoneTrigger(player, data, "E-SF-003", "E-MS-005", "hk3gtl.event.sf003");
        // E-SF-004: 学院的祝福 — 终焉阶段入口
        tryMilestoneTrigger(player, data, "E-SF-004", "E-MS-010", "hk3gtl.event.sf004");

        // ── 逐火之蛾 ──
        // E-FM-003: 巨构遗产 — 量子阶段入口
        tryMilestoneTrigger(player, data, "E-FM-003", "E-MS-007", "hk3gtl.event.fm003");
        // E-FM-004: 前文明最后的警告 — 终焉阶段入口
        tryMilestoneTrigger(player, data, "E-FM-004", "E-MS-010", "hk3gtl.event.fm004");

        // ── 符华 ──
        // E-FH-003: 武道与文明 — 海渊阶段完成（深海征服后）
        tryMilestoneTrigger(player, data, "E-FH-003", "E-MS-004", "hk3gtl.event.fh003");

        // ── 布洛妮娅 ──
        // E-BR-003: 布洛妮娅的计算 — 量子阶段完成
        tryMilestoneTrigger(player, data, "E-BR-003", "E-MS-009", "hk3gtl.event.br003");
        // E-BR-004: 最后的数据包 — 终焉阶段入口
        tryMilestoneTrigger(player, data, "E-BR-004", "E-MS-010", "hk3gtl.event.br004");

        // ── 梅比乌斯 ──
        // E-MB-004: 蛇的微笑 — 终焉阶段入口
        tryMilestoneTrigger(player, data, "E-MB-004", "E-MS-010", "hk3gtl.event.mb004");

        // ── 琪亚娜 ──
        // E-KI-003: 最后门前 — 终焉阶段主结构群大半完成（终焉III达成后）
        tryMilestoneTrigger(player, data, "E-KI-003", "E-MS-012", "hk3gtl.event.ki003");
    }

    /**
     * 注视度阈值型事件：当玩家注视度达到指定阈值时触发。
     * 注视度由注视度系统写入 persistentData，本方法只读取。
     * 若注视度系统尚未实装（tag 不存在），getInt 返回 0，事件不会误触发。
     */
    private static void checkGazeThresholdEvents(ServerPlayer player, CompoundTag data) {
        int gaze = data.getInt(GAZE_TAG);
        if (gaze <= 0) return;

        // ── 圣芙蕾雅 ──
        // E-SF-002: 研究提醒 — 注视度首次达到100
        tryGazeTrigger(player, data, "E-SF-002", 100, "hk3gtl.event.sf002");

        // ── 娑 ──
        // E-SA-001: 观测落点 — 注视度首次达到500
        tryGazeTrigger(player, data, "E-SA-001", 500, "hk3gtl.event.sa001");

        // ── 空之律者 ──
        // E-HQ-001: 第一次注目 — 注视度达到800
        tryGazeTrigger(player, data, "E-HQ-001", 800, "hk3gtl.event.hq001");
    }

    // ═══════════════════════════════════════════════════
    //  多方块建成入口（由 Hk3EventManagerImpl.onMultiblockFormed 调用）
    // ═══════════════════════════════════════════════════

    /**
     * 多方块建成时的阵营事件分发。
     * 同一台机器可能同时触发多个阵营的事件（如量子纠缠计算机触发5个阵营事件）。
     */
    public static void onMultiblockFormedFaction(ServerPlayer player, String machineId) {
        switch (machineId) {
            // ── 奥托/天命 ──
            // (E-OT-001 已由 Hk3EventManagerImpl 处理)

            // ── 瓦尔特 ──
            // E-WL-001 已改由 Hk3EventManagerImpl 检测背包 gtceu:circuits/max 触发

            case "quantum_entanglement_computer" -> {
                // E-WL-002: 理之律者的忠告
                Hk3EventService.tryTriggerFirstTime(player, "E-WL-002", "hk3gtl.event.wl002");
                // E-AE-003: 工程敬意（逆熵）
                Hk3EventService.tryTriggerFirstTime(player, "E-AE-003", "hk3gtl.event.ae003");
                // E-KI-001: 远方回应（琪亚娜）
                Hk3EventService.tryTriggerFirstTime(player, "E-KI-001", "hk3gtl.event.ki001");
                // E-BR-001: 数据接入（布洛妮娅）
                Hk3EventService.tryTriggerFirstTime(player, "E-BR-001", "hk3gtl.event.br001");
                // E-TS-003: 科学家的敬意（特斯拉/爱因斯坦）
                Hk3EventService.tryTriggerFirstTime(player, "E-TS-003", "hk3gtl.event.ts003");
            }

            case "thousand_realms_train" -> {
                // E-WL-003: 瓦尔特的认可
                Hk3EventService.tryTriggerFirstTime(player, "E-WL-003", "hk3gtl.event.wl003");
                // E-KI-002: 静默承认（琪亚娜）
                Hk3EventService.tryTriggerFirstTime(player, "E-KI-002", "hk3gtl.event.ki002");
            }

            // ── 世界蛇 ──
            case "imaginary_anchor_device" ->
                    // E-WS-003: 蛇的试探 — 虚数锚定装置建成
                    Hk3EventService.tryTriggerFirstTime(player, "E-WS-003", "hk3gtl.event.ws003");

            case "hyperion_flagship" ->
                    // E-WS-005: 蛇的评价 — 休伯利安号建成
                    Hk3EventService.tryTriggerFirstTime(player, "E-WS-005", "hk3gtl.event.ws005");

            case "civilization_validation_matrix" -> {
                // E-WS-006: 终局观察（世界蛇）
                Hk3EventService.tryTriggerFirstTime(player, "E-WS-006", "hk3gtl.event.ws006");
                // E-FM-005: 逐火之蛾的遗言
                Hk3EventService.tryTriggerFirstTime(player, "E-FM-005", "hk3gtl.event.fm005");
                // E-KI-004: 琪亚娜的注视
                Hk3EventService.tryTriggerFirstTime(player, "E-KI-004", "hk3gtl.event.ki004");
                // E-SA-003: 终局压迫（娑）
                Hk3EventService.tryTriggerFirstTime(player, "E-SA-003", "hk3gtl.event.sa003");
                // E-FH-005: 千年的见证（符华）
                Hk3EventService.tryTriggerFirstTime(player, "E-FH-005", "hk3gtl.event.fh005");
            }

            // ── 逆熵 ──
            case "large_honkai_reactor" -> {
                // E-AE-001: 工程协助 — 首个崩坏能反应堆建成（模组内以大型反应堆代理）
                Hk3EventService.tryTriggerFirstTime(player, "E-AE-001", "hk3gtl.event.ae001");
                // E-TS-001: 工程师的好奇
                Hk3EventService.tryTriggerFirstTime(player, "E-TS-001", "hk3gtl.event.ts001");
            }

            case "dual_energy_stable_supply_station" ->
                    // E-AE-002: 系统兼容报告 — 双能源系统建立
                    Hk3EventService.tryTriggerFirstTime(player, "E-AE-002", "hk3gtl.event.ae002");

            // ── 逐火之蛾 ──
            case "precivilization_database_decoder" -> {
                // E-FM-001: 封存权限开启 — 前文明数据库解码塔建成
                Hk3EventService.tryTriggerFirstTime(player, "E-FM-001", "hk3gtl.event.fm001");
                // E-FH-002: 历史的回响（符华）
                Hk3EventService.tryTriggerFirstTime(player, "E-FH-002", "hk3gtl.event.fh002");
            }

            // ── 月球基地 ──
            case "divine_key_gallery" ->
                    // E-LB-002: 高等级访问授权 — 神之键展示室建成（量子级权限升级）
                    Hk3EventService.tryTriggerFirstTime(player, "E-LB-002", "hk3gtl.event.lb002");

            // ── 娑 ──
            case "imaginary_dimension_gateway" -> {
                // E-SA-004: 娑的凝视 — 虚数维度跃迁门建成
                Hk3EventService.tryTriggerFirstTime(player, "E-SA-004", "hk3gtl.event.sa004");
                // E-HQ-004: 她的等待（空之律者）
                Hk3EventService.tryTriggerFirstTime(player, "E-HQ-004", "hk3gtl.event.hq004");
            }

            // ── 布洛妮娅 ──
            case "honkai_wireless_transit_hub" ->
                    // E-BR-002: 网络优化方案 — 无线崩坏能跃迁枢纽建成
                    Hk3EventService.tryTriggerFirstTime(player, "E-BR-002", "hk3gtl.event.br002");

            // ── 梅比乌斯 ──
            case "imaginary_matter_weaver" ->
                    // E-MB-001: 实验邀请 — 虚数物质编织机建成
                    Hk3EventService.tryTriggerFirstTime(player, "E-MB-001", "hk3gtl.event.mb001");

            case "soulium_superstructure_forge" ->
                    // E-MB-002: 进化的代价 — 魂钢超结构锻造厅建成
                    Hk3EventService.tryTriggerFirstTime(player, "E-MB-002", "hk3gtl.event.mb002");

            // ── 爱莉希雅 ──
            case "civilization_exchange_council_hub" ->
                    // E-EL-001: 温柔的问候 — 虚数议会中枢建成（首个正式跨文明交流设施）
                    Hk3EventService.tryTriggerFirstTime(player, "E-EL-001", "hk3gtl.event.el001");

            case "imaginary_circuit_computation_sanctum" ->
                    // E-EL-002: 记忆与意义 — 虚数级电路演算圣堂建成
                    Hk3EventService.tryTriggerFirstTime(player, "E-EL-002", "hk3gtl.event.el002");

            default -> { /* 无阵营事件 */ }
        }
    }

    // ═══════════════════════════════════════════════════
    //  研究完成入口（由 Hk3ResearchManager.completeResearch 调用）
    // ═══════════════════════════════════════════════════

    /**
     * 研究节点完成时的阵营事件分发。
     * 同一个研究节点可能触发多个阵营的事件。
     *
     */
    public static void onResearchCompleted(ServerPlayer player, String researchId) {
        switch (researchId) {
            // ── 海渊阶段研究 ──
            case "R-AB-001" -> {
                // E-SF-001: 初次补给（圣芙蕾雅）— 崩坏能基础研究完成
                Hk3EventService.tryTriggerFirstTime(player, "E-SF-001", "hk3gtl.event.sf001");
                // E-FH-001: 古老的注视（符华）— 崩坏能基础理论完成
                Hk3EventService.tryTriggerFirstTime(player, "E-FH-001", "hk3gtl.event.fh001");
            }
            case "R-AB-011" ->
                    // E-OT-003: 天命技术评估 — 海渊II电压解锁
                    Hk3EventService.tryTriggerFirstTime(player, "E-OT-003", "hk3gtl.event.ot003");

            case "R-AB-017" ->
                    // E-WS-002: 危险交易（世界蛇）— 海渊III研究完成
                    Hk3EventService.tryTriggerFirstTime(player, "E-WS-002", "hk3gtl.event.ws002");

            case "R-AB-025" -> {
                // E-OT-002: 天命档案馈赠 — 虚空万藏解析完成
                Hk3EventService.tryTriggerFirstTime(player, "E-OT-002", "hk3gtl.event.ot002");
                // E-FM-002: 魂钢工艺记录（逐火之蛾）
                Hk3EventService.tryTriggerFirstTime(player, "E-FM-002", "hk3gtl.event.fm002");
            }

            // ── 虚数阶段研究 ──
            case "R-IM-002" ->
                    // E-LB-001: 通道确认 — 虚数之树观测阵相关研究完成
                    Hk3EventService.tryTriggerFirstTime(player, "E-LB-001", "hk3gtl.event.lb001");

            case "R-IM-019" -> {
                // E-FH-004: 符华的沉思 — 虚数理论实验完成
                Hk3EventService.tryTriggerFirstTime(player, "E-FH-004", "hk3gtl.event.fh004");
                // E-TS-002: 理论讨论（特斯拉/爱因斯坦）
                Hk3EventService.tryTriggerFirstTime(player, "E-TS-002", "hk3gtl.event.ts002");
            }

            // ── 量子阶段研究 ──
            case "R-QT-007" -> {
                // E-WS-004: 高风险技术交换 — 量子II电压解锁
                Hk3EventService.tryTriggerFirstTime(player, "E-WS-004", "hk3gtl.event.ws004");
                // E-MB-003: 危险的知识（梅比乌斯）
                Hk3EventService.tryTriggerFirstTime(player, "E-MB-003", "hk3gtl.event.mb003");
            }
            case "R-QT-003" ->
                    // E-SA-002: 试探交换（娑）— 量子III研究完成
                    Hk3EventService.tryTriggerFirstTime(player, "E-SA-002", "hk3gtl.event.sa002");

            // ── 终焉阶段研究 ──
            case "R-FN-003" ->
                    // E-HQ-002: 杰作与资格 — 休伯利安舰载扩展研究完成
                    Hk3EventService.tryTriggerFirstTime(player, "E-HQ-002", "hk3gtl.event.hq002");

            case "R-FN-007" ->
                    // E-LB-003: 终局前校验 — 文明验证矩阵理论完成
                    Hk3EventService.tryTriggerFirstTime(player, "E-LB-003", "hk3gtl.event.lb003");

            case "R-FN-009" ->
                    // 毕业前终局认证：门前裁定 + 三阵营告别
                    triggerPreGraduationCertification(player);

            default -> { /* 无阵营事件 */ }
        }
    }

    // ═══════════════════════════════════════════════════
    //  外部触发入口（由毕业系统、特殊条件系统调用）
    // ═══════════════════════════════════════════════════

    /**
     * 外部系统直接触发阵营事件。
     * 适用于需要复杂条件判断、无法归入上述分类的事件：
     * <ul>
     *   <li>E-AE-005: 逆熵的告别 — 毕业前终局认证</li>
     *   <li>E-LB-004: 月球基地最终许可 — 毕业前终局认证</li>
     *   <li>E-EL-003: 爱莉希雅的祝福 — 毕业前终局认证</li>
     *   <li>E-HQ-002: 杰作与资格 — 休伯利安号满阶扩展</li>
     *   <li>E-HQ-003: 门前裁定 — 毕业前最后条件完成</li>
     *   <li>E-HQ-005: 终局对话 — 进入虚数维度接近唯一实体</li>
     * </ul>
     */
    public static void triggerFactionEvent(ServerPlayer player, String eventId, String langKey) {
        Hk3EventService.tryTriggerFirstTime(player, eventId, langKey);
    }

    /** 终局对话 UI 打开时触发 E-HQ-005 */
    public static void onFinaleDialogueStarted(ServerPlayer player) {
        triggerFactionEvent(player, "E-HQ-005", "hk3gtl.event.hq005");
        Hk3EasterEggChecker.onFinaleDialogueOpened(player);
    }

    /** 毕业前终局认证：E-HQ-003 + 逆熵/月球/爱莉希雅告别 */
    public static void triggerPreGraduationCertification(ServerPlayer player) {
        triggerFactionEvent(player, "E-HQ-003", "hk3gtl.event.hq003");
        triggerFactionEvent(player, "E-AE-005", "hk3gtl.event.ae005");
        triggerFactionEvent(player, "E-LB-004", "hk3gtl.event.lb004");
        triggerFactionEvent(player, "E-EL-003", "hk3gtl.event.el003");
    }

    /** 文明毕业里程碑 E-MS-015 */
    public static void triggerGraduationComplete(ServerPlayer player) {
        Hk3EventService.tryTriggerFirstTime(player, "E-MS-015", "hk3gtl.event.ms015");
        Hk3EasterEggChecker.onGraduationComplete(player);
    }

    // ═══════════════════════════════════════════════════
    //  工具方法
    // ═══════════════════════════════════════════════════

    /** 里程碑依赖：仅当目标事件未触发且前置里程碑已触发时触发 */
    private static void tryMilestoneTrigger(ServerPlayer player, CompoundTag data,
                                            String eventId, String requiredMilestone, String langKey) {
        if (!Hk3EventService.isEventMarked(data, eventId) && Hk3EventService.isEventMarked(data, requiredMilestone)) {
            Hk3EventService.tryTriggerFirstTime(player, eventId, langKey);
        }
    }

    /** 注视度阈值：仅当目标事件未触发且注视度 >= threshold 时触发 */
    private static void tryGazeTrigger(ServerPlayer player, CompoundTag data,
                                       String eventId, int threshold, String langKey) {
        if (!Hk3EventService.isEventMarked(data, eventId) && data.getInt(GAZE_TAG) >= threshold) {
            Hk3EventService.tryTriggerFirstTime(player, eventId, langKey);
        }
    }

}
