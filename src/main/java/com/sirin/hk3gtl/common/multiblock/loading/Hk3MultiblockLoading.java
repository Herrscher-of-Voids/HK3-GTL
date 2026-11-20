package com.sirin.hk3gtl.common.multiblock.loading;

import com.gregtechceu.gtceu.api.block.ActiveBlock;
import com.gregtechceu.gtceu.api.machine.multiblock.MultiblockControllerMachine;
import com.gregtechceu.gtceu.api.pattern.MultiblockState;
import com.gregtechceu.gtceu.api.pattern.MultiblockWorldSavedData;
import com.sirin.hk3gtl.common.multiblock.build.Hk3IntegrityHost;
import com.sirin.hk3gtl.common.multiblock.build.Hk3InterfaceChunks;
import com.sirin.hk3gtl.common.multiblock.build.Hk3UniversalTerminalBuilder;
import it.unimi.dsi.fastutil.longs.Long2ObjectOpenHashMap;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.level.LevelEvent;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.util.ArrayList;
import java.util.IdentityHashMap;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentLinkedQueue;

/** GT共用成型入口；仅分批搬运世界读取，不替换任何机器的原判定。 */
@Mod.EventBusSubscriber(modid="hk3gtl")
public final class Hk3MultiblockLoading {
    private static final Set<MultiblockControllerMachine> QUEUED=ConcurrentHashMap.newKeySet();
    private static final ConcurrentLinkedQueue<MultiblockControllerMachine> REQUESTS=new ConcurrentLinkedQueue<>();
    private static final Set<MultiblockState> QUEUED_STATES=ConcurrentHashMap.newKeySet();
    private static final ConcurrentLinkedQueue<MultiblockState> STATES=new ConcurrentLinkedQueue<>();
    private static final LinkedHashMap<MultiblockControllerMachine,Hk3PatternLoading> CHECKS=new LinkedHashMap<>();
    private record Formation(ServerLevel level,Hk3InterfaceChunks tickets) {}
    private static final Map<MultiblockControllerMachine,Formation> FORMED=new IdentityHashMap<>();
    private static final Map<ServerLevel,Long2ObjectOpenHashMap<MultiblockControllerMachine>> FORMED_POSITIONS=new IdentityHashMap<>();
    private Hk3MultiblockLoading(){}

    public static boolean managed(MultiblockControllerMachine controller){return !(controller instanceof Hk3IntegrityHost);}
    public static boolean intercept(MultiblockControllerMachine controller){
        if(!(controller.getLevel() instanceof ServerLevel level)||!managed(controller)||Hk3PatternLoading.current(level)!=null)return false;
        if(level.getServer().isSameThread())controller.getMultiblockState().setError(MultiblockState.UNLOAD_ERROR);
        queue(controller);return true;
    }
    public static boolean intercept(MultiblockState state){
        if(!(state.world instanceof ServerLevel level)||Hk3PatternLoading.current(level)!=null)return false;
        if(state.lastController!=null&&!managed(state.lastController.self()))return false;
        if(!level.getServer().isSameThread()){
            if(QUEUED_STATES.add(state))STATES.add(state);
            return true;
        }
        if(!(state.getController() instanceof MultiblockControllerMachine controller)||!managed(controller))return false;
        state.setError(MultiblockState.UNLOAD_ERROR);queue(controller);return true;
    }
    public static void queue(MultiblockControllerMachine controller){
        if(controller.getLevel() instanceof ServerLevel&&managed(controller)&&QUEUED.add(controller))REQUESTS.add(controller);
    }
    public static void recheck(MultiblockControllerMachine controller){
        MultiblockWorldSavedData.getOrCreate((ServerLevel)controller.getLevel()).removeMapping(controller.getMultiblockState());
        controller.onStructureInvalid();queue(controller);
    }
    public static void invalidated(MultiblockControllerMachine controller){
        var formed=FORMED.remove(controller);
        if(formed!=null){
            formed.tickets().close();
            var positions=FORMED_POSITIONS.get(formed.level());
            positions.remove(controller.getPos().asLong());
            if(positions.isEmpty())FORMED_POSITIONS.remove(formed.level());
        }
        Hk3ActiveShells.remove(controller);
        var check=CHECKS.get(controller);
        if(check!=null&&!check.running()){CHECKS.remove(controller);check.close();}
    }
    public static void unloaded(MultiblockControllerMachine controller){QUEUED.remove(controller);invalidated(controller);}

