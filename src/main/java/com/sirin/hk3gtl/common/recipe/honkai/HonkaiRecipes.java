package com.sirin.hk3gtl.common.recipe.honkai;



import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.machine.energy.Hk3HonkaiNetworkInjectorMachine;
import com.sirin.hk3gtl.common.material.Hk3Materials;
import com.sirin.hk3gtl.common.item.honkai.HonkaiMaterialItems;
import com.sirin.hk3gtl.common.recipe.Hk3RecipeTypesImpl;
import net.minecraft.data.recipes.FinishedRecipe;
import net.minecraft.world.item.ItemStack;

import java.util.function.Consumer;

/**
 * 崩坏能相关配方 —— 注册崩坏能吸收塔和崩坏能凝缩器的配方。
 *
 * <h3>职责</h3>
 * 提供崩坏能产业链的基础配方：原始崩坏粒子采集、粒子凝缩为结晶/液态崩坏能。
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>调整电压：修改 ABYSS_1_EUT / MAX_EUT 常量</li>
 *   <li>新增配方：在对应方法中调用 recipeBuilder().xxx.save()</li>
 *   <li>配方ID格式：直接使用描述性名称（如 "basic_absorption"）</li>
 *   <li>circuitMeta 用于区分同机器不同模式的配方</li>
 * </ul>
 */
public class HonkaiRecipes {

    /** 海渊I阶段基准电压（EU/t），来自 Hk3Values.VA_LONG */
    private static final long ABYSS_1_EUT = Hk3Values.VA_LONG[Hk3Tiers.ABYSS_1];
    /** MAX 电压（Tier 14）基准 EU/t */
    private static final long MAX_EUT = Hk3Values.VA_LONG[14];

    /** 注册崩坏能吸收塔配方：从虚空采集崩坏粒子（circuitMeta 区分基础/高级模式） */
    public static void addAbsorptionRecipes(Consumer<FinishedRecipe> provider) {
        Hk3RecipeTypesImpl.HONKAI_ABSORPTION_RECIPES.recipeBuilder("basic_absorption")
                .circuitMeta(1)
                .outputItems(new ItemStack(HonkaiMaterialItems.RAW_HONKAI_PARTICLE.get(), 256))
                .duration(800)
                .EUt(MAX_EUT)
                .save(provider);

        Hk3RecipeTypesImpl.HONKAI_ABSORPTION_RECIPES.recipeBuilder("advanced_absorption")
                .circuitMeta(2)
                .outputItems(new ItemStack(HonkaiMaterialItems.RAW_HONKAI_PARTICLE.get(), 1024))
                .duration(900)
                .EUt(MAX_EUT)
                .save(provider);
    }

    /**
     * 注册崩坏能网络注入器配方（双能源引擎 D-01 配套）。
     * <p>三条充网路线用编程电路区分，产出是无线网络余额（由
     * {@link com.sirin.hk3gtl.common.machine.energy.Hk3HonkaiNetworkInjectorMachine#afterWorking}
     * 结算），因此配方本身无物品/流体产出。</p>
     * <ul>
     *   <li>meta=1 液态路线：16000 mB = 16000 崩坏能（1:1，无损）</li>
     *   <li>meta=2 结晶路线：64 结晶 = 6400 崩坏能（1 结晶 = 100，便携高价）</li>
     *   <li>meta=3 纯EU路线：2000万 EU = 20000 崩坏能（1000:1，与全模组换算比一致）</li>
     * </ul>
     */
    public static void addNetworkInjectionRecipes(Consumer<FinishedRecipe> provider) {
        // 液态崩坏能 → 网络：16000 mB / 100 tick，处理耗电为象征性 ZPM 档
        Hk3RecipeTypesImpl.HONKAI_NETWORK_INJECTION_RECIPES.recipeBuilder("inject_liquid_honkai")
                .circuitMeta(1)
                .inputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(16000))
                .duration(100)
                .EUt(32768)
                .save(provider);
        Hk3HonkaiNetworkInjectorMachine.bindYield("honkai_network_injection", "inject_liquid_honkai", 16000L);

        // 崩坏能结晶 → 网络：64 结晶 / 60 tick
        Hk3RecipeTypesImpl.HONKAI_NETWORK_INJECTION_RECIPES.recipeBuilder("inject_honkai_crystal")
                .circuitMeta(2)
                .inputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 64))
                .duration(60)
                .EUt(32768)
                .save(provider);
        Hk3HonkaiNetworkInjectorMachine.bindYield("honkai_network_injection", "inject_honkai_crystal", 6400L);

        // 纯 EU → 网络：100万 EU/t × 20 tick = 2000万 EU → 20000 崩坏能（精确 1000:1）
        Hk3RecipeTypesImpl.HONKAI_NETWORK_INJECTION_RECIPES.recipeBuilder("inject_from_eu")
                .circuitMeta(3)
                .duration(20)
                .EUt(1_000_000)
                .save(provider);
        Hk3HonkaiNetworkInjectorMachine.bindYield("honkai_network_injection", "inject_from_eu", 20000L);
    }

    /** 注册崩坏能凝缩器配方：粒子转结晶(meta=1)或液态崩坏能(meta=2) */
    public static void addCondensationRecipes(Consumer<FinishedRecipe> provider) {
        Hk3RecipeTypesImpl.HONKAI_CONDENSATION_RECIPES.recipeBuilder("particle_to_crystal")
                .circuitMeta(1)
                .inputItems(new ItemStack(HonkaiMaterialItems.RAW_HONKAI_PARTICLE.get(), 2048))
                .outputItems(new ItemStack(HonkaiMaterialItems.HONKAI_ENERGY_CRYSTAL.get(), 64))
                .duration(600)
                .EUt(ABYSS_1_EUT)
                .save(provider);

        Hk3RecipeTypesImpl.HONKAI_CONDENSATION_RECIPES.recipeBuilder("particle_to_liquid")
                .circuitMeta(2)
                .inputItems(new ItemStack(HonkaiMaterialItems.RAW_HONKAI_PARTICLE.get(), 2048))
                .outputFluids(Hk3Materials.LIQUID_HONKAI_ENERGY.getFluid(2304))
                .duration(400)
                .EUt(ABYSS_1_EUT)
                .save(provider);
    }
}
