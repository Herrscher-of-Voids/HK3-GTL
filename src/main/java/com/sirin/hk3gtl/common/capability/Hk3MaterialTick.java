package com.sirin.hk3gtl.common.capability;

import com.lowdragmc.lowdraglib.misc.FluidStorage;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.lowdragmc.lowdraglib.misc.ItemStackTransfer;
import com.lowdragmc.lowdraglib.side.fluid.FluidStack;
import net.minecraft.world.item.ItemStack;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import com.gregtechceu.gtceu.api.machine.trait.RecipeLogic;
import com.gregtechceu.gtceu.api.machine.trait.NotifiableItemStackHandler;
import com.gregtechceu.gtceu.api.machine.trait.NotifiableFluidTank;
import com.gregtechceu.gtceu.api.capability.recipe.IO;
import com.gregtechceu.gtceu.api.capability.recipe.ItemRecipeCapability;
import com.gregtechceu.gtceu.api.capability.recipe.FluidRecipeCapability;
import com.sirin.hk3gtl.common.util.Hk3LedgerValidation;
import java.util.function.Function;
import java.util.function.BiPredicate;
import java.util.function.Consumer;
import java.util.function.Supplier;

 





 
public final class Hk3MaterialTick {
    private record Work(Hk3EnergyTick ticket, GTRecipe recipe, RecipeLogic logic) {}
    private static final ThreadLocal<Work> CURRENT = new ThreadLocal<>();
    private Hk3MaterialTick() {}

    public static void committed(GTRecipe recipe,Runnable receipt) {
        var work=CURRENT.get();
        if(work!=null&&work.recipe()==recipe)work.ticket().onCommit(receipt);
        else receipt.run();
    }

    public static <T> T run(Hk3EnergyTick ticket, GTRecipe recipe, Supplier<T> work) {
        return run(ticket, recipe, null, work);
    }

    public static <T> T run(Hk3EnergyTick ticket, GTRecipe recipe, RecipeLogic logic, Supplier<T> work) {
        ticket.requireOpen();
        var previous = CURRENT.get();
        CURRENT.set(new Work(ticket, recipe, logic));
        try { return work.get(); }
        finally {
            if (previous == null) CURRENT.remove();
            else CURRENT.set(previous);
        }
    }

    public static ItemStack item(GTRecipe recipe, ItemStackTransfer storage, int slot, boolean simulate,
                                 Supplier<ItemStack> change) {
        if (storage.getClass() != ItemStackTransfer.class) return change.get();
        return capture(recipe, simulate, () -> storage.getStackInSlot(slot).copy(), stack -> {
            storage.setStackInSlot(slot, stack.copy());
            storage.onContentsChanged(slot);
        }, ItemStack::matches, change, () -> target(storage), "item", slot, Hk3MaterialTick::itemTag);
    }

    public static <T> T fluid(GTRecipe recipe, FluidStorage storage, boolean simulate, Supplier<T> change) {
        if (storage.getClass() != FluidStorage.class) return change.get();
        return capture(recipe, simulate, () -> storage.getFluid().copy(),
                stack -> storage.setFluid(stack.copy()), FluidStack::isFluidStackEqual, change,
                () -> target(storage), "fluid", 0, value -> value.saveToTag(new CompoundTag()).copy());
    }

    private static <V, T> T capture(GTRecipe recipe, boolean simulate, Supplier<V> read, Consumer<V> write,
                                    BiPredicate<V, V> same, Supplier<T> change,
                                    Supplier<Hk3RefundTarget> locate, String kind, int slot,
                                    Function<V, CompoundTag> encode) {
        var scope = CURRENT.get();
        if (simulate || scope == null || recipe == null || scope.recipe() != recipe || !recipe.ingredientActions.isEmpty())
            return change.get();
        var target = locate.get();
        if (target != null && kind.equals("fluid")) slot = target.address().getInt("Storage");
        var undo = new CellUndo<>(read, write, same, read.get(), target, kind, slot, encode);
        scope.ticket().undoWith(undo);
        try { return change.get(); }
        finally { undo.after = read.get(); undo.sealed = true; }
    }

