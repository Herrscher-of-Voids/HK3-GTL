package com.sirin.hk3gtl.common.multiblock.loading;

import com.gregtechceu.gtceu.api.block.ActiveBlock;
import com.gregtechceu.gtceu.api.machine.multiblock.MultiblockControllerMachine;
import it.unimi.dsi.fastutil.ints.Int2ObjectOpenHashMap;
import it.unimi.dsi.fastutil.longs.Long2ObjectOpenHashMap;
import it.unimi.dsi.fastutil.longs.LongIterator;
import it.unimi.dsi.fastutil.longs.LongSet;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.ChunkPos;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.level.ChunkEvent;
import net.minecraftforge.event.level.LevelEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.util.ArrayDeque;
import java.util.BitSet;
import java.util.HashSet;
import java.util.IdentityHashMap;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentLinkedQueue;

/** 活动外壳按已加载区块分批同步，不借灯效维持结构区块。 */
@Mod.EventBusSubscriber(modid = "hk3gtl", bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class Hk3ActiveShells {
    private static final Map<MultiblockControllerMachine, ShellState> MACHINES = new IdentityHashMap<>();
    private static final Map<LongSet, ShellState> RETIRED = new IdentityHashMap<>();
    private static final Map<ServerLevel, Long2ObjectOpenHashMap<Set<ShellChunk>>> CHUNKS = new IdentityHashMap<>();
    private static final Map<ServerLevel, Long2ObjectOpenHashMap<ResetChunk>> RESET = new IdentityHashMap<>();
    private static final ArrayDeque<ShellState> INDEXING = new ArrayDeque<>();
    private static final ArrayDeque<ShellChunk> PENDING = new ArrayDeque<>();
    private static final ArrayDeque<ResetChunk> RESETS = new ArrayDeque<>();
    private static final ConcurrentLinkedQueue<LoadedChunk> LOADED = new ConcurrentLinkedQueue<>();

    private Hk3ActiveShells() {}

    public static void update(MultiblockControllerMachine machine, LongSet blocks, boolean active) {
        update(machine, blocks, active, 18);
    }

    public static void update(MultiblockControllerMachine machine, LongSet blocks, boolean active, int flags) {
        if (!(machine.getLevel() instanceof ServerLevel level)) return;
        if (blocks == null) {
            remove(machine);
            return;
        }
        if (!machine.isFormed()) {
            remove(machine);
            if (!RETIRED.containsKey(blocks)) {
                ShellState state = new ShellState(level, blocks, false, flags);
                state.retired = true;
                RETIRED.put(blocks, state);
                INDEXING.add(state);
            }
            return;
        }
        ShellState state = MACHINES.get(machine);
        if (state == null || state.blocks != blocks) {
            remove(machine);
            ShellState old = RETIRED.remove(blocks);
            if (old != null) discard(old);
            state = new ShellState(level, blocks, active, flags);
            MACHINES.put(machine, state);
            INDEXING.add(state);
        } else if (state.active != active) {
            state.active = active;
            for (ShellChunk chunk : state.chunks.values()) queue(chunk, true);
        }
    }

    public static void remove(MultiblockControllerMachine machine) {
        ShellState state = MACHINES.remove(machine);
        if (state == null) return;
        state.active = false;
        state.retired = true;
        RETIRED.put(state.blocks, state);
        for (ShellChunk chunk : state.chunks.values()) queue(chunk, true);
        finish(state);
    }

    @SubscribeEvent
    public static void loaded(ChunkEvent.Load event) {
        if (event.getLevel() instanceof ServerLevel level)
            LOADED.add(new LoadedChunk(level, event.getChunk().getPos().toLong()));
    }

    @SubscribeEvent
    public static void tick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END) return;
        LoadedChunk loaded;
        while ((loaded = LOADED.poll()) != null) {
            var chunks = CHUNKS.get(loaded.level);
            if (chunks != null) {
                var shells = chunks.get(loaded.chunk);
                if (shells != null) for (ShellChunk shell : shells) queue(shell, true);
            }
            var resets = RESET.get(loaded.level);
            if (resets != null) {
                var reset = resets.get(loaded.chunk);
                if (reset != null) queue(reset);
            }
        }
        long deadline = System.nanoTime() + 2_000_000L;
        int budget = 8192;
        boolean index = true;
        boolean reset = true;
        while (budget > 0 && (!INDEXING.isEmpty() || !PENDING.isEmpty() || !RESETS.isEmpty()) && System.nanoTime() < deadline) {
            if (!INDEXING.isEmpty() && (PENDING.isEmpty() && RESETS.isEmpty() || index)) {
                ShellState state = INDEXING.removeFirst();
                if (!state.discarded) budget -= index(state);
            } else if (!RESETS.isEmpty() && (PENDING.isEmpty() || reset)) {
                ResetChunk chunk = RESETS.removeFirst();
                chunk.queued = false;
                budget -= reset(chunk);
                reset = false;
            } else {
                ShellChunk chunk = PENDING.removeFirst();
                chunk.queued = false;
                if (!chunk.removed) budget -= sync(chunk);
                reset = true;
            }
            index = !index;
        }
    }

    @SubscribeEvent
    public static void unloaded(LevelEvent.Unload event) {
        if (!(event.getLevel() instanceof ServerLevel level)) return;
        MACHINES.values().removeIf(state -> {
            if (state.level != level) return false;
            state.discarded = true;
            return true;
        });
        RETIRED.values().removeIf(state -> {
            if (state.level != level) return false;
            state.discarded = true;
            return true;
        });
        CHUNKS.remove(level);
        RESET.remove(level);
        INDEXING.removeIf(state -> state.level == level);
        PENDING.removeIf(chunk -> chunk.state.level == level);
        RESETS.removeIf(chunk -> chunk.level == level);
        LOADED.removeIf(chunk -> chunk.level == level);
    }

    private static int index(ShellState state) {
        int count = 0;
        while (count < 256 && state.cursor.hasNext()) {
            long pos = state.cursor.nextLong();
            long key = ChunkPos.asLong(BlockPos.getX(pos) >> 4, BlockPos.getZ(pos) >> 4);
            ShellChunk chunk = state.chunks.get(key);
            if (chunk == null) {
                chunk = new ShellChunk(state, key);
                state.chunks.put(key, chunk);
                CHUNKS.computeIfAbsent(state.level, level -> new Long2ObjectOpenHashMap<>())
                        .computeIfAbsent(key, chunkKey -> new HashSet<>()).add(chunk);
            }
            int section = BlockPos.getY(pos) >> 4;
            int bit = localBit(pos);
            chunk.positions.computeIfAbsent(section, ignored -> new BitSet(4096)).set(bit);
            chunk.pending.computeIfAbsent(section, ignored -> new BitSet(4096)).set(bit);
            queue(chunk, false);
            count++;
        }
        state.indexing = state.cursor.hasNext();
        if (state.indexing) INDEXING.addLast(state);
        else {
            if (state.retired) for (ShellChunk chunk : state.chunks.values()) queue(chunk, false);
            finish(state);
        }
        return count;
    }

    private static int sync(ShellChunk shell) {
        ShellState state = shell.state;
        if (state.retired) {
            var reset = RESET.computeIfAbsent(state.level, ignored -> new Long2ObjectOpenHashMap<>())
                    .computeIfAbsent(shell.key, ignored -> new ResetChunk(state.level, shell.key));
            for (var entry : shell.positions.int2ObjectEntrySet())
                reset.pending.computeIfAbsent(entry.getIntKey(), ignored -> new BitSet(4096)).or(entry.getValue());
            reset.flags |= state.flags;
            queue(reset);
            unindex(shell);
            finish(state);
            return 0;
        }
        int count = sync(state.level, shell.key, shell.pending, state.active, state.flags);
        if (!shell.pending.isEmpty() && state.level.getChunkSource().getChunkNow(ChunkPos.getX(shell.key), ChunkPos.getZ(shell.key)) != null)
            queue(shell, false);
        return count;
    }

    private static int reset(ResetChunk shell) {
        int count = sync(shell.level, shell.key, shell.pending, false, shell.flags);
        if (shell.pending.isEmpty()) {
            var resets = RESET.get(shell.level);
            resets.remove(shell.key);
            if (resets.isEmpty()) RESET.remove(shell.level);
        } else if (shell.level.getChunkSource().getChunkNow(ChunkPos.getX(shell.key), ChunkPos.getZ(shell.key)) != null)
            queue(shell);
        return count;
    }

    private static int sync(ServerLevel level, long key, Int2ObjectOpenHashMap<BitSet> pending, boolean active, int flags) {
        var chunk = level.getChunkSource().getChunkNow(ChunkPos.getX(key), ChunkPos.getZ(key));
        if (chunk == null) return 0;
        int count = 0;
        var pos = new BlockPos.MutableBlockPos();
        while (count < 256 && !pending.isEmpty()) {
            var entry = pending.int2ObjectEntrySet().iterator().next();
            int section = entry.getIntKey();
            var bits = entry.getValue();
            for (int bit = bits.nextSetBit(0); bit >= 0 && count < 256; bit = bits.nextSetBit(bit + 1)) {
                pos.set((ChunkPos.getX(key) << 4) + (bit & 15), (section << 4) + (bit >> 8),
                        (ChunkPos.getZ(key) << 4) + (bit >> 4 & 15));
                var blockState = chunk.getBlockState(pos);
                if (blockState.getBlock() instanceof ActiveBlock block) {
                    boolean lit = active;
                    var chunks = CHUNKS.get(level);
                    var owners = chunks == null ? null : chunks.get(key);
                    if (!lit && owners != null) for (ShellChunk other : owners) {
                        var positions = other.positions.get(section);
                        if (other.state.active && positions != null && positions.get(bit)) {
                            lit = true;
                            break;
                        }
                    }
                    var changed = block.changeActive(blockState, lit);
                    if (changed != blockState) level.setBlock(pos, changed, flags);
                }
                bits.clear(bit);
                count++;
            }
            if (bits.isEmpty()) pending.remove(section);
        }
        return count;
    }

    private static void queue(ShellChunk chunk, boolean reset) {
        if (reset) for (var entry : chunk.positions.int2ObjectEntrySet())
            chunk.pending.computeIfAbsent(entry.getIntKey(), ignored -> new BitSet(4096)).or(entry.getValue());
        if (!chunk.queued) {
            chunk.queued = true;
            PENDING.addLast(chunk);
        }
    }

    private static void queue(ResetChunk chunk) {
        if (!chunk.queued) {
            chunk.queued = true;
            RESETS.addLast(chunk);
        }
    }

    private static int localBit(long pos) {
        return (BlockPos.getY(pos) & 15) << 8 | (BlockPos.getZ(pos) & 15) << 4 | (BlockPos.getX(pos) & 15);
    }

    private static void unindex(ShellChunk chunk) {
        chunk.removed = true;
        chunk.state.chunks.remove(chunk.key);
        var chunks = CHUNKS.get(chunk.state.level);
        var owners = chunks.get(chunk.key);
        owners.remove(chunk);
        if (owners.isEmpty()) chunks.remove(chunk.key);
        if (chunks.isEmpty()) CHUNKS.remove(chunk.state.level);
    }

    private static void finish(ShellState state) {
        if (state.retired && !state.indexing && state.chunks.isEmpty()) RETIRED.remove(state.blocks, state);
    }

    private static void discard(ShellState state) {
        state.discarded = true;
        for (ShellChunk chunk : state.chunks.values().toArray(ShellChunk[]::new)) unindex(chunk);
    }

    private static final class ShellState {
        final ServerLevel level;
        final LongSet blocks;
        final LongIterator cursor;
        final int flags;
        final Long2ObjectOpenHashMap<ShellChunk> chunks = new Long2ObjectOpenHashMap<>();
        boolean active;
        boolean indexing = true;
        boolean retired;
        boolean discarded;

        ShellState(ServerLevel level, LongSet blocks, boolean active, int flags) {
            this.level = level;
            this.blocks = blocks;
            this.cursor = blocks.iterator();
            this.active = active;
            this.flags = flags;
        }
    }

    private static final class ShellChunk {
        final ShellState state;
        final long key;
        final Int2ObjectOpenHashMap<BitSet> positions = new Int2ObjectOpenHashMap<>();
        final Int2ObjectOpenHashMap<BitSet> pending = new Int2ObjectOpenHashMap<>();
        boolean queued;
        boolean removed;

        ShellChunk(ShellState state, long key) {
            this.state = state;
            this.key = key;
        }
    }

    private static final class ResetChunk {
        final ServerLevel level;
        final long key;
        final Int2ObjectOpenHashMap<BitSet> pending = new Int2ObjectOpenHashMap<>();
        int flags;
        boolean queued;

        ResetChunk(ServerLevel level, long key) {
            this.level = level;
            this.key = key;
        }
    }

    private record LoadedChunk(ServerLevel level, long chunk) {}
}
