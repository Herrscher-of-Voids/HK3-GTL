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
import com.sirin.hk3gtl.common.multiblock.loading.Hk3PatternLoading;
import com.sirin.hk3gtl.mixin.gtceu.Hk3MultiblockStateAccess;
import it.unimi.dsi.fastutil.longs.AbstractLongSet;
import it.unimi.dsi.fastutil.longs.Long2ObjectOpenHashMap;
import it.unimi.dsi.fastutil.longs.LongIterator;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.ChunkPos;
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

    public Hk3LargeStructurePattern(MultiblockMachineDefinition definition, Hk3PackedArchitectureReader.PatternData data,
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
        cells = data.cells();
        states = new BlockState[4][data.palette().length];
        activeStates = new BlockState[4][data.palette().length];
        for (int i = 0; i < data.palette().length; i++) {
            BlockState state = state(data.palette()[i]);
            for (int turn = 0; turn < 4; turn++) {
                BlockState rotated = state.rotate(rotation(turn));
                states[turn][i] = rotated;
                activeStates[turn][i] = rotated.getBlock() instanceof ActiveBlock active
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
        var loading = Hk3PatternLoading.current(world.world);
        return (loading == null ? new Check(null) : loading.largeCheck()).match(world, center, front, up, flipped, savePredicate);
    }

    public Check newCheck(Hk3PatternLoading loading) { return new Check(loading); }

    public final class Check {
        private final Hk3PatternLoading loading;
        private MultiblockState world;
        private BlockPos center;
        private Bounds bounds;
        private ActivePositions active;
        private int turn, cursor = -1;
        private long sourceChunk = -1;
        private long[] chunks;
        private long deadline = Long.MAX_VALUE;
        private boolean started, dirty;

        private Check(Hk3PatternLoading loading) { this.loading = loading; }
        public void deadline(long value) { deadline = value; }
        public boolean dirty() { return dirty; }
        public void missingChunk() { dirty = true; }
        public boolean changed(BlockPos pos) {
            if (!started) return false;
            int index = active.index(pos);
            if (center.equals(pos) || index >= 0 && index < cursor) dirty = true;
            return dirty;
        }
        private boolean match(MultiblockState world, BlockPos center, Direction front, Direction up,
                              boolean flipped, boolean savePredicate) {
            var access = (Hk3MultiblockStateAccess) (Object) world;
            if (front.getAxis().isVertical() || up != Direction.NORTH || flipped)
                return fail(world, "该巨构仅支持水平四向且不可镜像");
            if (!started) {
                access.hk3gtl$clean();
                this.world = world; this.center = center;
                turn = switch (front) { case NORTH -> 0; case EAST -> 1; case SOUTH -> 2; default -> 3; };
                bounds = bounds(center, turn);
                if (world.world.isOutsideBuildHeight(bounds.min()) || world.world.isOutsideBuildHeight(bounds.max()))
                    return fail(world, "批准巨构超出当前世界高度");
                if (loading == null) for (var chunk : bounds.chunkRepresentatives())
                    if (!world.world.isLoaded(chunk)) { world.setError(MultiblockState.UNLOAD_ERROR); return false; }
                for (var limit : limits) world.getGlobalCount().put(limit, 0);
                active = new ActivePositions(center, turn);
                world.getMatchContext().set("vaBlocks", active);
                started = true;
            }
            if (cursor < 0) {
                if (!matchPart(world, access, center, control, savePredicate)) return false;
                cursor = 0;
            }
            long controlAt = positionKey(controller[0], controller[1], controller[2]);
            var pos = new BlockPos.MutableBlockPos();
            while (cursor < cells.length) {
                long at = cells[cursor] >>> 16;
                int state = (int) (cells[cursor] & 65535);
                if (at == controlAt) { cursor++; continue; }
                setPosition(pos, center, cellX(at) - controller[0], cellY(at) - controller[1], cellZ(at) - controller[2], turn);
                if (loading != null) {
                    long group = (at >>> 8) / size[1];
                    if (sourceChunk != group) {
                        sourceChunk = group;
                        int x = cellX(at) & ~15, z = cellZ(at) & ~15;
                        var a = worldPosition(center, new int[]{x, 0, z}, turn);
                        var b = worldPosition(center, new int[]{Math.min(x + 15, size[0] - 1), 0, Math.min(z + 15, size[2] - 1)}, turn);
                        int minX = Math.min(a.getX(), b.getX()) >> 4, maxX = Math.max(a.getX(), b.getX()) >> 4;
                        int minZ = Math.min(a.getZ(), b.getZ()) >> 4, maxZ = Math.max(a.getZ(), b.getZ()) >> 4;
                        chunks = new long[(maxX - minX + 1) * (maxZ - minZ + 1)];
                        int i = 0;
                        for (int cx = minX; cx <= maxX; cx++) for (int cz = minZ; cz <= maxZ; cz++) chunks[i++] = ChunkPos.asLong(cx, cz);
                    }
                    loading.checkpoint(pos, chunks, deadline);
                }
                BlockState actual = world.world.getBlockState(pos);
                if (Hk3InterfacePredicates.isInterface(actual)) {
                    if (!matchPart(world, access, pos.immutable(), universal, savePredicate)) return false;
                } else {
                    if (actual != states[turn][state] && actual != activeStates[turn][state]) {
                        access.hk3gtl$update(pos.immutable(), Predicates.states(states[turn][state]));
                        return fail(world, "批准巨构建材或状态不符");
                    }
                    if (actual.getBlock() instanceof ActiveBlock) active.addIndex(cursor);
                }
                cursor++;
            }
            for (var limit : limits) {
                int count = world.getGlobalCount().getOrDefault(limit, 0);
                if (count < limit.minCount) return fail(world, "缺少整机所需的真实工作仓");
                if (limit.maxCount >= 0 && count > limit.maxCount) return fail(world, "接口仓数量超过整机上限");
            }
            world.getMatchContext().set(BOUNDS_KEY, bounds);
            for (var chunk : bounds.chunkRepresentatives()) world.addPosCache(chunk);
            world.setError(null); world.setNeededFlip(false);
            return true;
        }
        public void close(boolean formed) {
            if (started && !formed) ((Hk3MultiblockStateAccess) (Object) world).hk3gtl$clean();
        }
    }

    private final class ActivePositions extends AbstractLongSet {
        private final BlockPos center;
        private final int turn;
        private final BitSet selected = new BitSet();
        private int count;
        private ActivePositions(BlockPos center, int turn) { this.center = center; this.turn = turn; }
        private int index(BlockPos pos) {
            int rx = pos.getX() - center.getX(), rz = pos.getZ() - center.getZ();
            int x = (switch (turn) { case 1 -> rz; case 2 -> -rx; case 3 -> -rz; default -> rx; }) + controller[0];
            int y = pos.getY() - center.getY() + controller[1];
            int z = (switch (turn) { case 1 -> -rx; case 2 -> -rz; case 3 -> rx; default -> rz; }) + controller[2];
            if (x < 0 || x >= size[0] || y < 0 || y >= size[1] || z < 0 || z >= size[2]) return -1;
            return cellIndex(positionKey(x, y, z));
        }
        private boolean addIndex(int index) {
            if (selected.get(index)) return false;
            selected.set(index); count++; return true;
        }
        @Override public boolean add(long pos) { return addIndex(index(BlockPos.of(pos))); }
        @Override public boolean contains(long pos) { int index = index(BlockPos.of(pos)); return index >= 0 && selected.get(index); }
        @Override public int size() { return count; }
        @Override public void clear() { selected.clear(); count = 0; }
        @Override public LongIterator iterator() {
            return new LongIterator() {
                int next = selected.nextSetBit(0);
                final BlockPos.MutableBlockPos pos = new BlockPos.MutableBlockPos();
                @Override public boolean hasNext() { return next >= 0; }
                @Override public long nextLong() {
                    long at = cells[next] >>> 16;
                    next = selected.nextSetBit(next + 1);
                    setPosition(pos, center, cellX(at) - controller[0], cellY(at) - controller[1], cellZ(at) - controller[2], turn);
                    return pos.asLong();
                }
            };
        }
    }

    /** 除雪只枚举批准实体的暴露顶面，不扫描整个空气包围盒。 */
    public int snowSurfaceCandidates() { return cells.length; }

    /** 远景只借用常驻实体坐标，状态必须在服务器已加载区块中重新实读。 */
    public int farViewCellCount() { return cells.length; }

    public void farViewCellPosition(int index, BlockPos center, Direction front, BlockPos.MutableBlockPos out) {
        Objects.checkIndex(index, cells.length);
        long at = cells[index] >>> 16;
        int turn = switch (front) { case NORTH -> 0; case EAST -> 1; case SOUTH -> 2; case WEST -> 3;
            default -> throw new IllegalArgumentException("巨构远景只支持水平控制器"); };
        setPosition(out, center, cellX(at) - controller[0], cellY(at) - controller[1], cellZ(at) - controller[2], turn);
    }

    public record SnowSurface(BlockPos support, BlockState expected, BlockState active) {}

    public SnowSurface snowSurface(int index, BlockPos center, Direction front) {
        long at = cells[index] >>> 16;
        int state = (int) (cells[index] & 65535), x = cellX(at), y = cellY(at), z = cellZ(at);
        if (y < size[1] - 1 && cellIndex(positionKey(x, y + 1, z)) >= 0) return null;
        if (at == positionKey(controller[0], controller[1], controller[2])) return null;
        int turn = switch (front) { case NORTH -> 0; case EAST -> 1; case SOUTH -> 2; case WEST -> 3;
            default -> throw new IllegalArgumentException("除雪只支持水平控制器"); };
        return new SnowSurface(worldPosition(center, new int[]{x, y, z}, turn), states[turn][state], activeStates[turn][state]);
    }

    /** 任意实体位置可容纳接口，主控与空气不进入拆除接口范围。 */
    public TraceabilityPredicate dismantlePort(int x, int y, int z) {
        x += controller[0]; y += controller[1]; z += controller[2];
        if (x < 0 || x >= size[0] || y < 0 || y >= size[1] || z < 0 || z >= size[2]) return null;
        long at = positionKey(x, y, z);
        if (at == positionKey(controller[0], controller[1], controller[2])) return null;
        return cellIndex(at) >= 0 ? universal : null;
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
    private long positionKey(int x, int y, int z) {
        long chunk = (long) (x >> 4) * ((size[2] + 15) >> 4) + (z >> 4);
        return ((chunk * size[1] + y) << 8) | ((z & 15) << 4) | (x & 15);
    }
    private int cellX(long at) { return (int) ((at >>> 8) / size[1] / ((size[2] + 15) >> 4)) * 16 + ((int) at & 15); }
    private int cellY(long at) { return (int) ((at >>> 8) % size[1]); }
    private int cellZ(long at) { return (int) ((at >>> 8) / size[1] % ((size[2] + 15) >> 4)) * 16 + ((int) (at >>> 4) & 15); }
    private int cellIndex(long at) {
        int index = Arrays.binarySearch(cells, at << 16);
        if (index < 0) index = -index - 1;
        return index < cells.length && cells[index] >>> 16 == at ? index : -1;
    }
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
