package com.sirin.hk3gtl.test.industry;

import com.sirin.hk3gtl.common.recipe.main.Hk3MainMaterialAccess;
import com.sirin.hk3gtl.common.recipe.main.Hk3MainMaterialUnits;

/**
 * 【文件职责】主材形态/回收守恒、启动豁免与前阶继承的纯Java合同验证。
 * 【变更记录 #1】2026-10-17 16:37:41（第1次备注 · 修订165）
 * - 删除：无。新增：七形态回收、六种守恒转换、75%循环上限、错误倍增和非法电压负例。
 * - 修改：不加载Forge或游戏注册表；MAX启动条件与工业量产研究条件分别验证。
 * - 用途：防止首制/工业研究自锁与材料增殖；不是完整原子质量模型，也不是游戏实机验收。
 */
public final class MainMaterialUnitTest {
    private static int assertions;

    public static void main(String[] args) {
        units();
        access();
        System.out.println("主材料合同通过：" + assertions + "项断言；未进行游戏加工验收。");
    }

    private static void units() {
        String[] forms = {"billet", "plate", "rod", "fine_wire", "ring", "foil", "frame"};
        for (String form : forms) {
            int units = Hk3MainMaterialUnits.perItem(form);
            int pieces = units < 144 ? 144 / units : 1;
            int scrap = units > 144 ? units / 144 : 1;
            Hk3MainMaterialUnits.requireConversion(form, pieces, "classified_scrap", scrap); assertions++;
        }
        Hk3MainMaterialUnits.requireConversion("billet", 2, "rod", 4); assertions++;
        Hk3MainMaterialUnits.requireConversion("rod", 1, "ring", 2); assertions++;
        Hk3MainMaterialUnits.requireConversion("rod", 1, "fine_wire", 4); assertions++;
        Hk3MainMaterialUnits.requireConversion("plate", 1, "foil", 4); assertions++;
        Hk3MainMaterialUnits.requireConversion("rod", 8, "frame", 1); assertions++;

        long input = Hk3MainMaterialUnits.amount("classified_scrap", 8);
        long recovered = Hk3MainMaterialUnits.amount("recovered_fraction", 48);
        long tailings = Hk3MainMaterialUnits.amount("unrecoverable_tailings", 16);
        Hk3MainMaterialUnits.requireBalanced(input, recovered + tailings); assertions++;
        check(recovered * 4 == input * 3, "回收不能超过75%");
        Hk3MainMaterialUnits.requireConversion("recovered_fraction", 48, "billet", 6); assertions++;

        reject(() -> Hk3MainMaterialUnits.requireConversion("rod", 1, "ring", 4));
        reject(() -> Hk3MainMaterialUnits.requireConversion("rod", 1, "fine_wire", 8));
        reject(() -> Hk3MainMaterialUnits.requireConversion("foil", 1, "billet", 1));
        reject(() -> Hk3MainMaterialUnits.requireConversion("rod", 4, "frame", 1));
        reject(() -> Hk3MainMaterialUnits.amount("plate", 0));
        reject(() -> Hk3MainMaterialUnits.amount("plate", -1));
        reject(() -> Hk3MainMaterialUnits.perItem("stage_9"));
        reject(() -> Hk3MainMaterialUnits.perItem(null));
    }

    private static void access() {
        check(Hk3MainMaterialAccess.requirements(15, 14).isEmpty(), "HBV的MAX首制不得要求研究");
        check(!Hk3MainMaterialAccess.requirements(15, 15).isEmpty(), "HBV工业量产必须保留研究");
        for (int tier = 16; tier <= 30; tier++) {
            check(Hk3MainMaterialAccess.productionPowerTier(tier) == tier - 1, "后阶首制必须继承前阶加工能力");
            check(!Hk3MainMaterialAccess.requirements(tier, tier - 1).isEmpty(), "不能跳过主材专属研究");
            Hk3MainMaterialAccess.validateOperation(tier, tier); assertions++;
            final int target = tier;
            reject(() -> Hk3MainMaterialAccess.validateOperation(target, 14));
            reject(() -> Hk3MainMaterialAccess.validateOperation(target, target - 2));
        }
        check(!Hk3MainMaterialAccess.requirements(23, 22).contains("RN-IAA"), "IMV不能预付ICV电路解锁自身");
        check(!Hk3MainMaterialAccess.requirements(24, 23).contains("RN-IAA"), "ICV不能预付本级电路解锁主材");
        check(Hk3MainMaterialAccess.requirements(29, 28).contains("RN-IAA"), "CIV四系统合仍保留独立锚定研究");
        reject(() -> Hk3MainMaterialAccess.validateOperation(14, 14));
        reject(() -> Hk3MainMaterialAccess.validateOperation(31, 30));
        reject(() -> Hk3MainMaterialAccess.validateOperation(15, 13));
        reject(() -> Hk3MainMaterialAccess.validateOperation(15, 16));
    }

    private static void check(boolean result, String message) {
        if (!result) throw new AssertionError(message);
        assertions++;
    }

    private static void reject(Runnable action) {
        try { action.run(); } catch (IllegalArgumentException expected) { assertions++; return; }
        throw new AssertionError("非法输入或越阶加工未被拒绝");
    }
}
