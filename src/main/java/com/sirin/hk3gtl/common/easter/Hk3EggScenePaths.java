package com.sirin.hk3gtl.common.easter;
import net.minecraft.core.*;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.block.*;
import net.minecraft.world.item.*;
import net.minecraft.tags.*;
import net.minecraft.world.phys.*;
import net.minecraft.world.entity.decoration.ArmorStand;
import net.minecraft.world.inventory.*;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.*;
@Mod.EventBusSubscriber(modid="hk3gtl")
/** 【变更记录 #1】2026-10-01 06:39:10（修订128）：删除无；新增普通建筑与出行旁注；修改无；用途：只检测现有世界，本人归属/连续动作/加载边界均核验，不生成结构。 */
/** 【变更记录 #2】2026-10-01 06:45:17（修订128）：删除：无；新增/修改：踩桥授予前重新核验整条20格桥及其下岩浆，拆桥或卸载不沿用成桥时旧证据；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public final class Hk3EggScenePaths {
    private Hk3EggScenePaths(){}
    private static boolean lamp(ServerPlayer p,BlockPos pos){if(!p.level().hasChunkAt(pos)||!Hk3EggBuildMemory.get(p.serverLevel()).owns(p,pos))return false;return p.level().getBlockState(pos).getLightEmission(p.level(),pos)>0;}
    public static void stored(ServerPlayer p,AbstractContainerMenu menu,List<Hk3EggStorageFacts.Stack> before,List<Hk3EggStorageFacts.Stack> after){
        if(!(menu instanceof ChestMenu chest))return;
        long old=before.stream().filter(v->v.id().equals("minecraft:paper")&&v.name().equals("343")).mapToLong(Hk3EggStorageFacts.Stack::count).sum();
        long now=after.stream().filter(v->v.id().equals("minecraft:paper")&&v.name().equals("343")).mapToLong(Hk3EggStorageFacts.Stack::count).sum();if(now<=old)return;
        var memory=Hk3EggBuildMemory.get(p.serverLevel());
        for(var part:Hk3EggChests.parts(p,chest.getContainer()))for(var at:memory.near(p,part.getBlockPos(),4)){
            if(!p.level().getBlockState(at).is(Blocks.CAKE)||at.distSqr(part.getBlockPos())>16)continue;
            boolean chair=false,table=false;for(var v:BlockPos.betweenClosed(at.offset(-2,-1,-2),at.offset(2,0,2))){if(!p.level().hasChunkAt(v))continue;var block=p.level().getBlockState(v).getBlock();chair|=block instanceof StairBlock;table|=block instanceof SlabBlock||block==Blocks.SCAFFOLDING;}
            if(chair&&table){Hk3EggVanilla.caseEvent(p,382);return;}
        }
    }
    public static void placed(ServerPlayer p,BlockPos pos,net.minecraft.world.level.block.state.BlockState state){
        if(!Hk3EggBuildings.ordinary(p,pos,state)||com.sirin.hk3gtl.common.narrative.Hk3NarrativeLog.isUnlocked(p,"E-EG-435"))return;
        boolean aboveLava=false;for(int y=1;y<=8;y++)if(p.level().getFluidState(pos.below(y)).is(FluidTags.LAVA)){aboveLava=true;break;}if(!aboveLava)return;
        var memory=Hk3EggBuildMemory.get(p.serverLevel());
        for(var dir:List.of(Direction.EAST,Direction.SOUTH))for(int start=-19;start<=0;start++){
            boolean valid=true;
            for(int i=0;i<20;i++){var at=pos.relative(dir,start+i);if(!memory.owns(p,at)||!p.level().getBlockState(at).isFaceSturdy(p.level(),at,Direction.UP)||!p.level().getBlockState(at.above()).getCollisionShape(p.level(),at.above()).isEmpty()){valid=false;break;}
                boolean lava=false;for(int y=1;y<=8;y++)if(p.level().getFluidState(at.below(y)).is(FluidTags.LAVA)){lava=true;break;}if(!lava){valid=false;break;}}
            if(valid){var s=Hk3EggRuntime.state(p);s.putString("lavaBridgeDim",p.level().dimension().location().toString());s.putLong("lavaBridgeStart",pos.relative(dir,start).asLong());s.putInt("lavaBridgeAxis",dir==Direction.EAST?0:1);return;}
        }
    }
    @SubscribeEvent public static void tick(TickEvent.PlayerTickEvent e){
        if(e.phase!=TickEvent.Phase.END||!(e.player instanceof ServerPlayer p))return;
        var s=Hk3EggRuntime.state(p);long now=p.server.overworld().getGameTime();boolean continuous=s.getLong("sceneTick")==now-1;var memory=Hk3EggBuildMemory.get(p.serverLevel());
        if(!continuous){s.remove("doorGaze");s.remove("armorGaze");s.remove("armorWatched");}
        if(s.contains("lavaBridgeStart")&&s.getString("lavaBridgeDim").equals(p.level().dimension().location().toString())&&p.onGround()&&!p.isOnFire()&&!p.isInLava()){
            var start=BlockPos.of(s.getLong("lavaBridgeStart"));var feet=p.blockPosition().below();int offset=s.getInt("lavaBridgeAxis")==0?feet.getX()-start.getX():feet.getZ()-start.getZ();
            boolean inline=feet.getY()==start.getY()&&(s.getInt("lavaBridgeAxis")==0?feet.getZ()==start.getZ():feet.getX()==start.getX());
            if(inline&&offset>=0&&offset<20){
                boolean valid=true;var dir=s.getInt("lavaBridgeAxis")==0?Direction.EAST:Direction.SOUTH;
                for(int i=0;i<20&&valid;i++){var at=start.relative(dir,i);if(!p.level().hasChunkAt(at)||!memory.owns(p,at)||!p.level().getBlockState(at).isFaceSturdy(p.level(),at,Direction.UP)||!p.level().getBlockState(at.above()).getCollisionShape(p.level(),at.above()).isEmpty()){valid=false;break;}
                    boolean lava=false;for(int y=1;y<=8;y++)if(p.level().getFluidState(at.below(y)).is(FluidTags.LAVA)){lava=true;break;}valid=lava;}
                if(valid)Hk3EggVanilla.caseEvent(p,435);s.remove("lavaBridgeStart");
            }
        }
        // 只在每五tick对看向的近距离装饰做查询；累计时按真实tick跨度算。
        if(now%5!=0){s.putLong("sceneTick",now);return;}
        boolean doorway=false;
        if(p.getMainHandItem().is(Items.IRON_SWORD)&&!com.sirin.hk3gtl.common.narrative.Hk3NarrativeLog.isUnlocked(p,"E-EG-381")){
            for(var at:memory.near(p,p.blockPosition(),6)){
                var b=p.level().getBlockState(at);if(!(b.getBlock() instanceof DoorBlock)||b.getValue(DoorBlock.HALF)!=net.minecraft.world.level.block.state.properties.DoubleBlockHalf.LOWER)continue;
                var side=b.getValue(DoorBlock.FACING).getClockWise();boolean lights=false;
                for(int y=0;y<=2;y++)if(lamp(p,at.relative(side).above(y))&&lamp(p,at.relative(side.getOpposite()).above(y)))lights=true;
                var aim=Vec3.atCenterOf(at.above()).subtract(p.getEyePosition());if(lights&&aim.lengthSqr()>0&&p.getLookAngle().dot(aim.normalize())>.93){
                    if(!s.getString("doorGazeKey").equals(Hk3EggVanilla.key(p,at))){s.putString("doorGazeKey",Hk3EggVanilla.key(p,at));s.putInt("doorGaze",0);}doorway=true;break;
                }
            }
        }
        s.putInt("doorGaze",doorway?s.getInt("doorGaze")+5:0);if(s.getInt("doorGaze")>=100)Hk3EggVanilla.caseEvent(p,381);
        ArmorStand watched=null;
        if(!com.sirin.hk3gtl.common.narrative.Hk3NarrativeLog.isUnlocked(p,"E-EG-398"))for(var stand:p.level().getEntitiesOfClass(ArmorStand.class,p.getBoundingBox().inflate(6),a->a.isAlive())){
            var base=stand.blockPosition().below();var state=p.level().getBlockState(base);
            if(!memory.owns(p,base)||!(state.is(BlockTags.BASE_STONE_OVERWORLD)||state.is(BlockTags.STONE_BRICKS)||state.is(Blocks.COBBLESTONE)))continue;
            var aim=stand.getBoundingBox().getCenter().subtract(p.getEyePosition());if(aim.lengthSqr()>0&&p.getLookAngle().dot(aim.normalize())>.95&&p.hasLineOfSight(stand)){watched=stand;break;}
        }
        if(watched!=null){if(!s.hasUUID("armorWatching")||!s.getUUID("armorWatching").equals(watched.getUUID())){s.putUUID("armorWatching",watched.getUUID());s.putInt("armorGaze",0);}s.putInt("armorGaze",s.getInt("armorGaze")+5);if(s.getInt("armorGaze")>=100){s.putUUID("armorWatched",watched.getUUID());s.putDouble("armorWatchDistance",p.distanceToSqr(watched));}}
        else{s.putInt("armorGaze",0);if(s.hasUUID("armorWatched")){var target=p.serverLevel().getEntity(s.getUUID("armorWatched"));if(target!=null&&p.onGround()&&p.distanceToSqr(target)>s.getDouble("armorWatchDistance")+4){Hk3EggVanilla.caseEvent(p,398);s.remove("armorWatched");}}}
        boolean home=Hk3EggTravel.home(p,16);
        if(home){if(s.getBoolean("fieldTrip")&&s.getInt("fieldGoods")==7)Hk3EggVanilla.caseEvent(p,460);s.remove("fieldTrip");s.putInt("fieldGoods",0);s.putBoolean("departedHome",true);}
        else if(s.getBoolean("departedHome")&&!s.getBoolean("fieldTrip")){s.putBoolean("fieldTrip",true);s.putInt("fieldGoods",0);}
        s.putLong("sceneTick",now);
    }
    @SubscribeEvent public static void pickup(PlayerEvent.ItemPickupEvent e){
        if(!(e.getEntity() instanceof ServerPlayer p))return;var s=Hk3EggRuntime.state(p);if(!s.getBoolean("fieldTrip"))return;var stack=e.getStack();if(stack.isEmpty())return;int bit=0;
        if(stack.is(ItemTags.LOGS))bit|=4;if(stack.is(ItemTags.FISHES))bit|=2;if(stack.is(ItemTags.create(new net.minecraft.resources.ResourceLocation("forge","ores")))||stack.is(ItemTags.create(new net.minecraft.resources.ResourceLocation("forge","raw_materials"))))bit|=1;s.putInt("fieldGoods",s.getInt("fieldGoods")|bit);
    }
    @SubscribeEvent public static void died(net.minecraftforge.event.entity.living.LivingDeathEvent e){if(e.getEntity() instanceof ServerPlayer p){var s=Hk3EggRuntime.state(p);s.remove("fieldTrip");s.remove("departedHome");s.remove("armorWatched");}}
    @SubscribeEvent public static void logout(PlayerEvent.PlayerLoggedOutEvent e){if(e.getEntity() instanceof ServerPlayer p){var s=Hk3EggRuntime.state(p);s.remove("sceneTick");s.remove("fieldTrip");s.remove("departedHome");}}
}
