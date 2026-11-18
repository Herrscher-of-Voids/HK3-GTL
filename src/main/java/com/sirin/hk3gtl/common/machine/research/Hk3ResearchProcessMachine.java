package com.sirin.hk3gtl.common.machine.research;




import com.gregtechceu.gtceu.api.machine.IMachineBlockEntity;














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
