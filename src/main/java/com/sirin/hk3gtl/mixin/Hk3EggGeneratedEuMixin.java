package com.sirin.hk3gtl.mixin;
import com.gregtechceu.gtceu.api.machine.trait.NotifiableEnergyContainer;
import com.gregtechceu.gtceu.api.capability.IEnergyContainer;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
@Mixin(value=NotifiableEnergyContainer.class,remap=false)
/** 【变更记录 #1】2026-10-01 06:45:17（修订128）：删除：无；新增/修改：新增配方输出实际EU计量及只读阅读关闭回执，模拟与网络搬运均不计发电；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public abstract class Hk3EggGeneratedEuMixin {
    @Redirect(method="handleRecipeInner",at=@At(value="INVOKE",target="Lcom/gregtechceu/gtceu/api/capability/IEnergyContainer;addEnergy(J)J"))
    private long hk3gtl$actual(IEnergyContainer container,long amount){long actual=container.addEnergy(amount);if(amount>0&&actual>0)com.sirin.hk3gtl.common.easter.Hk3EggGeneration.accepted(actual);return actual;}
}
