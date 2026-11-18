package com.sirin.hk3gtl.common.narrative.story;

import com.gregtechceu.gtceu.api.capability.recipe.ItemRecipeCapability;
import com.gregtechceu.gtceu.api.machine.feature.IRecipeLogicMachine;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.gregtechceu.gtceu.api.recipe.ingredient.SizedIngredient;
import com.sirin.hk3gtl.common.easter.Hk3EggProduction;
import com.sirin.hk3gtl.common.machine.Hk3WorkableMultiblockMachine;
import com.sirin.hk3gtl.common.research.Hk3ResearchTeams;
import java.util.Map;
import java.util.UUID;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraftforge.common.crafting.StrictNBTIngredient;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = "hk3gtl")
public final class Hk3StoryProduction {
    private static final Map<String, String> OUTPUTS = Map.of(
            "expatternprovider:fishbig", "fishbig_manufactured",
            "gtceu:creative_tank", "creative_tank_completed",
            "gtceu:creative_chest", "creative_chest_completed");

    private Hk3StoryProduction() {}

    @SubscribeEvent
    public static void crafted(PlayerEvent.ItemCraftedEvent event) {
        if (event.getEntity() instanceof ServerPlayer player && !player.isCreative() && !player.isSpectator())
            produced(player.server, Hk3ResearchTeams.scope(player.server, player.getUUID()), event.getCrafting());
    }

    public static void settled(IRecipeLogicMachine logic, GTRecipe recipe) {
        if (logic.canVoidRecipeOutputs(ItemRecipeCapability.CAP)) return;
        var machine = logic.self();
        if (!(machine.getLevel() instanceof ServerLevel level)
                || !(machine.getHolder() instanceof BlockEntity holder)) return;
        UUID owner = machine instanceof Hk3WorkableMultiblockMachine owned ? owned.getOwnerUUID()
                : holder.getPersistentData().hasUUID(Hk3EggProduction.OWNER)
                    ? holder.getPersistentData().getUUID(Hk3EggProduction.OWNER) : null;
        if (owner == null) return;
        UUID team = machine instanceof Hk3WorkableMultiblockMachine owned
                ? owned.getResearchTeamUUID() : Hk3ResearchTeams.scope(level.getServer(), owner);
        if (team == null) return;
        for (var content : recipe.getOutputContents(ItemRecipeCapability.CAP)) {
            if (content.maxChance <= 0 || content.chance < content.maxChance) continue;
            var ingredient = ItemRecipeCapability.CAP.of(content.content);
            if (!fixed(ingredient)) continue;
            var stacks = ingredient.getItems();
            if (stacks.length == 1 && !stacks[0].isEmpty()) produced(level.getServer(), team, stacks[0]);
        }
    }

    private static boolean fixed(Ingredient ingredient) {
        while (ingredient.getClass() == SizedIngredient.class)
            ingredient = ((SizedIngredient) ingredient).getInner();
        return ingredient.getClass() == Ingredient.class || ingredient.getClass() == StrictNBTIngredient.class;
    }

    private static void produced(MinecraftServer server, UUID team, ItemStack stack) {
        String event = OUTPUTS.get(BuiltInRegistries.ITEM.getKey(stack.getItem()).toString());
        if (event != null) Hk3StoryService.teamFact(server, team, event);
    }
}
