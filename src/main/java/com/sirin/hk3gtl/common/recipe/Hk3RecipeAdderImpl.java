package com.sirin.hk3gtl.common.recipe;




/** 中文说明：该处说明已按当前代码行为整理。*/
import com.gregtechceu.gtceu.api.data.chemical.ChemicalHelper;
import com.gregtechceu.gtceu.api.data.tag.TagPrefix;
import com.gregtechceu.gtceu.common.data.GTItems;
import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import com.gregtechceu.gtceu.data.recipe.CustomTags;
import com.gregtechceu.gtceu.api.GTValues;
import com.sirin.hk3gtl.common.block.CasingBlocks;
import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.material.Hk3Materials;
import com.sirin.hk3gtl.common.item.abyss.AbyssCircuitItems;
import com.sirin.hk3gtl.common.item.abyss.AbyssComponentItems;
import com.sirin.hk3gtl.common.item.honkai.HonkaiMaterialItems;
import com.sirin.hk3gtl.common.item.Hk3Items;
import com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate;
import com.sirin.hk3gtl.common.item.soulium.SouliumChainItems;
import com.sirin.hk3gtl.common.machine.Hk3Machines;
import com.sirin.hk3gtl.common.material.SouliumMaterial;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.data.recipes.FinishedRecipe;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.Blocks;
import org.gtlcore.gtlcore.common.data.GTLItems;
import org.gtlcore.gtlcore.common.data.GTLMaterials;
import org.slf4j.Logger;
import com.mojang.logging.LogUtils;
import com.sirin.hk3gtl.common.recipe.abyss.AbyssMaterialRecipes;
import com.sirin.hk3gtl.common.recipe.honkai.HonkaiMaterialRecipes;
import com.sirin.hk3gtl.common.recipe.honkai.HonkaiRecipes;
import com.sirin.hk3gtl.common.recipe.imaginary.ImaginaryCasingRecipes;
import com.sirin.hk3gtl.common.recipe.quantum.QuantumCasingRecipes;
import com.sirin.hk3gtl.common.recipe.soulium.SouliumRecipes;
import com.sirin.hk3gtl.common.recipe.validate.RecipeCycleDetector;

import java.util.function.Consumer;

/**
 * HK3GTL 配方注册总入口 — 所有 GT 配方的统一注册起点。
 *
 * <h3>职责</h3>
 * <ul>
 *   <li>被 {@link com.sirin.hk3gtl.Hk3GtAddon#addRecipes} 调用，在 GT 配方注册阶段一次性挂入全部配方</li>
 *   <li>本类保留 P1 核心配方（控制器/机壳/八大件/电路），按 Layer 分层注册</li>
 *   <li>其他领域配方下沉到子包中的专用类（recipe/abyss/, recipe/honkai/, recipe/max/ 等）</li>
 * </ul>
 *
 * <h3>修改指南 (Where to modify recipes)</h3>
 * <ul>
 *   <li>新增机器配方 → 按已批准工业职责选择专用配方类，再在 {@link #addRecipes} 中追加调用。</li>
 *   <li>修改配方材料/时间/耗电 → 调整 {@code .inputItems}, {@code .duration}, {@code .EUt} 的数值。使用 {@code Hk3Values.VA_LONG[tier]} 获取高阶电压，禁止硬编码 {@code GTValues.V[15]}（会溢出）。</li>
 *   <li>绑定研究门槛 → 注册配方后调用 {@code Hk3RecipeResearchGate.bind("recipeType", "recipeId", "R-AB-xxx")}</li>
 * </ul>
 *
 * <h3>注册 Layer 顺序</h3>
 * Layer 0: P1 基础产线 → Layer 1: Max 阶段 → Layer 2: 材料链 → Layer 3: 海渊中间件
 * → Layer 4: 八大件 II~IV → Layer 5: 海渊 23 台机器配方 → Layer 6: 控制器组装 → Layer 7: 研究凭证
 *
 * <h3>变更记录（2026-05-19）</h3>
 * <ul>
 *   <li>删除：后期阶段“只注册机器不注册配方”的残余状态</li>
 *   <li>新增：量子/终焉/奇观机器配方、量子/终焉电路配方、后期控制器组装配方</li>
 *   <li>修改：把后期阶段配方注册纳入统一入口，避免漏注册导致软锁</li>
 *   <li>用途：打通 R-QT / R-FN 研究节点所需物料来源与控制器建造链</li>
 * </ul>
 */
