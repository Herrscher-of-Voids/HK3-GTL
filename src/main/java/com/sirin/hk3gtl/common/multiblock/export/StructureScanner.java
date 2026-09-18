package com.sirin.hk3gtl.common.multiblock.export;



import com.sirin.hk3gtl.common.constants.Hk3Constants;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.AirBlock;
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
 *   <li>裁掉控制器前方的非空气方块（它们不属于结构一部分）</li>
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
        BlockPos min = new BlockPos(
                Math.min(pos1.getX(), pos2.getX()),
                Math.min(pos1.getY(), pos2.getY()),
                Math.min(pos1.getZ(), pos2.getZ()));
        BlockPos max = new BlockPos(
                Math.max(pos1.getX(), pos2.getX()),
                Math.max(pos1.getY(), pos2.getY()),
                Math.max(pos1.getZ(), pos2.getZ()));

        if (!contains(min, max, controllerPos)) {
            throw new ScanException("控制器坐标不在选区范围内：controller="
                    + controllerPos.toShortString() + "，selection=" + min.toShortString()
                    + "..." + max.toShortString());
        }

        BlockState controllerState = level.getBlockState(controllerPos);
        ResourceLocation controllerId = BuiltInRegistries.BLOCK.getKey(controllerState.getBlock());
        Direction facing = resolveFacing(controllerState);
        if (facing == null) {
            throw new ScanException("控制器方块没有可识别的水平朝向属性：" + controllerId);
        }

        return buildGrid(level, min, max, controllerPos, controllerId, facing, exportName);
    }

    private static ExportContext buildGrid(Level level, BlockPos min, BlockPos max,
                                           BlockPos ctrl, ResourceLocation ctrlId,
                                           Direction facing, String exportName) {
        Direction back = facing.getOpposite();
        Direction right = facing.getClockWise();

        List<Placed> placed = new ArrayList<>();
        int minX = Integer.MAX_VALUE, maxX = Integer.MIN_VALUE;
        int minY = Integer.MAX_VALUE, maxY = Integer.MIN_VALUE;
        int maxZ = 0;

        for (int wy = min.getY(); wy <= max.getY(); wy++) {
            for (int wz = min.getZ(); wz <= max.getZ(); wz++) {
                for (int wx = min.getX(); wx <= max.getX(); wx++) {
                    BlockPos pos = new BlockPos(wx, wy, wz);
                    BlockState state = level.getBlockState(pos);
                    boolean isAir = state.getBlock() instanceof AirBlock;

                    int relX = wx - ctrl.getX();
                    int relY = wy - ctrl.getY();
                    int relZ = wz - ctrl.getZ();

                    // 右手方向为 +X，朝控制器背后为 +Z，z=0 即控制器所在平面
                    int localX = relX * right.getStepX() + relZ * right.getStepZ();
                    int localZ = relX * back.getStepX() + relZ * back.getStepZ();

                    if (!isAir && localZ < 0) continue; // 控制器前方的装饰不计入

                    minX = Math.min(minX, localX);
                    maxX = Math.max(maxX, localX);
                    minY = Math.min(minY, relY);
                    maxY = Math.max(maxY, relY);
                    maxZ = Math.max(maxZ, localZ);

                    placed.add(new Placed(localX, relY, localZ, state, pos.equals(ctrl)));
                }
            }
        }

        int width = maxX - minX + 1;
        int height = maxY - minY + 1;
        int depth = maxZ + 1;

        char[][][] grid = new char[depth][height][width];
        for (int z = 0; z < depth; z++) {
            for (int y = 0; y < height; y++) {
                java.util.Arrays.fill(grid[z][y], SymbolAllocator.AIR_SYMBOL);
            }
        }

        SymbolAllocator allocator = new SymbolAllocator();
        List<String> warnings = new ArrayList<>();
        Set<ResourceLocation> rejected = new LinkedHashSet<>();

        // 项目约定（与 Hk3AbsorptionTowerPatternImpl 一致）：
        //   grid[0]        = 塔体最后排（背面），对应 FactoryBlockPattern 第一个 aisle
        //   grid[depth-1]  = 控制器所在前脸，对应最后一个 aisle
        // 该顺序匹配 GTCEu aisleDir 的默认切片方向，生成的 Pattern 可直接套用。
        for (Placed p : placed) {
            int gx = p.localX - minX;
            int gy = p.localY - minY;
            int gz = p.localZ;

            if (p.isController) {
                grid[gz][gy][gx] = SymbolAllocator.CONTROLLER_SYMBOL;
                continue;
            }
            if (p.state.getBlock() instanceof AirBlock) {
                grid[gz][gy][gx] = SymbolAllocator.AIR_SYMBOL;
                continue;
            }

            ResourceLocation id = BuiltInRegistries.BLOCK.getKey(p.state.getBlock());
            HatchAbilityMap.Ability ability = HatchAbilityMap.lookup(id);

            if (ability == HatchAbilityMap.CREATIVE_MARKER) {
                rejected.add(id);
                warnings.add("检测到创造模式舱口（严禁参与成型）：" + id + " @ 局部("
                        + p.localX + "," + p.localY + "," + p.localZ + ")");
                grid[gz][gy][gx] = SymbolAllocator.AIR_SYMBOL;
                continue;
            }

            char symbol = allocator.allocate(id, ability);
            grid[gz][gy][gx] = symbol;
        }

        if (!Hk3Constants.MOD_ID.equals(ctrlId.getNamespace())) {
            warnings.add("控制器并非 hk3gtl 命名空间：" + ctrlId
                    + "，请确认是否为外部多方块（导出仍可进行但需手动确认）");
        }

        return new ExportContext(
                exportName, width, height, depth, grid,
                allocator.legend(), allocator.abilityBySymbol(),
                ctrl, ctrlId, facing,
                warnings, rejected);
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

    private static boolean contains(BlockPos min, BlockPos max, BlockPos p) {
        return p.getX() >= min.getX() && p.getX() <= max.getX()
                && p.getY() >= min.getY() && p.getY() <= max.getY()
                && p.getZ() >= min.getZ() && p.getZ() <= max.getZ();
    }

    /** 扫描中间产物：局部坐标 + BlockState + 是否为控制器 */
    private record Placed(int localX, int localY, int localZ, BlockState state, boolean isController) {}
}
