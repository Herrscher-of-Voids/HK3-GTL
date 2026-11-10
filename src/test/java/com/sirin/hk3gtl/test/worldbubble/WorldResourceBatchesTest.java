package com.sirin.hk3gtl.test.worldbubble;

import com.sirin.hk3gtl.common.worldbubble.*;
import net.minecraft.nbt.*;
import java.util.*;
import static com.sirin.hk3gtl.common.worldbubble.Hk3WorldBubbleLedger.*;

/**
 * 【变更记录 #1】2026-09-29 23:54:00（内测5修订102）
 * 删除：无。新增：冻结抽样、十包预算、模拟一包、篡改拒绝和数量边界回归。
 * 修改：测试目录明确为夹具；用途：验证代码，不冒充两个实例的最终资源目录或实际交付。
 */
/**
 * 【变更记录 #2】2026-09-30 00:03:08（内测5修订102）
 * 删除：无。新增：模拟终止伪造舰船奖励的拒绝测试。修改：仍用夹具；用途：阻断非采掘奖励来源。
 */
/**
 * 【变更记录 #3】2026-09-30 00:04:43（内测5修订102）
 * 删除：无。新增：数量合法但与收据不符、冻结表被清空的损坏存档拒绝测试。
 * 修改：加入正常结算后重载检查；用途：验证资源来源一致性，不依赖抽样碰运气。
 */
