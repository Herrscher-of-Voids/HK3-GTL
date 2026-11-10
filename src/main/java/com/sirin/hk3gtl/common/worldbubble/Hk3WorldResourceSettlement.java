package com.sirin.hk3gtl.common.worldbubble;

import net.minecraft.nbt.*;
import java.util.UUID;

/**
 * 【文件职责】把已实际完成工序的回执补全为固定资源收据，不代表向玩家库存发货。
 * 【变更记录 #1】2026-09-29 23:51:00（内测5修订102）
 * 删除：无。新增：服务端身份/工序核验、资源包补全、结算前逐包核对。
 * 修改：重试使用已结算原结果；用途：只允许同一真实目标预算转成待交付资源，拒绝伪造数量。
 */
/**
 * 【变更记录 #2】2026-09-30 00:03:08（内测5修订102）
 * 删除：非采掘工序附带任务发现奖励的隐式许可。新增：非采掘收据拒绝MissionRewards。
 * 修改：验证保持纯函数；用途：捕获、终止和模拟不能伪造首份资料或舰船档案。
 */
public final class Hk3WorldResourceSettlement {
    private Hk3WorldResourceSettlement() {}
    public static String role(Hk3WorldBubbleLedger.Action action){return switch(action){
        case MINE->"I26";case CAPTURE->"I27";case TERMINATE_REAL->"I28";
        case STABILIZE_SIMULATION->"I30";case TERMINATE_SIMULATION->"I31";
    };}
    public static CompoundTag prepare(Hk3WorldBubbleLedger ledger,Hk3WorldResourceBatches batches,
            UUID operation,UUID actor,UUID scope,CompoundTag completed,Hk3WorldResourceCatalog catalog,long salt){
        var tx=ledger.transaction(operation);
        if(tx==null||!tx.actor().equals(actor)||tx.phase()==Hk3WorldBubbleLedger.Phase.CANCELLED
                ||!Hk3WorldBubbleResearch.valid(completed,scope,operation,role(tx.action())))
            throw new IllegalArgumentException("Invalid completed resource operation");
        var result=completed.copy();var outputs=result.getCompound("Outputs").copy();
        var packages=tx.phase()==Hk3WorldBubbleLedger.Phase.SETTLED
                ?tx.receipt().getCompound("Outputs").getList("ResourcePackages",Tag.TAG_COMPOUND).copy()
                :batches.prepare(ledger,operation,actor,catalog,salt);
        outputs.put("ResourcePackages",packages);
        if(tx.action()==Hk3WorldBubbleLedger.Action.MINE)outputs.put("MissionRewards",Hk3WorldMiningRewards.plan(ledger,scope,operation));
        result.put("Outputs",outputs);return result;
    }
    public static void validate(Hk3WorldBubbleLedger ledger,Hk3WorldResourceBatches batches,
            UUID operation,UUID actor,UUID scope,CompoundTag receipt){
        var tx=ledger.transaction(operation);
        if(tx==null||!tx.actor().equals(actor)||!Hk3WorldBubbleResearch.valid(receipt,scope,operation,role(tx.action())))
            throw new IllegalArgumentException("Invalid world receipt or actor");
        if(tx.phase()==Hk3WorldBubbleLedger.Phase.SETTLED){
            if(!tx.receipt().equals(receipt))throw new IllegalArgumentException("Changed settled world receipt");
            return;
        }
        var out=receipt.getCompound("Outputs");
        if(tx.action()!=Hk3WorldBubbleLedger.Action.MINE&&out.contains("MissionRewards"))
            throw new IllegalArgumentException("Only mining may award mission discoveries");
        if(!out.contains("ResourcePackages",Tag.TAG_LIST))throw new IllegalArgumentException("Missing allocated resource packages");
        var packages=out.getList("ResourcePackages",Tag.TAG_COMPOUND);
        if(packages.size()!=((ListTag)out.get("ResourcePackages")).size()
                ||!batches.matchesPrepared(ledger,operation,actor,packages))throw new IllegalArgumentException("Unallocated or changed resources");
        if(tx.action()==Hk3WorldBubbleLedger.Action.MINE&&!Hk3WorldMiningRewards.plan(ledger,scope,operation)
                .equals(out.getList("MissionRewards",Tag.TAG_COMPOUND)))throw new IllegalArgumentException("Changed mission rewards");
    }
}
