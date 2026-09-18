package com.sirin.hk3gtl.common.block;



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

        CasingBlocks.register();       // 机壳方块
        StructureBlocks.register();    // 结构方块

        LOGGER.info("[HK3GTL] 自定义方块注册完成。");
    }
}
