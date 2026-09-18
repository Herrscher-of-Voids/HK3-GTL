package com.sirin.hk3gtl.common.multiblock.pattern;



import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.api.pattern.BlockPattern;
import com.gregtechceu.gtceu.api.pattern.FactoryBlockPattern;
import com.gregtechceu.gtceu.api.pattern.Predicates;
import com.sirin.hk3gtl.common.block.CasingBlocks;
import com.sirin.hk3gtl.common.machine.multiblock.part.Hk3PartAbility;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.block.Block;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

/**
 * P1 核心三台多方块的正式结构 + 通用阶段结构模板。
 *
 * <p>外壳方块：按控制器阶段分别使用海渊能源 / 魂钢 / 海渊科研机壳</p>
 * <p>线圈方块：二硅化钼线圈 (gtceu:molybdenum_disilicide_coil_block)</p>
 * <p>玻璃方块：超空间引力透镜 (gtladditions:spatially_transcendent_gravitational_lens)</p>
 *
 * <ul>
 *   <li>{@link #createAbsorptionTower} — 崩坏能吸收塔 (3×3×3)</li>
 *   <li>{@link #createCrystalCondenser} — 崩坏能结晶凝结厂 (3×3×3)</li>
 *   <li>{@link #createSouliumSmeltery} — 魂钢冶铸中心 (5×3×3)</li>
 *   <li>{@link #createGenericMedium} — 通用 5×3×5 中型结构</li>
 * </ul>
 */
public class Hk3P1PatternsImpl {

    private Hk3P1PatternsImpl() {}

    // ════════════════════════════════════════════
    //  运行时方块引用（延迟加载，避免在注册表冻结前访问）
    // ════════════════════════════════════════════

    private static Block CACHED_COIL, CACHED_GLASS;

    private static Block blockOf(String namespace, String path) {
        Block b = ForgeRegistries.BLOCKS.getValue(new ResourceLocation(namespace, path));
        if (b == null) throw new IllegalStateException(
                "Required block not found: " + namespace + ":" + path);
        return b;
    }

    private static Block coil() {
        if (CACHED_COIL == null) CACHED_COIL = blockOf("gtceu", "molybdenum_disilicide_coil_block");
        return CACHED_COIL;
    }
    private static Block glass() {
        if (CACHED_GLASS == null) CACHED_GLASS = blockOf("gtladditions", "spatially_transcendent_gravitational_lens");
        return CACHED_GLASS;
    }

    // ════════════════════════════════════════════
    //  通用 hatch 谓词：按配方类型识别标准 IO + 崩坏能能力
    //  EU 不再走能源仓：由控制器 Hk3PlayerGridEnergyTrait 从绑定玩家的 GTM 电网直扣
    // ════════════════════════════════════════════

    private static com.gregtechceu.gtceu.api.pattern.TraceabilityPredicate hatchPredicates(
            MultiblockMachineDefinition definition, Block casingBlock, int minCasing) {
        return Predicates.blocks(casingBlock)
                .setMinGlobalLimited(minCasing)
                // 仅识别物品/流体能力；EU 由玩家无线电网直接扣除，不要求能源输入仓。
                .or(Predicates.autoAbilities(definition.getRecipeTypes(), false, false, true, true, true, true))
                // 崩坏能输入/输出仓：本模组扩展，参与基类 tickHk3EnergyBridge 桥接
                .or(Predicates.abilities(Hk3PartAbility.HONKAI_ENERGY_INPUT).setPreviewCount(0))
                .or(Predicates.abilities(Hk3PartAbility.HONKAI_ENERGY_OUTPUT).setPreviewCount(0));
    }

    // ════════════════════════════════════════════
    //  崩坏能吸收塔 — 3×3×3 紧凑立方
    //  IO: 1物入/1物出/0液入/0液出（从虚空抽取崩坏能粒子）
    // ════════════════════════════════════════════

