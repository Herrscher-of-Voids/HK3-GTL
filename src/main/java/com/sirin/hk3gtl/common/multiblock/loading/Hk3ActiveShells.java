package com.sirin.hk3gtl.common.multiblock.loading;

import com.gregtechceu.gtceu.api.block.ActiveBlock;
import com.gregtechceu.gtceu.api.machine.multiblock.MultiblockControllerMachine;
import it.unimi.dsi.fastutil.longs.Long2ObjectOpenHashMap;
import it.unimi.dsi.fastutil.longs.LongArrayList;
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
    private static final ArrayDeque<ShellState> INDEXING = new ArrayDeque<>();
    private static final ArrayDeque<ShellChunk> PENDING = new ArrayDeque<>();
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
            if (chunks == null) continue;
            var shells = chunks.get(loaded.chunk);
            if (shells != null) for (ShellChunk shell : shells) queue(shell, true);
        }
        long deadline = System.nanoTime() + 2_000_000L;
        int budget = 8192;
        boolean index = true;
        while (budget > 0 && (!INDEXING.isEmpty() || !PENDING.isEmpty()) && System.nanoTime() < deadline) {
            if (!INDEXING.isEmpty() && (PENDING.isEmpty() || index)) {
                ShellState state = INDEXING.removeFirst();
                if (!state.discarded) budget -= index(state);
            } else {
                ShellChunk chunk = PENDING.removeFirst();
                chunk.queued = false;
                if (!chunk.removed) budget -= sync(chunk);
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
        INDEXING.removeIf(state -> state.level == level);
        PENDING.removeIf(chunk -> chunk.state.level == level);
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
            chunk.positions.add(pos);
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
        var chunk = state.level.getChunkSource().getChunkNow(ChunkPos.getX(shell.key), ChunkPos.getZ(shell.key));
        if (chunk == null) {
            shell.cursor = 0;
            return 0;
        }
        int count = 0;
        while (count < 256 && shell.cursor < shell.positions.size()) {
            long packed = shell.positions.getLong(shell.cursor++);
            BlockPos pos = BlockPos.of(packed);
            var blockState = chunk.getBlockState(pos);
            if (blockState.getBlock() instanceof ActiveBlock block) {
                boolean active = state.active;
                if (!active) {
                    for (ShellChunk other : CHUNKS.get(state.level).get(shell.key)) {
                        if (other.state.active && other.state.blocks.contains(packed)) {
                            active = true;
                            break;
                        }
                    }
                }
                var changed = block.changeActive(blockState, active);
                if (changed != blockState) state.level.setBlock(pos, changed, state.flags);
            }
            count++;
        }
        if (shell.cursor < shell.positions.size()) queue(shell, false);
        else if (state.retired && !state.indexing) {
            unindex(shell);
            finish(state);
        }
        return count;
    }

    private static void queue(ShellChunk chunk, boolean reset) {
        if (reset) chunk.cursor = 0;
        if (!chunk.queued) {
            chunk.queued = true;
            PENDING.addLast(chunk);
        }
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
        final LongArrayList positions = new LongArrayList();
        int cursor;
        boolean queued;
        boolean removed;

        ShellChunk(ShellState state, long key) {
            this.state = state;
            this.key = key;
        }
    }

    private record LoadedChunk(ServerLevel level, long chunk) {}
}
