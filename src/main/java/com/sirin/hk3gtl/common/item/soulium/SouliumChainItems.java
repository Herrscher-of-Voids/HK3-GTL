package com.sirin.hk3gtl.common.item.soulium;


/**
 * 【文件职责】
 * - 注册或实现 SouliumChainItems 物品行为。
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
import com.sirin.hk3gtl.common.item.Hk3Items;
import net.minecraft.world.item.Item;
import net.minecraftforge.registries.RegistryObject;

/**
 * 魂钢工业链中间件物品注册。
 *
 * <p>魂钢冶铸链路（从原料到最终部件）：
 * <pre>
 *   前驱体混合物 → 激活纳米矩阵 → 魂钢原始团 → 稳定化魂钢原始团 → 定向魂钢组件
 * </pre>
 * 每个中间件作为前一步配方的输出、后一步配方的输入，构成多段魂钢冶铸流程。
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>新增中间件：追加字段 + {@link #register()} 中注册调用</li>
 *   <li>贴图路径：{@code assets/hk3gtl/textures/item/soulium/<注册ID>.png}</li>
 *   <li>语言 Key：{@code item.hk3gtl.<注册ID>}，同步更新 zh_cn.json / en_us.json</li>
 *   <li>此类替代早期材料注册类中的魂钢部分，
 *       禁止同时启用两者的 register()，否则 DeferredRegister 会报重复 ID</li>
 *   <li>禁止为魂钢材料添加 NO_SMELTING / NO_SMASHING 之外的简易加工；魂钢只能通过冶铸中心产出</li>
 * </ul>
 */
public class SouliumChainItems {

    /** 第 1 步产物：魂钢前驱体混合物 —— 原料初次混合。 */
    public static RegistryObject<Item> SOULIUM_PRECURSOR_MIX;
    /** 第 2 步产物：激活纳米矩阵 —— 催化纳米载体。 */
    public static RegistryObject<Item> ACTIVATED_NANO_MATRIX;
    /** 第 3 步产物：魂钢原始团 —— 未稳定的毛坯。 */
    public static RegistryObject<Item> SOULIUM_PROTO_MASS;
    /** 第 4 步产物：稳定化魂钢原始团 —— 经过稳定处理。 */
    public static RegistryObject<Item> STABILIZED_SOULIUM_PROTO_MASS;
    /** 第 5 步产物：定向魂钢组件 —— 最终可用于高阶合成的成品。 */
    public static RegistryObject<Item> ORIENTED_SOULIUM_COMPONENT;

    /**
     * 统一注册入口：在 {@link Hk3Items#ITEMS} 中注册全部 5 个链条中间件。
     * 由 mod 主类在 DeferredRegister 注册阶段调用。
     */
    public static void register() {
        SOULIUM_PRECURSOR_MIX = Hk3Items.ITEMS.register("soulium_precursor_mix",
                () -> new Item(new Item.Properties()));
        ACTIVATED_NANO_MATRIX = Hk3Items.ITEMS.register("activated_nano_matrix",
                () -> new Item(new Item.Properties()));
        SOULIUM_PROTO_MASS = Hk3Items.ITEMS.register("soulium_proto_mass",
                () -> new Item(new Item.Properties()));
        STABILIZED_SOULIUM_PROTO_MASS = Hk3Items.ITEMS.register("stabilized_soulium_proto_mass",
                () -> new Item(new Item.Properties()));
        ORIENTED_SOULIUM_COMPONENT = Hk3Items.ITEMS.register("oriented_soulium_component",
                () -> new Item(new Item.Properties()));
    }
}
