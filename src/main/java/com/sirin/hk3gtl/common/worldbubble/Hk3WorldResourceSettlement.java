package com.sirin.hk3gtl.common.worldbubble;

import net.minecraft.nbt.*;
import java.util.UUID;

/** 完成回执按目标冻结资源与遗留资料，交付由输出仓执行。 */
public final class Hk3WorldResourceSettlement {
    private Hk3WorldResourceSettlement() {}
    public static String role(Hk3WorldBubbleLedger.Action action){return switch(action){
        case MINE->"I26";case CAPTURE->"I27";case TERMINATE_REAL->"I28";
        case STABILIZE_SIMULATION->"I30";case TERMINATE_SIMULATION->"I31";case DISCARD_SIMULATION->"W14";
    };}
    static boolean valid(Hk3WorldBubbleLedger.Transaction tx,UUID scope,CompoundTag receipt){
        if(!receipt.getString("Role").equals("W14"))
            return tx.action()!=Hk3WorldBubbleLedger.Action.DISCARD_SIMULATION
                    &&Hk3WorldBubbleResearch.valid(receipt,scope,tx.id(),role(tx.action()));
        String stage=switch(tx.action()){
            case STABILIZE_SIMULATION->"STABILIZE";case TERMINATE_SIMULATION->"TERMINATE";case DISCARD_SIMULATION->"DISCARD";
            default->"";
        };
        return tx.domain()==Hk3WorldBubbleLedger.Domain.SIMULATED&&tx.target().equals(receipt.getUUID("WorldTarget"))
                &&Hk3WorldBubbleResearch.validSimulation(receipt,scope,tx.id(),stage);
    }
    public static CompoundTag prepare(Hk3WorldBubbleLedger ledger,Hk3WorldResourceBatches batches,
            UUID operation,UUID actor,UUID scope,CompoundTag completed,Hk3WorldResourceCatalog catalog,long salt){
        var tx=ledger.transaction(operation);
        if(tx==null||!tx.actor().equals(actor)||tx.phase()==Hk3WorldBubbleLedger.Phase.CANCELLED
                ||!valid(tx,scope,completed))
            throw new IllegalArgumentException("Invalid completed resource operation");
        var result=completed.copy();var outputs=result.getCompound("Outputs").copy();
        var packages=tx.phase()==Hk3WorldBubbleLedger.Phase.SETTLED
                ?tx.receipt().getCompound("Outputs").getList("ResourcePackages",Tag.TAG_COMPOUND).copy()
                :batches.prepare(ledger,operation,actor,catalog,salt);
        outputs.put("ResourcePackages",packages);
        if(tx.action()==Hk3WorldBubbleLedger.Action.MINE||tx.action()==Hk3WorldBubbleLedger.Action.TERMINATE_REAL)
            outputs.put("MissionRewards",Hk3WorldMiningRewards.plan(ledger,scope,operation));
        result.put("Outputs",outputs);return result;
    }
    public static void validate(Hk3WorldBubbleLedger ledger,Hk3WorldResourceBatches batches,
            UUID operation,UUID actor,UUID scope,CompoundTag receipt){
        var tx=ledger.transaction(operation);
        if(tx==null||!tx.actor().equals(actor)||!valid(tx,scope,receipt))
            throw new IllegalArgumentException("Invalid world receipt or actor");
        if(tx.phase()==Hk3WorldBubbleLedger.Phase.SETTLED){
            if(!tx.receipt().equals(receipt))throw new IllegalArgumentException("Changed settled world receipt");
            return;
        }
        var out=receipt.getCompound("Outputs");
        boolean rewards=tx.action()==Hk3WorldBubbleLedger.Action.MINE||tx.action()==Hk3WorldBubbleLedger.Action.TERMINATE_REAL;
        if(!rewards&&out.contains("MissionRewards"))
            throw new IllegalArgumentException("Only real-world resource operations may award discoveries");
        if(!out.contains("ResourcePackages",Tag.TAG_LIST))throw new IllegalArgumentException("Missing allocated resource packages");
        var packages=out.getList("ResourcePackages",Tag.TAG_COMPOUND);
        if(packages.size()!=((ListTag)out.get("ResourcePackages")).size()
                ||!batches.matchesPrepared(ledger,operation,actor,packages))throw new IllegalArgumentException("Unallocated or changed resources");
        if(rewards&&!Hk3WorldMiningRewards.plan(ledger,scope,operation)
                .equals(out.getList("MissionRewards",Tag.TAG_COMPOUND)))throw new IllegalArgumentException("Changed mission rewards");
    }
}
