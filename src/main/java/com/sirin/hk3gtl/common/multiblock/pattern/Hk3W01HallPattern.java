package com.sirin.hk3gtl.common.multiblock.pattern;

import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.api.pattern.*;
import com.gregtechceu.gtceu.api.pattern.error.PatternStringError;
import com.gregtechceu.gtceu.api.pattern.util.RelativeDirection;
import com.sirin.hk3gtl.mixin.gtceu.Hk3MultiblockStateAccess;
import com.sirin.hk3gtl.common.machine.Hk3W01HallMachine;
import com.sirin.hk3gtl.common.multiblock.build.Hk3UniversalTerminalBuilder;
import it.unimi.dsi.fastutil.longs.LongOpenHashSet;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.Property;

/** W01逐格真实成型：只约束原建筑实体，空气自由；无接口且不授予生产或毕业资格。 */
/**
 * 【变更记录 #1】2026-10-30 00:08:31（第1次备注 · 内测5修订183）
 * 删除：将源布局误作朝北的旋转口径；新增：西入口为零转的统一方向映射。
 * 修改：成型检查与终端搭建共用turnForFront，源坐标和全部真实状态保持原方向。
 * 用途：主控移至西入口后正面向外，四向搭建、材质旋转及完整检查一致，不改变成型标准。
 * 【变更记录 #2】2026-10-30 01:36:10（修订184）
 * - 删除：独立显示“当前创造模式验收”的提示；新增：W01终端请求交由统一分批建造器处理。
 * - 用途：W01仍保留自己的真实逐格Pattern成型检查与JEI完整预览。
 */
public final class Hk3W01HallPattern extends BlockPattern {
    private static final class Data { static final Hk3W01HallLayout VALUE = Hk3W01HallLayout.load(); }
    public static Hk3W01HallLayout layout() { return Data.VALUE; }
    private final BlockState[][] states;
    private final TraceabilityPredicate controller;

    public Hk3W01HallPattern(MultiblockMachineDefinition definition) {
        super(new TraceabilityPredicate[][][]{{{Predicates.controller(Predicates.blocks(definition.getBlock()))}}},
                new RelativeDirection[]{RelativeDirection.RIGHT, RelativeDirection.UP, RelativeDirection.BACK},
                new int[][]{{1, 1}}, new int[]{0, 0, 0, 0, 0});
        controller = Predicates.controller(Predicates.blocks(definition.getBlock()));
        states = new BlockState[4][layout().palette().size()];
        for (int i = 0; i < states[0].length; i++) {
            BlockState base = state(layout().palette().get(i));
            for (int turn = 0; turn < 4; turn++) states[turn][i] = base.rotate(Rotation.values()[turn]);
        }
    }

    @Override public boolean checkPatternAt(MultiblockState world, BlockPos center, Direction front,
            Direction up, boolean flipped, boolean savePredicate) {
        var access = (Hk3MultiblockStateAccess) (Object) world;
        access.hk3gtl$clean();
        if (world.getController() instanceof Hk3W01HallMachine hall && hall.isTerminalBuilding())
            return fail(world, "W01终极终端正在分批搭建，完成后重新逐格检查");
        if (!(world.getController() instanceof Hk3W01HallMachine hall) || !hall.verified())
            return fail(world,"请在主控内检查W01完整实体");
        if (front.getAxis().isVertical() || up != Direction.NORTH || flipped) return fail(world, "W01仅支持水平四向且不可镜像");
        int turn = turnForFront(front);
        var data = layout();
        BlockPos a = position(center, 0, 0, 0, turn).immutable();
        BlockPos b = position(center, data.width()-1, data.height()-1, data.depth()-1, turn).immutable();
        if (world.world.isOutsideBuildHeight(a) || world.world.isOutsideBuildHeight(b)) return fail(world, "W01建筑超出世界高度");
        var bounds = new Hk3LargeStructurePattern.Bounds(new BlockPos(Math.min(a.getX(), b.getX()), a.getY(), Math.min(a.getZ(), b.getZ())),
                new BlockPos(Math.max(a.getX(), b.getX()), b.getY(), Math.max(a.getZ(), b.getZ())));
        var pos = new BlockPos.MutableBlockPos();
        long chunk = Long.MIN_VALUE;
        if (!access.hk3gtl$update(center, controller) || !controller.test(world)) return false;
        world.addPosCache(center);
        // 所有实体由分批实读和精确写入回调维护，不强制常驻整座礼堂。
        // 区块映射和变更通知沿用巨构钩子，任何区域修改均触发GT失效及完整重检。
        world.setError(null);
        world.setNeededFlip(false);
        return true;
    }

    public static int turnForFront(Direction front) {
        return switch (front) {
            case WEST -> 0; case NORTH -> 1; case EAST -> 2; case SOUTH -> 3;
            default -> throw new IllegalArgumentException("W01主控必须水平放置");
        };
    }

    public static LongOpenHashSet requiredChunks(BlockPos center, int turn) {
        var result = new LongOpenHashSet();
        var pos = new BlockPos.MutableBlockPos();
        for (long cell : layout().cells()) {
            position(pos, center, Hk3W01HallLayout.x(cell), Hk3W01HallLayout.y(cell), Hk3W01HallLayout.z(cell), turn);
            result.add(ChunkPos.asLong(pos.getX() >> 4, pos.getZ() >> 4));
        }
        return result;
    }

    private static BlockPos.MutableBlockPos position(BlockPos center, int x, int y, int z, int turn) {
        var pos = new BlockPos.MutableBlockPos(); position(pos, center, x, y, z, turn); return pos;
    }
    public BlockState expectedState(long cell, int turn) { return states[turn][Hk3W01HallLayout.state(cell)]; }
    public static void position(BlockPos.MutableBlockPos pos, BlockPos center, int x, int y, int z, int turn) {
        var data = layout(); x -= data.controllerX(); y -= data.controllerY(); z -= data.controllerZ();
        int rx = switch (turn) { case 1 -> -z; case 2 -> -x; case 3 -> z; default -> x; };
        int rz = switch (turn) { case 1 -> x; case 2 -> -z; case 3 -> -x; default -> z; };
        pos.set(center.getX() + rx, center.getY() + y, center.getZ() + rz);
    }
    private static boolean fail(MultiblockState world, String text) { world.setError(new PatternStringError(text)); return false; }
    @Override public void autoBuild(Player player, MultiblockState state) {
        Hk3UniversalTerminalBuilder.use(player, state, null);
    }
    private static BlockState state(String text) {
        int at = text.indexOf('[');
        var block = Hk3StructureBlocks.require(at < 0 ? text : text.substring(0, at));
        BlockState result = block.defaultBlockState();
        if (at >= 0) for (String pair : text.substring(at+1, text.length()-1).split(",")) {
            String[] parts = pair.split("=", 2);
            var property = block.getStateDefinition().getProperty(parts[0]);
            if (parts.length != 2 || property == null) throw new IllegalStateException("W01状态属性错误：" + text);
            result = property(result, property, parts[1]);
        }
        return result;
    }
    private static <T extends Comparable<T>> BlockState property(BlockState state, Property<T> property, String value) {
        return state.setValue(property, property.getValue(value).orElseThrow(() -> new IllegalStateException("W01属性值错误：" + value)));
    }
}