/** 中文说明：该处说明已按当前代码行为整理。*/
/**
 * 【变更记录 #2】2026-09-25 03:59:11（第 2 次备注 · 内测5修订71）
 * 删除：单一电路形态或旧电压显示限制。新增：统一系列及电压映射。
 * 修改：电路输入使用本等级标签，允许不同系列替代；输出、材料成本及研究门槛保持明确。
 * 用途：保持同级电路可替换、资源与游戏行为一致。
 */
/**
 * 【变更记录 #3】2026-09-25 04:48:31（第 3 次备注 · 内测5修订72）
 * 删除：系列升级使用同级通用标签的混用入口。新增：电子部件制造链的明确输入。
 * 修改：系列内升级只消耗本系列上一形态；所有完整电路产出（含批量和种子路线）按产量消耗所属平台CPU。
 * 用途：让完整电路逐系列组装；保留原配方研究门槛、数量和电压，输入不超过现有槽位。
 */
/**
 * 【变更记录 #4】2026-09-25 05:09:13（第 4 次备注 · 内测5修订73）
 * 删除：完整电路的自创堆料输入。新增：格雷纳米系列四形态的逐项映射。
 * 修改：保留既有电压和研究绑定，材料数量、产量、耗时及洁净室使用原版；显式补入原类型自动焊料。
 * 用途：全部生产路线遵守同系列前形态输入，海渊路线迁入自有铸造类型。
 */
/**
 * 【变更记录 #5】2026-09-26 01:58:37（第 5 次备注 · 内测5修订74）
 * 删除：本文件完整电路配方中照搬低级纳米电路的输入。
 * 新增：统一高阶封装制造器调用。
 * 修改：只替换正式电路工艺，保留配方ID、设备、电压、既有研究绑定；每批产出一枚，按形态消耗平台部件。
 * 用途：与Hk3ElectronicRecipes形成材料→晶圆→裸片→封装闭环；同系列升级仍限定具体前形态。
 */
/**
 * 【变更记录 #6】2026-09-29 23:37:35（内测5修订101）
 * 删除：本轮被替代的单前置或旧提示分支；其余历史保留。
 * 新增／修改：接入暂定工艺配方注册入口；不恢复贸易。
 * 用途：补足研究接线并如实保留未接物理执行器及结构审批边界。
 * 追溯：logs/research-mainline-r101；R101_FINAL_RECORD。
 */
/**
 * 【变更记录 #7】2026-09-30 02:17:47（第7次备注 · 内测5修订107）
 * 删除：本文件可执行代码中的旧电压键及常量引用，不保留旧键注册别名。
 * 新增：16档正式缩写作为唯一电压标识；逐文件映射见logs/voltage-keys-r107。
 * 修改：注册、配方、查询或标签引用按原tier序号一一迁移；数值、层级与资源内容保持原义。
 * 用途：避免显示名与实际注册键不一致；历史备注保留，旧存档不自动改写。
 */
/** 【变更记录 #8】2026-10-01 20:58:37（修订149）：删除本轮电路旧研究绑定；新增/修改：3条正式电路路线改为共同构造器绑定，避免旧门槛覆盖；用途：新版团队研究一致核验，保留材料、耗时、能耗与历史备注，不代表结构已接通。 */
/**
 * 【变更记录 #9】2026-10-01 21:41:57（第9次备注 · 内测5修订151）
 * 删除：内测1—4旧结构相关入口。新增：无替代结构。
 * 修改：撤掉59台控制器制造调用，配方启动锚点改为内测5 I01；保留新液态线和研究工艺。
 * 用途：落实旧结构全部退役；内测5未审批设备仍待接入，不保留空注册兼容。
 */
