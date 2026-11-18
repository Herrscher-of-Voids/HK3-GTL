package com.sirin.hk3gtl.common.easter;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.inventory.*;
import net.minecraft.world.item.*;
import net.minecraft.world.item.alchemy.PotionUtils;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.world.Container;
import java.util.*;
 
 
 
 
 
 
 
 
 
public final class Hk3EggContainers {
    private Hk3EggContainers(){}
    public static List<Hk3EggStorageFacts.Stack> snapshot(AbstractContainerMenu menu,ServerPlayer p){
        if(!(menu instanceof ChestMenu||menu instanceof HopperMenu||menu instanceof DispenserMenu||menu instanceof ShulkerBoxMenu)||!menu.stillValid(p))return List.of();
        var slots=new ArrayList<Hk3EggStorageFacts.Stack>();
        for(var slot:menu.slots)if(slot.container!=p.getInventory()){
            var s=slot.getItem();String potion=s.getItem() instanceof PotionItem?BuiltInRegistries.POTION.getKey(PotionUtils.getPotion(s)).toString():"";
            if(potion.endsWith(":empty")||potion.endsWith(":water"))potion="";
            slots.add(new Hk3EggStorageFacts.Stack(BuiltInRegistries.ITEM.getKey(s.getItem()).toString(),s.getCount(),s.getDamageValue(),s.isEdible(),s.hasCustomHoverName()?s.getHoverName().getString():"",potion));
            if(slots.size()>54)return List.of();
        }return List.copyOf(slots);
    }
    public static void changed(ServerPlayer p,AbstractContainerMenu menu,List<Hk3EggStorageFacts.Stack> before,List<Hk3EggStorageFacts.Stack> after,java.util.BitSet authored){
        if(before.isEmpty()||before.size()!=after.size())return;
        Hk3EggExtraScenes.stored(p,menu,before,after);
        Hk3EggScenePaths.stored(p,menu,before,after);
        Hk3EggTools.stored(p,menu,before,after);
        Hk3EggDispenser.stored(p,menu,before,after);
        Hk3EggDecor.container(p,menu,before,after);
        Hk3EggContainerSequences.changed(p,menu,before,after);
        for(int id:Hk3EggStorageFacts.evaluate(before,after,menu instanceof ChestMenu,authored))Hk3EggRuntime.observe(p,"container",Map.of("case",Integer.toString(id)));
    }
    public static void closed(ServerPlayer p,AbstractContainerMenu menu,List<Hk3EggStorageFacts.Stack> original,List<Hk3EggStorageFacts.Stack> last,boolean changed){
        if(!changed||last.isEmpty()||!last.equals(snapshot(menu,p)))return;
        var f=new LinkedHashMap<String,String>();
        f.put("empty",Long.toString(last.stream().filter(Hk3EggStorageFacts.Stack::empty).count()));
        f.put("chest",Boolean.toString(menu instanceof ChestMenu));
        f.put("wheat",Long.toString(Hk3EggStorageFacts.count(last,"minecraft:wheat")));
        f.put("carrot",Long.toString(Hk3EggStorageFacts.count(last,"minecraft:carrot")));
        f.put("potato",Long.toString(Hk3EggStorageFacts.count(last,"minecraft:potato")));
        Hk3EggRuntime.observe(p,"container_close",f);
        if(original.stream().allMatch(Hk3EggStorageFacts.Stack::empty)&&Hk3EggStorageFacts.count(last,"minecraft:wheat")==99)Hk3EggRuntime.observe(p,"container",Map.of("case","320"));
    }
}
