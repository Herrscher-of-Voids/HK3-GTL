package com.sirin.hk3gtl.common.easter;
import net.minecraft.core.*;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.block.*;
import net.minecraft.world.item.*;
import net.minecraft.tags.BlockTags;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.living.LivingEntityUseItemEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.*;
@Mod.EventBusSubscriber(modid="hk3gtl")
/** 【变更记录 #1】2026-10-01 06:09:22（修订128）：删除无；新增已加载普通房间的封闭地板/屋顶有界检测；修改无；用途：仅确认安全回屋与本人蘑菇小屋，不生成建筑、不触发工程成型。 */
/** 【变更记录 #2】2026-10-01 06:23:20（修订128）：删除：无；新增/修改：封闭房间保留原地板基线，扩建新增至少九格本人地板才授收藏；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public final class Hk3EggRooms {
    public record Room(Set<BlockPos> floor,Set<BlockPos> boundary){}
    private Hk3EggRooms(){}
    private static boolean barrier(ServerPlayer p,BlockPos pos){var s=p.level().getBlockState(pos);return s.getBlock() instanceof DoorBlock||s.isCollisionShapeFullBlock(p.level(),pos);}
    public static Room room(ServerPlayer p){
        var origin=p.blockPosition();if(!p.level().getBlockState(origin).isAir())return null;
        var seen=new HashSet<BlockPos>();var floor=new HashSet<BlockPos>();var walls=new HashSet<BlockPos>();var queue=new ArrayDeque<BlockPos>();queue.add(origin);
        while(!queue.isEmpty()){
            var pos=queue.removeFirst();if(!seen.add(pos))continue;
            if(seen.size()>400||Math.abs(pos.getX()-origin.getX())>16||Math.abs(pos.getZ()-origin.getZ())>16||!p.level().hasChunkAt(pos))return null;
            if(barrier(p,pos)){walls.add(pos);continue;}
            if(!p.level().getBlockState(pos.below()).isFaceSturdy(p.level(),pos.below(),Direction.UP))return null;
            floor.add(pos.below());boolean roof=false;
            for(int y=2;y<=6;y++)if(barrier(p,pos.above(y))){roof=true;walls.add(pos.above(y));break;}
            if(!roof)return null;
            for(var dir:Direction.Plane.HORIZONTAL)queue.add(pos.relative(dir));
        }
        return floor.isEmpty()?null:new Room(Set.copyOf(floor),Set.copyOf(walls));
    }
    @SubscribeEvent public static void drink(LivingEntityUseItemEvent.Finish e){
        if(e.getEntity() instanceof ServerPlayer p&&e.getItem().is(Items.HONEY_BOTTLE)&&Hk3EggRuntime.state(p).getBoolean("honeyHungry"))Hk3EggRuntime.state(p).putBoolean("honeyReturn",true);
    }
    @SubscribeEvent public static void start(LivingEntityUseItemEvent.Start e){if(e.getEntity() instanceof ServerPlayer p&&e.getItem().is(Items.HONEY_BOTTLE))Hk3EggRuntime.state(p).putBoolean("honeyHungry",p.getFoodData().getFoodLevel()<20);}
    @SubscribeEvent public static void tick(TickEvent.PlayerTickEvent e){
        if(e.phase!=TickEvent.Phase.END||!(e.player instanceof ServerPlayer p)||p.tickCount%100!=0||!p.onGround())return;
        var s=Hk3EggRuntime.state(p);var r=room(p);if(r==null)return;
        var memory=Hk3EggBuildMemory.get(p.serverLevel());
        var old=s.getLongArray("roomFloor");String dim=p.level().dimension().location().toString();
        if(old.length>0&&s.getString("roomDimension").equals(dim)&&r.floor.size()>=old.length+9){
            boolean contains=true;for(long packed:old)if(!r.floor.contains(BlockPos.of(packed))){contains=false;break;}
            if(contains){var previous=new HashSet<Long>();for(long packed:old)previous.add(packed);long added=r.floor.stream().filter(at->!previous.contains(at.asLong())&&memory.owns(p,at)&&Hk3EggBuildings.ordinary(p,at,p.level().getBlockState(at))).count();if(added>=9)Hk3EggVanilla.caseEvent(p,400);}
        }
        // 首次记录或新房间建立基线，扩建中途未封闭不重置旧基线。
        if(old.length==0||!s.getString("roomDimension").equals(dim)||java.util.Arrays.stream(old).noneMatch(v->r.floor.contains(BlockPos.of(v)))){s.putLongArray("roomFloor",r.floor.stream().mapToLong(BlockPos::asLong).toArray());s.putString("roomDimension",dim);}
        if(s.getBoolean("honeyReturn")&&p.isAlive()){Hk3EggVanilla.caseEvent(p,487);s.remove("honeyReturn");s.remove("honeyHungry");}
        if(!com.sirin.hk3gtl.common.narrative.Hk3NarrativeLog.isUnlocked(p,"E-EG-445")){
            boolean door=false,bed=false,mushroom=false;
            for(var at:memory.near(p,p.blockPosition(),16)){
                var b=p.level().getBlockState(at);if(r.boundary.contains(at)){door|=b.getBlock() instanceof DoorBlock;mushroom|=b.is(Blocks.RED_MUSHROOM_BLOCK)||b.is(Blocks.BROWN_MUSHROOM_BLOCK)||b.is(Blocks.MUSHROOM_STEM);}
                if(r.floor.contains(at.below())&&b.getBlock() instanceof BedBlock)bed=true;
            }
            if(door&&bed&&mushroom)Hk3EggVanilla.caseEvent(p,445);
        }
    }
}
