package com.sirin.hk3gtl.common.recipe;



import com.gregtechceu.gtceu.api.gui.GuiTextures;
import com.gregtechceu.gtceu.api.recipe.GTRecipeType;
import com.gregtechceu.gtceu.api.capability.recipe.IO;
import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import com.gregtechceu.gtceu.common.data.GTSoundEntries;

import org.slf4j.Logger;
import com.mojang.logging.LogUtils;

import static com.lowdragmc.lowdraglib.gui.texture.ProgressTexture.FillDirection.LEFT_TO_RIGHT;

/**
 * 配方类型注册总入口 — P1 + Max起始 + 海渊阶段的 RecipeType。
 *
 * <h3>职责</h3>
 * 定义所有 GT 自定义配方类型（RecipeType），每个配方类型对应一台或多台多方块的配方表。
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>setMaxIOSize(物品输入, 物品输出, 流体输入, 流体输出) 必须与实际配方需求匹配</li>
 *   <li>物品输入至少设为 1（编程电路槽位），否则 JEI 会 AIOOB 崩溃</li>
 *   <li>setEUIO: IN=消耗电力, OUT=产生电力, BOTH=双向</li>
 *   <li>新增配方类型 → 仿照现有格式，ID 全小写下划线，"multiblock" 类别</li>
 *   <li>虚数/量子/终焉/奇观阶段分别在子类中注册</li>
 *   <li>语言文件键格式: "gtceu.配方类型ID"，需同步 zh_cn.json / en_us.json</li>
 * </ul>
 *
 * <h3>子类分布</h3>
 * {@link Hk3RecipeTypesImaginary}(10) → {@link Hk3RecipeTypesQuantum}(12) → {@link Hk3RecipeTypesFinality}(13) → {@link Hk3RecipeTypesWonder}(12)
 */
public class Hk3RecipeTypesImpl {

    private static final Logger LOGGER = LogUtils.getLogger();

    // ════════════════════════════════════════
    //  P1 已有（4个）— 对应 Hk3MachinesImpl 中的 4 台核心机
    // ════════════════════════════════════════

    /** 崩坏能吸收 | IO: 1物入/1物出/0液入/0液出 | EU: IN | 对应机器: HONKAI_ABSORPTION_TOWER */
    public static final GTRecipeType HONKAI_ABSORPTION_RECIPES = GTRecipeTypes.register(
                    "honkai_absorption", "multiblock")
            .setMaxIOSize(1, 1, 0, 0)
            .setEUIO(IO.IN)
            .setProgressBar(GuiTextures.PROGRESS_BAR_ARROW, LEFT_TO_RIGHT)
            .setSound(GTSoundEntries.ELECTROLYZER);

    /** 崩坏能凝结 | IO: 2/2/0/1 | EU: IN | 对应机器: HONKAI_CRYSTAL_CONDENSER */
    public static final GTRecipeType HONKAI_CONDENSATION_RECIPES = GTRecipeTypes.register(
                    "honkai_condensation", "multiblock")
            .setMaxIOSize(2, 2, 0, 1)
            .setEUIO(IO.IN)
            .setProgressBar(GuiTextures.PROGRESS_BAR_ARROW, LEFT_TO_RIGHT)
            .setSound(GTSoundEntries.COOLING);

    /** 魂钢冶炼 | IO: 4/4/1/0 | EU: IN | 对应机器: SOULIUM_SMELTERY */
    public static final GTRecipeType SOULIUM_SMELTING_RECIPES = GTRecipeTypes.register(
                    "soulium_smelting", "multiblock")
            .setMaxIOSize(4, 4, 1, 0)
            .setEUIO(IO.IN)
            .setProgressBar(GuiTextures.PROGRESS_BAR_ARROW, LEFT_TO_RIGHT)
            .setSound(GTSoundEntries.FURNACE);

    /** 海渊研究分析 | IO: 4/1/0/0 | EU: IN | 对应机器: ABYSS_RESEARCH_ANALYSIS_MATRIX + 共享 */
    public static final GTRecipeType ABYSS_RESEARCH_ANALYSIS_RECIPES = GTRecipeTypes.register(
                    "abyss_research_analysis", "multiblock")
            .setMaxIOSize(4, 1, 0, 0)
            .setEUIO(IO.IN)
            .setProgressBar(GuiTextures.PROGRESS_BAR_ARROW, LEFT_TO_RIGHT)
            .setSound(GTSoundEntries.ELECTROLYZER);

