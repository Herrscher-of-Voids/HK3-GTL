package com.sirin.hk3gtl.mixin.enhanced;

import com.gtl.enhancedcore.common.world.plot.PlotChunkGenerator;
import net.minecraft.world.level.block.state.BlockState;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.gen.Invoker;

@Pseudo
@Mixin(value = PlotChunkGenerator.class, remap = false)
public interface Hk3CampusMaterialAccess {
    @Invoker("resolveCampusMaterial")
    static BlockState hk3gtl$resolve(String block) {
        throw new AssertionError();
    }
}
