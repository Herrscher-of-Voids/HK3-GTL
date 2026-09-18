package com.sirin.hk3gtl.common.capability;

import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import net.minecraft.resources.ResourceLocation;
import org.slf4j.Logger;
import com.mojang.logging.LogUtils;

import javax.annotation.Nullable;
import java.math.BigInteger;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 双能源消耗登记表 —— 记录"哪些配方/机器在 EU 之外还要每 tick 扣多少崩坏能"。
 *
 * <h3>两级查找（配方级优先）</h3>
 * <ol>
 *   <li><b>配方级</b>：{@link #bindRecipe}，Key = 配方 ResourceLocation（即设计文档中的
 *       配方 {@code honkaiCost} 字段，与 {@link com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate}
 *       同一侧表模式，避免侵入 GTRecipe 序列化）</li>
 *   <li><b>机器级</b>：{@link #bindMachine}，Key = 机器注册 ID path（如 "soulium_smeltery"），
 *       作为该机器全部配方的默认值</li>
 * </ol>
 *
 * <h3>数值口径</h3>
 * 全部为"每 tick 崩坏能单位"（1 崩坏能 = 1000 EU），与 EUt 语义对齐。
 * 机器级默认值按四大阶段递增：海渊 64 → 虚数 256 → 量子 1024 → 终焉 4096。
 *
 * <h3>线程侧</h3>
 * 注册发生在启动期（单线程），查询发生在服务端 tick；用 ConcurrentHashMap 兜底。
 *
 * 【变更记录 #1】2026-07-19 19:16:14（第 1 次备注 · 内测四第 31 次更新）
 * - 删除：
 *   1) 删除合并配方只能按合成 recipe id 回查一次机器默认成本的错误语义。
 * - 新增：
 *   1) 新增 calculateMergedCost，按 Σ(原配方成本×实际并行量) 使用 BigInteger 精确求和。
 *   2) 新增权威成本 NBT 写入/读取 API，以十进制字符串保存任意精度每 tick 成本，零成本也明确记录。
 * - 修改：
 *   1) 写入成本前深复制 GTRecipe.data，避免 GTCEu copy() 共享 CompoundTag 时污染原始配方。
 * - 用途：
 *   1) 让 Hk3MultiRecipeLogic 将原配方身份和实际并行计费结果传递给 RecipeLogicMixin。
 */
public final class Hk3DualEnergyCosts {

    private static final Logger LOGGER = LogUtils.getLogger();
    private static final String MERGED_COST_KEY = "hk3gtlMergedHonkaiCostPerTick";

    /** 阶段默认档位：每 tick 崩坏能单位 */
    public static final long COST_ABYSS = 64L;
    public static final long COST_IMAGINARY = 256L;
    public static final long COST_QUANTUM = 1024L;
    public static final long COST_FINALITY = 4096L;
    public static final long COST_WONDER = 8192L;

    /** 配方级 honkaiCost：配方ID → 每 tick 崩坏能 */
    private static final Map<ResourceLocation, Long> RECIPE_COSTS = new ConcurrentHashMap<>();

    /** 机器级默认：机器注册 ID path → 每 tick 崩坏能 */
    private static final Map<String, Long> MACHINE_COSTS = new ConcurrentHashMap<>();

    private Hk3DualEnergyCosts() {
    }

    // ── 注册 API ─────────────────────────────────────────────────────────

    /** 配方级绑定：同时登记 gtceu:/hk3gtl: 两个命名空间（与研究门控 bind 同款约定） */
    public static void bindRecipe(String recipeType, String recipeId, long honkaiPerTick) {
        if (honkaiPerTick <= 0) return;
        RECIPE_COSTS.put(new ResourceLocation("gtceu", recipeType + "/" + recipeId), honkaiPerTick);
        RECIPE_COSTS.put(new ResourceLocation("hk3gtl", recipeType + "/" + recipeId), honkaiPerTick);
    }

    /** 机器级默认绑定 */
    public static void bindMachine(String machineIdPath, long honkaiPerTick) {
        if (honkaiPerTick <= 0) return;
        MACHINE_COSTS.put(machineIdPath, honkaiPerTick);
    }

    // ── 查询 API ─────────────────────────────────────────────────────────

    /**
     * 解析某配方在某机器上的每 tick 崩坏能消耗。
     *
     * @return 0 = 该配方不消耗崩坏能（纯 EU 机器）
     */
    public static long resolve(ResourceLocation recipeId, String machineIdPath) {
        if (recipeId != null) {
            Long perRecipe = RECIPE_COSTS.get(recipeId);
            if (perRecipe != null) return perRecipe;
        }
        if (machineIdPath != null) {
            Long perMachine = MACHINE_COSTS.get(machineIdPath);
            if (perMachine != null) return perMachine;
        }
        return 0L;
    }

    /** 机器是否登记为双能源机器（GUI 显示用） */
    public static long getMachineDefault(String machineIdPath) {
        Long v = MACHINE_COSTS.get(machineIdPath);
        return v == null ? 0L : v;
    }

