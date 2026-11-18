package com.sirin.hk3gtl.mixin.overview;

import com.gregtechceu.gtceu.api.machine.trait.RecipeLogic;
import net.minecraft.network.chat.Component;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

/**
 * 只读取GT实际保存的等待原因，不用等待标记笼统猜测缺电。
 */
@Mixin(value = RecipeLogic.class, remap = false)
public interface Hk3RecipeLogicOverviewAccessor {
    @Accessor("waitingReason") Component hk3gtl$waitingReason();
}