    /** 先登记再写入，通知回调在写入后抛异常也不会漏记；未知结果或并发冲突保持暂停。 */
    private static final class CellUndo<V> implements Hk3RefundJournal.Action {
        private final Supplier<V> read;
        private final Consumer<V> write;
        private final BiPredicate<V, V> same;
        private final V before;
        private final Hk3RefundTarget target;
        private final String kind;
        private final int slot;
        private final Function<V, CompoundTag> encode;
        private V after;
        private boolean sealed;
        private boolean restorePending;
        private CellUndo(Supplier<V> read, Consumer<V> write, BiPredicate<V, V> same, V before,
                         Hk3RefundTarget target, String kind, int slot, Function<V, CompoundTag> encode) {
            this.read = read; this.write = write; this.same = same; this.before = before;
            this.target = target; this.kind = kind; this.slot = slot; this.encode = encode;
        }
        @Override public CompoundTag snapshot() {
            var tag = new CompoundTag();
            if (target == null) {
                tag.putString("Kind", "unsupported"); tag.putString("Class", getClass().getName()); return tag;
            }
            tag.putString("Kind", kind); tag.put("Target", target.address().copy()); tag.putInt("Slot", slot);
            tag.put("Before", encode.apply(before).copy());
            tag.putBoolean("Sealed", sealed); tag.putBoolean("RestorePending", restorePending);
            if (sealed) tag.put("After", encode.apply(after).copy());
            return tag;
        }
        public void run() {
            if (target != null) {
                var current = restoredCell(target.server(), snapshot());
                try { current.apply(); }
                finally { restorePending = current.restorePending; }
                return;
            }
            apply();
        }
        private void apply() {
            var block = target == null ? null : target.machine().getHolder().getSelf();
            if (!sealed) throw new IllegalStateException("物料操作结果未知，保持暂停等待核对");
            V current = read.get();
            boolean restored = same.test(current, before);
            if (restored && !restorePending) return;
            if (!restored && !same.test(current, after)) throw new IllegalStateException("物料槽已被改写，禁止覆盖并暂停退款");
            restorePending = true;
            try { write.accept(before); }
            finally { if (block != null) block.setChanged(); }
            if (!same.test(read.get(), before)) throw new IllegalStateException("物料回滚未完整生效");
            restorePending = false;
        }
    }

    private static Hk3RefundTarget target(Object storage) {
        var scope = CURRENT.get();
        if (scope == null || scope.logic() == null) return null;
        for (IO io : IO.values()) {
            var itemHandlers = scope.logic().machine.getCapabilitiesProxy().get(io, ItemRecipeCapability.CAP);
            if (itemHandlers != null) for (var value : itemHandlers)
                if (value instanceof NotifiableItemStackHandler handler && handler.storage == storage)
                    return Hk3RefundTarget.capture(handler);
            var fluidHandlers = scope.logic().machine.getCapabilitiesProxy().get(io, FluidRecipeCapability.CAP);
            if (fluidHandlers != null) for (var value : fluidHandlers) if (value instanceof NotifiableFluidTank handler) {
                var tanks = handler.getStorages();
                for (int i = 0; i < tanks.length; i++) if (tanks[i] == storage) {
                    var target = Hk3RefundTarget.capture(handler);
                    target.address().putInt("Storage", i);
                    return target;
                }
            }
        }
        return null;
    }

    static Hk3RefundJournal.Action restore(MinecraftServer server, CompoundTag saved) {
        validate(saved);
        return new Hk3RefundJournal.Action() {
            private CompoundTag state = saved.copy();
            @Override public CompoundTag snapshot() { return state.copy(); }
            @Override public void run() {
                var undo = restoredCell(server, state);
                try { undo.apply(); }
                finally { state = undo.snapshot(); }
            }
        };
    }

    private static CellUndo<?> restoredCell(MinecraftServer server, CompoundTag tag) {
        var target = new Hk3RefundTarget(server, tag.getCompound("Target").copy());
        int slot = tag.getInt("Slot");
        CellUndo<?> undo;
        if (tag.getString("Kind").equals("item")) {
            if (!(target.trait() instanceof NotifiableItemStackHandler handler)
                    || handler.storage.getClass() != ItemStackTransfer.class || slot >= handler.storage.getSlots())
                throw new IllegalStateException("原物品槽不支持持久退款");
            var storage = handler.storage;
            var item = new CellUndo<>(() -> storage.getStackInSlot(slot).copy(), value -> {
                storage.setStackInSlot(slot, value.copy()); storage.onContentsChanged(slot);
            }, ItemStack::matches, itemStack(tag.getCompound("Before")), target, "item", slot, Hk3MaterialTick::itemTag);
            if (tag.getBoolean("Sealed")) item.after = itemStack(tag.getCompound("After"));
            undo = item;
        } else {
            if (!(target.trait() instanceof NotifiableFluidTank handler) || slot >= handler.getStorages().length
                    || handler.getStorages()[slot].getClass() != FluidStorage.class)
                throw new IllegalStateException("原流体槽不支持持久退款");
            var storage = handler.getStorages()[slot];
            var fluid = new CellUndo<>(() -> storage.getFluid().copy(), value -> storage.setFluid(value.copy()),
                    FluidStack::isFluidStackEqual, fluidStack(tag.getCompound("Before")), target, "fluid", slot,
                    value -> value.saveToTag(new CompoundTag()).copy());
            if (tag.getBoolean("Sealed")) fluid.after = fluidStack(tag.getCompound("After"));
            undo = fluid;
        }
        undo.sealed = tag.getBoolean("Sealed");
        undo.restorePending = tag.getBoolean("RestorePending");
        return undo;
    }

