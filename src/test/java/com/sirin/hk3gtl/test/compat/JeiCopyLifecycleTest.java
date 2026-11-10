package com.sirin.hk3gtl.test.compat;

import com.sirin.hk3gtl.client.compat.Hk3JeiLifecyclePlugin;
import com.sirin.hk3gtl.mixin.JeiCopyItemHandlerMixin;
import mezz.jei.api.runtime.IJeiRuntime;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import java.lang.reflect.Proxy;

/**
 * 【文件职责】直接执行复制监听守卫，检验JEI生命周期改变时的取消与放行。
 * 【变更记录 #1】2026-09-30 01:28:26（第1次备注 · 内测5修订105）
 * - 删除：无。新增：启动、就绪、卸载、重复卸载、恢复与空运行时检查。
 * - 修改：纳入构建检查，不启动游戏或触碰剪贴板。
 * - 用途：防止复制永久禁用或退出后仍放行；不替代实例Mixin注入验收。
 */
public final class JeiCopyLifecycleTest {
    public static void main(String[] args) throws Exception {
        var plugin = new Hk3JeiLifecyclePlugin();
        check(true, "首次启动");
        IJeiRuntime runtime = (IJeiRuntime) Proxy.newProxyInstance(
                IJeiRuntime.class.getClassLoader(), new Class<?>[]{IJeiRuntime.class},
                (proxy, method, values) -> { throw new AssertionError("不得读取运行时内部数据"); });
        plugin.onRuntimeAvailable(runtime);
        check(false, "运行时就绪");
        plugin.onRuntimeUnavailable();
        check(true, "退出或重载");
        plugin.onRuntimeUnavailable();
        check(true, "重复卸载");
        plugin.onRuntimeAvailable(runtime);
        check(false, "再次进入或重载完成");
        plugin.onRuntimeAvailable(null);
        check(true, "无效空运行时");
        System.out.println("JEI复制守卫：六项生命周期回归通过；游戏内注入待验收");
    }

    private static void check(boolean expectedCancellation, String stage) throws Exception {
        var method = JeiCopyItemHandlerMixin.class.getDeclaredMethod(
                "hk3gtl$guardJeiLifecycle", CallbackInfo.class);
        method.setAccessible(true);
        var callback = new CallbackInfo("onKeyInput", true);
        method.invoke(null, callback);
        if (callback.isCancelled() != expectedCancellation) throw new AssertionError(stage);
    }
}