    // ════════════════════════════════════════
    //  Max起始阶段新增（12个有 RecipeMap 的）— 对应 Hk3MachinesMaxStage
    //  无 RecipeMap 的机器不在此注册（见文件尾注释）
    // ════════════════════════════════════════

    /** 虚空档案分析 | IO: 4/2/0/0 */
    public static final GTRecipeType VOID_ARCHIVES_ANALYSIS_RECIPES = GTRecipeTypes.register(
                    "void_archives_analysis", "multiblock")
            .setMaxIOSize(4, 2, 0, 0)
            .setEUIO(IO.IN)
            .setProgressBar(GuiTextures.PROGRESS_BAR_ARROW, LEFT_TO_RIGHT)
            .setSound(GTSoundEntries.ELECTROLYZER);

    /** 理性重构 | IO: 4/4/1/1 */
    public static final GTRecipeType REASON_RECONSTRUCTION_RECIPES = GTRecipeTypes.register(
                    "reason_reconstruction", "multiblock")
            .setMaxIOSize(4, 4, 1, 1)
            .setEUIO(IO.IN)
            .setProgressBar(GuiTextures.PROGRESS_BAR_ARROW, LEFT_TO_RIGHT)
            .setSound(GTSoundEntries.ASSEMBLER);

    /** 小型崩坏能反应 | IO: 2/2/1/1 | EU: OUT（发电） */
    public static final GTRecipeType SMALL_HONKAI_REACTION_RECIPES = GTRecipeTypes.register(
                    "small_honkai_reaction", "multiblock")
            .setMaxIOSize(2, 2, 1, 1)
            .setEUIO(IO.OUT)
            .setProgressBar(GuiTextures.PROGRESS_BAR_ARROW, LEFT_TO_RIGHT)
            .setSound(GTSoundEntries.FURNACE);

    /** 中型崩坏能反应 | IO: 3/3/1/1 | EU: OUT（发电） */
    public static final GTRecipeType MEDIUM_HONKAI_REACTION_RECIPES = GTRecipeTypes.register(
                    "medium_honkai_reaction", "multiblock")
            .setMaxIOSize(3, 3, 1, 1)
            .setEUIO(IO.OUT)
            .setProgressBar(GuiTextures.PROGRESS_BAR_ARROW, LEFT_TO_RIGHT)
            .setSound(GTSoundEntries.FURNACE);

    /** 崩坏能-EU转换 | IO: 2/2/1/1 | EU: BOTH（双向转换） */
    public static final GTRecipeType HONKAI_EU_CONVERSION_RECIPES = GTRecipeTypes.register(
                    "honkai_eu_conversion", "multiblock")
            .setMaxIOSize(2, 2, 1, 1)
            .setEUIO(IO.BOTH)
            .setProgressBar(GuiTextures.PROGRESS_BAR_ARROW, LEFT_TO_RIGHT)
            .setSound(GTSoundEntries.ARC);

    /** 崩坏能网络注入 | IO: 2/1/1/0 | EU: IN | 对应机器: HONKAI_NETWORK_INJECTOR（产出为无线网络余额，非物品） */
    public static final GTRecipeType HONKAI_NETWORK_INJECTION_RECIPES = GTRecipeTypes.register(
                    "honkai_network_injection", "multiblock")
            .setMaxIOSize(2, 1, 1, 0)
            .setEUIO(IO.IN)
            .setProgressBar(GuiTextures.PROGRESS_BAR_ARROW, LEFT_TO_RIGHT)
            .setSound(GTSoundEntries.ELECTROLYZER);

    /** 海渊电路铸造 | IO: 6/4/1/0 */
    public static final GTRecipeType ABYSS_CIRCUIT_FOUNDRY_RECIPES = GTRecipeTypes.register(
                    "abyss_circuit_foundry", "multiblock")
            .setMaxIOSize(6, 4, 1, 0)
            .setEUIO(IO.IN)
            .setProgressBar(GuiTextures.PROGRESS_BAR_ARROW, LEFT_TO_RIGHT)
            .setSound(GTSoundEntries.ASSEMBLER);

