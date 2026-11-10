package com.sirin.hk3gtl.mixin;

/** 【变更记录 #3】2026-09-29 19:50:20（内测5修订99）：删除：机器输出后的贸易电压记账回调；新增：无；修改：按负责人决定撤下五方贸易；用途：保留其他系统独立运行。 */
import com.gregtechceu.gtceu.api.machine.feature.IRecipeLogicMachine;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.sirin.hk3gtl.common.machine.research.Hk3HonkaiAbsorptionMachine;
import org.gtlcore.gtlcore.api.recipe.RecipeRunnerHelper;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** 中文说明：该处说明已按当前代码行为整理。*/
/** 中文说明：该处说明已按当前代码行为整理。*/
/**
 * 【变更记录 #1】2026-09-24 17:22:00（内测5修订66）
 * 删除：无；保留采样塔及光谱阵列原有回调。
 * 新增：液态工业设备的真实输出成功回调，失败和模拟操作不授予实验或网络能量。
 * 修改：在GTL输出助手返回true后通知设备，由设备按持久化批次标志防止重复结算。
 * 用途：与GTL直接输出调用保持一致，避免错误使用其输入方法导致机器卡住。
 */
/** 【变更记录 #2】2026-09-29 19:19:27（内测5修订96）：新增已绑定机器成功输出后的电压制作记账；失败、模拟输出和无归属机器不计。 */
@Mixin(value=RecipeRunnerHelper.class, remap=false)
/** 【变更记录 #4】2026-10-01 04:24:23（修订128）：删除：旧固定上限或被替代的分支；新增/修改：复用GTL真实输出成功返回，工业收藏明确拒绝概率未证实产物及虚空输出；用途：已审核彩蛋独立执行，不授研究或审查资格。 */
public abstract class Hk3ResearchOutputMixin {
    /** 仅服务端真实成功输出触发；各设备负责检查归属、研究及批次幂等性。 */
    @Inject(method="handleRecipeOutput(Lcom/gregtechceu/gtceu/api/machine/feature/IRecipeLogicMachine;Lcom/gregtechceu/gtceu/api/recipe/GTRecipe;)Z",
            at=@At("RETURN"), remap=false, require=1)
    private static void hk3gtl$recordSampling(IRecipeLogicMachine machine, GTRecipe recipe, CallbackInfoReturnable<Boolean> result) {
        if(Boolean.TRUE.equals(result.getReturnValue()))com.sirin.hk3gtl.common.easter.Hk3EggProduction.settled(machine,recipe);
        if (Boolean.TRUE.equals(result.getReturnValue()) && machine instanceof Hk3HonkaiAbsorptionMachine tower)
            tower.onSamplingOutputSettled(recipe);
        if (Boolean.TRUE.equals(result.getReturnValue())
                && machine instanceof com.sirin.hk3gtl.common.machine.research.Hk3SpectrumAnalysisMachine analyzer)
            analyzer.onSpectrumOutputSettled(recipe);
        if (Boolean.TRUE.equals(result.getReturnValue())
                && machine instanceof com.sirin.hk3gtl.common.machine.research.Hk3LiquidProcessMachine process)
            process.onLiquidOutputSettled(recipe);
    }
}
