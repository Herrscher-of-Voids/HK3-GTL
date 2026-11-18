package com.sirin.hk3gtl.mixin.jei;
import mezz.jei.library.gui.recipes.RecipeLayout;
import net.minecraft.client.gui.GuiGraphics;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
@Mixin(value=RecipeLayout.class,remap=false)
 
public abstract class Hk3EggJeiLayoutMixin {
    @Inject(method="drawRecipe",at=@At("RETURN"))private void hk3gtl$read(GuiGraphics graphics,int x,int y,CallbackInfo ci){com.sirin.hk3gtl.client.compat.Hk3EggJeiReading.draw((RecipeLayout<?>)(Object)this,x,y);}
}