    public static BigInteger calculateMergedCost(List<GTRecipe> originRecipes,
                                                  long[] parallels,
                                                  String machineIdPath) {
        if (originRecipes == null || parallels == null || originRecipes.size() != parallels.length) {
            throw new IllegalArgumentException("原配方与并行量必须一一对应");
        }
        BigInteger total = BigInteger.ZERO;
        for (int index = 0; index < originRecipes.size(); index++) {
            long parallel = parallels[index];
            if (parallel <= 0) throw new IllegalArgumentException("并行量必须大于零");
            GTRecipe recipe = originRecipes.get(index);
            long unitCost = resolve(recipe == null ? null : recipe.id, machineIdPath);
            total = total.add(BigInteger.valueOf(unitCost).multiply(BigInteger.valueOf(parallel)));
        }
        return total;
    }

    public static void setMergedCost(GTRecipe recipe, BigInteger cost) {
        if (recipe == null) throw new IllegalArgumentException("运行配方不能为空");
        BigInteger normalized = cost == null || cost.signum() < 0 ? BigInteger.ZERO : cost;
        recipe.data = recipe.data.copy();
        recipe.data.putString(MERGED_COST_KEY, normalized.toString());
    }

    /** null 表示普通配方没有权威合并成本，应回退原 recipe id/机器默认值。 */
    @Nullable
    public static BigInteger getMergedCost(GTRecipe recipe) {
        if (recipe == null || !recipe.data.contains(MERGED_COST_KEY)) return null;
        String encoded = recipe.data.getString(MERGED_COST_KEY);
        BigInteger cost = new BigInteger(encoded);
        if (cost.signum() < 0) throw new IllegalStateException("合并配方崩坏能成本不能为负数");
        return cost;
    }

    // ── 机器级默认注册（与《多方块结构总表 v0.3》能源列"EU+崩坏能"一一对应） ──

    /**
     * 登记全部双能源机器的默认崩坏能消耗。
     * <p>只登记"EU+崩坏能"消耗型机器；发电类（产出EU）与纯 EU 机器不登记。</p>
     * <p>由 {@link com.sirin.hk3gtl.Hk3Gtl} 在 commonSetup 阶段调用一次。</p>
     */
    public static void init() {
        // ── 海渊桶（64/t） ──
        bindMachine("soulium_smeltery", COST_ABYSS);
        bindMachine("reason_reconstruction_array", COST_ABYSS);
        bindMachine("abyss_deep_smeltery", COST_ABYSS);
        bindMachine("abyss_precision_workshop", COST_ABYSS);
        bindMachine("abyss_particle_research_ring", COST_ABYSS);

        // ── 虚数桶（256/t） ──
        bindMachine("imaginary_dimension_gateway", COST_IMAGINARY);
        bindMachine("imaginary_tree_observation_array", COST_IMAGINARY);
        bindMachine("imaginary_anchor_device", COST_IMAGINARY);
        bindMachine("sea_of_quanta_observatory", COST_IMAGINARY);
        bindMachine("imaginary_circuit_computation_sanctum", COST_IMAGINARY);
        bindMachine("soulium_superstructure_forge", COST_IMAGINARY);
        bindMachine("dual_energy_stable_supply_station", COST_IMAGINARY);
        bindMachine("imaginary_dream_furnace", COST_IMAGINARY);
        bindMachine("imaginary_matter_weaver", COST_IMAGINARY);

        // ── 量子桶（1024/t） ──
        bindMachine("quantum_entanglement_computer", COST_QUANTUM);
        bindMachine("thousand_realms_train", COST_QUANTUM);
        bindMachine("world_bubble_meltdown_furnace", COST_QUANTUM);
        bindMachine("quantum_superconductor_lattice_factory", COST_QUANTUM);
        bindMachine("quantum_thought_forge", COST_QUANTUM);
        bindMachine("finality_pressure_buffer_array", COST_QUANTUM);
        bindMachine("quantum_precision_assembly_factory", COST_QUANTUM);

        // ── 终焉桶（4096/t） ──
        bindMachine("hyperion_flagship", COST_FINALITY);
        bindMachine("finality_civilization_construction_works", COST_FINALITY);
        bindMachine("civilization_validation_matrix", COST_FINALITY);
        bindMachine("finality_civilization_power_hub", COST_FINALITY);
        bindMachine("finality_ultimate_material_forge", COST_FINALITY);
        bindMachine("graduation_permission_verification_altar", COST_FINALITY);
        bindMachine("civilization_wonder_sanctum", COST_FINALITY);

        // ── 奇观桶（8192/t，仅消耗型） ──
        bindMachine("destiny_loom", COST_WONDER);
        bindMachine("civilization_eye_observation_array", COST_WONDER);
        bindMachine("grand_convergence_altar", COST_WONDER);

        LOGGER.info("[HK3GTL] 双能源消耗登记完成：{} 台机器默认档 + {} 条配方级覆盖",
                MACHINE_COSTS.size(), RECIPE_COSTS.size() / 2);
    }
}
