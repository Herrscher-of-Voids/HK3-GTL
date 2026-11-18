package com.sirin.hk3gtl.common.integration.ae.nexus.network;

import appeng.api.features.GridLinkables;
import appeng.api.features.IPlayerRegistry;
import appeng.api.implementations.blockentities.IWirelessAccessPoint;
import appeng.api.implementations.blockentities.PatternContainerGroup;
import appeng.api.inventories.InternalInventory;
import appeng.api.networking.GridFlags;
import appeng.api.networking.GridHelper;
import appeng.api.networking.IGrid;
import appeng.api.networking.IGridConnection;
import appeng.api.networking.IGridNode;
import appeng.api.networking.IGridNodeListener;
import appeng.api.networking.IInWorldGridNodeHost;
import appeng.api.networking.IManagedGridNode;
import appeng.api.networking.crafting.ICraftingProvider;
import appeng.api.networking.security.IActionHost;
import appeng.api.networking.security.IActionSource;
import appeng.api.parts.IPart;
import appeng.api.parts.IPartHost;
import appeng.api.stacks.AEKey;
import appeng.api.stacks.AEItemKey;
import appeng.api.storage.IStorageMounts;
import appeng.api.storage.IStorageProvider;
import appeng.api.storage.MEStorage;
import appeng.api.util.DimensionalBlockPos;
import appeng.parts.networking.CablePart;
import appeng.helpers.patternprovider.PatternContainer;
import appeng.util.Platform;
import com.gregtechceu.gtceu.api.machine.IMachineBlockEntity;
import com.lowdragmc.lowdraglib.side.item.IItemTransfer;
import com.sirin.hk3gtl.common.machine.ae.Hk3NexusMachine;
import com.sirin.hk3gtl.common.machine.ae.Hk3NexusMachines;
import com.sirin.hk3gtl.mixin.ae.Hk3NexusChunkMapAccess;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.GlobalPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ChunkHolder;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.entity.BlockEntity;

import java.math.BigInteger;
import java.util.ArrayList;
import java.util.EnumSet;
import java.util.IdentityHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.function.IntSupplier;

public final class Hk3NexusGrid implements IInWorldGridNodeHost, IActionHost, IStorageProvider, IWirelessAccessPoint, PatternContainer {
    private static final Map<MinecraftServer, Set<Hk3NexusGrid>> LOADED = new IdentityHashMap<>();
    private final Runnable changed;
    private IManagedGridNode node;
    private CompoundTag nodeData = new CompoundTag();
    private final Hk3NexusCells cells;
    private InternalInventory patterns;
    private final Map<IGridNode, IGridConnection> wireless = new IdentityHashMap<>();
    private final Set<IGridNode> seen = java.util.Collections.newSetFromMap(new IdentityHashMap<>());
    private final List<ChunkHolder> scanChunks = new ArrayList<>();
    private IGridConnection bridge;
    private ServerLevel level;
    private BlockPos pos;
    private UUID owner;
    private int scanIndex;

    public Hk3NexusGrid(Runnable changed) {
        this.changed = changed;
        this.cells = new Hk3NexusCells(changed, this::remount);
        this.node = createNode();
    }

    private IManagedGridNode createNode() {
        return GridHelper.createManagedNode(this, new IGridNodeListener<Hk3NexusGrid>() {
            @Override public void onSaveChanges(Hk3NexusGrid owner, IGridNode gridNode) { changed.run(); }
            @Override public void onGridChanged(Hk3NexusGrid owner, IGridNode gridNode) {
                gridNode.getGrid().getPathingService().repath();
            }
        }).setInWorldNode(true).setFlags(GridFlags.DENSE_CAPACITY)
                .setExposedOnSides(EnumSet.allOf(Direction.class)).setIdlePowerUsage(0).setTagName("NexusNode")
                .addService(IStorageProvider.class, this);
    }

    public void attach(ServerLevel level, BlockPos pos, UUID owner) {
        this.level = level;
        this.pos = pos.immutable();
        this.owner = owner;
        node.setOwningPlayerId(IPlayerRegistry.getMapping(level).getPlayerId(owner));
        node.create(level, pos);
        LOADED.computeIfAbsent(level.getServer(), ignored -> new LinkedHashSet<>()).add(this);
        rebuildBridges(level.getServer());
        node.getGrid().getPathingService().repath();
    }

