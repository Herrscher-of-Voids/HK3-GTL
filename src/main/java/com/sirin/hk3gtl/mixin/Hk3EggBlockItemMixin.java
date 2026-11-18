package com.sirin.hk3gtl.mixin;
import com.sirin.hk3gtl.common.easter.Hk3EggVanilla;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.level.block.state.BlockState;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
@Mixin(BlockItem.class)
public abstract class Hk3EggBlockItemMixin {
    @Unique private final ThreadLocal<BlockState> hk3gtl$before= new ThreadLocal<>();
    @Inject(method="place",at=@At("HEAD"))
    private void hk3gtl$before(BlockPlaceContext c,CallbackInfoReturnable<InteractionResult> ci){if(c.getPlayer() instanceof ServerPlayer)hk3gtl$before.set(c.getLevel().getBlockState(c.getClickedPos()));}
    @Inject(method="place",at=@At("RETURN"))
    private void hk3gtl$after(BlockPlaceContext c,CallbackInfoReturnable<InteractionResult> ci){
        var before=hk3gtl$before.get();hk3gtl$before.remove();
        if(before!=null&&c.getPlayer() instanceof ServerPlayer p&&ci.getReturnValue().consumesAction())Hk3EggVanilla.queuePlacement(p,c.getClickedPos(),before,c.getLevel().getBlockState(c.getClickedPos()));
    }
}