/**
 * 【变更记录 #10】2026-10-01 21:51:39（第10次备注 · 内测5修订152）
 * 删除：无。新增：16档电压配色机械机壳。
 * 修改：在总配方入口注册16个机壳装配配方。
 * 用途：提供独立建筑材料，不授予电压能力或研究进度，不修改既有结构。
 */
/**
 * 【变更记录 #11】2026-10-17 14:38:40（第11次备注 · 内测5修订162）
 * 删除：内测1–4退役结构的专用生产、旧电路和旧阶段配方注册，不保留空兼容壳。
 * 新增：量子机壳GT组装委托直接接入，避免随旧阶段入口一同误删。
 * 修改：仅保留现行工业、研究、GT材料加工与组件入口；旧配方不改挂现行机器。
 * 用途：落实已删除结构不继续遗留配方；逐文件原样备份见logs/retired-recipes-r162/before。
 */
/** 【变更记录 #12】2026-10-17 16:28:34（修订165）：删除三族旧八大件注册及HBV魂钢堆量方法，源码原字节归档至archive/main-materials-r165；新增整族主材与128八大件集中入口；修改后不再并存旧制造旁路；用途：保留L1至L12和L3八步主线，以本阶主材支撑现行部件。 */
public class Hk3RecipeAdderImpl {

    private static final Logger LOGGER = LogUtils.getLogger();

    /** MAX 电压 EU/t（Tier 14），用于 P1 核心机器配方 */
    private static final long MAX_EUT = Hk3Values.VA_LONG[GTValues.MAX];
    /** 海渊 I 电压 EU/t（Tier 15），用于海渊阶段配方 */
    private static final long HBV_EUT = Hk3Values.VA_LONG[Hk3Tiers.HBV];

    /**
     * 总注册顺序非常重要：
     * - 先注册崩坏能与魂钢主链，保证基础材料来源存在
     * - 再注册控制器、机壳、部件、电路，保证后续设备可组装
     * 这样阅读时可以按“基础产线 -> 结构件 -> 进阶件”的顺序理解整套内容。
     */
    public static void addRecipes(Consumer<FinishedRecipe> provider) {
        long started = System.nanoTime();
        LOGGER.info("[DEBUG] 开始注册GT配方...");

        if (Hk3Machines.I01_HONKAI_COLLECTION_TOWER == null) {
            LOGGER.error("[HK3GTL] 机器未注册（I01_HONKAI_COLLECTION_TOWER == null），跳过全部配方注册！");
            LOGGER.error("[HK3GTL] 这通常意味着 GTMachinesMixin 未被加载，或 Hk3MachinesImpl.init() 内部出错。");
            return;
        }

        // 包装 provider：注册过程中静默记录"输出→输入"反向图，注册末尾扫描循环并 LOG warning。
        // 工具不抛异常，仅做诊断；具体修复仍由开发者读 LOG 后手工调整配方。
        RecipeCycleDetector.reset();
        provider = RecipeCycleDetector.wrap(provider);
        com.sirin.hk3gtl.common.recipe.machine.Hk3ResearchComputerRecipes.register(provider);
        com.sirin.hk3gtl.common.recipe.machine.Hk3SpectrumBootstrapRecipes.register(provider);
        com.sirin.hk3gtl.common.recipe.machine.Hk3LiquidLineControllerRecipes.register(provider);

        // ── Layer 0: P1 基础产线 ──
        HonkaiRecipes.addAbsorptionRecipes(provider);
        HonkaiRecipes.addCondensationRecipes(provider);
        HonkaiRecipes.addNetworkInjectionRecipes(provider);
        // 修订160 · 2026-10-17 13:52:26：旧冶铸/深熔/精密装配控制器已退役，停止旧魂钢生产入口，避免绕过L3八步。
        SouliumRecipes.addSouliumProcessingRecipes(provider);
        addMachineRecipes(provider);
        com.sirin.hk3gtl.common.recipe.machine.Hk3VoltageCasingRecipes.register(provider);
        addCasingRecipes(provider);
        com.sirin.hk3gtl.common.recipe.main.Hk3MainMaterialRecipes.register(provider);
        com.sirin.hk3gtl.common.recipe.main.Hk3MainComponentRecipes.register(provider);
        Hk3ElectronicRecipes.register(provider);

        // ── Layer 2: 核心材料生产链 ──
        HonkaiMaterialRecipes.register(provider);

        // ── Layer 3: 海渊功能中间件 ──
        AbyssMaterialRecipes.register(provider);

        // ── Layer 4: 海渊 II~IV 八大件 ──




        // ── GT标准机中的虚数材料机壳与组件配方 ──
        ImaginaryCasingRecipes.register(provider);





        // 旧量子阶段入口已删除；其GT机壳配方仍有当前材料用途，独立保留。
        QuantumCasingRecipes.register(provider);
        // 量子 I~IV 八大件产线：补齐此前缺失的量子组件生产（原 robot_arm 配方消耗的量子电机无来源），打通量子组装链




        Hk3ResearchProcessRecipes.register(provider);

        // ── 研究矩阵配方 ──
        // 已彻底移除：研究矩阵由专用机器类 Hk3ResearchMatrixMachine 自行 serverTick 推进，
        // 不走 GT RecipeType / RecipeLogic。研究完成直接通过"崩坏能研究院"聊天栏通知。

        LOGGER.info("[DEBUG] GT配方注册完成，耗时={}ms（含循环检测前）",
                (System.nanoTime() - started) / 1_000_000L);
        RecipeCycleDetector.scanAndLog();
        LOGGER.info("[DEBUG] GT配方注册与循环检测总耗时={}ms",
                (System.nanoTime() - started) / 1_000_000L);
    }

