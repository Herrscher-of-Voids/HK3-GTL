package com.sirin.hk3gtl.common.material;



import com.gregtechceu.gtceu.api.data.chemical.material.Material;
import com.gregtechceu.gtceu.api.data.chemical.material.info.MaterialIconSet;
import net.minecraft.resources.ResourceLocation;

import static com.gregtechceu.gtceu.api.data.chemical.material.info.MaterialFlags.*;
import static com.sirin.hk3gtl.common.constants.Hk3Constants.MOD_ID;

/**
 * 魂钢（Soulium）材料定义 —— 基于 GT CEu {@link Material.Builder} 的模组专有材料。
 *
 * <h3>设计要点</h3>
 * <ul>
 *   <li>不设 {@code blastTemp} → GT 不会自动生成 EBF（电弧炉）配方</li>
 *   <li>{@code NO_SMELTING} → GT 不会自动生成普通熔炉配方</li>
 *   <li>{@code NO_SMASHING} → 禁止用锤子简易加工；强制走工业线路</li>
 *   <li>魂钢锭唯一获取途径：魂钢冶铸中心多方块机器产出，保证进度门槛</li>
 * </ul>
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>修改颜色：{@link Material.Builder#color(int)} / {@code secondaryColor}</li>
 *   <li>新增衍生形态：在 {@code flags(...)} 中追加 GENERATE_XXX 常量（来自 MaterialFlags）</li>
 *   <li><b>严禁</b>移除 NO_SMELTING / NO_SMASHING：会导致玩家用炉子 / 锤子绕过冶铸中心</li>
 *   <li>新增材料应另建类，不要塞进本文件（保持单一职责）</li>
 *   <li>修改后需同步更新 zh_cn.json / en_us.json 中的 {@code material.soulium} 条目</li>
 *   <li>贴图由 iconSet 决定，METALLIC 使用 GT 原版金属贴图集</li>
 * </ul>
 */
public class SouliumMaterial {

    /** 魂钢材料实例，注册后可通过 {@code SOULIUM.getProperties()} 或标签访问。 */
    public static Material SOULIUM;

    /**
     * 注册魂钢材料。
     * 必须在 GT 材料注册阶段（{@code MaterialRegistryEvent} 或其等价 hook）调用，否则会报找不到 registry。
     */
    public static void register() {
        SOULIUM = new Material.Builder(new ResourceLocation(MOD_ID + ":soulium"))
                .ingot()
                .fluid()
                .color(0xC0C8D0)
                .secondaryColor(0x8888A0)
                .iconSet(MaterialIconSet.METALLIC)
                .flags(
                        NO_SMELTING,
                        NO_SMASHING,
                        GENERATE_PLATE,
                        GENERATE_ROD,
                        GENERATE_LONG_ROD,
                        GENERATE_BOLT_SCREW,
                        GENERATE_GEAR,
                        GENERATE_SMALL_GEAR,
                        GENERATE_RING,
                        GENERATE_FOIL,
                        GENERATE_FINE_WIRE,
                        GENERATE_FRAME
                )
                .buildAndRegister();
    }
}
