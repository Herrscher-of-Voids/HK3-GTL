package com.sirin.hk3gtl.common.easter;

import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.gregtechceu.gtceu.api.machine.multiblock.MultiblockControllerMachine;
import com.gregtechceu.gtceu.api.pattern.MultiblockWorldSavedData;
import com.sirin.hk3gtl.common.civ.Hk3EngineeringFacts;
import com.sirin.hk3gtl.common.machine.wonder.Hk3WonderProductionMachine;
import com.sirin.hk3gtl.common.multiblock.build.Hk3UniversalTerminalBuilder;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3LargeStructurePattern;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3WonderPatternSource;
import com.sirin.hk3gtl.common.research.Hk3ResearchData;
import com.sirin.hk3gtl.common.research.Hk3ResearchTeams;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.BlockTags;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

@Mod.EventBusSubscriber(modid="hk3gtl")
public final class Hk3EggFacilityScenes {
    private record Site(MultiblockControllerMachine machine,BlockPos min,BlockPos max) {
        boolean contains(BlockPos p){return p.getX()>=min.getX()&&p.getX()<=max.getX()
                &&p.getY()>=min.getY()&&p.getY()<=max.getY()&&p.getZ()>=min.getZ()&&p.getZ()<=max.getZ();}
        boolean outside(BlockPos p,int radius){
            int x=Math.max(0,Math.max(min.getX()-p.getX(),p.getX()-max.getX()));
            int y=Math.max(0,Math.max(min.getY()-p.getY(),p.getY()-max.getY()));
            int z=Math.max(0,Math.max(min.getZ()-p.getZ(),p.getZ()-max.getZ()));
            return !contains(p)&&x*x+y*y+z*z<=radius*radius;
        }
        String key(){return machine.getLevel().dimension().location()+"@"+machine.getPos();}
        boolean valid(ServerPlayer p){return machine.getLevel()==p.level()&&!machine.isInValid()
                &&machine.isFormed()&&!machine.getMultiblockState().hasError()
                &&(!(machine instanceof Hk3WonderProductionMachine wonder)||wonder.verified());}
    }
    private static final Map<String,Hk3WonderPatternSource.Header> HEADERS=new ConcurrentHashMap<>();
    private static final Map<UUID,Site> WALKING=new ConcurrentHashMap<>();
    private static final Map<UUID,Site> RETURNS=new ConcurrentHashMap<>();
    private Hk3EggFacilityScenes(){}

