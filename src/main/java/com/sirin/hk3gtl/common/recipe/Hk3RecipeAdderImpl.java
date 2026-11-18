package com.sirin.hk3gtl.common.recipe;

import com.gregtechceu.gtceu.common.data.GTItems;
import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import com.gregtechceu.gtceu.data.recipe.CustomTags;
import com.gregtechceu.gtceu.api.GTValues;
import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.recipe.power.Hk3RecipePower;
import com.sirin.hk3gtl.common.material.Hk3Materials;
import com.sirin.hk3gtl.common.item.abyss.AbyssCircuitItems;
import com.sirin.hk3gtl.common.item.abyss.AbyssComponentItems;
import com.sirin.hk3gtl.common.item.honkai.HonkaiMaterialItems;
import com.sirin.hk3gtl.common.item.Hk3Items;
import com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate;
import com.sirin.hk3gtl.common.item.soulium.SouliumChainItems;
import com.sirin.hk3gtl.common.machine.Hk3Machines;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.data.recipes.FinishedRecipe;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.Blocks;
import org.gtlcore.gtlcore.common.data.GTLItems;
import org.slf4j.Logger;
import com.mojang.logging.LogUtils;
import com.sirin.hk3gtl.common.recipe.abyss.AbyssMaterialRecipes;
import com.sirin.hk3gtl.common.recipe.honkai.HonkaiMaterialRecipes;
import com.sirin.hk3gtl.common.recipe.honkai.HonkaiRecipes;
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
 */
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

        RecipeCycleDetector.reset();
        provider = RecipeCycleDetector.wrap(provider);
        Consumer<FinishedRecipe> approvedProvider = provider;
        provider = recipe -> {
            if (!Hk3ApprovedIndustrialPlans.isSuperseded(recipe.getId())) approvedProvider.accept(recipe);
        };
        com.sirin.hk3gtl.common.recipe.machine.Hk3ResearchComputerRecipes.register(provider);
        com.sirin.hk3gtl.common.recipe.machine.Hk3SpectrumBootstrapRecipes.register(provider);
        com.sirin.hk3gtl.common.recipe.machine.Hk3LiquidLineControllerRecipes.register(provider);
        com.sirin.hk3gtl.common.recipe.machine.Hk3ControllerRecipes.register(provider);
        com.sirin.hk3gtl.common.recipe.machine.Hk3FunctionalItemRecipes.register(provider);

        // ── Layer 0: P1 基础产线 ──
        HonkaiRecipes.addAbsorptionRecipes(provider);
        HonkaiRecipes.addCondensationRecipes(provider);
        HonkaiRecipes.addNetworkInjectionRecipes(provider);
        SouliumRecipes.addSouliumProcessingRecipes(provider);
        addMachineRecipes(provider);
        com.sirin.hk3gtl.common.recipe.machine.Hk3VoltageCasingRecipes.register(provider);
        com.sirin.hk3gtl.common.recipe.machine.Hk3ColoredCasingRecipes.register(provider);
        com.sirin.hk3gtl.common.recipe.main.Hk3MainMaterialRecipes.register(provider);
        com.sirin.hk3gtl.common.recipe.main.Hk3MainComponentRecipes.register(provider);
        Hk3ElectronicRecipes.register(provider);

        // ── Layer 2: 核心材料生产链 ──
        HonkaiMaterialRecipes.register(provider);

        // ── Layer 3: 海渊功能中间件 ──
        AbyssMaterialRecipes.register(provider);

        // ── Layer 4: 海渊 II~IV 八大件 ──




        // ── GT标准机中的虚数材料机壳与组件配方 ──





        // 旧量子阶段入口已删除；其GT机壳配方仍有当前材料用途，独立保留。
        // 量子 I~IV 八大件产线：补齐此前缺失的量子组件生产（原 robot_arm 配方消耗的量子电机无来源），打通量子组装链




        Hk3ResearchProcessRecipes.register(approvedProvider);

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
        Hk3RecipePower.require(GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder("hk3gtl_narrative_codex")
                .inputItems(new ItemStack(Items.BOOK, 1))
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(262144))
                .outputItems(Hk3Items.NARRATIVE_CODEX.get().getDefaultInstance())
                .duration(1200)
                .EUt(HBV_EUT), Hk3Tiers.HBV).save(provider);
    }





}
