package com.sirin.hk3gtl.common.machine.research;

/** 【变更记录 #7】2026-10-01 00:14:30（修订122）：删除无；新增/修改：合并配方保留稳定化子批次，公开不会混入同机其他工艺；用途：五方首信与真实批次分开记账，防止错误公开。 */

/** 【变更记录 #6】2026-10-01 00:14:30（修订122）：删除无；新增/修改：真实稳定化输出留下投入/产出与副产物规格，不凭空补出回收状态；用途：真实成果、团队授权与个人阅读分离，不开放贸易或免费完成研究。 */



/**
 * 【文件职责／本轮边界】I03至I05真实输出结算按固定团队授权并记录来源，离线不伪造或漏记已完成实验。
 * 【变更记录 #4】2026-09-29 21:06:40（第 4 次编号备注 · 内测5修订100）
 * 删除：取消已被批准规则替代的研究个人独占、旧数值或在线限定分支；历史备注与其他系统保留。
 * 新增／修改：I03至I05真实输出结算按固定团队授权并记录来源，离线不伪造或漏记已完成实验。
 * 用途：接通实际证据→付款→研究完成与权限检查；不授予缺真实证据的课题。
 * 边界：编译和账本测试不代表游戏验收；S02至S05正式结构及未接线课题仍未完成。
 * 追溯：logs/research-mainline-r100；R100_FINAL_RECORD。
 */

/** 修订100 · 2026-09-29：接通团队研究归属、个人付款及真实实验来源。 */

import com.gregtechceu.gtceu.api.capability.recipe.IO;
import com.gregtechceu.gtceu.api.machine.IMachineBlockEntity;
import com.gregtechceu.gtceu.api.machine.trait.RecipeLogic;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.gregtechceu.gtceu.api.recipe.logic.OCParams;
import com.gregtechceu.gtceu.api.recipe.logic.OCResult;
import com.sirin.hk3gtl.common.machine.Hk3MultiRecipeLogic;
import com.sirin.hk3gtl.common.machine.Hk3WorkableMultiblockMachine;
import com.sirin.hk3gtl.common.machine.ParallelData;
import com.sirin.hk3gtl.common.communication.Hk3CommunicationData;
import com.sirin.hk3gtl.common.research.Hk3ResearchData;
import com.sirin.hk3gtl.common.research.Hk3RecipeAccess;
import com.sirin.hk3gtl.common.research.Hk3ResearchRequirementPolicy;
import com.sirin.hk3gtl.common.research.Hk3ProcessReceipts;
import com.sirin.hk3gtl.common.research.Hk3ResearchRecipeRuntime;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.StringTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import java.math.BigInteger;
import java.util.LinkedHashSet;
import java.util.Set;

/**
 * 第一条工业线的归属、实验和批次结算入口；仅在真实输出成功后授予实验证据。
 * 【变更记录 #1】2026-09-24 16:36:00（内测5修订66）
 * 删除：不再依靠持有产物推测实验。新增：多配方原始研究权限和实验集合持久化。
 * 修改：输出阻塞时保留完成批次，停止再次扣料；注入量按各原配方实际并行求和。
 * 用途：离线、缺研究、模拟匹配及中断不能提前获得实验；首轮信息缺失时拒绝运行。
 *
 * 【变更记录 #2】2026-09-24 17:22:00（内测5修订66）
 * 删除：完成时借用handleRecipeIO输出的调用，GTL已将该方法改写成输入结算。
 * 新增：真实输出助手的成功回调、批次结算标志和单配方回退的实际并行产额。
 * 修改：完成前只模拟容量，输出交由GTL单次提交；启动时复制元数据并清除旧标志。
 * 用途：修复已扣料但没有产出的卡机，避免回退批处理少记网络余额及重复记账。
 *
 * 【变更记录 #3】2026-09-24 17:26:25（内测5修订66）
 * 删除：仅用外层并行计数推算网络产额的方法。
 * 新增：按原配方与最终批次首项消耗的精确比例计算产额，非整数比例拒绝结算。
 * 修改：同时覆盖部件倍乘、跨配方倍乘与GTL批处理；用途：使记账与实际扣料一致。
 */
