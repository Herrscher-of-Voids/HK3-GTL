package com.sirin.hk3gtl.common.machine.research;

/** 【变更记录 #4】2026-10-26 19:57:03（修订177）：允许高阶专用执行器继承固定工艺身份；既有设备行为不变。 */


import com.gregtechceu.gtceu.api.machine.IMachineBlockEntity;

/**
 * 【变更记录 #1】2026-09-29 · 修订101。
 * 删除：无。新增：带固定工艺身份的执行器。修改：不加入机器注册表。
 * 用途：结构逐台通过审核后可绑定对应工艺，不用旧小结构冒充新机器。
 */
/**
 * 【变更记录 #2】2026-09-29 23:37:35（内测5修订101）
 * 删除：本轮被替代的单前置或旧提示分支；其余历史保留。
 * 新增／修改：提供后续工艺设备专用执行类；本轮未注册控制器或结构。
 * 用途：补足研究接线并如实保留未接物理执行器及结构审批边界。
 * 追溯：logs/research-mainline-r101；R101_FINAL_RECORD。
 */
/** 【变更记录 #3】2026-10-15 01:12:48（修订156）：批准工业控制器实际绑定固定工艺身份，跨类型搜索保留原类型。 */
public class Hk3ResearchProcessMachine extends Hk3LiquidProcessMachine
        implements com.sirin.hk3gtl.common.machine.IMultiTypeRecipeMachine {
    private final String researchRole;
    public Hk3ResearchProcessMachine(IMachineBlockEntity holder,String role){super(holder);researchRole=role;}
    public String researchRole(){return researchRole;}
    /** 2026-10-15：批准执行器按注册定义保留旧类型，实际身份仍固定为单一工业职责。 */
    @Override public java.util.List<com.gregtechceu.gtceu.api.recipe.GTRecipeType> getExtendRecipeTypes() {
        return java.util.List.of(getDefinition().getRecipeTypes());
    }
}
