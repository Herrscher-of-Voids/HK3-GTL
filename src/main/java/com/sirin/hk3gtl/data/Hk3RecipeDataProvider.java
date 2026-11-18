package com.sirin.hk3gtl.data;

import com.sirin.hk3gtl.common.recipe.Hk3RecipeAdder;
import net.minecraft.data.PackOutput;
import net.minecraft.data.recipes.FinishedRecipe;
import net.minecraft.data.recipes.RecipeProvider;
import net.minecraftforge.data.event.GatherDataEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.util.function.Consumer;

@Mod.EventBusSubscriber(modid = "hk3gtl", bus = Mod.EventBusSubscriber.Bus.MOD)
public final class Hk3RecipeDataProvider extends RecipeProvider {
    public Hk3RecipeDataProvider(PackOutput output) {
        super(output);
    }

    @SubscribeEvent
    public static void gatherData(GatherDataEvent event) {
        event.getGenerator().addProvider(event.includeServer(),
                new Hk3RecipeDataProvider(event.getGenerator().getPackOutput()));
    }

    @Override
    protected void buildRecipes(Consumer<FinishedRecipe> provider) {
        Hk3RecipeAdder.addRecipes(provider);
    }
}
