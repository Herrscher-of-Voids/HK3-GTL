package com.sirin.hk3gtl.client.preview;

import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.lowdragmc.lowdraglib.utils.BlockInfo;
import com.lowdragmc.lowdraglib.utils.TrackedDummyWorld;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3W01HallLayout;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3W01PreviewIndex;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.level.BlockAndTintGetter;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import com.gregtechceu.gtceu.api.data.RotationState;
import net.minecraft.world.level.material.FluidState;

import java.util.AbstractSet;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.NoSuchElementException;

 








public final class Hk3W01PreviewWorld extends TrackedDummyWorld {
    final Hk3W01HallLayout layout;
    final Hk3W01PreviewIndex index;
    final BlockState[] states;
    final int layer;
    final Direction front;
    final Map<Long, CompoundTag> entities;
    private final BlockPos controller;
    private final BlockState controllerState;
    private final Map<BlockPos, BlockEntity> previewEntities = new HashMap<>();

    Hk3W01PreviewWorld(MultiblockMachineDefinition definition, Hk3W01HallLayout layout,
            Hk3W01PreviewIndex index, BlockState[] states, int layer) {
        this(definition, layout, index, states, layer, Direction.WEST, Map.of());
    }

    Hk3W01PreviewWorld(MultiblockMachineDefinition definition, Hk3W01HallLayout layout,
            Hk3W01PreviewIndex index, BlockState[] states, int layer, Direction front, Map<Long, CompoundTag> entities) {
        this.layout = layout;
        this.index = index;
        this.states = states;
        this.layer = layer;
        this.front = front;
        this.entities = entities;
        controller = new BlockPos(layout.controllerX(), layout.controllerY(), layout.controllerZ());
        controllerState = definition.getBlock().defaultBlockState().setValue(RotationState.NON_Y_AXIS.property, front);
        long controllerCell = Hk3W01HallLayout.pack(controller.getX(), controller.getY(), controller.getZ(), 0);
        if (layer < 0 || layer == controller.getY()) createPreviewEntity(controllerCell, controllerState);
        for (long cell : index.blockEntityCells()) {
            int y = Hk3W01HallLayout.y(cell);
            if (layer >= 0 && layer != y) continue;
            if ((cell >>> 16) == (controllerCell >>> 16)) continue;
            createPreviewEntity(cell, states[Hk3W01HallLayout.state(cell)]);
        }
    }

    private void createPreviewEntity(long cell, BlockState state) {
        var pos = new BlockPos(Hk3W01HallLayout.x(cell), Hk3W01HallLayout.y(cell), Hk3W01HallLayout.z(cell));
        BlockInfo info = BlockInfo.fromBlockState(state);
        CompoundTag tag = entities.get(cell >>> 16);
        if (tag != null) info.setTag(tag.copy());
        BlockEntity entity = info.getBlockEntity(pos);
        if (entity != null) { entity.setLevel(this); previewEntities.put(pos, entity); }
    }

    @Override public BlockState getBlockState(BlockPos pos) {
        if (layer >= 0 && pos.getY() != layer) return Blocks.AIR.defaultBlockState();
        if (pos.equals(controller)) return controllerState;
        int state = index.stateAt(pos.getX(), pos.getY(), pos.getZ());
        return state < 0 ? Blocks.AIR.defaultBlockState() : states[state];
    }

    @Override public BlockEntity getBlockEntity(BlockPos pos) { return previewEntities.get(pos); }
    @Override public FluidState getFluidState(BlockPos pos) { return getBlockState(pos).getFluidState(); }
    @Override public void tickWorld() { /* 预览不执行实际世界的珊瑚死亡、重力和生产逻辑。 */ }

    public static boolean isW01Preview(BlockAndTintGetter world) {
        return world instanceof Hk3W01PreviewWorld || world instanceof TrackedDummyWorld tracked
                && tracked.proxyWorld.get() instanceof Hk3W01PreviewWorld;
    }

    AbstractSet<BlockPos> positions() {
        return positions(index.renderCells());
    }

    AbstractSet<BlockPos> positions(int[] rendered) {
        long[] cells = layout.cells();
        int size = layer < 0 ? rendered.length : cells.length;
        return new AbstractSet<>() {
            @Override public int size() { return layer < 0 ? rendered.length : index.countLayer(layer); }
            @Override public boolean contains(Object value) {
                return value instanceof BlockPos pos && (layer < 0 || layer == pos.getY())
                        && index.stateAt(pos.getX(), pos.getY(), pos.getZ()) >= 0;
            }
            @Override public Iterator<BlockPos> iterator() {
                return new Iterator<>() {
                    int next = advance(0);
                    private int advance(int from) {
                        while (from < size && layer >= 0 && Hk3W01HallLayout.y(cells[from]) != layer) from++;
                        return from;
                    }
                    @Override public boolean hasNext() { return next < size && !Thread.currentThread().isInterrupted(); }
                    @Override public BlockPos next() {
                        if (!hasNext()) throw new NoSuchElementException();
                        long cell = cells[layer < 0 ? rendered[next] : next];
                        next = advance(next + 1);
                        return new BlockPos(Hk3W01HallLayout.x(cell), Hk3W01HallLayout.y(cell), Hk3W01HallLayout.z(cell));
                    }
                };
            }
        };
    }
}
