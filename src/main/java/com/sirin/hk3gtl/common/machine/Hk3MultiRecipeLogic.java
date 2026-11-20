package com.sirin.hk3gtl.common.machine;

/**
 * 
 * - 本模组多方块的"多配方同时运行 + 无限并行"配方逻辑（替换 GTCEu 原版单配方 RecipeLogic）。
 * - 关键调用链：WorkableMultiblockMachine.serverTick -> findAndHandleRecipe()（本类重写）
 *   -> lookupRecipeSet() 收集全量匹配配方 -> calculateParallels() 贪心/公平分配并行量
 *   -> buildFinalNormalRecipe() 构建合成配方 -> setupRecipe()
 *   -> onRecipeFinish() 一次性产出后立即重新批量匹配下一轮。
 *
 */

import com.gregtechceu.gtceu.api.capability.recipe.IO;
import com.gregtechceu.gtceu.api.capability.recipe.EURecipeCapability;
import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.gregtechceu.gtceu.api.machine.feature.IRecipeLogicMachine;
import com.gregtechceu.gtceu.api.machine.trait.RecipeLogic;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.gregtechceu.gtceu.api.recipe.GTRecipeType;
import com.gregtechceu.gtceu.api.recipe.content.Content;
import com.sirin.hk3gtl.common.capability.Hk3DualEnergyCosts;
import net.minecraft.network.chat.Component;
import org.slf4j.Logger;
import com.mojang.logging.LogUtils;
import org.gtlcore.gtlcore.api.recipe.RecipeRunnerHelper;

import java.util.*;
import java.util.function.Supplier;

/**
 * "多配方同时运行 + 无限并行"配方逻辑 —— GTLsupb 机制完整移植版。
 *
 * <h3>核心流程</h3>
 * <ol>
 *   <li>{@link #lookupRecipeSet()} —— 跨配方类型收集全部可匹配配方，研究门控过滤</li>
 *   <li>{@link #calculateParallels()} —— 贪心/公平分配，返回 {@link ParallelData}</li>
 *   <li>{@link #buildFinalNormalRecipe(ParallelData)} —— 构建最终合成配方</li>
 *   <li>{@link #setupRecipe(GTRecipe)} —— 交由 GTCEu 原生执行</li>
 * </ol>
 *
 * <h3>与 GTCEu 原版的区别</h3>
 * 原版 RecipeLogic.findAndHandleRecipe() 只挑第一个能跑的配方；
 * 本类把当前库存能匹配的所有配方各自并行后合并成一个合成配方，
 * 让机器同 tick 同时产出多种配方的产物。
 */
public class Hk3MultiRecipeLogic extends Hk3RecipeLogic {

    private static final Logger LOGGER = LogUtils.getLogger();

    private int diagTickCounter = 0;
    private boolean commitFailed;
    private CandidateScan candidateScan;
    private Set<GTRecipe> readyCandidates = Set.of();
    private static final int CANDIDATES_PER_PASS = 128;
    private static final long LOOKUP_BUDGET_NANOS = 500_000L;
    private static final java.util.concurrent.atomic.AtomicLong LOOKUP_REVISION = new java.util.concurrent.atomic.AtomicLong();

    private static final class CandidateScan {
        final List<GTRecipeType> types;
        final Set<GTRecipe> recipes = new LinkedHashSet<>();
        final long revision = LOOKUP_REVISION.get();
        long tick = Long.MIN_VALUE;
        int typeIndex;
        Iterator<GTRecipe> iterator = Collections.emptyIterator();

        CandidateScan(List<GTRecipeType> types) { this.types = types; }
    }

    public static void invalidateLookups() { LOOKUP_REVISION.incrementAndGet(); }
    protected final boolean pendingLookup() { return candidateScan != null; }

    @Override public void resetRecipeLogic() {
        candidateScan = null;
        super.resetRecipeLogic();
    }

    @Override public void inValid() {
        candidateScan = null;
        super.inValid();
    }