    /** 海渊机壳压制 | IO: 4/2/0/0 */
    public static final GTRecipeType ABYSS_CASING_PRESS_RECIPES = GTRecipeTypes.register(
                    "abyss_casing_press", "multiblock")
            .setMaxIOSize(4, 2, 0, 0)
            .setEUIO(IO.IN)
            .setProgressBar(GuiTextures.PROGRESS_BAR_ARROW, LEFT_TO_RIGHT)
            .setSound(GTSoundEntries.COMPRESSOR);

    /** 崩坏能蒸馏 | IO: 2/1/2/6（多液体输出） */
    public static final GTRecipeType HONKAI_DISTILLATION_RECIPES = GTRecipeTypes.register(
                    "honkai_distillation", "multiblock")
            .setMaxIOSize(2, 1, 2, 6)
            .setEUIO(IO.IN)
            .setProgressBar(GuiTextures.PROGRESS_BAR_ARROW, LEFT_TO_RIGHT)
            .setSound(GTSoundEntries.COOLING);

    /** 魂钢拉丝 | IO: 2/4/0/0 */
    public static final GTRecipeType SOULIUM_WIRE_DRAWING_RECIPES = GTRecipeTypes.register(
                    "soulium_wire_drawing", "multiblock")
            .setMaxIOSize(2, 4, 0, 0)
            .setEUIO(IO.IN)
            .setProgressBar(GuiTextures.PROGRESS_BAR_ARROW, LEFT_TO_RIGHT)
            .setSound(GTSoundEntries.MOTOR);

    /** 前文明数据恢复 | IO: 2/4/0/0 */
    public static final GTRecipeType PRECIVILIZATION_DATA_RECOVERY_RECIPES = GTRecipeTypes.register(
                    "precivilization_data_recovery", "multiblock")
            .setMaxIOSize(2, 4, 0, 0)
            .setEUIO(IO.IN)
            .setProgressBar(GuiTextures.PROGRESS_BAR_ARROW, LEFT_TO_RIGHT)
            .setSound(GTSoundEntries.ELECTROLYZER);

    /** 崩坏能环境采样 | IO: 1/4/0/1 */
    public static final GTRecipeType HONKAI_ENVIRONMENT_SAMPLING_RECIPES = GTRecipeTypes.register(
                    "honkai_environment_sampling", "multiblock")
            .setMaxIOSize(1, 4, 0, 1)
            .setEUIO(IO.IN)
            .setProgressBar(GuiTextures.PROGRESS_BAR_ARROW, LEFT_TO_RIGHT)
            .setSound(GTSoundEntries.ELECTROLYZER);

    // ════════════════════════════════════════
    //  海渊阶段新增（24个）— 对应 Hk3MachinesAbyssStage 中的 23 台机器
    //  （部分机器共享配方类型，如 ABYSS_ENERGY_BUFFER 被多台机器使用）
    // ════════════════════════════════════════

    /** 大型崩坏能反应 | IO: 3/3/2/2 | EU: OUT（发电） */
    public static final GTRecipeType LARGE_HONKAI_REACTION_RECIPES = GTRecipeTypes.register(
                    "large_honkai_reaction", "multiblock")
            .setMaxIOSize(3, 3, 2, 2)
            .setEUIO(IO.OUT)
            .setProgressBar(GuiTextures.PROGRESS_BAR_ARROW, LEFT_TO_RIGHT)
            .setSound(GTSoundEntries.FURNACE);

    public static final GTRecipeType ABYSS_MATERIAL_COMPRESSION_RECIPES = GTRecipeTypes.register(
                    "abyss_material_compression", "multiblock")
            .setMaxIOSize(4, 2, 0, 0)
            .setEUIO(IO.IN)
            .setProgressBar(GuiTextures.PROGRESS_BAR_ARROW, LEFT_TO_RIGHT)
            .setSound(GTSoundEntries.COMPRESSOR);

    public static final GTRecipeType ABYSS_PRECISION_ASSEMBLY_RECIPES = GTRecipeTypes.register(
                    "abyss_precision_assembly", "multiblock")
            .setMaxIOSize(6, 4, 1, 0)
            .setEUIO(IO.IN)
            .setProgressBar(GuiTextures.PROGRESS_BAR_ARROW, LEFT_TO_RIGHT)
            .setSound(GTSoundEntries.ASSEMBLER);

    public static final GTRecipeType SEA_OF_QUANTA_OBSERVATION_RECIPES = GTRecipeTypes.register(
                    "sea_of_quanta_observation", "multiblock")
            .setMaxIOSize(4, 4, 1, 1)
            .setEUIO(IO.IN)
            .setProgressBar(GuiTextures.PROGRESS_BAR_ARROW, LEFT_TO_RIGHT)
            .setSound(GTSoundEntries.ELECTROLYZER);

