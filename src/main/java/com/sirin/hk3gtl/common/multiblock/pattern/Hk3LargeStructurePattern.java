package com.sirin.hk3gtl.common.multiblock.pattern;

import com.gregtechceu.gtceu.api.block.ActiveBlock;
import com.gregtechceu.gtceu.api.machine.IMachineBlockEntity;
import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.api.machine.feature.multiblock.IMultiPart;
import com.gregtechceu.gtceu.api.pattern.*;
import com.gregtechceu.gtceu.api.pattern.error.PatternStringError;
import com.gregtechceu.gtceu.api.pattern.predicates.SimplePredicate;
import com.gregtechceu.gtceu.api.pattern.util.RelativeDirection;
import com.lowdragmc.lowdraglib.utils.BlockInfo;
import com.sirin.hk3gtl.mixin.gtceu.Hk3MultiblockStateAccess;
import it.unimi.dsi.fastutil.longs.Long2ObjectOpenHashMap;
import it.unimi.dsi.fastutil.longs.LongOpenHashSet;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.Property;
import java.util.*;



















public final class Hk3LargeStructurePattern extends BlockPattern {
    public static final String BOUNDS_KEY = "hk3gtlLargeBounds";
    private final MultiblockMachineDefinition definition;
    private final String architectureId;
    private final int[] size, controller;
    private final long[] cells;
    private final BlockState[][] states, activeStates;
    private final TraceabilityPredicate control, universal;
    private final Set<SimplePredicate> limits = Collections.newSetFromMap(new IdentityHashMap<>());

    public record Bounds(BlockPos min, BlockPos max) {
        public boolean contains(BlockPos pos) {
            return pos.getX() >= min.getX() && pos.getX() <= max.getX()
                    && pos.getY() >= min.getY() && pos.getY() <= max.getY()
                    && pos.getZ() >= min.getZ() && pos.getZ() <= max.getZ();
        }
        public List<BlockPos> chunkRepresentatives() {
            List<BlockPos> result = new ArrayList<>();
            for (int x = min.getX() >> 4; x <= max.getX() >> 4; x++)
                for (int z = min.getZ() >> 4; z <= max.getZ() >> 4; z++)
                    result.add(new BlockPos(x << 4, min.getY(), z << 4));
            return result;
        }
    }

    public Hk3LargeStructurePattern(MultiblockMachineDefinition definition, Hk3ApprovedArchitecture.Layout data,
                                   TraceabilityPredicate universal) {
        super(new TraceabilityPredicate[][][]{{{Predicates.controller(Predicates.blocks(definition.getBlock()))}}},
                new RelativeDirection[]{RelativeDirection.RIGHT, RelativeDirection.UP, RelativeDirection.BACK},
                new int[][]{{1, 1}}, new int[]{0, 0, 0, 0, 0});
        this.definition = definition;
        this.universal = universal;
        architectureId = data.key();
        size = data.size(); controller = data.controller();
        Math.multiplyExact(Math.multiplyExact(size[0], size[1]), size[2]);
        control = Predicates.controller(Predicates.blocks(definition.getBlock()));
        Map<String, Integer> palette = new LinkedHashMap<>();
        cells = new long[data.blocks().size()];
        int i = 0;
        for (var cell : data.blocks()) {
            int state = palette.computeIfAbsent(cell.state(), ignored -> palette.size());
            if (state > 65535) throw new IllegalStateException("巨构材料数量越界：" + data.key());
            cells[i++] = ((long) linear(cell.pos()) << 16) | state;
        }
        Arrays.sort(cells);
        states = new BlockState[4][palette.size()];
        activeStates = new BlockState[4][palette.size()];
        for (var entry : palette.entrySet()) {
            BlockState state = state(entry.getKey());
            for (int turn = 0; turn < 4; turn++) {
                BlockState rotated = state.rotate(rotation(turn));
                states[turn][entry.getValue()] = rotated;
                activeStates[turn][entry.getValue()] = rotated.getBlock() instanceof ActiveBlock active
                        ? active.changeActive(rotated, !active.isActive(rotated)) : rotated;
            }
        }
        limits.addAll(universal.limited);
    }

    @Override public BlockInfo[][][] getPreview(int[] repetitions) {
        return Hk3LargeArchitectureShapes.create(definition, architectureId).getBlocks();
    }

