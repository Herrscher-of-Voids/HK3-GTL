package com.sirin.hk3gtl.client.compat;

import mezz.jei.api.IModPlugin;
import mezz.jei.api.JeiPlugin;
import mezz.jei.api.constants.VanillaTypes;
import mezz.jei.api.runtime.IJeiRuntime;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;

import java.util.List;

/**
 * 通过JEI公开生命周期记录复制操作是否可以读取运行时，不保存运行时实例。
 */
@JeiPlugin
public final class Hk3JeiLifecyclePlugin implements IModPlugin {
    private static volatile boolean runtimeAvailable;
    private static IJeiRuntime runtime;
    private static boolean institutesHidden;

    @Override
    public ResourceLocation getPluginUid() {
        return new ResourceLocation("hk3gtl", "jei_copy_lifecycle");
    }

    @Override
    public void onRuntimeAvailable(IJeiRuntime runtime) {
        Hk3JeiLifecyclePlugin.runtime = runtime;
        runtimeAvailable = runtime != null;
        refreshResearchVisibility();
    }

    @Override
    public void onRuntimeUnavailable() {
        runtime = null;
        runtimeAvailable = false;
        institutesHidden = false;
    }

    public static boolean isRuntimeAvailable() {
        return runtimeAvailable;
    }

    public static void refreshResearchVisibility() {
        if (runtime == null) return;
        boolean hide = !com.sirin.hk3gtl.common.config.Hk3ResearchSettings.enabled();
        if (hide == institutesHidden) return;
        List<ItemStack> stacks = com.sirin.hk3gtl.common.config.Hk3ResearchInstituteVisibility.ids().stream()
                .map(BuiltInRegistries.ITEM::get)
                .filter(item -> item != net.minecraft.world.item.Items.AIR)
                .map(ItemStack::new)
                .toList();
        if (hide) runtime.getIngredientManager().removeIngredientsAtRuntime(VanillaTypes.ITEM_STACK, stacks);
        else runtime.getIngredientManager().addIngredientsAtRuntime(VanillaTypes.ITEM_STACK, stacks);
        institutesHidden = hide;
    }
}
