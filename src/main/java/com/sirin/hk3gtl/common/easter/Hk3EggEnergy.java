package com.sirin.hk3gtl.common.easter;
import com.gregtechceu.gtceu.api.machine.MetaMachine;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.block.entity.BlockEntity;
import java.util.UUID;
public final class Hk3EggEnergy {
    private Hk3EggEnergy(){}
    public static void worked(MetaMachine machine){
        if(!(machine instanceof com.sirin.hk3gtl.common.machine.research.Hk3ResearchProcessMachine process)
                ||!process.researchRole().equals("I35")
                ||!machine.getDefinition().getId().toString().equals("hk3gtl:i35_imaginary_space_anchoring_array")
                ||process.getOwnerUUID()==null)return;
        var owner=process.getOwnerUUID();var be=(BlockEntity)machine.getHolder();var n=be.getPersistentData();
        long now=machine.getLevel().getServer().overworld().getGameTime();
        if(!n.hasUUID("hk3EggAnchorOwner")||!n.getUUID("hk3EggAnchorOwner").equals(owner)){
            n.putUUID("hk3EggAnchorOwner",owner);n.remove("hk3EggAnchorTicks");n.remove("hk3EggAnchorTick");
        }
        long count=n.getLong("hk3EggAnchorTicks");
        if(count>=72000||n.contains("hk3EggAnchorTick")&&n.getLong("hk3EggAnchorTick")==now)return;
        n.putLong("hk3EggAnchorTicks",count+1);n.putLong("hk3EggAnchorTick",now);be.setChanged();
        if(count+1==72000)Hk3EggProductionData.get(machine.getLevel().getServer()).produced(owner,"receipt:12",1);
    }
    public static void paid(MetaMachine machine,UUID owner,boolean honkai){
        if(owner==null||!(machine.getLevel() instanceof ServerLevel level)||!level.getServer().isSameThread()||!(machine.getHolder() instanceof BlockEntity be))return;
        var receipts=Hk3EggProductionData.get(level.getServer());
        if(machine.getDefinition().getId().toString().equals(Hk3EggNativeMachineFacts.QUANTUM_MACHINE)&&receipts.count(owner,"receipt:14")==0)receipts.produced(owner,"receipt:14",1);
        if(!honkai&&receipts.count(owner,"receipt:269")==0&&receipts.count(owner,"context:manual_voltage_ready")>0)receipts.produced(owner,"receipt:269",1);
        if(honkai&&receipts.count(owner,"receipt:39")==0){
            String node="context:hw_node:"+level.dimension().location()+"@"+machine.getPos().asLong();
            if(receipts.count(owner,node)==0){
                receipts.produced(owner,node,1);
                if(receipts.counts(owner).keySet().stream().filter(key->key.startsWith("context:hw_node:")).count()>=5)receipts.produced(owner,"receipt:39",1);
            }
        }
        if(honkai&&receipts.count(owner,"receipt:8")==0)receipts.produced(owner,"receipt:8",1);
        var n=be.getPersistentData();if(n.getBoolean("hk3_egg_dual_done"))return;long now=level.getServer().overworld().getGameTime();
        if(!n.hasUUID("hk3_egg_dual_owner")||!n.getUUID("hk3_egg_dual_owner").equals(owner)){
            for(String k:new String[]{"hk3_egg_dual_eu","hk3_egg_dual_hk","hk3_egg_dual_at","hk3_egg_dual_n"})n.remove(k);n.putUUID("hk3_egg_dual_owner",owner);
        }
        n.putLong(honkai?"hk3_egg_dual_hk":"hk3_egg_dual_eu",now);
        if(n.contains("hk3_egg_dual_eu")&&n.contains("hk3_egg_dual_hk")&&n.getLong("hk3_egg_dual_eu")==now&&n.getLong("hk3_egg_dual_hk")==now&&(!n.contains("hk3_egg_dual_at")||n.getLong("hk3_egg_dual_at")!=now)){
            int count=n.contains("hk3_egg_dual_at")&&n.getLong("hk3_egg_dual_at")==now-1?n.getInt("hk3_egg_dual_n")+1:1;
            n.putLong("hk3_egg_dual_at",now);n.putInt("hk3_egg_dual_n",Math.min(200,count));var data=Hk3EggProductionData.get(level.getServer());
            if(!n.getBoolean("hk3_egg_dual_first")){data.produced(owner,"receipt:7",1);n.putBoolean("hk3_egg_dual_first",true);}
            if(count>=200){data.produced(owner,"receipt:38",1);n.putBoolean("hk3_egg_dual_done",true);}
        }be.setChanged();
    }
    public static void voltageChanged(MetaMachine machine,UUID owner){
        if(owner!=null&&machine.getLevel() instanceof ServerLevel level){
            var data=Hk3EggProductionData.get(level.getServer());String source="context:voltage_changed:"+level.dimension().location()+"@"+machine.getPos().asLong();
            if(data.count(owner,"receipt:269")==0){
                if(data.count(owner,source)==0)data.produced(owner,source,1);
                if(data.count(owner,"context:manual_voltage_ready")==0)data.produced(owner,"context:manual_voltage_ready",1);
            }
        }
    }
}
