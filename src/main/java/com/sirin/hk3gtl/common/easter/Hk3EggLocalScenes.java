package com.sirin.hk3gtl.common.easter;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.core.*;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.entity.*;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.*;
@Mod.EventBusSubscriber(modid="hk3gtl")
/** 【变更记录 #1】2026-10-01 13:27:41（修订128）：删除：无；新增/修改：新增3/6/9独立红石灯、同一命名僵尸受伤后隔离、天然地牢放火把后停门口，均查现有世界与本人真实行为；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
/** 【变更记录 #2】2026-10-01 13:28:18（修订128）：删除：无；新增/修改：拆分Java禁止的var多变量声明，保持门口检测逻辑；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public final class Hk3EggLocalScenes {
    private Hk3EggLocalScenes(){}
    public static void hurt(LivingEntity target,DamageSource source,float before){
        if(target.getType()!=EntityType.ZOMBIE||!target.hasCustomName()||!target.isAlive()||target.getHealth()>=before||!(source.getEntity() instanceof ServerPlayer p)||isolated(p,target))return;
        var s=Hk3EggRuntime.state(p);s.putUUID("isolationZombie",target.getUUID());s.putString("isolationDim",p.level().dimension().location().toString());s.putBoolean("isolationBuilt",false);
    }
    private static boolean isolated(ServerPlayer p,LivingEntity target){
        var start=target.blockPosition();var seen=new HashSet<BlockPos>();var queue=new ArrayDeque<BlockPos>();queue.add(start);boolean own=false;
        while(!queue.isEmpty()){
            var at=queue.removeFirst();if(!seen.add(at))continue;if(seen.size()>49||Math.abs(at.getX()-start.getX())>4||Math.abs(at.getZ()-start.getZ())>4||!p.level().hasChunkAt(at))return false;
            boolean barrier=!p.level().getBlockState(at).getCollisionShape(p.level(),at).isEmpty()||!p.level().getBlockState(at.above()).getCollisionShape(p.level(),at.above()).isEmpty();
            if(barrier){own|=Hk3EggBuildMemory.get(p.serverLevel()).owns(p,at)||Hk3EggBuildMemory.get(p.serverLevel()).owns(p,at.above());continue;}
            if(!p.level().getBlockState(at.below()).isFaceSturdy(p.level(),at.below(),Direction.UP))return false;
            for(var d:Direction.Plane.HORIZONTAL)queue.add(at.relative(d));
        }return own;
    }
    public static void placed(ServerPlayer p,BlockPos pos,BlockState block){
        var s=Hk3EggRuntime.state(p);
        if(s.hasUUID("isolationZombie")&&s.getString("isolationDim").equals(p.level().dimension().location().toString())){var target=p.serverLevel().getEntity(s.getUUID("isolationZombie"));if(target!=null&&target.blockPosition().distSqr(pos)<=36&&!block.getCollisionShape(p.level(),pos).isEmpty())s.putBoolean("isolationBuilt",true);}
        if(block.is(Blocks.TORCH)||block.is(Blocks.WALL_TORCH)){
            for(var at:BlockPos.betweenClosed(pos.offset(-6,-3,-6),pos.offset(6,3,6))){
                if(!p.level().hasChunkAt(at)||!p.level().getBlockState(at).is(Blocks.SPAWNER))continue;
                boolean natural=false;for(var c:BlockPos.betweenClosed(at.offset(-5,-1,-5),at.offset(5,1,5)))if(p.level().hasChunkAt(c)&&p.level().getBlockEntity(c) instanceof net.minecraft.world.level.block.entity.ChestBlockEntity chest){var tag=chest.saveWithoutMetadata();if(tag.getString("LootTable").equals("minecraft:chests/simple_dungeon")||chest.getPersistentData().getBoolean("hk3EggDungeonChest")){natural=true;break;}}
                if(natural){s.putLong("torchDungeon",at.asLong());s.putLong("torchDungeonLamp",pos.asLong());s.putString("torchDungeonDim",p.level().dimension().location().toString());s.putInt("dungeonDoorTicks",0);break;}
            }
        }
    }
    private static int lampPower(ServerPlayer p,BlockPos at){
        if(!p.level().hasChunkAt(at)||!Hk3EggBuildMemory.get(p.serverLevel()).owns(p,at)||!p.level().getBlockState(at).is(Blocks.REDSTONE_LAMP)||!p.level().getBlockState(at).getValue(RedstoneLampBlock.LIT))return 0;
        int power=0,feeds=0;for(var d:Direction.values()){var v=at.relative(d);if(!p.level().hasChunkAt(v))return 0;var b=p.level().getBlockState(v);int signal=p.level().getSignal(v,d);if(signal<=0)continue;if(!b.is(Blocks.REDSTONE_WIRE)||!Hk3EggBuildMemory.get(p.serverLevel()).owns(p,v))return 0;power=b.getValue(RedStoneWireBlock.POWER);feeds++;}return feeds==1?power:0;
    }
    @SubscribeEvent public static void tick(TickEvent.PlayerTickEvent e){
        if(e.phase!=TickEvent.Phase.END||!(e.player instanceof ServerPlayer p)||p.tickCount%20!=0)return;var s=Hk3EggRuntime.state(p);
        if(s.getBoolean("isolationBuilt")&&s.hasUUID("isolationZombie")&&s.getString("isolationDim").equals(p.level().dimension().location().toString())){
            var target=p.serverLevel().getEntity(s.getUUID("isolationZombie"));if(target instanceof LivingEntity living&&living.isAlive()&&living.hasCustomName()&&p.distanceToSqr(living)<1024&&isolated(p,living)){Hk3EggVanilla.caseEvent(p,410);s.remove("isolationZombie");s.remove("isolationBuilt");}
        }
        if(s.contains("torchDungeon")&&s.getString("torchDungeonDim").equals(p.level().dimension().location().toString())){
            var center=BlockPos.of(s.getLong("torchDungeon"));var lamp=BlockPos.of(s.getLong("torchDungeonLamp"));var feet=p.blockPosition();double distance=feet.distSqr(center);
            boolean door=false;for(var axis:List.of(Direction.EAST,Direction.SOUTH)){var a=feet.relative(axis);var b=feet.relative(axis.getOpposite());if(p.level().hasChunkAt(a)&&p.level().hasChunkAt(b)&&p.level().getBlockState(a).isCollisionShapeFullBlock(p.level(),a)&&p.level().getBlockState(b).isCollisionShapeFullBlock(p.level(),b))door=true;}
            if(distance>=9&&distance<=81&&door&&p.onGround()&&p.getDeltaMovement().horizontalDistanceSqr()<.0025&&Hk3EggBuildMemory.get(p.serverLevel()).owns(p,lamp)&&p.level().getBlockState(lamp).getLightEmission(p.level(),lamp)>0){int n=s.getInt("dungeonDoorTicks")+20;s.putInt("dungeonDoorTicks",n);if(n>=40){Hk3EggVanilla.caseEvent(p,432);s.remove("torchDungeon");}}else s.putInt("dungeonDoorTicks",0);
        }
        if(p.tickCount%100!=0||com.sirin.hk3gtl.common.narrative.Hk3NarrativeLog.isUnlocked(p,"E-EG-338"))return;
        for(var middle:Hk3EggBuildMemory.get(p.serverLevel()).near(p,p.blockPosition(),8)){
            int m=lampPower(p,middle);if(m!=6)continue;for(var dir:Direction.Plane.HORIZONTAL)if(lampPower(p,middle.relative(dir))==3&&lampPower(p,middle.relative(dir.getOpposite()))==9){Hk3EggVanilla.caseEvent(p,338);return;}
        }
    }
    @SubscribeEvent public static void logout(PlayerEvent.PlayerLoggedOutEvent e){if(e.getEntity() instanceof ServerPlayer p){var s=Hk3EggRuntime.state(p);s.remove("isolationZombie");s.remove("isolationBuilt");s.remove("torchDungeon");}}
}