    public static final GTRecipeType WORLD_BUBBLE_SAMPLING_RECIPES = GTRecipeTypes.register(
                    "world_bubble_sampling", "multiblock")
            .setMaxIOSize(4, 2, 1, 1)
            .setEUIO(IO.IN)
            .setProgressBar(GuiTextures.PROGRESS_BAR_ARROW, LEFT_TO_RIGHT)
            .setSound(GTSoundEntries.ELECTROLYZER);

    public static final GTRecipeType HONKAI_POLLUTION_SUPPRESSION_RECIPES = GTRecipeTypes.register(
                    "honkai_pollution_suppression", "multiblock")
            .setMaxIOSize(2, 1, 1, 0)
            .setEUIO(IO.IN)
            .setProgressBar(GuiTextures.PROGRESS_BAR_ARROW, LEFT_TO_RIGHT)
            .setSound(GTSoundEntries.COOLING);

    public static final GTRecipeType ABYSS_SUPERCONDUCTOR_COOLING_RECIPES = GTRecipeTypes.register(
                    "abyss_superconductor_cooling", "multiblock")
            .setMaxIOSize(2, 2, 1, 1)
            .setEUIO(IO.IN)
            .setProgressBar(GuiTextures.PROGRESS_BAR_ARROW, LEFT_TO_RIGHT)
            .setSound(GTSoundEntries.COOLING);

    public static final GTRecipeType ABYSS_ALLOY_REFINING_RECIPES = GTRecipeTypes.register(
                    "abyss_alloy_refining", "multiblock")
            .setMaxIOSize(4, 4, 2, 1)
            .setEUIO(IO.IN)
            .setProgressBar(GuiTextures.PROGRESS_BAR_ARROW, LEFT_TO_RIGHT)
            .setSound(GTSoundEntries.FURNACE);

    public static final GTRecipeType ABYSS_CHEMICAL_MEGA_REACTION_RECIPES = GTRecipeTypes.register(
                    "abyss_chemical_mega_reaction", "multiblock")
            .setMaxIOSize(4, 4, 3, 3)
            .setEUIO(IO.IN)
            .setProgressBar(GuiTextures.PROGRESS_BAR_ARROW, LEFT_TO_RIGHT)
            .setSound(GTSoundEntries.ELECTROLYZER);

    public static final GTRecipeType ABYSS_PARTICLE_ACCELERATION_RECIPES = GTRecipeTypes.register(
                    "abyss_particle_acceleration", "multiblock")
            .setMaxIOSize(4, 4, 1, 1)
            .setEUIO(IO.IN)
            .setProgressBar(GuiTextures.PROGRESS_BAR_ARROW, LEFT_TO_RIGHT)
            .setSound(GTSoundEntries.ARC);

    public static final GTRecipeType ABYSS_NANO_FABRICATION_RECIPES = GTRecipeTypes.register(
                    "abyss_nano_fabrication", "multiblock")
            .setMaxIOSize(6, 2, 1, 0)
            .setEUIO(IO.IN)
            .setProgressBar(GuiTextures.PROGRESS_BAR_ARROW, LEFT_TO_RIGHT)
            .setSound(GTSoundEntries.ASSEMBLER);

    /** 海渊精炼窑 | IO: 4/2/1/0 | 机器: ABYSS_KILN_CHAMBER（替代数据保险库） */
    public static final GTRecipeType ABYSS_KILN_REFINING_RECIPES = GTRecipeTypes.register(
                    "abyss_kiln_refining", "multiblock")
            .setMaxIOSize(4, 2, 1, 0)
            .setEUIO(IO.IN)
            .setProgressBar(GuiTextures.PROGRESS_BAR_ARROW, LEFT_TO_RIGHT)
            .setSound(GTSoundEntries.FURNACE);

    /** 海渊能源缓冲 | IO: 2/2/1/1 | EU: BOTH | 被多台机器共享（存储阵列/发射塔/接收塔/缓冲站） */
    public static final GTRecipeType ABYSS_ENERGY_BUFFER_RECIPES = GTRecipeTypes.register(
                    "abyss_energy_buffer", "multiblock")
            .setMaxIOSize(2, 2, 1, 1)
            .setEUIO(IO.BOTH)
            .setProgressBar(GuiTextures.PROGRESS_BAR_ARROW, LEFT_TO_RIGHT)
            .setSound(GTSoundEntries.ARC);

