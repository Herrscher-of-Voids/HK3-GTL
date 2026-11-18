package com.sirin.hk3gtl.mixin.enhanced;

import com.gtl.enhancedcore.common.world.plot.PlotChunkGenerator;
import com.gtl.enhancedcore.common.world.plot.PlotSettings;
import com.sirin.hk3gtl.common.campus.Hk3EnhancedCampusBridge;
import net.minecraft.world.level.StructureManager;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.ChunkAccess;
import net.minecraft.world.level.levelgen.RandomState;
import net.minecraft.world.level.levelgen.blending.Blender;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import java.util.concurrent.CompletableFuture;
import java.util.concurrent.Executor;

@Pseudo
@Mixin(value = PlotChunkGenerator.class, remap = false)
public abstract class Hk3CampusGeneratorMixin {
    @Shadow public abstract PlotSettings settings();

    @Inject(method = {"fillFromNoise", "m_213974_"}, at = @At("RETURN"), cancellable = true)
    private void hk3gtl$devices(Executor executor, Blender blender, RandomState random, StructureManager structures,
                               ChunkAccess chunk, CallbackInfoReturnable<CompletableFuture<ChunkAccess>> cir) {
        var settings = settings();
        cir.setReturnValue(cir.getReturnValue().thenApply(result -> {
            Hk3EnhancedCampusBridge.populate(settings, result);
            return result;
        }));
    }

    @Inject(method = "campusTerrain", at = @At("RETURN"), cancellable = true)
    private void hk3gtl$terrain(int x, int z, CallbackInfoReturnable<Boolean> cir) {
        if (!cir.getReturnValue() && Hk3EnhancedCampusBridge.expansion(settings()).terrainAt(x, z)) cir.setReturnValue(true);
    }

    @Inject(method = "stateAt", at = @At("HEAD"), cancellable = true)
    private void hk3gtl$materials(int x, int y, int z, CallbackInfoReturnable<BlockState> cir) {
        var block = Hk3EnhancedCampusBridge.blockState(settings(), x, y, z);
        if (block != null) cir.setReturnValue(block);
    }
}
