package com.sirin.hk3gtl.common.easter;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.*;
import net.minecraft.world.level.Level;
import net.minecraft.core.BlockPos;
import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.gregtechceu.gtceu.api.machine.feature.IRecipeLogicMachine;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.living.LivingEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.*;

@Mod.EventBusSubscriber(modid="hk3gtl")


public final class Hk3EggViews {
    private Hk3EggViews(){}
    public static void input(ServerPlayer p,String action){
        var s=Hk3EggRuntime.state(p);long now=p.server.overworld().getGameTime();String throttle="viewTick_"+action;
        if(s.contains(throttle)&&now-s.getLong(throttle)<10)return;s.putLong(throttle,now);
        if(action.equals("inventory")&&p.containerMenu==p.inventoryMenu){
            if(p.getInventory().items.stream().allMatch(v->!v.isEmpty()))Hk3EggVanilla.caseEvent(p,314);
            if(List.of("minecraft:compass","minecraft:clock","minecraft:spyglass","minecraft:shield").stream().allMatch(id->Hk3EggVanilla.count(p,id)>0))Hk3EggVanilla.caseEvent(p,441);
        }else if(action.equals("map_view")){
            ItemStack map=p.getMainHandItem().is(Items.FILLED_MAP)?p.getMainHandItem():p.getOffhandItem();if(!map.is(Items.FILLED_MAP))return;
            var data=MapItem.getSavedData(map,p.level());if(data==null)return;var date=Hk3EggCalendar.now();
            if(s.getBoolean("filledMap")&&data.dimension.location().toString().equals(s.getString("filledMapDim"))&&data.scale==s.getInt("filledMapScale")){
                long dx=Math.abs((long)data.centerX-s.getInt("filledMapX")),dz=Math.abs((long)data.centerZ-s.getInt("filledMapZ")),span=128L<<data.scale;
                boolean unfinished=false;for(byte color:data.colors)if(color==0){unfinished=true;break;}
                if(unfinished&&((dx==span&&dz==0)||(dz==span&&dx==0)))Hk3EggVanilla.caseEvent(p,489);
            }
            if(date.getMonthValue()==4&&date.getDayOfMonth()==22&&data.dimension==Level.OVERWORLD)Hk3EggVanilla.caseEvent(p,349);
            if(date.getMonthValue()==8&&date.getDayOfMonth()==19)Hk3EggVanilla.caseEvent(p,360);
        }
    }
    @SubscribeEvent public static void tick(TickEvent.PlayerTickEvent e){
        if(e.phase!=TickEvent.Phase.END||!(e.player instanceof ServerPlayer p)||p.tickCount%200!=0||com.sirin.hk3gtl.common.narrative.Hk3NarrativeLog.isUnlocked(p,"E-EG-033"))return;
        var source=p.serverLevel().getChunkSource();var center=p.chunkPosition();int count=0;
        outer:for(int cx=center.x-6;cx<=center.x+6;cx++)for(int cz=center.z-6;cz<=center.z+6;cz++){
            var chunk=source.getChunkNow(cx,cz);if(chunk==null)continue;
            for(var be:chunk.getBlockEntities().values()){
                if(be.isRemoved()||p.position().distanceToSqr(net.minecraft.world.phys.Vec3.atCenterOf(be.getBlockPos()))>96*96)continue;
                if(be instanceof com.gregtechceu.gtceu.api.machine.IMachineBlockEntity holder&&holder.getMetaMachine() instanceof IRecipeLogicMachine logic&&!logic.self().isInValid()&&logic.getRecipeLogic().isWorking()&&!logic.getRecipeLogic().isHasNotEnoughEnergy())if(++count>=50)break outer;
            }
        }
        Hk3EggRuntime.observe(p,"running_machines",Map.of("count",Integer.toString(count)));
    }
    @SubscribeEvent public static void jump(LivingEvent.LivingJumpEvent e){
        if(!(e.getEntity() instanceof ServerPlayer p))return;var pos=p.blockPosition().below();if(!p.level().hasChunkAt(pos))return;
        var m=MetaMachine.getMachine(p.level(),pos);
        if(m==null){
            for(var state:com.gregtechceu.gtceu.api.pattern.MultiblockWorldSavedData.getOrCreate(p.serverLevel()).getControllerInChunk(new net.minecraft.world.level.ChunkPos(pos))){
                if(!state.isPosInCache(pos)||state.hasError()||!p.level().hasChunkAt(state.controllerPos))continue;
                var controller=MetaMachine.getMachine(p.level(),state.controllerPos);
                if(controller instanceof com.gregtechceu.gtceu.api.machine.multiblock.MultiblockControllerMachine c&&c.isFormed()&&c instanceof IRecipeLogicMachine&& !c.getDefinition().getId().getPath().contains("flagship")&&!c.getDefinition().getId().getPath().contains("hyperion")){
                    if(Hk3EggVanilla.increment(p,"machineJumps",5)>=5)Hk3EggVanilla.caseEvent(p,462);return;
                }
            }
        }
        if(m instanceof IRecipeLogicMachine&&!(m instanceof com.gregtechceu.gtceu.api.machine.multiblock.MultiblockControllerMachine))if(Hk3EggVanilla.increment(p,"machineJumps",5)>=5)Hk3EggVanilla.caseEvent(p,462);
    }
}
