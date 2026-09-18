package com.sirin.hk3gtl.common.multiblock.hyperion;



import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.api.machine.multiblock.PartAbility;
import com.gregtechceu.gtceu.api.pattern.BlockPattern;
import com.gregtechceu.gtceu.api.pattern.FactoryBlockPattern;
import com.gregtechceu.gtceu.api.pattern.Predicates;
import com.sirin.hk3gtl.common.machine.multiblock.part.Hk3PartAbility;
import com.sirin.hk3gtl.common.constants.Hk3Constants;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.NbtUtils;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import org.slf4j.Logger;
import com.mojang.logging.LogUtils;

import java.lang.reflect.Field;
import java.util.Arrays;
import java.util.Comparator;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * 休伯利安号旗舰多方块 Pattern。
 * 由 tools/hyperion_litematic_gen.js 从单一 .litematic 投影生成。
 * 维度: 536W × 94H × 201D，总方块: 169216。
 * 控制器位置(归零本地坐标，底向上 Y): (267, 42, 198)
 *
 * 'S' = 控制器
 * 'X' = gtladditions:gravity_stabilization_casing（原石英块位置）
 * 'B' = gtladditions:extreme_density_casing（原黑色混凝土位置）
 * '\u03A9' = 物品输入总线, '\u03A8' = 重力稳定机壳（原 EU 能源输入仓，能源仓已退役）, '\u03A6' = 崩坏能输入仓, '\u03A3' = 维护仓（与玩家投影体素对应关系见 {@link com.sirin.hk3gtl.common.multiblock.pattern.HyperionPatternProviderImpl}）
 * ' ' = 空气
 * 其余字符 = 各自方块（半砖/楼梯已换成同材质完整方块，仅 Predicates.blocks）。
 * 活板门若有则仍按完整 BlockState 锁朝向。
 */
public final class HyperionPatternData {

    private static final Logger LOGGER = LogUtils.getLogger();
    /** 显式控制器 ID，避免 definition.getBlock() 在某些时序下返回错块（如把奇观建筑模拟平台误识别为材料）。 */
    private static final ResourceLocation HYPERION_CONTROLLER_ID =
            new ResourceLocation(Hk3Constants.MOD_ID, "hyperion_flagship");
    private static final AtomicBoolean BUILT = new AtomicBoolean(false);
    private static BlockPattern cachedPattern;

    /**
     * 把 Name + Properties 还原成 BlockState。
     * 借助 NbtUtils.readBlockState 实现，失败回退 AIR，避免初始化抛异常。
     */
    private static BlockState parseState(String name, java.util.function.Consumer<CompoundTag> propsBuilder) {
        try {
            CompoundTag root = new CompoundTag();
            root.putString("Name", name);
            CompoundTag props = new CompoundTag();
            if (propsBuilder != null) propsBuilder.accept(props);
            if (!props.isEmpty()) root.put("Properties", props);
            BlockState state = NbtUtils.readBlockState(BuiltInRegistries.BLOCK.asLookup(), root);
            return state == null ? Blocks.AIR.defaultBlockState() : state;
        } catch (Exception e) {
            return Blocks.AIR.defaultBlockState();
        }
    }

