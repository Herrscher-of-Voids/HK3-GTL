package com.sirin.hk3gtl.common.recipe;



/** 新配方静态容量约束；仅指已注册配方类型槽数，不批准任何物理结构。 */
/**
 * 【变更记录 #1】2026-09-29 23:37:35（内测5修订101）
 * 删除：本轮被替代的单前置或旧提示分支；其余历史保留。
 * 新增／修改：集中定义已有及待接工艺类型的槽位容量，不等同物理端口审批。
 * 用途：补足研究接线并如实保留未接物理执行器及结构审批边界。
 * 追溯：logs/research-mainline-r101；R101_FINAL_RECORD。
 */
/**
 * 【变更记录 #2】2026-09-30 00:01:44（内测5修订102）
 * 删除：消耗并重造原图纸的路径。新增／修改：模板也计入输入槽容量，避免JEI槽位溢出。
 * 用途：落实已确认的图纸成本，保留非消耗模板；新结构与物品来源交付另行接入。
 */
public final class Hk3ResearchProcessPorts {
    private Hk3ResearchProcessPorts() {}
    public record Ports(int itemsIn,int itemsOut,int fluidsIn,int fluidsOut) {}
    public static Ports get(String role){
        return switch(role){
            case "GT_ASSEMBLER" -> new Ports(9,1,1,0);
            case "GT_MIXER" -> new Ports(6,1,2,1);
            case "GT_CHEMICAL" -> new Ports(2,2,3,2);
            case "I01-1" -> new Ports(6,4,2,3);
            case "I02" -> new Ports(6,4,2,2);
            case "I07" -> new Ports(8,4,0,0);
            case "I11" -> new Ports(12,6,2,2);
            case "I12" -> new Ports(8,4,3,2);
            case "I16" -> new Ports(12,8,4,4);
            case "I33" -> new Ports(12,4,2,2);
            default -> {
                if(!role.matches("I(0[3-9]|[1-3][0-9]|4[0-5])|I01-[234]"))
                    throw new IllegalArgumentException("Unknown recipe role "+role);
                yield new Ports(8,6,4,4);
            }
        };
    }
    public static void validate(Hk3ResearchProcessPlans.Plan p){
        var limit=get(p.role());
        if(p.inputs().size()+p.catalysts().size()>limit.itemsIn()||p.outputs().size()>limit.itemsOut()
                ||p.fluidInputs().size()>limit.fluidsIn()||p.fluidOutputs().size()>limit.fluidsOut())
            throw new IllegalArgumentException("Recipe exceeds registered ports "+p.id());
    }
}
