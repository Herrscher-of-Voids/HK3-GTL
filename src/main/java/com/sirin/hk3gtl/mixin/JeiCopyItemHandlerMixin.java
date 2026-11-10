package com.sirin.hk3gtl.mixin;

import com.sirin.hk3gtl.client.compat.Hk3JeiLifecyclePlugin;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * 【文件职责】仅在安装JEI复制附属时，守卫其按键监听入口。
 * 【变更记录 #1】2026-09-30 01:28:26（第1次备注 · 内测5修订105）
 * - 删除：无，保留附属原有复制逻辑。
 * - 新增：JEI未就绪时提前结束本监听器，不取消Forge键盘事件。
 * - 修改：创建世界、退回菜单和重载期间不读取不存在的JEI运行时；就绪后原样执行。
 * - 用途：修复1.1.2-fix4复制插件在CreateWorldScreen按键时的崩溃，普通输入仍可继续。
 */
@Pseudo
@Mixin(targets = "net.yiran.jcrj.CopyItemHandler", remap = false)
public abstract class JeiCopyItemHandlerMixin {
    @Inject(method = "onKeyInput(Lnet/minecraftforge/client/event/ScreenEvent$KeyPressed$Pre;)V",
            at = @At("HEAD"), cancellable = true, remap = false)
    private static void hk3gtl$guardJeiLifecycle(CallbackInfo callback) {
        if (!Hk3JeiLifecyclePlugin.isRuntimeAvailable()) callback.cancel();
    }
}