    /** 海渊机械匠厅 | IO: 6/4/0/0 | 机器: ABYSS_CARTWRIGHT_HALL（替代物流分拣枢纽，叙事向：手工锻造） */
    public static final GTRecipeType ABYSS_CARTWRIGHT_CRAFTING_RECIPES = GTRecipeTypes.register(
                    "abyss_cartwright_crafting", "multiblock")
            .setMaxIOSize(6, 4, 0, 0)
            .setEUIO(IO.IN)
            .setProgressBar(GuiTextures.PROGRESS_BAR_ARROW, LEFT_TO_RIGHT)
            .setSound(GTSoundEntries.ASSEMBLER);

    public static final GTRecipeType ABYSS_VACUUM_SMELTING_RECIPES = GTRecipeTypes.register(
                    "abyss_vacuum_smelting", "multiblock")
            .setMaxIOSize(4, 4, 1, 1)
            .setEUIO(IO.IN)
            .setProgressBar(GuiTextures.PROGRESS_BAR_ARROW, LEFT_TO_RIGHT)
            .setSound(GTSoundEntries.FURNACE);

    public static final GTRecipeType ABYSS_CRYSTAL_GROWTH_RECIPES = GTRecipeTypes.register(
                    "abyss_crystal_growth", "multiblock")
            .setMaxIOSize(4, 2, 2, 0)
            .setEUIO(IO.IN)
            .setProgressBar(GuiTextures.PROGRESS_BAR_ARROW, LEFT_TO_RIGHT)
            .setSound(GTSoundEntries.COOLING);

    public static final GTRecipeType ABYSS_MAGNETIC_CONFINEMENT_RECIPES = GTRecipeTypes.register(
                    "abyss_magnetic_confinement", "multiblock")
            .setMaxIOSize(2, 2, 1, 1)
            .setEUIO(IO.IN)
            .setProgressBar(GuiTextures.PROGRESS_BAR_ARROW, LEFT_TO_RIGHT)
            .setSound(GTSoundEntries.ARC);

    public static final GTRecipeType ABYSS_BIOCOMPUTING_RECIPES = GTRecipeTypes.register(
                    "abyss_biocomputing", "multiblock")
            .setMaxIOSize(4, 4, 1, 0)
            .setEUIO(IO.IN)
            .setProgressBar(GuiTextures.PROGRESS_BAR_ARROW, LEFT_TO_RIGHT)
            .setSound(GTSoundEntries.ELECTROLYZER);

    public static final GTRecipeType ABYSS_WASTE_RECYCLING_RECIPES = GTRecipeTypes.register(
                    "abyss_waste_recycling", "multiblock")
            .setMaxIOSize(4, 6, 1, 1)
            .setEUIO(IO.IN)
            .setProgressBar(GuiTextures.PROGRESS_BAR_ARROW, LEFT_TO_RIGHT)
            .setSound(GTSoundEntries.MACERATOR);

    public static final GTRecipeType ABYSS_SPECTRUM_ANALYSIS_RECIPES = GTRecipeTypes.register(
                    "abyss_spectrum_analysis", "multiblock")
            .setMaxIOSize(4, 4, 0, 0)
            .setEUIO(IO.IN)
            .setProgressBar(GuiTextures.PROGRESS_BAR_ARROW, LEFT_TO_RIGHT)
            .setSound(GTSoundEntries.ELECTROLYZER);

    public static final GTRecipeType ABYSS_HONKAI_CONCENTRATION_RECIPES = GTRecipeTypes.register(
                    "abyss_honkai_concentration", "multiblock")
            .setMaxIOSize(2, 2, 2, 1)
            .setEUIO(IO.IN)
            .setProgressBar(GuiTextures.PROGRESS_BAR_ARROW, LEFT_TO_RIGHT)
            .setSound(GTSoundEntries.COOLING);

    public static final GTRecipeType ABYSS_ARMOR_PLATE_FORGING_RECIPES = GTRecipeTypes.register(
                    "abyss_armor_plate_forging", "multiblock")
            .setMaxIOSize(4, 2, 0, 0)
            .setEUIO(IO.IN)
            .setProgressBar(GuiTextures.PROGRESS_BAR_ARROW, LEFT_TO_RIGHT)
            .setSound(GTSoundEntries.COMPRESSOR);

