package com.sirin.hk3gtl.common.easter;

import net.minecraft.server.level.*;
import net.minecraft.core.*;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid="hk3gtl")
public final class Hk3EggExploration {
    private Hk3EggExploration(){}
    public static void broken(ServerPlayer p,BlockPos pos,BlockState old){
        if(old.is(Blocks.TRIPWIRE)&&p.serverLevel().structureManager().getStructureWithPieceAt(pos,net.minecraft.world.level.levelgen.structure.BuiltinStructures.JUNGLE_TEMPLE).isValid())Hk3EggVanilla.caseEvent(p,451);
        if(!old.isAir()&&!p.isCreative()&&pos.getY()<p.level().getSeaLevel()&&p.level().getBlockState(pos).isAir()){
            var s=Hk3EggRuntime.state(p);var cells=s.getCompound("minedTunnelCells");String key=Hk3EggVanilla.key(p,pos);if(cells.size()>=1024&&!cells.contains(key)){String first=cells.getAllKeys().iterator().next();cells.remove(first);}cells.putBoolean(key,true);s.put("minedTunnelCells",cells);
        }
    }
    private static int progress(ServerPlayer p){var data=com.sirin.hk3gtl.common.research.Hk3ResearchData.get(p);int n=0;for(String id:com.sirin.hk3gtl.common.research.Hk3ResearchPlans.all().keySet())if(data.completed(com.sirin.hk3gtl.common.research.Hk3ResearchTeams.scope(p.server,p.getUUID()),id))n++;return n;}
    public static void note(ServerPlayer p,String title,String body){if(!(title+body).contains("速通"))return;var s=Hk3EggRuntime.state(p);s.putLong("speedPrepareStart",p.server.overworld().getGameTime());s.putInt("speedPrepareStage",com.sirin.hk3gtl.common.phone.Hk3SocialService.stage(p));s.putInt("speedPrepareResearch",progress(p));s.putUUID("speedPrepareScope",com.sirin.hk3gtl.common.research.Hk3ResearchTeams.scope(p.server,p.getUUID()));}
    @SubscribeEvent public static void tick(TickEvent.PlayerTickEvent e){
        if(e.phase!=TickEvent.Phase.END||!(e.player instanceof ServerPlayer p))return;var s=Hk3EggRuntime.state(p);long now=p.server.overworld().getGameTime();String dim=p.level().dimension().location().toString();
        var previous=new Vec3(s.getDouble("tunnelX"),s.getDouble("tunnelY"),s.getDouble("tunnelZ"));var delta=p.position().subtract(previous);var feet=p.blockPosition();
        boolean continuous=s.getLong("tunnelTick")==now-1&&dim.equals(s.getString("tunnelDim"))&&delta.lengthSqr()<2.25&&BlockPos.containing(previous).getY()==feet.getY();
        var cells=s.getCompound("minedTunnelCells");boolean own=cells.getBoolean(Hk3EggVanilla.key(p,feet))||cells.getBoolean(Hk3EggVanilla.key(p,feet.above()));
        boolean walking=continuous&&own&&p.onGround()&&!p.isPassenger()&&!p.getAbilities().flying&&!p.isFallFlying()&&!p.level().canSeeSky(feet)&&p.level().getBlockState(feet).isAir();
        double distance=walking?s.getDouble("tunnelDistance")+Math.sqrt(delta.x*delta.x+delta.z*delta.z):0;s.putDouble("tunnelDistance",Math.min(200,distance));if(distance>=200)Hk3EggVanilla.caseEvent(p,436);
        s.putLong("tunnelTick",now);s.putString("tunnelDim",dim);s.putDouble("tunnelX",p.getX());s.putDouble("tunnelY",p.getY());s.putDouble("tunnelZ",p.getZ());
        if(s.contains("speedPrepareStart")&&now%20==0){
            if(!s.hasUUID("speedPrepareScope")||!s.getUUID("speedPrepareScope").equals(com.sirin.hk3gtl.common.research.Hk3ResearchTeams.scope(p.server,p.getUUID()))||com.sirin.hk3gtl.common.phone.Hk3SocialService.stage(p)!=s.getInt("speedPrepareStage")||progress(p)!=s.getInt("speedPrepareResearch")){s.remove("speedPrepareStart");}
            else if(now-s.getLong("speedPrepareStart")>=1200){Hk3EggVanilla.caseEvent(p,471);s.remove("speedPrepareStart");}
        }
    }
    public static void portal(ServerPlayer p,ServerLevel from,BlockPos origin,boolean valid){
        if(!valid||from==p.serverLevel())return;var s=Hk3EggRuntime.state(p);
        if(from.dimension()==Level.OVERWORLD&&p.level().dimension()==Level.NETHER){s.putLong("portalTripOrigin",origin.asLong());s.putLong("portalTripNether",p.blockPosition().asLong());}
        else if(from.dimension()==Level.NETHER&&p.level().dimension()==Level.OVERWORLD&&s.contains("portalTripOrigin")){
            if(origin.distSqr(BlockPos.of(s.getLong("portalTripNether")))<=16&&p.blockPosition().distSqr(BlockPos.of(s.getLong("portalTripOrigin")))<=16)Hk3EggVanilla.caseEvent(p,479);s.remove("portalTripOrigin");s.remove("portalTripNether");
        }
    }
    @SubscribeEvent public static void death(LivingDeathEvent e){if(e.getEntity() instanceof ServerPlayer p)reset(p);}
    @SubscribeEvent public static void logout(PlayerEvent.PlayerLoggedOutEvent e){if(e.getEntity() instanceof ServerPlayer p)reset(p);}
    private static void reset(ServerPlayer p){var s=Hk3EggRuntime.state(p);s.remove("portalTripOrigin");s.remove("portalTripNether");s.remove("tunnelTick");s.remove("speedPrepareStart");}
}