    private static final String MERGED_PLAN_KEY = "hk3gtlMergedPlan";
    public static final String PARALLEL_COUNT_KEY = "hk3gtlParallelCount";
    public static final String RECIPE_COUNT_KEY = "hk3gtlRecipeCount";

    private static final int DEFAULT_MAX_MERGED_RECIPES = Integer.MAX_VALUE;

    public Hk3MultiRecipeLogic(IRecipeLogicMachine machine) {
        super(machine);
    }

    // ── 可重写配置项 ──────────────────────────────────────────────────────

    /**
     * 返回分配策略，默认贪心（GREEDY）。
     * 子类可覆写为 {@link AllocationAlgorithm#FAIR} 实现公平分配。
     */
    protected AllocationAlgorithm allocateMethod() {
        return AllocationAlgorithm.GREEDY;
    }

    /**
     * 返回单次合并的配方数量上限。
     * 子类可覆写以放宽或收紧限制。
     */
    protected int getMaxMergedRecipes() {
        return DEFAULT_MAX_MERGED_RECIPES;
    }

    public boolean hasUnlimitedParallelism() {
        return getMaxParallel() == Integer.MAX_VALUE && getMaxMergedRecipes() == DEFAULT_MAX_MERGED_RECIPES;
    }

    // ── 主流程 ────────────────────────────────────────────────────────────

    @Override
    public void findAndHandleRecipe() {
        if (dispatchProbabilityOrder()) { candidateScan = null; return; }
        lastFailedMatches = null;

        lastRecipe = null;
        lastOriginRecipe = null;
        commitFailed = false;

        GTRecipe merged = getRecipe();
        if (pendingLookup()) { recipeDirty = true; return; }
        if (merged != null) {
            if (diagTickCounter % 200 == 0) {
                LOGGER.info("[HK3GTL-diag] findAndHandleRecipe 成功: type={} id={} dur={} eut={}",
                        merged.recipeType, merged.id, merged.duration, getRecipeEUt(merged));
            }
            setupRecipe(merged);
            if (getStatus() != Status.WORKING && diagTickCounter % 200 == 0) {
                LOGGER.warn("[HK3GTL-diag] 合并规划可匹配但启动未通过: recipe={} inputCommitFailed={} machine={} pos={}",
                        merged.id, commitFailed, getMachine().getDefinition().getId(), getMachine().getPos());
            }
        } else {
            if (diagTickCounter % 200 == 0) {
                LOGGER.warn("[HK3GTL-diag] findAndHandleRecipe 返回 null，回退原版单配方匹配: status={} machine={} pos={}",
                        getStatus(), getMachine().getDefinition().getId(), getMachine().getPos());
            }
            // 回退到原版 RecipeLogic 的配方匹配流程，确保 status/WAITING/error 提示正常
            fallbackToStandardMatch(searchRecipe());
        }
        diagTickCounter++;
        recipeDirty = false;
    }

    /**
     * 回退到原版 RecipeLogic 的逐个配方匹配流程。
     * <p>使用 {@link #checkMatchedRecipeAvailable} 逐个尝试，失败时自动填充
     * {@code lastFailedMatches} 列表（与 GTCEu 原版 handleSearchingRecipes 行为一致）。
     * 原版 {@code serverTick()} 会在此之后自动重试失败列表中的配方，实现"等待条件满足"语义。</p>
     */
    private void fallbackToStandardMatch(Iterator<GTRecipe> matches) {
        while (matches != null && matches.hasNext()) {
            GTRecipe match = matches.next();
            if (match == null) continue;
            if (checkMatchedRecipeAvailable(match)) return;
            // 缓存失败配方，供 serverTick 后续重试（与原版 handleSearchingRecipes 一致）
            if (lastFailedMatches == null) {
                lastFailedMatches = new ArrayList<>();
            }
            lastFailedMatches.add(match);
        }
    }

