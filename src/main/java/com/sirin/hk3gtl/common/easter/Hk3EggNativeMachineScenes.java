package com.sirin.hk3gtl.common.easter;

import com.gregtechceu.gtceu.api.data.chemical.ChemicalHelper;
import com.gregtechceu.gtceu.api.data.tag.TagPrefix;
import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.gregtechceu.gtceu.api.machine.multiblock.MultiblockControllerMachine;
import com.gregtechceu.gtceu.api.pattern.MultiblockState;
import com.gregtechceu.gtceu.api.pattern.MultiblockWorldSavedData;
import com.gregtechceu.gtceu.common.machine.multiblock.electric.FusionReactorMachine;
import com.sirin.hk3gtl.common.machine.hyperion.Hk3HyperionMachine;
import com.sirin.hk3gtl.common.material.SouliumMaterial;
import com.sirin.hk3gtl.common.multiblock.pattern.Hk3LargeStructurePattern;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.FluidTags;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.vehicle.Boat;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;

import java.util.HashSet;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.BiPredicate;

/** 真实放船、放冰及旗舰交互的只读旁注；查询仅限已加载邻近区块索引。 */
public final class Hk3EggNativeMachineScenes {
    private static final AtomicLong LAST_FAILURE = new AtomicLong();

    private Hk3EggNativeMachineScenes() {}

    public static void boatSpawned(ServerPlayer player, Entity entity, boolean spawned) {
        if (!spawned || !(entity instanceof Boat boat) || !player.server.isSameThread()) return;
        optional(() -> {
            var level = player.serverLevel();
            if (boat.level() != level || boat.isRemoved() || level.getEntity(boat.getId()) != boat) return;
            var waterPos = BlockPos.containing(boat.getX(), Math.nextDown(boat.getY()), boat.getZ());
            if (!level.hasChunkAt(waterPos)) return;
            var fluid = level.getFluidState(waterPos);
            if (!Hk3EggNativeMachineFacts.waterSurface(fluid.is(FluidTags.WATER), boat.getY(), waterPos.getY(),
                    fluid.getHeight(level, waterPos))) return;
            var pos = boat.blockPosition();
            if (near(player, pos, 8, (machine, bounds) -> Hk3EggNativeMachineFacts.boat(true, true, true,
                    machine.getDefinition().getId().toString(), machine.isFormed(), machine.getMultiblockState().hasError(),
                    bounds, pos.getX(), pos.getY(), pos.getZ()))) Hk3EggVanilla.caseEvent(player, 91);
        });
    }

    public static void icePlaced(ServerPlayer player, BlockPos pos, BlockState block) {
        if (!block.is(Blocks.ICE) || !player.server.isSameThread()) return;
        optional(() -> {
            var level = player.serverLevel();
            if (!level.hasChunkAt(pos) || !level.getBlockState(pos).equals(block)) return;
            if (near(player, pos, 4, (machine, bounds) -> Hk3EggNativeMachineFacts.ice(true,
                    machine instanceof FusionReactorMachine, machine.isFormed(), machine.getMultiblockState().hasError(),
                    bounds, pos.getX(), pos.getY(), pos.getZ()))) Hk3EggVanilla.caseEvent(player, 95);
        });
    }

    public static void controllerUsed(ServerPlayer player, BlockPos pos, InteractionHand hand, boolean succeeded) {
        if (!succeeded || !player.server.isSameThread()) return;
        optional(() -> {
            var level = player.serverLevel();
            if (!level.hasChunkAt(pos)) return;
            var machine = MetaMachine.getMachine(level, pos);
            if (!(machine instanceof Hk3HyperionMachine)) return;
            var held = player.getItemInHand(hand);
            var ingot = ChemicalHelper.get(TagPrefix.ingot, SouliumMaterial.SOULIUM);
            if (Hk3EggNativeMachineFacts.flagship(succeeded, true, machine.getDefinition().getId().toString(),
                    !ingot.isEmpty() && held.is(ingot.getItem()), held.getCount())) Hk3EggVanilla.caseEvent(player, 96);
        });
    }

    private static boolean near(ServerPlayer player, BlockPos pos, int radius,
                                BiPredicate<MultiblockControllerMachine, Hk3EggNativeMachineFacts.Box> accepts) {
        var level = player.serverLevel();
        var saved = MultiblockWorldSavedData.getOrCreate(level);
        var seen = new HashSet<BlockPos>();
        for (int x = (pos.getX() - radius) >> 4; x <= (pos.getX() + radius) >> 4; x++)
            for (int z = (pos.getZ() - radius) >> 4; z <= (pos.getZ() + radius) >> 4; z++) {
                if (!level.hasChunk(x, z)) continue;
                for (var state : saved.getControllerInChunk(new ChunkPos(x, z))) {
                    if (!seen.add(state.controllerPos) || state.hasError() || !level.hasChunkAt(state.controllerPos)) continue;
                    var machine = MetaMachine.getMachine(level, state.controllerPos);
                    if (!(machine instanceof MultiblockControllerMachine controller) || !controller.isFormed()
                            || controller.getMultiblockState() != state) continue;
                    boolean quantum = Hk3EggNativeMachineFacts.QUANTUM_MACHINE.equals(controller.getDefinition().getId().toString());
                    if ((radius == 8 ? quantum : controller instanceof FusionReactorMachine)
                            && accepts.test(controller, bounds(state, quantum))) return true;
                }
            }
        return false;
    }

    private static Hk3EggNativeMachineFacts.Box bounds(MultiblockState state, boolean quantum) {
        Hk3LargeStructurePattern.Bounds box = state.getMatchContext().get(Hk3LargeStructurePattern.BOUNDS_KEY);
        if (box != null) return new Hk3EggNativeMachineFacts.Box(box.min().getX(), box.min().getY(), box.min().getZ(),
                box.max().getX(), box.max().getY(), box.max().getZ());
        if (quantum || state.cache.isEmpty()) return null;
        int minX = Integer.MAX_VALUE, minY = Integer.MAX_VALUE, minZ = Integer.MAX_VALUE;
        int maxX = Integer.MIN_VALUE, maxY = Integer.MIN_VALUE, maxZ = Integer.MIN_VALUE;
        for (long packed : state.cache) {
            var pos = BlockPos.of(packed);
            minX = Math.min(minX, pos.getX()); minY = Math.min(minY, pos.getY()); minZ = Math.min(minZ, pos.getZ());
            maxX = Math.max(maxX, pos.getX()); maxY = Math.max(maxY, pos.getY()); maxZ = Math.max(maxZ, pos.getZ());
        }
        return new Hk3EggNativeMachineFacts.Box(minX, minY, minZ, maxX, maxY, maxZ);
    }

    private static void optional(Runnable observation) {
        try { observation.run(); }
        catch (RuntimeException failure) {
            long now = System.nanoTime(), previous = LAST_FAILURE.get();
            if ((previous == 0 || now - previous >= 60_000_000_000L) && LAST_FAILURE.compareAndSet(previous, now))
                com.mojang.logging.LogUtils.getLogger().warn("[HK3GTL] 彩蛋设备旁注失败，原操作结果保留。", failure);
        }
    }
}
