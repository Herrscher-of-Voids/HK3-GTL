package com.sirin.hk3gtl.common.machine;



/**
 * 【文件职责】
 * - 本模组多方块的"多配方同时运行 + 无限并行"配方逻辑（替换 GTCEu 原版单配方 RecipeLogic）。
 * - 关键调用链：WorkableMultiblockMachine.serverTick -> findAndHandleRecipe()（本类重写）
 *   -> lookupRecipeSet() 收集全量匹配配方 -> calculateParallels() 贪心/公平分配并行量
 *   -> buildFinalNormalRecipe() 构建合成配方 -> setupRecipe()
 *   -> onRecipeFinish() 一次性产出后立即重新批量匹配下一轮。
 *
 * 【变更记录 #2】2026-06-28（第 2 次备注 · GTLsupb 机制完整移植）
 * - 删除：
 *   1) 旧的 lookupMergedRecipe / mergeTwo / mergeInto / isResearchBlocked 内联实现。
 * - 新增：
 *   1) 完整移植 GTLsupb 的 "无限并行 + 无限跨配方" 核心机制：
 *      - lookupRecipeSet()：支持单/多配方类型跨类型搜索（via IMultiTypeRecipeMachine）
 *      - calculateParallels()：贪心(GREEDY)/公平(FAIR) 两种能量-输入分配策略
 *      - buildFinalNormalRecipe()：将 ParallelData 构建为可直接执行的合成配方
 *   2) Hk3RecipeCalculationHelper 工具类：multipleRecipe / calculateParallel /
 *      calculateParallelsWithGreedyAllocation / calculateParallelsWithFairAllocation /
 *      buildNormalRecipe 等核心算法
 *   3) 新增 allocateMethod() 可重写方法，允许子机选择 GREEDY 或 FAIR 分配算法
 *   4) 新增 getMaxMergedRecipes() 可重写方法，允许子机调整单次合并配方上限
 * - 修改：
 *   1) findAndHandleRecipe() 采用新流程：lookupRecipeSet -> calculateParallels -> buildFinalNormalRecipe
 *   2) 保留研究门控在 lookupRecipeSet 阶段过滤，不将未解锁配方纳入 ParallelData
 *   3) duration 保持取所有组件最大值（玩法定案：不额外提速，仅"同时跑多种"便利）
 * - 用途：
 *   1) 让继承 Hk3WorkableMultiblockMachine 且 enableMultiRecipe() 为 true 的制造类多方块获得
 *      完整的 GTLsupb 级别跨配方+无限并行能力。
 *   2) 关键风险点：合成配方的 chance 逻辑保留首个组件的设置；
 *      handleRecipeWorking 不重写，确保研究门控/虚数锚定/注视度三个 Mixin 节流继续生效。
 *
 * 【变更记录 #3】2026-07-02 14:20:00（第 3 次备注 · 内测三第 24 次更新）
 * - 删除：
 *   1) 删除 onRecipeFinish() 重写。原重写版产出后手动置 IDLE，但无法访问父类私有字段 isActive，
 *      导致机器完成配方后渲染状态永远卡在"活跃"；且缺失原版 alwaysTryModifyRecipe 语义。
 *      现在直接使用父类实现（父类会 markLastRecipeDirty → IDLE → 下一 tick 重新进入本类批量匹配）。
 * - 新增：
 *   1) findAndHandleRecipe() 头部补回原版"续跑上一配方"快路径：上一合成配方仍可满足时直接 setupRecipe，
 *      不再每轮全量重搜+重合并（原版对齐 + 性能）。
 *   2) deepDiagnoseEmptyLookup()：配方搜索为空时（这是本次"机器不执行配方"的实际卡点，
 *      发生在原版 searchRecipe 层而非合并层），从 RecipeManager 拉取该类型全部配方，
 *      逐个输出 matchRecipe/matchTickRecipe 的具体拒绝原因 + hasProxies + IN 侧能力代理清单，
 *      一次运行即可定位：电路未设置 / 能源不足 / 仓室代理未挂载。
 * - 修改：
 *   1) getRecipe() 空集分支改为调用 deepDiagnoseEmptyLookup()（保留 200 tick 采样节流）。
 * - 用途：
 *   1) 修复产出后活跃状态残留；把"搜索层失败"从黑盒变成日志可读的确定性结论。
 *   2) 关键风险点：深度诊断走 RecipeManager.getAllRecipesFor，仅在空集+采样命中时执行，不影响正常 tick 性能。
 *
 * 【段内说明】
 * - mergeInto/mergeTwo：仅做 Content 列表拼接 + duration 取大 + 条件并集，IO 正确性完全交给 GTCEu 原生处理。
 *
 * 【变更记录 #4】2026-07-19 15:35:56（第 4 次备注 · 内测四第 30 次更新）
 * - 删除：
 *   1) 删除“分配阶段已逐配方扣料、最终阶段只校验输出”的非事务流程。
 *   2) 删除最终提交失败后继续回退普通配方的路径，避免底层能力已部分落账时再启动另一配方。
 * - 新增：
 *   1) buildFinalNormalRecipe() 在完整合并配方上依次执行条件、一次性 I/O、tick I/O 模拟，全部成功后统一调用 commitInputs()。
 *   2) commitFailed 标记区分“无匹配”与“输入提交异常”，提交异常时当前 tick 直接停止并限频记录机器位置。
 * - 修改：
 *   1) 提交成功后才清除运行副本的一次性 inputs；输出与 tickInputs/tickOutputs 原样交给 GTCEu RecipeLogic 执行。
 *   2) 主流程改为严格两阶段提交：规划阶段不写库存，提交阶段只对最终合并输入落账一次。
 * - 用途：
 *   1) 修复最终输出满、tick 条件变化或共享输入冲突时的玩家物资吞失。
 *   2) 保持 GTLCore 对 ME 样板输入和 ME 输出内部缓冲的匹配/消费兼容入口不变。
 *
 * 【变更记录 #5】2026-07-19 19:16:14（第 5 次备注 · 内测四第 31 次更新）
 * - 删除：
 *   1) 删除最终合成配方只携带首个 recipe id、导致崩坏能默认成本仅结算一次的行为。
 * - 新增：
 *   1) 根据 ParallelData 原配方列表与实际并行量计算 Σ(cost×parallel)，并写入运行配方权威 BigInteger 成本字段。
 * - 修改：
 *   1) 成本计算和 NBT 写入发生在一次性输入提交前；异常时不消费输入，也不启动无计费元数据的配方。
 * - 用途：
 *   1) 让跨配方、单配方高并行和配方级成本覆盖都按真实产能逐 tick 结算崩坏能。
 *
 * 【变更记录 #6】2026-07-19 19:40:31（第 6 次备注 · 内测四第 32 次更新）
 * - 删除：
 *   1) 删除通过 IRecipeLogicMachine 静态类型直接调用 getDefinition() 的无效代码。
 * - 新增：
 *   1) 无。
 * - 修改：
 *   1) 合并成本机器 ID 改从 RecipeLogic#getMachine() 返回的 MetaMachine 获取，保持与本类其他诊断和查找路径一致。
 * - 用途：
 *   1) 修复 runClient 重新编译时的 cannot find symbol，并确保机器默认崩坏能成本仍使用实际控制器 ID。
 *
 * 【变更记录 #7】2026-07-19 21:49:23（第 7 次备注 · revision 35）
 * - 删除：
 *   1) 删除跨配方候选过滤按 64 格最近玩家判断研究权限的逻辑。
 * - 新增：
 *   1) 新增基于 Hk3WorkableMultiblockMachine 持久化 ownerUUID 的在线 owner 查询。
 * - 修改：
 *   1) owner 未绑定、离线或研究未完成时阻止对应候选进入合并规划；异常改为 fail-closed。
 * - 用途：
 *   1) 让候选过滤与 RecipeLogic 最终工作守卫使用同一研究账户，避免站位改变权限或绕过研究。
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
/** 中文说明：该处说明已按当前代码行为整理。*/
/** 中文说明：该处说明已按当前代码行为整理。*/
/** 中文说明：该处备注已按当前代码行为整理，不使用问号占位。*/
/**
 * 【变更记录 #8】2026-09-29 23:37:35（内测5修订101）
 * 删除：本轮被替代的单前置或旧提示分支；其余历史保留。
 * 新增／修改：多配方采用统一研究权限检查，修复离线绑定人导致的旧式阻塞。
 * 用途：补足研究接线并如实保留未接物理执行器及结构审批边界。
 * 追溯：logs/research-mainline-r101；R101_FINAL_RECORD。
 */
