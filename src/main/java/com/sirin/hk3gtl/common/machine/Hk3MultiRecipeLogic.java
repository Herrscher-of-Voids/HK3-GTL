package com.sirin.hk3gtl.common.machine;



import com.gregtechceu.gtceu.api.capability.recipe.IO;
import com.gregtechceu.gtceu.api.capability.recipe.EURecipeCapability;
import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.gregtechceu.gtceu.api.machine.feature.IRecipeLogicMachine;
import com.gregtechceu.gtceu.api.machine.trait.RecipeLogic;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.gregtechceu.gtceu.api.recipe.GTRecipeType;
import com.gregtechceu.gtceu.api.recipe.content.Content;
import com.sirin.hk3gtl.common.capability.Hk3DualEnergyCosts;
import com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate;
import com.sirin.hk3gtl.common.research.Hk3ResearchManager;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.Level;
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
public class Hk3MultiRecipeLogic extends RecipeLogic {

    private static final Logger LOGGER = LogUtils.getLogger();

    private int diagTickCounter = 0;
    private boolean commitFailed;

    /** 单次合并的配方数量上限，避免极端库存下遍历配方过多拖累 TPS。 */
    private static final int DEFAULT_MAX_MERGED_RECIPES = 16;

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

    // ── 主流程 ────────────────────────────────────────────────────────────

