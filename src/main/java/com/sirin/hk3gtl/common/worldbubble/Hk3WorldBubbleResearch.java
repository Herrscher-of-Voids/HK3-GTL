package com.sirin.hk3gtl.common.worldbubble;



import com.sirin.hk3gtl.common.research.*;
import net.minecraft.nbt.*;
import java.util.*;

/**
 * 【变更记录 #1】2026-09-29 · 修订101。
 * 删除：无。新增：从已结算世界泡账本核验同批链、跨目标及资料来源。
 * 修改：只读取机器固定团队与实际回执；用途：重放不会复制证据，预留/取消/拼接批次不算成功。
 * 边界：本类不创建机器、不结算资源；结构获批后的工序通过WorldBubbleData提交真实完成结果。
 */
/**
 * 【变更记录 #2】2026-09-29 23:37:35（内测5修订101）
 * 删除：本轮被替代的单前置或旧提示分支；其余历史保留。
 * 新增／修改：从有效结算事务投影同批次链与不同目标证据，不接受预留、取消、旧无来源记录。
 * 用途：补足研究接线并如实保留未接物理执行器及结构审批边界。
 * 追溯：logs/research-mainline-r101；R101_FINAL_RECORD。
 */
public final class Hk3WorldBubbleResearch {
    private Hk3WorldBubbleResearch() {}
    public static boolean valid(CompoundTag receipt,UUID scope,UUID batch,String role) {
        return Hk3ResearchBatchProofs.valid(receipt)&&receipt.hasUUID("Team")&&scope.equals(receipt.getUUID("Team"))
                &&batch.equals(receipt.getUUID("Batch"))&&role.equals(receipt.getString("Role"));
    }
    public static void project(Hk3WorldBubbleLedger ledger,Hk3ResearchData data,UUID scope) {
        Set<UUID> routes=new HashSet<>(),legacySources=new HashSet<>(),stable=new HashSet<>();
        Map<UUID,CompoundTag> created=new HashMap<>();
        for(var simulation:ledger.simulations()){
            var r=simulation.creationReceipt();
            if(!valid(r,scope,simulation.id(),"I29"))continue;
            created.put(simulation.id(),r);fact(data,scope,"simulation_created",r);
            data.recordExperiment(scope,"RN-SWS",source(r));
        }
        for(var tx:ledger.settledTransactions()){
            var r=tx.receipt();String role=switch(tx.action()){
                case MINE->"I26";case CAPTURE->"I27";case TERMINATE_REAL->"I28";
                case STABILIZE_SIMULATION->"I30";case TERMINATE_SIMULATION->"I31";
            };
            if(!valid(r,scope,tx.id(),role))continue;
            switch(tx.action()){
                case MINE->{
                    routes.add(tx.target());fact(data,scope,"drone_return",r);
                    if(Hk3WorldMiningRewards.contains(r,Hk3WorldMiningRewards.LEGACY)){
                        legacySources.add(tx.target());fact(data,scope,"first_mining_legacy",r);
                    }
                    if(Hk3WorldMiningRewards.contains(r,Hk3WorldMiningRewards.SHIP))fact(data,scope,"ship_archive",r);
                    if(routes.size()>=2)fact(data,scope,"distinct_mining_routes",r);
                    if(legacySources.size()>=2)fact(data,scope,"distinct_legacy_sources",r);
                }
                case CAPTURE->fact(data,scope,"real_capture",r);
                case TERMINATE_REAL->fact(data,scope,"real_termination",r);
                case STABILIZE_SIMULATION->{
                    if(created.containsKey(tx.target())){stable.add(tx.target());fact(data,scope,"simulation_stabilized",r);}
                }
                case TERMINATE_SIMULATION->{
                    if(created.containsKey(tx.target())&&stable.contains(tx.target())){
                        var proof=r.copy();proof.putUUID("Simulation",tx.target());
                        proof.put("Creation",created.get(tx.target()));fact(data,scope,"simulation_full_chain",proof);
                    }
                }
            }
        }
    }
    private static void fact(Hk3ResearchData data,UUID scope,String id,CompoundTag receipt){data.recordProcessFact(scope,id,receipt);}
    private static String source(CompoundTag r){return r.getString("Facility")+"/"+r.getString("Recipe")+"/"+r.getUUID("Batch");}
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
