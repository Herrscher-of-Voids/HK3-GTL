package com.sirin.hk3gtl.common.research;

import com.gregtechceu.gtceu.api.capability.recipe.ItemRecipeCapability;
import com.gregtechceu.gtceu.api.machine.feature.IRecipeLogicMachine;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.gregtechceu.gtceu.api.recipe.ingredient.SizedIngredient;
import com.gregtechceu.gtceu.common.data.GTRecipeTypes;
import com.gregtechceu.gtceu.data.recipe.CustomTags;
import com.sirin.hk3gtl.common.easter.Hk3EggProduction;
import com.sirin.hk3gtl.common.machine.Hk3WorkableMultiblockMachine;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraftforge.common.crafting.StrictNBTIngredient;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.util.Locale;
import java.util.UUID;






@Mod.EventBusSubscriber(modid = "hk3gtl", bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class Hk3CircuitTechnology {
    private Hk3CircuitTechnology() {}

    @SubscribeEvent
    public static void crafted(PlayerEvent.ItemCraftedEvent event) {
        if (event.getEntity() instanceof ServerPlayer player && !event.getCrafting().isEmpty()) {
            String tier = tier(event.getCrafting());
            if (tier != null) Hk3ResearchData.get(player).recordCircuitTechnology(
                    Hk3ResearchTeams.scope(player.server, player.getUUID()), tier);
        }
    }

    public static void settled(IRecipeLogicMachine logic, GTRecipe recipe) {
        if (recipe.recipeType != GTRecipeTypes.ASSEMBLER_RECIPES
                && recipe.recipeType != GTRecipeTypes.CIRCUIT_ASSEMBLER_RECIPES
                && recipe.recipeType != GTRecipeTypes.ASSEMBLY_LINE_RECIPES
                || logic.canVoidRecipeOutputs(ItemRecipeCapability.CAP)) return;
        var machine = logic.self();
        if (!(machine.getLevel() instanceof ServerLevel level)
                || !(machine.getHolder() instanceof BlockEntity holder)) return;
        UUID owner = machine instanceof Hk3WorkableMultiblockMachine owned ? owned.getOwnerUUID()
                : holder.getPersistentData().hasUUID(Hk3EggProduction.OWNER)
                    ? holder.getPersistentData().getUUID(Hk3EggProduction.OWNER) : null;
        if (owner == null) return;
        for (var content : recipe.getOutputContents(ItemRecipeCapability.CAP)) {
            if (content.maxChance <= 0 || content.chance < content.maxChance) continue;
            var output = ItemRecipeCapability.CAP.of(content.content);
            if (!fixed(output)) continue;
            var stacks = output.getItems();
            if (stacks.length != 1 || stacks[0].isEmpty()) continue;
            String tier = tier(stacks[0]);
            if (tier == null) continue;
            UUID scope = machine instanceof Hk3WorkableMultiblockMachine owned
                    ? owned.getResearchTeamUUID() : Hk3ResearchTeams.scope(level.getServer(), owner);
            if (scope != null) Hk3ResearchData.get(level.getServer()).recordCircuitTechnology(scope, tier);
        }
    }

    private static boolean fixed(Ingredient ingredient) {
        while (ingredient.getClass() == SizedIngredient.class)
            ingredient = ((SizedIngredient) ingredient).getInner();
        return ingredient.getClass() == Ingredient.class || ingredient.getClass() == StrictNBTIngredient.class;
    }

    private static String tier(ItemStack stack) {
        for (var tag : CustomTags.CIRCUITS_ARRAY) {
            if (stack.is(tag)) return tag.location().getPath().substring("circuits/".length()).toLowerCase(Locale.ROOT);
        }
        return null;
    }
}
