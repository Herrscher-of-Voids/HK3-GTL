package com.sirin.hk3gtl.common.easter;
import com.gregtechceu.gtceu.api.machine.MetaMachine;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.block.entity.BlockEntity;
import java.util.UUID;
/** 【变更记录 #1】2026-10-01 06:11:31（修订128）：删除无；新增同一机器同一服务器tick双能源实际扣款配对；修改无；用途：模拟/失败扣款/卸载缺口不计连续200tick，离线回执仍归机器绑定人。 */
public final class Hk3EggEnergy {
    private Hk3EggEnergy(){}
    public static void paid(MetaMachine machine,UUID owner,boolean honkai){
        if(owner==null||!(machine.getLevel() instanceof ServerLevel level)||!level.getServer().isSameThread()||!(machine.getHolder() instanceof BlockEntity be))return;
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
}
