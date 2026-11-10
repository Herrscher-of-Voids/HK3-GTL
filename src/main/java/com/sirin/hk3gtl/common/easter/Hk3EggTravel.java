package com.sirin.hk3gtl.common.easter;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.core.*;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.*;
import net.minecraft.world.item.*;
import net.minecraft.world.phys.Vec3;
import net.minecraft.tags.*;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid="hk3gtl")
/** 【变更记录 #1】2026-10-01 06:05:54（修订128）：删除无；新增服务端连续位移、楼梯/梯子往返、探洞返回、森林夜行和高台安全检查；修改无；用途：瞬移、死亡和离线不累计位移，不强载区块，不变更世界。 */
/** 【变更记录 #2】2026-10-01 06:09:22（修订128）：删除：无；新增/修改：修正放置箱子后中心碰撞自锁，20块梯子的端点跨度，夜行不跨白天累计；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public final class Hk3EggTravel {
    private Hk3EggTravel(){}
    public static boolean home(ServerPlayer p,int radius){var at=p.getRespawnPosition();return at!=null&&p.getRespawnDimension().equals(p.level().dimension())&&p.position().distanceToSqr(Vec3.atCenterOf(at))<=radius*radius;}
    public static boolean platform(ServerPlayer p,BlockPos at,boolean own){
        if(at.getY()<p.level().getSeaLevel()+80)return false;var memory=Hk3EggBuildMemory.get(p.serverLevel());
        for(int x=-1;x<=1;x++)for(int z=-1;z<=1;z++){
            var pos=at.offset(x,0,z);if(!p.level().hasChunkAt(pos)||!p.level().getBlockState(pos).isFaceSturdy(p.level(),pos,Direction.UP)||(!p.level().getBlockState(pos.above()).getCollisionShape(p.level(),pos.above()).isEmpty()&&!(own&&x==0&&z==0&&p.level().getBlockState(pos.above()).is(Blocks.CHEST)))||(own&&!memory.owns(p,pos)))return false;
        }return true;
    }
    public static void placed(ServerPlayer p,BlockPos pos,net.minecraft.world.level.block.state.BlockState block){
        if(block.is(Blocks.CHEST)&&platform(p,pos.below(),true))Hk3EggVanilla.caseEvent(p,427);
    }
    public static void note(ServerPlayer p,String body){if(Hk3EggRuntime.state(p).getBoolean("returnedCave")&&body.contains("Terraria"))Hk3EggVanilla.caseEvent(p,459);}
    @SubscribeEvent public static void tick(TickEvent.PlayerTickEvent e){
        if(e.phase!=TickEvent.Phase.END||!(e.player instanceof ServerPlayer p))return;
        var s=Hk3EggRuntime.state(p);long now=p.server.overworld().getGameTime();String dim=p.level().dimension().location().toString();
        var previous=new Vec3(s.getDouble("travelX"),s.getDouble("travelY"),s.getDouble("travelZ"));var delta=p.position().subtract(previous);
        boolean continuous=s.getLong("travelTick")==now-1&&s.getString("travelDim").equals(dim)&&delta.lengthSqr()<2.25;
        boolean ground=p.onGround()&&!p.getAbilities().flying&&!p.isPassenger()&&!p.isFallFlying();double step=continuous&&ground?Math.sqrt(delta.x*delta.x+delta.z*delta.z):0;
        if(!continuous){s.remove("forestWalk");s.remove("caveJourney");s.remove("stairsDrop");s.remove("ladderStart");}
        var feet=p.blockPosition();var below=feet.below();var floor=p.level().getBlockState(below);var atFeet=p.level().getBlockState(feet);
        boolean stair=atFeet.getBlock() instanceof StairBlock||floor.getBlock() instanceof StairBlock;
        double down=continuous&&ground&&stair&&delta.y<=.01?s.getDouble("stairsDrop")+Math.max(0,-delta.y):0;s.putDouble("stairsDrop",Math.min(30,down));if(down>=30)Hk3EggVanilla.caseEvent(p,393);
        boolean ladder=p.onClimbable()&&atFeet.is(Blocks.LADDER)&&!p.getAbilities().flying&&!p.isPassenger();
        if(ladder&&continuous){
            if(!s.contains("ladderStart")){s.putDouble("ladderStart",p.getY());s.putInt("ladderX",feet.getX());s.putInt("ladderZ",feet.getZ());s.putBoolean("ladderFar",false);}
            if(s.getInt("ladderX")!=feet.getX()||s.getInt("ladderZ")!=feet.getZ())s.remove("ladderStart");
            else{double origin=s.getDouble("ladderStart"),distance=Math.abs(p.getY()-origin);
                if(distance>=19){boolean valid=true;for(int y=(int)Math.floor(Math.min(origin,p.getY()));y<=(int)Math.floor(Math.max(origin,p.getY()));y++)if(!p.level().getBlockState(new BlockPos(feet.getX(),y,feet.getZ())).is(Blocks.LADDER)){valid=false;break;}if(valid)s.putBoolean("ladderFar",true);}
                if(s.getBoolean("ladderFar")&&distance<1){Hk3EggVanilla.caseEvent(p,438);s.remove("ladderStart");}
            }
        }else if(s.contains("ladderStart")&&Math.abs(p.getY()-s.getDouble("ladderStart"))<1&&s.getBoolean("ladderFar")&&continuous){Hk3EggVanilla.caseEvent(p,438);s.remove("ladderStart");}
        else s.remove("ladderStart");
        if(p.level().dimension()==Level.OVERWORLD&&continuous){
            if(ground&&feet.getY()<p.level().getSeaLevel()-8&&!p.level().canSeeSky(feet))s.putBoolean("caveJourney",true);
            if(s.getBoolean("caveJourney")&&ground&&feet.getY()>=p.level().getSeaLevel()-4&&p.level().canSeeSky(feet)){
                s.putBoolean("returnedCave",true);s.remove("caveJourney");if(Hk3EggVanilla.count(p,"minecraft:torch")==29)Hk3EggVanilla.caseEvent(p,309);
            }
            if(p.level().isDay())s.remove("forestWalk");
            boolean forest=p.level().getBiome(feet).is(BiomeTags.IS_FOREST);
            if(ground&&forest&&p.level().isNight())s.putDouble("forestWalk",Math.min(50,s.getDouble("forestWalk")+step));
            if(s.getDouble("forestWalk")>=50&&ground&&home(p,4)&&p.isAlive()){Hk3EggVanilla.caseEvent(p,415);s.remove("forestWalk");}
        }
        if(now%20==0&&ground&&p.getMainHandItem().getItem() instanceof SwordItem&&p.getXRot()<-45&&p.level().canSeeSky(feet.above())&&platform(p,below,false))Hk3EggVanilla.caseEvent(p,458);
        s.putDouble("travelX",p.getX());s.putDouble("travelY",p.getY());s.putDouble("travelZ",p.getZ());s.putLong("travelTick",now);s.putString("travelDim",dim);
    }
    @SubscribeEvent public static void logout(PlayerEvent.PlayerLoggedOutEvent e){if(e.getEntity() instanceof ServerPlayer p)reset(p);}
    @SubscribeEvent public static void death(LivingDeathEvent e){if(e.getEntity() instanceof ServerPlayer p)reset(p);}
    private static void reset(ServerPlayer p){var s=Hk3EggRuntime.state(p);for(String k:new String[]{"travelTick","forestWalk","caveJourney","stairsDrop","ladderStart"})s.remove(k);}
}
