package com.sirin.hk3gtl.common.easter;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.phys.Vec3;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.ChunkPos;
import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.gregtechceu.gtceu.api.pattern.MultiblockWorldSavedData;
import com.sirin.hk3gtl.common.machine.research.Hk3LateIndustrialMachine;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid="hk3gtl")
 
public final class Hk3EggStillness {
    @SubscribeEvent public static void tick(TickEvent.PlayerTickEvent e){
        if(e.phase!=TickEvent.Phase.END||!(e.player instanceof ServerPlayer p))return;
        var s=Hk3EggRuntime.state(p);long now=p.server.overworld().getGameTime();
        boolean allowed=p.level().dimension().equals(com.sirin.hk3gtl.common.dimension.Hk3Dimensions.IMAGINARY)&&p.onGround()&&!p.isPassenger();
        var anchor=new Vec3(s.getDouble("stillX"),s.getDouble("stillY"),s.getDouble("stillZ"));
        if(!allowed||s.getLong("stillLast")!=now-1||p.position().distanceToSqr(anchor)>=1){s.putDouble("stillX",p.getX());s.putDouble("stillY",p.getY());s.putDouble("stillZ",p.getZ());s.putInt("stillTicks",0);}
        else{int ticks=Math.min(600,s.getInt("stillTicks")+1);s.putInt("stillTicks",ticks);if(ticks==600)Hk3EggVanilla.caseEvent(p,21);}
        s.putLong("stillLast",now);
        verification(p,now);
    }

    private static void verification(ServerPlayer p,long now){
        var s=Hk3EggRuntime.state(p);var device=verificationDevice(p);
        String identity=device==null?"":p.level().dimension().location()+"@"+device;
        var anchor=new Vec3(s.getDouble("verifyX"),s.getDouble("verifyY"),s.getDouble("verifyZ"));
        if(device==null||!identity.equals(s.getString("verifyDevice"))||s.getLong("verifyLast")!=now-1
                ||p.position().distanceToSqr(anchor)>=1){
            s.putString("verifyDevice",identity);s.putDouble("verifyX",p.getX());
            s.putDouble("verifyY",p.getY());s.putDouble("verifyZ",p.getZ());s.putInt("verifyTicks",0);
        }else{
            int ticks=Math.min(1200,s.getInt("verifyTicks")+1);s.putInt("verifyTicks",ticks);
            if(ticks==1200)Hk3EggVanilla.caseEvent(p,81);
        }
        s.putLong("verifyLast",now);
    }

    private static BlockPos verificationDevice(ServerPlayer p){
        var level=p.serverLevel();var pos=p.blockPosition();var saved=MultiblockWorldSavedData.getOrCreate(level);
        for(int x=(pos.getX()-8)>>4;x<=(pos.getX()+8)>>4;x++)
            for(int z=(pos.getZ()-8)>>4;z<=(pos.getZ()+8)>>4;z++){
                if(!level.hasChunk(x,z))continue;
                for(var state:saved.getControllerInChunk(new ChunkPos(x,z))){
                    if(state.hasError()||!level.hasChunkAt(state.controllerPos))continue;
                    if(!(MetaMachine.getMachine(level,state.controllerPos) instanceof Hk3LateIndustrialMachine machine)
                            ||!machine.researchRole().equals("I43")||!machine.isFormed())continue;
                    var delta=p.position().subtract(Vec3.atCenterOf(state.controllerPos));
                    var front=machine.getFrontFacing();
                    if(delta.lengthSqr()<=64&&delta.x*front.getStepX()+delta.z*front.getStepZ()>0)
                        return state.controllerPos;
                }
            }
        return null;
    }
}
