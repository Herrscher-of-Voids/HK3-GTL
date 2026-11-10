package com.sirin.hk3gtl.common.multiblock.build;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.level.block.state.BlockState;

/**
 * 【文件职责】统一终端建造器的只读实体蓝图；坐标相对源主控，不展开空气，不保存世界引用。
 * 【变更记录 #1】2026-10-30 01:13:48（第1次备注 · 内测5修订184）
 * - 删除：无；新增：W01、批准建筑与小型GT模式共用的坐标、状态、实体数据和分步准备契约。
 * - 修改：建造引擎通过本契约消费建筑，不依赖W01的10位坐标编码。
 * - 用途：保持真实完整实体与源朝向；准备失败须关闭输入流，最终成型仍由原Pattern决定。
 * 【变更记录 #2】2026-10-30 02:11:33（第2次备注 · 内测5修订184）
 * - 修改：源朝向在蓝图返回时即固定；无仓搭建的批准接口使用合法填充壳，不携带原仓室数据。
 * - 用途：建造任务可在准备实体前校验四向边界，既有真实仓室继续由建造引擎保留。
 */
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

    default boolean isMachinePartSlot(int x, int y, int z) { return false; }

    default com.gregtechceu.gtceu.api.pattern.TraceabilityPredicate dismantlePort(int index) { return null; }
    default Direction portFacing(int index) { return null; }

    /** 每次最多读取一条稀疏记录；返回true后才能消费实体数据。 */
    default boolean prepareStep() { return true; }
    @Override default void close() {}
}