/**
 * 【变更记录 #9】2026-10-01 17:33:35（修订138）
 * 删除：对丢弃tick提交结果的原始父类直接继承；新增：共用Hk3RecipeLogic实际提交检查。
 * 修改：仅切换父类，不改并行分配和一次性投入；用途：多配方及液态工序实际扣能失败时不推进。
 */
public class Hk3MultiRecipeLogic extends Hk3RecipeLogic {

    private static final Logger LOGGER = LogUtils.getLogger();

    private int diagTickCounter = 0;
    private boolean commitFailed;

    /** 中文说明：该处说明已按当前代码行为整理。*/
    private static final String MERGED_PLAN_KEY = "hk3gtlMergedPlan";

    /** 中文说明：该处说明已按当前代码行为整理。*/
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

    // ── 主流程 ────────────────────────────────────────────────────────────

    /** 中文说明：该处说明已按当前代码行为整理。*/
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

    /** 中文说明：该处说明已按当前代码行为整理。*/
    @Override
    protected boolean handleRecipeIO(GTRecipe recipe, IO io) {
        if (io == IO.IN && recipe.data.getBoolean(MERGED_PLAN_KEY)) {
            // 中文备注：该处说明已按当前代码行为整理。
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

    /** 中文说明：该处说明已按当前代码行为整理。*/
    @Override
    public void onRecipeFinish() {
        if (lastRecipe != null && lastRecipe.data.getBoolean(MERGED_PLAN_KEY)) {
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

        // 中文备注：该处说明已按当前代码行为整理。
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
        // 中文备注：该处说明已按当前代码行为整理。
        runningRecipe.data.putBoolean(MERGED_PLAN_KEY, true);
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
                var itemCap = com.gregtechceu.gtceu.api.capability.recipe.ItemRecipeCapability.CAP;
                for (Content required : r.inputs.getOrDefault(itemCap, List.of())) {
                    var ingredient = (net.minecraft.world.item.crafting.Ingredient) required.content;
                    LOGGER.warn("[HK3-INPUT] recipe={} ingredient={} chance={}", r.id,
                            ingredient.toJson(), required.chance);
                    for (var handler : this.machine.getCapabilitiesProxy().get(IO.IN, itemCap)) {
                        var leftover = handler.handleRecipe(IO.IN, r, List.of(ingredient), required.slotName, true);
                        LOGGER.warn("[HK3-INPUT] handler={} contents={} accepts={}", handler.getClass().getName(),
                                handler.getContents(), leftover == null || leftover.isEmpty());
                    }
                }
                boolean coreMatch = RecipeRunnerHelper.matchRecipe(this.machine, r);
                var t = r.matchTickRecipe(this.machine);
                LOGGER.warn("[HK3GTL-diag][deep] 配方 {}: nativeMatch={}({}) coreMatch={} matchTick={}({})",
                        r.id,
                        m.isSuccess(), m.isSuccess() ? "-" : describeFailureReason(m),
                        coreMatch,
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