    private static Site site(MultiblockControllerMachine machine){
        if(machine instanceof Hk3WonderProductionMachine wonder){
            var h=HEADERS.computeIfAbsent(wonder.researchRole(),role->{
                try(var source=Hk3WonderPatternSource.open(role)){return source.header();}
            });
            var rotation=Hk3UniversalTerminalBuilder.rotation(h.facing(),machine.getFrontFacing());
            var a=new BlockPos(-h.cx(),-h.cy(),-h.cz()).rotate(rotation).offset(machine.getPos());
            var b=new BlockPos(h.width()-1-h.cx(),h.height()-1-h.cy(),h.depth()-1-h.cz()).rotate(rotation).offset(machine.getPos());
            return new Site(machine,new BlockPos(Math.min(a.getX(),b.getX()),Math.min(a.getY(),b.getY()),Math.min(a.getZ(),b.getZ())),
                    new BlockPos(Math.max(a.getX(),b.getX()),Math.max(a.getY(),b.getY()),Math.max(a.getZ(),b.getZ())));
        }
        Hk3LargeStructurePattern.Bounds box=machine.getMultiblockState().getMatchContext().get(Hk3LargeStructurePattern.BOUNDS_KEY);
        return box==null?null:new Site(machine,box.min(),box.max());
    }
    private static Site find(ServerPlayer p,BlockPos pos,String role,int radius,boolean inside){
        var level=p.serverLevel();var saved=MultiblockWorldSavedData.getOrCreate(level);var seen=new HashSet<BlockPos>();
        for(int x=(pos.getX()-radius)>>4;x<=(pos.getX()+radius)>>4;x++)
            for(int z=(pos.getZ()-radius)>>4;z<=(pos.getZ()+radius)>>4;z++){
                if(!level.hasChunk(x,z))continue;
                for(var state:saved.getControllerInChunk(new ChunkPos(x,z))){
                    if(!seen.add(state.controllerPos)||state.hasError()||!level.hasChunkAt(state.controllerPos))continue;
                    var machine=MetaMachine.getMachine(level,state.controllerPos);
                    if(!(machine instanceof MultiblockControllerMachine controller)||!controller.isFormed()
                            ||controller.getMultiblockState()!=state)continue;
                    if(role.startsWith("W")){
                        if(!(controller instanceof Hk3WonderProductionMachine wonder)||!wonder.researchRole().equals(role)||!wonder.verified())continue;
                    }else if(!controller.getDefinition().getId().toString().equals("hk3gtl:"+role))continue;
                    var site=site(controller);
                    if(site!=null&&(inside?site.contains(pos):site.outside(pos,radius)))return site;
                }
            }
        return null;
    }
    public static void placed(ServerPlayer p,BlockPos pos,BlockState block){
        if((block.is(Blocks.TORCH)||block.is(Blocks.WALL_TORCH))&&find(p,pos,"W09",3,false)!=null)
            Hk3EggRuntime.observe(p,"consensus_torch_placed",Map.of("placed","true","outside","true"));
        if((block.is(Blocks.REDSTONE_TORCH)||block.is(Blocks.REDSTONE_WALL_TORCH))&&find(p,pos,"W15",3,false)!=null)
            Hk3EggRuntime.observe(p,"audience_torch_placed",Map.of("placed","true","outside","true"));
        if(block.is(BlockTags.SMALL_FLOWERS)&&block.canSurvive(p.level(),pos)
                &&find(p,pos,"i28_world_bubble_termination_reclaimer",4,false)!=null)
            Hk3EggRuntime.observe(p,"termination_flower_planted",Map.of("placed","true","outside","true"));
    }
    public static void book(ServerPlayer p,BlockPos pos){
        if(find(p,pos,"W09",4,false)!=null)Hk3EggRuntime.observe(p,"consensus_book_placed",Map.of("written_book","true","outside","true"));
    }
    public static void played(ServerPlayer p,BlockPos pos){
        if(Hk3EggBuildMemory.get(p.serverLevel()).owns(p,pos)&&find(p,pos,"W11",4,false)!=null)
            Hk3EggRuntime.observe(p,"command_note_played",Map.of("placed_by_player","true","played","true"));
    }
    public static void firework(ServerPlayer p,BlockPos pos){
        if(find(p,pos,"i33_imitation_divine_key_assembly_center",0,true)!=null)
            Hk3EggRuntime.observe(p,"divine_key_firework_launched",Map.of("spawned","true","inside","true"));
    }
    @SubscribeEvent public static void tick(TickEvent.PlayerTickEvent e){
        if(e.phase!=TickEvent.Phase.END||!(e.player instanceof ServerPlayer p))return;
        boolean acceptance=!com.sirin.hk3gtl.common.narrative.Hk3NarrativeLog.isUnlocked(p,"E-EG-029");
        boolean returningNeeded=!com.sirin.hk3gtl.common.narrative.Hk3NarrativeLog.isUnlocked(p,"E-EG-100");
        boolean walkingNeeded=com.sirin.hk3gtl.common.machine.wonder.Hk3WonderCatalog.hasBlueprint("W15")
                &&!com.sirin.hk3gtl.common.narrative.Hk3NarrativeLog.isUnlocked(p,"E-EG-077");
        if(!walkingNeeded)WALKING.remove(p.getUUID());
        if(!returningNeeded)RETURNS.remove(p.getUUID());
        if(!acceptance&&!returningNeeded&&!walkingNeeded)return;
        var s=Hk3EggRuntime.state(p);long now=p.server.overworld().getGameTime();
        if(p.tickCount%20==0){
            var data=Hk3ResearchData.get(p);var scope=Hk3ResearchTeams.scope(p.server,p.getUUID());
            if(acceptance&&!Hk3EngineeringFacts.receipt(p.server,data,scope,"W09").isEmpty())
                Hk3EggRuntime.observe(p,"consensus_accepted",Map.of("valid_receipt","true"));
            if(s.getBoolean("graduatedReturnLogin")&&returningNeeded){
                var nearby=find(p,p.blockPosition(),"W09",4,false);
                if(nearby==null)RETURNS.remove(p.getUUID());else RETURNS.put(p.getUUID(),nearby);
            }
            if(walkingNeeded){
                var walking=find(p,p.blockPosition(),"W15",0,true);
                if(walking==null)WALKING.remove(p.getUUID());else WALKING.put(p.getUUID(),walking);
            }
        }
        var returning=RETURNS.get(p.getUUID());
        if(returning!=null&&returning.valid(p)&&returning.outside(p.blockPosition(),4)){
            boolean same=s.getLong("consensusReturnTick")==now-1&&returning.key().equals(s.getString("consensusReturnSite"));
            int stay=same?s.getInt("consensusReturnTicks")+1:1;
            s.putString("consensusReturnSite",returning.key());s.putLong("consensusReturnTick",now);s.putInt("consensusReturnTicks",stay);
            if(stay>=100){
                Hk3EggRuntime.observe(p,"graduated_consensus_return",Map.of("new_login","true","stay_ticks","100"));
                RETURNS.remove(p.getUUID());
            }
        }else{s.remove("consensusReturnTick");s.remove("consensusReturnTicks");}
        if(!walkingNeeded)return;
        var previous=new Vec3(s.getDouble("facilityWalkX"),s.getDouble("facilityWalkY"),s.getDouble("facilityWalkZ"));
        var delta=p.position().subtract(previous);var walking=WALKING.get(p.getUUID());
        boolean continuous=s.getLong("facilityWalkTick")==now-1&&s.getString("facilityWalkDim").equals(p.level().dimension().location().toString());
        if(walking!=null&&walking.valid(p)&&walking.contains(p.blockPosition())&&continuous&&delta.lengthSqr()<2.25
                &&p.onGround()&&!p.getAbilities().flying&&!p.isPassenger()){
            double distance=s.getDouble("audienceWalk")+Math.sqrt(delta.x*delta.x+delta.z*delta.z);
            s.putDouble("audienceWalk",Math.min(16,distance));
            if(distance>=16)Hk3EggRuntime.observe(p,"audience_walked",Map.of("distance","16"));
        }
        s.putDouble("facilityWalkX",p.getX());s.putDouble("facilityWalkY",p.getY());s.putDouble("facilityWalkZ",p.getZ());
        s.putLong("facilityWalkTick",now);s.putString("facilityWalkDim",p.level().dimension().location().toString());
    }
    @SubscribeEvent public static void logout(PlayerEvent.PlayerLoggedOutEvent e){
        WALKING.remove(e.getEntity().getUUID());
        RETURNS.remove(e.getEntity().getUUID());
        if(e.getEntity() instanceof ServerPlayer p){var s=Hk3EggRuntime.state(p);s.remove("facilityWalkTick");s.remove("consensusReturnSite");}
    }
    @SubscribeEvent public static void stopped(ServerStoppedEvent e){
        WALKING.entrySet().removeIf(v->v.getValue().machine().getLevel().getServer()==e.getServer());
        RETURNS.entrySet().removeIf(v->v.getValue().machine().getLevel().getServer()==e.getServer());
    }
}
