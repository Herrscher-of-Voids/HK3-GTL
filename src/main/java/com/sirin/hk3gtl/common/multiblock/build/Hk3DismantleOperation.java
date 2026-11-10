package com.sirin.hk3gtl.common.multiblock.build;

import com.gregtechceu.gtceu.api.machine.MetaMachine;
import com.gregtechceu.gtceu.api.block.ActiveBlock;
import com.gregtechceu.gtceu.api.machine.feature.multiblock.IMultiPart;
import com.gregtechceu.gtceu.api.machine.feature.multiblock.IMultiController;
import com.gregtechceu.gtceu.api.machine.multiblock.MultiblockControllerMachine;
import com.gregtechceu.gtceu.api.pattern.MultiblockState;
import com.sirin.hk3gtl.mixin.gtceu.Hk3MultiblockStateAccess;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.common.ForgeHooks;
import org.gtlcore.gtlcore.common.item.UltimateTerminalBehavior.AutoBuildSetting;

/** 单格拆除事务；掉落按真实方块和实体计算，不使用蓝图物品或包围盒空气。 */
final class Hk3DismantleOperation {
    private final AutoBuildSetting setting;
    private final MultiblockControllerMachine controller;
    private final MultiblockState probe;
    private final ItemStack terminal, tool;
    private boolean removed;

    Hk3DismantleOperation(ServerPlayer player, MultiblockControllerMachine controller, AutoBuildSetting setting) {
        this.setting = setting;
        this.controller = controller;
        probe = new MultiblockState(player.serverLevel(),controller.getPos());
        terminal = player.getMainHandItem();
        tool = terminal.copy();
    }

    boolean matches(Hk3BuildPlan plan, int index, BlockPos pos, BlockState actual,
                    BlockState expected, Rotation rotation) {
        if (pos.equals(controller.getPos()) || actual.isAir()
                || setting.shouldPreserveDuringDismantle(actual.getBlock())) return false;
        var machine = MetaMachine.getMachine(probe.world,pos);
        if (machine instanceof IMultiController) return false;
        if (machine instanceof IMultiPart part) {
            if (plan.dismantlePort(index) == null || setting.isNoHatchMode()
                    || part.getControllers().stream().anyMatch(other -> other != controller)) return false;
            Direction face = plan.portFacing(index);
            if (face != null && machine.getFrontFacing() != rotation.rotate(face)) return false;
        }
        var predicate = plan.dismantlePort(index);
        if (predicate == null) return actual == expected || expected.getBlock() instanceof ActiveBlock active
                && actual == active.changeActive(expected,!active.isActive(expected));
        var access = (Hk3MultiblockStateAccess)(Object)probe;
        access.hk3gtl$clean();
        return access.hk3gtl$update(pos.immutable(),predicate) && predicate.test(probe);
    }

    boolean permitted(ServerPlayer player, BlockPos pos) {
        return !player.isSpectator() && player.getAbilities().mayBuild
                && player.serverLevel().mayInteract(player,pos)
                && player.serverLevel().getWorldBorder().isWithinBounds(pos)
                && player.mayUseItemAt(pos,Direction.UP,player.getMainHandItem())
                && player.serverLevel().getBlockState(pos).getDestroySpeed(player.serverLevel(),pos) >= 0
                && ForgeHooks.onBlockBreakEvent(player.serverLevel(),player.gameMode.getGameModeForPlayer(),player,pos) != -1;
    }

    boolean remove(ServerPlayer player, BlockPos pos, BlockState actual, Hk3BuildMaterials materials,
                   java.util.function.BooleanSupplier active) {
        var level = player.serverLevel();
        // 增强版终端在创造和生存均回收真实掉落，包含仓室自己的物品NBT；不凭蓝图生成物品。
        var entity = level.getBlockEntity(pos);
        var drops = Block.getDrops(actual,level,pos,entity,player,tool);
        if (!active.getAsBoolean() || level.getBlockState(pos) != actual || level.getBlockEntity(pos) != entity) return false;
        RuntimeException mutationFailure = null;
        try { level.setBlock(pos,Blocks.AIR.defaultBlockState(),Block.UPDATE_ALL); }
        catch (RuntimeException failure) { mutationFailure = failure; }
        // 移除回调可在方块已经消失后抛错；已确认的掉落仍须结算，原块仍在则不能发放。
        if (!level.getBlockState(pos).isAir()) {
            if (mutationFailure != null) throw mutationFailure;
            return false;
        }
        if (!removed) {
            removed = true;
            if (terminal.hasTag()) terminal.getTag().putBoolean("DismantleMode",false);
        }
        try { materials.deliver(drops); }
        catch (RuntimeException deliveryFailure) {
            if (mutationFailure != null) deliveryFailure.addSuppressed(mutationFailure);
            throw deliveryFailure;
        }
        if (mutationFailure != null) throw mutationFailure;
        return true;
    }
}