    @Override
    public boolean checkMatchedRecipeAvailable(GTRecipe recipe) {
        boolean started = super.checkMatchedRecipeAvailable(recipe);
        if (started) lastFailedMatches = null;
        return started;
    }

    @Override
    protected boolean handleRecipeIO(GTRecipe recipe, IO io) {
        if (io == IO.IN && recipe.data.getBoolean(MERGED_PLAN_KEY)) {
            boolean matched = recipe.checkConditions(this).isSuccess()
                    && RecipeRunnerHelper.matchRecipe(machine, recipe)
                    && recipe.matchTickRecipe(machine).isSuccess();
            if (!matched) return false;
            boolean committed = Hk3RecipeCalculationHelper.commitInputs(machine, recipe);
            commitFailed = !committed;
            return committed;
        }
        return super.handleRecipeIO(recipe, io);
    }

    @Override
    public void onRecipeFinish() {
        if (lastRecipe != null) {
            markLastRecipeDirty();
            lastOriginRecipe = null;
        }
        super.onRecipeFinish();
    }

    /**
     * 完整流程：lookupRecipeSet → calculateParallels → buildFinalNormalRecipe。
     *
     * @return 可直接执行的合成配方，或 null 表示无配方可跑
     */
    protected GTRecipe getRecipe() {
        if (!checkBeforeWorking()) {
            if (diagTickCounter % 200 == 0) {
                LOGGER.warn("[HK3GTL-diag] checkBeforeWorking() 返回 false，status={}", getStatus());
            }
            candidateScan = null;
            return null;
        }

        if (!advanceCandidateScan()) return null;
        Set<GTRecipe> recipeSet;
        try { recipeSet = lookupRecipeSet(); }
        finally { readyCandidates = Set.of(); }
        if (recipeSet == null || recipeSet.isEmpty()) {
            if (diagTickCounter % 200 == 0) {
                LOGGER.warn("[HK3GTL-diag] lookupRecipeSet() 返回空，机器类型={}",
                        getMachine().getDefinition().getId());
            }
            return null;
        }

        if (diagTickCounter % 200 == 0) {
            LOGGER.info("[HK3GTL-diag] lookupRecipeSet 找到 {} 个配方", recipeSet.size());
        }

        ParallelData parallelData = calculateParallels(recipeSet);
        if (parallelData == null || !parallelData.isValid()) {
            if (diagTickCounter % 200 == 0) {
                LOGGER.warn("[HK3GTL-diag] calculateParallels() 返回 null/invalid ({} 个输入配方)", recipeSet.size());
            }
            return null;
        }

        return buildFinalNormalRecipe(parallelData);
    }

    // ── 阶段 1：配方集收集 ────────────────────────────────────────────────

    /**
     * 收集当前机器所有可匹配的配方。
     *
     * <p>支持多配方类型：若机器实现了 {@link IMultiTypeRecipeMachine}，
     * 则遍历其声明的全部 {@link GTRecipeType}；否则回退到原版单类型搜索。</p>
     *
     * <p>研究门控在此阶段过滤：已匹配但被研究锁定的配方不进入后续分配。</p>
     *
     * @return 去除研究锁定后的可执行配方集合
     */
    protected Set<GTRecipe> lookupRecipeSet() { return readyCandidates; }

