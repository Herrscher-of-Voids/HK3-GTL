package com.sirin.hk3gtl.mixin.ae;

import appeng.api.networking.pathing.ChannelMode;
import appeng.api.networking.pathing.ControllerState;
import appeng.me.Grid;
import appeng.me.service.PathingService;
import com.sirin.hk3gtl.common.integration.ae.nexus.network.Hk3NexusGrid;
import org.objectweb.asm.Opcodes;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

@Mixin(value = PathingService.class, remap = false)
public abstract class Hk3NexusPathingMixin {
    @Shadow @Final private Grid grid;
    @Shadow private ChannelMode channelMode;
    @Shadow private ControllerState controllerState;

    @Redirect(method = {"calculateAdHocChannels", "getChannelMode"}, at = @At(value = "FIELD", opcode = Opcodes.GETFIELD,
            target = "Lappeng/me/service/PathingService;channelMode:Lappeng/api/networking/pathing/ChannelMode;"))
    private ChannelMode hk3gtl$nexusChannels(PathingService service) {
        return Hk3NexusGrid.contains(grid) ? ChannelMode.INFINITE : channelMode;
    }

    @Redirect(method = {"onServerEndTick", "getControllerState"}, at = @At(value = "FIELD", opcode = Opcodes.GETFIELD,
            target = "Lappeng/me/service/PathingService;controllerState:Lappeng/api/networking/pathing/ControllerState;"))
    private ControllerState hk3gtl$nexusPathing(PathingService service) {
        return Hk3NexusGrid.contains(grid) ? ControllerState.NO_CONTROLLER : controllerState;
    }
}
