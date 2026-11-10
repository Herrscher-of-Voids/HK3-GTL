package com.sirin.hk3gtl.mixin;


/**
 * 【文件职责】
 * - 处理 GTMachinesMixin 的 Mixin 注入逻辑。
 * - 关键调用链：由上层系统入口调用 -> 本文件核心方法 -> 下游模块。
 *
 * 【变更记录】2026-05-19
 * - 删除：
 *   1) 初始归档备注：自 v0.3 基线梳理，无本次 diff。
 * - 新增：
 *   1) 新增统一变更备注块，便于后续维护与审计追踪。
 * - 修改：
 *   1) 未改动业务逻辑，仅补充文件级职责与维护注释模板。
 * - 用途：
 *   1) 帮助维护者快速理解文件职责、变更背景与风险点。
 *
 * 【段内说明】
 * - 复杂方法补充“干什么 / 边界 / 线程侧”精简中文注释。
 */
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
