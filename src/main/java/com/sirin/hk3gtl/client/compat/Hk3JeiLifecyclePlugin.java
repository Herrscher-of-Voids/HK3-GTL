package com.sirin.hk3gtl.client.compat;

import mezz.jei.api.IModPlugin;
import mezz.jei.api.JeiPlugin;
import mezz.jei.api.runtime.IJeiRuntime;
import net.minecraft.resources.ResourceLocation;

/**
 * 【文件职责】通过JEI公开生命周期记录复制操作是否可以读取运行时，不保存运行时实例。
 * 【变更记录 #1】2026-09-30 01:28:26（第1次备注 · 内测5修订105）
 * - 删除：无。
 * - 新增：初始关闭、运行时就绪开启、运行时卸载关闭的客户端状态。
 * - 修改：复制插件兼容保护读取本状态，避免菜单和重载期间调用JEI内部取值器。
 * - 用途：保留世界内复制功能；不注册配方，不持有世界、玩家或JEI对象。
 */
@JeiPlugin
public final class Hk3JeiLifecyclePlugin implements IModPlugin {
    private static volatile boolean runtimeAvailable;

    @Override
    public ResourceLocation getPluginUid() {
        return new ResourceLocation("hk3gtl", "jei_copy_lifecycle");
    }

    @Override
    public void onRuntimeAvailable(IJeiRuntime runtime) {
        runtimeAvailable = runtime != null;
    }

    @Override
    public void onRuntimeUnavailable() {
        runtimeAvailable = false;
    }

    public static boolean isRuntimeAvailable() {
        return runtimeAvailable;
    }
}
