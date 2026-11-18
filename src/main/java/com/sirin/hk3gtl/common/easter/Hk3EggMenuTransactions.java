package com.sirin.hk3gtl.common.easter;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.inventory.*;
import net.minecraft.world.item.ItemStack;
import net.minecraft.core.registries.BuiltInRegistries;
import java.util.*;
 
 
 
public final class Hk3EggMenuTransactions {
    public record Snapshot(List<ItemStack> inventory,ItemStack carried,ItemStack input,ItemStack result){}
    public static final class Sorting {
        List<ItemStack> initial=List.of(),last=List.of();Map<String,Long> total=Map.of();final Set<String> moved=new HashSet<>();int empty;
        void reset(){initial=List.of();last=List.of();total=Map.of();moved.clear();empty=0;}
    }
    private Hk3EggMenuTransactions(){}
    private static List<ItemStack> inventory(ServerPlayer p){return p.getInventory().items.stream().map(ItemStack::copy).toList();}
    public static Snapshot before(ServerPlayer p,AbstractContainerMenu menu){
        if(p.containerMenu!=menu||!menu.stillValid(p))return null;
        ItemStack input=ItemStack.EMPTY,result=ItemStack.EMPTY;
        if(menu instanceof StonecutterMenu){input=menu.getSlot(0).getItem().copy();result=menu.getSlot(1).getItem().copy();}
        return new Snapshot(inventory(p),menu.getCarried().copy(),input,result);
    }
    private static String identity(ItemStack stack){var copy=stack.copy();copy.setCount(1);return copy.save(new net.minecraft.nbt.CompoundTag()).toString();}
    private static Map<String,Long> counts(List<ItemStack> inv,ItemStack carried){var out=new HashMap<String,Long>();for(var v:inv)if(!v.isEmpty())out.merge(identity(v),(long)v.getCount(),Long::sum);if(!carried.isEmpty())out.merge(identity(carried),(long)carried.getCount(),Long::sum);return out;}
    private static long count(List<ItemStack> inv,ItemStack carried,ItemStack result){return counts(inv,carried).getOrDefault(identity(result),0L);}
    private static boolean same(List<ItemStack> a,List<ItemStack> b){if(a.size()!=b.size())return false;for(int i=0;i<a.size();i++)if(!ItemStack.matches(a.get(i),b.get(i)))return false;return true;}
    public static void after(ServerPlayer p,AbstractContainerMenu menu,Snapshot before,Sorting sort){
        if(before==null||p.containerMenu!=menu||!menu.stillValid(p)){sort.reset();return;}
        var after=inventory(p);var carried=menu.getCarried();
        for(var slot:menu.slots)if(slot.container==p.getInventory())Hk3EggTools.batteryOwner(p,slot.getItem());
        Hk3EggTools.batteryOwner(p,carried);
        for(String id:List.of("gtladditions:barnarda_data","gtladditions:create_data")){
            var item=BuiltInRegistries.ITEM.get(new net.minecraft.resources.ResourceLocation(id)).getDefaultInstance();
            if(count(after,carried,item)>count(before.inventory,before.carried,item))Hk3EggUiReceipts.acquired(p,item);
        }
        if(menu instanceof StonecutterMenu&&!before.input.isEmpty()&&!before.result.isEmpty()){
            var current=menu.getSlot(0).getItem();int used=before.input.getCount()-(current.isEmpty()?0:ItemStack.isSameItemSameTags(current,before.input)?current.getCount():before.input.getCount());
            if(used>0&&count(after,carried,before.result)>count(before.inventory,before.carried,before.result)){
                var state=Hk3EggRuntime.state(p);String input=BuiltInRegistries.ITEM.getKey(before.input.getItem()).toString();String output=BuiltInRegistries.ITEM.getKey(before.result.getItem()).toString();
                var history=state.getCompound("stonecutInputs");String old=history.getString(input);
                if(!old.isEmpty()&&!old.equals(output))Hk3EggVanilla.caseEvent(p,412);
                if(history.size()<128||history.contains(input)){history.putString(input,output);state.put("stonecutInputs",history);}
            }
        }
        if(menu!=p.inventoryMenu){sort.reset();return;}
        var oldTotal=counts(before.inventory,before.carried);var newTotal=counts(after,carried);
        if(!oldTotal.equals(newTotal)){sort.reset();return;}
        if(sort.initial.isEmpty()||!sort.total.equals(oldTotal)||(!sort.last.isEmpty()&&!same(sort.last,before.inventory))){sort.reset();sort.initial=before.inventory;sort.total=oldTotal;sort.empty=(int)before.inventory.stream().filter(ItemStack::isEmpty).count();}
        for(int i=0;i<after.size();i++)if(!ItemStack.matches(before.inventory.get(i),after.get(i))){if(!after.get(i).isEmpty())sort.moved.add(BuiltInRegistries.ITEM.getKey(after.get(i).getItem()).toString());if(!before.inventory.get(i).isEmpty())sort.moved.add(BuiltInRegistries.ITEM.getKey(before.inventory.get(i).getItem()).toString());}
        sort.last=after;
        if(carried.isEmpty()&&sort.moved.size()>=8&&after.stream().filter(ItemStack::isEmpty).count()>sort.empty){Hk3EggVanilla.caseEvent(p,474);sort.reset();}
    }
}
