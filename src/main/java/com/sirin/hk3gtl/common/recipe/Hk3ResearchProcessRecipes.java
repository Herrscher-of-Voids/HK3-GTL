package com.sirin.hk3gtl.common.recipe;



import com.sirin.hk3gtl.common.research.*;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.registration.Hk3IndustrialFluids;
import net.minecraft.data.recipes.FinishedRecipe;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.world.item.ItemStack;
import com.lowdragmc.lowdraglib.side.fluid.FluidStack;
import java.util.function.Consumer;

/**
 * 【变更记录 #1】2026-09-29 · 修订101。
 * 删除：无。新增：样件制造、破坏性检测、研究后工业配方。
 * 修改：数量来自公开的暂定平衡表；用途：真实耗料耗电后才可结算证据。
 */
/**
 * 【变更记录 #2】2026-09-29 23:37:35（内测5修订101）
 * 删除：本轮被替代的单前置或旧提示分支；其余历史保留。
 * 新增／修改：注册暂定样件、检测和生产配方；按长整数电压计费，未知物料拒绝加载。
 * 用途：补足研究接线并如实保留未接物理执行器及结构审批边界。
 * 追溯：logs/research-mainline-r101；R101_FINAL_RECORD。
 */
/**
 * 【变更记录 #3】2026-09-30 00:01:44（内测5修订102）
 * 删除：消耗并重造原图纸的路径。新增／修改：把模板注册为GT非消耗输入，不销毁原图纸的NBT。
 * 用途：落实已确认的图纸成本，保留非消耗模板；新结构与物品来源交付另行接入。
 */
/**
 * 【变更记录 #4】2026-09-30 00:54:00（第4次备注 · 内测5修订103）
 * 删除：重复构造逻辑。新增：不写注册表、不绑定门槛的期望配方构造入口。
 * 修改：注册与实际实例核验共用同一数值解析；用途：检测脚本覆盖、资源缺失与运行时门槛差异。
 */
/**
 * 【变更记录 #5】2026-09-30 01:42:00（第5次备注 · 内测5修订106）
 * - 删除：核验只读取原始耗时的假设；新增：独立构造器toJson的实例序列化耗时。
 * - 修改：仅预期耗时沿用GTLCore配置及发电豁免；其余字段来自批准配方。
 * - 用途：修复增强版0.2倍耗时误报；不调用save，不注册配方，不更改实例配置。
 */
public final class Hk3ResearchProcessRecipes {
    private Hk3ResearchProcessRecipes() {}
    public static void register(Consumer<FinishedRecipe> provider){
        for(var p:Hk3ResearchProcessPlans.all()){
            var type=Hk3ResearchProcessTypes.get(p.role());
            Hk3RecipeResearchGate.bindAll(type.registryName.getPath(),p.id(),p.requirements());
            builder(p).save(provider);
        }
    }
    public static com.gregtechceu.gtceu.api.recipe.GTRecipe expected(Hk3ResearchProcessPlans.Plan p) {
        var builder = builder(p);
        var recipe = builder.buildRawRecipe();
        var serialized = new com.google.gson.JsonObject();
        builder.toJson(serialized);
        // GTLCore在toJson阶段应用耗时倍率，buildRawRecipe不经过这一步。
        recipe.duration = serialized.get("duration").getAsInt();
        return recipe;
    }
    private static com.gregtechceu.gtceu.data.recipe.builder.GTRecipeBuilder builder(Hk3ResearchProcessPlans.Plan p) {
            var type=Hk3ResearchProcessTypes.get(p.role());
            long eut=Hk3Values.VA_LONG[p.energyTier()];
            var b=type.recipeBuilder(new ResourceLocation("hk3gtl",p.id())).duration(p.ticks())
                    .EUt(Hk3ResearchProcessTypes.isGenerator(p.role())?-eut:eut);
            for(var item:p.inputs())b.inputItems(stack(item));for(var item:p.outputs())b.outputItems(stack(item));
            for(var item:p.catalysts())b.notConsumable(stack(item));
            for(var fluid:p.fluidInputs())b.inputFluids(fluid(fluid));for(var fluid:p.fluidOutputs())b.outputFluids(fluid(fluid));
            if(!p.role().startsWith("GT_"))b.addData(Hk3ResearchRecipeRuntime.PLAN,p.id());
            return b;
    }
    private static ItemStack stack(Hk3ResearchProcessPlans.Item value){
        // 魂钢由材料系统注册，直接解析前缀，避免猜测GT生成物品的命名空间。
        if(value.id().startsWith("material:soulium/")) {
            var prefix=switch(value.id().substring("material:soulium/".length())) {
                case "plate" -> com.gregtechceu.gtceu.api.data.tag.TagPrefix.plate;
                case "fine_wire" -> com.gregtechceu.gtceu.api.data.tag.TagPrefix.wireFine;
                case "ingot" -> com.gregtechceu.gtceu.api.data.tag.TagPrefix.ingot;
                default -> throw new IllegalArgumentException("Unknown soulium form "+value.id());
            };
            var stack=com.gregtechceu.gtceu.api.data.chemical.ChemicalHelper.get(prefix,
                    com.sirin.hk3gtl.common.material.SouliumMaterial.SOULIUM,value.count());
            if(stack.isEmpty())throw new IllegalArgumentException("Unregistered soulium form "+value.id());
            return stack;
        }
        var id=new ResourceLocation(value.id());if(!BuiltInRegistries.ITEM.containsKey(id))throw new IllegalArgumentException("Unknown process item "+id);
        return new ItemStack(BuiltInRegistries.ITEM.get(id),value.count());
    }
    private static FluidStack fluid(Hk3ResearchProcessPlans.Fluid value){
        if(value.id().contains(":")){
            var id=new ResourceLocation(value.id());if(!BuiltInRegistries.FLUID.containsKey(id))throw new IllegalArgumentException("Unknown process fluid "+id);
            return FluidStack.create(BuiltInRegistries.FLUID.get(id),value.amount());
        }
        var material=Hk3IndustrialFluids.materials().get(value.id());if(material==null)throw new IllegalArgumentException("Unknown process fluid "+value.id());
        return material.getFluid(value.amount());
    }
}

// 【变更记录 · 修订161】2026-10-17 14:11:55：本轮仅将活动类名、资源与工业配方引用迁移为长期业务命名；历史备注保留，不代表旧逻辑已全部按现行设计重写。