    @Override public boolean checkPatternAt(MultiblockState world, BlockPos center, Direction front,
                                           Direction up, boolean flipped, boolean savePredicate) {
        var access = (Hk3MultiblockStateAccess) (Object) world;
        access.hk3gtl$clean();
        if (front.getAxis().isVertical() || up != Direction.NORTH || flipped)
            return fail(world, "该巨构仅支持水平四向且不可镜像");
        int turn = switch (front) { case NORTH -> 0; case EAST -> 1; case SOUTH -> 2; default -> 3; };
        Bounds bounds = bounds(center, turn);
        if (world.world.isOutsideBuildHeight(bounds.min()) || world.world.isOutsideBuildHeight(bounds.max()))
            return fail(world, "批准巨构超出当前世界高度");
        if (com.sirin.hk3gtl.common.multiblock.loading.Hk3PatternLoading.current(world.world) == null)
            for (var chunk : bounds.chunkRepresentatives())
                if (!world.world.isLoaded(chunk)) { world.setError(MultiblockState.UNLOAD_ERROR); return false; }
        for (var limit : limits) world.getGlobalCount().put(limit, 0);
        if (!matchPart(world, access, center, control, savePredicate)) return false;

        // 按线性坐标合并稀疏实体和空气，不为每个空气格分配谓词、坐标或IO记录。
        int cursor = 0, controlAt = linear(controller), linear = 0;
        var pos = new BlockPos.MutableBlockPos();
        for (int z = 0; z < size[2]; z++) for (int y = 0; y < size[1]; y++) for (int x = 0; x < size[0]; x++, linear++) {
            boolean occupied = cursor < cells.length && (cells[cursor] >>> 16) == linear;
            int state = occupied ? (int) (cells[cursor++] & 65535) : -1;
            if (linear == controlAt) continue;
            setPosition(pos, center, x - controller[0], y - controller[1], z - controller[2], turn);
            BlockState actual = world.world.getBlockState(pos);
            if (occupied && Hk3InterfacePredicates.isInterface(actual)) {
                if (!matchPart(world, access, pos.immutable(), universal, savePredicate)) return false;
                continue;
            }
            if (occupied ? actual != states[turn][state] && actual != activeStates[turn][state] : !Hk3InterfacePredicates.isClearance(actual)) {
                access.hk3gtl$update(pos.immutable(), occupied ? Predicates.states(states[turn][state]) : Hk3InterfacePredicates.clearance());
                return fail(world, occupied ? "批准巨构建材或状态不符" : "批准巨构空气区被占用");
            }
            if (actual.getBlock() instanceof ActiveBlock)
                world.getMatchContext().getOrCreate("vaBlocks", LongOpenHashSet::new).add(pos.asLong());
        }
        for (var limit : limits) {
            int count = world.getGlobalCount().getOrDefault(limit, 0);
            if (count < limit.minCount)
                return fail(world, "缺少整机所需的真实工作仓");
            if (limit.maxCount >= 0 && count > limit.maxCount)
                return fail(world, "接口仓数量超过整机上限");
        }
        world.getMatchContext().set(BOUNDS_KEY, bounds);
        for (var chunk : bounds.chunkRepresentatives()) world.addPosCache(chunk);
        world.setError(null); world.setNeededFlip(false);
        return true;
    }

    /** 除雪只枚举批准实体的暴露顶面，不扫描整个空气包围盒。 */
    public int snowSurfaceCandidates() { return cells.length; }

    /** 远景只借用常驻实体坐标，状态必须在服务器已加载区块中重新实读。 */
    public int farViewCellCount() { return cells.length; }

    public void farViewCellPosition(int index, BlockPos center, Direction front, BlockPos.MutableBlockPos out) {
        Objects.checkIndex(index, cells.length);
        int at = (int) (cells[index] >>> 16);
        int turn = switch (front) { case NORTH -> 0; case EAST -> 1; case SOUTH -> 2; case WEST -> 3;
            default -> throw new IllegalArgumentException("巨构远景只支持水平控制器"); };
        setPosition(out, center, at % size[0] - controller[0], at / size[0] % size[1] - controller[1],
                at / size[0] / size[1] - controller[2], turn);
    }

    public record SnowSurface(BlockPos support, BlockState expected, BlockState active) {}

    public SnowSurface snowSurface(int index, BlockPos center, Direction front) {
        if (!Hk3SnowSurfaceIndex.exposed(cells, index, size[0], size[1])) return null;
        int at = (int) (cells[index] >>> 16), state = (int) (cells[index] & 65535);
        if (at == linear(controller)) return null;
        int turn = switch (front) { case NORTH -> 0; case EAST -> 1; case SOUTH -> 2; case WEST -> 3;
            default -> throw new IllegalArgumentException("除雪只支持水平控制器"); };
        int x = at % size[0], y = at / size[0] % size[1], z = at / size[0] / size[1];
        return new SnowSurface(worldPosition(center, new int[]{x, y, z}, turn), states[turn][state], activeStates[turn][state]);
    }

