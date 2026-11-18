package com.sirin.hk3gtl.common.multiblock.build;

import net.minecraft.world.level.block.*;

import java.util.function.IntUnaryOperator;










final class Hk3BuildOrder {
    private final IntUnaryOperator yAt, phaseAt;
    private final int height, minY;
    private final IntUnaryOperator chunkAt;
    private final int chunkCount;
    private final int[] counts;
    private final int[] order;
    private final int size;
    private final Hk3RunBuildOrder runs;
    private int cursor, total;
    private Stage stage = Stage.COUNT;

    Hk3BuildOrder(Hk3BuildPlan plan) {
        this(plan,1,i->0);
    }

    Hk3BuildOrder(Hk3BuildPlan plan, int chunkCount, IntUnaryOperator chunkAt) {
        this(plan.size(), checkedHeight(plan), plan.minOffset().getY(), plan::y,
                index -> phase(plan.state(index).getBlock()), chunkCount, chunkAt,
                plan instanceof Hk3W11BuildPlan w11?w11:null);
    }

    Hk3BuildOrder(int size, int height, int minY, IntUnaryOperator yAt, IntUnaryOperator phaseAt) {
        this(size,height,minY,yAt,phaseAt,1,i -> 0);
    }

    Hk3BuildOrder(int size, int height, int minY, IntUnaryOperator yAt, IntUnaryOperator phaseAt,
                  int chunkCount, IntUnaryOperator chunkAt) {
        this(size,height,minY,yAt,phaseAt,chunkCount,chunkAt,null);
    }

    private Hk3BuildOrder(int size,int height,int minY,IntUnaryOperator yAt,IntUnaryOperator phaseAt,
                          int chunkCount,IntUnaryOperator chunkAt,Hk3W11BuildPlan plan) {
        if (size < 1 || height < 1)
            throw new IllegalArgumentException("建造排序的实体数量或高度范围无效");
        this.height = height;
        this.size = size;
        this.minY = minY;
        this.yAt = yAt;
        this.phaseAt = phaseAt;
        this.chunkAt = chunkAt;
        this.chunkCount = chunkCount;
        if (chunkCount < 1) throw new IllegalArgumentException("区块桶数无效");
        runs=plan==null?null:new Hk3RunBuildOrder(plan,height,minY,yAt,phaseAt,chunkCount,chunkAt);
        counts = runs==null?new int[Math.multiplyExact(Math.multiplyExact(height, 3),chunkCount)]:null;
        order = runs==null?new int[size]:null;
    }

    private static int checkedHeight(Hk3BuildPlan plan) {
        int height = plan.height();
        if ((long) plan.maxOffset().getY() - plan.minOffset().getY() + 1L != height)
            throw new IllegalArgumentException("建造排序的蓝图高度与包围盒不一致");
        return height;
    }

    /** 调用前蓝图必须已准备完成；每步最多处理一格实体或一个高度桶。 */
    boolean step() {
        if(runs!=null)return runs.step();
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
        if(runs!=null)return runs.index(sortedIndex);
        if (stage != Stage.DONE) throw new IllegalStateException("建造排序尚未完成");
        if (sortedIndex < 0 || sortedIndex >= order.length) throw new IndexOutOfBoundsException("建造排序索引越界");
        return order[sortedIndex];
    }

    /** 拆除先移走附着物与高处实体，最后移走承重主体；不遍历空气。 */
    int dismantleIndex(int cursor) {
        if (cursor < 0 || cursor >= size) throw new IndexOutOfBoundsException("拆除排序索引越界");
        return index(size-1-cursor);
    }

    /** 已完成索引按阶段和区块单调排列，二分跳过整段，不逐格寻找下个预加载区块。 */
    int nextChunkIndex(int sortedIndex) {
        if(runs!=null)return runs.nextChunkIndex(sortedIndex);
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
