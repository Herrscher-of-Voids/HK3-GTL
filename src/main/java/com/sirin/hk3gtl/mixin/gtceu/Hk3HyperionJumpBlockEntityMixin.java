package com.sirin.hk3gtl.mixin.gtceu;

import com.sirin.hk3gtl.common.machine.hyperion.Hk3HyperionJumpData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.block.entity.BlockEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(targets="net.minecraft.world.level.chunk.LevelChunk$BoundTickingBlockEntity")
public abstract class Hk3HyperionJumpBlockEntityMixin {
    @Shadow @Final private BlockEntity blockEntity;
    @Inject(method="tick",at=@At("HEAD"),cancellable=true)
    private void hk3gtl$pauseJump(CallbackInfo ci) {
        if(blockEntity.getLevel() instanceof ServerLevel level&&Hk3HyperionJumpData.locked(level,blockEntity.getBlockPos()))ci.cancel();
    }
}