    public void detach() {
        if (level == null) return;
        var server = level.getServer();
        LOADED.get(server).remove(this);
        if (bridge != null && node.getNode().getConnections().contains(bridge)) bridge.destroy();
        bridge = null;
        wireless.clear();
        seen.clear();
        scanChunks.clear();
        var crafting = node.getNode().getService(ICraftingProvider.class);
        nodeData = new CompoundTag();
        node.saveToNBT(nodeData);
        node.destroy();
        // AE的受管节点销毁后不能再次create，重新成型时换新节点并保留服务。
        node = createNode();
        node.addService(ICraftingProvider.class, crafting);
        node.loadFromNBT(nodeData);
        if (LOADED.get(server).isEmpty()) LOADED.remove(server);
        else rebuildBridges(server);
        level = null;
        scanIndex = 0;
    }

    public void tick() {
        if (!node.isReady()) return;
        if (scanIndex == 0) {
            for (var dimension : level.getServer().getAllLevels()) {
                for (var holder : ((Hk3NexusChunkMapAccess) dimension.getChunkSource().chunkMap).hk3gtl$loadedChunks())
                    scanChunks.add(holder);
            }
        }
        // 跨维扫描分摊到每tick四个区块，不加载远端区块。
        for (int step = 0; step < 4 && scanIndex < scanChunks.size(); step++) {
            var chunk = scanChunks.get(scanIndex++).getFullChunk();
            if (chunk != null) for (var entity : chunk.getBlockEntities().values()) discover(entity);
        }
        if (scanIndex < scanChunks.size()) return;
        scanIndex = 0;
        scanChunks.clear();
        var iterator = wireless.entrySet().iterator();
        while (iterator.hasNext()) {
            var link = iterator.next();
            if (seen.contains(link.getKey())) continue;
            if (link.getKey().getConnections().contains(link.getValue())) link.getValue().destroy();
            iterator.remove();
        }
        seen.clear();
        rebuildBridges(level.getServer());
    }

    private void discover(BlockEntity entity) {
        if (entity.isRemoved()) return;
        if (entity instanceof IPartHost parts) {
            discover(parts.getPart(null));
            for (var direction : Direction.values()) discover(parts.getPart(direction));
            return;
        }
        var host = GridHelper.getNodeHost(entity.getLevel(), entity.getBlockPos());
        if (host != null) {
            connect(host.getGridNode(null));
            for (var direction : Direction.values()) connect(host.getGridNode(direction));
        }
    }

    private void discover(IPart part) {
        if (part != null && !(part instanceof CablePart)) connect(part.getGridNode());
    }

    private void connect(IGridNode target) {
        if (target == null || target == node.getNode()) return;
        if (target.getOwningPlayerId() >= 0 && target.getOwningPlayerId() != node.getNode().getOwningPlayerId()) return;
        for (var nexus : target.getGrid().getMachines(Hk3NexusGrid.class))
            if (!owner.equals(nexus.owner)) return;
        if (!seen.add(target)) return;
        var connections = target.getConnections();
        var existing = wireless.get(target);
        if (existing != null && connections.contains(existing)) return;
        for (var connection : connections) {
            if (connection.getOtherSide(target) != node.getNode()) continue;
            wireless.remove(target);
            return;
        }
        wireless.put(target, GridHelper.createConnection(node.getNode(), target));
    }

    private static void rebuildBridges(MinecraftServer server) {
        var leaders = new java.util.HashMap<UUID, Hk3NexusGrid>();
        for (var nexus : LOADED.get(server)) {
            var leader = leaders.putIfAbsent(nexus.owner, nexus);
            if (nexus.bridge != null && !nexus.node.getNode().getConnections().contains(nexus.bridge)) nexus.bridge = null;
            if (nexus.bridge != null && (leader == null || nexus.bridge.getOtherSide(nexus.node.getNode()) != leader.node.getNode())) {
                nexus.bridge.destroy();
                nexus.bridge = null;
            }
            if (leader != null && nexus.bridge == null && leader.getGrid() != nexus.getGrid())
                nexus.bridge = GridHelper.createConnection(leader.node.getNode(), nexus.node.getNode());
        }
    }

