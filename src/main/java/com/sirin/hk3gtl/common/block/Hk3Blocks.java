package com.sirin.hk3gtl.common.block;


/**
 * 【文件职责】
 * - 维护 Hk3Blocks 的核心功能实现。
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
/**
 * 【变更记录 #1】2026-09-29 18:22:20（内测5修订94）
 * - 删除：无；保留历史代码与数据入口。
 * - 新增：五方贸易服务端结算支持及失败校验。
 * - 修改：注册独立T02贸易终端及方块实体；不替换旧量子贸易港及其研究。
 * - 用途：执行一次性交齐与交付前无损取消；报价未审核不开放，不授予研究完成。
 */
/** 【变更记录 #2】2026-09-29 19:50:20（内测5修订99）：删除：T02方块及方块实体注册；新增：无；修改：按负责人决定撤下五方贸易；用途：保留其他系统独立运行。 */
import com.sirin.hk3gtl.common.constants.Hk3Constants;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;
import org.slf4j.Logger;
import com.mojang.logging.LogUtils;

/**
 * 方块注册总入口。持有全局方块/方块物品 DeferredRegister，所有子模块通过此处注册。
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>新增方块子模块：在 {@link #register()} 中调用对应类的 register()</li>
 *   <li>所有方块通过 {@link #registerBlock} 同时注册方块+对应的 BlockItem</li>
 *   <li>注册ID必须全小写下划线，如 {@code casing_abyss_energy}</li>
 *   <li>方块贴图：{@code assets/hk3gtl/textures/block/<注册ID>.png}</li>
 *   <li>方块模型：{@code assets/hk3gtl/models/block/<注册ID>.json}（机壳用 cube_all）</li>
 *   <li>方块状态：{@code assets/hk3gtl/blockstates/<注册ID>.json}</li>
 *   <li>物品模型：{@code assets/hk3gtl/models/item/<注册ID>.json}</li>
 * </ul>
 *
 * @see CasingBlocks 机壳方块
 * @see StructureBlocks 结构方块（玻璃/线圈/冷却/通讯/数据柱）
 */
/** 中文说明：该处说明已按当前代码行为整理。*/
public class Hk3Blocks {

    private static final Logger LOGGER = LogUtils.getLogger();

    /** 全局方块 DeferredRegister */
    public static final DeferredRegister<Block> BLOCKS =
            DeferredRegister.create(ForgeRegistries.BLOCKS, Hk3Constants.MOD_ID);

    /** 全局方块物品 DeferredRegister（与 BLOCKS 一一对应） */
    public static final DeferredRegister<Item> BLOCK_ITEMS =
            DeferredRegister.create(ForgeRegistries.ITEMS, Hk3Constants.MOD_ID);

    /**
     * 注册方块并自动创建对应的 BlockItem。
     * @param name 注册ID（全小写下划线）
     * @param blockSupplier 方块工厂
     * @return 方块的 RegistryObject
     */
    public static RegistryObject<Block> registerBlock(String name,
                                                      java.util.function.Supplier<Block> blockSupplier) {
        RegistryObject<Block> block = BLOCKS.register(name, blockSupplier);
        BLOCK_ITEMS.register(name, () -> new BlockItem(block.get(), new Item.Properties()));
        return block;
    }

    /** 统一注册入口，由 Hk3Gtl 构造函数调用 */
    public static void register() {
        LOGGER.info("[HK3GTL] 开始注册自定义方块...");

        com.sirin.hk3gtl.common.registration.Hk3IndustrialContent.registerBlocks();
        CasingBlocks.register();       // 机壳方块
        StructureBlocks.register();    // 结构方块

        LOGGER.info("[HK3GTL] 自定义方块注册完成。");
    }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
