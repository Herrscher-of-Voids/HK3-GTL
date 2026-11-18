package com.sirin.hk3gtl.mixin;
import net.minecraft.world.level.block.SaplingBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.core.BlockPos;
import net.minecraft.util.RandomSource;
import net.minecraft.tags.*;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
@Mixin(SaplingBlock.class)

public abstract class Hk3EggSaplingMixin {
    @Unique private java.util.UUID hk3gtl$planter;
    @Inject(method="advanceTree",at=@At("HEAD"))private void hk3gtl$before(ServerLevel level,BlockPos pos,BlockState state,RandomSource random,CallbackInfo ci){hk3gtl$planter=null;if(!level.getBiome(pos).is(BiomeTags.IS_JUNGLE))return;hk3gtl$planter=com.sirin.hk3gtl.common.easter.Hk3EggBuildMemory.get(level).recordedOwner(pos,net.minecraft.core.registries.BuiltInRegistries.BLOCK.getKey(state.getBlock()).toString());}
    @Inject(method="advanceTree",at=@At("RETURN"))private void hk3gtl$after(ServerLevel level,BlockPos pos,BlockState state,RandomSource random,CallbackInfo ci){var owner=hk3gtl$planter;hk3gtl$planter=null;if(owner==null||!level.getBlockState(pos).is(BlockTags.LOGS))return;var p=level.getServer().getPlayerList().getPlayer(owner);if(p!=null&&p.serverLevel()==level)com.sirin.hk3gtl.common.easter.Hk3EggVanilla.caseEvent(p,450);}
}