    private boolean advanceCandidateScan() {
        MetaMachine holder = getMachine();
        var extended = holder instanceof IMultiTypeRecipeMachine multi ? multi.getExtendRecipeTypes() : List.<GTRecipeType>of();
        List<GTRecipeType> types = extended != null && !extended.isEmpty() ? extended
                : machine.getRecipeType() == null ? List.of() : List.of(machine.getRecipeType());
        if (candidateScan == null || candidateScan.revision != LOOKUP_REVISION.get() || !candidateScan.types.equals(types))
            candidateScan = new CandidateScan(new ArrayList<>(types));
        var scan = candidateScan;
        long tick = holder.getLevel().getGameTime();
        if (scan.tick == tick) return false;
        scan.tick = tick;
        long deadline = System.nanoTime() + LOOKUP_BUDGET_NANOS;
        int max = getMaxMergedRecipes(), visited = 0;
        while (scan.recipes.size() < max) {
            if (visited > 0 && (visited >= CANDIDATES_PER_PASS || System.nanoTime() >= deadline)) return false;
            if (!scan.iterator.hasNext()) {
                if (scan.typeIndex == scan.types.size()) break;
                var type = scan.types.get(scan.typeIndex++);
                if (type != null) {
                    var iterator = type.getLookup().getRecipeIterator(machine, recipe -> true);
                    if (iterator != null) scan.iterator = iterator;
                }
                visited++;
                continue;
            }
            var recipe = scan.iterator.next();
            if (recipe != null && !isResearchBlocked(recipe)) scan.recipes.add(recipe);
            visited++;
        }
        candidateScan = null;
        readyCandidates = scan.recipes;
        return true;
    }

    // ── 阶段 2：并行量分配 ────────────────────────────────────────────────

    /**
     * 对配方集进行并行量分配，返回 {@link ParallelData}。
     *
     * <p>分配策略由 {@link #allocateMethod()} 决定：</p>
     * <ul>
     *   <li>GREEDY：贪心分配，高吞吐</li>
     *   <li>FAIR：公平分配，均衡产出</li>
     * </ul>
     */
    protected ParallelData calculateParallels(Set<GTRecipe> recipeSet) {
        long maxParallel = getMaxParallel();
        if (maxParallel <= 0) return null;

        return switch (allocateMethod()) {
            case FAIR -> Hk3RecipeCalculationHelper.calculateParallelsWithFairAllocation(
                    recipeSet, maxParallel, this.machine,
                    this::fullModify, Hk3RecipeCalculationHelper::calculateParallel
            );
            case GREEDY -> Hk3RecipeCalculationHelper.calculateParallelsWithGreedyAllocation(
                    recipeSet, maxParallel, this.machine,
                    this::fullModify, Hk3RecipeCalculationHelper::calculateParallel
            );
        };
    }

    /**
     * 获取最大总并行量。
     * 默认使用 Integer.MAX_VALUE（无限并行），由 GTCEu 按库存与输出空间裁剪。
     */
    protected long getMaxParallel() {
        return Integer.MAX_VALUE;
    }

    /** 对配方执行超频+并行修改，返回修改后的配方副本 */
    private GTRecipe fullModify(GTRecipe raw) {
        GTRecipe copy = raw.copy();
        GTRecipe modified = machine.fullModifyRecipe(copy, ocParams, ocResult);
        if (modified != null) Hk3DualEnergyCosts.setMergedCost(modified,
                Hk3DualEnergyCosts.calculateMergedCost(List.of(raw), new long[]{1},
                        getMachine().getDefinition().getId().getPath()));
        return modified;
    }

    // ── 阶段 3：最终配方构建 ──────────────────────────────────────────────

