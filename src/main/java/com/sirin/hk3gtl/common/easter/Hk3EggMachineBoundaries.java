package com.sirin.hk3gtl.common.easter;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.gregtechceu.gtceu.api.machine.multiblock.MultiblockControllerMachine;
import com.gregtechceu.gtceu.api.pattern.MultiblockWorldSavedData;
import com.gregtechceu.gtceu.api.pattern.util.RelativeDirection;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3LargeStructurePattern;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.BlockTags;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;

import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.HashSet;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;

/** 2026-11-11：复用成功放置回执与已加载区块的成型索引，收藏只归放置者。 */
public final class Hk3EggMachineBoundaries {
    private record Geometry(int[] size, int[] controller) {}
    private static final Map<String, Optional<Geometry>> GEOMETRY = new ConcurrentHashMap<>();

    private Hk3EggMachineBoundaries() {}

    public static void placed(ServerPlayer player, BlockPos pos, BlockState block) {
        boolean sapling = block.is(BlockTags.SAPLINGS);
        if (!sapling && !block.is(Blocks.CRAFTING_TABLE) && !block.is(Blocks.TNT)) return;
        var level = player.serverLevel();
        if (!level.hasChunkAt(pos) || !level.getBlockState(pos).equals(block)) return;
        if (sapling && (!level.hasChunkAt(pos.below()) || !level.getBlockState(pos.below()).is(BlockTags.DIRT)
                || !block.canSurvive(level, pos))) return;
        String blockId = BuiltInRegistries.BLOCK.getKey(block.getBlock()).toString();
        var saved = MultiblockWorldSavedData.getOrCreate(level);
        var seen = new HashSet<BlockPos>();
        for (int x = (pos.getX() - 4) >> 4; x <= (pos.getX() + 4) >> 4; x++)
            for (int z = (pos.getZ() - 4) >> 4; z <= (pos.getZ() + 4) >> 4; z++) {
                if (!level.hasChunk(x, z)) continue;
                for (var state : saved.getControllerInChunk(new ChunkPos(x, z))) {
                    if (!seen.add(state.controllerPos) || state.hasError() || !level.hasChunkAt(state.controllerPos)) continue;
                    var machine = MetaMachine.getMachine(level, state.controllerPos);
                    if (!(machine instanceof MultiblockControllerMachine controller) || !controller.isFormed()
                            || controller.getMultiblockState() != state) continue;
                    String machineId = controller.getDefinition().getId().toString();
                    String layout = sapling && machineId.equals("hk3gtl:i34_imaginary_tree_observation_array")
                            ? "i34" : Hk3EggMachineBoundaryFacts.layout(blockId, machineId);
                    if (layout == null) continue;
                    var bounds = bounds(controller, layout, machineId);
                    int egg = sapling ? bounds != null && bounds.nearOutside(pos.getX(), pos.getY(), pos.getZ()) ? 92 : 0
                            : Hk3EggMachineBoundaryFacts.caseFor(blockId, machineId, controller.isFormed(), state.hasError(),
                                    bounds, pos.getX(), pos.getY(), pos.getZ());
                    if (egg != 0) {
                        Hk3EggVanilla.caseEvent(player, egg);
                        return;
                    }
                }
            }
    }

    private static Hk3EggMachineBoundaryFacts.Box bounds(MultiblockControllerMachine machine, String layout, String machineId) {
        if (!layout.equals("i14") && !layout.equals("i15") && !layout.equals("i16")) {
            Hk3LargeStructurePattern.Bounds box = machine.getMultiblockState().getMatchContext().get(Hk3LargeStructurePattern.BOUNDS_KEY);
            return box == null ? null : new Hk3EggMachineBoundaryFacts.Box(box.min().getX(), box.min().getY(), box.min().getZ(),
                    box.max().getX(), box.max().getY(), box.max().getZ());
        }
        // 仅首次读取三份轻量元数据；不解压建筑体素，也不持有世界或控制器。
        var geometry = GEOMETRY.computeIfAbsent(layout, key -> read(key, machineId));
        if (geometry.isEmpty()) return null;
        var data = geometry.get();
        var pos = machine.getPos();
        return transform(data.size(), data.controller(), pos, machine.getFrontFacing(), machine.getUpwardsFacing(), machine.isFlipped());
    }

    public static Hk3EggMachineBoundaryFacts.Box transform(int[] size, int[] control, BlockPos origin,
                                                         Direction front, Direction upwards, boolean flipped) {
        if (size.length != 3 || control.length != 3 || upwards.getAxis().isVertical())
            throw new IllegalArgumentException("设备边界坐标无效");
        for (int axis = 0; axis < 3; axis++)
            if (size[axis] <= 0 || control[axis] < 0 || control[axis] >= size[axis])
                throw new IllegalArgumentException("设备边界尺寸无效");
        Direction right = RelativeDirection.RIGHT.getRelativeFacing(front, upwards, flipped);
        Direction up = RelativeDirection.UP.getRelativeFacing(front, upwards, flipped);
        Direction back = RelativeDirection.BACK.getRelativeFacing(front, upwards, flipped);
        var first = origin.relative(right, -control[0]).relative(up, -control[1]).relative(back, -control[2]);
        var last = origin.relative(right, size[0] - 1 - control[0]).relative(up, size[1] - 1 - control[1])
                .relative(back, size[2] - 1 - control[2]);
        return new Hk3EggMachineBoundaryFacts.Box(Math.min(first.getX(), last.getX()), Math.min(first.getY(), last.getY()),
                Math.min(first.getZ(), last.getZ()), Math.max(first.getX(), last.getX()), Math.max(first.getY(), last.getY()),
                Math.max(first.getZ(), last.getZ()));
    }

    private static Optional<Geometry> read(String layout, String machineId) {
        try (var input = Hk3EggMachineBoundaries.class.getResourceAsStream("/data/hk3gtl/structures/approved/" + layout + ".json")) {
            if (input == null) throw new IllegalStateException("缺少批准设备边界元数据");
            JsonObject metadata = JsonParser.parseReader(new InputStreamReader(input, StandardCharsets.UTF_8)).getAsJsonObject();
            if (!machineId.equals(metadata.get("machine").getAsString())) throw new IllegalStateException("设备身份与批准边界不符");
            var size = metadata.getAsJsonArray("size_xyz");
            var controller = metadata.getAsJsonArray("controller");
            if (size.size() != 3 || controller.size() != 3) throw new IllegalStateException("设备边界坐标不完整");
            var geometry = new Geometry(new int[]{size.get(0).getAsInt(), size.get(1).getAsInt(), size.get(2).getAsInt()},
                    new int[]{controller.get(0).getAsInt(), controller.get(1).getAsInt(), controller.get(2).getAsInt()});
            transform(geometry.size(), geometry.controller(), BlockPos.ZERO, Direction.NORTH, Direction.NORTH, false);
            return Optional.of(geometry);
        } catch (Exception failure) {
            com.mojang.logging.LogUtils.getLogger().warn("[HK3GTL] 彩蛋设备边界不可用，保持条目休眠。id={}", layout, failure);
            return Optional.empty();
        }
    }
}