public final class WorldResourceBatchesTest {
    private static final UUID ACTOR=new UUID(1,1),TEAM=new UUID(2,2);
    private static int checks;
    private static Hk3WorldResourceCatalog catalog(String version,int size){
        var items=new ArrayList<Hk3WorldResourceCatalog.Entry>();var fluids=new ArrayList<Hk3WorldResourceCatalog.Entry>();
        for(int i=0;i<size;i++)items.add(new Hk3WorldResourceCatalog.Entry("fixture:item_"+i,i%15,"fixture:recipe_"+i));
        for(int i=0;i<Math.min(size,5);i++)fluids.add(new Hk3WorldResourceCatalog.Entry("fixture:fluid_"+i,i,"fixture:fluid_recipe_"+i));
        return new Hk3WorldResourceCatalog("fixture",version,items,fluids);
    }
    private static CompoundTag receipt(UUID op,Action action){
        var r=new CompoundTag();r.putUUID("Batch",op);r.putUUID("Team",TEAM);r.putString("Role",Hk3WorldResourceSettlement.role(action));
        r.putString("Facility","fixture:machine");r.putString("Recipe","fixture:completed");r.putLong("Tick",100);
        var in=new CompoundTag();in.putInt("ConsumedFixture",1);var out=new CompoundTag();out.putInt("CompletedFixture",1);
        r.put("Inputs",in);r.put("Outputs",out);return r;
    }
    private static CompoundTag complete(Hk3WorldBubbleLedger ledger,Hk3WorldResourceBatches batches,UUID op,Action action){
        var r=Hk3WorldResourceSettlement.prepare(ledger,batches,op,ACTOR,TEAM,receipt(op,action),catalog("v1",8),42);
        Hk3WorldResourceSettlement.validate(ledger,batches,op,ACTOR,TEAM,r);ledger.settle(op,ACTOR,r);return r;
    }
    public static void main(String[] args){
        replay();budgets();simulation();bounds();corrupt();
        System.out.println("WorldResourceBatchesTest: "+checks+" checks passed; no live catalog or inventory delivery tested");
    }
    private static void replay(){
        var ledger=new Hk3WorldBubbleLedger();var batches=new Hk3WorldResourceBatches();UUID target=ledger.discover("fixture:reroll");
        UUID first=new UUID(3,1),second=new UUID(3,2);ledger.begin(first,ACTOR,Domain.REAL,target,Action.MINE);
        var draw=batches.prepare(ledger,first,ACTOR,catalog("v1",8),42);var reward=Hk3WorldMiningRewards.plan(ledger,TEAM,first);
        var frozen=draw.copy();draw.getCompound(0).getList("Items",10).getCompound(0).putInt("Count",999);
        check(!draw.equals(batches.prepare(ledger,first,ACTOR,catalog("v1",8),42)),"returned packages are defensive copies");
        ledger.cancel(first,ACTOR);ledger=Hk3WorldBubbleLedger.load(ledger.save());batches=Hk3WorldResourceBatches.load(batches.save(),ledger);
        ledger.begin(second,ACTOR,Domain.REAL,target,Action.MINE);
        check(frozen.equals(batches.prepare(ledger,second,ACTOR,catalog("v2",10),999)),"cancel, restart, new task, new catalog and salt cannot reroll allocated ordinal");
        check(reward.equals(Hk3WorldMiningRewards.plan(ledger,TEAM,second)),"archive draw cannot be rerolled with task ID");
        var done=Hk3WorldResourceSettlement.prepare(ledger,batches,second,ACTOR,TEAM,receipt(second,Action.MINE),catalog("v2",10),999);
        var bad=done.copy();bad.getCompound("Outputs").getList("ResourcePackages",10).getCompound(0).getList("Items",10).getCompound(0).putInt("Count",999);
        var l=ledger;var b=batches;
        reject(()->Hk3WorldResourceSettlement.validate(l,b,second,ACTOR,TEAM,bad));
        reject(()->Hk3WorldResourceSettlement.validate(l,b,second,new UUID(8,8),TEAM,done));
        Hk3WorldResourceSettlement.validate(ledger,batches,second,ACTOR,TEAM,done);ledger.settle(second,ACTOR,done);
        check(ledger.real(target).miningCount()==1&&!ledger.transaction(second).delivered(),"settled once; output remains pending delivery");
        var retry=Hk3WorldResourceSettlement.prepare(ledger,batches,second,ACTOR,TEAM,receipt(second,Action.MINE),catalog("v3",3),1);
        Hk3WorldResourceSettlement.validate(ledger,batches,second,ACTOR,TEAM,retry);ledger.settle(second,ACTOR,retry);
        check(retry.equals(done)&&ledger.real(target).miningCount()==1,"settled replay unchanged and does not add mining count");
    }
    private static void budgets(){
        for(int mined:new int[]{0,1,4,9,10}){
            var ledger=new Hk3WorldBubbleLedger();var batches=new Hk3WorldResourceBatches();UUID target=ledger.discover("fixture:budget/"+mined);int packages=0;
            for(int i=0;i<mined;i++){UUID op=UUID.randomUUID();ledger.begin(op,ACTOR,Domain.REAL,target,Action.MINE);
                packages+=complete(ledger,batches,op,Action.MINE).getCompound("Outputs").getList("ResourcePackages",10).size();}
            UUID capture=UUID.randomUUID();ledger.begin(capture,ACTOR,Domain.REAL,target,Action.CAPTURE);
            check(complete(ledger,batches,capture,Action.CAPTURE).getCompound("Outputs").getList("ResourcePackages",10).isEmpty(),"capture gives no free package");
            UUID end=UUID.randomUUID();ledger.begin(end,ACTOR,Domain.REAL,target,Action.TERMINATE_REAL);
            var out=complete(ledger,batches,end,Action.TERMINATE_REAL).getCompound("Outputs").getList("ResourcePackages",10);
            check(out.size()==10-mined,"termination only returns unused budget");packages+=out.size();
            check(packages==10&&ledger.real(target).state()==RealState.TERMINATED,"lifetime ten, no eleventh package");
            for(int i=0;i<out.size();i++)check(out.getCompound(i).getInt("Ordinal")==mined+1+i,"consecutive remaining ordinals");
        }
    }
    private static void simulation(){
        var ledger=new Hk3WorldBubbleLedger();var batches=new Hk3WorldResourceBatches();UUID target=UUID.randomUUID();ledger.createSimulation(target,ACTOR,"fixture:simulation");
        UUID stable=UUID.randomUUID();ledger.begin(stable,ACTOR,Domain.SIMULATED,target,Action.STABILIZE_SIMULATION);
        check(complete(ledger,batches,stable,Action.STABILIZE_SIMULATION).getCompound("Outputs").getList("ResourcePackages",10).isEmpty(),"stabilizing does not produce resources");
        UUID end=UUID.randomUUID();ledger.begin(end,ACTOR,Domain.SIMULATED,target,Action.TERMINATE_SIMULATION);
        var proposal=Hk3WorldResourceSettlement.prepare(ledger,batches,end,ACTOR,TEAM,receipt(end,Action.TERMINATE_SIMULATION),catalog("v1",8),42);
        var forged=new ListTag();var reward=new CompoundTag();reward.putString("id",Hk3WorldMiningRewards.SHIP);reward.putInt("Count",1);forged.add(reward);
        proposal.getCompound("Outputs").put("MissionRewards",forged);
        reject(()->Hk3WorldResourceSettlement.validate(ledger,batches,end,ACTOR,TEAM,proposal));
        var result=complete(ledger,batches,end,Action.TERMINATE_SIMULATION);
        check(result.getCompound("Outputs").getList("ResourcePackages",10).size()==1,"simulation gives one package");
        check(!result.getCompound("Outputs").contains("MissionRewards"),"simulation gives no discovery guarantees");
        reject(()->ledger.begin(UUID.randomUUID(),ACTOR,Domain.SIMULATED,target,Action.TERMINATE_SIMULATION));
    }
    private static void bounds(){
        var ledger=new Hk3WorldBubbleLedger();var batches=new Hk3WorldResourceBatches();var catalog=catalog("v1",8);
        Map<String,Integer> frequency=new HashMap<>();Set<Integer> amounts=new HashSet<>(),fluidAmounts=new HashSet<>();
        for(int i=0;i<1200;i++){
            UUID target=ledger.discover("fixture:distribution/"+i),op=new UUID(7,i);ledger.begin(op,ACTOR,Domain.REAL,target,Action.MINE);
            var out=batches.prepare(ledger,op,ACTOR,catalog,42).getCompound(0);Set<String> unique=new HashSet<>();
            for(var raw:out.getList("Items",10)){var v=(CompoundTag)raw;unique.add(v.getString("id"));int n=v.getInt("Count");
                check(n>=1&&n<=64,"item quantity range");amounts.add(n);frequency.merge(v.getString("id"),1,Integer::sum);}
            check(unique.size()==4,"four distinct items");unique.clear();
            for(var raw:out.getList("Fluids",10)){var v=(CompoundTag)raw;int n=v.getInt("Amount");unique.add(v.getString("id"));
                check(n>=1000&&n<=16000&&n%1000==0,"whole bucket range");fluidAmounts.add(n);}
            check(unique.size()==2,"two distinct fluids");
        }
        check(amounts.size()==64&&fluidAmounts.size()==16,"all allowed quantities reachable");
        check(frequency.values().stream().allMatch(n->n>480&&n<720),"deterministic broad distribution guard");
        var reordered=new ArrayList<>(catalog.items());Collections.reverse(reordered);
        check(catalog.hash().equals(new Hk3WorldResourceCatalog("fixture","v1",reordered,catalog.fluids()).hash()),"catalog ordering does not alter hash");
        reject(()->new Hk3WorldResourceCatalog("fixture","v1",List.of(catalog.items().get(0),catalog.items().get(0)),catalog.fluids()));
        reject(()->new Hk3WorldResourceCatalog.Entry("fixture:too_high",15,"fixture:source"));
        reject(()->new Hk3WorldResourceCatalog("fixture","v1",List.of(),catalog.fluids()));
    }
    private static void corrupt(){
        var ledger=new Hk3WorldBubbleLedger();var batches=new Hk3WorldResourceBatches();UUID target=ledger.discover("fixture:corrupt"),op=UUID.randomUUID();
        ledger.begin(op,ACTOR,Domain.REAL,target,Action.MINE);batches.prepare(ledger,op,ACTOR,catalog("v1",1),42);
        var saved=batches.save();check(Hk3WorldResourceBatches.load(saved,ledger).save().equals(saved),"exact package persistence");
        var bad=saved.copy();bad.getList("Packages",10).getCompound(0).putInt("Ordinal",11);reject(()->Hk3WorldResourceBatches.load(bad,ledger));
        var duplicate=saved.copy();duplicate.getList("Packages",10).add(duplicate.getList("Packages",10).getCompound(0).copy());reject(()->Hk3WorldResourceBatches.load(duplicate,ledger));
        complete(ledger,batches,op,Action.MINE);
        var mismatch=batches.save();var amount=mismatch.getList("Packages",10).getCompound(0).getList("Items",10).getCompound(0);
        amount.putInt("Count",amount.getInt("Count")==64?63:64);
        reject(()->Hk3WorldResourceBatches.load(mismatch,ledger));
        var erased=batches.save();erased.put("Packages",new ListTag());reject(()->Hk3WorldResourceBatches.load(erased,ledger));
        check(Hk3WorldResourceBatches.load(batches.save(),ledger).save().equals(batches.save()),"settled packages retain matching frozen provenance");
        var missing=new Hk3WorldBubbleData().save(new CompoundTag());missing.remove("Resources");reject(()->Hk3WorldBubbleData.load(missing));
    }
    private static void check(boolean value,String message){checks++;if(!value)throw new AssertionError(message);}
    private static void reject(Runnable call){checks++;try{call.run();}catch(IllegalArgumentException expected){return;}throw new AssertionError("Invalid resource data accepted");}
}
