package com.sirin.hk3gtl.common.worldbubble;



import com.sirin.hk3gtl.common.research.*;
import net.minecraft.nbt.*;
import java.util.*;

 





 






public final class Hk3WorldBubbleResearch {
    private Hk3WorldBubbleResearch() {}
    public static boolean valid(CompoundTag receipt,UUID scope,UUID batch,String role) {
        return Hk3ResearchBatchProofs.valid(receipt)&&receipt.hasUUID("Team")&&scope.equals(receipt.getUUID("Team"))
                &&batch.equals(receipt.getUUID("Batch"))&&role.equals(receipt.getString("Role"));
    }
    public static boolean validSimulation(CompoundTag receipt,UUID scope,UUID batch,String stage){
        return valid(receipt,scope,batch,"W14")&&stage.equals(receipt.getString("WorldStage"))
                &&receipt.hasUUID("WorldTarget")&&Hk3W14WorldProcesses.of(receipt).supports(stage);
    }
    public static void project(Hk3WorldBubbleLedger ledger,Hk3ResearchData data,UUID scope) {
        Set<UUID> routes=new HashSet<>(),legacySources=new HashSet<>(),stable=new HashSet<>();
        Map<UUID,CompoundTag> created=new HashMap<>();
        for(var simulation:ledger.simulations()){
            var r=simulation.creationReceipt();
            if(!valid(r,scope,simulation.id(),"I29")&&!(validSimulation(r,scope,simulation.id(),"CREATE")
                    &&simulation.id().equals(r.getUUID("WorldTarget"))))continue;
            created.put(simulation.id(),r);fact(data,scope,"simulation_created",r);
            data.recordExperiment(scope,"RN-SWS",source(r));
        }
        for(var tx:ledger.settledTransactions()){
            var r=tx.receipt();
            if(!Hk3WorldResourceSettlement.valid(tx,scope,r))continue;
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
                case DISCARD_SIMULATION->{}
            }
        }
    }
    private static void fact(Hk3ResearchData data,UUID scope,String id,CompoundTag receipt){data.recordProcessFact(scope,id,receipt);}
    private static String source(CompoundTag r){return r.getString("Facility")+"/"+r.getString("Recipe")+"/"+r.getUUID("Batch");}
}

 
