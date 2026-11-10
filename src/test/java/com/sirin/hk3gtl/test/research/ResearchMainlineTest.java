package com.sirin.hk3gtl.test.research;

/** 【变更记录 #4】2026-09-30 23:58:50（修订121）：删除旧个人答复自动代表新队的生产路径；新增/修改：更新真实团队交流边界，旧个人回信不能代表新队；用途：团队外交、阅读与个人经历分账，不发研究或物品奖励。 */



import com.sirin.hk3gtl.common.research.*;
import com.sirin.hk3gtl.common.recipe.Hk3ResearchProcessPlans;
import com.sirin.hk3gtl.common.recipe.Hk3ResearchProcessEnergy;
import com.sirin.hk3gtl.common.worldbubble.*;
import net.minecraft.nbt.*;
import java.util.*;

/** 修订101：验证100题执行契约、回收批次及重启边界；不冒充游戏运行验收。 */
/**
 * 【变更记录 #1】2026-09-29 23:37:35（内测5修订101）
 * 删除：本轮被替代的单前置或旧提示分支；其余历史保留。
 * 新增／修改：验证100题契约、付费状态机、真实批次格式、世界同批次规则和任务资料保证；夹具不等同游戏验收。
 * 用途：补足研究接线并如实保留未接物理执行器及结构审批边界。
 * 追溯：logs/research-mainline-r101；R101_FINAL_RECORD。
 */
/**
 * 【变更记录 #2】2026-09-30 00:03:08（内测5修订102）
 * 删除：必须恰好第五次出档案的错误断言。新增：批准图纸成本、非消耗模板与复制不发证据回归。
 * 修改：允许合法提前发现且总共只发一份档案；用途：核验20%提前发现及五次成功保底。
 */
/**
 * 【变更记录 #3】2026-09-30 01:17:37（第3次备注 · 内测5修订104）
 * 删除：无。新增：终止组件首件、工序门槛与不授予证据的回归。
 * 修改：保留全部旧检查；用途：防止SWR样件被无来源物料永久卡住，不代替真实世界任务验收。
 */
