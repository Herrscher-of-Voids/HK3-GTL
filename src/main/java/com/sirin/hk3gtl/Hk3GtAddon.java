package com.sirin.hk3gtl;



import com.gregtechceu.gtceu.api.addon.GTAddon;
import com.gregtechceu.gtceu.api.addon.IGTAddon;
import com.gregtechceu.gtceu.api.registry.registrate.GTRegistrate;
import com.sirin.hk3gtl.common.constants.Hk3Constants;
import com.sirin.hk3gtl.common.recipe.Hk3RecipeAdder;
import net.minecraft.data.recipes.FinishedRecipe;
import net.minecraft.resources.ResourceLocation;
import org.slf4j.Logger;
import com.mojang.logging.LogUtils;

import java.util.function.Consumer;

/**
 * GTCEu Addon 入口 — 通过 {@code @GTAddon} 注解被 GT 自动发现和回调。
 *
 * <h3>职责</h3>
 * <ul>
 *   <li>{@link #addRecipes} → 委托给 {@link Hk3RecipeAdder} 注册全部自定义配方</li>
 *   <li>{@link #removeRecipes} → 移除 GT 自动生成的魂钢加工配方（防止绕过自定义产线）</li>
 *   <li>{@link #getRegistrate} → 提供 GTRegistrate 实例给 GT 框架</li>
 * </ul>
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>新增配方 → 在 {@link com.sirin.hk3gtl.common.recipe.Hk3RecipeAdderImpl} 中添加</li>
 *   <li>新增移除配方 → 在 {@link #removeSouliumAutoRecipes} 的 patterns 数组中追加</li>
 *   <li>GT 回调时序: initializeAddon → addRecipes → removeRecipes</li>
 * </ul>
 */
@GTAddon
public class Hk3GtAddon implements IGTAddon {

    private static final Logger LOGGER = LogUtils.getLogger();

    /** 返回 GT 注册器实例，由 {@link Hk3Gtl#onMaterialRegistry} 中创建 */
    @Override
    public GTRegistrate getRegistrate() {
        return Hk3Gtl.REGISTRATE;
    }

    /** Addon 初始化回调（机器注册通过 Mixin 在 GTMachines.init 中完成） */
    @Override
    public void initializeAddon() {}

    /** 返回模组 ID，GT 框架用于资源定位 */
    @Override
    public String addonModId() {
        return Hk3Constants.MOD_ID;
    }

    /** GT 配方注册回调 — 委托给 Hk3RecipeAdder 统一注册 */
    @Override
    public void addRecipes(Consumer<FinishedRecipe> provider) {
        Hk3RecipeAdder.addRecipes(provider);
    }

    /** GT 配方移除回调 — 移除 GT 自动生成的魂钢加工配方 */
    @Override
    public void removeRecipes(Consumer<ResourceLocation> consumer) {
        LOGGER.info("[HK3GTL] 移除魂钢自动配方...");
        removeSouliumAutoRecipes(consumer);
        LOGGER.info("[HK3GTL] 魂钢自动配方移除完成。");
    }

    /**
     * 移除 GT 自动生成的魂钢加工配方。
     * 魂钢材料已设 NO_SMELTING + NO_SMASHING，此处兜底移除残留的自动配方。
     * 魂钢的板/线/箔/框架只能通过本模组自定义配方获取（海渊I级 EU/t）。
     *
     * 新增移除 → 在 patterns 数组中追加 "机器类型/配方名" 格式的字符串
     */
    private void removeSouliumAutoRecipes(Consumer<ResourceLocation> consumer) {
        String[] patterns = {
                "electric_blast_furnace/blast_soulium",
                "bender/plate_soulium",
                "bender/foil_soulium",
                "wiremill/fine_wire_soulium",
                "lathe/rod_soulium",
                "lathe/bolt_soulium",
                "assembler/frame_soulium",
                "extruder/plate_soulium",
                "extruder/rod_soulium",
                "extruder/ring_soulium",
                "extruder/gear_soulium",
                "extruder/gear_small_soulium",
                "extruder/bolt_soulium",
                "extruder/foil_soulium",
                "extruder/wire_soulium",
                "forge_hammer/plate_soulium",
        };

        for (String pattern : patterns) {
            consumer.accept(new ResourceLocation("gtceu", pattern));
        }
    }
}