    @Deprecated
    private static final BlockState S_x2e = parseState("minecraft:iron_trapdoor", p -> {
        p.putString("facing", "east");
        p.putString("half", "bottom");
        p.putString("open", "false");
        p.putString("powered", "false");
        p.putString("waterlogged", "false");
    }); // minecraft:iron_trapdoor|facing=east,half=bottom,open=false,powered=false,waterlogged=false
    @Deprecated
    private static final BlockState S_x2f = parseState("minecraft:iron_trapdoor", p -> {
        p.putString("facing", "east");
        p.putString("half", "top");
        p.putString("open", "false");
        p.putString("powered", "false");
        p.putString("waterlogged", "false");
    }); // minecraft:iron_trapdoor|facing=east,half=top,open=false,powered=false,waterlogged=false
    @Deprecated
    private static final BlockState S_0 = parseState("minecraft:iron_trapdoor", p -> {
        p.putString("facing", "north");
        p.putString("half", "top");
        p.putString("open", "false");
        p.putString("powered", "false");
        p.putString("waterlogged", "false");
    }); // minecraft:iron_trapdoor|facing=north,half=top,open=false,powered=false,waterlogged=false
    @Deprecated
    private static final BlockState S_1 = parseState("minecraft:iron_trapdoor", p -> {
        p.putString("facing", "south");
        p.putString("half", "top");
        p.putString("open", "false");
        p.putString("powered", "false");
        p.putString("waterlogged", "false");
    }); // minecraft:iron_trapdoor|facing=south,half=top,open=false,powered=false,waterlogged=false
    @Deprecated
    private static final BlockState S_2 = parseState("minecraft:iron_trapdoor", p -> {
        p.putString("facing", "west");
        p.putString("half", "bottom");
        p.putString("open", "false");
        p.putString("powered", "false");
        p.putString("waterlogged", "false");
    }); // minecraft:iron_trapdoor|facing=west,half=bottom,open=false,powered=false,waterlogged=false
    @Deprecated
    private static final BlockState S_3 = parseState("minecraft:iron_trapdoor", p -> {
        p.putString("facing", "west");
        p.putString("half", "top");
        p.putString("open", "false");
        p.putString("powered", "false");
        p.putString("waterlogged", "false");
    }); // minecraft:iron_trapdoor|facing=west,half=top,open=false,powered=false,waterlogged=false

    private static final net.minecraft.world.level.block.Block IRON_TRAPDOOR =
            BuiltInRegistries.BLOCK.get(new ResourceLocation("minecraft", "iron_trapdoor"));

    private HyperionPatternData() {}

    public static BlockPattern createPattern(MultiblockMachineDefinition definition) {
        if (BUILT.get() && cachedPattern != null) return cachedPattern;
        synchronized (BUILT) {
            if (BUILT.get() && cachedPattern != null) return cachedPattern;
            cachedPattern = build(definition);
            BUILT.set(true);
            return cachedPattern;
        }
    }

