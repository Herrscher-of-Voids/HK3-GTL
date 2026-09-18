package com.sirin.hk3gtl.common.multiblock.pattern;



import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.api.pattern.BlockPattern;
import com.gregtechceu.gtceu.api.pattern.FactoryBlockPattern;
import com.gregtechceu.gtceu.api.pattern.Predicates;
import com.sirin.hk3gtl.common.block.CasingBlocks;
import com.sirin.hk3gtl.common.machine.multiblock.part.Hk3PartAbility;

/**
 * 海渊研究分析矩阵专用结构 Pattern 实现。
 *
 * <h3>关键约束（与 {@link com.sirin.hk3gtl.common.machine.research.Hk3ResearchMatrixMachine} 保持一致）</h3>
 * <ul>
 *   <li>不带物品仓/流体仓：本机器不走 GT RecipeType，所有研究状态由机器自管 NBT 驱动</li>
 *   <li>不带并行仓：每台机器同时只能跑 1 个研究节点</li>
 *   <li>无能源仓：研究矩阵每 tick 消耗 21 亿 EU（待机）+ 节点额外能耗，
 *       由 {@code Hk3ResearchMatrixMachine.consumeEnergy} 反射走 {@code getEnergyContainer()}，
 *       现在聚合的是控制器自带的 Hk3PlayerGridEnergyTrait —— 从绑定玩家的 GTM 无线电网直扣；
 *       崩坏能能源体系保留 {@link Hk3PartAbility#HONKAI_ENERGY_INPUT}</li>
 * </ul>
 *
 * <h3>修改指南</h3>
 * <ul>
 *   <li>调结构尺寸：改 aisle 字符串</li>
 *   <li>新增允许的仓类型：在 X 谓词处 {@code .or(...)} 追加</li>
 *   <li>需要维护仓 / 消声仓时，追加对应 PartAbility，但当前不需要（已 try/catch 兜底异常）</li>
 * </ul>
 */
public class Hk3ResearchMatrixPatternImpl {

    public static BlockPattern createPattern(MultiblockMachineDefinition definition) {
        return FactoryBlockPattern.start()
                .aisle("XXX", "XXX", "XXX")
                .aisle("XXX", "XXX", "XXX")
                .aisle("XXX", "XSX", "XXX")
                .where('S', Predicates.controller(Predicates.blocks(definition.getBlock())))
                .where('X', Predicates.blocks(CasingBlocks.CASING_ABYSS_RESEARCH.get())
                        .setMinGlobalLimited(1)
                        .or(Predicates.abilities(Hk3PartAbility.HONKAI_ENERGY_INPUT).setPreviewCount(0))
                        .or(Predicates.abilities(Hk3PartAbility.WIRELESS_HONKAI_INPUT).setPreviewCount(0)))
                .build();
    }
}
