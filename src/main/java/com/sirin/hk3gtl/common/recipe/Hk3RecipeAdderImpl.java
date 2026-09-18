package com.sirin.hk3gtl.common.recipe;



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
import com.sirin.hk3gtl.common.recipe.abyss.AbyssComponentRecipes;
import com.sirin.hk3gtl.common.recipe.abyss.AbyssMachineRecipes;
import com.sirin.hk3gtl.common.recipe.abyss.AbyssMaterialRecipes;
import com.sirin.hk3gtl.common.recipe.honkai.HonkaiMaterialRecipes;
import com.sirin.hk3gtl.common.recipe.honkai.HonkaiRecipes;
import com.sirin.hk3gtl.common.recipe.imaginary.ImaginaryCasingRecipes;
import com.sirin.hk3gtl.common.recipe.imaginary.ImaginaryChainRecipes;
import com.sirin.hk3gtl.common.recipe.imaginary.ImaginaryCircuitRecipes;
import com.sirin.hk3gtl.common.recipe.imaginary.ImaginaryComponentRecipes;
import com.sirin.hk3gtl.common.recipe.imaginary.ImaginaryControllerRecipes;
import com.sirin.hk3gtl.common.recipe.imaginary.ImaginaryMachineRecipes;
import com.sirin.hk3gtl.common.recipe.machine.AdvancedControllerRecipes;
import com.sirin.hk3gtl.common.recipe.machine.ControllerRecipes;
import com.sirin.hk3gtl.common.recipe.max.MaxStageRecipes;
import com.sirin.hk3gtl.common.recipe.finality.FinalityStageRecipes;
import com.sirin.hk3gtl.common.recipe.quantum.QuantumComponentRecipes;
import com.sirin.hk3gtl.common.recipe.quantum.QuantumStageRecipes;
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
 *   <li>新增机器配方 → 找到或创建对应阶段的配方类（如 {@link com.sirin.hk3gtl.common.recipe.abyss.AbyssMachineRecipes}），然后在 {@link #addRecipes} 中追加调用。</li>
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
public class Hk3RecipeAdderImpl {

    private static final Logger LOGGER = LogUtils.getLogger();

    /** MAX 电压 EU/t（Tier 14），用于 P1 核心机器配方 */
    private static final long MAX_EUT = Hk3Values.VA_LONG[GTValues.MAX];
    /** 海渊 I 电压 EU/t（Tier 15），用于海渊阶段配方 */
    private static final long ABYSS_1_EUT = Hk3Values.VA_LONG[Hk3Tiers.ABYSS_1];

    /**
     * 总注册顺序非常重要：
     * - 先注册崩坏能与魂钢主链，保证基础材料来源存在
     * - 再注册控制器、机壳、部件、电路，保证后续设备可组装
     * 这样阅读时可以按“基础产线 -> 结构件 -> 进阶件”的顺序理解整套内容。
     */
    public static void addRecipes(Consumer<FinishedRecipe> provider) {
        long started = System.nanoTime();
        LOGGER.info("[DEBUG] 开始注册GT配方...");

        if (Hk3Machines.HONKAI_ABSORPTION_TOWER == null) {
            LOGGER.error("[HK3GTL] 机器未注册（HONKAI_ABSORPTION_TOWER == null），跳过全部配方注册！");
            LOGGER.error("[HK3GTL] 这通常意味着 GTMachinesMixin 未被加载，或 Hk3MachinesImpl.init() 内部出错。");
            return;
        }

        // 包装 provider：注册过程中静默记录"输出→输入"反向图，注册末尾扫描循环并 LOG warning。
        // 工具不抛异常，仅做诊断；具体修复仍由开发者读 LOG 后手工调整配方。
        RecipeCycleDetector.reset();
        provider = RecipeCycleDetector.wrap(provider);

        // ── Layer 0: P1 基础产线 ──
        HonkaiRecipes.addAbsorptionRecipes(provider);
        HonkaiRecipes.addCondensationRecipes(provider);
        HonkaiRecipes.addNetworkInjectionRecipes(provider);
        SouliumRecipes.addSouliumSmeltingRecipes(provider);
        SouliumRecipes.addSouliumProcessingRecipes(provider);
        addMachineRecipes(provider);
        addCasingRecipes(provider);
        addComponentRecipes(provider);
        addCircuitRecipes(provider);

        // ── Layer 1: Max 起始阶段 12 台机器配方 ──
        MaxStageRecipes.register(provider);

        // ── Layer 2: 核心材料生产链 ──
        HonkaiMaterialRecipes.register(provider);

        // ── Layer 3: 海渊功能中间件 ──
        AbyssMaterialRecipes.register(provider);

        // ── Layer 4: 海渊 II~IV 八大件 ──
        AbyssComponentRecipes.addAbyssIIComponentRecipes(provider);
        AbyssComponentRecipes.addAbyssIIIComponentRecipes(provider);
        AbyssComponentRecipes.addAbyssIVComponentRecipes(provider);

        // ── Layer 5: 海渊 23 台多方块专属配方 ──
        AbyssMachineRecipes.register(provider);

        // ── Layer 6: Max + 海渊 40 台控制器组装配方 ──
        ControllerRecipes.register(provider);

        // ── Layer 7: 虚数阶段 (Imaginary) 配方 ──
        ImaginaryCasingRecipes.register(provider);
        ImaginaryCircuitRecipes.register(provider);
        ImaginaryComponentRecipes.addImaginaryIComponentRecipes(provider);
        ImaginaryComponentRecipes.addImaginaryIIComponentRecipes(provider);
        ImaginaryComponentRecipes.addImaginaryIIIComponentRecipes(provider);
        ImaginaryComponentRecipes.addImaginaryIVComponentRecipes(provider);
        ImaginaryControllerRecipes.register(provider);

        // ── Layer 8: 虚数双阵营核心 + 相位纯化回收（v0.4 新增产线）──
        ImaginaryChainRecipes.register(provider);
        ImaginaryMachineRecipes.register(provider);

        // ── Layer 9: 量子 / 终焉 / 奇观核心配方 + 控制器补全（修复 130→60 残余缺口） ──
        QuantumStageRecipes.register(provider);
        // 量子 I~IV 八大件产线：补齐此前缺失的量子组件生产（原 robot_arm 配方消耗的量子电机无来源），打通量子组装链
        QuantumComponentRecipes.addQuantumIComponentRecipes(provider);
        QuantumComponentRecipes.addQuantumIIComponentRecipes(provider);
        QuantumComponentRecipes.addQuantumIIIComponentRecipes(provider);
        QuantumComponentRecipes.addQuantumIVComponentRecipes(provider);
        FinalityStageRecipes.register(provider);
        AdvancedControllerRecipes.register(provider);

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
        ItemStack createCasing = new ItemStack(
                BuiltInRegistries.BLOCK.get(new ResourceLocation("gtlcore", "create_casing")), 16);
        ItemStack eternityCoil = new ItemStack(
                BuiltInRegistries.BLOCK.get(new ResourceLocation("kubejs", "eternity_coil_block")), 8);

        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_honkai_absorption_tower")
                .inputItems(GTLItems.FIELD_GENERATOR_MAX.asStack(4))
                .inputItems(GTLItems.EMITTER_MAX.asStack(4))
                .inputItems(GTLItems.SENSOR_MAX.asStack(4))
                .inputItems(CustomTags.MAX_CIRCUITS, 8)
                .inputItems(createCasing)
                .inputItems(eternityCoil)
                .inputItems(GTItems.NEURO_PROCESSOR.asStack(8))
                .inputItems(new ItemStack(Blocks.IRON_BLOCK, 32))
                .inputItems(new ItemStack(Blocks.LIGHT_BLUE_STAINED_GLASS, 16))
                .outputItems(Hk3Machines.HONKAI_ABSORPTION_TOWER.asStack())
                .duration(1200)
                .EUt(MAX_EUT)
                .save(provider);

        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_honkai_crystal_condenser")
                .inputItems(GTLItems.ELECTRIC_PUMP_MAX.asStack(4))
                .inputItems(GTLItems.ELECTRIC_MOTOR_MAX.asStack(4))
                .inputItems(CustomTags.MAX_CIRCUITS, 4)
                .inputItems(new ItemStack(HonkaiMaterialItems.RAW_HONKAI_PARTICLE.get(), 16))
                .inputItems(new ItemStack(Blocks.IRON_BLOCK, 24))
                .inputItems(new ItemStack(Blocks.BLUE_ICE, 16))
                .inputItems(new ItemStack(Blocks.LIGHT_BLUE_STAINED_GLASS, 16))
                .inputItems(createCasing.copy())
                .outputItems(Hk3Machines.HONKAI_CRYSTAL_CONDENSER.asStack())
                .duration(900)
                .EUt(MAX_EUT)
                .save(provider);

        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_abyss_research_analysis_matrix")
                .inputItems(new ItemStack(CasingBlocks.CASING_REINFORCED_SOULIUM.get(), 16))
                .inputItems(CustomTags.MAX_CIRCUITS, 4)
                .inputItems(GTLItems.SENSOR_MAX.asStack(4))
                .inputItems(GTLItems.EMITTER_MAX.asStack(2))
                .inputItems(new ItemStack(HonkaiMaterialItems.GAZE_BUFFER_UNIT.get(), 4))
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 8))
                .outputItems(Hk3Machines.ABYSS_RESEARCH_ANALYSIS_MATRIX.asStack())
                .duration(1200)
                .EUt(ABYSS_1_EUT)
                .save(provider);

        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_soulium_smeltery")
                .inputItems(createCasing.copy())
                .inputItems(GTLItems.FIELD_GENERATOR_MAX.asStack(4))
                .inputItems(GTLItems.ELECTRIC_MOTOR_MAX.asStack(4))
                .inputItems(CustomTags.MAX_CIRCUITS, 8)
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 32))
                // 修复死锁：本机器是魂钢生产的唯一入口，原配方要求魂钢板会让玩家无法启动产线。
                // 改用 GTL Shirabon 板（MAX 阶段玩家已可大量生产），保持工业感同时打通进度。
                .inputItems(ChemicalHelper.get(TagPrefix.plate, GTLMaterials.Shirabon, 64))
                .outputItems(Hk3Machines.SOULIUM_SMELTERY.asStack())
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
                .EUt(ABYSS_1_EUT)
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
                .EUt(ABYSS_1_EUT)
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
                .EUt(ABYSS_1_EUT)
                .save(provider);

        // 海渊机械机壳：强化魂钢机壳 + 海渊I电路 + 魂钢板。
        // 用途：制造/物流/冶金类海渊多方块的主体结构。
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_casing_abyss_mechanical")
                .inputItems(new ItemStack(CasingBlocks.CASING_REINFORCED_SOULIUM.get(), 128))
                .inputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_1.get(), 256))
                .inputItems(ChemicalHelper.get(TagPrefix.plate, SouliumMaterial.SOULIUM, 1024))
                .circuitMeta(8)
                .outputItems(new ItemStack(CasingBlocks.CASING_ABYSS_MECHANICAL.get(), 64))
                .duration(600)
                .EUt(ABYSS_1_EUT)
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
                .inputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_2.get(), 128))
                .inputItems(new ItemStack(HonkaiMaterialItems.GAZE_BUFFER_UNIT.get(), 128))
                .circuitMeta(8)
                .outputItems(new ItemStack(CasingBlocks.CASING_ABYSS_RESEARCH.get(), 32))
                .duration(800)
                .EUt(ABYSS_1_EUT)
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
                .inputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_3.get(), 128))
                .inputItems(new ItemStack(HonkaiMaterialItems.STABILIZED_HONKAI_CRYSTAL.get(), 256))
                .circuitMeta(8)
                .outputItems(new ItemStack(CasingBlocks.CASING_ABYSS_ENERGY.get(), 16))
                .duration(800)
                .EUt(ABYSS_1_EUT)
                .save(provider);
    }

    // ═══════════════════════════════════════════
    //  海渊 I 八大件 — 组装机配方
    //  MAX 组件 + 魂钢材料 + 崩坏能结晶 → 海渊 I 组件
    //  压缩策略：巨量输入换取极少输出
    //  维护说明：
    //  - 本组是海渊I八大件的入口产线，后续 II~IV 八大件由 AbyssComponentRecipes 接管。
    //  - 每条配方的输出数量很低，改产能直接改 outputItems 第二参数。
    //  - 这些配方消耗本模组魂钢/崩坏能材料，必须确保魂钢与崩坏能基础链已能生产。
    //  - 如需降低开局压力，优先下调 MAX 组件输入数量，而不是下调魂钢/崩坏能消耗。
    // ═══════════════════════════════════════════
    /**
     * 海渊 I 八大件。
     */
    private static void addComponentRecipes(Consumer<FinishedRecipe> provider) {
        // 电机: MAX电机×256 + 魂钢细丝×4096 + 魂钢杆×1024 + 崩坏能结晶×512 → ×2
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_motor_abyss_1")
                .inputItems(GTLItems.ELECTRIC_MOTOR_MAX.asStack(256))
                .inputItems(ChemicalHelper.get(TagPrefix.wireFine, SouliumMaterial.SOULIUM, 4096))
                .inputItems(ChemicalHelper.get(TagPrefix.rod, SouliumMaterial.SOULIUM, 1024))
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 512))
                .outputItems(new ItemStack(AbyssComponentItems.ELECTRIC_MOTOR_ABYSS_1.get(), 2))
                .duration(800)
                .EUt(ABYSS_1_EUT)
                .save(provider);

        // 活塞: MAX活塞×256 + 魂钢板×1024 + 魂钢杆×512 + 海渊I电机×256 → ×2
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_piston_abyss_1")
                .inputItems(GTLItems.ELECTRIC_PISTON_MAX.asStack(256))
                .inputItems(ChemicalHelper.get(TagPrefix.plate, SouliumMaterial.SOULIUM, 1024))
                .inputItems(ChemicalHelper.get(TagPrefix.rod, SouliumMaterial.SOULIUM, 512))
                .inputItems(new ItemStack(AbyssComponentItems.ELECTRIC_MOTOR_ABYSS_1.get(), 256))
                .outputItems(new ItemStack(AbyssComponentItems.ELECTRIC_PISTON_ABYSS_1.get(), 2))
                .duration(800)
                .EUt(ABYSS_1_EUT)
                .save(provider);

        // 泵: MAX泵×256 + 魂钢板×512 + 魂钢环×1024 + 海渊I电机×256 → ×2
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_pump_abyss_1")
                .inputItems(GTLItems.ELECTRIC_PUMP_MAX.asStack(256))
                .inputItems(ChemicalHelper.get(TagPrefix.plate, SouliumMaterial.SOULIUM, 512))
                .inputItems(ChemicalHelper.get(TagPrefix.ring, SouliumMaterial.SOULIUM, 1024))
                .inputItems(new ItemStack(AbyssComponentItems.ELECTRIC_MOTOR_ABYSS_1.get(), 256))
                .outputItems(new ItemStack(AbyssComponentItems.ELECTRIC_PUMP_ABYSS_1.get(), 2))
                .duration(800)
                .EUt(ABYSS_1_EUT)
                .save(provider);

        // 传送带: MAX传送带×256 + 魂钢板×1024 + 海渊I电机×512 → ×2
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_conveyor_abyss_1")
                .inputItems(GTLItems.CONVEYOR_MODULE_MAX.asStack(256))
                .inputItems(ChemicalHelper.get(TagPrefix.plate, SouliumMaterial.SOULIUM, 1024))
                .inputItems(new ItemStack(AbyssComponentItems.ELECTRIC_MOTOR_ABYSS_1.get(), 512))
                .outputItems(new ItemStack(AbyssComponentItems.CONVEYOR_MODULE_ABYSS_1.get(), 2))
                .duration(800)
                .EUt(ABYSS_1_EUT)
                .save(provider);

        // 机械臂: MAX臂×128 + 魂钢杆×256 + 海渊I电机×128 + 海渊I活塞×128 + 电路×128 → ×2
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_robot_arm_abyss_1")
                .inputItems(GTLItems.ROBOT_ARM_MAX.asStack(128))
                .inputItems(ChemicalHelper.get(TagPrefix.rod, SouliumMaterial.SOULIUM, 256))
                .inputItems(new ItemStack(AbyssComponentItems.ELECTRIC_MOTOR_ABYSS_1.get(), 128))
                .inputItems(new ItemStack(AbyssComponentItems.ELECTRIC_PISTON_ABYSS_1.get(), 128))
                .inputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_1.get(), 128))
                .outputItems(new ItemStack(AbyssComponentItems.ROBOT_ARM_ABYSS_1.get(), 2))
                .duration(1200)
                .EUt(ABYSS_1_EUT)
                .save(provider);

        // 场发生器: MAX场×128 + 魂钢框架×128 + 崩坏能结晶×512 + 电路×128 → ×2
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_field_gen_abyss_1")
                .inputItems(GTLItems.FIELD_GENERATOR_MAX.asStack(128))
                .inputItems(ChemicalHelper.get(TagPrefix.frameGt, SouliumMaterial.SOULIUM, 128))
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 512))
                .inputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_1.get(), 128))
                .outputItems(new ItemStack(AbyssComponentItems.FIELD_GENERATOR_ABYSS_1.get(), 2))
                .duration(1200)
                .EUt(ABYSS_1_EUT)
                .save(provider);

        // 发射器: MAX发射器×128 + 魂钢杆×256 + 崩坏能结晶×256 + 电路×128 → ×2
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_emitter_abyss_1")
                .inputItems(GTLItems.EMITTER_MAX.asStack(128))
                .inputItems(ChemicalHelper.get(TagPrefix.rod, SouliumMaterial.SOULIUM, 256))
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 256))
                .inputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_1.get(), 128))
                .outputItems(new ItemStack(AbyssComponentItems.EMITTER_ABYSS_1.get(), 2))
                .duration(1200)
                .EUt(ABYSS_1_EUT)
                .save(provider);

        // 传感器: MAX传感器×128 + 魂钢板×256 + 崩坏能结晶×256 + 电路×128 → ×2
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_sensor_abyss_1")
                .inputItems(GTLItems.SENSOR_MAX.asStack(128))
                .inputItems(ChemicalHelper.get(TagPrefix.plate, SouliumMaterial.SOULIUM, 256))
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 256))
                .inputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_1.get(), 128))
                .outputItems(new ItemStack(AbyssComponentItems.SENSOR_ABYSS_1.get(), 2))
                .duration(1200)
                .EUt(ABYSS_1_EUT)
                .save(provider);
    }

    // ═══════════════════════════════════════════
    //  海渊电路 — 组装机配方
    //  4级电路对应 Tier 15~18
    //  压缩策略：加入巨量流体与资源消耗，降低单次产出
    //  维护说明：
    //  - 海渊I电路无研究门槛，是 P1 到海渊阶段的入口。
    //  - 海渊II~IV电路分别绑定 R-AB-012 / R-AB-018 / R-AB-022。
    //  - 修改研究门槛时同步修改 Hk3ResearchNodes 中对应节点描述。
    //  - 液态崩坏能消耗在 inputFluids，单位为 mB。
    // ═══════════════════════════════════════════
    /**
     * 海渊电路配方。
     *
     * 当前分层原则：
     * - 海渊 I 电路属于 P1 已验证主链，不再锁研究许可
     * - 海渊 II~IV 才逐步挂研究许可，体现“研究矩阵建成后再推进更深层电路”
     */
    private static void addCircuitRecipes(Consumer<FinishedRecipe> provider) {
        // 海渊1电路: MAX级电路×2048 + 魂钢板×1024 + 魂钢细丝×4096 + 崩坏能结晶×1024 + 液态崩坏能 40000mB → ×4
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_circuit_abyss_1")
                .inputItems(CustomTags.MAX_CIRCUITS, 2048)
                .inputItems(ChemicalHelper.get(TagPrefix.plate, SouliumMaterial.SOULIUM, 1024))
                .inputItems(ChemicalHelper.get(TagPrefix.wireFine, SouliumMaterial.SOULIUM, 4096))
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 1024))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(40000))
                .outputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_1.get(), 4))
                .duration(1200)
                .EUt(ABYSS_1_EUT)
                .save(provider);

        // 海渊2电路: 海渊1电路×128 + 魂钢箔×1024 + 崩坏能结晶×1024 + 液态崩坏能 40000mB → ×4
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_circuit_abyss_2")
                .inputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_1.get(), 128))
                .inputItems(ChemicalHelper.get(TagPrefix.foil, SouliumMaterial.SOULIUM, 1024))
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 1024))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(40000))
                .outputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_2.get(), 4))
                .duration(1200)
                .EUt(ABYSS_1_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("assembler", "hk3gtl_circuit_abyss_2", "R-AB-012");

        // 海渊3电路: 海渊2电路×128 + 魂钢框架×256 + 崩坏能结晶×1024 + 液态崩坏能 60000mB → ×2
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_circuit_abyss_3")
                .inputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_2.get(), 128))
                .inputItems(ChemicalHelper.get(TagPrefix.frameGt, SouliumMaterial.SOULIUM, 256))
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 1024))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(60000))
                .outputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_3.get(), 2))
                .duration(1600)
                .EUt(ABYSS_1_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("assembler", "hk3gtl_circuit_abyss_3", "R-AB-018");

        // 海渊4电路: 海渊3电路×128 + 定向魂钢构件×128 + 稳定崩坏能晶体×256 + 液态崩坏能 80000mB → ×1
        GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_circuit_abyss_4")
                .inputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_3.get(), 128))
                .inputItems(new ItemStack(SouliumChainItems.ORIENTED_SOULIUM_COMPONENT.get(), 128))
                .inputItems(new ItemStack(HonkaiMaterialItems.STABILIZED_HONKAI_CRYSTAL.get(), 256))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(80000))
                .outputItems(new ItemStack(AbyssCircuitItems.CIRCUIT_ABYSS_4.get(), 1))
                .duration(2000)
                .EUt(ABYSS_1_EUT)
                .save(provider);
        Hk3RecipeResearchGate.bind("assembler", "hk3gtl_circuit_abyss_4", "R-AB-022");
    }
}
