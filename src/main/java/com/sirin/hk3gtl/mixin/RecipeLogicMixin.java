package com.sirin.hk3gtl.mixin;



import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.gregtechceu.gtceu.api.machine.trait.RecipeLogic;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.mojang.logging.LogUtils;
import com.sirin.hk3gtl.common.capability.Hk3DualEnergyCosts;
import com.sirin.hk3gtl.common.capability.IDualEnergyConsumer;
import com.sirin.hk3gtl.common.gaze.Hk3GazeManager;
import com.sirin.hk3gtl.common.machine.Hk3WorkableMultiblockMachine;
import com.sirin.hk3gtl.common.machine.imaginary.Hk3ImaginaryAnchor;
import com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate;
import com.sirin.hk3gtl.common.research.Hk3ResearchManager;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.slf4j.Logger;

import java.math.BigInteger;
import java.util.concurrent.atomic.AtomicLong;

@Mixin(value = RecipeLogic.class, remap = false)
public class RecipeLogicMixin {

    private static final Logger LOGGER = LogUtils.getLogger();
    private static final long HK3GTL$LOG_INTERVAL_NANOS = 10_000_000_000L;
    private static final AtomicLong HK3GTL$LAST_GUARD_LOG_NANOS = new AtomicLong();

    /**
     * 单一工作守卫入口。前三项只决定是否跳过，全部通过后才执行不可逆的崩坏能扣款。
     */
    @Inject(method = "handleRecipeWorking", at = @At("HEAD"), cancellable = true, require = 1)
    private void hk3gtl$applyWorkingGuards(CallbackInfo ci) {
        RecipeLogic self = (RecipeLogic) (Object) this;
        GTRecipe recipe = self.getLastRecipe();
        if (recipe == null) return;

        MetaMachine machine = self.getMachine();
        Level level = machine.getLevel();

        if (hk3gtl$blocksResearch(recipe, machine, level)
                || hk3gtl$throttlesWithoutAnchor(recipe, machine, level)
                || hk3gtl$throttlesByGaze(recipe, machine, level)
                || hk3gtl$blocksDualEnergy(recipe, machine, level)) {
            ci.cancel();
        }
    }

    private boolean hk3gtl$blocksResearch(GTRecipe recipe, MetaMachine machine, Level level) {
        try {
            String researchId = Hk3RecipeResearchGate.getRequiredResearch(recipe.id);
            if (researchId == null || level == null || level.isClientSide()) return false;

            ServerPlayer player;
            if (machine instanceof Hk3WorkableMultiblockMachine ownedMachine) {
                if (ownedMachine.getOwnerUUID() == null || level.getServer() == null) return true;
                player = level.getServer().getPlayerList().getPlayer(ownedMachine.getOwnerUUID());
            } else {
                player = hk3gtl$getNearestServerPlayer(level, machine.getPos());
            }
            return player == null || !Hk3ResearchManager.isCompleted(player, researchId);
        } catch (Exception exception) {
            hk3gtl$logGuardFailure("research_gate", exception);
            return true;
        }
    }

    private boolean hk3gtl$throttlesWithoutAnchor(GTRecipe recipe, MetaMachine machine, Level level) {
        try {
            if (recipe.recipeType == null || !Hk3ImaginaryAnchor.appliesTo(recipe.recipeType.registryName.toString())) {
                return false;
            }
            BlockPos pos = machine.getPos();
            if (level == null || level.isClientSide() || pos == null) return false;
            if (Hk3ImaginaryAnchor.hasActiveAnchorNearby(level, pos)) return false;

            // 无锚时偶数 tick 跳过，等效 50% 推进速度。
            return (level.getGameTime() & 1L) == 0L;
        } catch (Exception exception) {
            hk3gtl$logGuardFailure("imaginary_anchor", exception);
            return true;
        }
    }

    private boolean hk3gtl$throttlesByGaze(GTRecipe recipe, MetaMachine machine, Level level) {
        try {
            BlockPos pos = machine.getPos();
            if (level == null || level.isClientSide() || pos == null) return false;

            ServerPlayer player = hk3gtl$getNearestServerPlayer(level, pos);
            if (player == null) return false;

            double factor = hk3gtl$gazeMachineFactor(Hk3GazeManager.getEffectiveGaze(player));
            if (factor >= 0.999D) return false;

            long allow = Math.max(1L, Math.round(100L * factor));
            long phase = Math.floorMod(level.getGameTime() + pos.asLong(), 100L);
            return phase >= allow;
        } catch (Exception exception) {
            hk3gtl$logGuardFailure("gaze", exception);
            return true;
        }
    }

    private boolean hk3gtl$blocksDualEnergy(GTRecipe recipe, MetaMachine machine, Level level) {
        try {
            if (!(machine instanceof IDualEnergyConsumer consumer)) return false;
            if (level == null || level.isClientSide()) return false;

            BigInteger cost = Hk3DualEnergyCosts.getMergedCost(recipe);
            if (cost == null) {
                cost = BigInteger.valueOf(Hk3DualEnergyCosts.resolve(
                        recipe.id, machine.getDefinition().getId().getPath()));
            }
            return cost.signum() > 0 && !consumer.tryExtractHonkaiFromNetwork(cost);
        } catch (Exception exception) {
            hk3gtl$logGuardFailure("dual_energy", exception);
            return true;
        }
    }

    private static ServerPlayer hk3gtl$getNearestServerPlayer(Level level, BlockPos pos) {
        if (level == null || pos == null) return null;
        Player nearest = level.getNearestPlayer(
                pos.getX() + 0.5D,
                pos.getY() + 0.5D,
                pos.getZ() + 0.5D,
                64.0D,
                false);
        return nearest instanceof ServerPlayer player ? player : null;
    }

    private static double hk3gtl$gazeMachineFactor(int gaze) {
        if (gaze < 200) return 1.0D;
        if (gaze < 500) return 0.95D;
        if (gaze < 800) return 0.75D;
        if (gaze < 1000) return 0.60D;
        return 0.50D;
    }

    private static void hk3gtl$logGuardFailure(String stage, Exception exception) {
        long now = System.nanoTime();
        long previous = HK3GTL$LAST_GUARD_LOG_NANOS.get();
        if ((previous != 0L && now - previous < HK3GTL$LOG_INTERVAL_NANOS)
                || !HK3GTL$LAST_GUARD_LOG_NANOS.compareAndSet(previous, now)) {
            return;
        }
        LOGGER.warn("[HK3GTL] RecipeLogic 守卫异常，已取消当前 tick。stage={}, exceptionType={}, message={}",
                stage, exception.getClass().getName(), exception.getMessage());
    }
}
