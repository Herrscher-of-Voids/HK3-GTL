package com.sirin.hk3gtl.common.multiblock.build;

import net.minecraft.world.level.block.*;

import java.util.Objects;
import java.util.function.IntUnaryOperator;

/**
 * 【文件职责】为统一建造蓝图建立先支撑、后重力、最后附着的稳定高度索引，不展开空气。
 * 【变更记录 #1】2026-10-30（第1次备注 · 内测5修订184）
 * - 新增：分步计数、前缀和与填充；每格仅增加一个int索引，阶段内从低层到高层。
 * - 修改：无；用途：所有实体准备完成后共用放置顺序，避免原始记录顺序破坏附着及重力方块。
 * 【变更记录 #2】2026-10-30（第2次备注 · 内测5修订184）
 * - 新增：高度和阶段读取器入口；修改：排序与Minecraft注册表初始化分离，阶段必须位于0至2。
 * - 用途：直接回归生产算法，不为纯排序测试启动Forge网络或方块注册。
 */
final class Hk3BuildOrder {
    private final IntUnaryOperator yAt, phaseAt;
    private final int height, minY;
    private final IntUnaryOperator chunkAt;
    private final int chunkCount;
    private final int[] counts;
    private final int[] order;
    private int cursor, total;
    private Stage stage = Stage.COUNT;

    Hk3BuildOrder(Hk3BuildPlan plan) {
        this(plan.size(), checkedHeight(plan), plan.minOffset().getY(), plan::y,
                index -> phase(plan.state(index).getBlock()));
    }

    Hk3BuildOrder(Hk3BuildPlan plan, int chunkCount, IntUnaryOperator chunkAt) {
        this(plan.size(), checkedHeight(plan), plan.minOffset().getY(), plan::y,
                index -> phase(plan.state(index).getBlock()), chunkCount, chunkAt);
    }

    Hk3BuildOrder(int size, int height, int minY, IntUnaryOperator yAt, IntUnaryOperator phaseAt) {
        this(size,height,minY,yAt,phaseAt,1,i -> 0);
    }

    Hk3BuildOrder(int size, int height, int minY, IntUnaryOperator yAt, IntUnaryOperator phaseAt,
                  int chunkCount, IntUnaryOperator chunkAt) {
        if (size < 1 || height < 1)
            throw new IllegalArgumentException("建造排序的实体数量或高度范围无效");
        this.height = height;
        this.minY = minY;
        this.yAt = Objects.requireNonNull(yAt);
        this.phaseAt = Objects.requireNonNull(phaseAt);
        this.chunkAt = Objects.requireNonNull(chunkAt);
        this.chunkCount = chunkCount;
        if (chunkCount < 1) throw new IllegalArgumentException("区块桶数无效");
        counts = new int[Math.multiplyExact(Math.multiplyExact(height, 3),chunkCount)];
        order = new int[size];
    }

    private static int checkedHeight(Hk3BuildPlan plan) {
        int height = plan.height();
        if ((long) plan.maxOffset().getY() - plan.minOffset().getY() + 1L != height)
            throw new IllegalArgumentException("建造排序的蓝图高度与包围盒不一致");
        return height;
    }

    /** 调用前蓝图必须已准备完成；每步最多处理一格实体或一个高度桶。 */
    boolean step() {
        switch (stage) {
            case COUNT -> {
                counts[bucket(cursor++)]++;
                if (cursor == order.length) { cursor = 0; stage = Stage.PREFIX; }
            }
            case PREFIX -> {
                int count = counts[cursor];
                counts[cursor++] = total;
                total = Math.addExact(total, count);
                if (cursor == counts.length) {
                    if (total != order.length) throw new IllegalStateException("建造排序的计数与实体数量不一致");
                    cursor = 0; stage = Stage.FILL;
                }
            }
            case FILL -> {
                order[counts[bucket(cursor)]++] = cursor;
                if (++cursor == order.length) stage = Stage.DONE;
            }
            case DONE -> { }
        }
        return stage == Stage.DONE;
    }

    int index(int sortedIndex) {
        if (stage != Stage.DONE) throw new IllegalStateException("建造排序尚未完成");
        if (sortedIndex < 0 || sortedIndex >= order.length) throw new IndexOutOfBoundsException("建造排序索引越界");
        return order[sortedIndex];
    }

    /** 拆除先移走附着物与高处实体，最后移走承重主体；不遍历空气。 */
    int dismantleIndex(int cursor) {
        if (cursor < 0 || cursor >= order.length) throw new IndexOutOfBoundsException("拆除排序索引越界");
        return index(order.length-1-cursor);
    }

    /** 已完成索引按阶段和区块单调排列，二分跳过整段，不逐格寻找下个预加载区块。 */
    int nextChunkIndex(int sortedIndex) {
        int group=groupAt(index(sortedIndex)),low=sortedIndex+1,high=order.length;
        while(low<high) {
            int mid=(low+high)>>>1;
            if(groupAt(order[mid])==group)low=mid+1;else high=mid;
        }
        return low;
    }

    private int groupAt(int index) { return phaseAt.applyAsInt(index)*chunkCount+chunkAt.applyAsInt(index); }

    private int bucket(int index) {
        long y = (long) yAt.applyAsInt(index) - minY;
        if (y < 0 || y >= height) throw new IllegalStateException("建造实体高度超出蓝图范围");
        int phase = phaseAt.applyAsInt(index);
        if (phase < 0 || phase > 2) throw new IllegalStateException("建造实体阶段必须位于0至2");
        int chunk = chunkAt.applyAsInt(index);
        if (chunk < 0 || chunk >= chunkCount) throw new IllegalStateException("建造实体区块桶越界");
        return (phase * chunkCount + chunk) * height + (int) y;
    }

    private static int phase(Block block) { return block instanceof FallingBlock ? 1 : attached(block) ? 2 : 0; }

    private static boolean attached(Block block) {
        return block instanceof BushBlock || block instanceof SignBlock
                || block instanceof BaseCoralPlantTypeBlock || block instanceof AmethystClusterBlock
                || block instanceof TorchBlock || block instanceof LadderBlock
                || block instanceof FaceAttachedHorizontalDirectionalBlock || block instanceof BaseRailBlock
                || block instanceof CarpetBlock || block instanceof SnowLayerBlock
                || block instanceof LanternBlock || block instanceof BasePressurePlateBlock
                || block instanceof RedStoneWireBlock || block instanceof TripWireHookBlock
                || block instanceof TripWireBlock || block instanceof VineBlock
                || block instanceof MultifaceBlock || block instanceof GrowingPlantBlock
                || block instanceof PointedDripstoneBlock || block instanceof DoorBlock || block instanceof BedBlock;
    }

    private enum Stage { COUNT, PREFIX, FILL, DONE }
}