    /** 任意实体位置可容纳接口，主控与空气不进入拆除接口范围。 */
    public TraceabilityPredicate dismantlePort(int x, int y, int z) {
        int at = ((z + controller[2]) * size[1] + y + controller[1]) * size[0] + x + controller[0];
        if (at == linear(controller)) return null;
        int index = Arrays.binarySearch(cells, (long) at << 16);
        if (index < 0) index = -index - 1;
        return index < cells.length && cells[index] >>> 16 == at ? universal : null;
    }

    private static boolean matchPart(MultiblockState world, Hk3MultiblockStateAccess access, BlockPos pos,
                                     TraceabilityPredicate predicate, boolean savePredicate) {
        if (!access.hk3gtl$update(pos, predicate) || !predicate.test(world)) return false;
        if (world.getTileEntity() instanceof IMachineBlockEntity entity && entity.getMetaMachine() instanceof IMultiPart part) {
            if (part.isFormed() && !part.canShared() && !part.hasController(world.controllerPos))
                return fail(world, "接口仓已被其他控制器占用");
            world.getMatchContext().getOrCreate("parts", HashSet::new).add(part);
        }
        world.addPosCache(pos);
        world.getMatchContext().getOrCreate("ioMap", Long2ObjectOpenHashMap::new).put(pos.asLong(), world.io);
        if (savePredicate) world.getMatchContext().getOrCreate("predicates", HashMap::new).put(pos, predicate);
        return true;
    }

    private static boolean fail(MultiblockState world, String message) {
        world.setError(new PatternStringError(message)); return false;
    }
    private int linear(int[] p) { return (p[2] * size[1] + p[1]) * size[0] + p[0]; }
    private static Rotation rotation(int turn) { return Rotation.values()[turn]; }
    private BlockPos worldPosition(BlockPos center, int[] p, int turn) {
        var pos = new BlockPos.MutableBlockPos();
        setPosition(pos, center, p[0] - controller[0], p[1] - controller[1], p[2] - controller[2], turn);
        return pos.immutable();
    }
    private static void setPosition(BlockPos.MutableBlockPos pos, BlockPos center, int x, int y, int z, int turn) {
        int rx = switch (turn) { case 1 -> -z; case 2 -> -x; case 3 -> z; default -> x; };
        int rz = switch (turn) { case 1 -> x; case 2 -> -z; case 3 -> -x; default -> z; };
        pos.set(center.getX() + rx, center.getY() + y, center.getZ() + rz);
    }
    private Bounds bounds(BlockPos center, int turn) {
        BlockPos a = worldPosition(center, new int[]{0, 0, 0}, turn);
        BlockPos b = worldPosition(center, new int[]{size[0] - 1, size[1] - 1, size[2] - 1}, turn);
        return new Bounds(new BlockPos(Math.min(a.getX(), b.getX()), a.getY(), Math.min(a.getZ(), b.getZ())),
                new BlockPos(Math.max(a.getX(), b.getX()), b.getY(), Math.max(a.getZ(), b.getZ())));
    }
    @Override public void autoBuild(Player player, MultiblockState state) {
        com.sirin.hk3gtl.common.multiblock.build.Hk3UniversalTerminalBuilder.use(player, state, null);
    }
    private static BlockState state(String text) {
        int start = text.indexOf('[');
        var block = Hk3StructureBlocks.require(start < 0 ? text : text.substring(0, start));
        BlockState state = block.defaultBlockState();
        if (start >= 0) for (String entry : text.substring(start + 1, text.length() - 1).split(",")) {
            String[] pair = entry.split("=", 2);
            if (pair.length != 2) throw new IllegalStateException("批准巨构状态错误：" + text);
            Property<?> property = block.getStateDefinition().getProperty(pair[0]);
            if (property == null) throw new IllegalStateException("批准巨构状态错误：" + text);
            state = property(state, property, pair[1]);
        }
        return state;
    }
    private static <T extends Comparable<T>> BlockState property(BlockState state, Property<T> property, String value) {
        return state.setValue(property, property.getValue(value).orElseThrow(() -> new IllegalStateException("批准巨构属性错误：" + value)));
    }
}
