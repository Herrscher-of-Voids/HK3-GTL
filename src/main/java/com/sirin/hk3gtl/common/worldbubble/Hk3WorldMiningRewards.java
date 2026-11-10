package com.sirin.hk3gtl.common.worldbubble;



import net.minecraft.nbt.*;
import java.util.*;

/**
 * 【变更记录 #1】2026-09-29 · 修订101。
 * 删除：无。新增：首次成功资料、舰船档案20%与第五次保底的可重放结算。
 * 修改：以已完成事务和固定团队计数，失败/预留不计次；用途：重启不能重抽，复制物品不能改任务历史。
 * 资料按不同真实目标保留来源；普通物品和流体资源池由世界泡工序另行结算。
 */
/**
 * 【变更记录 #2】2026-09-29 23:37:35（内测5修订101）
 * 删除：本轮被替代的单前置或旧提示分支；其余历史保留。
 * 新增／修改：保存首次资料与舰船档案20%/第五次保底计算；普通资源池和真实发货尚未接入。
 * 用途：补足研究接线并如实保留未接物理执行器及结构审批边界。
 * 追溯：logs/research-mainline-r101；R101_FINAL_RECORD。
 */
/**
 * 【变更记录 #3】2026-09-29 23:51:00（内测5修订102）
 * 删除：按可重新创建的任务UUID抽取档案。新增：团队、真实目标及有效采掘序号的稳定抽签身份。
 * 修改：失败重开不重抽；用途：保留20%与第五次真实成功保底，不允许换任务编号刷首次档案。
 */
public final class Hk3WorldMiningRewards {
    public static final String LEGACY="hk3gtl:world_mining_legacy_record",SHIP="hk3gtl:ship_engineering_archive";
    private Hk3WorldMiningRewards() {}
    public static boolean contains(CompoundTag receipt,String item){
        for(var raw:receipt.getCompound("Outputs").getList("MissionRewards",Tag.TAG_COMPOUND)){
            var entry=(CompoundTag)raw;if(item.equals(entry.getString("id"))&&entry.getInt("Count")>0)return true;
        }
        return false;
    }
    public static ListTag plan(Hk3WorldBubbleLedger ledger,UUID scope,UUID operation){
        var tx=ledger.transaction(operation);
        if(tx==null||tx.action()!=Hk3WorldBubbleLedger.Action.MINE||tx.phase()==Hk3WorldBubbleLedger.Phase.CANCELLED)
            throw new IllegalArgumentException("Not a valid mining transaction");
        if(tx.phase()==Hk3WorldBubbleLedger.Phase.SETTLED){
            if(!Hk3WorldBubbleResearch.valid(tx.receipt(),scope,operation,"I26"))throw new IllegalArgumentException("Foreign mining receipt");
            return tx.receipt().getCompound("Outputs").getList("MissionRewards",10).copy();
        }
        int successes=0;boolean archive=false;
        for(var old:ledger.settledTransactions()){
            if(old.action()!=Hk3WorldBubbleLedger.Action.MINE||!Hk3WorldBubbleResearch.valid(old.receipt(),scope,old.id(),"I26"))continue;
            successes++;archive|=contains(old.receipt(),SHIP);
        }
        var result=new ListTag();
        // 暂定每个成功采掘任务提供一份带目标来源的资料，不能靠复制报告增加不同来源。
        result.add(item(LEGACY,tx.target()));
        UUID draw=UUID.nameUUIDFromBytes(("archive/"+scope+"/"+tx.target()+"/"+(ledger.real(tx.target()).miningCount()+1))
                .getBytes(java.nio.charset.StandardCharsets.UTF_8));
        int roll=new java.util.SplittableRandom(draw.getMostSignificantBits()^draw.getLeastSignificantBits()).nextInt(5);
        if(!archive&&(successes>=4||roll==0))result.add(item(SHIP,tx.target()));
        return result;
    }
    private static CompoundTag item(String id,UUID source){
        var entry=new CompoundTag();entry.putString("id",id);entry.putInt("Count",1);entry.putUUID("Source",source);return entry;
    }
}
