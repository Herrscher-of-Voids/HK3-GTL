package com.sirin.hk3gtl.common.easter;

import net.minecraft.server.level.ServerPlayer;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.item.*;
import net.minecraft.stats.Stats;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.*;

@Mod.EventBusSubscriber(modid="hk3gtl")





public final class Hk3EggCurrentPaths {
    private Hk3EggCurrentPaths(){}
    public static void crafted(ServerPlayer p,String id){
        var s=Hk3EggRuntime.state(p);
        if(p.containerMenu instanceof net.minecraft.world.inventory.CraftingMenu&&(id.equals("gtceu:resistor")||id.equals("gtceu:capacitor"))){
            String menu=p.getUUID()+":"+p.containerMenu.containerId;
            if(!s.getString("partsMenu").equals(menu)){s.putString("partsMenu",menu);s.remove("resistorMade");s.remove("capacitorMade");}
            s.putBoolean(id.equals("gtceu:resistor")?"resistorMade":"capacitorMade",true);
            if(s.getBoolean("resistorMade")&&s.getBoolean("capacitorMade"))Hk3EggVanilla.caseEvent(p,212);
        }
        if(Hk3EggVanilla.count(p,"gtceu:smd_resistor")>0&&Hk3EggVanilla.count(p,"gtceu:smd_capacitor")>0&&Hk3EggVanilla.count(p,"gtceu:smd_transistor")>0)Hk3EggVanilla.caseEvent(p,215);
    }
    public static void placed(ServerPlayer p,BlockPos pos,BlockState state){
        var s=Hk3EggRuntime.state(p);
        if(state.is(Blocks.LANTERN)&&p.level().getBiome(pos).value().coldEnoughToSnow(pos)){
            var lamps=s.getCompound("snowLamps");if(lamps.size()<128)lamps.putBoolean(Hk3EggVanilla.key(p,pos),true);s.put("snowLamps",lamps);
            for(var axis:List.of(net.minecraft.core.Direction.EAST,net.minecraft.core.Direction.SOUTH))for(int offset=0;offset<5;offset++){
                boolean row=true;for(int i=0;i<5;i++){var at=pos.relative(axis,i-offset);if(!lamps.getBoolean(Hk3EggVanilla.key(p,at))||!Hk3EggBuildMemory.get(p.serverLevel()).owns(p,at)||!p.level().hasChunkAt(at)||!p.level().getBlockState(at).is(Blocks.LANTERN)){row=false;break;}}
                if(row)Hk3EggVanilla.caseEvent(p,454);
            }
        }
    }
    @SubscribeEvent public static void dimension(PlayerEvent.PlayerChangedDimensionEvent e){
        if(!(e.getEntity() instanceof ServerPlayer p))return;var s=Hk3EggRuntime.state(p);
        String from=e.getFrom().location().toString(),to=e.getTo().location().toString();
        if(s.getString("dimensionStart").equals(to)&&s.getString("dimensionEnd").equals(from))Hk3EggVanilla.caseEvent(p,408);
        s.putString("dimensionStart",from);s.putString("dimensionEnd",to);
        if(e.getTo()==Level.OVERWORLD)s.putBoolean("returnedOverworld",true);
    }
    @SubscribeEvent public static void menuOpened(net.minecraftforge.event.entity.player.PlayerContainerEvent.Open e){
        if(!(e.getEntity() instanceof ServerPlayer p))return;var s=Hk3EggRuntime.state(p);var menu=e.getContainer();
        if(menu instanceof appeng.menu.me.common.MEStorageMenu){if(s.getInt("aeMachineSequence")==2)Hk3EggVanilla.caseEvent(p,463);s.putInt("aeMachineSequence",1);}
        if(menu instanceof com.lowdragmc.lowdraglib.gui.modular.ModularUIContainer heldUi&&heldUi.getModularUI().holder instanceof com.lowdragmc.lowdraglib.gui.factory.HeldItemUIFactory.HeldItemHolder held&&menu.stillValid(p)&&net.minecraft.core.registries.BuiltInRegistries.ITEM.getKey(held.getHeld().getItem()).toString().equals("gtlsupb:super_terminal"))Hk3EggVanilla.caseEvent(p,262);
        if(menu instanceof com.lowdragmc.lowdraglib.gui.modular.ModularUIContainer ui&&ui.getModularUI().holder instanceof com.gregtechceu.gtceu.api.machine.MetaMachine machine){
            if(s.getInt("aeMachineSequence")==1)s.putInt("aeMachineSequence",2);
            if(machine instanceof com.sirin.hk3gtl.common.machine.research.Hk3HonkaiAbsorptionMachine&&machine.getDefinition().getId().toString().equals("hk3gtl:i01_honkai_collection_tower"))Hk3EggVanilla.caseEvent(p,1);
        }
    }
    @SubscribeEvent public static void respawn(PlayerEvent.PlayerRespawnEvent e){if(e.getEntity() instanceof ServerPlayer p&&!e.isEndConquered())Hk3EggRuntime.state(p).putBoolean("deathFirstMessage",true);}
    @SubscribeEvent public static void menuClosed(net.minecraftforge.event.entity.player.PlayerContainerEvent.Close e){
        if(e.getEntity() instanceof ServerPlayer p){var s=Hk3EggRuntime.state(p);s.remove("partsMenu");s.remove("resistorMade");s.remove("capacitorMade");}
    }
    public static void tick(ServerPlayer p){
        var s=Hk3EggRuntime.state(p);
        if(s.getBoolean("returnedOverworld")&&p.level().dimension()==Level.OVERWORLD&&p.getRespawnDimension()==Level.OVERWORLD&&p.getRespawnPosition()!=null&&p.position().distanceTo(net.minecraft.world.phys.Vec3.atCenterOf(p.getRespawnPosition()))<=16){Hk3EggVanilla.caseEvent(p,439);s.remove("returnedOverworld");}
        String biome=p.level().getBiome(p.blockPosition()).unwrapKey().map(k->k.location().toString()).orElse("");
        if(p.level().dimension()==Level.OVERWORLD&&!biome.isEmpty()){
            var biomes=s.getCompound("visitedBiomes");
            if(!biomes.getBoolean(biome)){
                if(s.getBoolean("adventurePlanRead")){Hk3EggVanilla.caseEvent(p,418);s.remove("adventurePlanRead");}
                if(s.getBoolean("biomesInitialized")&&Hk3EggCalendar.now().getMonthValue()==8)Hk3EggVanilla.caseEvent(p,359);
                if(biomes.size()<4096)biomes.putBoolean(biome,true);s.put("visitedBiomes",biomes);s.putBoolean("biomesInitialized",true);
            }
        }
    }
}
