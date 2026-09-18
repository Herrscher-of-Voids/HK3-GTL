package com.sirin.hk3gtl.common.block;



import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraftforge.registries.RegistryObject;

/**
 * 所有阶段的机壳方块注册。
 * <p>
 * 【修改指南】
 * - 新增机壳：在对应阶段区域添加 static 字段 + 在 register() 中调用 casing("注册ID")
 * - 修改硬度/爆炸抗性：调整 casingProperties() 或 coloredCasingProperties() 中的数值
 * - 修改颜色机壳的 MapColor：修改 COLORED_CASINGS 数组中对应元素的 MapColor 参数
 * - 所有注册ID必须全小写下划线，与 blockstates / models / textures / lang 保持一致
 */
public class CasingBlocks {

    // ════════════════════════════════════════════
    // P1 基础 / 海渊阶段机壳（多方块结构主体方块）
    // 修改数值：不需要改这里，去 casingProperties() 调整
    // ════════════════════════════════════════════
    public static RegistryObject<Block> CASING_SOULIUM;              // 魂钢机壳
    public static RegistryObject<Block> CASING_REINFORCED_SOULIUM;   // 强化魂钢机壳
    public static RegistryObject<Block> CASING_ABYSS_MECHANICAL;     // 海渊机械机壳
    public static RegistryObject<Block> CASING_ABYSS_RESEARCH;       // 海渊科研机壳
    public static RegistryObject<Block> CASING_ABYSS_ENERGY;         // 海渊能源机壳

    // ════════════════════════════════════════════
    // 虚数阶段机壳（金色 + 黑色色调）
    // ════════════════════════════════════════════
    public static RegistryObject<Block> CASING_IMAGINARY_TREE;       // 虚数之树机壳
    public static RegistryObject<Block> CASING_IMAGINARY_LATTICE;    // 虚数晶格机壳
    public static RegistryObject<Block> CASING_IMAGINARY_CORE;       // 虚数核心机壳
    public static RegistryObject<Block> CASING_IMAGINARY_ANCHOR;     // 虚数锚定机壳
    public static RegistryObject<Block> CASING_IMAGINARY_WEAVE;      // 虚数编织机壳

    // ════════════════════════════════════════════
    // 量子阶段机壳（浅紫色 + 白色色调）
    // ════════════════════════════════════════════
    public static RegistryObject<Block> CASING_QUANTUM_SEA;          // 量子之海机壳
    public static RegistryObject<Block> CASING_QUANTUM_BUBBLE;       // 世界泡机壳
    public static RegistryObject<Block> CASING_QUANTUM_FLUX;         // 量子通量机壳
    public static RegistryObject<Block> CASING_QUANTUM_ENTANGLE;     // 量子纠缠机壳
    public static RegistryObject<Block> CASING_QUANTUM_SHIPBOARD;    // 量子舰载机壳

    // ════════════════════════════════════════════
    // 终焉阶段机壳（金色 + 白色 + 黑色，空之律者色调）
    // ════════════════════════════════════════════
    public static RegistryObject<Block> CASING_FINALITY_VOID;        // 终焉虚空机壳
    public static RegistryObject<Block> CASING_FINALITY_SANCTUM;     // 终焉圣殿机壳
    public static RegistryObject<Block> CASING_FINALITY_DOMINION;    // 终焉统御机壳
    public static RegistryObject<Block> CASING_FINALITY_HYPERION;    // 休伯利安舰载机壳
    public static RegistryObject<Block> CASING_FINALITY_WONDER;      // 文明奇观机壳

    // ════════════════════════════════════════════
    // 16色通用装饰机壳（用于多方块结构的外壳装饰拼搭）
    // 注册ID格式: casing_colored_<颜色>
    // 贴图路径: textures/block/casings/casing_colored_<颜色>.png
    // 在多方块 pattern 中可用 any(COLORED_CASINGS) 匹配任意颜色
    // ════════════════════════════════════════════
    public static RegistryObject<Block> CASING_COLORED_WHITE;
    public static RegistryObject<Block> CASING_COLORED_ORANGE;
    public static RegistryObject<Block> CASING_COLORED_MAGENTA;
    public static RegistryObject<Block> CASING_COLORED_LIGHT_BLUE;
    public static RegistryObject<Block> CASING_COLORED_YELLOW;
    public static RegistryObject<Block> CASING_COLORED_LIME;
    public static RegistryObject<Block> CASING_COLORED_PINK;
    public static RegistryObject<Block> CASING_COLORED_GRAY;
    public static RegistryObject<Block> CASING_COLORED_LIGHT_GRAY;
    public static RegistryObject<Block> CASING_COLORED_CYAN;
    public static RegistryObject<Block> CASING_COLORED_PURPLE;
    public static RegistryObject<Block> CASING_COLORED_BLUE;
    public static RegistryObject<Block> CASING_COLORED_BROWN;
    public static RegistryObject<Block> CASING_COLORED_GREEN;
    public static RegistryObject<Block> CASING_COLORED_RED;
    public static RegistryObject<Block> CASING_COLORED_BLACK;

