package com.sirin.hk3gtl.common.recipe;

import com.sirin.hk3gtl.common.research.*;
import com.sirin.hk3gtl.common.constants.Hk3Values;
import com.sirin.hk3gtl.common.registration.Hk3IndustrialFluids;
import com.google.gson.JsonObject;
import net.minecraft.data.recipes.FinishedRecipe;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.RecipeSerializer;
import com.lowdragmc.lowdraglib.side.fluid.FluidStack;
import java.util.function.Consumer;

public final class Hk3ResearchProcessRecipes {
    private Hk3ResearchProcessRecipes() {}
    public static void register(Consumer<FinishedRecipe> provider){
        com.sirin.hk3gtl.common.recipe.honkai.Hk3ReactorFuelRecipes.register(recipe -> {
            if (!Hk3ApprovedIndustrialPlans.isSuperseded(recipe.getId())) provider.accept(recipe);
        });
        for(var p:Hk3ResearchProcessPlans.all()){
            var type=Hk3ResearchProcessTypes.of(p);
            Hk3RecipeResearchGate.bindAll(type.registryName.getPath(),p.id(),p.requirements());
            if(p.inputHw()>0)com.sirin.hk3gtl.common.capability.Hk3DualEnergyCosts.bindRecipe(
                    type.registryName.getPath(),p.id(),p.inputHw());
            if(p.role().equals("NETWORK_INJECTION"))com.sirin.hk3gtl.common.machine.energy.Hk3HonkaiNetworkInjectorMachine.bindYield(
                    type.registryName.getPath(),p.id(),p.networkCredit());
            save(p, provider);
        }
    }
    public static com.gregtechceu.gtceu.api.recipe.GTRecipe expected(Hk3ResearchProcessPlans.Plan p) {
        var builder = builder(p);
        var recipe = builder.buildRawRecipe();
        var serialized = new com.google.gson.JsonObject();
        builder.toJson(serialized);
        // GTLCore在toJson阶段应用耗时倍率，buildRawRecipe不经过这一步。
        recipe.duration = p.role().equals("I02") ? p.ticks() : serialized.get("duration").getAsInt();
        return recipe;
    }
    private static void save(Hk3ResearchProcessPlans.Plan p, Consumer<FinishedRecipe> provider) {
        builder(p).save(recipe -> {
            if (!p.role().equals("I02")) {
                provider.accept(recipe);
                return;
            }
            provider.accept(new FinishedRecipe() {
                @Override public void serializeRecipeData(JsonObject json) {
                    recipe.serializeRecipeData(json);
                    json.addProperty("duration", p.ticks());
                }
                @Override public ResourceLocation getId() { return recipe.getId(); }
                @Override public RecipeSerializer<?> getType() { return recipe.getType(); }
                @Override public JsonObject serializeAdvancement() { return recipe.serializeAdvancement(); }
                @Override public ResourceLocation getAdvancementId() { return recipe.getAdvancementId(); }
            });
        });
    }
    private static com.gregtechceu.gtceu.data.recipe.builder.GTRecipeBuilder builder(Hk3ResearchProcessPlans.Plan p) {
            var type=Hk3ResearchProcessTypes.of(p);
            long eut=Hk3ResearchProcessTypes.isGenerator(p.role()) ? p.outputEut()
                    : p.inputEut()>0 ? p.inputEut() : Hk3Values.VA_LONG[p.energyTier()];
            var b=type.recipeBuilder(new ResourceLocation("hk3gtl",p.id())).duration(p.ticks())
                    .EUt(Hk3ResearchProcessTypes.isGenerator(p.role())?-eut:eut);
            if(p.inputEut()>0||Hk3ResearchProcessTypes.isGenerator(p.role())||p.id().equals("industrial_lithography_mask"))b.onSave(null);
            for(var item:p.inputs()){
                if(item.id().startsWith("#"))b.inputItems(net.minecraft.tags.TagKey.create(
                        net.minecraft.core.registries.Registries.ITEM,new ResourceLocation(item.id().substring(1))),item.count());
                else b.inputItems(stack(item));
            }
            for(var item:p.outputs())b.outputItems(stack(item));
            for(var output:p.chancedOutputs())b.chancedOutput(stack(output.item()),output.chance(),output.tierChanceBoost());
            for(var item:p.catalysts())b.notConsumable(stack(item));
            if(p.circuit()>0)b.circuitMeta(p.circuit());
            for(var fluid:p.fluidInputs())b.inputFluids(fluid(fluid));for(var fluid:p.fluidOutputs())b.outputFluids(fluid(fluid));
            b.addData(Hk3ResearchRecipeRuntime.PLAN,p.id());
            if(p.inputHw()>=0)b.addData("hk3gtlMergedHonkaiCostPerTick",Long.toString(p.inputHw()));
            if(p.networkCredit()>0)b.addData(com.sirin.hk3gtl.common.machine.research.Hk3LiquidProcessMachine.CREDIT,p.networkCredit());
            return Hk3ResearchProcessTypes.isGenerator(p.role()) ? b
                    : com.sirin.hk3gtl.common.recipe.power.Hk3RecipePower.require(b,p.energyTier());
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
