package com.sirin.hk3gtl.common.multiblock.loading;

import com.gregtechceu.gtceu.api.block.ActiveBlock;
import com.gregtechceu.gtceu.api.machine.multiblock.MultiblockControllerMachine;
import com.gregtechceu.gtceu.api.pattern.MultiblockState;
import com.gregtechceu.gtceu.api.pattern.MultiblockWorldSavedData;
import com.sirin.hk3gtl.common.multiblock.build.Hk3IntegrityHost;
import com.sirin.hk3gtl.common.multiblock.build.Hk3InterfaceChunks;
import com.sirin.hk3gtl.common.multiblock.build.Hk3UniversalTerminalBuilder;
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
    private static final Map<MultiblockControllerMachine,Hk3PatternLoading> CHECKS=new LinkedHashMap<>();
    private static final Map<MultiblockControllerMachine,Hk3InterfaceChunks> FORMED=new IdentityHashMap<>();
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
        var retained=FORMED.remove(controller);if(retained!=null)retained.close();
        Hk3ActiveShells.remove(controller);
        if(controller.getLevel() instanceof ServerLevel level){
            var current=Hk3PatternLoading.current(level);if(current!=null&&current.controller==controller)return;
        }
        var check=CHECKS.remove(controller);if(check!=null)check.close();
    }
    public static void unloaded(MultiblockControllerMachine controller){QUEUED.remove(controller);invalidated(controller);}

    public static void changed(ServerLevel level,BlockPos pos,BlockState old,BlockState state){
        if(old==state)return;
        // 配方启停只改变活动位，不撤销已经匹配的机壳材料证据。
        if(old.getBlock()==state.getBlock()&&state.getBlock() instanceof ActiveBlock block
                &&block.changeActive(old,block.isActive(state))==state)return;
        for(var check:CHECKS.values())if(check.level==level
                &&!(Hk3PatternLoading.current(level)==check&&check.controller.getPos().equals(pos)&&old.is(state.getBlock())))
            check.changed(pos,state);
        if(!old.is(state.getBlock())){
            for(var controller:new ArrayList<>(FORMED.keySet()))
                if(controller.getLevel()==level&&controller.getPos().equals(pos))unloaded(controller);
        }
    }
    @SubscribeEvent public static void tick(TickEvent.ServerTickEvent event){
        if(event.phase!=TickEvent.Phase.END)return;
        MultiblockState state;
        while((state=STATES.poll())!=null){
            QUEUED_STATES.remove(state);
            if(state.getController() instanceof MultiblockControllerMachine controller)queue(controller);
        }
        MultiblockControllerMachine requested;
        while((requested=REQUESTS.poll())!=null){
            QUEUED.remove(requested);
            if(requested.isInValid()||Hk3UniversalTerminalBuilder.isBuilding(requested)||CHECKS.containsKey(requested)
                    ||requested.isFormed()&&!requested.getMultiblockState().hasError())continue;
            if(requested.isFormed())requested.onStructureInvalid();
            CHECKS.put(requested,new Hk3PatternLoading(requested));
        }
        long deadline=System.nanoTime()+2_000_000L;
        for(var check:new ArrayList<>(CHECKS.values())){
            if(System.nanoTime()>=deadline)break;
            var controller=check.controller;
            if(!check.valid()||Hk3UniversalTerminalBuilder.isBuilding(controller)){unloaded(controller);continue;}
            if(!check.capture(deadline))continue;
            int result=check.check(deadline);
            if(result==0){CHECKS.remove(controller);CHECKS.put(controller,check);continue;}
            CHECKS.remove(controller);
            if(result>0){
                FORMED.put(controller,check.retainUsed());
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
        for(var controller:new ArrayList<>(FORMED.keySet()))if(controller.getLevel()==level)unloaded(controller);
    }
    @SubscribeEvent public static void stopped(ServerStoppedEvent event){
        CHECKS.values().forEach(Hk3PatternLoading::close);CHECKS.clear();
        FORMED.values().forEach(Hk3InterfaceChunks::close);FORMED.clear();QUEUED.clear();REQUESTS.clear();
        QUEUED_STATES.clear();STATES.clear();
    }
}
