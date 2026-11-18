package com.sirin.hk3gtl.common.easter;
import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.gregtechceu.gtceu.api.machine.multiblock.MultiblockControllerMachine;
import com.gregtechceu.gtceu.api.pattern.MultiblockWorldSavedData;
import net.minecraft.server.level.*;
import net.minecraft.core.*;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid="hk3gtl")


public final class Hk3EggStructureScenes {
    private record Dismantled(ServerPlayer player,ServerLevel level,net.minecraftforge.event.level.BlockEvent.BreakEvent event,
                              MultiblockControllerMachine machine,net.minecraft.world.level.block.state.BlockState before,long tick) {}
    private static final java.util.Map<net.minecraft.server.MinecraftServer,java.util.List<Dismantled>> DISMANTLED=new java.util.concurrent.ConcurrentHashMap<>();
    private record Mined(ServerPlayer player,ServerLevel level,net.minecraftforge.event.level.BlockEvent.BreakEvent event){}
    private static final java.util.List<Mined> MINED=new java.util.ArrayList<>();
    private Hk3EggStructureScenes(){}
    @SubscribeEvent(priority=net.minecraftforge.eventbus.api.EventPriority.LOWEST)
    public static void breaking(net.minecraftforge.event.level.BlockEvent.BreakEvent e){
        if(e.isCanceled()||!(e.getPlayer() instanceof ServerPlayer p))return;
        var level=p.serverLevel();
        if(level.dimension().equals(com.sirin.hk3gtl.common.dimension.melon.Hk3MelonWorld.KEY)
                &&com.sirin.hk3gtl.common.dimension.melon.Hk3MelonAdventure.unlocked(p)
                &&!p.isCreative()&&!p.isSpectator()&&!e.getState().isAir()&&!e.getState().hasBlockEntity()
                &&e.getState().getDestroySpeed(level,e.getPos())>=0)
            MINED.add(new Mined(p,level,e));
        for(var state:MultiblockWorldSavedData.getOrCreate(level).getControllerInChunk(new net.minecraft.world.level.ChunkPos(e.getPos()))){
            if(state.hasError()||!state.isPosInCache(e.getPos())||!level.hasChunkAt(state.controllerPos))continue;
            var machine=MetaMachine.getMachine(level,state.controllerPos);
            if(!(machine instanceof com.sirin.hk3gtl.common.machine.wonder.Hk3WonderProductionMachine wonder)
                    ||!wonder.researchRole().startsWith("W")||!wonder.isFormed()||!wonder.verified())continue;
            var receipt=com.sirin.hk3gtl.common.civ.Hk3EngineeringFacts.receipt(p.server,
                    com.sirin.hk3gtl.common.research.Hk3ResearchData.get(p),wonder.getResearchTeamUUID(),wonder.researchRole());
            if(!receipt.getString("Facility").equals(level.dimension().location()+"@"+wonder.getPos()))continue;
            DISMANTLED.computeIfAbsent(p.server,key->new java.util.ArrayList<>()).add(new Dismantled(p,level,e,wonder,e.getState(),p.server.overworld().getGameTime()));
        }
    }
    @SubscribeEvent public static void dismantled(TickEvent.ServerTickEvent e){
        if(e.phase!=TickEvent.Phase.END)return;
        var mined=MINED.iterator();
        while(mined.hasNext()){
            var broken=mined.next();if(broken.player().server!=e.getServer())continue;mined.remove();
            var event=broken.event();var p=broken.player();var level=broken.level();
            if(!event.isCanceled()&&level.hasChunkAt(event.getPos())&&!level.getBlockState(event.getPos()).equals(event.getState()))
                Hk3EggRuntime.observe(p,"seed_sea_block_mined",java.util.Map.of("allowed","true","ordinary_block","true","changed","true"));
        }
        var pending=DISMANTLED.get(e.getServer());if(pending==null)return;
        var iterator=pending.iterator();long now=e.getServer().overworld().getGameTime();
        while(iterator.hasNext()){
            var broken=iterator.next();
            var event=broken.event();var machine=broken.machine();var level=broken.level();
            if(event.isCanceled()||!level.hasChunkAt(event.getPos())||level.getBlockState(event.getPos()).equals(broken.before())){
                iterator.remove();continue;
            }
            if(machine.isInValid()||!machine.isFormed()||machine.getMultiblockState().hasError()){
                Hk3EggRuntime.observe(broken.player(),"accepted_wonder_dismantled",java.util.Map.of("member_removed","true","invalidated","true"));
                iterator.remove();
            }else if(now-broken.tick()>=40)iterator.remove();
        }
        if(pending.isEmpty())DISMANTLED.remove(e.getServer());
    }
    @SubscribeEvent public static void stopped(net.minecraftforge.event.server.ServerStoppedEvent e){DISMANTLED.remove(e.getServer());MINED.removeIf(v->v.player().server==e.getServer());}
    public static void formed(MultiblockControllerMachine m){
        if(!(m.getLevel() instanceof ServerLevel level)||!m.isFormed()||m.getMultiblockState().hasError()||!(m.getHolder() instanceof BlockEntity be))return;
        var owner=m instanceof com.sirin.hk3gtl.common.machine.Hk3WorkableMultiblockMachine h?h.getOwnerUUID():be.getPersistentData().hasUUID(Hk3EggProduction.OWNER)?be.getPersistentData().getUUID(Hk3EggProduction.OWNER):null;
        if(owner==null)return;var p=level.getServer().getPlayerList().getPlayer(owner);if(p==null)return;
        var s=Hk3EggRuntime.state(p);var seen=s.getCompound("formedLocations");
        String key=Hk3EggNotes.digest("industrial:"+level.dimension().location()+":"+m.getPos().asLong()+":"+m.getDefinition().getId());
        if(seen.size()<100)seen.putBoolean(key,true);s.put("formedLocations",seen);if(seen.size()>=100)Hk3EggVanilla.caseEvent(p,67);
    }
    @SubscribeEvent public static void tick(TickEvent.PlayerTickEvent e){
        if(e.phase!=TickEvent.Phase.END||!(e.player instanceof ServerPlayer p)||p.tickCount%20!=0||!p.onGround()||p.getAbilities().flying||com.sirin.hk3gtl.common.narrative.Hk3NarrativeLog.isUnlocked(p,"E-EG-071"))return;
        var feet=p.blockPosition().below();
        for(var s:MultiblockWorldSavedData.getOrCreate(p.serverLevel()).getControllerInChunk(new net.minecraft.world.level.ChunkPos(feet))){
            if(!s.isPosInCache(feet)||s.hasError()||s.cache==null||!p.level().hasChunkAt(s.controllerPos))continue;
            var m=MetaMachine.getMachine(p.level(),s.controllerPos);
            if(!(m instanceof MultiblockControllerMachine controller)||!controller.isFormed()||!m.getDefinition().getId().toString().equals("hk3gtl:i01_honkai_collection_tower"))continue;
            int top=Integer.MIN_VALUE;
            for(long packed:s.cache){var at=BlockPos.of(packed);if(!p.level().hasChunkAt(at)){top=Integer.MAX_VALUE;break;}
                if(p.level().getBlockState(at).isFaceSturdy(p.level(),at,Direction.UP)&&p.level().getBlockState(at.above()).getCollisionShape(p.level(),at.above()).isEmpty()&&p.level().getBlockState(at.above(2)).getCollisionShape(p.level(),at.above(2)).isEmpty())top=Math.max(top,at.getY());}
            if(feet.getY()==top)Hk3EggVanilla.caseEvent(p,71);
        }
    }
}


