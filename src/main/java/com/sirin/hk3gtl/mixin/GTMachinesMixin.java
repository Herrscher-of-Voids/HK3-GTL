package com.sirin.hk3gtl.mixin;



import com.gregtechceu.gtceu.common.data.GTMachines;
import com.sirin.hk3gtl.common.data.Hk3Machines;
import org.gtlcore.gtlcore.common.data.GTLMachines;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * 搭车到 GTLMachines.init() 的 TAIL 注入。
 * GTLCore 的 GTMachinesMixin 会取消 GTMachines.init() 的原始执行，
 * 因此我们不能注入到 GTMachines.init()。
 * 改为注入 GTLMachines.init() 的末尾，此时注册表仍然开放。
 */
@Mixin(value = GTLMachines.class, remap = false)
public class GTMachinesMixin {

    @Inject(method = "init", at = @At("TAIL"), require = 1)
    private static void hk3gtl$registerMachines(CallbackInfo ci) {
        Hk3Machines.init();
    }
}