/**
 * 【变更记录 #5】2026-09-29 23:37:35（内测5修订101）
 * 删除：本轮被替代的单前置或旧提示分支；其余历史保留。
 * 新增／修改：保留合并批次的全部权限与工艺回执，真实输出完成才结算研究实验及三类回收来源。
 * 用途：补足研究接线并如实保留未接物理执行器及结构审批边界。
 * 追溯：logs/research-mainline-r101；R101_FINAL_RECORD。
 */
public class Hk3LiquidProcessMachine extends Hk3WorkableMultiblockMachine {
    public static final String EXPERIMENT="hk3gtlExperiment", EXPERIMENTS="hk3gtlExperiments";
    public static final String REQUIREMENTS=Hk3ResearchRequirementPolicy.METADATA_KEY, CREDIT="hk3gtlNetworkCredit";
    private static final String SETTLED="hk3gtlLiquidOutputSettled";
    public Hk3LiquidProcessMachine(IMachineBlockEntity holder) { super(holder); }
    @Override public boolean keepSubscribing() { return true; }

    protected ServerPlayer informedOwner() {
        if(isRemote()||getLevel()==null||getLevel().getServer()==null||getOwnerUUID()==null)return null;
        var owner=getLevel().getServer().getPlayerList().getPlayer(getOwnerUUID());
        return owner!=null&&Hk3CommunicationData.get(owner).state(owner.getUUID()).hasObservationData()?owner:null;
    }
    protected boolean hasObservationData() {
        return !isRemote() && getLevel()!=null && getLevel().getServer()!=null && getOwnerUUID()!=null
                && Hk3CommunicationData.get(getLevel().getServer()).state(getOwnerUUID()).hasObservationData();
    }
    /** 修订163 · 2026-10-17 15:07:22：检查全部注册与批次门槛，旧ID和错误列表不能绕过。 */
    private boolean allowed(GTRecipe recipe) {
        if(!hasObservationData()||recipe==null)return false;
        if(!Hk3ResearchRecipeRuntime.allowed(this,recipe))return false;
        return !Hk3RecipeAccess.blocks(recipe,this);
    }
    @Override public boolean beforeWorking(GTRecipe recipe) { return allowed(recipe)&&super.beforeWorking(recipe); }

