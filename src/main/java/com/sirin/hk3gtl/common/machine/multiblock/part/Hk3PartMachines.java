package com.sirin.hk3gtl.common.machine.multiblock.part;


/**
 * 【文件职责】
 * - 定义 Hk3PartMachines 机器行为与结构逻辑。
 * - 关键调用链：由上层系统入口调用 -> 本文件核心方法 -> 下游模块。
 *
 * 【变更记录】2026-05-19
 * - 删除：
 *   1) 初始归档备注：自 v0.3 基线梳理，无本次 diff。
 * - 新增：
 *   1) 新增统一变更备注块，便于后续维护与审计追踪。
 * - 修改：
 *   1) 未改动业务逻辑，仅补充文件级职责与维护注释模板。
 * - 用途：
 *   1) 帮助维护者快速理解文件职责、变更背景与风险点。
 *
 * 【段内说明】
 * - 复杂方法补充“干什么 / 边界 / 线程侧”精简中文注释。
 *
 * 【变更记录 #2】2026-07-19 21:49:23（第 2 次备注 · revision 35）
 * - 删除：
 *   1) 删除公开字段直接持有可变 EnumMap 的写入口，外部代码不能再增删或清空退役仓室映射。
 *   2) 未删除 init 入口及兼容映射字段，机器初始化调用链保持不变。
 * - 新增：
 *   1) 新增私有可变仓室 Map，仅允许本类在初始化期维护。
 *   2) 公开 HONKAI_HATCHES 改为不可变动态视图，保留旧代码的只读兼容能力。
 * - 修改：
 *   1) init 改为清理私有 Map，不再经公开引用修改内部状态。
 *   2) 封装退役仓室占位状态，防止外部误写伪造未注册的 MachineDefinition 映射。
 * - 用途：
 *   1) 本文件继续作为五种已退役崩坏能仓室的兼容占位入口，不注册方块、物品或部件。
 *   2) 关键风险点是旧结构扫描读取兼容；公开视图保持 Map 类型和实时内容，读取行为不变。
 */
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
