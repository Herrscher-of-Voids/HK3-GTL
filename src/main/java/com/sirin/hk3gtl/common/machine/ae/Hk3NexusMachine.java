package com.sirin.hk3gtl.common.machine.ae;

import appeng.api.networking.IManagedGridNode;
import appeng.api.networking.crafting.ICraftingProvider;
import com.gregtechceu.gtceu.api.machine.IMachineBlockEntity;
import com.gregtechceu.gtceu.api.machine.feature.IFancyUIMachine;
import com.gregtechceu.gtceu.api.machine.feature.IMachineLife;
import com.gregtechceu.gtceu.api.machine.feature.IDropSaveMachine;
import com.gregtechceu.gtceu.api.machine.multiblock.MultiblockControllerMachine;
import com.gregtechceu.gtceu.integration.ae2.machine.feature.IGridConnectedMachine;
import com.lowdragmc.lowdraglib.gui.modular.ModularUI;
import com.sirin.hk3gtl.common.integration.ae.nexus.crafting.Hk3NexusCrafting;
import com.sirin.hk3gtl.common.integration.ae.nexus.management.Hk3NexusManagement;
import com.sirin.hk3gtl.common.integration.ae.nexus.network.Hk3NexusGrid;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.phys.BlockHitResult;

import java.util.UUID;

public final class Hk3NexusMachine extends MultiblockControllerMachine
        implements IFancyUIMachine, IGridConnectedMachine, IMachineLife, IDropSaveMachine {
    private final Hk3NexusGrid network = new Hk3NexusGrid(this::markDirty);
    private final Hk3NexusCrafting crafting = new Hk3NexusCrafting(
            network::getActionableNode, this::getLevel, this::plannerId, this::markDirty);
    private final Hk3NexusManagement management = new Hk3NexusManagement(
            network::getGrid, this::getLevel, crafting, this::markDirty);
    private UUID owner;
    private UUID plannerId;
    private boolean attached;
    private boolean online;

    public Hk3NexusMachine(IMachineBlockEntity holder) {
        super(holder);
        network.setPatternInventory(management.patterns());
        network.getMainNode().addService(ICraftingProvider.class, crafting);
        crafting.setPatterns(management::localPatterns);
        crafting.setInfiniteSource(network::isInfiniteSource);
        management.setInfiniteSource(network::isInfiniteSource);
    }

    public Hk3NexusGrid network() { return network; }
    public Hk3NexusManagement management() { return management; }
    @Override public IManagedGridNode getMainNode() { return network.getMainNode(); }
    @Override public boolean isOnline() { return online; }
    @Override public void setOnline(boolean online) { this.online = online; }

    @Override public void onLoad() {
        super.onLoad();
        if (!isRemote()) {
            connect();
            subscribeServerTick(this::tickNexus);
        }
    }

    @Override public void onUnload() { disconnect(); super.onUnload(); }
    @Override public void onMachineRemoved() {
        disconnect();
        if (isRemote()) return;
        clearInventory(management.patterns());
        clearInventory(network.pager(0, network.slotCount()));
    }
    @Override public boolean savePickClone() { return false; }
    @Override public void onPartUnload() { disconnect(); super.onPartUnload(); }
    @Override public void onStructureFormed() { super.onStructureFormed(); connect(); }
    @Override public void onStructureInvalid() { disconnect(); super.onStructureInvalid(); }

    private void connect() {
        if (attached || !isFormed() || owner == null || !(getLevel() instanceof ServerLevel level)) return;
        network.attach(level, getPos(), owner);
        com.sirin.hk3gtl.common.easter.Hk3EggEngineering.formed(this, owner);
        attached = true;
    }

    private void disconnect() {
        if (!attached) return;
        crafting.close();
        network.detach();
        attached = false;
        online = false;
    }

    private void tickNexus() {
        if (!attached) return;
        network.tick();
        updateMEStatus();
        crafting.tick();
        if (online) management.tick();
    }

    @Override public void onMachinePlaced(LivingEntity placer, ItemStack stack) {
        if (!isRemote() && placer instanceof Player player) {
            if (plannerId == null) plannerId = UUID.randomUUID();
            setOwner(player);
        }
    }

    private UUID plannerId() {
        if (plannerId == null) {
            String origin = getLevel().dimension().location() + ":" + getPos().asLong() + ":" + owner;
            plannerId = UUID.nameUUIDFromBytes(origin.getBytes(java.nio.charset.StandardCharsets.UTF_8));
        }
        return plannerId;
    }

    @Override public void setOwner(Player player) {
        if (owner != null) return;
        owner = player.getUUID();
        getMainNode().setOwningPlayer(player);
        markDirty();
        connect();
    }

    @Override public boolean shouldOpenUI(Player player, InteractionHand hand, BlockHitResult hit) {
        return owner == null || owner.equals(player.getUUID()) || player.isCreative();
    }

    @Override public ModularUI createUI(Player player) {
        if (!isRemote()) setOwner(player);
        return Hk3NexusUi.create(this, player);
    }

    @Override public void saveCustomPersistedData(CompoundTag tag, boolean forDrop) {
        super.saveCustomPersistedData(tag, forDrop);
        var state = new CompoundTag();
        if (owner != null) state.putUUID("Owner", owner);
        if (plannerId != null) state.putUUID("PlannerId", plannerId);
        state.put("Network", network.save());
        crafting.write(state);
        management.write(state);
        if (forDrop) {
            state.remove("Patterns");
            state.getCompound("Network").remove("Cells");
        }
        tag.put("Hk3Nexus", state);
    }

    @Override public void loadCustomPersistedData(CompoundTag tag) {
        super.loadCustomPersistedData(tag);
        var state = tag.getCompound("Hk3Nexus");
        if (state.hasUUID("Owner")) owner = state.getUUID("Owner");
        if (state.hasUUID("PlannerId")) plannerId = state.getUUID("PlannerId");
        network.load(state.getCompound("Network"));
        crafting.read(state);
        management.read(state);
    }
}