    /** 保留全部输出，由真实仓容量决定并行量；禁止trimRecipeOutputs静默丢掉副产物。 */
    @Override public GTRecipe fullModifyRecipe(GTRecipe recipe,OCParams params,OCResult result) {
        if(!allowed(recipe))return null;
        return doModifyRecipe(recipe.copy(),params,result);
    }
    /** 输出结算后更新幂等实验集合；不是研究完成授权，开题仍需正常付费。 */
    protected void onProcessOutput(GTRecipe recipe) {
        if(!hasObservationData()||!isFormed()||getResearchTeamUUID()==null)return;
        Hk3ResearchRecipeRuntime.settled(this,recipe);
        var owner=informedOwner();
        Set<String> experiments=new LinkedHashSet<>();
        String single=recipe.data.getString(EXPERIMENT);if(!single.isBlank())experiments.add(single);
        for(var tag:recipe.data.getList(EXPERIMENTS,8))experiments.add(tag.getAsString());
        var data=Hk3ResearchData.get(getLevel().getServer());
        String facility=getLevel().dimension().location()+"@"+getPos();
        if(recipe.data.contains("hk3gtlCommunicationBatches")){
            for(var raw:recipe.data.getList("hk3gtlCommunicationBatches",10))com.sirin.hk3gtl.common.communication.Hk3CommunicationEvidence.get(getLevel().getServer()).record(getResearchTeamUUID(),"stabilization",Hk3ProcessReceipts.settle((net.minecraft.nbt.CompoundTag)raw,facility,getLevel().getGameTime()));
        }else if(recipe.data.getString(EXPERIMENT).equals("RN-LES"))com.sirin.hk3gtl.common.communication.Hk3CommunicationEvidence.get(getLevel().getServer()).record(getResearchTeamUUID(),"stabilization",Hk3ProcessReceipts.settle(Hk3ProcessReceipts.snapshot(recipe),facility,getLevel().getGameTime()));
        if (recipe.data.contains(Hk3ProcessReceipts.RECEIPTS)) {
            for (var raw:recipe.data.getList(Hk3ProcessReceipts.RECEIPTS,10)) {
                var receipt=(net.minecraft.nbt.CompoundTag)raw;
                data.recordRecovery(getResearchTeamUUID(),receipt.getString("Category"),
                        Hk3ProcessReceipts.settle(receipt,facility,getLevel().getGameTime()));
            }
        } else if (!Hk3ProcessReceipts.category(recipe).isBlank()) {
            data.recordRecovery(getResearchTeamUUID(),Hk3ProcessReceipts.category(recipe),
                    Hk3ProcessReceipts.settle(Hk3ProcessReceipts.snapshot(recipe),facility,getLevel().getGameTime()));
        }
        for(String topic:experiments)if(data.recordExperiment(getResearchTeamUUID(),topic,getLevel().dimension().location()+"@"+getPos()+"/"+recipe.id) && owner!=null)
            owner.sendSystemMessage(Component.translatable("hk3gtl.research.industrial_recorded",
                    Component.translatable("hk3gtl.research.topic."+topic.toLowerCase(java.util.Locale.ROOT))));
    }
    /** GTL直接调用输出助手，必须在其真实输出成功后回调，不能调用已被改写为输入的handleRecipeIO。 */
    public final void onLiquidOutputSettled(GTRecipe recipe) {
        if(recipe==null||recipe.data.getBoolean(SETTLED)||!allowed(recipe)||!isFormed())return;
        onProcessOutput(recipe);
        recipe.data.putBoolean(SETTLED,true);
    }
    /** 注入配方的消耗顺序在倍乘时保持不变；优先比较燃料流体，否则比较首项消耗物品。 */
    private static BigInteger creditFor(GTRecipe original,GTRecipe consumed) {
        long unit=original.data.getLong(CREDIT);
        if(unit<0)throw new IllegalArgumentException("网络注入产额不能为负数");
        if(unit==0)return BigInteger.ZERO;
        long base=0,actual=0;
        var fluids=original.getInputContents(com.gregtechceu.gtceu.api.capability.recipe.FluidRecipeCapability.CAP);
        for(int i=0;i<fluids.size();i++)if(fluids.get(i).chance>0) {
            var cap=com.gregtechceu.gtceu.api.capability.recipe.FluidRecipeCapability.CAP;
            base=cap.of(fluids.get(i).content).getAmount();
            actual=cap.of(consumed.getInputContents(cap).get(i).content).getAmount();break;
        }
        if(base==0) {
            var cap=com.gregtechceu.gtceu.api.capability.recipe.ItemRecipeCapability.CAP;
            var items=original.getInputContents(cap);
            for(int i=0;i<items.size();i++)if(items.get(i).chance>0) {
                base=cap.of(items.get(i).content).getItems()[0].getCount();
                actual=cap.of(consumed.getInputContents(cap).get(i).content).getItems()[0].getCount();break;
            }
        }
        if(base<=0||actual<base||actual%base!=0)throw new IllegalStateException("注入批次消耗比例无效："+original.id);
        return BigInteger.valueOf(unit).multiply(BigInteger.valueOf(actual/base));
    }
    @Override protected RecipeLogic createRecipeLogic(Object... args) { return new ProcessLogic(this); }

