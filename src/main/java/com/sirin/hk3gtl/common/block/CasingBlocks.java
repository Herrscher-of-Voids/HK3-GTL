package com.sirin.hk3gtl.common.block;

import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraftforge.registries.RegistryObject;

public class CasingBlocks {

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
     * 16色装饰机壳属性（硬度3，爆炸抗性6，比功能机壳更软）。
     * 修改硬度/抗性：调整 strength() 参数
     */
    private static BlockBehaviour.Properties coloredCasingProperties() {
        return BlockBehaviour.Properties.of()
                .strength(3.0f, 6.0f)
                .sound(SoundType.METAL)
                .requiresCorrectToolForDrops();
    }


    /** 注册装饰性颜色机壳（低硬度） */
    private static RegistryObject<Block> coloredCasing(String color) {
        return Hk3Blocks.registerBlock("casing_colored_" + color,
                () -> new Block(coloredCasingProperties()));
    }

    @SuppressWarnings("unchecked")
    public static void register() {
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