    private static BlockPattern build(MultiblockMachineDefinition definition) {
        logLayerHeights();
        FactoryBlockPattern pat = FactoryBlockPattern.start()
                .aisle(HyperionLayerPart1.LAYER_001)
                .aisle(HyperionLayerPart1.LAYER_002)
                .aisle(HyperionLayerPart1.LAYER_003)
                .aisle(HyperionLayerPart1.LAYER_004)
                .aisle(HyperionLayerPart1.LAYER_005)
                .aisle(HyperionLayerPart1.LAYER_006)
                .aisle(HyperionLayerPart1.LAYER_007)
                .aisle(HyperionLayerPart1.LAYER_008)
                .aisle(HyperionLayerPart1.LAYER_009)
                .aisle(HyperionLayerPart1.LAYER_010)
                .aisle(HyperionLayerPart2.LAYER_001)
                .aisle(HyperionLayerPart2.LAYER_002)
                .aisle(HyperionLayerPart2.LAYER_003)
                .aisle(HyperionLayerPart2.LAYER_004)
                .aisle(HyperionLayerPart2.LAYER_005)
                .aisle(HyperionLayerPart2.LAYER_006)
                .aisle(HyperionLayerPart2.LAYER_007)
                .aisle(HyperionLayerPart2.LAYER_008)
                .aisle(HyperionLayerPart2.LAYER_009)
                .aisle(HyperionLayerPart2.LAYER_010)
                .aisle(HyperionLayerPart3.LAYER_001)
                .aisle(HyperionLayerPart3.LAYER_002)
                .aisle(HyperionLayerPart3.LAYER_003)
                .aisle(HyperionLayerPart3.LAYER_004)
                .aisle(HyperionLayerPart3.LAYER_005)
                .aisle(HyperionLayerPart3.LAYER_006)
                .aisle(HyperionLayerPart3.LAYER_007)
                .aisle(HyperionLayerPart3.LAYER_008)
                .aisle(HyperionLayerPart3.LAYER_009)
                .aisle(HyperionLayerPart3.LAYER_010)
                .aisle(HyperionLayerPart4.LAYER_001)
                .aisle(HyperionLayerPart4.LAYER_002)
                .aisle(HyperionLayerPart4.LAYER_003)
                .aisle(HyperionLayerPart4.LAYER_004)
                .aisle(HyperionLayerPart4.LAYER_005)
                .aisle(HyperionLayerPart4.LAYER_006)
                .aisle(HyperionLayerPart4.LAYER_007)
                .aisle(HyperionLayerPart4.LAYER_008)
                .aisle(HyperionLayerPart4.LAYER_009)
                .aisle(HyperionLayerPart4.LAYER_010)
                .aisle(HyperionLayerPart5.LAYER_001)
                .aisle(HyperionLayerPart5.LAYER_002)
                .aisle(HyperionLayerPart5.LAYER_003)
                .aisle(HyperionLayerPart5.LAYER_004)
                .aisle(HyperionLayerPart5.LAYER_005)
                .aisle(HyperionLayerPart5.LAYER_006)
                .aisle(HyperionLayerPart5.LAYER_007)
                .aisle(HyperionLayerPart5.LAYER_008)
                .aisle(HyperionLayerPart5.LAYER_009)
                .aisle(HyperionLayerPart5.LAYER_010)
                .aisle(HyperionLayerPart6.LAYER_001)
                .aisle(HyperionLayerPart6.LAYER_002)
                .aisle(HyperionLayerPart6.LAYER_003)
                .aisle(HyperionLayerPart6.LAYER_004)
                .aisle(HyperionLayerPart6.LAYER_005)
                .aisle(HyperionLayerPart6.LAYER_006)
                .aisle(HyperionLayerPart6.LAYER_007)
                .aisle(HyperionLayerPart6.LAYER_008)
                .aisle(HyperionLayerPart6.LAYER_009)
                .aisle(HyperionLayerPart6.LAYER_010)
                .aisle(HyperionLayerPart7.LAYER_001)
                .aisle(HyperionLayerPart7.LAYER_002)
                .aisle(HyperionLayerPart7.LAYER_003)
                .aisle(HyperionLayerPart7.LAYER_004)
                .aisle(HyperionLayerPart7.LAYER_005)
                .aisle(HyperionLayerPart7.LAYER_006)
                .aisle(HyperionLayerPart7.LAYER_007)
                .aisle(HyperionLayerPart7.LAYER_008)
                .aisle(HyperionLayerPart7.LAYER_009)
                .aisle(HyperionLayerPart7.LAYER_010)
                .aisle(HyperionLayerPart8.LAYER_001)
                .aisle(HyperionLayerPart8.LAYER_002)
                .aisle(HyperionLayerPart8.LAYER_003)
                .aisle(HyperionLayerPart8.LAYER_004)
                .aisle(HyperionLayerPart8.LAYER_005)
                .aisle(HyperionLayerPart8.LAYER_006)
                .aisle(HyperionLayerPart8.LAYER_007)
                .aisle(HyperionLayerPart8.LAYER_008)
                .aisle(HyperionLayerPart8.LAYER_009)
                .aisle(HyperionLayerPart8.LAYER_010)
                .aisle(HyperionLayerPart9.LAYER_001)
                .aisle(HyperionLayerPart9.LAYER_002)
                .aisle(HyperionLayerPart9.LAYER_003)
                .aisle(HyperionLayerPart9.LAYER_004)
                .aisle(HyperionLayerPart9.LAYER_005)
                .aisle(HyperionLayerPart9.LAYER_006)
                .aisle(HyperionLayerPart9.LAYER_007)
                .aisle(HyperionLayerPart9.LAYER_008)
                .aisle(HyperionLayerPart9.LAYER_009)
                .aisle(HyperionLayerPart9.LAYER_010)
                .aisle(HyperionLayerPart10.LAYER_001)
                .aisle(HyperionLayerPart10.LAYER_002)
                .aisle(HyperionLayerPart10.LAYER_003)
                .aisle(HyperionLayerPart10.LAYER_004)
                .aisle(HyperionLayerPart10.LAYER_005)
                .aisle(HyperionLayerPart10.LAYER_006)
                .aisle(HyperionLayerPart10.LAYER_007)
                .aisle(HyperionLayerPart10.LAYER_008)
                .aisle(HyperionLayerPart10.LAYER_009)
                .aisle(HyperionLayerPart10.LAYER_010)
                .aisle(HyperionLayerPart11.LAYER_001)
                .aisle(HyperionLayerPart11.LAYER_002)
                .aisle(HyperionLayerPart11.LAYER_003)
                .aisle(HyperionLayerPart11.LAYER_004)
                .aisle(HyperionLayerPart11.LAYER_005)
                .aisle(HyperionLayerPart11.LAYER_006)
                .aisle(HyperionLayerPart11.LAYER_007)
                .aisle(HyperionLayerPart11.LAYER_008)
                .aisle(HyperionLayerPart11.LAYER_009)
                .aisle(HyperionLayerPart11.LAYER_010)
                .aisle(HyperionLayerPart12.LAYER_001)
                .aisle(HyperionLayerPart12.LAYER_002)
                .aisle(HyperionLayerPart12.LAYER_003)
                .aisle(HyperionLayerPart12.LAYER_004)
                .aisle(HyperionLayerPart12.LAYER_005)
                .aisle(HyperionLayerPart12.LAYER_006)
                .aisle(HyperionLayerPart12.LAYER_007)
                .aisle(HyperionLayerPart12.LAYER_008)
                .aisle(HyperionLayerPart12.LAYER_009)
                .aisle(HyperionLayerPart12.LAYER_010)
                .aisle(HyperionLayerPart13.LAYER_001)
                .aisle(HyperionLayerPart13.LAYER_002)
                .aisle(HyperionLayerPart13.LAYER_003)
                .aisle(HyperionLayerPart13.LAYER_004)
                .aisle(HyperionLayerPart13.LAYER_005)
                .aisle(HyperionLayerPart13.LAYER_006)
                .aisle(HyperionLayerPart13.LAYER_007)
                .aisle(HyperionLayerPart13.LAYER_008)
                .aisle(HyperionLayerPart13.LAYER_009)
                .aisle(HyperionLayerPart13.LAYER_010)
                .aisle(HyperionLayerPart14.LAYER_001)
                .aisle(HyperionLayerPart14.LAYER_002)
                .aisle(HyperionLayerPart14.LAYER_003)
                .aisle(HyperionLayerPart14.LAYER_004)
                .aisle(HyperionLayerPart14.LAYER_005)
                .aisle(HyperionLayerPart14.LAYER_006)
                .aisle(HyperionLayerPart14.LAYER_007)
                .aisle(HyperionLayerPart14.LAYER_008)
                .aisle(HyperionLayerPart14.LAYER_009)
                .aisle(HyperionLayerPart14.LAYER_010)
                .aisle(HyperionLayerPart15.LAYER_001)
                .aisle(HyperionLayerPart15.LAYER_002)
                .aisle(HyperionLayerPart15.LAYER_003)
                .aisle(HyperionLayerPart15.LAYER_004)
                .aisle(HyperionLayerPart15.LAYER_005)
                .aisle(HyperionLayerPart15.LAYER_006)
                .aisle(HyperionLayerPart15.LAYER_007)
                .aisle(HyperionLayerPart15.LAYER_008)
                .aisle(HyperionLayerPart15.LAYER_009)
                .aisle(HyperionLayerPart15.LAYER_010)
                .aisle(HyperionLayerPart16.LAYER_001)
                .aisle(HyperionLayerPart16.LAYER_002)
                .aisle(HyperionLayerPart16.LAYER_003)
                .aisle(HyperionLayerPart16.LAYER_004)
                .aisle(HyperionLayerPart16.LAYER_005)
                .aisle(HyperionLayerPart16.LAYER_006)
                .aisle(HyperionLayerPart16.LAYER_007)
                .aisle(HyperionLayerPart16.LAYER_008)
                .aisle(HyperionLayerPart16.LAYER_009)
                .aisle(HyperionLayerPart16.LAYER_010)
                .aisle(HyperionLayerPart17.LAYER_001)
                .aisle(HyperionLayerPart17.LAYER_002)
                .aisle(HyperionLayerPart17.LAYER_003)
                .aisle(HyperionLayerPart17.LAYER_004)
                .aisle(HyperionLayerPart17.LAYER_005)
                .aisle(HyperionLayerPart17.LAYER_006)
                .aisle(HyperionLayerPart17.LAYER_007)
                .aisle(HyperionLayerPart17.LAYER_008)
                .aisle(HyperionLayerPart17.LAYER_009)
                .aisle(HyperionLayerPart17.LAYER_010)
                .aisle(HyperionLayerPart18.LAYER_001)
                .aisle(HyperionLayerPart18.LAYER_002)
                .aisle(HyperionLayerPart18.LAYER_003)
                .aisle(HyperionLayerPart18.LAYER_004)
                .aisle(HyperionLayerPart18.LAYER_005)
                .aisle(HyperionLayerPart18.LAYER_006)
                .aisle(HyperionLayerPart18.LAYER_007)
                .aisle(HyperionLayerPart18.LAYER_008)
                .aisle(HyperionLayerPart18.LAYER_009)
                .aisle(HyperionLayerPart18.LAYER_010)
                .aisle(HyperionLayerPart19.LAYER_001)
                .aisle(HyperionLayerPart19.LAYER_002)
                .aisle(HyperionLayerPart19.LAYER_003)
                .aisle(HyperionLayerPart19.LAYER_004)
                .aisle(HyperionLayerPart19.LAYER_005)
                .aisle(HyperionLayerPart19.LAYER_006)
                .aisle(HyperionLayerPart19.LAYER_007)
                .aisle(HyperionLayerPart19.LAYER_008)
                .aisle(HyperionLayerPart19.LAYER_009)
                .aisle(HyperionLayerPart19.LAYER_010)
                .aisle(HyperionLayerPart20.LAYER_001)
                .aisle(HyperionLayerPart20.LAYER_002)
                .aisle(HyperionLayerPart20.LAYER_003)
                .aisle(HyperionLayerPart20.LAYER_004)
                .aisle(HyperionLayerPart20.LAYER_005)
                .aisle(HyperionLayerPart20.LAYER_006)
                .aisle(HyperionLayerPart20.LAYER_007)
                .aisle(HyperionLayerPart20.LAYER_008)
                .aisle(HyperionLayerPart20.LAYER_009)
                .aisle(HyperionLayerPart20.LAYER_010)
                .aisle(HyperionLayerPart21.LAYER_001);

        // 用显式注册表查询的 Hyperion 控制器，避免被相邻多方块误绑定。
        net.minecraft.world.level.block.Block controllerBlock =
                BuiltInRegistries.BLOCK.get(HYPERION_CONTROLLER_ID);
        if (controllerBlock == null || controllerBlock == net.minecraft.world.level.block.Blocks.AIR) {
            LOGGER.warn("[HK3GTL] Hyperion 控制器查表失败，回退 definition.getBlock(): id={} fallback={}",
                    HYPERION_CONTROLLER_ID, definition.getBlock());
            controllerBlock = definition.getBlock();
        }
        pat = pat.where('S', Predicates.controller(Predicates.blocks(controllerBlock)));

        // 'X' = 原石英块位置 → gtladditions:gravity_stabilization_casing
        pat = pat.where('X', Predicates.blocks(BuiltInRegistries.BLOCK.get(new ResourceLocation("gtladditions", "gravity_stabilization_casing"))));

        // 'B' = 原黑色混凝土位置 → gtladditions:extreme_density_casing
        pat = pat.where('B', Predicates.blocks(BuiltInRegistries.BLOCK.get(new ResourceLocation("gtladditions", "extreme_density_casing"))));

        // 休伯利安专用舱位（图案中为希腊字母，避免与 ASCII 装饰符号冲突）
        pat = pat.where('\u03A9', Predicates.abilities(PartAbility.IMPORT_ITEMS).setPreviewCount(1));
        // 'Ψ' 原为 EU 能源输入仓：能源仓退役（EU 走玩家电网直扣），槽位改放重力稳定机壳
        pat = pat.where('\u03A8', Predicates.blocks(BuiltInRegistries.BLOCK.get(new ResourceLocation("gtladditions", "gravity_stabilization_casing"))));
        pat = pat.where('\u03A6', Predicates.abilities(Hk3PartAbility.HONKAI_ENERGY_INPUT).setPreviewCount(1));
        pat = pat.where('\u03A3', Predicates.abilities(PartAbility.MAINTENANCE).setPreviewCount(1));

        pat = pat.where('!', Predicates.blocks(BuiltInRegistries.BLOCK.get(new ResourceLocation("minecraft", "black_stained_glass")))); // minecraft:black_stained_glass
        pat = pat.where('#', Predicates.blocks(BuiltInRegistries.BLOCK.get(new ResourceLocation("minecraft", "black_stained_glass_pane")))); // minecraft:black_stained_glass_pane
        pat = pat.where('$', Predicates.blocks(BuiltInRegistries.BLOCK.get(new ResourceLocation("minecraft", "blue_concrete")))); // minecraft:blue_concrete
        pat = pat.where('%', Predicates.blocks(BuiltInRegistries.BLOCK.get(new ResourceLocation("minecraft", "blue_stained_glass")))); // minecraft:blue_stained_glass
        pat = pat.where('&', Predicates.blocks(BuiltInRegistries.BLOCK.get(new ResourceLocation("minecraft", "blue_stained_glass_pane")))); // minecraft:blue_stained_glass_pane
        pat = pat.where('(', Predicates.blocks(BuiltInRegistries.BLOCK.get(new ResourceLocation("minecraft", "brown_concrete")))); // minecraft:brown_concrete
        pat = pat.where(')', Predicates.blocks(BuiltInRegistries.BLOCK.get(new ResourceLocation("gtlcore", "qft_coil")))); // minecraft:cyan_concrete → gtlcore:qft_coil
        pat = pat.where('*', Predicates.blocks(BuiltInRegistries.BLOCK.get(new ResourceLocation("gtlcore", "ultimate_stellar_containment_casing")))); // minecraft:cyan_terracotta → gtlcore:ultimate_stellar_containment_casing
        pat = pat.where('+', Predicates.blocks(BuiltInRegistries.BLOCK.get(new ResourceLocation("minecraft", "deepslate_tiles")))); // minecraft:deepslate_tiles
        pat = pat.where(',', Predicates.blocks(BuiltInRegistries.BLOCK.get(new ResourceLocation("minecraft", "end_rod")))); // minecraft:end_rod
        pat = pat.where('-', Predicates.blocks(BuiltInRegistries.BLOCK.get(new ResourceLocation("minecraft", "gold_block")))); // minecraft:gold_block
        pat = pat.where('.', Predicates.blocks(IRON_TRAPDOOR)); // iron_trapdoor (ignore facing/open/half)
        pat = pat.where('/', Predicates.blocks(IRON_TRAPDOOR)); // iron_trapdoor (ignore facing/open/half)
        pat = pat.where('0', Predicates.blocks(IRON_TRAPDOOR)); // iron_trapdoor (ignore facing/open/half)
        pat = pat.where('1', Predicates.blocks(IRON_TRAPDOOR)); // iron_trapdoor (ignore facing/open/half)
        pat = pat.where('2', Predicates.blocks(IRON_TRAPDOOR)); // iron_trapdoor (ignore facing/open/half)
        pat = pat.where('3', Predicates.blocks(IRON_TRAPDOOR)); // iron_trapdoor (ignore facing/open/half)
        pat = pat.where('4', Predicates.blocks(BuiltInRegistries.BLOCK.get(new ResourceLocation("minecraft", "light_blue_concrete")))); // minecraft:light_blue_concrete
        pat = pat.where('5', Predicates.blocks(BuiltInRegistries.BLOCK.get(new ResourceLocation("minecraft", "light_blue_stained_glass")))); // minecraft:light_blue_stained_glass
        pat = pat.where('6', Predicates.blocks(BuiltInRegistries.BLOCK.get(new ResourceLocation("minecraft", "light_blue_stained_glass_pane")))); // minecraft:light_blue_stained_glass_pane
        pat = pat.where('7', Predicates.blocks(BuiltInRegistries.BLOCK.get(new ResourceLocation("minecraft", "light_gray_concrete")))); // minecraft:light_gray_concrete
        pat = pat.where('8', Predicates.blocks(BuiltInRegistries.BLOCK.get(new ResourceLocation("minecraft", "orange_concrete")))); // minecraft:orange_concrete
        pat = pat.where('9', Predicates.blocks(BuiltInRegistries.BLOCK.get(new ResourceLocation("gtlcore", "antifreeze_heatproof_machine_casing")))); // minecraft:polished_deepslate → gtlcore:antifreeze_heatproof_machine_casing
        pat = pat.where(':', Predicates.blocks(BuiltInRegistries.BLOCK.get(new ResourceLocation("minecraft", "polished_deepslate_wall")))); // minecraft:polished_deepslate_wall
        pat = pat.where(';', Predicates.blocks(BuiltInRegistries.BLOCK.get(new ResourceLocation("minecraft", "purple_stained_glass")))); // minecraft:purple_stained_glass
        pat = pat.where('<', Predicates.blocks(BuiltInRegistries.BLOCK.get(new ResourceLocation("minecraft", "redstone_block")))); // minecraft:redstone_block
        pat = pat.where('=', Predicates.blocks(BuiltInRegistries.BLOCK.get(new ResourceLocation("minecraft", "redstone_lamp")))); // minecraft:redstone_lamp
        pat = pat.where('>', Predicates.blocks(BuiltInRegistries.BLOCK.get(new ResourceLocation("minecraft", "sea_lantern")))); // minecraft:sea_lantern
        pat = pat.where('?', Predicates.blocks(BuiltInRegistries.BLOCK.get(new ResourceLocation("gtlcore", "fission_reactor_casing")))); // minecraft:smooth_stone → gtlcore:fission_reactor_casing
        pat = pat.where('@', Predicates.blocks(BuiltInRegistries.BLOCK.get(new ResourceLocation("minecraft", "soul_lantern")))); // minecraft:soul_lantern
        pat = pat.where('A', Predicates.blocks(BuiltInRegistries.BLOCK.get(new ResourceLocation("minecraft", "white_stained_glass_pane")))); // minecraft:white_stained_glass_pane
        pat = pat.where('C', Predicates.blocks(BuiltInRegistries.BLOCK.get(new ResourceLocation("gtceu", "industrial_steam_casing")))); // minecraft:yellow_concrete → gtceu:industrial_steam_casing
        pat = pat.where('D', Predicates.blocks(BuiltInRegistries.BLOCK.get(new ResourceLocation("minecraft", "yellow_terracotta")))); // minecraft:yellow_terracotta

        pat = pat.where(' ', Predicates.air());

        return pat.build();
    }

    private static void logLayerHeights() {
        if (!LOGGER.isDebugEnabled()) {
            return;
        }
        final String packageName = HyperionPatternData.class.getPackageName();
        for (int part = 1; part <= 21; part++) {
            String className = packageName + ".HyperionLayerPart" + part;
            try {
                Class<?> layerClass = Class.forName(className);
                Field[] fields = layerClass.getDeclaredFields();
                Arrays.sort(fields, Comparator.comparing(Field::getName));
                for (Field field : fields) {
                    if (!field.getName().startsWith("LAYER_")) {
                        continue;
                    }
                    field.setAccessible(true);
                    Object value = field.get(null);
                    if (value instanceof String[] rows) {
                        LOGGER.debug("[HK3GTL] Hyperion layer rows {}.{} = {}", layerClass.getSimpleName(), field.getName(), rows.length);
                    }
                }
            } catch (ReflectiveOperationException e) {
                LOGGER.debug("[HK3GTL] Hyperion layer reflection failed for {}: {}", className, e.toString());
            }
        }
    }
}