package com.sirin.hk3gtl.common.recipe;


/**
 * 【文件职责】
 * - 负责 Hk3RecipeTypesImpl 对应的配方注册与门槛绑定。
 * - 关键调用链：由上层系统入口调用 -> 本文件核心方法 -> 下游模块。
 *
 * 【变更记录】2026-05-19
 * - 删除：
 *   1) 初始归档备注：自 v0.3 基线梳理，无本次 diff。
 * - 新增：
 *   1) 新增统一变更备注块，便于后续维护与审计追踪。
 * - 修改：
 *   1) 未改动业务逻辑，仅补充文件级职责与维护注释模板。
 * - 用途：
 *   1) 帮助维护者快速理解文件职责、变更背景与风险点。
 *
 * 【段内说明】
 * - 复杂方法补充“干什么 / 边界 / 线程侧”精简中文注释。
 */
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
/** 中文说明：该处说明已按当前代码行为整理。*/
/**
 * 【变更记录 #1】2026-10-01 21:41:57（第1次备注 · 内测5修订151）
 * 删除：内测1—4旧结构相关入口。新增：无替代结构。
 * 修改：移除无工艺使用的旧吸收/冷凝配方类型；其他生产配方定义保留待新设备接入。
 * 用途：落实旧结构全部退役；内测5未审批设备仍待接入，不保留空注册兼容。
 */
public class Hk3RecipeTypesImpl {

    /** 内测5活动配方类型已迁移到 Hk3Beta5RecipeTypes，本类保留旧类型兼容入口。 */
    // 中文备注：该处说明已按当前代码行为整理。

    private static final Logger LOGGER = LogUtils.getLogger();

    // ════════════════════════════════════════
    //  P1 已有（4个）— 对应 Hk3MachinesImpl 中的 4 台核心机
    // ════════════════════════════════════════

    /** 崩坏能吸收 | IO: 1物入/1物出/0液入/0液出 | EU: IN | 对应机器: HONKAI_ABSORPTION_TOWER */

    /** 崩坏能凝结 | IO: 2/2/0/1 | EU: IN | 对应机器: HONKAI_CRYSTAL_CONDENSER */

    /** 魂钢冶炼 | IO: 4/4/1/0 | EU: IN | 对应机器: SOULIUM_SMELTERY */

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

    /** 理性重构 | IO: 4/4/1/1 */

    /** 小型崩坏能反应 | IO: 2/2/1/1 | EU: OUT（发电） */

    /** 中型崩坏能反应 | IO: 3/3/1/1 | EU: OUT（发电） */

    /** 崩坏能-EU转换 | IO: 2/2/1/1 | EU: BOTH（双向转换） */

    /** 崩坏能网络注入 | IO: 2/1/1/0 | EU: IN | 对应机器: HONKAI_NETWORK_INJECTOR（产出为无线网络余额，非物品） */

    /** 海渊电路铸造 | IO: 6/4/1/0 */

    /** 海渊机壳压制 | IO: 4/2/0/0 */

    /** 崩坏能蒸馏 | IO: 2/1/2/6（多液体输出） */

    /** 魂钢拉丝 | IO: 2/4/0/0 */

    /** 前文明数据恢复 | IO: 2/4/0/0 */

    /** 崩坏能环境采样 | IO: 1/4/0/1 */

    // ════════════════════════════════════════
    //  海渊阶段新增（24个）— 对应 Hk3MachinesAbyssStage 中的 23 台机器
    //  （部分机器共享配方类型，如 ABYSS_ENERGY_BUFFER 被多台机器使用）
    // ════════════════════════════════════════

    /** 大型崩坏能反应 | IO: 3/3/2/2 | EU: OUT（发电） */











    /** 海渊精炼窑 | IO: 4/2/1/0 | 机器: ABYSS_KILN_CHAMBER（替代数据保险库） */

    /** 海渊能源缓冲 | IO: 2/2/1/1 | EU: BOTH | 被多台机器共享（存储阵列/发射塔/接收塔/缓冲站） */

    /** 海渊机械匠厅 | IO: 6/4/0/0 | 机器: ABYSS_CARTWRIGHT_HALL（替代物流分拣枢纽，叙事向：手工锻造） */










    // ════════════════════════════════════════
    //  独立配方类型 — 此前错误共享 ABYSS_RESEARCH_ANALYSIS / ABYSS_ENERGY_BUFFER
    // ════════════════════════════════════════

    /** 文明通讯 | IO: 4/2/0/0 | EU: IN | 对应机器: CIVILIZATION_COMMUNICATION_RELAY */

    /** 崩坏能污染监测 | IO: 2/4/0/0 | EU: IN | 对应机器: HONKAI_POLLUTION_MONITOR */

    /** 崩坏能裂解 | IO: 2/2/2/2 | 机器: HONKAI_CRACKING_FURNACE */

    /** 远古遗物解析 | IO: 2/2/0/0 | 机器: ANCIENT_RELIC_ANALYZER */

    /**
     * 崩坏能认知铸锻 | IO: 4/2/1/0 | EU: IN | 机器: HONKAI_COGNITION_STUDIO
     * 把崩坏能凝结成概念性产物（思维晶片），替代已移除的储存阵列，走叙事向。
     */

    /**
     * 初始化所有配方类型（含子阶段）。
     * 由 GTRecipeTypesMixin 通过 Mixin 注入调用，时序在材料注册之后。
     * 新增阶段在此追加子类 init() 调用即可。
     */
    public static void init() {
        Hk3IndustrialRecipeTypes.init();
        LOGGER.info("[HK3GTL] 已注册现行工业工艺类型与研究所分析类型；旧设备配方类型已退役。");
    }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。

// 【变更记录 · 修订162】2026-10-17 14:38:46：移除旧四版设备配方类型注册及其专用注册入口，不保留兼容字段或空常量；仅保留研究所分析类型与现行工业工艺初始化。历史备注原样保留，本次退役不声明现行规划已完成。
