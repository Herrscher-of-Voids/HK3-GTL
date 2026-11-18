package com.sirin.hk3gtl.common.machine.research;

import com.sirin.hk3gtl.common.integration.ae.exact.Hk3ProbabilitySupport;




/**
 * 【文件职责／本轮边界】I03至I05真实输出结算按固定团队授权并记录来源，离线不伪造或漏记已完成实验。
 */


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
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.recipe.Hk3ResearchProcessEnergy;
import com.sirin.hk3gtl.common.research.Hk3ResearchData;
import com.sirin.hk3gtl.common.research.Hk3RecipeAccess;
import com.sirin.hk3gtl.common.research.Hk3ResearchRequirementPolicy;
import com.sirin.hk3gtl.common.research.Hk3ProcessReceipts;
import com.sirin.hk3gtl.common.research.Hk3ResearchRecipeRuntime;
import com.sirin.hk3gtl.common.research.Hk3OutputReceiptDispatch;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.StringTag;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import java.math.BigInteger;
import java.util.LinkedHashSet;
import java.util.Set;

/**
 * 第一条工业线的归属、实验和批次结算入口；仅在真实输出成功后授予实验证据。
 */
public class Hk3LiquidProcessMachine extends Hk3WorkableMultiblockMachine {
    public static final String EXPERIMENT="hk3gtlExperiment", EXPERIMENTS="hk3gtlExperiments";
    public static final String REQUIREMENTS=Hk3ResearchRequirementPolicy.METADATA_KEY, CREDIT="hk3gtlNetworkCredit";
    private static final String SETTLED="hk3gtlLiquidOutputSettled";
    private static final String REQUIRED_SETTLED="hk3gtlLiquidRequiredOutputSettled";
    public Hk3LiquidProcessMachine(IMachineBlockEntity holder) { super(holder); }
    @Override public boolean keepSubscribing() { return true; }
    @Override public long getMaxVoltage() {
        return Hk3Values.getV(Hk3ResearchProcessEnergy.executionVoltageTier(
                getDefinition().getRecipeTypes(), getDefinition().getTier()));
    }
    @Override public long getOverclockVoltage() { return getMaxVoltage(); }

    protected ServerPlayer informedOwner() {
        if(isRemote()||getLevel()==null||getLevel().getServer()==null||getOwnerUUID()==null)return null;
        var owner=getLevel().getServer().getPlayerList().getPlayer(getOwnerUUID());
        return owner!=null&&Hk3CommunicationData.get(owner).state(owner.getUUID()).hasObservationData()?owner:null;
    }
    protected boolean hasObservationData() {
        return !isRemote() && getLevel()!=null && getLevel().getServer()!=null && getOwnerUUID()!=null
                && Hk3CommunicationData.get(getLevel().getServer()).state(getOwnerUUID()).hasObservationData();
    }
    protected final boolean allowed(GTRecipe recipe) {
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
        Hk3OutputReceiptDispatch.dispatch(true,
                () -> recipe!=null&&!recipe.data.getBoolean(SETTLED)&&allowed(recipe)&&isFormed(),
                () -> {
                    // 必要入账成功与旁注完成分开，回执失败后重入不能重复发放HW。
                    if(!recipe.data.getBoolean(REQUIRED_SETTLED)) {
                        onRequiredProcessOutput(recipe);
                        recipe.data.putBoolean(REQUIRED_SETTLED,true);
                    }
                },
                () -> {
                    onProcessOutput(recipe);
                    recipe.data.putBoolean(SETTLED,true);
                },
                failure -> com.mojang.logging.LogUtils.getLogger().error("HK3GTL液态工艺已输出，但实验或批次回执记录失败：{}",getPos(),failure));
    }
    /** 必要生产结算不能随旁注异常一起吞掉；默认工艺无额外输出。 */
    protected void onRequiredProcessOutput(GTRecipe recipe) {}
    /** 注入配方的消耗顺序在倍乘时保持不变；优先比较燃料流体，否则比较首项消耗物品。 */
    private static BigInteger creditFor(GTRecipe original,GTRecipe consumed) {
        BigInteger unit=original.data.contains(CREDIT,Tag.TAG_STRING)
                ?new BigInteger(original.data.getString(CREDIT)):BigInteger.valueOf(original.data.getLong(CREDIT));
        if(unit.signum()<0)throw new IllegalArgumentException("网络注入产额不能为负数");
        if(unit.signum()==0)return BigInteger.ZERO;
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
        return unit.multiply(BigInteger.valueOf(actual/base));
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
            running.data.remove(SETTLED);running.data.remove(REQUIRED_SETTLED);return running;
        }
        private static ListTag strings(Set<String> values) {
            var list=new ListTag();values.forEach(v->list.add(StringTag.valueOf(v)));return list;
        }
        @Override public void setupRecipe(GTRecipe recipe) {
            // 续跑时必须用新副本清理输出标志，不修改仍在使用的上一批次。
            var next=recipe.copy();next.data=recipe.data.copy();next.data.remove(SETTLED);next.data.remove(REQUIRED_SETTLED);
            next.data.remove(com.sirin.hk3gtl.common.easter.Hk3EggProduction.REACTOR_FUEL_SETTLED);super.setupRecipe(next);
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
            boolean escrow=Hk3ProbabilitySupport.AVAILABLE
                    &&com.sirin.hk3gtl.common.integration.ae.exact.Hk3ProbabilityOrderService.escrowsOutput(lastRecipe);
            if(!process.allowed(lastRecipe)||!escrow
                    &&!org.gtlcore.gtlcore.api.recipe.RecipeRunnerHelper.matchRecipeOutput(process,lastRecipe)) {
                setWaiting(Component.translatable("hk3gtl.machine.liquid_line.waiting_output"));return;
            }
            // GTL完成函数直接调用RecipeRunnerHelper输出；服务端同一调用栈中先模拟，再单次提交。
            // 成功回调由Hk3ResearchOutputMixin触发，避免误走GTL改写后的输入入口或重复输出。
            super.onRecipeFinish();
        }
    }
}