    public static final GTRecipeType ABYSS_COMMUNICATION_AMPLIFIER_RECIPES = GTRecipeTypes.register(
                    "abyss_communication_amplifier", "multiblock")
            .setMaxIOSize(4, 2, 0, 0)
            .setEUIO(IO.IN)
            .setProgressBar(GuiTextures.PROGRESS_BAR_ARROW, LEFT_TO_RIGHT)
            .setSound(GTSoundEntries.ELECTROLYZER);

    // ════════════════════════════════════════
    //  独立配方类型 — 此前错误共享 ABYSS_RESEARCH_ANALYSIS / ABYSS_ENERGY_BUFFER
    // ════════════════════════════════════════

    /** 文明通讯 | IO: 4/2/0/0 | EU: IN | 对应机器: CIVILIZATION_COMMUNICATION_RELAY */
    public static final GTRecipeType CIVILIZATION_COMMUNICATION_RECIPES = GTRecipeTypes.register(
                    "civilization_communication", "multiblock")
            .setMaxIOSize(4, 2, 0, 0)
            .setEUIO(IO.IN)
            .setProgressBar(GuiTextures.PROGRESS_BAR_ARROW, LEFT_TO_RIGHT)
            .setSound(GTSoundEntries.ELECTROLYZER);

    /** 崩坏能污染监测 | IO: 2/4/0/0 | EU: IN | 对应机器: HONKAI_POLLUTION_MONITOR */
    public static final GTRecipeType HONKAI_POLLUTION_MONITORING_RECIPES = GTRecipeTypes.register(
                    "honkai_pollution_monitoring", "multiblock")
            .setMaxIOSize(2, 4, 0, 0)
            .setEUIO(IO.IN)
            .setProgressBar(GuiTextures.PROGRESS_BAR_ARROW, LEFT_TO_RIGHT)
            .setSound(GTSoundEntries.ELECTROLYZER);

    /** 崩坏能裂解 | IO: 2/2/2/2 | 机器: HONKAI_CRACKING_FURNACE */
    public static final GTRecipeType HONKAI_CRACKING_RECIPES = GTRecipeTypes.register(
                    "honkai_cracking", "multiblock")
            .setMaxIOSize(2, 2, 2, 2)
            .setEUIO(IO.IN)
            .setProgressBar(GuiTextures.PROGRESS_BAR_ARROW, LEFT_TO_RIGHT)
            .setSound(GTSoundEntries.FURNACE);

    /** 远古遗物解析 | IO: 2/2/0/0 | 机器: ANCIENT_RELIC_ANALYZER */
    public static final GTRecipeType ANCIENT_RELIC_ANALYSIS_RECIPES = GTRecipeTypes.register(
                    "ancient_relic_analysis", "multiblock")
            .setMaxIOSize(2, 2, 0, 0)
            .setEUIO(IO.IN)
            .setProgressBar(GuiTextures.PROGRESS_BAR_ARROW, LEFT_TO_RIGHT)
            .setSound(GTSoundEntries.ELECTROLYZER);

    /**
     * 崩坏能认知铸锻 | IO: 4/2/1/0 | EU: IN | 机器: HONKAI_COGNITION_STUDIO
     * 把崩坏能凝结成概念性产物（思维晶片），替代已移除的储存阵列，走叙事向。
     */
    public static final GTRecipeType HONKAI_COGNITION_SMITHING_RECIPES = GTRecipeTypes.register(
                    "honkai_cognition_smithing", "multiblock")
            .setMaxIOSize(4, 2, 1, 0)
            .setEUIO(IO.IN)
            .setProgressBar(GuiTextures.PROGRESS_BAR_ARROW, LEFT_TO_RIGHT)
            .setSound(GTSoundEntries.COOLING);

    /**
     * 初始化所有配方类型（含子阶段）。
     * 由 GTRecipeTypesMixin 通过 Mixin 注入调用，时序在材料注册之后。
     * 新增阶段在此追加子类 init() 调用即可。
     */
    public static void init() {
        Hk3RecipeTypesImaginary.init();
        Hk3RecipeTypesQuantum.init();
        Hk3RecipeTypesFinality.init();
        Hk3RecipeTypesWonder.init();
        LOGGER.info("[HK3GTL] RecipeTypes 已注册（共 {} 个）。",
                43 + 10 + 12 + 13 + 12);
    }
}