    /**
     * 重写配方查找：逐配方分配并处理一次性输入，再构建只负责运行和输出的合成配方。
     */
    @Override
    public void findAndHandleRecipe() {
        lastFailedMatches = null;

        lastRecipe = null;
        lastOriginRecipe = null;
        commitFailed = false;

        GTRecipe merged = getRecipe();
        if (merged != null) {
            if (diagTickCounter % 200 == 0) {
                LOGGER.info("[HK3GTL-diag] findAndHandleRecipe 成功: type={} id={} dur={} eut={}",
                        merged.recipeType, merged.id, merged.duration, getRecipeEUt(merged));
            }
            setupRecipe(merged);
        } else if (commitFailed) {
            if (diagTickCounter % 200 == 0) {
                LOGGER.error("[HK3GTL-diag] 合并配方输入提交失败，已停止本 tick 且不回退普通配方: machine={} pos={}",
                        getMachine().getDefinition().getId(), getMachine().getPos());
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

    // 不重写 onRecipeFinish：父类负责输出、标脏和复位；下一轮重新逐配方处理输入。

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
            return null;
        }

        Set<GTRecipe> recipeSet = lookupRecipeSet();
        if (recipeSet == null || recipeSet.isEmpty()) {
            if (diagTickCounter % 200 == 0) {
                LOGGER.warn("[HK3GTL-diag] lookupRecipeSet() 返回空，机器类型={}",
                        getMachine().getDefinition().getId());
                deepDiagnoseEmptyLookup();
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
    protected Set<GTRecipe> lookupRecipeSet() {
        MetaMachine machine = getMachine();

        // 多配方类型路径
        if (machine instanceof IMultiTypeRecipeMachine multi) {
            List<GTRecipeType> types = multi.getExtendRecipeTypes();
            if (types == null || types.isEmpty()) {
                return legacySingleTypeLookup();
            }

            Set<GTRecipe> all = new LinkedHashSet<>();
            int max = getMaxMergedRecipes();
            outer:
            for (GTRecipeType type : types) {
                if (type == null) continue;
                Iterator<GTRecipe> it = type.getLookup().getRecipeIterator(
                        this.machine,
                        r -> true
                );
                if (it == null) continue;
                while (it.hasNext()) {
                    if (all.size() >= max) break outer;
                    GTRecipe recipe = it.next();
                    if (recipe != null && !isResearchBlocked(recipe)) {
                        all.add(recipe);
                    }
                }
            }
            return all;
        }

        // 单配方类型路径（回退兼容）
        return legacySingleTypeLookup();
    }

    /**
     * 单配方类型候选收集：使用无匹配过滤的迭代器（r -> true）。
     * <p>不能用原版 {@code searchRecipe()}，它按普通库存匹配过滤会漏掉 ME 样板配方；
     * 由后续逐配方 {@link RecipeRunnerHelper} 处理来完成真正的输入匹配与消费。</p>
     */
    private Set<GTRecipe> legacySingleTypeLookup() {
        GTRecipeType type = machine.getRecipeType();
        if (type == null) return Collections.emptySet();
        Iterator<GTRecipe> it = type.getLookup().getRecipeIterator(this.machine, r -> true);
        if (it == null) return Collections.emptySet();

        Set<GTRecipe> set = new LinkedHashSet<>();
        int max = getMaxMergedRecipes();
        int count = 0;
        while (it.hasNext() && count < max) {
            GTRecipe recipe = it.next();
            if (recipe != null && !isResearchBlocked(recipe)) {
                set.add(recipe);
                count++;
            }
        }
        return set;
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
    private GTRecipe fullModify(GTRecipe raw) throws Exception {
        GTRecipe copy = raw.copy();
        return machine.fullModifyRecipe(copy, ocParams, ocResult);
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

        // 阶段一：对保留完整 inputs 的最终候选做统一模拟，任何失败都不会修改库存。
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
        GTRecipe runningRecipe = Hk3RecipeCalculationHelper.withoutProcessedInputs(merged);
        Hk3DualEnergyCosts.setMergedCost(runningRecipe, Hk3DualEnergyCosts.calculateMergedCost(
                parallelData.getOriginRecipeList(),
                parallelData.getParallels(),
                getMachine().getDefinition().getId().getPath()));

        // 阶段二：全部模拟和计费元数据构建通过后，只提交一次聚合输入。
        if (!Hk3RecipeCalculationHelper.commitInputs(this.machine, merged)) {
            commitFailed = true;
            return null;
        }
        return runningRecipe;
    }

    /**
     * GTCEu 1.20.1 将 EU/t 存为每 tick 的 EURecipeCapability 内容，而不是 GTRecipe 字段。
     */
    private static long getRecipeEUt(GTRecipe recipe) {
        if (recipe == null) return 0L;

        long inputEU = getFirstEUContent(recipe.getTickInputContents(EURecipeCapability.CAP));
        if (inputEU != 0L) return inputEU;

        long outputEU = getFirstEUContent(recipe.getTickOutputContents(EURecipeCapability.CAP));
        return outputEU == 0L ? 0L : -outputEU;
    }

    private static long getFirstEUContent(List<Content> contents) {
        if (contents == null || contents.isEmpty()) return 0L;
        Object value = contents.get(0).getContent();
        return value instanceof Number number ? number.longValue() : 0L;
    }

    private static String describeFailureReason(GTRecipe.ActionResult result) {
        if (result == null) return "?";
        Supplier<Component> reason = result.reason();
        if (reason == null) return "?";
        try {
            Component component = reason.get();
            return component == null ? "?" : component.getString();
        } catch (Exception ignored) {
            return "?";
        }
    }

    // ── 深度诊断 ──────────────────────────────────────────────────────────

    /**
     * 配方搜索为空时的深度诊断：绕过库存索引树，从 RecipeManager 直接取该类型全部配方，
     * 逐个输出 matchRecipe / matchTickRecipe 的具体拒绝原因。
     *
     * <p>用于区分三类根因：</p>
     * <ul>
     *   <li>hasProxies=false → 仓室能力代理没挂上（结构成型问题）</li>
     *   <li>matchRecipe 失败 → 输入不满足（最常见：编程电路未设置/物料不足）</li>
     *   <li>matchTickRecipe 失败 → 每 tick 输入不满足（最常见：能源仓供电不足）</li>
     * </ul>
     *
     * <p>仅在空集 + 200 tick 采样命中时执行，正式发布前应随其他诊断日志一并移除。</p>
     */
    private void deepDiagnoseEmptyLookup() {
        try {
            Level level = getMachine().getLevel();
            if (level == null || level.isClientSide()) return;

            GTRecipeType type = machine.getRecipeType();
            LOGGER.warn("[HK3GTL-diag][deep] type={} hasProxies={}", type.registryName, machine.hasProxies());

            // IN 侧能力代理清单：确认物品总线/能源仓是否真的挂进了 capabilitiesProxy
            var inRow = machine.getCapabilitiesProxy().row(IO.IN);
            if (inRow.isEmpty()) {
                LOGGER.warn("[HK3GTL-diag][deep] IN 侧没有任何能力代理（仓室未挂载）");
            } else {
                inRow.forEach((cap, handlers) -> LOGGER.warn("[HK3GTL-diag][deep] IN 能力 {}: {} 个 handler",
                        cap.name, handlers == null ? 0 : handlers.size()));
            }

            List<GTRecipe> all = getRecipeManager().getAllRecipesFor(type);
            LOGGER.warn("[HK3GTL-diag][deep] 数据包内该类型配方总数={}", all.size());
            int shown = 0;
            for (GTRecipe r : all) {
                if (shown++ >= 5) break;
                var m = r.matchRecipe(this.machine);
                var t = r.matchTickRecipe(this.machine);
                LOGGER.warn("[HK3GTL-diag][deep] 配方 {}: matchRecipe={}({}) matchTick={}({})",
                        r.id,
                        m.isSuccess(), m.isSuccess() ? "-" : describeFailureReason(m),
                        t.isSuccess(), t.isSuccess() ? "-" : describeFailureReason(t));
            }
        } catch (Throwable t) {
            LOGGER.warn("[HK3GTL-diag][deep] 深度诊断异常: {}", t.toString());
        }
    }

    // ── 研究门控 ──────────────────────────────────────────────────────────

    /**
     * 判断配方是否被研究门控拦截。
     * 使用机器持久化 owner 判断研究权限；无法确认权威账户时 fail-closed。
     */
    private boolean isResearchBlocked(GTRecipe recipe) {
        try {
            if (recipe.id == null) return false;
            String researchId = Hk3RecipeResearchGate.getRequiredResearch(recipe.id);
            if (researchId == null) return false;

            Level level = getMachine().getLevel();
            if (level == null || level.isClientSide()) return false;
            if (!(getMachine() instanceof Hk3WorkableMultiblockMachine ownedMachine)
                    || ownedMachine.getOwnerUUID() == null
                    || level.getServer() == null) {
                return true;
            }

            ServerPlayer owner = level.getServer().getPlayerList().getPlayer(ownedMachine.getOwnerUUID());
            return owner == null || !Hk3ResearchManager.isCompleted(owner, researchId);
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
