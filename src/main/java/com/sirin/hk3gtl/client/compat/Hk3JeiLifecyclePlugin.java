package com.sirin.hk3gtl.client.compat;

import mezz.jei.api.IModPlugin;
import mezz.jei.api.JeiPlugin;
import mezz.jei.api.runtime.IJeiRuntime;
import net.minecraft.resources.ResourceLocation;

/**
 * 通过JEI公开生命周期记录复制操作是否可以读取运行时，不保存运行时实例。
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
