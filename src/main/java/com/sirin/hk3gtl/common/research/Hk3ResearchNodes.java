package com.sirin.hk3gtl.common.research;



import com.gregtechceu.gtceu.api.data.chemical.ChemicalHelper;
import com.gregtechceu.gtceu.api.data.tag.TagPrefix;
import com.gregtechceu.gtceu.data.recipe.CustomTags;
import com.sirin.hk3gtl.common.item.abyss.AbyssCircuitItems;
import com.sirin.hk3gtl.common.item.abyss.AbyssFunctionalItems;
import com.sirin.hk3gtl.common.item.finality.FinalityCircuitItems;
import com.sirin.hk3gtl.common.item.honkai.HonkaiMaterialItems;
import com.sirin.hk3gtl.common.item.imaginary.ImaginaryCircuitItems;
import com.sirin.hk3gtl.common.item.quantum.QuantumCircuitItems;
import com.sirin.hk3gtl.common.material.SouliumMaterial;
import net.minecraft.world.item.ItemStack;

import java.util.Collection;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * P2 海渊阶段全部 25 个研究节点注册表。
 *
 * <h3>职责</h3>
 * 集中定义所有研究节点的 ID、类型、tier、前置、提交物和解锁效果。
 * 节点按 tier 从低到高、按功能分组排列。
 *
 * <h3>修改指南 (Where to modify research data)</h3>
 * <ul>
 *   <li>新增节点 → 仿照现有格式调用 {@link #reg}，注意 ID 不要重复 (R-XX-XXX)</li>
 *   <li>修改前置依赖 → 更改 `prereqs` 列表中的 ID 字符串</li>
 *   <li>修改提交物 → 更改 `reqs` 列表中的 {@link #req} 调用，可以替换 ItemStack 的物品与数量</li>
 *   <li>修改自动/手动类型 → autoEvent 参数非 null 即为自动完成型</li>
 *   <li>翻译键 → 需同步 zh_cn.json / en_us.json 中的描述文本</li>
 * </ul>
 *
 * <h3>reg() 参数顺序</h3>
 * {@code reg(id, type, tier, nameKey, effectKey, unlockKey, prereqs, reqEvent, autoEvent, reqs)}
 * <ul>
 *   <li>reqEvent = 需要的前置事件（如 "E-FB-007" = 研究矩阵已激活）</li>
 *   <li>autoEvent = 自动完成事件（非 null 表示事件触发后自动完成）</li>
 * </ul>
 *
 * 依赖图参见设计文档：06_科技树与研究系统/研究节点依赖图与卡关检查表.md
 */
public class Hk3ResearchNodes {

    /** 按注册顺序存储所有节点，用 LinkedHashMap 保证遍历顺序 */
    private static final Map<String, Hk3ResearchNode> NODES = new LinkedHashMap<>();


    // ══════════════════════════════════════
    //  自动完成型节点（autoEvent 非 null，事件触发后自动标记完成）
    // ══════════════════════════════════════

    /** R-AB-001: 理论型 | tier=14.5 | 无前置 | 事件 E-MS-001 触发自动完成 → 解锁海渊科技入口 */
    public static final Hk3ResearchNode R_AB_001 = reg("R-AB-001", Hk3ResearchType.THEORY, 14.5,
            "hk3gtl.research.r_ab_001.name", "hk3gtl.research.r_ab_001.effect", "hk3gtl.research.r_ab_001.unlock",
            List.of(), null, "E-MS-001", List.of());

    /** R-AB-002「崩坏能结晶化工艺」: 材料型 | tier=14.8 | 前置 R-AB-001 | 事件 E-MS-001 自动完成 → 解锁魂钢材料
     *  修复死循环：原绑定 E-FB-003（大型崩坏能反应堆建成）作为完成条件，
     *  而反应堆控制器配方门槛(R-AB-007)又前置本研究，形成"造反应堆需先解锁本研究、
     *  解锁本研究又需先造反应堆"的死回圈。改绑 E-MS-001（背包首次持有崩坏能结晶）后，
     *  完成条件回到"持有崩坏能结晶"这一可独立达成的前置，回圈消除。 */
    public static final Hk3ResearchNode R_AB_002 = reg("R-AB-002", Hk3ResearchType.MATERIAL, 14.8,
            "hk3gtl.research.r_ab_002.name", "hk3gtl.research.r_ab_002.effect", "hk3gtl.research.r_ab_002.unlock",
            List.of("R-AB-001"), null, "E-MS-001", List.of());

    /** R-AB-003: 材料型 | tier=15.0 | 前置 R-AB-001 | 事件 E-MS-002 自动完成 */
    public static final Hk3ResearchNode R_AB_003 = reg("R-AB-003", Hk3ResearchType.MATERIAL, 15.0,
            "hk3gtl.research.r_ab_003.name", "hk3gtl.research.r_ab_003.effect", "hk3gtl.research.r_ab_003.unlock",
            List.of("R-AB-001"), null, "E-MS-002", List.of());

    /** R-AB-025: 事件型 | tier=15.0 | 无前置 | 事件 E-OT-001 自动完成 */
    public static final Hk3ResearchNode R_AB_025 = reg("R-AB-025", Hk3ResearchType.EVENT, 15.0,
            "hk3gtl.research.r_ab_025.name", "hk3gtl.research.r_ab_025.effect", "hk3gtl.research.r_ab_025.unlock",
            List.of(), null, "E-OT-001", List.of());

    /** R-WL-001: 事件型 | tier=14.9 | 事件 E-WL-001 自动完成 → 解锁理构电路重构阵列的崩坏能电路板配方 */
    public static final Hk3ResearchNode R_WL_001 = reg("R-WL-001", Hk3ResearchType.EVENT, 14.9,
            "hk3gtl.research.r_wl_001.name", "hk3gtl.research.r_wl_001.effect", "hk3gtl.research.r_wl_001.unlock",
            List.of("R-AB-001"), null, "E-WL-001", List.of());

    // ══════════════════════════════════════
    //  手动提交型 — 海渊 I 基础层（需要手动提交物品完成）
    // ══════════════════════════════════════

    /** R-AB-004: 电压型 | tier=15.0 | 前置 R-AB-001 | 事件 E-FB-007 | 提交: 崩坏能结晶×16 + 魂钢板×8 → 解锁海渊I电压 */
    public static final Hk3ResearchNode R_AB_004 = reg("R-AB-004", Hk3ResearchType.VOLTAGE, 15.0,
            "hk3gtl.research.r_ab_004.name", "hk3gtl.research.r_ab_004.effect", "hk3gtl.research.r_ab_004.unlock",
            List.of("R-AB-001"), "E-FB-007", null, List.of(
                    req(() -> new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 16), "hk3gtl.research.requirement.honkai_energy_crystal"),
                    req(() -> ChemicalHelper.get(TagPrefix.plate, SouliumMaterial.SOULIUM, 8), "hk3gtl.research.requirement.soulium_plate")
            ));

    /** R-AB-005: 电路型 | tier=15.2 | 前置 R-AB-004 | 提交: 崩坏能结晶×4 + 魂钢细丝×8 + 魂钢箔×2 → 解锁海渊I电路 */
    public static final Hk3ResearchNode R_AB_005 = reg("R-AB-005", Hk3ResearchType.CIRCUIT, 15.2,
            "hk3gtl.research.r_ab_005.name", "hk3gtl.research.r_ab_005.effect", "hk3gtl.research.r_ab_005.unlock",
            List.of("R-AB-004"), "E-FB-007", null, List.of(
                    req(() -> new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 4), "hk3gtl.research.requirement.honkai_energy_crystal"),
                    req(() -> ChemicalHelper.get(TagPrefix.wireFine, SouliumMaterial.SOULIUM, 8), "hk3gtl.research.requirement.soulium_fine_wire"),
                    req(() -> ChemicalHelper.get(TagPrefix.foil, SouliumMaterial.SOULIUM, 2), "hk3gtl.research.requirement.soulium_foil")
            ));

    /** R-AB-006: 结构型 | tier=15.3 | 前置 R-AB-004+005 | 提交: 海渊I电路×1 + 魂钢板×8 + 崩坏能结晶×4 → 解锁海渊I结构 */
    public static final Hk3ResearchNode R_AB_006 = reg("R-AB-006", Hk3ResearchType.STRUCTURE, 15.3,
            "hk3gtl.research.r_ab_006.name", "hk3gtl.research.r_ab_006.effect", "hk3gtl.research.r_ab_006.unlock",
            List.of("R-AB-004", "R-AB-005"), "E-FB-007", null, List.of(
                    req(() -> new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_1.get(), 1), "hk3gtl.research.requirement.abyss_circuit_1"),
                    req(() -> ChemicalHelper.get(TagPrefix.plate, SouliumMaterial.SOULIUM, 8), "hk3gtl.research.requirement.soulium_plate"),
                    req(() -> new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 4), "hk3gtl.research.requirement.honkai_energy_crystal")
            ));

    // ══════════════════════════════════════
    //  手动提交型 — 能力类（从 R-AB-001/002 直接扩展）
    // ══════════════════════════════════════

    /** R-AB-007: 理论型 | tier=15.5 | 前置 R-AB-002 | 提交: 崩坏能燃料棒×4 + 崩坏能结晶×8 */
    public static final Hk3ResearchNode R_AB_007 = reg("R-AB-007", Hk3ResearchType.THEORY, 15.5,
            "hk3gtl.research.r_ab_007.name", "hk3gtl.research.r_ab_007.effect", "hk3gtl.research.r_ab_007.unlock",
            List.of("R-AB-002"), "E-FB-007", null, List.of(
                    req(() -> new ItemStack(HonkaiMaterialItems.HONKAI_FUEL_ROD.get(), 4), "hk3gtl.research.requirement.honkai_fuel_rod"),
                    req(() -> new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 8), "hk3gtl.research.requirement.honkai_energy_crystal")
            ));

    /** R-AB-008: 理论型 | tier=15.5 | 前置 R-AB-001 | 提交: 崩坏能结晶×16 + 凝视缓冲单元×2 */
    public static final Hk3ResearchNode R_AB_008 = reg("R-AB-008", Hk3ResearchType.THEORY, 15.5,
            "hk3gtl.research.r_ab_008.name", "hk3gtl.research.r_ab_008.effect", "hk3gtl.research.r_ab_008.unlock",
            List.of("R-AB-001"), "E-FB-007", null, List.of(
                    req(() -> new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 16), "hk3gtl.research.requirement.honkai_energy_crystal"),
                    req(() -> new ItemStack(HonkaiMaterialItems.GAZE_BUFFER_UNIT.get(), 2), "hk3gtl.research.requirement.gaze_buffer_unit")
            ));

    /** R-AB-009: 理论型 | tier=15.5 | 前置 R-AB-001 | 提交: 崩坏能结晶×8 + 任意MAX级电路×2（gtceu:circuits/max 标签匹配） */
    public static final Hk3ResearchNode R_AB_009 = reg("R-AB-009", Hk3ResearchType.THEORY, 15.5,
            "hk3gtl.research.r_ab_009.name", "hk3gtl.research.r_ab_009.effect", "hk3gtl.research.r_ab_009.unlock",
            List.of("R-AB-001"), "E-FB-007", null, List.of(
                    req(() -> new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 8), "hk3gtl.research.requirement.honkai_energy_crystal"),
                    Hk3ResearchRequirement.ofTag(CustomTags.MAX_CIRCUITS, 2, "hk3gtl.research.requirement.max_circuit_any")
            ));

    /** R-AB-010: 理论型 | tier=15.5 | 前置 R-AB-001 | 提交: 数据研究包×4 */
    public static final Hk3ResearchNode R_AB_010 = reg("R-AB-010", Hk3ResearchType.THEORY, 15.5,
            "hk3gtl.research.r_ab_010.name", "hk3gtl.research.r_ab_010.effect", "hk3gtl.research.r_ab_010.unlock",
            List.of("R-AB-001"), "E-FB-007", null, List.of(
                    req(() -> new ItemStack(HonkaiMaterialItems.DATA_RESEARCH_PACKAGE.get(), 4), "hk3gtl.research.requirement.data_research_package")
            ));

    // ══════════════════════════════════════
    //  手动提交型 — 海渊 II 层（tier 16.0~16.5）
    // ══════════════════════════════════════

    /** R-AB-011: 电压型 | tier=16.0 | 前置 R-AB-004 | 提交: 海渊I电路×8 + 稳定崩坏能晶体×4 → 解锁海渊II电压 */
    public static final Hk3ResearchNode R_AB_011 = reg("R-AB-011", Hk3ResearchType.VOLTAGE, 16.0,
            "hk3gtl.research.r_ab_011.name", "hk3gtl.research.r_ab_011.effect", "hk3gtl.research.r_ab_011.unlock",
            List.of("R-AB-004"), "E-FB-007", null, List.of(
                    req(() -> new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_1.get(), 8), "hk3gtl.research.requirement.abyss_circuit_1"),
                    req(() -> new ItemStack(HonkaiMaterialItems.STABILIZED_HONKAI_CRYSTAL.get(), 4), "hk3gtl.research.requirement.stabilized_honkai_crystal")
            ));

    /** R-AB-012: 电路型 | tier=16.2 | 前置 R-AB-011 | 提交: 崩坏能结晶×8 + 魂钢箔×16 + 海渊I电路×4 → 解锁海渊2电路(绑定 hk3gtl_circuit_abyss_2) */
    public static final Hk3ResearchNode R_AB_012 = reg("R-AB-012", Hk3ResearchType.CIRCUIT, 16.2,
            "hk3gtl.research.r_ab_012.name", "hk3gtl.research.r_ab_012.effect", "hk3gtl.research.r_ab_012.unlock",
            List.of("R-AB-011"), "E-FB-007", null, List.of(
                    req(() -> new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 8), "hk3gtl.research.requirement.honkai_energy_crystal"),
                    req(() -> ChemicalHelper.get(TagPrefix.foil, SouliumMaterial.SOULIUM, 16), "hk3gtl.research.requirement.soulium_foil"),
                    req(() -> new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_1.get(), 4), "hk3gtl.research.requirement.abyss_circuit_1")
            ));

    /** R-AB-013: 材料型 | tier=16.3 | 前置 R-AB-011 | 提交: 崩坏能结晶×16 + 魂钢板×8 */
    public static final Hk3ResearchNode R_AB_013 = reg("R-AB-013", Hk3ResearchType.MATERIAL, 16.3,
            "hk3gtl.research.r_ab_013.name", "hk3gtl.research.r_ab_013.effect", "hk3gtl.research.r_ab_013.unlock",
            List.of("R-AB-011"), "E-FB-007", null, List.of(
                    req(() -> new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 16), "hk3gtl.research.requirement.honkai_energy_crystal"),
                    req(() -> ChemicalHelper.get(TagPrefix.plate, SouliumMaterial.SOULIUM, 8), "hk3gtl.research.requirement.soulium_plate")
            ));

    /** R-AB-014: 材料型 | tier=16.5 | 前置 R-AB-013 | 提交: 稳定崩坏能晶体×4 + 压缩崩坏能核心×2 */
    public static final Hk3ResearchNode R_AB_014 = reg("R-AB-014", Hk3ResearchType.MATERIAL, 16.5,
            "hk3gtl.research.r_ab_014.name", "hk3gtl.research.r_ab_014.effect", "hk3gtl.research.r_ab_014.unlock",
            List.of("R-AB-013"), "E-FB-007", null, List.of(
                    req(() -> new ItemStack(HonkaiMaterialItems.STABILIZED_HONKAI_CRYSTAL.get(), 4), "hk3gtl.research.requirement.stabilized_honkai_crystal"),
                    req(() -> new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 2), "hk3gtl.research.requirement.compressed_honkai_core")
            ));

    /** R-AB-015: 结构型 | tier=16.5 | 前置 R-AB-007 | 提交: 崩坏能燃料棒×8 + 崩坏能结晶×16 + 魂钢框架×4 */
    public static final Hk3ResearchNode R_AB_015 = reg("R-AB-015", Hk3ResearchType.STRUCTURE, 16.5,
            "hk3gtl.research.r_ab_015.name", "hk3gtl.research.r_ab_015.effect", "hk3gtl.research.r_ab_015.unlock",
            List.of("R-AB-007"), "E-FB-007", null, List.of(
                    req(() -> new ItemStack(HonkaiMaterialItems.HONKAI_FUEL_ROD.get(), 8), "hk3gtl.research.requirement.honkai_fuel_rod"),
                    req(() -> new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 16), "hk3gtl.research.requirement.honkai_energy_crystal"),
                    req(() -> ChemicalHelper.get(TagPrefix.frameGt, SouliumMaterial.SOULIUM, 4), "hk3gtl.research.requirement.soulium_frame")
            ));

    /** R-AB-016: 材料型 | tier=16.0 | 前置 R-AB-003 | 提交: 魂钢细丝×32 + 海渊I电路×4 */
    public static final Hk3ResearchNode R_AB_016 = reg("R-AB-016", Hk3ResearchType.MATERIAL, 16.0,
            "hk3gtl.research.r_ab_016.name", "hk3gtl.research.r_ab_016.effect", "hk3gtl.research.r_ab_016.unlock",
            List.of("R-AB-003"), "E-FB-007", null, List.of(
                    req(() -> ChemicalHelper.get(TagPrefix.wireFine, SouliumMaterial.SOULIUM, 32), "hk3gtl.research.requirement.soulium_fine_wire"),
                    req(() -> new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_1.get(), 4), "hk3gtl.research.requirement.abyss_circuit_1")
            ));

    // ══════════════════════════════════════
    //  手动提交型 — 海渊 III 层（tier 17.0~17.2）
    // ══════════════════════════════════════

    /** R-AB-017: 电压型 | tier=17.0 | 前置 R-AB-011 | 提交: 海渊I电路×16 + 崩坏能结晶×16 → 解锁海渊III电压 */
    public static final Hk3ResearchNode R_AB_017 = reg("R-AB-017", Hk3ResearchType.VOLTAGE, 17.0,
            "hk3gtl.research.r_ab_017.name", "hk3gtl.research.r_ab_017.effect", "hk3gtl.research.r_ab_017.unlock",
            List.of("R-AB-011"), "E-FB-007", null, List.of(
                    req(() -> new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_1.get(), 16), "hk3gtl.research.requirement.abyss_circuit_1"),
                    req(() -> new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 16), "hk3gtl.research.requirement.honkai_energy_crystal")
            ));

    /** R-AB-018: 电路型 | tier=17.2 | 前置 R-AB-017 | 提交: 崩坏能结晶×16 + 魂钢板×16 + 海渊I电路×8 → 解锁海渊3电路(绑定 hk3gtl_circuit_abyss_3) */
    public static final Hk3ResearchNode R_AB_018 = reg("R-AB-018", Hk3ResearchType.CIRCUIT, 17.2,
            "hk3gtl.research.r_ab_018.name", "hk3gtl.research.r_ab_018.effect", "hk3gtl.research.r_ab_018.unlock",
            List.of("R-AB-017"), "E-FB-007", null, List.of(
                    req(() -> new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 16), "hk3gtl.research.requirement.honkai_energy_crystal"),
                    req(() -> ChemicalHelper.get(TagPrefix.plate, SouliumMaterial.SOULIUM, 16), "hk3gtl.research.requirement.soulium_plate"),
                    req(() -> new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_1.get(), 8), "hk3gtl.research.requirement.abyss_circuit_1")
            ));

    // ══════════════════════════════════════
    //  手动提交型 — 特殊理论线（tier 16.0~17.5，与主线平行）
    // ══════════════════════════════════════

    /** R-AB-019: 理论型 | tier=17.0 | 前置 R-AB-001 | 提交: 崩坏能结晶×32 + 凝视缓冲单元×4 */
    public static final Hk3ResearchNode R_AB_019 = reg("R-AB-019", Hk3ResearchType.THEORY, 17.0,
            "hk3gtl.research.r_ab_019.name", "hk3gtl.research.r_ab_019.effect", "hk3gtl.research.r_ab_019.unlock",
            List.of("R-AB-001"), "E-FB-007", null, List.of(
                    req(() -> new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 32), "hk3gtl.research.requirement.honkai_energy_crystal"),
                    req(() -> new ItemStack(HonkaiMaterialItems.GAZE_BUFFER_UNIT.get(), 4), "hk3gtl.research.requirement.gaze_buffer_unit")
            ));

    /** R-AB-020: 理论型 | tier=17.5 | 前置 R-AB-019 | 提交: 世界泡样本×1 + 崩坏能结晶×16 */
    public static final Hk3ResearchNode R_AB_020 = reg("R-AB-020", Hk3ResearchType.THEORY, 17.5,
            "hk3gtl.research.r_ab_020.name", "hk3gtl.research.r_ab_020.effect", "hk3gtl.research.r_ab_020.unlock",
            List.of("R-AB-019"), "E-FB-007", null, List.of(
                    req(() -> new ItemStack(HonkaiMaterialItems.WORLD_BUBBLE_SAMPLE.get(), 1), "hk3gtl.research.requirement.world_bubble_sample"),
                    req(() -> new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 16), "hk3gtl.research.requirement.honkai_energy_crystal")
            ));

    /** R-AB-023: 理论型 | tier=16.0 | 前置 R-AB-001 | 提交: 崩坏能抑制剂×4 + 崩坏能结晶×8 */
    public static final Hk3ResearchNode R_AB_023 = reg("R-AB-023", Hk3ResearchType.THEORY, 16.0,
            "hk3gtl.research.r_ab_023.name", "hk3gtl.research.r_ab_023.effect", "hk3gtl.research.r_ab_023.unlock",
            List.of("R-AB-001"), "E-FB-007", null, List.of(
                    req(() -> new ItemStack(HonkaiMaterialItems.HONKAI_SUPPRESSANT.get(), 4), "hk3gtl.research.requirement.honkai_suppressant"),
                    req(() -> new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 8), "hk3gtl.research.requirement.honkai_energy_crystal")
            ));

    // ══════════════════════════════════════
    //  手动提交型 — 海渊 IV 层（tier 18.0~18.2）
    // ══════════════════════════════════════

    /** R-AB-021: 电压型 | tier=18.0 | 前置 R-AB-017 | 提交: 崩坏能结晶×32 + 稳定崩坏能晶体×8 + 海渊I电路×16 → 解锁海渊IV电压 */
    public static final Hk3ResearchNode R_AB_021 = reg("R-AB-021", Hk3ResearchType.VOLTAGE, 18.0,
            "hk3gtl.research.r_ab_021.name", "hk3gtl.research.r_ab_021.effect", "hk3gtl.research.r_ab_021.unlock",
            List.of("R-AB-017"), "E-FB-007", null, List.of(
                    req(() -> new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 32), "hk3gtl.research.requirement.honkai_energy_crystal"),
                    req(() -> new ItemStack(HonkaiMaterialItems.STABILIZED_HONKAI_CRYSTAL.get(), 8), "hk3gtl.research.requirement.stabilized_honkai_crystal"),
                    req(() -> new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_1.get(), 16), "hk3gtl.research.requirement.abyss_circuit_1")
            ));

    /** R-AB-022: 电路型 | tier=18.2 | 前置 R-AB-021 | 提交: 崩坏能结晶×32 + 魂钢箔×32 + 海渊I电路×16 → 解锁海渊4电路(绑定 hk3gtl_circuit_abyss_4) */
    public static final Hk3ResearchNode R_AB_022 = reg("R-AB-022", Hk3ResearchType.CIRCUIT, 18.2,
            "hk3gtl.research.r_ab_022.name", "hk3gtl.research.r_ab_022.effect", "hk3gtl.research.r_ab_022.unlock",
            List.of("R-AB-021"), "E-FB-007", null, List.of(
                    req(() -> new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 32), "hk3gtl.research.requirement.honkai_energy_crystal"),
                    req(() -> ChemicalHelper.get(TagPrefix.foil, SouliumMaterial.SOULIUM, 32), "hk3gtl.research.requirement.soulium_foil"),
                    req(() -> new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_1.get(), 16), "hk3gtl.research.requirement.abyss_circuit_1")
            ));

    // ══════════════════════════════════════
    //  手动提交型 — 海渊出口认证（最终节点 tier=18.5）
    // ══════════════════════════════════════

    /** R-AB-024: 认证型 | tier=18.5 | 前置 R-AB-022+020+025 | 提交: 世界泡样本×1 + 数据研究包×8 → 通过海渊出口认证 */
    public static final Hk3ResearchNode R_AB_024 = reg("R-AB-024", Hk3ResearchType.CERTIFICATION, 18.5,
            "hk3gtl.research.r_ab_024.name", "hk3gtl.research.r_ab_024.effect", "hk3gtl.research.r_ab_024.unlock",
            List.of("R-AB-022", "R-AB-020", "R-AB-025"), "E-FB-007", null, List.of(
                    req(() -> new ItemStack(HonkaiMaterialItems.WORLD_BUBBLE_SAMPLE.get(), 1), "hk3gtl.research.requirement.world_bubble_sample"),
                    req(() -> new ItemStack(HonkaiMaterialItems.DATA_RESEARCH_PACKAGE.get(), 8), "hk3gtl.research.requirement.data_research_package")
            ));

    // ══════════════════════════════════════
    //  手动提交型 — 虚数阶段入口（补齐配方门控 R-IM-001~004）
    // ══════════════════════════════════════

    /** R-IM-001: 虚数 I 电路与基础机壳门控 */
    public static final Hk3ResearchNode R_IM_001 = reg("R-IM-001", Hk3ResearchType.CIRCUIT, 19.0,
            "hk3gtl.research.r_im_001.name", "hk3gtl.research.r_im_001.effect", "hk3gtl.research.r_im_001.unlock",
            List.of("R-AB-024"), "E-FB-009", null, List.of(
                    req(() -> new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_4.get(), 16), "hk3gtl.research.requirement.abyss_circuit_4"),
                    req(() -> new ItemStack(HonkaiMaterialItems.NANO_CERAMIC.get(), 32), "hk3gtl.research.requirement.nano_ceramic"),
                    req(() -> new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 16), "hk3gtl.research.requirement.compressed_honkai_core"),
                    req(() -> new ItemStack(HonkaiMaterialItems.WORLD_BUBBLE_SAMPLE.get(), 1), "hk3gtl.research.requirement.world_bubble_sample")
            ));

    /** R-IM-002: 虚数 II 控制器与文明交流设施门控 */
    public static final Hk3ResearchNode R_IM_002 = reg("R-IM-002", Hk3ResearchType.STRUCTURE, 20.0,
            "hk3gtl.research.r_im_002.name", "hk3gtl.research.r_im_002.effect", "hk3gtl.research.r_im_002.unlock",
            List.of("R-IM-001"), "E-FB-009", null, List.of(
                    req(() -> new ItemStack(HonkaiMaterialItems.SUPERCONDUCTIVE_METAL_HYDROGEN.get(), 32), "hk3gtl.research.requirement.superconductive_metal_hydrogen"),
                    req(() -> new ItemStack(HonkaiMaterialItems.SCHICKSAL_IMAGINARY_CORE.get(), 8), "hk3gtl.research.requirement.schicksal_imaginary_core"),
                    req(() -> new ItemStack(HonkaiMaterialItems.ANTI_ENTROPY_IMAGINARY_CORE.get(), 8), "hk3gtl.research.requirement.anti_entropy_imaginary_core"),
                    req(() -> new ItemStack(HonkaiMaterialItems.DATA_RESEARCH_PACKAGE.get(), 16), "hk3gtl.research.requirement.data_research_package")
            ));

    /** R-IM-003: 虚数 III 高维演算门控 */
    public static final Hk3ResearchNode R_IM_003 = reg("R-IM-003", Hk3ResearchType.THEORY, 21.0,
            "hk3gtl.research.r_im_003.name", "hk3gtl.research.r_im_003.effect", "hk3gtl.research.r_im_003.unlock",
            List.of("R-IM-002"), "E-FB-010", null, List.of(
                    req(() -> new ItemStack(ImaginaryCircuitItems.CIRCUIT_IMAGINARY_2.get(), 4), "hk3gtl.research.requirement.imaginary_circuit_2"),
                    req(() -> new ItemStack(HonkaiMaterialItems.EINSTEIN_RINGMAGNET.get(), 24), "hk3gtl.research.requirement.einstein_ringmagnet"),
                    req(() -> new ItemStack(HonkaiMaterialItems.ANCIENT_LEGACY.get(), 12), "hk3gtl.research.requirement.ancient_legacy"),
                    req(() -> new ItemStack(HonkaiMaterialItems.ADVANCED_GAZE_BUFFER_UNIT.get(), 4), "hk3gtl.research.requirement.advanced_gaze_buffer_unit")
            ));

    /** R-IM-004: 虚数 IV 锚定与量子入口门控 */
    public static final Hk3ResearchNode R_IM_004 = reg("R-IM-004", Hk3ResearchType.CERTIFICATION, 22.0,
            "hk3gtl.research.r_im_004.name", "hk3gtl.research.r_im_004.effect", "hk3gtl.research.r_im_004.unlock",
            List.of("R-IM-003"), "E-FB-011", null, List.of(
                    req(() -> new ItemStack(ImaginaryCircuitItems.CIRCUIT_IMAGINARY_3.get(), 4), "hk3gtl.research.requirement.imaginary_circuit_3"),
                    req(() -> new ItemStack(HonkaiMaterialItems.ANCIENT_WILL.get(), 16), "hk3gtl.research.requirement.ancient_will"),
                    req(() -> new ItemStack(HonkaiMaterialItems.FLUID_ALLOY_BLOCK.get(), 24), "hk3gtl.research.requirement.fluid_alloy_block"),
                    req(() -> new ItemStack(HonkaiMaterialItems.WORLD_BUBBLE_SAMPLE.get(), 2), "hk3gtl.research.requirement.world_bubble_sample")
            ));

    // ══════════════════════════════════════
    //  虚数细分节点 R-IM-005~022（设计文档 22 节点的扩展层，
    //  R-IM-001~004 已承担电路主线，本组补充部件 / 阶段细节 / 出口认证）
    // ══════════════════════════════════════

    /** R-IM-005: 虚数 I 部件工程 */
    public static final Hk3ResearchNode R_IM_005 = reg("R-IM-005", Hk3ResearchType.STRUCTURE, 19.2,
            "hk3gtl.research.r_im_005.name", "hk3gtl.research.r_im_005.effect", "hk3gtl.research.r_im_005.unlock",
            List.of("R-IM-001"), "E-FB-009", null, List.of(
                    req(() -> new ItemStack(HonkaiMaterialItems.WORLD_BUBBLE_SAMPLE.get(), 1), "hk3gtl.research.requirement.world_bubble_sample"),
                    req(() -> ChemicalHelper.get(TagPrefix.plate, SouliumMaterial.SOULIUM, 16), "hk3gtl.research.requirement.soulium_plate"),
                    req(() -> new ItemStack(HonkaiMaterialItems.NANO_CERAMIC.get(), 8), "hk3gtl.research.requirement.nano_ceramic")
            ));

    /** R-IM-006: 前文明数据解析 II — 解锁前文明数据库解码塔深度研究 */
    public static final Hk3ResearchNode R_IM_006 = reg("R-IM-006", Hk3ResearchType.THEORY, 19.4,
            "hk3gtl.research.r_im_006.name", "hk3gtl.research.r_im_006.effect", "hk3gtl.research.r_im_006.unlock",
            List.of("R-IM-001"), "E-FB-011", null, List.of(
                    req(() -> new ItemStack(HonkaiMaterialItems.DATA_RESEARCH_PACKAGE.get(), 16), "hk3gtl.research.requirement.data_research_package"),
                    req(() -> new ItemStack(AbyssFunctionalItems.ARTIFACT_VOID_ARCHIVES.get(), 1), "hk3gtl.research.requirement.artifact_void_archives")
            ));

    /** R-IM-007: 虚数 II 电压理论 */
    public static final Hk3ResearchNode R_IM_007 = reg("R-IM-007", Hk3ResearchType.VOLTAGE, 19.6,
            "hk3gtl.research.r_im_007.name", "hk3gtl.research.r_im_007.effect", "hk3gtl.research.r_im_007.unlock",
            List.of("R-IM-005"), "E-FB-009", null, List.of(
                    req(() -> new ItemStack(HonkaiMaterialItems.WORLD_BUBBLE_SAMPLE.get(), 2), "hk3gtl.research.requirement.world_bubble_sample"),
                    req(() -> new ItemStack(HonkaiMaterialItems.STABILIZED_HONKAI_CRYSTAL.get(), 8), "hk3gtl.research.requirement.stabilized_honkai_crystal")
            ));

    /** R-IM-008: 虚数 II 部件工程 */
    public static final Hk3ResearchNode R_IM_008 = reg("R-IM-008", Hk3ResearchType.STRUCTURE, 19.8,
            "hk3gtl.research.r_im_008.name", "hk3gtl.research.r_im_008.effect", "hk3gtl.research.r_im_008.unlock",
            List.of("R-IM-007"), "E-FB-009", null, List.of(
                    req(() -> new ItemStack(ImaginaryCircuitItems.CIRCUIT_IMAGINARY_2.get(), 4), "hk3gtl.research.requirement.imaginary_circuit_2"),
                    req(() -> ChemicalHelper.get(TagPrefix.foil, SouliumMaterial.SOULIUM, 32), "hk3gtl.research.requirement.soulium_foil")
            ));

    /** R-IM-009: 魂钢超结构理论 — 解锁魂钢超结构锻造厅深度研究 */
    public static final Hk3ResearchNode R_IM_009 = reg("R-IM-009", Hk3ResearchType.MATERIAL, 20.0,
            "hk3gtl.research.r_im_009.name", "hk3gtl.research.r_im_009.effect", "hk3gtl.research.r_im_009.unlock",
            List.of("R-IM-007"), "E-FB-032", null, List.of(
                    req(() -> new ItemStack(HonkaiMaterialItems.ANCIENT_WILL.get(), 4), "hk3gtl.research.requirement.ancient_will"),
                    req(() -> new ItemStack(HonkaiMaterialItems.FLUID_ALLOY_BLOCK.get(), 8), "hk3gtl.research.requirement.fluid_alloy_block"),
                    req(() -> ChemicalHelper.get(TagPrefix.frameGt, SouliumMaterial.SOULIUM, 8), "hk3gtl.research.requirement.soulium_frame")
            ));

    /** R-IM-010: 文明交流高级协议 */
    public static final Hk3ResearchNode R_IM_010 = reg("R-IM-010", Hk3ResearchType.CERTIFICATION, 20.2,
            "hk3gtl.research.r_im_010.name", "hk3gtl.research.r_im_010.effect", "hk3gtl.research.r_im_010.unlock",
            List.of("R-IM-007"), "E-FB-004", null, List.of(
                    req(() -> new ItemStack(HonkaiMaterialItems.ANCIENT_LEGACY.get(), 8), "hk3gtl.research.requirement.ancient_legacy"),
                    req(() -> new ItemStack(HonkaiMaterialItems.FLUID_ALLOY_BLOCK.get(), 8), "hk3gtl.research.requirement.fluid_alloy_block"),
                    req(() -> new ItemStack(HonkaiMaterialItems.DATA_RESEARCH_PACKAGE.get(), 16), "hk3gtl.research.requirement.data_research_package")
            ));

    /** R-IM-011: 虚数 III 电压理论 */
    public static final Hk3ResearchNode R_IM_011 = reg("R-IM-011", Hk3ResearchType.VOLTAGE, 20.4,
            "hk3gtl.research.r_im_011.name", "hk3gtl.research.r_im_011.effect", "hk3gtl.research.r_im_011.unlock",
            List.of("R-IM-007"), "E-FB-009", null, List.of(
                    req(() -> new ItemStack(HonkaiMaterialItems.FLUID_ALLOY_BLOCK.get(), 8), "hk3gtl.research.requirement.fluid_alloy_block"),
                    req(() -> new ItemStack(HonkaiMaterialItems.ADVANCED_GAZE_BUFFER_UNIT.get(), 4), "hk3gtl.research.requirement.advanced_gaze_buffer_unit")
            ));

    /** R-IM-012: 虚数 III 部件工程 */
    public static final Hk3ResearchNode R_IM_012 = reg("R-IM-012", Hk3ResearchType.STRUCTURE, 20.6,
            "hk3gtl.research.r_im_012.name", "hk3gtl.research.r_im_012.effect", "hk3gtl.research.r_im_012.unlock",
            List.of("R-IM-011"), "E-FB-009", null, List.of(
                    req(() -> new ItemStack(HonkaiMaterialItems.SUPERCONDUCTIVE_METAL_HYDROGEN.get(), 16), "hk3gtl.research.requirement.superconductive_metal_hydrogen"),
                    req(() -> new ItemStack(HonkaiMaterialItems.NANO_CERAMIC.get(), 16), "hk3gtl.research.requirement.nano_ceramic"),
                    req(() -> ChemicalHelper.get(TagPrefix.frameGt, SouliumMaterial.SOULIUM, 16), "hk3gtl.research.requirement.soulium_frame")
            ));

    /** R-IM-013: 世界泡稳相理论 */
    public static final Hk3ResearchNode R_IM_013 = reg("R-IM-013", Hk3ResearchType.THEORY, 20.8,
            "hk3gtl.research.r_im_013.name", "hk3gtl.research.r_im_013.effect", "hk3gtl.research.r_im_013.unlock",
            List.of("R-IM-011"), "E-FB-008", null, List.of(
                    req(() -> new ItemStack(HonkaiMaterialItems.WORLD_BUBBLE_SAMPLE.get(), 4), "hk3gtl.research.requirement.world_bubble_sample"),
                    req(() -> new ItemStack(HonkaiMaterialItems.STABILIZED_HONKAI_CRYSTAL.get(), 32), "hk3gtl.research.requirement.stabilized_honkai_crystal")
            ));

    /** R-IM-014: 虚数物质编织学 — 解锁虚数物质编织机深度配方 */
    public static final Hk3ResearchNode R_IM_014 = reg("R-IM-014", Hk3ResearchType.MATERIAL, 21.0,
            "hk3gtl.research.r_im_014.name", "hk3gtl.research.r_im_014.effect", "hk3gtl.research.r_im_014.unlock",
            List.of("R-IM-011"), "E-FB-035", null, List.of(
                    req(() -> new ItemStack(ImaginaryCircuitItems.CIRCUIT_IMAGINARY_3.get(), 4), "hk3gtl.research.requirement.imaginary_circuit_3"),
                    req(() -> new ItemStack(HonkaiMaterialItems.FLUID_ALLOY_BLOCK.get(), 16), "hk3gtl.research.requirement.fluid_alloy_block"),
                    req(() -> new ItemStack(HonkaiMaterialItems.PHASE_TRANSFER_MIRROR.get(), 8), "hk3gtl.research.requirement.phase_transfer_mirror")
            ));

    /** R-IM-015: 虚数 IV 电压理论 */
    public static final Hk3ResearchNode R_IM_015 = reg("R-IM-015", Hk3ResearchType.VOLTAGE, 21.2,
            "hk3gtl.research.r_im_015.name", "hk3gtl.research.r_im_015.effect", "hk3gtl.research.r_im_015.unlock",
            List.of("R-IM-011"), "E-FB-009", null, List.of(
                    req(() -> new ItemStack(ImaginaryCircuitItems.CIRCUIT_IMAGINARY_3.get(), 16), "hk3gtl.research.requirement.imaginary_circuit_3"),
                    req(() -> new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 16), "hk3gtl.research.requirement.compressed_honkai_core")
            ));

    /** R-IM-016: 虚数 IV 部件工程 */
    public static final Hk3ResearchNode R_IM_016 = reg("R-IM-016", Hk3ResearchType.STRUCTURE, 21.4,
            "hk3gtl.research.r_im_016.name", "hk3gtl.research.r_im_016.effect", "hk3gtl.research.r_im_016.unlock",
            List.of("R-IM-015"), "E-FB-009", null, List.of(
                    req(() -> new ItemStack(ImaginaryCircuitItems.CIRCUIT_IMAGINARY_4.get(), 4), "hk3gtl.research.requirement.imaginary_circuit_4"),
                    req(() -> ChemicalHelper.get(TagPrefix.frameGt, SouliumMaterial.SOULIUM, 32), "hk3gtl.research.requirement.soulium_frame")
            ));

    /** R-IM-017: 瓦尔特馈赠确认 — 自动完成（事件 E-WL-001） */
    public static final Hk3ResearchNode R_IM_017 = reg("R-IM-017", Hk3ResearchType.EVENT, 21.4,
            "hk3gtl.research.r_im_017.name", "hk3gtl.research.r_im_017.effect", "hk3gtl.research.r_im_017.unlock",
            List.of("R-IM-001"), null, "E-WL-001", List.of());

    /** R-IM-018: 理构电路重组原理 — 进一步加固崩坏能电路板配方 */
    public static final Hk3ResearchNode R_IM_018 = reg("R-IM-018", Hk3ResearchType.THEORY, 21.6,
            "hk3gtl.research.r_im_018.name", "hk3gtl.research.r_im_018.effect", "hk3gtl.research.r_im_018.unlock",
            List.of("R-IM-017"), "E-FB-023", null, List.of(
                    req(() -> new ItemStack(ImaginaryCircuitItems.CIRCUIT_IMAGINARY_4.get(), 2), "hk3gtl.research.requirement.imaginary_circuit_4"),
                    req(() -> new ItemStack(HonkaiMaterialItems.ANCIENT_WILL.get(), 8), "hk3gtl.research.requirement.ancient_will")
            ));

    /** R-IM-019: 虚数理论实验 */
    public static final Hk3ResearchNode R_IM_019 = reg("R-IM-019", Hk3ResearchType.THEORY, 21.8,
            "hk3gtl.research.r_im_019.name", "hk3gtl.research.r_im_019.effect", "hk3gtl.research.r_im_019.unlock",
            List.of("R-IM-016"), "E-FB-009", null, List.of(
                    req(() -> new ItemStack(ImaginaryCircuitItems.CIRCUIT_IMAGINARY_4.get(), 4), "hk3gtl.research.requirement.imaginary_circuit_4"),
                    req(() -> new ItemStack(HonkaiMaterialItems.EINSTEIN_RINGMAGNET.get(), 16), "hk3gtl.research.requirement.einstein_ringmagnet"),
                    req(() -> new ItemStack(HonkaiMaterialItems.ADVANCED_GAZE_BUFFER_UNIT.get(), 8), "hk3gtl.research.requirement.advanced_gaze_buffer_unit")
            ));

    /** R-IM-020: 文明档案建立 */
    public static final Hk3ResearchNode R_IM_020 = reg("R-IM-020", Hk3ResearchType.CERTIFICATION, 22.0,
            "hk3gtl.research.r_im_020.name", "hk3gtl.research.r_im_020.effect", "hk3gtl.research.r_im_020.unlock",
            List.of("R-IM-010", "R-IM-013"), "E-FB-004", null, List.of(
                    req(() -> new ItemStack(HonkaiMaterialItems.DATA_RESEARCH_PACKAGE.get(), 32), "hk3gtl.research.requirement.data_research_package"),
                    req(() -> new ItemStack(HonkaiMaterialItems.WORLD_BUBBLE_SAMPLE.get(), 2), "hk3gtl.research.requirement.world_bubble_sample"),
                    req(() -> new ItemStack(ImaginaryCircuitItems.CIRCUIT_IMAGINARY_2.get(), 8), "hk3gtl.research.requirement.imaginary_circuit_2")
            ));

    /** R-IM-021: 虚数阶段出口认证 — 毕业必需 */
    public static final Hk3ResearchNode R_IM_021 = reg("R-IM-021", Hk3ResearchType.CERTIFICATION, 22.2,
            "hk3gtl.research.r_im_021.name", "hk3gtl.research.r_im_021.effect", "hk3gtl.research.r_im_021.unlock",
            List.of("R-IM-016", "R-IM-017", "R-IM-020"), "E-FB-009", null, List.of(
                    req(() -> new ItemStack(ImaginaryCircuitItems.CIRCUIT_IMAGINARY_4.get(), 8), "hk3gtl.research.requirement.imaginary_circuit_4"),
                    req(() -> new ItemStack(HonkaiMaterialItems.WORLD_BUBBLE_SAMPLE.get(), 4), "hk3gtl.research.requirement.world_bubble_sample"),
                    req(() -> new ItemStack(HonkaiMaterialItems.ANCIENT_WILL.get(), 16), "hk3gtl.research.requirement.ancient_will")
            ));

    /** R-IM-022: 跨维通讯理论 */
    public static final Hk3ResearchNode R_IM_022 = reg("R-IM-022", Hk3ResearchType.THEORY, 22.4,
            "hk3gtl.research.r_im_022.name", "hk3gtl.research.r_im_022.effect", "hk3gtl.research.r_im_022.unlock",
            List.of("R-IM-021"), "E-FB-004", null, List.of(
                    req(() -> new ItemStack(ImaginaryCircuitItems.CIRCUIT_IMAGINARY_4.get(), 4), "hk3gtl.research.requirement.imaginary_circuit_4"),
                    req(() -> new ItemStack(HonkaiMaterialItems.ANCIENT_WILL.get(), 8), "hk3gtl.research.requirement.ancient_will")
            ));

    // ══════════════════════════════════════
    //  v0.3 新增：量子 / 终焉 / 毕业校验节点（用于 60 台主线闭环）
    //  说明：这些节点当前先以“流程门控”为主，后续可按阶段补充提交物。
    // ══════════════════════════════════════

    /** R-QT-001: 量子基础理论 — 需虚数出口认证（R-IM-021）+ 量子纠缠计算机已建成 */
    public static final Hk3ResearchNode R_QT_001 = reg("R-QT-001", Hk3ResearchType.THEORY, 22.6,
            "hk3gtl.research.r_qt_001.name", "hk3gtl.research.r_qt_001.effect", "hk3gtl.research.r_qt_001.unlock",
            List.of("R-IM-021"), "E-FB-012", null, List.of(
                    req(() -> new ItemStack(ImaginaryCircuitItems.CIRCUIT_IMAGINARY_4.get(), 8), "hk3gtl.research.requirement.imaginary_circuit_4"),
                    req(() -> new ItemStack(HonkaiMaterialItems.WORLD_BUBBLE_SAMPLE.get(), 2), "hk3gtl.research.requirement.world_bubble_sample"),
                    req(() -> new ItemStack(HonkaiMaterialItems.SUPERCONDUCTIVE_METAL_HYDROGEN.get(), 16), "hk3gtl.research.requirement.superconductive_metal_hydrogen")
            ));

    /** R-QT-002: 量子 I 电压理论 */
    public static final Hk3ResearchNode R_QT_002 = reg("R-QT-002", Hk3ResearchType.VOLTAGE, 22.8,
            "hk3gtl.research.r_qt_002.name", "hk3gtl.research.r_qt_002.effect", "hk3gtl.research.r_qt_002.unlock",
            List.of("R-QT-001"), "E-FB-012", null, List.of(
                    req(() -> new ItemStack(ImaginaryCircuitItems.CIRCUIT_IMAGINARY_4.get(), 16), "hk3gtl.research.requirement.imaginary_circuit_4"),
                    req(() -> new ItemStack(HonkaiMaterialItems.SUPERCONDUCTIVE_METAL_HYDROGEN.get(), 32), "hk3gtl.research.requirement.superconductive_metal_hydrogen")
            ));

    /** R-QT-003: 量子 I 电路设计 */
    public static final Hk3ResearchNode R_QT_003 = reg("R-QT-003", Hk3ResearchType.CIRCUIT, 23.0,
            "hk3gtl.research.r_qt_003.name", "hk3gtl.research.r_qt_003.effect", "hk3gtl.research.r_qt_003.unlock",
            List.of("R-QT-002"), "E-FB-012", null, List.of(
                    req(() -> new ItemStack(QuantumCircuitItems.CIRCUIT_QUANTUM_1.get(), 4), "hk3gtl.research.requirement.quantum_circuit_1"),
                    req(() -> new ItemStack(HonkaiMaterialItems.SUPERCONDUCTIVE_METAL_HYDROGEN.get(), 16), "hk3gtl.research.requirement.superconductive_metal_hydrogen")
            ));

    /** R-QT-004: 量子纠缠计算原理 — 解锁量子纠缠计算机正式研究 */
    public static final Hk3ResearchNode R_QT_004 = reg("R-QT-004", Hk3ResearchType.THEORY, 23.2,
            "hk3gtl.research.r_qt_004.name", "hk3gtl.research.r_qt_004.effect", "hk3gtl.research.r_qt_004.unlock",
            List.of("R-QT-001"), "E-FB-012", null, List.of(
                    req(() -> new ItemStack(HonkaiMaterialItems.EINSTEIN_RINGMAGNET.get(), 16), "hk3gtl.research.requirement.einstein_ringmagnet"),
                    req(() -> new ItemStack(HonkaiMaterialItems.PHASE_TRANSFER_MIRROR.get(), 16), "hk3gtl.research.requirement.phase_transfer_mirror"),
                    req(() -> new ItemStack(QuantumCircuitItems.CIRCUIT_QUANTUM_1.get(), 4), "hk3gtl.research.requirement.quantum_circuit_1")
            ));

    /** R-QT-005: 量子超导晶格学
     *  死锁修复：原 requiredEvent=E-FB-037 由量子超导晶格厂建成触发，而该厂配方门槛正是 R-QT-005 自身，
     *  形成"解锁 R-QT-005 需先建厂、建厂又需先解锁 R-QT-005"自锁。改用量子阶段入口事件 E-FB-012
     *  （量子纠缠计算机建成，已是可达锚点），解除自锁。 */
    public static final Hk3ResearchNode R_QT_005 = reg("R-QT-005", Hk3ResearchType.MATERIAL, 23.4,
            "hk3gtl.research.r_qt_005.name", "hk3gtl.research.r_qt_005.effect", "hk3gtl.research.r_qt_005.unlock",
            List.of("R-QT-004"), "E-FB-012", null, List.of(
                    req(() -> new ItemStack(QuantumCircuitItems.CIRCUIT_QUANTUM_1.get(), 8), "hk3gtl.research.requirement.quantum_circuit_1"),
                    req(() -> new ItemStack(HonkaiMaterialItems.SUPERCONDUCTIVE_METAL_HYDROGEN.get(), 64), "hk3gtl.research.requirement.superconductive_metal_hydrogen")
            ));

    /** R-QT-006: 千界一乘设计理论 — 解锁千界一乘建造 */
    public static final Hk3ResearchNode R_QT_006 = reg("R-QT-006", Hk3ResearchType.STRUCTURE, 23.6,
            "hk3gtl.research.r_qt_006.name", "hk3gtl.research.r_qt_006.effect", "hk3gtl.research.r_qt_006.unlock",
            List.of("R-QT-004"), "E-FB-012", null, List.of(
                    req(() -> new ItemStack(QuantumCircuitItems.CIRCUIT_QUANTUM_1.get(), 16), "hk3gtl.research.requirement.quantum_circuit_1"),
                    req(() -> new ItemStack(HonkaiMaterialItems.WORLD_BUBBLE_SAMPLE.get(), 8), "hk3gtl.research.requirement.world_bubble_sample"),
                    req(() -> ChemicalHelper.get(TagPrefix.frameGt, SouliumMaterial.SOULIUM, 32), "hk3gtl.research.requirement.soulium_frame")
            ));

    /** R-QT-007: 量子 II 电压理论 */
    public static final Hk3ResearchNode R_QT_007 = reg("R-QT-007", Hk3ResearchType.VOLTAGE, 23.8,
            "hk3gtl.research.r_qt_007.name", "hk3gtl.research.r_qt_007.effect", "hk3gtl.research.r_qt_007.unlock",
            List.of("R-QT-002"), "E-FB-012", null, List.of(
                    req(() -> new ItemStack(QuantumCircuitItems.CIRCUIT_QUANTUM_1.get(), 16), "hk3gtl.research.requirement.quantum_circuit_1"),
                    req(() -> new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 16), "hk3gtl.research.requirement.compressed_honkai_core")
            ));

    /** R-QT-008: 量子 II 电路设计 */
    public static final Hk3ResearchNode R_QT_008 = reg("R-QT-008", Hk3ResearchType.CIRCUIT, 24.0,
            "hk3gtl.research.r_qt_008.name", "hk3gtl.research.r_qt_008.effect", "hk3gtl.research.r_qt_008.unlock",
            List.of("R-QT-007"), "E-FB-012", null, List.of(
                    req(() -> new ItemStack(QuantumCircuitItems.CIRCUIT_QUANTUM_2.get(), 4), "hk3gtl.research.requirement.quantum_circuit_2"),
                    req(() -> new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 32), "hk3gtl.research.requirement.compressed_honkai_core")
            ));

    /** R-QT-009: 文明认证理论
     *  死锁修复：原 requiredEvent=E-FB-043 由量子文明贸易港建成触发，而该港配方门槛正是 R-QT-009 自身，
     *  且 R-QT-009 又是量子出口认证 R-QT-012 的前置之一，自锁会直接阻断毕业。改用量子阶段入口事件
     *  E-FB-012（可达锚点），解除自锁。 */
    public static final Hk3ResearchNode R_QT_009 = reg("R-QT-009", Hk3ResearchType.CERTIFICATION, 24.2,
            "hk3gtl.research.r_qt_009.name", "hk3gtl.research.r_qt_009.effect", "hk3gtl.research.r_qt_009.unlock",
            List.of("R-QT-008"), "E-FB-012", null, List.of(
                    req(() -> new ItemStack(QuantumCircuitItems.CIRCUIT_QUANTUM_2.get(), 8), "hk3gtl.research.requirement.quantum_circuit_2"),
                    req(() -> new ItemStack(HonkaiMaterialItems.DATA_RESEARCH_PACKAGE.get(), 64), "hk3gtl.research.requirement.data_research_package")
            ));

    /** R-QT-010: 量子 III 电压理论 */
    public static final Hk3ResearchNode R_QT_010 = reg("R-QT-010", Hk3ResearchType.VOLTAGE, 24.4,
            "hk3gtl.research.r_qt_010.name", "hk3gtl.research.r_qt_010.effect", "hk3gtl.research.r_qt_010.unlock",
            List.of("R-QT-007"), "E-FB-012", null, List.of(
                    req(() -> new ItemStack(QuantumCircuitItems.CIRCUIT_QUANTUM_2.get(), 16), "hk3gtl.research.requirement.quantum_circuit_2"),
                    req(() -> new ItemStack(HonkaiMaterialItems.ADVANCED_GAZE_BUFFER_UNIT.get(), 16), "hk3gtl.research.requirement.advanced_gaze_buffer_unit")
            ));

    /** R-QT-011: 量子 IV 电压理论 */
    public static final Hk3ResearchNode R_QT_011 = reg("R-QT-011", Hk3ResearchType.VOLTAGE, 24.6,
            "hk3gtl.research.r_qt_011.name", "hk3gtl.research.r_qt_011.effect", "hk3gtl.research.r_qt_011.unlock",
            List.of("R-QT-010"), "E-FB-012", null, List.of(
                    req(() -> new ItemStack(QuantumCircuitItems.CIRCUIT_QUANTUM_3.get(), 16), "hk3gtl.research.requirement.quantum_circuit_3"),
                    req(() -> new ItemStack(HonkaiMaterialItems.ADVANCED_GAZE_BUFFER_UNIT.get(), 32), "hk3gtl.research.requirement.advanced_gaze_buffer_unit")
            ));

    /** R-QT-012: 量子阶段出口认证 — 毕业必需 */
    public static final Hk3ResearchNode R_QT_012 = reg("R-QT-012", Hk3ResearchType.CERTIFICATION, 24.8,
            "hk3gtl.research.r_qt_012.name", "hk3gtl.research.r_qt_012.effect", "hk3gtl.research.r_qt_012.unlock",
            List.of("R-QT-011", "R-QT-006", "R-QT-009"), "E-FB-012", null, List.of(
                    req(() -> new ItemStack(QuantumCircuitItems.CIRCUIT_QUANTUM_4.get(), 8), "hk3gtl.research.requirement.quantum_circuit_4"),
                    req(() -> new ItemStack(HonkaiMaterialItems.WORLD_BUBBLE_SAMPLE.get(), 8), "hk3gtl.research.requirement.world_bubble_sample"),
                    req(() -> new ItemStack(HonkaiMaterialItems.ANCIENT_WILL.get(), 16), "hk3gtl.research.requirement.ancient_will")
            ));

    /** R-FN-001: 终焉基础理论 — 需量子出口 + 千界一乘建成事件 */
    public static final Hk3ResearchNode R_FN_001 = reg("R-FN-001", Hk3ResearchType.THEORY, 25.0,
            "hk3gtl.research.r_fn_001.name", "hk3gtl.research.r_fn_001.effect", "hk3gtl.research.r_fn_001.unlock",
            List.of("R-QT-012"), "E-FB-013", null, List.of(
                    req(() -> new ItemStack(QuantumCircuitItems.CIRCUIT_QUANTUM_4.get(), 16), "hk3gtl.research.requirement.quantum_circuit_4"),
                    req(() -> new ItemStack(HonkaiMaterialItems.ANCIENT_WILL.get(), 32), "hk3gtl.research.requirement.ancient_will")
            ));

    /** R-FN-002: 休伯利安号设计蓝图 */
    public static final Hk3ResearchNode R_FN_002 = reg("R-FN-002", Hk3ResearchType.STRUCTURE, 25.2,
            "hk3gtl.research.r_fn_002.name", "hk3gtl.research.r_fn_002.effect", "hk3gtl.research.r_fn_002.unlock",
            List.of("R-FN-001"), "E-FB-013", null, List.of(
                    req(() -> new ItemStack(QuantumCircuitItems.CIRCUIT_QUANTUM_4.get(), 16), "hk3gtl.research.requirement.quantum_circuit_4"),
                    req(() -> new ItemStack(HonkaiMaterialItems.WORLD_BUBBLE_SAMPLE.get(), 16), "hk3gtl.research.requirement.world_bubble_sample"),
                    req(() -> ChemicalHelper.get(TagPrefix.frameGt, SouliumMaterial.SOULIUM, 64), "hk3gtl.research.requirement.soulium_frame")
            ));

    /** R-FN-003: 舰载扩展协调协议 — 休伯利安号建成（E-FB-015）后开启 */
    public static final Hk3ResearchNode R_FN_003 = reg("R-FN-003", Hk3ResearchType.STRUCTURE, 25.4,
            "hk3gtl.research.r_fn_003.name", "hk3gtl.research.r_fn_003.effect", "hk3gtl.research.r_fn_003.unlock",
            List.of("R-FN-002"), "E-FB-015", null, List.of(
                    req(() -> new ItemStack(FinalityCircuitItems.CIRCUIT_FINALITY_1.get(), 4), "hk3gtl.research.requirement.finality_circuit_1"),
                    req(() -> new ItemStack(HonkaiMaterialItems.ANCIENT_WILL.get(), 16), "hk3gtl.research.requirement.ancient_will")
            ));

    /** R-FN-004: 终焉能源总站理论 */
    public static final Hk3ResearchNode R_FN_004 = reg("R-FN-004", Hk3ResearchType.THEORY, 25.6,
            "hk3gtl.research.r_fn_004.name", "hk3gtl.research.r_fn_004.effect", "hk3gtl.research.r_fn_004.unlock",
            List.of("R-FN-003"), "E-FB-013", null, List.of(
                    req(() -> new ItemStack(FinalityCircuitItems.CIRCUIT_FINALITY_1.get(), 8), "hk3gtl.research.requirement.finality_circuit_1"),
                    req(() -> new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 32), "hk3gtl.research.requirement.compressed_honkai_core")
            ));

    /** R-FN-005: 终焉材料终锻理论 */
    public static final Hk3ResearchNode R_FN_005 = reg("R-FN-005", Hk3ResearchType.MATERIAL, 25.8,
            "hk3gtl.research.r_fn_005.name", "hk3gtl.research.r_fn_005.effect", "hk3gtl.research.r_fn_005.unlock",
            List.of("R-FN-004"), "E-FB-054", null, List.of(
                    req(() -> new ItemStack(FinalityCircuitItems.CIRCUIT_FINALITY_2.get(), 4), "hk3gtl.research.requirement.finality_circuit_2"),
                    req(() -> new ItemStack(HonkaiMaterialItems.ANCIENT_WILL.get(), 32), "hk3gtl.research.requirement.ancient_will")
            ));

    /** R-FN-006: 终焉湮灭反应理论 */
    public static final Hk3ResearchNode R_FN_006 = reg("R-FN-006", Hk3ResearchType.THEORY, 26.0,
            "hk3gtl.research.r_fn_006.name", "hk3gtl.research.r_fn_006.effect", "hk3gtl.research.r_fn_006.unlock",
            List.of("R-FN-005"), "E-FB-020", null, List.of(
                    req(() -> new ItemStack(FinalityCircuitItems.CIRCUIT_FINALITY_2.get(), 8), "hk3gtl.research.requirement.finality_circuit_2"),
                    req(() -> new ItemStack(HonkaiMaterialItems.COMPRESSED_HONKAI_CORE.get(), 64), "hk3gtl.research.requirement.compressed_honkai_core")
            ));

    /** R-FN-007: 文明验证矩阵理论 */
    public static final Hk3ResearchNode R_FN_007 = reg("R-FN-007", Hk3ResearchType.CERTIFICATION, 26.2,
            "hk3gtl.research.r_fn_007.name", "hk3gtl.research.r_fn_007.effect", "hk3gtl.research.r_fn_007.unlock",
            List.of("R-FN-006"), "E-FB-016", null, List.of(
                    req(() -> new ItemStack(FinalityCircuitItems.CIRCUIT_FINALITY_3.get(), 4), "hk3gtl.research.requirement.finality_circuit_3"),
                    req(() -> new ItemStack(HonkaiMaterialItems.DATA_RESEARCH_PACKAGE.get(), 64), "hk3gtl.research.requirement.data_research_package")
            ));

    /** R-FN-008: 奇观总控网络理论 */
    public static final Hk3ResearchNode R_FN_008 = reg("R-FN-008", Hk3ResearchType.CERTIFICATION, 26.4,
            "hk3gtl.research.r_fn_008.name", "hk3gtl.research.r_fn_008.effect", "hk3gtl.research.r_fn_008.unlock",
            List.of("R-FN-007"), "E-FB-018", null, List.of(
                    req(() -> new ItemStack(FinalityCircuitItems.CIRCUIT_FINALITY_3.get(), 8), "hk3gtl.research.requirement.finality_circuit_3"),
                    req(() -> new ItemStack(HonkaiMaterialItems.ANCIENT_WILL.get(), 32), "hk3gtl.research.requirement.ancient_will")
            ));

    /** R-FN-009: 毕业权限校验理论 */
    public static final Hk3ResearchNode R_FN_009 = reg("R-FN-009", Hk3ResearchType.CERTIFICATION, 26.6,
            "hk3gtl.research.r_fn_009.name", "hk3gtl.research.r_fn_009.effect", "hk3gtl.research.r_fn_009.unlock",
            List.of("R-FN-008"), "E-FB-055", null, List.of(
                    req(() -> new ItemStack(FinalityCircuitItems.CIRCUIT_FINALITY_4.get(), 4), "hk3gtl.research.requirement.finality_circuit_4"),
                    req(() -> new ItemStack(HonkaiMaterialItems.DATA_RESEARCH_PACKAGE.get(), 128), "hk3gtl.research.requirement.data_research_package")
            ));

    /** R-FN-010: 终焉 I 电压理论 */
    public static final Hk3ResearchNode R_FN_010 = reg("R-FN-010", Hk3ResearchType.VOLTAGE, 26.8,
            "hk3gtl.research.r_fn_010.name", "hk3gtl.research.r_fn_010.effect", "hk3gtl.research.r_fn_010.unlock",
            List.of("R-FN-001"), "E-FB-013", null, List.of(
                    req(() -> new ItemStack(QuantumCircuitItems.CIRCUIT_QUANTUM_4.get(), 16), "hk3gtl.research.requirement.quantum_circuit_4"),
                    req(() -> new ItemStack(FinalityCircuitItems.CIRCUIT_FINALITY_1.get(), 4), "hk3gtl.research.requirement.finality_circuit_1")
            ));

    /** R-FN-011: 终焉 II 电路设计 */
    public static final Hk3ResearchNode R_FN_011 = reg("R-FN-011", Hk3ResearchType.CIRCUIT, 27.0,
            "hk3gtl.research.r_fn_011.name", "hk3gtl.research.r_fn_011.effect", "hk3gtl.research.r_fn_011.unlock",
            List.of("R-FN-010"), "E-FB-013", null, List.of(
                    req(() -> new ItemStack(FinalityCircuitItems.CIRCUIT_FINALITY_2.get(), 8), "hk3gtl.research.requirement.finality_circuit_2"),
                    req(() -> new ItemStack(HonkaiMaterialItems.ANCIENT_WILL.get(), 32), "hk3gtl.research.requirement.ancient_will")
            ));

    /** R-FN-012: 终焉阶段出口认证 — 毕业必需 */
    public static final Hk3ResearchNode R_FN_012 = reg("R-FN-012", Hk3ResearchType.CERTIFICATION, 27.2,
            "hk3gtl.research.r_fn_012.name", "hk3gtl.research.r_fn_012.effect", "hk3gtl.research.r_fn_012.unlock",
            List.of("R-FN-007", "R-FN-008", "R-FN-009"), "E-FB-013", null, List.of(
                    req(() -> new ItemStack(FinalityCircuitItems.CIRCUIT_FINALITY_4.get(), 8), "hk3gtl.research.requirement.finality_circuit_4"),
                    req(() -> new ItemStack(HonkaiMaterialItems.WORLD_BUBBLE_SAMPLE.get(), 16), "hk3gtl.research.requirement.world_bubble_sample"),
                    req(() -> new ItemStack(HonkaiMaterialItems.ANCIENT_WILL.get(), 64), "hk3gtl.research.requirement.ancient_will")
            ));

    /** R-GR-001: 奇观网络完整性校验 — 验证矩阵已成型 */
    public static final Hk3ResearchNode R_GR_001 = reg("R-GR-001", Hk3ResearchType.CERTIFICATION, 27.4,
            "hk3gtl.research.r_gr_001.name", "hk3gtl.research.r_gr_001.effect", "hk3gtl.research.r_gr_001.unlock",
            List.of("R-FN-012"), "E-FB-016", null, List.of(
                    req(() -> new ItemStack(FinalityCircuitItems.CIRCUIT_FINALITY_4.get(), 16), "hk3gtl.research.requirement.finality_circuit_4")
            ));

    /** R-GR-002: 研究完整性校验 */
    public static final Hk3ResearchNode R_GR_002 = reg("R-GR-002", Hk3ResearchType.CERTIFICATION, 27.5,
            "hk3gtl.research.r_gr_002.name", "hk3gtl.research.r_gr_002.effect", "hk3gtl.research.r_gr_002.unlock",
            List.of("R-GR-001"), "E-FB-016", null, List.of(
                    req(() -> new ItemStack(HonkaiMaterialItems.DATA_RESEARCH_PACKAGE.get(), 256), "hk3gtl.research.requirement.data_research_package")
            ));

    /** R-GR-003: 事件完整性校验 */
    public static final Hk3ResearchNode R_GR_003 = reg("R-GR-003", Hk3ResearchType.CERTIFICATION, 27.6,
            "hk3gtl.research.r_gr_003.name", "hk3gtl.research.r_gr_003.effect", "hk3gtl.research.r_gr_003.unlock",
            List.of("R-GR-002"), "E-FB-016", null, List.of(
                    req(() -> new ItemStack(HonkaiMaterialItems.ANCIENT_LEGACY.get(), 32), "hk3gtl.research.requirement.ancient_legacy")
            ));

    /** R-GR-004: 文明交流完整性校验 */
    public static final Hk3ResearchNode R_GR_004 = reg("R-GR-004", Hk3ResearchType.CERTIFICATION, 27.7,
            "hk3gtl.research.r_gr_004.name", "hk3gtl.research.r_gr_004.effect", "hk3gtl.research.r_gr_004.unlock",
            List.of("R-GR-003"), "E-FB-016", null, List.of(
                    alt("hk3gtl.research.requirement.imaginary_core_either",
                            () -> new ItemStack(HonkaiMaterialItems.SCHICKSAL_IMAGINARY_CORE.get(), 32),
                            () -> new ItemStack(HonkaiMaterialItems.ANTI_ENTROPY_IMAGINARY_CORE.get(), 32))
            ));

    /** R-GR-005: 最终毕业许可 */
    public static final Hk3ResearchNode R_GR_005 = reg("R-GR-005", Hk3ResearchType.CERTIFICATION, 27.9,
            "hk3gtl.research.r_gr_005.name", "hk3gtl.research.r_gr_005.effect", "hk3gtl.research.r_gr_005.unlock",
            List.of("R-GR-004"), "E-FB-016", null, List.of(
                    req(() -> new ItemStack(HonkaiMaterialItems.WORLD_BUBBLE_SAMPLE.get(), 16), "hk3gtl.research.requirement.world_bubble_sample"),
                    req(() -> new ItemStack(HonkaiMaterialItems.ANCIENT_WILL.get(), 128), "hk3gtl.research.requirement.ancient_will")
            ));

    // ══════════════════════════════════════
    //  辅助方法（新增/修改节点时使用）
    // ══════════════════════════════════════

    /** 创建提交物需求。sup 返回所需 ItemStack，key 为翻译键（显示在 GUI） */
    private static Hk3ResearchRequirement req(java.util.function.Supplier<ItemStack> sup, String key) {
        return Hk3ResearchRequirement.of(sup, key);
    }

    @SafeVarargs
    private static Hk3ResearchRequirement alt(String key, java.util.function.Supplier<ItemStack>... candidates) {
        return Hk3ResearchRequirement.oneOf(key, candidates);
    }

    /** 注册节点到 NODES 映射表。新增节点复制此调用格式即可 */
    private static Hk3ResearchNode reg(String id, Hk3ResearchType type, double tier,
                                       String nameKey, String effectKey, String unlockKey,
                                       List<String> prereqs, String reqEvent, String autoEvent,
                                       List<Hk3ResearchRequirement> reqs) {
        Hk3ResearchNode node = new Hk3ResearchNode(id, type, tier, nameKey, effectKey, unlockKey,
                prereqs, reqEvent, autoEvent, reqs);
        NODES.put(id, node);
        return node;
    }

    /** 按注册顺序返回所有节点（含自动完成型），供 Manager 遍历 */
    public static Collection<Hk3ResearchNode> ordered() {
        return NODES.values();
    }

    /** 仅返回手动提交型节点，按 ID 排序，供 GUI 列表显示 */
    public static List<Hk3ResearchNode> manualNodes() {
        return NODES.values().stream()
                .filter(Hk3ResearchNode::isManualResearch)
                .sorted(java.util.Comparator.comparing(Hk3ResearchNode::id))
                .collect(Collectors.toList());
    }

    /** 返回所有节点（含自动完成型），按 ID 排序 */
    public static List<Hk3ResearchNode> allNodes() {
        return NODES.values().stream()
                .sorted(java.util.Comparator.comparing(Hk3ResearchNode::id))
                .collect(Collectors.toList());
    }

    /** 按 ID 查询节点，不存在返回 null */
    public static Hk3ResearchNode get(String id) {
        return NODES.get(id);
    }

    /** 已注册节点总数（海渊 25 + 瓦尔特 1 + 虚数 22 + 量子 12 + 终焉 12 + 毕业 5 = 77） */
    public static int totalCount() {
        return NODES.size();
    }

    /** 匹配前缀 "R-XX-NNN " 用于在 GUI / JEI / 聊天提示里剥掉内部编号。 */
    private static final java.util.regex.Pattern RESEARCH_ID_PREFIX =
            java.util.regex.Pattern.compile("^R-[A-Z]+-\\d+\\s+");

    /**
     * 把"R-AB-001 海渊I电压理论"剥成"海渊I电压理论"，供任何"对玩家显示研究名"的位置统一调用。
     * 输入为 null / 空字符串时原样返回。
     */
    public static String stripIdPrefix(String displayName) {
        if (displayName == null || displayName.isEmpty()) return displayName;
        return RESEARCH_ID_PREFIX.matcher(displayName).replaceFirst("");
    }
}
