package com.sirin.hk3gtl.common.integration.ae;

import appeng.api.networking.IGrid;
import appeng.api.networking.crafting.CalculationStrategy;
import appeng.api.networking.crafting.ICraftingPlan;
import appeng.api.networking.crafting.ICraftingSimulationRequester;
import appeng.api.networking.security.IActionSource;
import appeng.api.stacks.AEFluidKey;
import appeng.api.stacks.AEItemKey;
import appeng.api.stacks.AEKey;
import appeng.api.stacks.GenericStack;
import appeng.core.definitions.AEItems;
import com.glodblock.github.extendedae.common.me.taglist.TagPriorityList;
import com.gregtechceu.gtceu.api.capability.IControllable;
import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.gregtechceu.gtceu.api.machine.TickableSubscription;
import com.gregtechceu.gtceu.api.machine.fancyconfigurator.FancyInvConfigurator;
import com.gregtechceu.gtceu.api.machine.trait.MachineTrait;
import com.gregtechceu.gtceu.integration.ae2.machine.MEInputBusPartMachine;
import com.gregtechceu.gtceu.integration.ae2.machine.MEInputHatchPartMachine;
import com.gregtechceu.gtceu.integration.ae2.machine.feature.IGridConnectedMachine;
import com.gregtechceu.gtceu.integration.ae2.machine.feature.multiblock.IMEStockingPart;
import com.gregtechceu.gtceu.integration.ae2.slot.ExportOnlyAEFluidList;
import com.gregtechceu.gtceu.integration.ae2.slot.ExportOnlyAEItemList;
import com.gregtechceu.gtceu.integration.ae2.slot.ExportOnlyAESlot;
import com.lowdragmc.lowdraglib.misc.ItemStackTransfer;
import com.lowdragmc.lowdraglib.syncdata.field.ManagedFieldHolder;
import com.sirin.hk3gtl.common.integration.ae.nexus.crafting.Hk3NexusCrafting;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.ItemStack;
import org.gtlcore.gtlcore.common.machine.multiblock.part.TagFilterMEStockBusPartMachine;
import org.gtlcore.gtlcore.common.machine.multiblock.part.TagFilterMEStockHatchPartMachine;

import java.math.BigInteger;
import java.util.Comparator;
import java.util.List;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Future;

public final class Hk3StockingCraftingCard extends MachineTrait {
    private static final String TAG = "hk3gtlStockingCraftingCard";
    private static final ManagedFieldHolder FIELDS = new ManagedFieldHolder(Hk3StockingCraftingCard.class);
    private final ItemStackTransfer card = new ItemStackTransfer(1) {
        @Override public int getSlotLimit(int slot) { return 1; }
    };
    private static final ExportOnlyAESlot[] NO_SLOTS = new ExportOnlyAESlot[0];
    private final IGridConnectedMachine network;
    private final boolean buffered;
    private ExportOnlyAESlot[] items = NO_SLOTS, fluids = NO_SLOTS;
    private final IActionSource source;
    private TickableSubscription subscription;
    private boolean loaded;
    private Pending pending;
    private int cursor;
    private String white = "", black = "";
    private TagPriorityList tags;

    private record Pending(IGrid grid, GenericStack request, Future<ICraftingPlan> plan) {}

    public Hk3StockingCraftingCard(MetaMachine machine) {
        super(machine);
        network = (IGridConnectedMachine) machine;
        source = IActionSource.ofMachine(network);
        buffered = (machine instanceof MEInputBusPartMachine || machine instanceof MEInputHatchPartMachine)
                && !(machine instanceof IMEStockingPart);
        card.setFilter(AEItems.CRAFTING_CARD::isSameAs);
        card.setOnContentsChanged(() -> {
            machine.markDirty();
            if (loaded) updateSubscription();
        });
    }

    @Override public ManagedFieldHolder getFieldHolder() { return FIELDS; }

    @Override public void saveCustomPersistedData(CompoundTag tag, boolean forDrop) {
        if (!forDrop && !card.getStackInSlot(0).isEmpty()) tag.put(TAG, card.getStackInSlot(0).save(new CompoundTag()));
    }

    @Override public void loadCustomPersistedData(CompoundTag tag) {
        card.setStackInSlot(0, ItemStack.of(tag.getCompound(TAG)));
    }

    @Override public void onMachineLoad() {
        loaded = !machine.isRemote();
        if (loaded) updateSubscription();
    }

    @Override public void onMachineUnLoad() {
        loaded = false;
        updateSubscription();
    }

    private void updateSubscription() {
        if (loaded && !card.getStackInSlot(0).isEmpty()) {
            if (subscription == null) {
                for (var trait : machine.getTraits()) {
                    if (trait instanceof ExportOnlyAEItemList itemList) items = itemList.getInventory();
                    if (trait instanceof ExportOnlyAEFluidList fluidList) fluids = fluidList.getInventory();
                }
                subscription = machine.subscribeServerTick(this::tick);
            }
            return;
        }
        machine.unsubscribe(subscription);
        subscription = null;
        cancel();
    }

