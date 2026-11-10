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
/** 【变更记录 #1】2026-10-01 12:18:50（修订128）：删除：无；新增/修改：自然神庙绊线、本人矿道步行、60秒不推进主线准备及原下界门往返；死亡离线重置连续条件；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #2】2026-11-05 22:19:02（修订211）：删除个人UUID研究计数；新增团队研究与团队身份基线；修改471连续准备在换队或共享研究推进时失效；用途：不能把队友完成的研究当无进度。 */
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

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
