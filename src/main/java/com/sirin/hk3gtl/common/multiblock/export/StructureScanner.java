package com.sirin.hk3gtl.common.multiblock.export;


/**
 * 【文件职责】
 * - 维护 StructureScanner 的核心功能实现。
 * - 关键调用链：由上层系统入口调用 -> 本文件核心方法 -> 下游模块。
 *
 * 【变更记录】2026-05-19
 * - 删除：
 *   1) 初始归档备注：自 v0.3 基线梳理，无本次 diff。
 * - 新增：
 *   1) 新增统一变更备注块，便于后续维护与审计追踪。
 * - 修改：
 *   1) 未改动业务逻辑，仅补充文件级职责与维护注释模板。
 * - 用途：
 *   1) 帮助维护者快速理解文件职责、变更背景与风险点。
 *
 *
 * 【变更记录 #1】2026-10-31 17:44:08（第 1 次备注 · 修订 189）
 * - 删除：逐格 Placed 中间对象、允许前方空气进入矩阵的分支与可能强加载区块的世界读取。
 * - 新增：服务器线程限制，全选区体积、轴长、世界坐标、高度与已加载区块预检。
 * - 修改：由 ExportScanBounds 计算裁剪后的局部矩阵，只读取预检缓存的 LevelChunk；创造仓警告按注册名去重。
 * - 用途：确保同步导出有明确预算，前方空气不再触发负索引，任何未加载区块在读取控制器前即拒绝。
 * 【段内说明】
 * - 复杂方法补充“干什么 / 边界 / 线程侧”精简中文注释。
 */
import com.sirin.hk3gtl.common.constants.Hk3Constants;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.chunk.LevelChunk;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.Property;

import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;

/**
 * 选区扫描器：把世界空间下的 AABB 选区 + 控制器坐标转换为 {@link ExportContext}。
 *
 * <h3>流程概述</h3>
 * <ol>
 *   <li>确定控制器朝向：从显式指定位置读 BlockState 的 {@code facing} 属性</li>
 *   <li>遍历 AABB 内每个方块，坐标变换到控制器局部系（x 右 / y 上 / z 背后）</li>
 *   <li>裁掉控制器前方全部位置（包括空气，避免负索引）</li>
 *   <li>为每种方块 id 申请符号（经 {@link SymbolAllocator}）</li>
 *   <li>创造仓登记到 rejectedBlocks，不进入最终成型</li>
 * </ol>
 *
 * <h3>朝向约定</h3>
 * 生成的 grid 中 z=0 对应"控制器前脸"这一面，z 随深度递增延伸到塔体背后。
 * 该约定与项目现有 {@code Hk3AbsorptionTowerPatternImpl}（FRONT_Z = DEPTH-1）的
 * 表达方式等价（aisle 从背面 z=0 画到前脸 FRONT_Z），但在字符矩阵里更直观。
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>放宽/收紧控制器过滤：调整 {@link #resolveFacing}</li>
 *   <li>调整空气 / 前方裁剪逻辑：修改 {@link #scan} 内的跳过条件</li>
 *   <li>新增特殊方块分类（如"必须参与成型但不是舱口"）：在 allocate 前插入自定义处理</li>
 * </ul>
 */
public final class StructureScanner {

    private StructureScanner() {}

    /** 扫描失败时的抛出类型，消息会直接回显给玩家 */
    public static final class ScanException extends RuntimeException {
        public ScanException(String msg) { super(msg); }
    }

