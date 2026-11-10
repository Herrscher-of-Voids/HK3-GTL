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

/**
 * 【文件职责】W01只读预览世界，按原坐标读取全部实体和状态，不创建区块、物理tick或百万BlockInfo。
 * 【变更记录 #1】2026-10-29 23:12:35（第1次备注 · 本轮高度与预览修复）
 * 删除：无；新增：原布局的稀疏世界及惰性坐标集合；修改：主控预览替换原钻石占位。
 * 用途：让原生JEI场景使用真实MC模型；切层只控制可见层，不改蓝图、数量或游戏世界。
 * 【变更记录 #2】2026-10-30 00:08:31（第2次备注 · 内测5修订183）
 * 删除：预览主控固定朝北；新增：无；修改：新入口主控正面朝西，与原坐标零转布局一致。
 * 用途：JEI继续显示完整修订建筑及实际GT主控，不把侧面误作可操作入口。
 */
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
        // 只有实际带BE的少量方块需要实例；普通石材不生成方块实体。
        for (long cell : layout.cells()) {
            int y = Hk3W01HallLayout.y(cell);
            if (layer >= 0 && layer != y) continue;
            BlockState state = states[Hk3W01HallLayout.state(cell)];
            if (!state.hasBlockEntity() && !(Hk3W01HallLayout.x(cell) == controller.getX()
                    && y == controller.getY() && Hk3W01HallLayout.z(cell) == controller.getZ())) continue;
            var pos = new BlockPos(Hk3W01HallLayout.x(cell), y, Hk3W01HallLayout.z(cell));
            if (pos.equals(controller)) state = controllerState;
            if (state.hasBlockEntity()) {
                BlockInfo info = BlockInfo.fromBlockState(state);
                CompoundTag tag = entities.get(cell >>> 16);
                if (tag != null) info.setTag(tag.copy());
                BlockEntity entity = info.getBlockEntity(pos);
                if (entity != null) { entity.setLevel(this); previewEntities.put(pos, entity); }
            }
        }
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
        return new AbstractSet<>() {
            @Override public int size() { return index.countLayer(layer); }
            @Override public boolean contains(Object value) {
                return value instanceof BlockPos pos && (layer < 0 || layer == pos.getY())
                        && index.stateAt(pos.getX(), pos.getY(), pos.getZ()) >= 0;
            }
            @Override public Iterator<BlockPos> iterator() {
                return new Iterator<>() {
                    int next = advance(0);
                    private int advance(int from) {
                        while (from < layout.cells().length && layer >= 0 && Hk3W01HallLayout.y(layout.cells()[from]) != layer) from++;
                        return from;
                    }
                    @Override public boolean hasNext() { return next < layout.cells().length && !Thread.currentThread().isInterrupted(); }
                    @Override public BlockPos next() {
                        if (!hasNext()) throw new NoSuchElementException();
                        long cell = layout.cells()[next];
                        next = advance(next + 1);
                        return new BlockPos(Hk3W01HallLayout.x(cell), Hk3W01HallLayout.y(cell), Hk3W01HallLayout.z(cell));
                    }
                };
            }
        };
    }
}
