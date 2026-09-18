package com.sirin.hk3gtl.common.multiblock.pattern;



import com.gregtechceu.gtceu.api.machine.MultiblockMachineDefinition;
import com.gregtechceu.gtceu.api.pattern.BlockPattern;

/**
 * 临时多方块结构 Pattern 门面类（Facade）。
 *
 * <p>当前临时结构统一为“仅控制器本体”：放下控制器即可成型。
 * 真正实现位于 {@link Hk3TemporaryMultiblockPatternsImpl}。</p>
 */
public class Hk3TemporaryMultiblockPatterns {

    private Hk3TemporaryMultiblockPatterns() {}

    /**
     * 创建仅控制器本体的临时结构。
     */
    public static BlockPattern createControllerOnly(MultiblockMachineDefinition definition) {
        return Hk3TemporaryMultiblockPatternsImpl.createControllerOnly(definition);
    }

    /**
     * 兼容旧引用：旧临时结构入口，现在统一委托到仅控制器结构。
     */
    public static BlockPattern createDirtCube3x3x3(MultiblockMachineDefinition definition) {
        return Hk3TemporaryMultiblockPatternsImpl.createDirtCube3x3x3(definition);
    }
}