    /**
     * 将 ParallelData 构建为最终的合成配方。
     *
     * <p>使用 {@link Hk3RecipeCalculationHelper#buildNormalRecipe} 将多个
     * 已处理（倍乘后）的配方合并为一个完整的 GTRecipe。</p>
     */
    protected GTRecipe buildFinalNormalRecipe(ParallelData parallelData) {
        GTRecipeType recipeType = null;
        List<GTRecipe> processed = parallelData.getProcessedRecipeList();
        if (processed != null && !processed.isEmpty()) {
            recipeType = processed.get(0).recipeType;
        }
        if (recipeType == null) {
            List<GTRecipe> origin = parallelData.getOriginRecipeList();
            if (origin != null && !origin.isEmpty()) {
                recipeType = origin.get(0).recipeType;
            }
        }

        GTRecipe merged = Hk3RecipeCalculationHelper.buildNormalRecipe(parallelData, recipeType);
        if (merged == null) {
            if (diagTickCounter % 200 == 0) {
                LOGGER.warn("[HK3GTL-diag] buildNormalRecipe 返回 null，processed数={} origin数={}",
                        processed != null ? processed.size() : 0,
                        parallelData.getOriginRecipeList() != null ? parallelData.getOriginRecipeList().size() : 0);
            }
            return null;
        }

        if (!merged.checkConditions(this).isSuccess()) {
            if (diagTickCounter % 200 == 0) {
                LOGGER.warn("[HK3GTL-diag] 合并配方条件校验失败: {}", merged.id);
            }
            return null;
        }
        if (!RecipeRunnerHelper.matchRecipe(this.machine, merged)) {
            if (diagTickCounter % 200 == 0) {
                LOGGER.warn("[HK3GTL-diag] matchRecipe 失败: {} dur={} eut={}",
                        merged.id, merged.duration, getRecipeEUt(merged));
            }
            return null;
        }
        var tickMatchResult = merged.matchTickRecipe(this.machine);
        if (!tickMatchResult.isSuccess()) {
            if (diagTickCounter % 200 == 0) {
                LOGGER.warn("[HK3GTL-diag] matchTickRecipe 失败: {} reason={}",
                        merged.id,
                        describeFailureReason(tickMatchResult));
            }
            return null;
        }

        // 将原配方成本与实际并行量写入最终运行副本；包括 0，避免 Mixin 错误回退机器默认值。
        GTRecipe runningRecipe = merged.copy();
        Hk3DualEnergyCosts.setMergedCost(runningRecipe, Hk3DualEnergyCosts.calculateMergedCost(
                parallelData.getOriginRecipeList(),
                parallelData.getParallels(),
                getMachine().getDefinition().getId().getPath()));

        // setMergedCost已复制data；保留完整输入，正式启动后由handleRecipeIO统一扣料。
        runningRecipe.data.putBoolean(MERGED_PLAN_KEY, true);
        return runningRecipe;
    }

    /**
     * GTCEu 1.20.1 将 EU/t 存为每 tick 的 EURecipeCapability 内容，而不是 GTRecipe 字段。
     */
    private static long getRecipeEUt(GTRecipe recipe) {
        long inputEU = getFirstEUContent(recipe.getTickInputContents(EURecipeCapability.CAP));
        if (inputEU != 0L) return inputEU;

        return -getFirstEUContent(recipe.getTickOutputContents(EURecipeCapability.CAP));
    }

    private static long getFirstEUContent(List<Content> contents) {
        if (contents == null || contents.isEmpty()) return 0L;
        Object value = contents.get(0).getContent();
        return value instanceof Number number ? number.longValue() : 0L;
    }

    private static String describeFailureReason(GTRecipe.ActionResult result) {
        Supplier<Component> reason = result.reason();
        if (reason == null) return "?";
        return reason.get().getString();
    }

    // ── 深度诊断 ──────────────────────────────────────────────────────────

    // ── 研究门控 ──────────────────────────────────────────────────────────

    /**
     * 判断配方是否被研究门控拦截。
     * 使用机器持久化 owner 判断研究权限；无法确认权威账户时 fail-closed。
     */
    protected boolean isResearchBlocked(GTRecipe recipe) {
        try {
            return com.sirin.hk3gtl.common.research.Hk3RecipeAccess.blocks(recipe, getMachine());
        } catch (Exception e) {
            LOGGER.warn("[HK3GTL] 跨配方研究门控异常，已阻止候选配方。recipe={}", recipe.id, e);
            return true;
        }
    }

    // ── 前置条件检查 ──────────────────────────────────────────────────────

    /**
     * 检查机器是否可以开始工作。
     * 参考 GTLsupb MutableRecipesLogic.checkBeforeWorking()。
     */
    protected boolean checkBeforeWorking() {
        MetaMachine m = getMachine();
        return m.getLevel() != null
                && !m.getLevel().isClientSide()
                && getStatus() != Status.WORKING;
    }
}
