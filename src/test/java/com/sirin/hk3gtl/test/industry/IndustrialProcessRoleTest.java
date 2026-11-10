package com.sirin.hk3gtl.test.industry;

import com.sirin.hk3gtl.common.machine.research.Hk3IndustrialProcessRoles;

/** 验证升级能继承前阶，并拒绝更高阶、伪造身份及其他工业职责；不代表游戏运行验收。 */
public final class IndustrialProcessRoleTest {
    public static void main(String[] args) {
        int checks = 0;
        for (int controllerStage = 1; controllerStage <= 4; controllerStage++) {
            for (int recipeStage = 1; recipeStage <= 4; recipeStage++) {
                check(Hk3IndustrialProcessRoles.acceptsCollectionRole("I01-" + recipeStage, controllerStage)
                        == (recipeStage <= controllerStage), "错误采集阶级权限");
                checks++;
            }
            for (String role : new String[]{"I02", "I13", "I01", "I01-0", "I01-5", "I01-01", "i01-1", "I01-1x", "S01"}) {
                check(!Hk3IndustrialProcessRoles.acceptsCollectionRole(role, controllerStage), "错误工业身份：" + role);
                checks++;
            }
        }
        check(!Hk3IndustrialProcessRoles.acceptsCollectionRole(null, 4), "空工艺身份");
        check(!Hk3IndustrialProcessRoles.acceptsCollectionRole("I01-1", 0), "未注册阶段");
        check(!Hk3IndustrialProcessRoles.acceptsCollectionRole("I01-1", 5), "越界注册阶段");
        System.out.println("IndustrialProcessRoleTest: " + (checks + 3) + " checks passed");
    }

    private static void check(boolean value, String message) { if (!value) throw new AssertionError(message); }
}