    /**
     * <pre>
     *  Z=0 (背面):   Z=1 (中间):   Z=2 (正面):
     *  CCC           CGC           CCC
     *  CCC           CGC           CSC  ← 控制器
     *  CCC           CGC           CCC
     *
     *  C = 创造机械方块 / 仓位
     *  G = 超空间引力透镜
     *  S = 控制器
     * </pre>
     */
    public static BlockPattern createAbsorptionTower(MultiblockMachineDefinition definition) {
        return FactoryBlockPattern.start()
                .aisle("CCC", "CCC", "CCC")   // Z=0 背面
                .aisle("CGC", "CGC", "CGC")   // Z=1 中间（玻璃柱）
                .aisle("CCC", "CSC", "CCC")   // Z=2 正面
                .where('S', Predicates.controller(Predicates.blocks(definition.getBlock())))
                .where('G', Predicates.blocks(glass()))
                .where('C', hatchPredicates(definition, CasingBlocks.CASING_ABYSS_ENERGY.get(), 10))
                .build();
    }

    // ════════════════════════════════════════════
    //  崩坏能结晶凝结厂 — 3×3×3 紧凑立方
    //  IO: 2物入/2物出/0液入/1液出（粒子→晶体/液态崩坏能）
    // ════════════════════════════════════════════

    /**
     * <pre>
     *  Z=0 (背面):   Z=1 (中间):   Z=2 (正面):
     *  CCC           CLC           CCC
     *  CCC           CLC           CSC  ← 控制器
     *  CCC           CLC           CCC
     *
     *  C = 创造机械方块 / 仓位
     *  L = 二硅化钼线圈
     *  S = 控制器
     * </pre>
     */
    public static BlockPattern createCrystalCondenser(MultiblockMachineDefinition definition) {
        return FactoryBlockPattern.start()
                .aisle("CCC", "CCC", "CCC")   // Z=0 背面
                .aisle("CLC", "CLC", "CLC")   // Z=1 中间（线圈柱）
                .aisle("CCC", "CSC", "CCC")   // Z=2 正面
                .where('S', Predicates.controller(Predicates.blocks(definition.getBlock())))
                .where('L', Predicates.blocks(coil()))
                .where('C', hatchPredicates(definition, CasingBlocks.CASING_ABYSS_ENERGY.get(), 10))
                .build();
    }

    // ════════════════════════════════════════════
    //  魂钢冶铸中心 — 5(宽) × 3(高) × 3(深)
    //  IO: 4物入/4物出/1液入/0液出（多步魂钢冶炼链）
    // ════════════════════════════════════════════

    /**
     * <pre>
     *  正视图 (Z=2 正面):         中间切面 (Z=1):
     *  Y=2  CCCCC                 CCCCC
     *  Y=1  CCSC C                CLLLC    L = 二硅化钼线圈
     *  Y=0  CCCCC                 CCCCC
     * </pre>
     */
    public static BlockPattern createSouliumSmeltery(MultiblockMachineDefinition definition) {
        return FactoryBlockPattern.start()
                .aisle("CCCCC", "CCCCC", "CCCCC")   // Z=0 背面
                .aisle("CCCCC", "CLLLC", "CCCCC")   // Z=1 中间 (线圈)
                .aisle("CCCCC", "CCSCC", "CCCCC")   // Z=2 正面
                .where('S', Predicates.controller(Predicates.blocks(definition.getBlock())))
                .where('L', Predicates.blocks(coil()))
                .where('C', hatchPredicates(definition, CasingBlocks.CASING_SOULIUM.get(), 20))
                .build();
    }

    // ════════════════════════════════════════════
    //  通用中型结构 — 5(宽) × 3(高) × 5(深)
    //  用于 Max / Abyss 阶段大部分机器
    // ════════════════════════════════════════════

    public static BlockPattern createGenericMedium(MultiblockMachineDefinition definition,
                                                   RegistryObject<Block> casingRO) {
        Block casingBlock = casingRO.get();
        return FactoryBlockPattern.start()
                .aisle("CCCCC", "CCCCC", "CCCCC")   // Z=0 背面
                .aisle("CCCCC", "CGGGC", "CCCCC")   // Z=1
                .aisle("CCCCC", "CGGGC", "CCCCC")   // Z=2 中间
                .aisle("CCCCC", "CGGGC", "CCCCC")   // Z=3
                .aisle("CCCCC", "CCSCC", "CCCCC")   // Z=4 正面
                .where('S', Predicates.controller(Predicates.blocks(definition.getBlock())))
                .where('G', Predicates.blocks(glass()))
                .where('C', hatchPredicates(definition, casingBlock, 40))
                .build();
    }

}
