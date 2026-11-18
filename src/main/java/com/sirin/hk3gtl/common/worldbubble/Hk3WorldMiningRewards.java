package com.sirin.hk3gtl.common.worldbubble;



import net.minecraft.nbt.*;
import java.util.*;

/** 遗留资料绑定真实目标；舰船和神器发现奖励只由采掘触发。 */
public final class Hk3WorldMiningRewards {
    public static final String LEGACY="hk3gtl:world_mining_legacy_record",SHIP="hk3gtl:ship_engineering_archive";
    public static final String RELIC="hk3gtl:artifact_void_archives";
    private Hk3WorldMiningRewards() {}
    public static boolean contains(CompoundTag receipt,String item){
        for(var raw:receipt.getCompound("Outputs").getList("MissionRewards",Tag.TAG_COMPOUND)){
            var entry=(CompoundTag)raw;if(item.equals(entry.getString("id"))&&entry.getInt("Count")>0)return true;
        }
        return false;
    }
    public static ListTag plan(Hk3WorldBubbleLedger ledger,UUID scope,UUID operation){
        var tx=ledger.transaction(operation);
        if(tx==null||(tx.action()!=Hk3WorldBubbleLedger.Action.MINE
                &&tx.action()!=Hk3WorldBubbleLedger.Action.TERMINATE_REAL)||tx.phase()==Hk3WorldBubbleLedger.Phase.CANCELLED)
            throw new IllegalArgumentException("Not a valid real-world resource transaction");
        if(tx.phase()==Hk3WorldBubbleLedger.Phase.SETTLED){
            if(!Hk3WorldBubbleResearch.valid(tx.receipt(),scope,operation,Hk3WorldResourceSettlement.role(tx.action())))
                throw new IllegalArgumentException("Foreign resource receipt");
            return tx.receipt().getCompound("Outputs").getList("MissionRewards",10).copy();
        }
        var result=new ListTag();
        result.add(item(LEGACY,tx.target()));
        if(tx.action()==Hk3WorldBubbleLedger.Action.TERMINATE_REAL)return result;
        int successes=0;boolean relic=false;
        for(var old:ledger.settledTransactions()){
            if(old.action()!=Hk3WorldBubbleLedger.Action.MINE||!Hk3WorldBubbleResearch.valid(old.receipt(),scope,old.id(),"I26"))continue;
            successes++;relic|=contains(old.receipt(),RELIC);
        }
        UUID draw=UUID.nameUUIDFromBytes(("archive/"+scope+"/"+tx.target()+"/"+(ledger.real(tx.target()).miningCount()+1))
                .getBytes(java.nio.charset.StandardCharsets.UTF_8));
        int roll=new java.util.SplittableRandom(draw.getMostSignificantBits()^draw.getLeastSignificantBits()).nextInt(100);
        if(roll==0)result.add(item(SHIP,tx.target()));
        if(!relic&&successes>=4)result.add(item(RELIC,tx.target()));
        return result;
    }
    private static CompoundTag item(String id,UUID source){
        var entry=new CompoundTag();entry.putString("id",id);entry.putInt("Count",1);entry.putUUID("Source",source);return entry;
    }
}