    private void remount() {
        if (node.isReady()) IStorageProvider.requestUpdate(node);
    }

    public IManagedGridNode getMainNode() { return node; }
    public void setPatternInventory(InternalInventory patterns) { this.patterns = patterns; }
    @Override public InternalInventory getTerminalPatternInventory() { return patterns; }
    @Override public long getTerminalSortOrder() { return pos.asLong(); }
    @Override public PatternContainerGroup getTerminalGroup() {
        // 槽数变化让AE重建终端缓存，接收新增的样板槽。
        return new PatternContainerGroup(AEItemKey.of(Hk3NexusMachines.NEXUS.asStack()),
                Component.translatable("block.hk3gtl.ae_nexus"),
                List.of(Component.translatable("hk3gtl.nexus.pattern_slots", patterns.size())));
    }
    @Override public IGridNode getGridNode(Direction direction) { return node.getNode(); }
    @Override public IGridNode getActionableNode() { return node.getNode(); }
    @Override public IGrid getGrid() { return node.getGrid(); }
    @Override public boolean isActive() { return node.isActive(); }
    @Override public DimensionalBlockPos getLocation() { return new DimensionalBlockPos(level, pos); }
    @Override public double getRange() { return Double.MAX_VALUE; }
    @Override public void mountInventories(IStorageMounts mounts) { cells.mount(mounts); }
    public int wirelessConnections() { return wireless.size(); }
    public int cellCount() { return cells.count(); }
    public int slotCount() { return cells.slots(); }
    public ItemStack cell(int slot) { return cells.get(slot); }
    public void setCell(int slot, ItemStack stack) { cells.set(slot, stack); }
    public ItemStack insertCell(ItemStack stack) { return cells.insert(stack); }
    public ItemStack removeCell(int slot) { return cells.remove(slot); }
    public IItemTransfer pager(int page, int size) { return cells.pager(() -> page, size); }
    public IItemTransfer pager(IntSupplier page, int size) { return cells.pager(page, size); }
    public BigInteger stored(AEKey key) { return cells.stored(key); }
    public boolean isInfiniteSource(AEKey key) {
        var source = IActionSource.ofMachine(this);
        for (var nexus : getGrid().getMachines(Hk3NexusGrid.class))
            if (nexus.cells.infinite(key, source)) return true;
        return false;
    }

    public boolean bind(ItemStack stack) {
        var handler = GridLinkables.get(stack.getItem());
        if (handler == null || !handler.canLink(stack)) return false;
        handler.link(stack, GlobalPos.of(level.dimension(), pos));
        changed.run();
        return true;
    }

    public CompoundTag save() {
        var tag = cells.save();
        if (node.isReady()) {
            nodeData = new CompoundTag();
            node.saveToNBT(nodeData);
        }
        tag.merge(nodeData);
        return tag;
    }

    public void load(CompoundTag tag) {
        cells.load(tag);
        nodeData = new CompoundTag();
        nodeData.put("NexusNode", tag.getCompound("NexusNode").copy());
        node.loadFromNBT(nodeData);
    }

    public static boolean contains(IGrid grid) {
        return !grid.getMachines(Hk3NexusGrid.class).isEmpty();
    }

    public static List<InternalInventory> patternInventories(IGrid grid) {
        return grid.getActiveMachines(Hk3NexusGrid.class).stream()
                .map(Hk3NexusGrid::getTerminalPatternInventory).toList();
    }

    public static boolean contains(MEStorage storage) {
        for (var loaded : LOADED.values()) for (var nexus : loaded)
            if (nexus.getGrid().getStorageService().getInventory() == storage) return true;
        return false;
    }

    public static Hk3NexusGrid at(MinecraftServer server, GlobalPos position) {
        var level = server.getLevel(position.dimension());
        if (level == null) return null;
        var entity = Platform.getTickingBlockEntity(level, position.pos());
        if (!(entity instanceof IMachineBlockEntity holder)
                || !(holder.getMetaMachine() instanceof Hk3NexusMachine machine)) return null;
        var nexus = machine.network();
        return nexus.node.isReady() ? nexus : null;
    }
}
