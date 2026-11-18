package com.sirin.hk3gtl.common.easter;
import net.minecraft.core.*;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.*;
import net.minecraft.world.item.*;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.stats.Stats;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.living.LivingEntityUseItemEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.entity.player.PlayerContainerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.*;

@Mod.EventBusSubscriber(modid="hk3gtl")





















public final class Hk3EggVanilla {
    private record Placement(java.util.UUID player,net.minecraft.resources.ResourceKey<net.minecraft.world.level.Level> dimension,BlockPos pos,BlockState before,BlockState after){}
    private static final Map<net.minecraft.server.MinecraftServer,ArrayDeque<Placement>> PENDING=new java.util.concurrent.ConcurrentHashMap<>();
    private Hk3EggVanilla(){}
    public static void queuePlacement(ServerPlayer p,BlockPos pos,BlockState before,BlockState after){
        var queue=PENDING.computeIfAbsent(p.server,k->new ArrayDeque<>());
        if(queue.size()<4096)queue.addLast(new Placement(p.getUUID(),p.level().dimension(),pos.immutable(),before,after));
    }
    @SubscribeEvent public static void flush(TickEvent.ServerTickEvent e){
        if(e.phase!=TickEvent.Phase.END)return;var server=e.getServer();var queue=PENDING.remove(server);if(queue==null)return;
        for(var pending:queue){var p=server.getPlayerList().getPlayer(pending.player);var level=server.getLevel(pending.dimension);
            if(p==null||level==null||p.level()!=level||!level.hasChunkAt(pending.pos)||!level.getBlockState(pending.pos).equals(pending.after))continue;
            placed(p,pending.pos,pending.before,pending.after);
        }
    }
    @SubscribeEvent public static void stop(net.minecraftforge.event.server.ServerStoppedEvent e){PENDING.remove(e.getServer());}
    public static void placed(ServerPlayer p,BlockPos pos,BlockState before,BlockState after){
        if(before.equals(after))return;
        Hk3EggBuildings.placed(p,pos,after);
        Hk3EggMachineBoundaries.placed(p,pos,after);
        Hk3EggNativeMachineScenes.icePlaced(p,pos,after);
        Hk3EggFestivalActions.placed(p,pos,after);
        Hk3EggExtraScenes.placed(p,pos,after);
        Hk3EggTravel.placed(p,pos,after);
        Hk3EggScenePaths.placed(p,pos,after);
        Hk3EggLocalScenes.placed(p,pos,after);
        Hk3EggLineBranch.placed(p,pos);
        Hk3EggProduction.placed(p,pos);
        Hk3EggCurrentPaths.placed(p,pos,after);
        Hk3EggLifeEvents.lamp(p,pos,after);
        Hk3EggContainerSequences.placed(p,pos);
        String id=BuiltInRegistries.BLOCK.getKey(after.getBlock()).toString();
        var f=new LinkedHashMap<>(Hk3EggCalendar.facts(Hk3EggCalendar.now(),p.server.overworld().getDayTime()));
        boolean ordinary=!after.hasBlockEntity()&&after.isCollisionShapeFullBlock(p.level(),pos)
                &&(after.is(BlockTags.PLANKS)||after.is(BlockTags.STONE_BRICKS)||after.is(BlockTags.BASE_STONE_OVERWORLD)||after.is(BlockTags.WOOL)||id.endsWith("_concrete")||after.is(Blocks.BRICKS)||after.is(Blocks.COBBLESTONE)||after.is(Blocks.DIRT));
        f.put("ordinary_building",Boolean.toString(ordinary));
        f.put("block",id);f.put("creative",Boolean.toString(p.isCreative()));
        f.put("lantern",Boolean.toString(Hk3EggFestivalActions.lantern(after)));
        f.put("sapling",Boolean.toString(after.is(BlockTags.SAPLINGS)));f.put("flower",Boolean.toString(after.is(BlockTags.FLOWERS)));
        f.put("ordinary_ground",Boolean.toString(p.level().hasChunkAt(pos.below())
                &&p.level().getBlockState(pos.below()).is(BlockTags.DIRT)&&after.canSurvive(p.level(),pos)));
        f.put("snow",Boolean.toString(p.level().getBiome(pos).value().coldEnoughToSnow(pos)));
        Hk3EggRuntime.observe(p,"block_placed",f);
        if(after.is(BlockTags.FLOWERS))distinct(p,"flowers",pos,11,291);
        if(after.getBlock() instanceof GlassBlock||after.getBlock() instanceof StainedGlassBlock)distinct(p,"glass",pos,22,302);
        if(after.is(Blocks.CHEST)){
            boolean air=true;for(Direction dir:Direction.values()){var side=pos.relative(dir);if(!p.level().hasChunkAt(side)||!p.level().getBlockState(side).isAir()){air=false;break;}}
            if(air)caseEvent(p,286);
        }
        if(after.is(Blocks.CAKE)){var cakes=Hk3EggRuntime.state(p).getCompound("ownCakes");if(cakes.size()<128)cakes.putBoolean(key(p,pos),true);Hk3EggRuntime.state(p).put("ownCakes",cakes);}
        if(after.is(Blocks.WHEAT)){
            // 任一角定位最多625次局部查询，不跨未加载区块；须全部由本人种下。
            var cells=Hk3EggRuntime.state(p).getCompound("wheatPlaced");String key=key(p,pos);
            if(cells.size()<1024)cells.putBoolean(key,true);Hk3EggRuntime.state(p).put("wheatPlaced",cells);
            for(int dx=-4;dx<=0;dx++)for(int dz=-4;dz<=0;dz++){
                boolean all=true;for(int x=0;x<5&&all;x++)for(int z=0;z<5;z++){
                    var at=pos.offset(dx+x,0,dz+z);if(!cells.getBoolean(key(p,at))||!Hk3EggBuildMemory.get(p.serverLevel()).owns(p,at)||!p.level().hasChunkAt(at)||!p.level().getBlockState(at).is(Blocks.WHEAT)){all=false;break;}}
                if(all){caseEvent(p,305);return;}
            }
        }
    }
    public static void broken(ServerPlayer p,BlockPos pos,BlockState old){
        Hk3EggExploration.broken(p,pos,old);
        Hk3EggWaterFall.broken(p,pos);
        if(old.getBlock() instanceof CropBlock crop&&crop.isMaxAge(old)){
            Hk3EggPersonalScenes.farming(p,"harvest");
            var f=new LinkedHashMap<>(Hk3EggCalendar.facts(Hk3EggCalendar.now(),p.server.overworld().getDayTime()));
            Hk3EggRuntime.observe(p,"crop_harvest",f);
            Hk3EggRuntime.state(p).putLong("harvestTick",p.server.overworld().getGameTime());
        }
        if((old.is(Blocks.GRASS)||old.is(Blocks.TALL_GRASS))&&p.getMainHandItem().getItem() instanceof SwordItem){
            long n=increment(p,"grassSword",10);if(n==10)caseEvent(p,482);
        }
        if(old.is(Blocks.REDSTONE_ORE)||old.is(Blocks.DEEPSLATE_REDSTONE_ORE))Hk3EggRuntime.state(p).putLong("redstoneMineTick",p.server.overworld().getGameTime());
    }
    public static void caseEvent(ServerPlayer p,int id){Hk3EggRuntime.observe(p,"vanilla_case",Map.of("case",Integer.toString(id)));}
    public static String key(ServerPlayer p,BlockPos pos){return p.level().dimension().location()+":"+pos.asLong();}
    private static void distinct(ServerPlayer p,String field,BlockPos pos,int limit,int id){
        var state=Hk3EggRuntime.state(p);var cells=state.getCompound(field);if(cells.size()>=limit)return;
        cells.putBoolean(key(p,pos),true);state.put(field,cells);if(cells.size()==limit)caseEvent(p,id);
    }
    public static long increment(ServerPlayer p,String key,long cap){var s=Hk3EggRuntime.state(p);long n=Math.min(cap,Math.max(0,s.getLong(key))+1);s.putLong(key,n);return n;}
    public static long count(ServerPlayer p,String id){long n=0;for(var s:p.getInventory().items)if(BuiltInRegistries.ITEM.getKey(s.getItem()).toString().equals(id))n+=s.getCount();return n;}
    @SubscribeEvent public static void craft(PlayerEvent.ItemCraftedEvent e){
        if(!(e.getEntity() instanceof ServerPlayer p)||e.getCrafting().isEmpty())return;
        Hk3EggProduction.handmade(p,e.getCrafting());
        String item=BuiltInRegistries.ITEM.getKey(e.getCrafting().getItem()).toString();
        var inputs=e.getInventory();int occupied=0;for(int i=0;i<inputs.getContainerSize();i++)if(!inputs.getItem(i).isEmpty())occupied++;
        Hk3EggRuntime.observe(p,"crafted",Hk3EggRuntime.fields("item",item,"input_slots",Integer.toString(occupied)));
        Hk3EggCurrentPaths.crafted(p,item);
        if(e.getCrafting().getItem() instanceof TieredItem){var types=Hk3EggRuntime.state(p).getCompound("craftedTools");if(types.size()<5)types.putBoolean(item,true);Hk3EggRuntime.state(p).put("craftedTools",types);if(types.size()==5)caseEvent(p,440);}
    }
    @SubscribeEvent public static void ate(LivingEntityUseItemEvent.Finish e){
        if(!(e.getEntity() instanceof ServerPlayer p)||!e.getItem().isEdible())return;
        Hk3EggRuntime.observe(p,"food_finished",withTime(p,"item",BuiltInRegistries.ITEM.getKey(e.getItem().getItem()).toString()));
        if(Hk3EggRuntime.state(p).getBoolean("placedOrangeHoney"))Hk3EggVanilla.caseEvent(p,414);
        if(p.getHealth()<p.getMaxHealth())Hk3EggRuntime.state(p).putBoolean("foodRecovery",true);
        Hk3EggRuntime.state(p).putLong("ateTick",p.server.overworld().getGameTime());
        if(e.getItem().getItem()==Items.COOKED_BEEF||e.getItem().getItem()==Items.COOKED_CHICKEN||e.getItem().getItem()==Items.COOKED_PORKCHOP||e.getItem().getItem()==Items.COOKED_MUTTON||e.getItem().getItem()==Items.COOKED_RABBIT||e.getItem().getItem()==Items.COOKED_COD||e.getItem().getItem()==Items.COOKED_SALMON)Hk3EggRuntime.state(p).putBoolean("ateCooked",true);
    }
    public static Map<String,String> withTime(ServerPlayer p,String... pairs){var f=new LinkedHashMap<>(Hk3EggCalendar.facts(Hk3EggCalendar.now(),p.server.overworld().getDayTime()));f.putAll(Hk3EggRuntime.fields(pairs));return f;}
    @SubscribeEvent public static void opened(PlayerContainerEvent.Open e){
        if(!(e.getEntity() instanceof ServerPlayer p))return;
        if(e.getContainer() instanceof net.minecraft.world.inventory.ChestMenu||e.getContainer() instanceof net.minecraft.world.inventory.ShulkerBoxMenu||e.getContainer() instanceof net.minecraft.world.inventory.HopperMenu){
            if(count(p,"gtceu:copper_credit")>0)caseEvent(p,237);
        }
    }
    @SubscribeEvent public static void tick(TickEvent.PlayerTickEvent e){
        if(e.phase!=TickEvent.Phase.END||!(e.player instanceof ServerPlayer p)||p.tickCount%20!=0)return;
        Hk3EggCurrentPaths.tick(p);
        Hk3EggExtraScenes.tick(p);
        var s=Hk3EggRuntime.state(p);var stats=p.getStats();
        Hk3EggRuntime.observe(p,"player_stats",Hk3EggRuntime.fields("walk_cm",Integer.toString(stats.getValue(Stats.CUSTOM.get(Stats.WALK_ONE_CM))),"arrows",Integer.toString(stats.getValue(Stats.ITEM_USED.get(Items.BOW))),"fish",Integer.toString(stats.getValue(Stats.CUSTOM.get(Stats.FISH_CAUGHT)))));
        Hk3EggRuntime.observe(p,"holdings",Hk3EggRuntime.fields("soulium",Long.toString(count(p,BuiltInRegistries.ITEM.getKey(com.gregtechceu.gtceu.api.data.chemical.ChemicalHelper.get(com.gregtechceu.gtceu.api.data.tag.TagPrefix.ingot,com.sirin.hk3gtl.common.material.SouliumMaterial.SOULIUM).getItem()).toString())),"crystal",Long.toString(count(p,"hk3gtl:honkai_energy_crystal"))));
        boolean sleep=p.isSleeping();if(sleep&&!s.getBoolean("sleeping")){Hk3EggRuntime.observe(p,"slept",withTime(p));Hk3EggDecor.sleeping(p);}s.putBoolean("sleeping",sleep);
        long now=p.server.overworld().getGameTime();
        if(s.contains("harvestTick")&&now-s.getLong("harvestTick")<=60&&count(p,"minecraft:wheat_seeds")==17)caseEvent(p,297);
        if(s.contains("redstoneMineTick")&&now-s.getLong("redstoneMineTick")<=60&&count(p,"minecraft:redstone")==33)caseEvent(p,313);
    }
}
