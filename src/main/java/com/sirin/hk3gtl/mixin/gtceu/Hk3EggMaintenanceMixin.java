package com.sirin.hk3gtl.mixin.gtceu;

import com.gregtechceu.gtceu.api.machine.feature.multiblock.IMaintenanceMachine;
import com.gregtechceu.gtceu.common.machine.multiblock.part.MaintenanceHatchPartMachine;
import com.sirin.hk3gtl.common.easter.Hk3EggRuntime;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin(value=MaintenanceHatchPartMachine.class,remap=false)
public abstract class Hk3EggMaintenanceMixin {
    @Unique private boolean hk3gtl$hadProblems;

    @Inject(method="fixMaintenanceProblems",at=@At("HEAD"))
    private void hk3gtl$beforeGuiRepair(Player player,CallbackInfo ci) {
        hk3gtl$hadProblems=((IMaintenanceMachine)this).hasMaintenanceProblems();
    }

    @Inject(method="fixMaintenanceProblems",at=@At("RETURN"))
    private void hk3gtl$afterGuiRepair(Player player,CallbackInfo ci) {
        hk3gtl$recordRepair(player);
    }

    @Inject(method="onUse",at=@At("HEAD"))
    private void hk3gtl$beforeHandRepair(BlockState state,Level level,BlockPos pos,Player player,
                                        InteractionHand hand,BlockHitResult hit,CallbackInfoReturnable<InteractionResult> cir) {
        hk3gtl$hadProblems=((IMaintenanceMachine)this).hasMaintenanceProblems();
    }

    @Inject(method="onUse",at=@At("RETURN"))
    private void hk3gtl$afterHandRepair(BlockState state,Level level,BlockPos pos,Player player,
                                       InteractionHand hand,BlockHitResult hit,CallbackInfoReturnable<InteractionResult> cir) {
        hk3gtl$recordRepair(player);
    }

    @Unique private void hk3gtl$recordRepair(Player player) {
        if (player instanceof ServerPlayer p && hk3gtl$hadProblems && !((IMaintenanceMachine)this).hasMaintenanceProblems())
            Hk3EggRuntime.state(p).putBoolean("socialDeviceRepaired",true);
    }
}