    public static void changed(ServerLevel level,BlockPos pos,BlockState old,BlockState state){
        if(old==state)return;
        // 配方启停只改变活动位，不撤销已经匹配的机壳材料证据。
        if(old.getBlock()==state.getBlock()&&state.getBlock() instanceof ActiveBlock block
                &&block.changeActive(old,block.isActive(state))==state)return;
        for(var check:CHECKS.values())if(check.level==level
                &&!(check.running()&&check.controller.getPos().equals(pos)&&old.is(state.getBlock())))
            check.changed(pos,state);
        if(!old.is(state.getBlock())){
            var positions=FORMED_POSITIONS.get(level);
            if(positions!=null){
                var controller=positions.get(pos.asLong());
                if(controller!=null)unloaded(controller);
            }
        }
    }
    @SubscribeEvent public static void tick(TickEvent.ServerTickEvent event){
        if(event.phase!=TickEvent.Phase.END)return;
        long admissionDeadline=System.nanoTime()+500_000L;
        MultiblockState state;
        while(System.nanoTime()<admissionDeadline&&(state=STATES.poll())!=null){
            QUEUED_STATES.remove(state);
            if(state.getController() instanceof MultiblockControllerMachine controller)queue(controller);
        }
        int snapshotChecks=(int)CHECKS.values().stream().filter(Hk3PatternLoading::keepsSnapshots).count();
        MultiblockControllerMachine requested;
        for(int scanned=0;scanned<32 && CHECKS.size()<32 && System.nanoTime()<admissionDeadline
                && (requested=REQUESTS.poll())!=null;scanned++){
            if(requested.isInValid()||Hk3UniversalTerminalBuilder.isBuilding(requested)||CHECKS.containsKey(requested)
                    ||requested.isFormed()&&!requested.getMultiblockState().hasError()){
                QUEUED.remove(requested);
                continue;
            }
            boolean snapshots=Hk3PatternLoading.needsSnapshots(requested);
            if(snapshots && snapshotChecks>=4){REQUESTS.add(requested);continue;}
            QUEUED.remove(requested);
            if(requested.isFormed())requested.onStructureInvalid();
            CHECKS.put(requested,new Hk3PatternLoading(requested));
            if(snapshots)snapshotChecks++;
        }
        long deadline=System.nanoTime()+2_000_000L;
        for(int remaining=CHECKS.size();remaining>0&&!CHECKS.isEmpty()&&System.nanoTime()<deadline;remaining--){
            var check=CHECKS.values().iterator().next();
            var controller=check.controller;
            if(!check.valid()||Hk3UniversalTerminalBuilder.isBuilding(controller)){unloaded(controller);continue;}
            int result=check.capture(deadline)?check.check(deadline):0;
            if(!CHECKS.remove(controller,check))continue;
            if(result==0){CHECKS.put(controller,check);continue;}
            if(result>0){
                FORMED.put(controller,new Formation(check.level,check.retainUsed()));
                FORMED_POSITIONS.computeIfAbsent(check.level,ignored->new Long2ObjectOpenHashMap<>())
                        .put(controller.getPos().asLong(),controller);
                var data=MultiblockWorldSavedData.getOrCreate(check.level);
                data.addMapping(controller.getMultiblockState());data.removeAsyncLogic(controller);
            }else{
                controller.onStructureInvalid();
                var data=MultiblockWorldSavedData.getOrCreate(check.level);
                data.removeMapping(controller.getMultiblockState());
                data.removeAsyncLogic(controller);data.addAsyncLogic(controller);
            }
            check.close();
            if(System.nanoTime()>=deadline)break;
        }
    }
    @SubscribeEvent public static void levelUnload(LevelEvent.Unload event){
        if(!(event.getLevel() instanceof ServerLevel level))return;
        for(var controller:new ArrayList<>(CHECKS.keySet()))if(controller.getLevel()==level)unloaded(controller);
        var positions=FORMED_POSITIONS.get(level);
        if(positions!=null)for(var controller:new ArrayList<>(positions.values()))unloaded(controller);
    }
    @SubscribeEvent public static void stopped(ServerStoppedEvent event){
        CHECKS.values().forEach(Hk3PatternLoading::close);CHECKS.clear();
        FORMED.values().forEach(formation->formation.tickets().close());FORMED.clear();FORMED_POSITIONS.clear();QUEUED.clear();REQUESTS.clear();
        QUEUED_STATES.clear();STATES.clear();
    }
}