    static void validate(CompoundTag tag) {
        Hk3LedgerValidation.type(tag, "Target", Tag.TAG_COMPOUND);
        Hk3RefundTarget.validate(tag.getCompound("Target"), true);
        Hk3LedgerValidation.type(tag, "Slot", Tag.TAG_INT);
        Hk3LedgerValidation.require(tag.getInt("Slot") >= 0, "退款物料槽位");
        if (tag.getString("Kind").equals("fluid")) {
            Hk3LedgerValidation.type(tag.getCompound("Target"), "Storage", Tag.TAG_INT);
            Hk3LedgerValidation.require(tag.getCompound("Target").getInt("Storage") == tag.getInt("Slot"), "退款流体槽索引");
        }
        Hk3LedgerValidation.flag(tag, "Sealed", true);
        Hk3LedgerValidation.flag(tag, "RestorePending", true);
        Hk3LedgerValidation.type(tag, "Before", Tag.TAG_COMPOUND);
        if (tag.getBoolean("Sealed")) Hk3LedgerValidation.type(tag, "After", Tag.TAG_COMPOUND);
        for (String key : tag.getBoolean("Sealed") ? java.util.List.of("Before", "After") : java.util.List.of("Before")) {
            if (tag.getString("Kind").equals("item")) itemStack(tag.getCompound(key));
            else fluidStack(tag.getCompound(key));
        }
    }

    private static CompoundTag itemTag(ItemStack stack) {
        var tag = stack.save(new CompoundTag()).copy();
        // 原版Count是byte；标准槽被扩容时也必须保留完整int数量。
        tag.putByte("Count", (byte) (stack.isEmpty() ? 0 : 1));
        tag.putInt("CountExact", stack.getCount());
        return tag;
    }

    private static ItemStack itemStack(CompoundTag tag) {
        Hk3LedgerValidation.type(tag, "id", Tag.TAG_STRING);
        Hk3LedgerValidation.type(tag, "CountExact", Tag.TAG_INT);
        Hk3LedgerValidation.type(tag, "Count", Tag.TAG_BYTE);
        int count = tag.getInt("CountExact");
        Hk3LedgerValidation.require(tag.getByte("Count") == (byte) (count == 0 ? 0 : 1), "退款物品编码数量");
        var id = ResourceLocation.tryParse(tag.getString("id"));
        Hk3LedgerValidation.require(count >= 0 && id != null && BuiltInRegistries.ITEM.containsKey(id), "退款物品身份");
        var stack = ItemStack.of(tag.copy());
        Hk3LedgerValidation.require(count == 0 || !stack.isEmpty(), "退款物品解码");
        stack.setCount(count);
        return stack;
    }

    private static FluidStack fluidStack(CompoundTag tag) {
        Hk3LedgerValidation.type(tag, "FluidName", Tag.TAG_STRING);
        Hk3LedgerValidation.type(tag, "Amount", Tag.TAG_LONG);
        Hk3LedgerValidation.optionalType(tag, "Tag", Tag.TAG_COMPOUND);
        var id = ResourceLocation.tryParse(tag.getString("FluidName"));
        Hk3LedgerValidation.require(tag.getLong("Amount") >= 0 && id != null && BuiltInRegistries.FLUID.containsKey(id),
                "退款流体身份");
        var stack = FluidStack.loadFromTag(tag.copy());
        Hk3LedgerValidation.require(tag.getLong("Amount") == 0 || !stack.isEmpty(), "退款流体解码");
        return stack;
    }
}
