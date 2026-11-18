package com.sirin.hk3gtl.common.multiblock.pattern;

import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import it.unimi.dsi.fastutil.longs.LongOpenHashSet;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.Property;

/** W01搭建与预览共用布局和四向坐标，成型委托GTL原生匹配。 */
public final class Hk3W01HallPattern extends Hk3NativeWonderPattern {
    private static final class Data { static final Hk3W01HallLayout VALUE = Hk3W01HallLayout.load(); }
    public static Hk3W01HallLayout layout() { return Data.VALUE; }
    private final BlockState[][] states;

    public Hk3W01HallPattern(MultiblockMachineDefinition definition) {
        super("W01", definition);
        states = new BlockState[4][layout().palette().size()];
        for (int i = 0; i < states[0].length; i++) {
            BlockState base = state(layout().palette().get(i));
            for (int turn = 0; turn < 4; turn++) states[turn][i] = base.rotate(Rotation.values()[turn]);
        }
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