    /** 16色机壳数组，方便遍历/批量处理/多方块 pattern 匹配 */
    public static RegistryObject<Block>[] ALL_COLORED_CASINGS;

    /**
     * 功能性机壳属性（硬度5，爆炸抗性10）。
     * 修改硬度：调整 strength() 的第一个参数
     * 修改爆炸抗性：调整 strength() 的第二个参数
     */
    private static BlockBehaviour.Properties casingProperties() {
        return BlockBehaviour.Properties.of()
                .strength(5.0f, 10.0f)
                .sound(SoundType.METAL)
                .requiresCorrectToolForDrops();
    }

    /**
     * 16色装饰机壳属性（硬度3，爆炸抗性6，比功能机壳更软）。
     * 修改硬度/抗性：调整 strength() 参数
     */
    private static BlockBehaviour.Properties coloredCasingProperties() {
        return BlockBehaviour.Properties.of()
                .strength(3.0f, 6.0f)
                .sound(SoundType.METAL)
                .requiresCorrectToolForDrops();
    }

    /** 注册功能性机壳（高硬度） */
    private static RegistryObject<Block> casing(String id) {
        return Hk3Blocks.registerBlock(id, () -> new Block(casingProperties()));
    }

    /** 注册装饰性颜色机壳（低硬度） */
    private static RegistryObject<Block> coloredCasing(String color) {
        return Hk3Blocks.registerBlock("casing_colored_" + color,
                () -> new Block(coloredCasingProperties()));
    }

    @SuppressWarnings("unchecked")
    public static void register() {
        // ── 基础 / 海渊（Max后第一批多方块的主体结构方块） ──
        CASING_SOULIUM = casing("casing_soulium");
        CASING_REINFORCED_SOULIUM = casing("casing_reinforced_soulium");
        CASING_ABYSS_MECHANICAL = casing("casing_abyss_mechanical");
        CASING_ABYSS_RESEARCH = casing("casing_abyss_research");
        CASING_ABYSS_ENERGY = casing("casing_abyss_energy");

        // ── 虚数阶段 ──
        CASING_IMAGINARY_TREE = casing("casing_imaginary_tree");
        CASING_IMAGINARY_LATTICE = casing("casing_imaginary_lattice");
        CASING_IMAGINARY_CORE = casing("casing_imaginary_core");
        CASING_IMAGINARY_ANCHOR = casing("casing_imaginary_anchor");
        CASING_IMAGINARY_WEAVE = casing("casing_imaginary_weave");

        // ── 量子阶段 ──
        CASING_QUANTUM_SEA = casing("casing_quantum_sea");
        CASING_QUANTUM_BUBBLE = casing("casing_quantum_bubble");
        CASING_QUANTUM_FLUX = casing("casing_quantum_flux");
        CASING_QUANTUM_ENTANGLE = casing("casing_quantum_entangle");
        CASING_QUANTUM_SHIPBOARD = casing("casing_quantum_shipboard");

        // ── 终焉阶段 ──
        CASING_FINALITY_VOID = casing("casing_finality_void");
        CASING_FINALITY_SANCTUM = casing("casing_finality_sanctum");
        CASING_FINALITY_DOMINION = casing("casing_finality_dominion");
        CASING_FINALITY_HYPERION = casing("casing_finality_hyperion");
        CASING_FINALITY_WONDER = casing("casing_finality_wonder");

        // ── 16色通用装饰机壳 ──
        CASING_COLORED_WHITE      = coloredCasing("white");
        CASING_COLORED_ORANGE     = coloredCasing("orange");
        CASING_COLORED_MAGENTA    = coloredCasing("magenta");
        CASING_COLORED_LIGHT_BLUE = coloredCasing("light_blue");
        CASING_COLORED_YELLOW     = coloredCasing("yellow");
        CASING_COLORED_LIME       = coloredCasing("lime");
        CASING_COLORED_PINK       = coloredCasing("pink");
        CASING_COLORED_GRAY       = coloredCasing("gray");
        CASING_COLORED_LIGHT_GRAY = coloredCasing("light_gray");
        CASING_COLORED_CYAN       = coloredCasing("cyan");
        CASING_COLORED_PURPLE     = coloredCasing("purple");
        CASING_COLORED_BLUE       = coloredCasing("blue");
        CASING_COLORED_BROWN      = coloredCasing("brown");
        CASING_COLORED_GREEN      = coloredCasing("green");
        CASING_COLORED_RED        = coloredCasing("red");
        CASING_COLORED_BLACK      = coloredCasing("black");

        ALL_COLORED_CASINGS = new RegistryObject[] {
            CASING_COLORED_WHITE, CASING_COLORED_ORANGE, CASING_COLORED_MAGENTA,
            CASING_COLORED_LIGHT_BLUE, CASING_COLORED_YELLOW, CASING_COLORED_LIME,
            CASING_COLORED_PINK, CASING_COLORED_GRAY, CASING_COLORED_LIGHT_GRAY,
            CASING_COLORED_CYAN, CASING_COLORED_PURPLE, CASING_COLORED_BLUE,
            CASING_COLORED_BROWN, CASING_COLORED_GREEN, CASING_COLORED_RED,
            CASING_COLORED_BLACK
        };
    }
}
