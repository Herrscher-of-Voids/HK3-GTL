package com.sirin.hk3gtl.common.farview;

import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.gregtechceu.gtceu.api.machine.multiblock.MultiblockControllerMachine;
import com.gregtechceu.gtceu.api.pattern.BlockPattern;
import com.mojang.logging.LogUtils;
import com.sirin.hk3gtl.common.multiblock.build.Hk3IntegrityHost;
import com.sirin.hk3gtl.common.multiblock.build.Hk3UniversalTerminalBuilder;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3LargeStructurePattern;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;

import java.lang.ref.WeakReference;
import java.util.IdentityHashMap;
import java.util.Map;
import java.util.NoSuchElementException;
import java.util.PrimitiveIterator;

/** 真实GT成型后延迟实读；只借判定坐标，不解码蓝图、不申请区块票据。 */
public final class Hk3FarViewCapture {
    private static final int MAX_STEPS = 4096;
    private static final long BUDGET_NANOS = 500_000L;
    private static final Map<MinecraftServer, Hk3FarViewCaptureQueue> QUEUES = new IdentityHashMap<>();

    private static final class Key {
        final ResourceKey<Level> dimension;
        final WeakReference<MultiblockControllerMachine> owner;
        final int hash;
        Key(ServerLevel level, MultiblockControllerMachine controller) {
            dimension = level.dimension(); owner = new WeakReference<>(controller);
            hash = System.identityHashCode(controller);
        }
        @Override public int hashCode() { return hash; }
        @Override public boolean equals(Object other) {
            return this == other || other instanceof Key key && owner.get() != null && owner.get() == key.owner.get();
        }
    }

    private Hk3FarViewCapture() {}

    public static void formed(MultiblockControllerMachine controller) {
        try {
            if (!(controller.getLevel() instanceof ServerLevel level) || !level.getServer().isSameThread()
                    || !"hk3gtl".equals(controller.self().getDefinition().getId().getNamespace())
                    || controller.isInValid() || !controller.isFormed() || controller.getMultiblockState().hasError()
                    || Hk3UniversalTerminalBuilder.isBuilding(controller)) return;
            // 专用完整性任务已有实读；W03明确禁用静态远景，不能为动态构件生成重影。
            if (controller instanceof Hk3IntegrityHost) return;
            BlockPattern pattern = controller.getPattern();
            if (pattern == null || !(pattern instanceof Hk3LargeStructurePattern) && pattern.getClass() != BlockPattern.class) return;
            var state = controller.getMultiblockState();
            var cache = state.cache;
            var owner = new WeakReference<>(controller);
            BlockPos center = controller.getPos().immutable();
            Direction front = controller.getFrontFacing(), up = controller.getUpwardsFacing();
            boolean flipped = controller.isFlipped();
            long notBefore = (long) level.getServer().getTickCount() + 1;
            PrimitiveIterator.OfLong positions;
            if (pattern instanceof Hk3LargeStructurePattern large) {
                positions = new PrimitiveIterator.OfLong() {
                    int index;
                    final BlockPos.MutableBlockPos pos = new BlockPos.MutableBlockPos();
                    @Override public boolean hasNext() { return index < large.farViewCellCount(); }
                    @Override public long nextLong() {
                        if (!hasNext()) throw new NoSuchElementException();
                        large.farViewCellPosition(index++, center, front, pos); return pos.asLong();
                    }
                };
            } else {
                positions = cache.iterator();
            }
            var pos = new BlockPos.MutableBlockPos();
            var capture = Hk3FarViewCaptureQueue.<BlockState>capture(() -> {
                var machine = owner.get();
                return machine != null && !machine.isInValid() && machine.getLevel() == level
                        && machine.isFormed() && machine.getMultiblockState() == state && !state.hasError()
                        && state.cache == cache && machine.getPattern() == pattern
                        && machine.getFrontFacing() == front && machine.getUpwardsFacing() == up
                        && machine.isFlipped() == flipped && !Hk3UniversalTerminalBuilder.isBuilding(machine)
                        && level.getChunkSource().getChunkNow(center.getX() >> 4, center.getZ() >> 4) != null
                        && MetaMachine.getMachine(level, center) == machine;
            }, positions, position -> {
                pos.set(position);
                var chunk = level.getChunkSource().getChunkNow(pos.getX() >> 4, pos.getZ() >> 4);
                return chunk == null ? null : chunk.getBlockState(pos);
            }, (position, actual) -> {
                pos.set(position);
                if (actual.isAir()) Hk3FarViewData.changed(level, pos, actual);
                else Hk3FarViewData.observe(level, pos, actual);
            });
            var task = new Hk3FarViewCaptureQueue.Task() {
                @Override public boolean valid() { return capture.valid(); }
                @Override public Hk3FarViewCaptureQueue.Step step() {
                    // 父类RETURN仍早于派生类最终验证，必须等后续服务器tick再读取世界。
                    return level.getServer().getTickCount() < notBefore
                            ? Hk3FarViewCaptureQueue.Step.WAIT : capture.step();
                }
                @Override public void failed(RuntimeException failure) {
                    LogUtils.getLogger().error("HK3GTL成型远景实读失败：{} {}", level.dimension().location(), center, failure);
                }
            };
            QUEUES.computeIfAbsent(level.getServer(), ignored -> new Hk3FarViewCaptureQueue())
                    .add(new Key(level, controller), task);
        } catch (RuntimeException failure) {
            LogUtils.getLogger().error("HK3GTL成型远景登记失败：{}", controller.getPos(), failure);
        }
    }

    public static void cancel(MultiblockControllerMachine controller) {
        if (!(controller.getLevel() instanceof ServerLevel level) || !level.getServer().isSameThread()) return;
        var queue = QUEUES.get(level.getServer());
        if (queue != null) queue.cancel(new Key(level, controller));
    }
    public static void unload(ServerLevel level) {
        var queue = QUEUES.get(level.getServer());
        if (queue != null) queue.cancelIf(key -> key instanceof Key capture && capture.dimension.equals(level.dimension()));
    }
    public static void tick(MinecraftServer server) {
        var queue = QUEUES.get(server);
        if (queue != null) queue.tick(System.nanoTime() + BUDGET_NANOS, MAX_STEPS, System::nanoTime);
    }
    public static void stop(MinecraftServer server) {
        var queue = QUEUES.remove(server); if (queue != null) queue.clear();
    }
}
