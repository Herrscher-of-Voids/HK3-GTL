package com.sirin.hk3gtl.common.multiblock.pattern;



import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.api.pattern.BlockPattern;
import com.gregtechceu.gtceu.api.pattern.FactoryBlockPattern;
import com.gregtechceu.gtceu.api.pattern.Predicates;

/**
 * 临时多方块结构 Pattern 实现类。
 *
 * <p>当前临时结构统一改为“仅控制器本体”：放下控制器即可成型，
 * 不再要求泥土、机壳或仓室方块，便于快速测试机器、配方与事件链。</p>
 */
public class Hk3TemporaryMultiblockPatternsImpl {

    private Hk3TemporaryMultiblockPatternsImpl() {}

    /**
     * 创建仅控制器本体的临时结构。
     *
     * @param definition 多方块机器定义，用于绑定控制器方块
     * @return 供成型校验的 {@link BlockPattern}
     */
    public static BlockPattern createControllerOnly(MultiblockMachineDefinition definition) {
        return FactoryBlockPattern.start()
                .aisle("S")
                .where('S', Predicates.controller(Predicates.blocks(definition.getBlock())))
                .build();
    }

    /**
     * 兼容旧引用：旧临时结构入口，现在统一委托到仅控制器结构。
     */
    public static BlockPattern createDirtCube3x3x3(MultiblockMachineDefinition definition) {
        return createControllerOnly(definition);
    }
}
