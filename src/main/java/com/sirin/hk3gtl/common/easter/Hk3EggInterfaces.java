package com.sirin.hk3gtl.common.easter;

import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.gregtechceu.gtceu.api.machine.multiblock.part.MultiblockPartMachine;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.sirin.hk3gtl.common.capability.Hk3MaterialTick;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.block.entity.BlockEntity;

import java.util.Set;

public final class Hk3EggInterfaces {
    private static final Set<String> KINDS=Set.of("item_in","item_out","fluid_in","fluid_out","eu");
    private Hk3EggInterfaces() {}

    public static boolean watches(MetaMachine machine,String kind){
        if(!(machine instanceof MultiblockPartMachine)||!(machine.getLevel() instanceof ServerLevel level))return false;
        var block=(BlockEntity)machine.getHolder();
        return block.getPersistentData().hasUUID(Hk3EggProduction.OWNER)&&Hk3EggProductionData.get(level.getServer()).count(
                block.getPersistentData().getUUID(Hk3EggProduction.OWNER),"context:interface:"+kind)==0;
    }

    public static void transferred(MetaMachine machine,GTRecipe recipe,String kind){
        Hk3MaterialTick.committed(recipe,()->transferred(machine,kind));
    }

    public static void transferred(MetaMachine machine,String kind){
        if(!(machine instanceof MultiblockPartMachine)||!(machine.getLevel() instanceof ServerLevel level))return;
        var block=(BlockEntity)machine.getHolder();
        if(!block.getPersistentData().hasUUID(Hk3EggProduction.OWNER))return;
        var owner=block.getPersistentData().getUUID(Hk3EggProduction.OWNER);
        var data=Hk3EggProductionData.get(level.getServer());
        if(data.count(owner,"context:interface:"+kind)>0)return;
        data.produced(owner,"context:interface:"+kind,1);
        if(KINDS.stream().allMatch(value->data.count(owner,"context:interface:"+value)>0))data.produced(owner,"receipt:48",1);
    }
}