    /**
     * 执行扫描并返回完整的 {@link ExportContext}。
     *
     * @param level 世界
     * @param pos1 选区角点 A
     * @param pos2 选区角点 B
     * @param controllerPos 显式指定的控制器世界坐标（必须在选区内）
     * @param exportName 玩家指定的导出名（用于类名与文件名生成）
     */
    public static ExportContext scan(Level level, BlockPos pos1, BlockPos pos2,
                                     BlockPos controllerPos, String exportName) {
        if (!(level instanceof ServerLevel serverLevel) || !serverLevel.getServer().isSameThread()) {
            throw new ScanException("结构导出必须在服务器主线程执行");
        }
        ExportScanBounds bounds;
        try {
            bounds = ExportScanBounds.create(point(pos1), point(pos2), point(controllerPos),
                    level.getMinBuildHeight(), level.getMaxBuildHeight());
        } catch (IllegalArgumentException e) {
            throw new ScanException(e.getMessage());
        }
        int minChunkX = bounds.min.x() >> 4;
        int minChunkZ = bounds.min.z() >> 4;
        LevelChunk[][] chunks = new LevelChunk[(bounds.max.x() >> 4) - minChunkX + 1]
                [(bounds.max.z() >> 4) - minChunkZ + 1];
        // 先缓存全部已加载区块；后续读取不经过会隐式加载的 Level#getBlockState。
        for (int x = 0; x < chunks.length; x++) {
            for (int z = 0; z < chunks[x].length; z++) {
                chunks[x][z] = serverLevel.getChunkSource().getChunkNow(minChunkX + x, minChunkZ + z);
                if (chunks[x][z] == null) {
                    throw new ScanException("选区包含未加载区块：("
                            + (minChunkX + x) + "," + (minChunkZ + z) + ")，请先加载完整选区");
                }
            }
        }
        BlockState controllerState = chunks[(controllerPos.getX() >> 4) - minChunkX]
                [(controllerPos.getZ() >> 4) - minChunkZ].getBlockState(controllerPos);
        ResourceLocation controllerId = BuiltInRegistries.BLOCK.getKey(controllerState.getBlock());
        Direction facing = resolveFacing(controllerState);
        if (facing == null) {
            throw new ScanException("控制器方块没有可识别的水平朝向属性：" + controllerId);
        }
        return buildGrid(chunks, minChunkX, minChunkZ, bounds.frame(facing.getStepX(), facing.getStepZ()),
                controllerPos, controllerId, facing, exportName);
    }

    private static ExportContext buildGrid(LevelChunk[][] chunks, int minChunkX, int minChunkZ,
                                           ExportScanBounds.Frame frame, BlockPos ctrl,
                                           ResourceLocation ctrlId, Direction facing, String exportName) {
        char[][][] grid = new char[frame.depth()][frame.height()][frame.width()];
        SymbolAllocator allocator = new SymbolAllocator();
        List<String> warnings = new ArrayList<>();
        Set<ResourceLocation> rejected = new LinkedHashSet<>();
        BlockPos.MutableBlockPos pos = new BlockPos.MutableBlockPos();
        // 每格直接写入最终矩阵，不保留整份世界状态副本。
        for (int gy = 0; gy < frame.height(); gy++) {
            for (int gz = 0; gz < frame.depth(); gz++) {
                for (int gx = 0; gx < frame.width(); gx++) {
                    pos.set(frame.worldX(gx, gz), frame.worldY(gy), frame.worldZ(gx, gz));
                    BlockState state = chunks[(pos.getX() >> 4) - minChunkX]
                            [(pos.getZ() >> 4) - minChunkZ].getBlockState(pos);
                    if (pos.equals(ctrl)) {
                        grid[gz][gy][gx] = SymbolAllocator.CONTROLLER_SYMBOL;
                        continue;
                    }
                    if (state.isAir()) {
                        grid[gz][gy][gx] = SymbolAllocator.AIR_SYMBOL;
                        continue;
                    }
                    ResourceLocation id = BuiltInRegistries.BLOCK.getKey(state.getBlock());
                    HatchAbilityMap.Ability ability = HatchAbilityMap.lookup(id);
                    if (ability == HatchAbilityMap.CREATIVE_MARKER) {
                        if (rejected.add(id)) {
                            warnings.add("检测到创造模式舱口（严禁参与成型）：" + id);
                        }
                        grid[gz][gy][gx] = SymbolAllocator.AIR_SYMBOL;
                        continue;
                    }
                    try {
                        grid[gz][gy][gx] = allocator.allocate(id, ability);
                    } catch (IllegalStateException e) {
                        throw new ScanException("导出符号分配失败：" + e.getMessage());
                    }
                }
            }
        }
        if (!Hk3Constants.MOD_ID.equals(ctrlId.getNamespace())) {
            warnings.add("控制器并非 hk3gtl 命名空间：" + ctrlId
                    + "，请确认是否为外部多方块（导出仍可进行但需手动确认）");
        }
        return new ExportContext(exportName, frame.width(), frame.height(), frame.depth(), grid,
                allocator.legend(), allocator.abilityBySymbol(), ctrl, ctrlId, facing, warnings, rejected);
    }

    private static ExportScanBounds.Point point(BlockPos pos) {
        return new ExportScanBounds.Point(pos.getX(), pos.getY(), pos.getZ());
    }
    /**
     * 从 BlockState 中解析水平朝向。
     * 只认路径含 {@code facing} 的属性，且值为水平 Direction。
     */
    public static Direction resolveFacing(BlockState state) {
        for (Property<?> prop : state.getProperties()) {
            if (!prop.getName().contains("facing")) continue;
            Object v = state.getValue(prop);
            if (v instanceof Direction dir && dir.getAxis().isHorizontal()) {
                return dir;
            }
        }
        return null;
    }

}