    public FancyInvConfigurator configurator() {
        return new FancyInvConfigurator(card, Component.translatable("item.ae2.crafting_card"));
    }

    public void drops(List<ItemStack> drops) {
        if (!card.getStackInSlot(0).isEmpty()) drops.add(card.getStackInSlot(0).copy());
    }

    private void tick() {
        var node = network.getMainNode();
        if (!node.isActive() || (machine instanceof IControllable control && !control.isWorkingEnabled())) {
            cancel();
            return;
        }
        var grid = node.getGrid();
        var crafting = grid.getCraftingService();
        if (pending != null) {
            if (pending.grid() != grid) { cancel(); return; }
            if (!pending.plan().isDone()) return;
            var finished = pending;
            pending = null;
            var request = finished.request();
            if (finished.plan().isCancelled() || isRequesting(grid, request.what())) return;
            var remaining = target(grid, request.what());
            if (remaining == null || remaining.amount() < request.amount()) return;
            try {
                var plan = finished.plan().get();
                if (!plan.simulation()) crafting.submitJob(plan, null, null, true, source);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            } catch (ExecutionException ignored) {
            }
            return;
        }
        if (machine.getOffsetTimer() % 60 != 0) return;
        var request = target(grid, null);
        if (request == null) return;
        var key = request.what();
        long amount = request.amount();
        var strategy = CalculationStrategy.CRAFT_LESS;
        var nexus = Hk3NexusCrafting.plannerOn(grid);
        Future<ICraftingPlan> plan = nexus == null
                ? crafting.beginCraftingCalculation(machine.getLevel(), (ICraftingSimulationRequester) () -> source, key, amount, strategy)
                : nexus.calculate(key, BigInteger.valueOf(amount), source, strategy);
        pending = new Pending(grid, request, plan);
    }

    private void cancel() {
        if (pending == null) return;
        pending.plan().cancel(true);
        pending = null;
    }

    private static boolean isRequesting(IGrid grid, AEKey key) {
        return grid.getCraftingService().isRequesting(key)
                || Hk3NexusCrafting.forGrid(grid).stream().anyMatch(nexus -> nexus.inFlight(key).signum() > 0);
    }

    private GenericStack target(IGrid grid, AEKey requested) {
        if (machine instanceof TagFilterMEStockBusPartMachine || machine instanceof TagFilterMEStockHatchPartMachine)
            return tagTarget(grid, requested);
        var crafting = grid.getCraftingService();
        var inventory = grid.getStorageService().getCachedInventory();
        int count = items.length + fluids.length;
        for (int i = 0; i < count; i++) {
            int index = (cursor + i) % count;
            var slot = index < items.length ? items[index] : fluids[index - items.length];
            var config = buffered ? slot.requestStack() : slot.getConfig();
            if (config == null) continue;
            var key = config.what();
            long available = inventory.get(key);
            long amount = buffered ? config.amount() - available : available > 0 ? 0 : batchSize(key);
            if (amount <= 0) continue;
            if (requested != null ? key.equals(requested) : crafting.isCraftable(key) && !isRequesting(grid, key)) {
                if (requested == null) cursor = (index + 1) % count;
                return new GenericStack(key, amount);
            }
        }
        return null;
    }

    private static long batchSize(AEKey key) {
        return key instanceof AEItemKey item ? item.getMaxStackSize() : key.getAmountPerUnit();
    }

    private GenericStack tagTarget(IGrid grid, AEKey requested) {
        boolean item = machine instanceof TagFilterMEStockBusPartMachine;
        String nextWhite = item ? ((TagFilterMEStockBusPartMachine) machine).getTagWhite()
                : ((TagFilterMEStockHatchPartMachine) machine).getTagWhite();
        if (nextWhite.isBlank()) return null;
        String nextBlack = item ? ((TagFilterMEStockBusPartMachine) machine).getTagBlack()
                : ((TagFilterMEStockHatchPartMachine) machine).getTagBlack();
        if (!white.equals(nextWhite) || !black.equals(nextBlack)) {
            white = nextWhite;
            black = nextBlack;
            tags = new TagPriorityList(white, black);
        }
        if (requested != null && !matches(requested, item)) return null;
        for (var entry : grid.getStorageService().getCachedInventory())
            if (entry.getLongValue() > 0 && matches(entry.getKey(), item)) return null;
        if (requested != null) return new GenericStack(requested, batchSize(requested));
        return grid.getCraftingService().getCraftables(key -> matches(key, item)).stream()
                .filter(key -> !isRequesting(grid, key)).min(Comparator.comparing(AEKey::getId))
                .map(key -> new GenericStack(key, batchSize(key))).orElse(null);
    }

    private boolean matches(AEKey key, boolean item) {
        return (item ? key instanceof AEItemKey : key instanceof AEFluidKey) && tags.isListed(key);
    }
}
