package com.sirin.hk3gtl.common.machine.multiblock.part;



import com.gregtechceu.gtceu.api.machine.MachineDefinition;
import com.sirin.hk3gtl.common.block.energy.HonkaiHatchType;

import java.util.Collections;
import java.util.EnumMap;
import java.util.Map;

/**
 * 已退役崩坏能仓室的注册占位入口。
 * 五种仓室不再注册，但保留类型映射供旧存档和结构扫描代码编译兼容。
 */
public class Hk3PartMachines {

    private static final Map<HonkaiHatchType, MachineDefinition> MUTABLE_HONKAI_HATCHES =
            new EnumMap<>(HonkaiHatchType.class);

    public static final Map<HonkaiHatchType, MachineDefinition> HONKAI_HATCHES =
            Collections.unmodifiableMap(MUTABLE_HONKAI_HATCHES);

    public static void init() {
        // 五种崩坏能仓室已退役，不再向 GTCEu 注册方块、物品或多方块部件。
        MUTABLE_HONKAI_HATCHES.clear();
    }
}
