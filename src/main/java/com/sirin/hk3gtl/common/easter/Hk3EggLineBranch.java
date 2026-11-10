package com.sirin.hk3gtl.common.easter;
import com.gregtechceu.gtceu.common.blockentity.ItemPipeBlockEntity;
import com.gregtechceu.gtceu.common.pipelike.item.*;
import com.gregtechceu.gtceu.api.machine.MetaMachine;
import net.minecraft.core.*;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.core.registries.BuiltInRegistries;
/** 【变更记录 #1】2026-10-01 13:36:23（修订128）：删除：无；新增/修改：已有真实生产且交付过的GT物品线新增本人管道端点，旧端点仍可达且新端点实际接收；等待目标机实际消耗该物料并产出；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public final class Hk3EggLineBranch {
    private Hk3EggLineBranch(){}
    private static String endpoint(ItemRoutePath path){return path.getTargetPipePos().relative(path.getTargetFacing()).asLong()+":"+path.getTargetFacing().getName();}
    public static void placed(net.minecraft.server.level.ServerPlayer p,BlockPos pos){if(p.level().getBlockEntity(pos) instanceof ItemPipeBlockEntity pipe){pipe.getPersistentData().putLong("hk3EggPipePlaced",p.server.overworld().getGameTime());pipe.setChanged();}}
    public static void delivered(ItemPipeNet net,ItemPipeBlockEntity pipe,Direction facing,ItemRoutePath path,ItemStack supplied,int oldCount,int remaining,boolean simulate){
        if(simulate||oldCount<=remaining||facing==null||!(pipe.getLevel() instanceof ServerLevel level))return;
        var source=MetaMachine.getMachine(level,pipe.getPipePos().relative(facing));var target=MetaMachine.getMachine(level,path.getTargetPipePos().relative(path.getTargetFacing()));
        if(source==null||target==null||source==target||!(source.getHolder() instanceof BlockEntity origin)||!(target.getHolder() instanceof BlockEntity destination))return;
        var data=origin.getPersistentData();if(!data.getBoolean("hk3EggActualProduction")||!data.hasUUID(Hk3EggProduction.OWNER))return;var owner=data.getUUID(Hk3EggProduction.OWNER);var p=level.getServer().getPlayerList().getPlayer(owner);
        if(p==null||p.serverLevel()!=level||!destination.getPersistentData().hasUUID(Hk3EggProduction.OWNER)||!destination.getPersistentData().getUUID(Hk3EggProduction.OWNER).equals(owner))return;
        var seen=data.getCompound("hk3EggLineTargets");String key=endpoint(path);long now=level.getServer().overworld().getGameTime();
        if(!seen.contains(key)&&!seen.isEmpty()){
            var branch=path.getTargetPipe();boolean oldPathAlive=net.getNetData(pipe.getPipePos(),facing).stream().anyMatch(v->!endpoint(v).equals(key)&&seen.contains(endpoint(v)));
            if(oldPathAlive&&Hk3EggBuildMemory.get(level).owns(p,branch.getPipePos())&&branch.getPersistentData().contains("hk3EggPipePlaced")&&branch.getPersistentData().getLong("hk3EggPipePlaced")>data.getLong("hk3EggFirstLineDelivery")){
                var n=destination.getPersistentData();n.putUUID("hk3EggBranchBy",owner);n.putString("hk3EggBranchItem",BuiltInRegistries.ITEM.getKey(supplied.getItem()).toString());n.putLong("hk3EggBranchPipe",branch.getPipePos().asLong());destination.setChanged();
            }
        }
        if(seen.isEmpty())data.putLong("hk3EggFirstLineDelivery",now);if(seen.size()<64){seen.putBoolean(key,true);data.put("hk3EggLineTargets",seen);origin.setChanged();}
    }
}
