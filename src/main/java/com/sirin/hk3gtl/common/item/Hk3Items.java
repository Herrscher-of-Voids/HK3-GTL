package com.sirin.hk3gtl.common.item;



import com.sirin.hk3gtl.common.constants.Hk3Constants;
import com.sirin.hk3gtl.common.item.abyss.AbyssCircuitItems;
import com.sirin.hk3gtl.common.item.abyss.AbyssComponentItems;
import com.sirin.hk3gtl.common.item.abyss.AbyssFunctionalItems;
import com.sirin.hk3gtl.common.item.finality.FinalityCircuitItems;
import com.sirin.hk3gtl.common.item.finality.FinalityComponentItems;
import com.sirin.hk3gtl.common.item.honkai.HonkaiMaterialItems;
import com.sirin.hk3gtl.common.item.imaginary.ImaginaryCircuitItems;
import com.sirin.hk3gtl.common.item.imaginary.ImaginaryComponentItems;
import com.sirin.hk3gtl.common.item.quantum.QuantumCircuitItems;
import com.sirin.hk3gtl.common.item.quantum.QuantumComponentItems;
import com.sirin.hk3gtl.common.item.soulium.SouliumChainItems;
import net.minecraft.world.item.Item;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;
import org.slf4j.Logger;
import com.mojang.logging.LogUtils;

/**
 * 物品注册总入口。持有全局 DeferredRegister，所有子模块通过此处注册。
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>新增物品子模块：在 {@link #register()} 中调用对应类的 register/init</li>
 *   <li>注册顺序：先 register()（真实注册），后 init()（桥接别名），不可颠倒</li>
 *   <li>所有物品共用 {@link #ITEMS}，注册ID必须全小写下划线</li>
 * </ul>
 *
 * @see Hk3CircuitItems 电路统一注册（崩坏能电路 + 64级细分电路）
 * @see HonkaiMaterialItems 崩坏能体系材料
 */
public class Hk3Items {

    private static final Logger LOGGER = LogUtils.getLogger();

    /** 全局物品 DeferredRegister，所有子模块物品均通过此实例注册 */
    public static final DeferredRegister<Item> ITEMS =
            DeferredRegister.create(ForgeRegistries.ITEMS, Hk3Constants.MOD_ID);

    /**
     * 统一注册入口，由 Hk3Gtl 构造函数调用。
     * <p>注册分两阶段：①各模块 register() 注册真实物品 → ②电路别名 init() 绑定引用。
     * 新增子模块时务必按此顺序插入。</p>
     */
    public static void register() {
        LOGGER.info("[HK3GTL] 开始注册自定义物品...");

        // ── 阶段1：注册真实物品（DeferredRegister.register）──
        HonkaiMaterialItems.register();       // 崩坏能体系材料
        SouliumChainItems.register();          // 魂钢工业链中间件
        AbyssComponentItems.register();        // 海渊 I~IV 八大件
        ImaginaryComponentItems.register();    // 虚数 I~IV 八大件
        QuantumComponentItems.register();      // 量子 I~IV 八大件
        FinalityComponentItems.register();     // 终焉 I~IV 八大件
        Hk3CircuitItems.register();            // 崩坏能电路 + 64级细分电路
        EasterEggItems.register();             // 彩蛋类物品（非酋证书等）

        // ── 阶段2：桥接别名（从 Hk3CircuitItems 取已注册的 processor 变体）──
        AbyssCircuitItems.init();              // 海渊电路别名
        ImaginaryCircuitItems.init();          // 虚数电路别名
        QuantumCircuitItems.init();            // 量子电路别名
        FinalityCircuitItems.init();           // 终焉电路别名

        // ── 阶段3：功能性物品 ──
        AbyssFunctionalItems.register();       // 海渊阶段功能性中间件

        // ── 阶段4：开发调试工具 ──
        STRUCTURE_EXPORT_WAND = ITEMS.register("structure_export_wand",
                () -> new StructureExportWand(new Item.Properties().stacksTo(1)));

        // ── 阶段5：叙事系统入口物品 ──
        NARRATIVE_CODEX = ITEMS.register("narrative_codex",
                () -> new NarrativeCodexItem(new Item.Properties().stacksTo(1).rarity(net.minecraft.world.item.Rarity.UNCOMMON)));

        LOGGER.info("[HK3GTL] 自定义物品注册完成。");
    }

    /**
     * 多方块结构导出棒 — 开发期工具，用于配合 {@code /hk3export} 命令导出多方块 Pattern。
     * 堆叠上限 1，作为工具类物品单独注册，不参与配方。
     */
    public static RegistryObject<Item> STRUCTURE_EXPORT_WAND;

    /**
     * 文明档案卷轴 — 世界文本叙事系统（需求 1）的玩家入口物品。
     * <p>右键查看已解锁叙事节点列表；潜行右键显示总进度。</p>
     * <p>GUI 查看器将在后续版本上线，当前阶段以聊天栏输出为主。</p>
     */
    public static RegistryObject<Item> NARRATIVE_CODEX;
}