    /** 输出检查与元数据合并仅作用于本工业线，其他机器继续使用原有逻辑。 */
    protected static class ProcessLogic extends Hk3MultiRecipeLogic {
        protected final Hk3LiquidProcessMachine process;
        protected ProcessLogic(Hk3LiquidProcessMachine machine) { super(machine);process=machine; }
        @Override protected Set<GTRecipe> lookupRecipeSet() {
            var recipes=new LinkedHashSet<>(super.lookupRecipeSet());recipes.removeIf(r->!process.allowed(r));return recipes;
        }
        @Override protected GTRecipe buildFinalNormalRecipe(ParallelData plan) {
            var running=super.buildFinalNormalRecipe(plan);if(running==null)return null;
            Set<String> experiments=new LinkedHashSet<>(),requirements=new LinkedHashSet<>();
            BigInteger credit=BigInteger.ZERO;
            ListTag receipts=new ListTag();
            ListTag executionPlans=new ListTag();
            ListTag communicationBatches=new ListTag();
            for(int i=0;i<plan.getOriginRecipeList().size();i++) {
                var original=plan.getOriginRecipeList().get(i);long parallel=plan.getParallels()[i];
                if(parallel<=0)continue;
                String topic=original.data.getString(EXPERIMENT);if(!topic.isBlank())experiments.add(topic);
                if(topic.equals("RN-LES"))communicationBatches.add(Hk3ProcessReceipts.snapshot(plan.getProcessedRecipeList().get(i)));
                var originalRequirements=Hk3RecipeAccess.effectiveRequirements(original);
                if(!originalRequirements.valid())return null;
                requirements.addAll(originalRequirements.requirements());
                credit=credit.add(creditFor(original,plan.getProcessedRecipeList().get(i)));
                if (!Hk3ProcessReceipts.category(original).isBlank())
                    receipts.add(Hk3ProcessReceipts.snapshot(plan.getProcessedRecipeList().get(i)));
                if(!original.data.getString(Hk3ResearchRecipeRuntime.PLAN).isBlank()){
                    var snapshot=Hk3ResearchRecipeRuntime.snapshot(plan.getProcessedRecipeList().get(i));
                    snapshot.putString(Hk3ResearchRecipeRuntime.PLAN,original.data.getString(Hk3ResearchRecipeRuntime.PLAN));executionPlans.add(snapshot);
                }
            }
            running.data=running.data.copy();running.data.put(EXPERIMENTS,strings(experiments));
            running.data.put(REQUIREMENTS,strings(requirements));running.data.putString(CREDIT,credit.toString());
            running.data.put(Hk3ProcessReceipts.RECEIPTS,receipts);
            running.data.put(Hk3ResearchRecipeRuntime.MERGED,executionPlans);
            running.data.put("hk3gtlCommunicationBatches",communicationBatches);
            running.data.remove(SETTLED);return running;
        }
        private static ListTag strings(Set<String> values) {
            var list=new ListTag();values.forEach(v->list.add(StringTag.valueOf(v)));return list;
        }
        @Override public void setupRecipe(GTRecipe recipe) {
            // 续跑时必须用新副本清理输出标志，不修改仍在使用的上一批次。
            var next=recipe.copy();next.data=recipe.data.copy();next.data.remove(SETTLED);super.setupRecipe(next);
        }
        @Override protected boolean handleTickRecipeIO(GTRecipe recipe,IO io) {
            return process.allowed(recipe)&&super.handleTickRecipeIO(recipe,io);
        }
        @Override protected boolean handleRecipeIO(GTRecipe recipe,IO io) {
            if(!process.allowed(recipe))return false;
            boolean committed=super.handleRecipeIO(recipe,io);
            if(committed&&io==IO.IN&&!recipe.data.getBoolean("hk3gtlMergedPlan")
                    &&recipe.data.contains(CREDIT,net.minecraft.nbt.Tag.TAG_ANY_NUMERIC)) {
                // 使用注册原方与已经扣料的最终批次比较，不重复套用任何并行或批处理倍数。
                var original=recipe.recipeType.getRecipe(process.getLevel().getServer().getRecipeManager(),recipe.id);
                if(original==null)throw new IllegalStateException("注入原配方缺失："+recipe.id);
                recipe.data.putString(CREDIT,creditFor(original,recipe).toString());
            }
            return committed;
        }
        @Override public void onRecipeFinish() {
            if(lastRecipe==null)return;
            if(!process.allowed(lastRecipe)||!org.gtlcore.gtlcore.api.recipe.RecipeRunnerHelper.matchRecipeOutput(process,lastRecipe)) {
                setWaiting(Component.translatable("hk3gtl.machine.liquid_line.waiting_output"));return;
            }
            // GTL完成函数直接调用RecipeRunnerHelper输出；服务端同一调用栈中先模拟，再单次提交。
            // 成功回调由Hk3ResearchOutputMixin触发，避免误走GTL改写后的输入入口或重复输出。
            super.onRecipeFinish();
        }
    }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
