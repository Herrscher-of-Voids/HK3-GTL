package com.sirin.hk3gtl.common.recipe.machine;

import com.gregtechceu.gtceu.data.recipe.VanillaRecipeHelper;
import com.sirin.hk3gtl.common.item.main.Hk3MainMaterialItems;
import com.sirin.hk3gtl.common.material.main.Hk3MainMaterialCatalog;
import com.sirin.hk3gtl.common.registration.Hk3IndustrialContent;
import net.minecraft.data.recipes.FinishedRecipe;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import java.util.Locale;
import java.util.function.Consumer;

/**
 * 【文件职责】提供16种建筑机壳装配配方；颜色不代表电压处理能力。
 * 【变更记录 #1】2026-10-01 21:51:39（第1次备注 · 内测5修订152）
 * 删除：无。新增：6钢板+1钢框架，电路配置1—16，32EU/t、5秒产出2块。
 * 修改：无既有配方替换。用途：统一建筑材料成本，不强制以同级电路消耗装饰方块。
 */
/**
 * 【变更记录 #2】2026-10-17 16:28:36（第2次备注 · 修订165）
 * - 删除：6钢板、1钢框架、配置电路装配出2块的全部16条旧入口，不保留钢料旁路。
 * - 新增：工作台3×3同级主材板围外圈、中心为空、每次产1块的16条配方。
 * - 修改：材料与机壳级别从统一十六阶目录读取，不能将错级板材混用或由颜色推断电压。
 * - 用途：连接本级专属成板产物与既有机壳身份；只改变配方，不批准新方块或建筑改色。
 */
public final class Hk3VoltageCasingRecipes {
    private Hk3VoltageCasingRecipes() {}
    public static void register(Consumer<FinishedRecipe> provider) {
        for (var entry : Hk3MainMaterialCatalog.entries()) {
            String id = "voltage_machine_casing_" + entry.voltage().toLowerCase(Locale.ROOT);
            var block = Hk3IndustrialContent.blocks().get(id);
            if (block == null) throw new IllegalStateException("本级机械机壳未注册：" + id);
            VanillaRecipeHelper.addShapedRecipe(provider, new ResourceLocation("hk3gtl", id),
                    new ItemStack(block.get().asItem(), 1), "PPP", "P P", "PPP",
                    'P', Hk3MainMaterialItems.stack(entry.tier(), "plate", 1));
        }
    }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
