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
import it.unimi.dsi.fastutil.ints.Int2ObjectOpenHashMap;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.Property;
import java.util.*;

/**
 * 【文件职责】I19–I28按批准全体素判定，保留严格空气、状态、朝向、真实仓及部件共享约束。
 * 【变更记录 #1】2026-10-26 19:36:08（第1次备注 · 内测5修订177）
 * - 删除：新巨构对完整三维谓词数组及逐空气格IO映射的需求；旧机Pattern不变。
 * - 新增：排序紧凑坐标、端口优先检查、四向状态旋转及区块边界通知。
 * - 修改：普通建材直接比较精确状态，只有控制器/真实接口进入GT谓词与IO上下文。
 * - 用途：千万体积结构仍验证全部空气，内存随实体数量增长；未加载区块拒绝成型。
 * 【变更记录 #2】2026-10-26 21:01:40（第2次备注 · 内测5修订177）
 * - 删除：将GT活动机壳的正常active切换误判为破坏的比较；新增：双活动状态预计算。
 * - 修改：只有ActiveBlock的活动位可变化，材料及其他属性仍逐格严格匹配。
 * - 用途：机器开始运行后重检不会因正常灯效解体，与原GT状态谓词语义一致。
 * 【变更记录 #3】2026-10-26 22:36:20（修订179）
 * - 删除：继承单主控占位Pattern的预览回退；新增：完整批准模板的getPreview入口。
 * - 修改：预览与显式形状共用无损流式烘焙；用途：任何GT回退路径都保留完整建筑。
 * 【变更记录 #4】2026-10-30 01:36:10（修订184）
 * - 删除：只提示拒绝的巨构自动搭建入口；新增：转入统一分批建造器。
 * - 用途：使用批准实体模板放置，最终仍由本Pattern检查完整空气、材料及接口。
 */
public final class Hk3LargeStructurePattern extends BlockPattern {
    public static final String BOUNDS_KEY = "hk3gtlLargeBounds";
    private final MultiblockMachineDefinition definition;
    private final String architectureId;
    private final int[] size, controller;
    private final long[] cells;
    private final BlockState[][] states, activeStates;
    private final Int2ObjectOpenHashMap<PortCheck> ports;
    private final TraceabilityPredicate control;
    private final Set<SimplePredicate> limits = Collections.newSetFromMap(new IdentityHashMap<>());
    private record PortCheck(int[] pos, Direction face, TraceabilityPredicate predicate) {}

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
                                   Map<String, TraceabilityPredicate> portPredicates) {
        super(new TraceabilityPredicate[][][]{{{Predicates.controller(Predicates.blocks(definition.getBlock()))}}},
                new RelativeDirection[]{RelativeDirection.RIGHT, RelativeDirection.UP, RelativeDirection.BACK},
                new int[][]{{1, 1}}, new int[]{0, 0, 0, 0, 0});
        this.definition = definition;
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
        ports = new Int2ObjectOpenHashMap<>();
        for (var port : data.ports()) {
            var predicate = Objects.requireNonNull(portPredicates.get(port.id()), "巨构端口缺少能力：" + port.id());
            var direction = Objects.requireNonNull(Direction.byName(port.face()), "巨构端口方向错误");
            if (direction.getAxis().isVertical()) throw new IllegalStateException("巨构端口方向必须水平");
            int at = linear(port.pos());
            if (at == linear(controller) || ports.put(at, new PortCheck(port.pos(), direction, predicate)) != null)
                throw new IllegalStateException("巨构端口与主控重叠");
            limits.addAll(predicate.limited);
        }
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
        for (var chunk : bounds.chunkRepresentatives())
            if (!world.world.isLoaded(chunk)) { world.setError(MultiblockState.UNLOAD_ERROR); return false; }
        for (var limit : limits) world.getGlobalCount().put(limit, 0);
        if (!matchPart(world, access, center, control, front, savePredicate)) return false;
        for (var port : ports.values()) {
            BlockPos pos = worldPosition(center, port.pos(), turn);
            if (!matchPart(world, access, pos, port.predicate(), rotation(turn).rotate(port.face()), savePredicate))
                return false;
        }
        for (var limit : limits)
            if (world.getGlobalCount().getOrDefault(limit, 0) < limit.minCount)
                return fail(world, "缺少批准接口所需的真实工作仓");

        // 按线性坐标合并稀疏实体和空气，不为每个空气格分配谓词、坐标或IO记录。
        int cursor = 0, controlAt = linear(controller), linear = 0;
        var pos = new BlockPos.MutableBlockPos();
        for (int z = 0; z < size[2]; z++) for (int y = 0; y < size[1]; y++) for (int x = 0; x < size[0]; x++, linear++) {
            boolean occupied = cursor < cells.length && (cells[cursor] >>> 16) == linear;
            int state = occupied ? (int) (cells[cursor++] & 65535) : -1;
            if (linear == controlAt || ports.containsKey(linear)) continue;
            setPosition(pos, center, x - controller[0], y - controller[1], z - controller[2], turn);
            BlockState actual = world.world.getBlockState(pos);
            if (occupied ? actual != states[turn][state] && actual != activeStates[turn][state] : !Hk3InterfacePredicates.isClearance(actual)) {
                access.hk3gtl$update(pos.immutable(), occupied ? Predicates.states(states[turn][state]) : Hk3InterfacePredicates.clearance());
                return fail(world, occupied ? "批准巨构建材或状态不符" : "批准巨构空气区被占用");
            }
            if (actual.getBlock() instanceof ActiveBlock)
                world.getMatchContext().getOrCreate("vaBlocks", LongOpenHashSet::new).add(pos.asLong());
        }
        world.getMatchContext().set(BOUNDS_KEY, bounds);
        world.setError(null); world.setNeededFlip(false);
        return true;
    }

    /** 除雪只枚举批准实体的暴露顶面，不扫描整个空气包围盒。 */
    public int snowSurfaceCandidates() { return cells.length; }

    public record SnowSurface(BlockPos support, BlockState expected, BlockState active) {}

    public SnowSurface snowSurface(int index, BlockPos center, Direction front) {
        if (!Hk3SnowSurfaceIndex.exposed(cells, index, size[0], size[1])) return null;
        int at = (int) (cells[index] >>> 16), state = (int) (cells[index] & 65535);
        if (at == linear(controller) || ports.containsKey(at)) return null;
        int turn = switch (front) { case NORTH -> 0; case EAST -> 1; case SOUTH -> 2; case WEST -> 3;
            default -> throw new IllegalArgumentException("除雪只支持水平控制器"); };
        int x = at % size[0], y = at / size[0] % size[1], z = at / size[0] / size[1];
        return new SnowSurface(worldPosition(center, new int[]{x, y, z}, turn), states[turn][state], activeStates[turn][state]);
    }

    /** 只返回正式实体接口的原谓词，不把巨构空气包围盒当作拆除范围。 */
    public TraceabilityPredicate dismantlePort(int x, int y, int z) {
        var port = ports.get(((z + controller[2]) * size[1] + y + controller[1]) * size[0] + x + controller[0]);
        return port == null ? null : port.predicate();
    }

    private static boolean matchPart(MultiblockState world, Hk3MultiblockStateAccess access, BlockPos pos,
                                     TraceabilityPredicate predicate, Direction face, boolean savePredicate) {
        if (!access.hk3gtl$update(pos, predicate) || !predicate.test(world)) return false;
        if (world.getTileEntity() instanceof IMachineBlockEntity entity && entity.getMetaMachine() instanceof IMultiPart part) {
            if (part.self().getFrontFacing() != face) return fail(world, "接口仓朝向与批准外立面不符");
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
