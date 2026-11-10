package com.sirin.hk3gtl.mixin.jei;
import mezz.jei.library.gui.recipes.RecipeLayout;
import net.minecraft.client.gui.GuiGraphics;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
@Mixin(value=RecipeLayout.class,remap=false)
/** 【变更记录 #1】2026-10-01 12:13:33（修订128）：删除：无；新增/修改：客户端JEI有效绘制回执；仅可选JEI存在时加载；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public abstract class Hk3EggJeiLayoutMixin {
    @Inject(method="drawRecipe",at=@At("RETURN"))private void hk3gtl$read(GuiGraphics graphics,int x,int y,CallbackInfo ci){com.sirin.hk3gtl.client.compat.Hk3EggJeiReading.draw((RecipeLayout<?>)(Object)this,x,y);}
}
