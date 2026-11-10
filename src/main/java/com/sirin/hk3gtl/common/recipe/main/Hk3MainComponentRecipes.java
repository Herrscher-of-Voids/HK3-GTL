package com.sirin.hk3gtl.common.recipe.main;

import com.gregtechceu.gtceu.api.GTValues;
import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import com.gregtechceu.gtceu.data.recipe.builder.GTRecipeBuilder;
import com.sirin.hk3gtl.common.constants.Hk3Tiers;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.item.Hk3CircuitCatalog;
import com.sirin.hk3gtl.common.item.main.Hk3MainMaterialItems;
import com.sirin.hk3gtl.common.material.main.Hk3MainMaterialCatalog;
import com.sirin.hk3gtl.common.recipe.Hk3ElectronicRecipes;
import com.sirin.hk3gtl.common.recipe.power.Hk3RecipePower;
import com.sirin.hk3gtl.common.research.Hk3ElectronicResearch;
import com.sirin.hk3gtl.common.research.Hk3RecipeResearchGate;
import net.minecraft.data.recipes.FinishedRecipe;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.registries.ForgeRegistries;
import org.gtlcore.gtlcore.common.data.GTLItems;

import java.util.List;
import java.util.function.Consumer;

/**
 * 【文件职责】16阶八大件消费本阶主材料和电子平台，前一阶组件作为不可跳过的装配基件。
 * 【变更记录 #1】2026-10-17 16:26:10（修订165）
 * - 删除：本入口不再沿用通用魂钢巨量压缩及仅有前三族的旧组件配方。
 * - 新增：128条有明确主材形状、功能部件、前级实物和本阶电路的装配路线。
 * - 修改：现有物品ID保持；总入口只调用本类，配方按实际额定电压和完整研究权限执行。
 * - 用途：将主材接入全部八大件；不注册新设备、方块或贴图，不代表第三方机器已通过高阶承载验收。
 */
public final class Hk3MainComponentRecipes {
    public static final List<String> PARTS = List.of("electric_motor", "electric_piston", "electric_pump",
            "conveyor_module", "robot_arm", "field_generator", "emitter", "sensor");

    private Hk3MainComponentRecipes() {}

    /** 注册时拒绝缺项，避免拼错ID悄悄生成空气配方。 */
    public static ItemStack component(int tier, String part, int count) {
        if (!PARTS.contains(part) || count < 1 || count > 64) throw new IllegalArgumentException("非法组件参数");
        if (tier == GTValues.MAX) {
            return switch (part) {
                case "electric_motor" -> GTLItems.ELECTRIC_MOTOR_MAX.asStack(count);
                case "electric_piston" -> GTLItems.ELECTRIC_PISTON_MAX.asStack(count);
                case "electric_pump" -> GTLItems.ELECTRIC_PUMP_MAX.asStack(count);
                case "conveyor_module" -> GTLItems.CONVEYOR_MODULE_MAX.asStack(count);
                case "robot_arm" -> GTLItems.ROBOT_ARM_MAX.asStack(count);
                case "field_generator" -> GTLItems.FIELD_GENERATOR_MAX.asStack(count);
                case "emitter" -> GTLItems.EMITTER_MAX.asStack(count);
                case "sensor" -> GTLItems.SENSOR_MAX.asStack(count);
                default -> throw new IllegalArgumentException("未知MAX组件");
            };
        }
        Hk3MainMaterialCatalog.entry(tier);
        var id = new ResourceLocation("hk3gtl", part + "_" + Hk3Tiers.voltageKey(tier));
        var item = ForgeRegistries.ITEMS.getValue(id);
        if (item == null || item == net.minecraft.world.item.Items.AIR)
            throw new IllegalStateException("组件尚未注册：" + id);
        return new ItemStack(item, count);
    }

    private static GTRecipeBuilder base(int tier, String part) {
        String id = "hk3gtl_main_component_" + Hk3Tiers.voltageKey(tier) + "_" + part;
        var builder = GTRecipeTypes.ASSEMBLER_RECIPES.recipeBuilder(id)
                .EUt(Hk3Values.VA_LONG[tier])
                .duration(800 + 160 * ((tier - Hk3Tiers.HBV) % 4))
                .inputItems(component(tier - 1, part, 2))
                .inputItems(Hk3CircuitCatalog.tag(tier), 2)
                .outputItems(component(tier, part, 1));
        Hk3RecipeResearchGate.bindAll(builder.recipeType.registryName.getPath(), id,
                Hk3ElectronicResearch.requirements((tier - Hk3Tiers.HBV) / 4));
        return Hk3RecipePower.require(builder, tier);
    }

    private static ItemStack shape(int tier, String form, int count) {
        return Hk3MainMaterialItems.stack(tier, form, count);
    }

    public static void register(Consumer<FinishedRecipe> provider) {
        for (var material : Hk3MainMaterialCatalog.entries()) registerTier(material.tier(), provider);
    }

    private static void registerTier(int tier, Consumer<FinishedRecipe> provider) {
        int p = (tier - Hk3Tiers.HBV) / 4;
        base(tier, "electric_motor")
                .inputItems(shape(tier, "fine_wire", 16), shape(tier, "rod", 4), shape(tier, "ring", 2))
                .inputItems(Hk3ElectronicRecipes.part(p, "dielectric_film", 4)).save(provider);
        base(tier, "electric_piston")
                .inputItems(component(tier, "electric_motor", 1))
                .inputItems(shape(tier, "rod", 4), shape(tier, "plate", 4), shape(tier, "ring", 2)).save(provider);
        base(tier, "electric_pump")
                .inputItems(component(tier, "electric_motor", 1))
                .inputItems(shape(tier, "ring", 4), shape(tier, "plate", 2), shape(tier, "foil", 8)).save(provider);
        base(tier, "conveyor_module")
                .inputItems(component(tier, "electric_motor", 2))
                .inputItems(shape(tier, "plate", 4), shape(tier, "foil", 8))
                .inputItems(Hk3ElectronicRecipes.part(p, "interconnect_mesh", 2)).save(provider);
        base(tier, "robot_arm")
                .inputItems(component(tier, "electric_motor", 2), component(tier, "electric_piston", 1))
                .inputItems(shape(tier, "rod", 4))
                .inputItems(Hk3ElectronicRecipes.part(p, "printed_circuit_board", 2)).save(provider);
        base(tier, "field_generator")
                .inputItems(shape(tier, "frame", 2), shape(tier, "fine_wire", 16), shape(tier, "foil", 8))
                .inputItems(Hk3ElectronicRecipes.part(p, "cpu", 2)).save(provider);
        base(tier, "emitter")
                .inputItems(shape(tier, "rod", 2), shape(tier, "foil", 8))
                .inputItems(Hk3ElectronicRecipes.part(p, "cpu", 1), Hk3ElectronicRecipes.part(p, "logic_die", 2)).save(provider);
        base(tier, "sensor")
                .inputItems(shape(tier, "plate", 2), shape(tier, "ring", 2))
                .inputItems(Hk3ElectronicRecipes.part(p, "cpu", 1), Hk3ElectronicRecipes.part(p, "ram_chip", 4)).save(provider);
    }
}