public final class ResearchMainlineTest {
    public static void main(String[] args) {
        check(Hk3ResearchExecutionContracts.all().size()==100,"100 contracts load");
        check(!Hk3ResearchProcessPlans.all().isEmpty(),"process plans load");
        energyPlanContracts();
        var data=new Hk3ResearchData(); var team=UUID.randomUUID();
        var receipt=receipt(UUID.randomUUID());
        check(!data.recordRecovery(team,"medium",new CompoundTag()),"empty receipt rejected");
        check(data.recordRecovery(team,"medium",receipt),"medium settled");
        check(!data.recordRecovery(team,"heat",receipt),"same batch cannot prove distinct recoveries");
        check(!data.recoveryAuditReady(team),"one recovery is insufficient");
        check(data.recordRecovery(team,"heat",receipt(UUID.randomUUID())),"heat settled");
        check(data.recordRecovery(team,"spent_rods",receipt(UUID.randomUUID())),"rods settled");
        check(data.recoveryAuditReady(team),"three actual batches ready");
        data=Hk3ResearchData.load(data.save(new CompoundTag()));
        check(data.recoveryAuditReady(team),"recovery survives restart");
        check(!data.hasProcessFact(team,"simulation_full_chain"),"missing world evidence fails closed");
        check(!Hk3ResearchExecutionContracts.ready(data,team,Hk3ResearchExecutionContracts.get("RN-IOP")),"recipe data alone never unlocks experiment");
        check(!data.hasExperiment(team,"RN-OPR")&&!data.completed(team,"RN-OPR"),"production receipts do not complete experiment or research");
        communication();worlds();rewards();paidCatalog();blueprintBalances();terminationComponent();
        System.out.println("ResearchMainlineTest: contracts, recipes, receipts, world provenance, same-batch chain and reward guarantees passed");
    }
    private static void terminationComponent(){
        var p=Hk3ResearchProcessPlans.all().stream().filter(x->x.id().equals("industrial_bubble_termination_component")).findFirst().orElseThrow();
        check(p.role().equals("I16")&&p.requirements().equals(List.of("RN-WTR","RN-SPM")),"component made on earlier precision line");
        check(!p.requirements().contains("RN-SWR")&&p.ticks()==1200&&p.energyTier()==22,"no own-research lock; sixty seconds at QAV");
        check(p.outputs().equals(List.of(new Hk3ResearchProcessPlans.Item("hk3gtl:bubble_termination_charge",1))),"one paid component");
        check(p.fluidInputs().contains(new Hk3ResearchProcessPlans.Fluid("honkai_coolant",250))&&p.fluidOutputs().contains(new Hk3ResearchProcessPlans.Fluid("hot_honkai_coolant",250)),"coolant accounted for");
        check(p.facts().isEmpty()&&p.experiment().isEmpty(),"manufacturing cannot terminate a target or grant evidence");
        check(Hk3ResearchExecutionContracts.get("RN-SWR").facts().contains("simulation_stabilized"),"actual stable-world evidence still required");
    }
    private static void energyPlanContracts(){
        for(var plan:Hk3ResearchProcessPlans.all()){
            check(plan.energyDirection().equals(Hk3ResearchProcessEnergy.isGenerator(plan.role())?"output":"input"),
                    plan.id()+" energy direction follows its machine role");
            int ratedTier=Hk3ResearchProcessEnergy.ratedVoltageTier(plan.role());
            if(ratedTier>0)check(plan.energyTier()<=ratedTier,plan.id()+" is within its machine voltage rating");
        }
        var freshGas=Hk3ResearchProcessPlans.all().stream().filter(p->p.id().equals("industrial_fresh_protective_gas")).findFirst().orElseThrow();
        check(freshGas.role().equals("I05")&&freshGas.energyTier()==15,"protective gas processing stays on the HBV gas-recovery line");
        check(freshGas.facts().contains("gas_purification")&&freshGas.facts().contains("gas_exhaust")
                &&!freshGas.facts().contains("phase_conversion"),"gas cleaning cannot impersonate I23 phase-conversion evidence");
        check(Hk3ResearchProcessEnergy.isGenerator("I23")&&Hk3ResearchProcessEnergy.ratedVoltageTier("I23")==20,
                "I23 is reserved for QCV gas-to-solid energy recovery");
    }
    private static void blueprintBalances(){
        var plans=Hk3ResearchProcessPlans.all();
        var analysis=plans.stream().filter(p->p.id().equals("industrial_ship_blueprint_analysis")).findFirst().orElseThrow();
        var copy=plans.stream().filter(p->p.id().equals("industrial_ship_blueprint_copy")).findFirst().orElseThrow();
        check(analysis.ticks()==2400&&copy.ticks()==1200&&analysis.energyTier()==19&&copy.energyTier()==19,"approved QSV 120/60 second blueprint costs");
        check(copy.experiment().isEmpty()&&copy.facts().isEmpty(),"copy never grants experimental evidence");
        check(copy.catalysts().size()==1&&copy.catalysts().get(0).id().equals("hk3gtl:imitation_hyperion_blueprint"),"original blueprint remains a non-consumed template");
        check(copy.inputs().stream().noneMatch(i->i.id().equals("hk3gtl:imitation_hyperion_blueprint"))&&copy.outputs().get(0).count()==1,"one paid copy; original not destroyed and recreated");
        for(var p:List.of(analysis,copy)){
            check(p.inputs().contains(new Hk3ResearchProcessPlans.Item("hk3gtl:soulium_data_substrate",2)),"two substrates per copy or analysis");
            check(p.inputs().contains(new Hk3ResearchProcessPlans.Item("minecraft:paper",4)),"four sheets of paper");
            check(p.fluidInputs().contains(new Hk3ResearchProcessPlans.Fluid("honkai_analysis_reagent",250)),"analysis reagent actually charged");
            check(p.fluidOutputs().contains(new Hk3ResearchProcessPlans.Fluid("spent_analysis_reagent",250)),"spent reagent remains an output");
        }
    }
    private static void communication(){
        var contacts=new com.sirin.hk3gtl.common.communication.Hk3CommunicationData();
        var data=new Hk3ResearchData();UUID player=UUID.randomUUID(),team=UUID.randomUUID();
        check(!Hk3CommunicationResearchProof.project(contacts,data,player,team,10),"no letter is not communication");
        contacts.discover(player);contacts.read(player);
        check(!Hk3CommunicationResearchProof.project(contacts,data,player,team,11),"reading alone is not communication");
        contacts.reply(player,false);
        contacts=com.sirin.hk3gtl.common.communication.Hk3CommunicationData.load(contacts.save(new CompoundTag()));
        check(!Hk3CommunicationResearchProof.project(contacts,data,player,team,12),"旧个人回复不能推定团队授权");
        check(!Hk3CommunicationResearchProof.project(contacts,data,player,team,13),"reply projection idempotent");
        check(!data.hasProcessFact(team,"formal_communication")&&!data.hasExperiment(team,"RN-HCCO")&&!data.completed(team,"RN-HCCO"),"reply cannot grant experiment or knowledge");
        check(!Hk3CommunicationResearchProof.project(contacts,data,player,UUID.randomUUID(),14),"换队不带走团队外交成果");
    }
    /** 注入的实验数据仅为单元测试夹具；此处验证付费与解锁，不宣称真实机器已完成。 */
    private static void paidCatalog(){
        UUID scope=UUID.randomUUID(),payer=UUID.randomUUID();
        var root=new CompoundTag();var accounts=new CompoundTag();var account=new CompoundTag();
        long total=Hk3ResearchPlans.all().values().stream().mapToLong(Hk3ResearchPlans.Plan::points).sum();
        account.putString("Points",Long.toString(total));accounts.put(payer.toString(),account);root.put("Accounts",accounts);
        var data=Hk3ResearchData.load(root);data.reconcileTeams(Map.of(payer,scope),Set.of(scope));
        Set<String> pending=new LinkedHashSet<>(Hk3ResearchExecutionContracts.all().keySet());long tick=1000;
        while(!pending.isEmpty()){
            int before=pending.size();
            for(String id:new ArrayList<>(pending)){
                var def=Hk3ResearchCatalog.bundled().get(id);
                if(!def.prerequisites().stream().allMatch(p->data.completed(scope,p)))continue;
                var c=Hk3ResearchExecutionContracts.get(id);var plan=Hk3ResearchPlans.get(id);
                for(String role:c.unlocks())check(!Hk3ResearchExecutionContracts.permitsMachine(data,scope,role,true),"locked before "+id);
                data.recordExperiment(scope,id,"unit-fixture:"+id);
                var paid=new CompoundTag();paid.putString("Points",Long.toString(plan.points()));
                var quote=new Hk3ResearchWorkQueue.Quote(id,"unit-facility",def.lab(),1,plan.eut(),"points",paid);
                check(data.startResearchWithPoints(scope,payer,quote,true),"paid start "+id);
                check(!data.completed(scope,id),"payment alone not completion "+id);
                check(data.advanceResearch(scope,id,quote.facility(),tick++,true,true,1,()->true)==Hk3ResearchWorkQueue.Outcome.COMPLETED,"completion "+id);
                for(String role:c.unlocks()){
                    check(Hk3ResearchExecutionContracts.permitsMachine(data,scope,role,true),"unlock after "+id);
                    if(role.startsWith("W"))check(!Hk3ResearchExecutionContracts.permitsMachine(data,scope,role,false),"wonder still needs second review "+role);
                }
                pending.remove(id);
            }
            check(pending.size()<before,"all topic payment graph resolves");
        }
        check(data.points(payer).signum()==0,"all approved costs paid once");
    }
    private static CompoundTag world(UUID batch,UUID team,String role){
        var r=receipt(batch);r.putUUID("Team",team);r.putString("Role",role);return r;
    }
    private static void worlds(){
        UUID team=UUID.randomUUID(),other=UUID.randomUUID(),actor=UUID.randomUUID();
        var ledger=new Hk3WorldBubbleLedger();var data=new Hk3ResearchData();
        UUID a=UUID.randomUUID(),b=UUID.randomUUID();
        ledger.createSimulation(a,actor,"test:a",world(a,team,"I29"));
        ledger.createSimulation(b,actor,"test:b",world(b,other,"I29"));
        UUID op=UUID.randomUUID();ledger.begin(op,actor,Hk3WorldBubbleLedger.Domain.SIMULATED,a,Hk3WorldBubbleLedger.Action.STABILIZE_SIMULATION);
        Hk3WorldBubbleResearch.project(ledger,data,team);
        check(data.hasExperiment(team,"RN-SWS")&&!data.hasProcessFact(team,"simulation_stabilized"),"created is direct SWS evidence; reserved not stable");
        ledger.settle(op,actor,world(op,team,"I30"));
        UUID bs=UUID.randomUUID(),bt=UUID.randomUUID();
        ledger.begin(bs,actor,Hk3WorldBubbleLedger.Domain.SIMULATED,b,Hk3WorldBubbleLedger.Action.STABILIZE_SIMULATION);
        ledger.settle(bs,actor,world(bs,team,"I30"));
        ledger.begin(bt,actor,Hk3WorldBubbleLedger.Domain.SIMULATED,b,Hk3WorldBubbleLedger.Action.TERMINATE_SIMULATION);
        ledger.settle(bt,actor,world(bt,team,"I31"));
        Hk3WorldBubbleResearch.project(ledger,data,team);
        check(!data.hasProcessFact(team,"simulation_full_chain"),"cannot stitch one team's creation with another team's termination");
        UUID at=UUID.randomUUID();ledger.begin(at,actor,Hk3WorldBubbleLedger.Domain.SIMULATED,a,Hk3WorldBubbleLedger.Action.TERMINATE_SIMULATION);
        ledger.settle(at,actor,world(at,team,"I31"));
        ledger=Hk3WorldBubbleLedger.load(ledger.save());Hk3WorldBubbleResearch.project(ledger,data,team);
        check(data.hasProcessFact(team,"simulation_full_chain"),"same batch actual three stages survive restart");
        var saved=data.save(new CompoundTag());Hk3WorldBubbleResearch.project(ledger,data,team);
        check(saved.equals(data.save(new CompoundTag())),"projection idempotent");
        var untouched=new Hk3ResearchData();Hk3WorldBubbleResearch.project(ledger,untouched,UUID.randomUUID());
        check(!untouched.hasProcessFact(team,"simulation_full_chain"),"foreign scope cannot claim evidence");
        var fake=new Hk3WorldBubbleLedger();UUID old=UUID.randomUUID();fake.createSimulation(old,actor,"old-unverified");
        var empty=new Hk3ResearchData();Hk3WorldBubbleResearch.project(fake,empty,team);
        check(!empty.hasExperiment(team,"RN-SWS"),"old creation without receipt cannot complete new evidence");
    }
    private static void rewards(){
        var ledger=new Hk3WorldBubbleLedger();UUID team=UUID.randomUUID(),actor=UUID.randomUUID();
        var data=new Hk3ResearchData();
        int archives=0;
        for(int i=0;i<5;i++){
            UUID target=ledger.discover("route:"+(i<4?0:1)),op=new UUID(0,1+5L*i);
            ledger.begin(op,actor,Hk3WorldBubbleLedger.Domain.REAL,target,Hk3WorldBubbleLedger.Action.MINE);
            var rewards=Hk3WorldMiningRewards.plan(ledger,team,op);
            check(rewards.equals(Hk3WorldMiningRewards.plan(ledger,team,op)),"retry cannot reroll");
            var receipt=world(op,team,"I26");receipt.getCompound("Outputs").put("MissionRewards",rewards);
            check(Hk3WorldMiningRewards.contains(receipt,Hk3WorldMiningRewards.LEGACY),"first mission has starter material");
            if(Hk3WorldMiningRewards.contains(receipt,Hk3WorldMiningRewards.SHIP))archives++;
            check(archives<=1&&(i<4||archives==1),"at most one archive; no later than fifth success");
            ledger.settle(op,actor,receipt);ledger=Hk3WorldBubbleLedger.load(ledger.save());
            Hk3WorldBubbleResearch.project(ledger,data,team);
            check(data.hasProcessFact(team,"distinct_mining_routes")==(i==4),"repeat same target never counts as distinct route");
        }
        check(data.hasProcessFact(team,"ship_archive")&&!data.hasExperiment(team,"RN-HBD"),"archive still requires real I32 analysis");
    }
    static CompoundTag receipt(UUID batch) {
        var r=new CompoundTag();r.putUUID("Batch",batch);r.putString("Facility","test:I05");
        r.putString("Recipe","test:recovery");r.putLong("Tick",100);
        var in=new CompoundTag();in.putInt("test",1);var out=new CompoundTag();out.putInt("test",1);
        r.put("Inputs",in);r.put("Outputs",out);return r;
    }
    static void check(boolean value,String message){if(!value)throw new AssertionError(message);}
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