    /**
     * 控制器配方集中放在一起，方便后续统一调整“机器本体”的解锁顺序。
     *
     * 注意：
     * - 当前多方块结构虽然暂时统一为泥土 3x3x3 立方体联调用结构，
     *   但控制器配方仍代表正式机器本体的制造门槛。
     * - 研究矩阵配方故意只依赖 P1 可达材料，避免再次形成研究系统自锁。
     *
     * <h4>维护说明</h4>
     * <ul>
     *   <li>本组只注册 P1 四台控制器：吸收塔、凝结厂、研究矩阵、魂钢冶铸中心。</li>
     *   <li>输入材料可以引用外部 GTL/GT/KubeJS 物品；若配方用于解锁本模组产线入口，避免使用本模组产物。</li>
     *   <li>createCasing / eternityCoil 是外部方块 ItemStack，改 ID 时确认整合包内该方块存在。</li>
     *   <li>改控制器成本：直接改对应 recipeBuilder 下 inputItems；改耗时：duration；改电压：EUt。</li>
     * </ul>
     */
    private static void addMachineRecipes(Consumer<FinishedRecipe> provider) {



        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_abyss_research_analysis_matrix")
                .inputItems(com.gregtechceu.gtceu.api.data.tag.TagPrefix.plate, com.gregtechceu.gtceu.common.data.GTMaterials.TungstenSteel, 16)
                .inputItems(CustomTags.MAX_CIRCUITS, 4)
                .inputItems(GTLItems.SENSOR_MAX.asStack(4))
                .inputItems(GTLItems.EMITTER_MAX.asStack(2))
                .inputItems(com.gregtechceu.gtceu.api.data.tag.TagPrefix.wireGtSingle, com.gregtechceu.gtceu.common.data.GTMaterials.Platinum, 8)
                .outputItems(Hk3Machines.ABYSS_RESEARCH_ANALYSIS_MATRIX.asStack())
                .duration(1200)
                .EUt(MAX_EUT)
                .save(provider);


        // 文明档案卷轴：一本书 + 巨量液态崩坏能 -> 卷轴。
        // 设计意图：卷轴属于文明级记录器，要求玩家投入高能量而非早期白送。
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_narrative_codex")
                .inputItems(new ItemStack(Items.BOOK, 1))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(262144))
                .outputItems(Hk3Items.NARRATIVE_CODEX.get().getDefaultInstance())
                .duration(1200)
                .EUt(HBV_EUT)
                .save(provider);
    }

    /**
     * 机壳配方单独收口，方便未来把“基础机壳 / 研究机壳 / 能源机壳”
     * 拆成更加明确的阶段化模块。
     *
     * <h4>维护说明</h4>
     * <ul>
     *   <li>无后缀的三条配方（{@code hk3gtl_casing_soulium / abyss_research / abyss_energy}）是 MAX 前置启动配方。</li>
     *   <li>这些启动配方不要使用本模组物品作输入，避免“还没建 P1 机器就需要 P1 产物”的死锁。</li>
     *   <li>{@code *_abyss} 后缀配方是海渊阶段批量升级/扩产配方，可以使用本模组已有产物。</li>
     *   <li>改成本：优先改 GTLMaterials / GTLItems / CustomTags.MAX_CIRCUITS 的数量。</li>
     *   <li>改产量：只改 outputItems 第二参数；改耗时：duration，20 tick = 1 秒；改电压：EUt。</li>
     * </ul>
     */
    private static void addCasingRecipes(Consumer<FinishedRecipe> provider) {
        // MAX前启动配方：GTL Shirabon/Magmatter + MAX部件 + MAX电路 → 魂钢机壳。
        // 用途：给魂钢冶铸中心提供结构方块；不依赖本模组物品，避免开局死锁。
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_casing_soulium")
                .inputItems(ChemicalHelper.get(TagPrefix.plate, GTLMaterials.Shirabon, 4096))
                .inputItems(ChemicalHelper.get(TagPrefix.ingot, GTLMaterials.Magmatter, 2048))
                .inputItems(GTLItems.ELECTRIC_PISTON_MAX.asStack(128))
                .inputItems(GTLItems.FIELD_GENERATOR_MAX.asStack(32))
                .inputItems(CustomTags.MAX_CIRCUITS, 64)
                .circuitMeta(8)
                .outputItems(new ItemStack(CasingBlocks.CASING_SOULIUM.get(), 32))
                .duration(3600)
                .EUt(MAX_EUT)
                .save(provider);

        // 海渊阶段扩产配方：魂钢板 → 魂钢机壳。
        // 用途：进入魂钢产线后批量补结构方块；可依赖本模组魂钢材料。
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_casing_soulium_abyss")
                .inputItems(ChemicalHelper.get(TagPrefix.plate, SouliumMaterial.SOULIUM, 2048))
                .circuitMeta(8)
                .outputItems(new ItemStack(CasingBlocks.CASING_SOULIUM.get(), 64))
                .duration(400)
                .EUt(HBV_EUT)
                .save(provider);

        // 强化魂钢机壳：魂钢机壳 + 魂钢板 + 崩坏能晶体。
        // 用途：作为海渊机械/研究/能源等更高级机壳的中间基底。
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_casing_reinforced_soulium")
                .inputItems(new ItemStack(CasingBlocks.CASING_SOULIUM.get(), 128))
                .inputItems(ChemicalHelper.get(TagPrefix.plate, SouliumMaterial.SOULIUM, 1024))
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 512))
                .circuitMeta(8)
                .outputItems(new ItemStack(CasingBlocks.CASING_REINFORCED_SOULIUM.get(), 64))
                .duration(600)
                .EUt(HBV_EUT)
                .save(provider);

        // 海渊机械机壳：强化魂钢机壳 + 海渊I电路 + 魂钢板。
        // 用途：制造/物流/冶金类海渊多方块的主体结构。
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_casing_abyss_mechanical")
                .inputItems(new ItemStack(CasingBlocks.CASING_REINFORCED_SOULIUM.get(), 128))
                .inputItems(com.sirin.hk3gtl.common.item.Hk3CircuitCatalog.tag(15), 256)
                .inputItems(ChemicalHelper.get(TagPrefix.plate, SouliumMaterial.SOULIUM, 1024))
                .circuitMeta(8)
                .outputItems(new ItemStack(CasingBlocks.CASING_ABYSS_MECHANICAL.get(), 64))
                .duration(600)
                .EUt(HBV_EUT)
                .save(provider);

        // MAX前启动配方：GTL材料 + MAX传感/发射器 + 神经处理器 → 海渊科研机壳。
        // 用途：给海渊研究解析矩阵提供结构方块；不要使用本模组研究物品作输入。
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_casing_abyss_research")
                .inputItems(ChemicalHelper.get(TagPrefix.plate, GTLMaterials.Shirabon, 4096))
                .inputItems(ChemicalHelper.get(TagPrefix.ingot, GTLMaterials.Magmatter, 4096))
                .inputItems(GTLItems.SENSOR_MAX.asStack(64))
                .inputItems(GTLItems.EMITTER_MAX.asStack(64))
                .inputItems(CustomTags.MAX_CIRCUITS, 128)
                .inputItems(GTItems.NEURO_PROCESSOR.asStack(128))
                .circuitMeta(8)
                .outputItems(new ItemStack(CasingBlocks.CASING_ABYSS_RESEARCH.get(), 16))
                .duration(4800)
                .EUt(MAX_EUT)
                .save(provider);

        // 海渊阶段扩产配方：强化魂钢 + 海渊II电路 + 凝视缓冲单元 → 海渊科研机壳。
        // 用途：研究线启动后批量补科研类机器结构方块。
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_casing_abyss_research_abyss")
                .inputItems(new ItemStack(CasingBlocks.CASING_REINFORCED_SOULIUM.get(), 128))
                .inputItems(com.sirin.hk3gtl.common.item.Hk3CircuitCatalog.tag(16), 128)
                .inputItems(new ItemStack(HonkaiMaterialItems.GAZE_BUFFER_UNIT.get(), 128))
                .circuitMeta(8)
                .outputItems(new ItemStack(CasingBlocks.CASING_ABYSS_RESEARCH.get(), 32))
                .duration(800)
                .EUt(HBV_EUT)
                .save(provider);

        // MAX前启动配方：GTL材料 + MAX能源/泵/电机部件 → 海渊能源机壳。
        // 用途：给崩坏能吸收塔、结晶凝结厂提供结构方块；不依赖本模组产物。
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_casing_abyss_energy")
                .inputItems(ChemicalHelper.get(TagPrefix.plate, GTLMaterials.Shirabon, 4096))
                .inputItems(ChemicalHelper.get(TagPrefix.ingot, GTLMaterials.Magmatter, 4096))
                .inputItems(GTLItems.FIELD_GENERATOR_MAX.asStack(64))
                .inputItems(GTLItems.ELECTRIC_PUMP_MAX.asStack(64))
                .inputItems(CustomTags.MAX_CIRCUITS, 128)
                .inputItems(GTLItems.ELECTRIC_MOTOR_MAX.asStack(128))
                .circuitMeta(8)
                .outputItems(new ItemStack(CasingBlocks.CASING_ABYSS_ENERGY.get(), 16))
                .duration(4800)
                .EUt(MAX_EUT)
                .save(provider);

        // 海渊阶段扩产配方：强化魂钢 + 海渊III电路 + 稳定崩坏晶体 → 海渊能源机壳。
        // 用途：能源类多方块扩建时的批量生产路线。
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_casing_abyss_energy_abyss")
                .inputItems(new ItemStack(CasingBlocks.CASING_REINFORCED_SOULIUM.get(), 128))
                .inputItems(com.sirin.hk3gtl.common.item.Hk3CircuitCatalog.tag(17), 128)
                .inputItems(new ItemStack(HonkaiMaterialItems.STABILIZED_HONKAI_CRYSTAL.get(), 256))
                .circuitMeta(8)
                .outputItems(new ItemStack(CasingBlocks.CASING_ABYSS_ENERGY.get(), 16))
                .duration(800)
                .EUt(HBV_EUT)
                .save(provider);
    }



}
