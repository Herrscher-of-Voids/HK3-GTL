package com.sirin.hk3gtl.common.multiblock.build;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.level.block.state.BlockState;











public interface Hk3BuildPlan extends AutoCloseable {
    int size();
    int height();
    int x(int index);
    int y(int index);
    int z(int index);
    BlockState state(int index);
    CompoundTag tag(int index);
    /** 创建蓝图时已确定，不能在prepareStep期间改变。 */
    Direction sourceFacing();
    BlockPos minOffset();
    BlockPos maxOffset();

    /** 原稿装饰状态与实体数据仅供创造搭建，不走生存扣料或毕业判定。 */
    default boolean creativeOnly() { return false; }
    default boolean captureFarView() { return true; }
    default boolean contains(int x,int y,int z) { return false; }
    default int sourceDataVersion() { return net.minecraft.SharedConstants.getCurrentVersion().getDataVersion().getVersion(); }

    default boolean isMachinePartSlot(int x, int y, int z) {
        return (x != 0 || y != 0 || z != 0) && contains(x,y,z);
    }

    /** 每次最多读取一条稀疏记录；返回true后才能消费实体数据。 */
    default boolean prepareStep() { return true; }
    @Override default void close() {}
}
