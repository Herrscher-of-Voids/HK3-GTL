package com.sirin.hk3gtl.common.capability;

import com.lowdragmc.lowdraglib.misc.FluidStorage;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.lowdragmc.lowdraglib.misc.ItemStackTransfer;
import com.lowdragmc.lowdraglib.side.fluid.FluidStack;
import net.minecraft.world.item.ItemStack;
import java.util.function.BiPredicate;
import java.util.function.Consumer;
import java.util.function.Supplier;

/**
 * 【变更记录 #1】2026-11-06 00:21:21 Asia/Hong_Kong（第1次备注 · 修订212）
 * 删除：无；新增：HK实际工作刻的标准本地槽位撤销记录，与现有能源票据逆序结算。
 * 修改：只捕获实际修改的单格，操作抛错后仍读取结果；回滚前比较状态，冲突暂停而不覆盖他机改动。
 * 用途：标准GT逐刻物品/流体失败与能源联合退还；不涵盖特殊仓、配方首尾、KubeJS动作或硬崩持久化。
 */
/** 【变更记录 #2】2026-11-06：回滚通知失败时保留重试状态，内容已恢复也须补完通知；仅保证票据仍存活期间。 */
public final class Hk3MaterialTick {
    private record Work(Hk3EnergyTick ticket, GTRecipe recipe) {}
    private static final ThreadLocal<Work> CURRENT = new ThreadLocal<>();
    private Hk3MaterialTick() {}

    public static <T> T run(Hk3EnergyTick ticket, GTRecipe recipe, Supplier<T> work) {
        ticket.requireOpen();
        var previous = CURRENT.get();
        CURRENT.set(new Work(ticket, recipe));
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
        }, ItemStack::matches, change);
    }

    public static <T> T fluid(GTRecipe recipe, FluidStorage storage, boolean simulate, Supplier<T> change) {
        if (storage.getClass() != FluidStorage.class) return change.get();
        return capture(recipe, simulate, () -> storage.getFluid().copy(),
                stack -> storage.setFluid(stack.copy()), FluidStack::isFluidStackEqual, change);
    }

    private static <V, T> T capture(GTRecipe recipe, boolean simulate, Supplier<V> read, Consumer<V> write,
                                    BiPredicate<V, V> same, Supplier<T> change) {
        var scope = CURRENT.get();
        if (simulate || scope == null || scope.recipe() != recipe) return change.get();
        var undo = new CellUndo<>(read, write, same);
        scope.ticket().undoWith(undo);
        try { return change.get(); }
        finally { undo.after = read.get(); undo.sealed = true; }
    }

    /** 先登记再写入，通知回调在写入后抛异常也不会漏记；未知结果或并发冲突保持暂停。 */
    private static final class CellUndo<V> implements Runnable {
        private final Supplier<V> read;
        private final Consumer<V> write;
        private final BiPredicate<V, V> same;
        private final V before;
        private V after;
        private boolean sealed;
        private boolean restorePending;
        private CellUndo(Supplier<V> read, Consumer<V> write, BiPredicate<V, V> same) {
            this.read = read; this.write = write; this.same = same; this.before = read.get();
        }
        public void run() {
            if (!sealed) throw new IllegalStateException("物料操作结果未知，保持暂停等待核对");
            V current = read.get();
            boolean restored = same.test(current, before);
            if (restored && !restorePending) return;
            if (!restored && !same.test(current, after)) throw new IllegalStateException("物料槽已被改写，禁止覆盖并暂停退款");
            restorePending = true;
            write.accept(before);
            if (!same.test(read.get(), before)) throw new IllegalStateException("物料回滚未完整生效");
            restorePending = false;
        }
    }
}
