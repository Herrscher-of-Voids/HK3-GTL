package com.sirin.hk3gtl.common.research;

/**
 * 【文件职责／本轮边界】独立实验统一分配实际物品与NBT，将耗材及工装区分存入支付快照。
 */

import net.minecraft.world.Container;
import net.minecraft.world.item.ItemStack;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import java.util.List;

public final class Hk3ResearchMaterialPayment {
    private Hk3ResearchMaterialPayment() {}
    public record Requirement(java.util.function.Predicate<ItemStack> match,int count,boolean tool) {}
    public static Prepared prepareExperiment(Container inventory,List<Requirement> requirements) {
        int slots=Math.min(36,inventory.getContainerSize());
        ItemStack[] before=new ItemStack[slots];long[] stock=new long[slots],demands=new long[requirements.size()];
        boolean[][] matches=new boolean[slots][requirements.size()];
        for(int j=0;j<demands.length;j++)demands[j]=requirements.get(j).count();
        for(int i=0;i<slots;i++) {
            before[i]=inventory.getItem(i).copy();stock[i]=before[i].getCount();
            for(int j=0;j<demands.length;j++)matches[i][j]=requirements.get(j).match().test(before[i]);
        }
        var plan=Hk3MaterialAllocation.allocateDetailed(stock,demands,matches);if(plan==null)return null;
        Prepared result=new Prepared(inventory,before,plan.used());
        for(int i=0;i<slots;i++)for(int j=0;j<demands.length;j++)if(requirements.get(j).tool() && plan.assigned()[i][j]>0)
            result.tools.add(before[i].copyWithCount(Math.toIntExact(plan.assigned()[i][j])).save(new CompoundTag()));
        return result;
    }

    public static Prepared prepare(Container inventory, int slots, List<Hk3ResearchPlans.Material> costs) {
        if (slots < 0 || slots > inventory.getContainerSize()) throw new IllegalArgumentException("Invalid slot range");
        ItemStack[] before = new ItemStack[slots]; long[] stock = new long[slots], demands = new long[costs.size()];
        boolean[][] matches = new boolean[slots][costs.size()];
        for (int j=0;j<costs.size();j++) demands[j]=costs.get(j).count();
        for (int i=0;i<slots;i++) {
            before[i]=inventory.getItem(i).copy(); stock[i]=before[i].getCount();
            for (int j=0;j<costs.size();j++) matches[i][j]=before[i].is(TagKey.create(Registries.ITEM, new ResourceLocation(costs.get(j).tag())));
        }
        long[] used = Hk3MaterialAllocation.allocate(stock, demands, matches);
        return used == null ? null : new Prepared(inventory, before, used);
    }

    public static final class Prepared {
        private final ItemStack[] before;
        private final long[] used;
        private final Hk3InventoryDebit<ItemStack> debit;
        private final ListTag tools=new ListTag();
        private Prepared(Container inventory, ItemStack[] before, long[] used) {
            this.before=before; this.used=used;
            java.util.List<ItemStack> after=new java.util.ArrayList<>();
            for (int i=0;i<before.length;i++) { ItemStack stack=before[i].copy(); stack.shrink(Math.toIntExact(used[i])); after.add(stack); }
            debit=new Hk3InventoryDebit<>(java.util.Arrays.asList(before),after,inventory::getItem,inventory::setItem,
                    ItemStack::matches,ItemStack::copy,inventory::setChanged);
        }

        public CompoundTag receipt() {
            CompoundTag result = new CompoundTag(); ListTag items = new ListTag();
            for (int i=0;i<used.length;i++) if (used[i]>0) items.add(before[i].copyWithCount(Math.toIntExact(used[i])).save(new CompoundTag()));
            result.put("Items", items); result.put("Tools",tools.copy()); return result;
        }

        public boolean commit() {
            return debit.commit();
        }
    }
}
