package com.sirin.hk3gtl.client.compat;

import com.gregtechceu.gtceu.api.capability.recipe.FluidRecipeCapability;
import com.gregtechceu.gtceu.api.capability.recipe.ItemRecipeCapability;
import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.gregtechceu.gtceu.api.recipe.content.Content;
import com.gregtechceu.gtceu.api.recipe.ingredient.FluidIngredient;
import com.gregtechceu.gtceu.api.recipe.ingredient.SizedIngredient;
import com.lowdragmc.lowdraglib.side.fluid.FluidStack;
import com.sirin.hk3gtl.common.research.Hk3ResearchRecipeRuntime;
import com.sirin.hk3gtl.common.worldbubble.Hk3WorldMiningRewards;
import com.sirin.hk3gtl.common.worldbubble.Hk3WorldResourceCatalog;
import com.sirin.hk3gtl.common.worldbubble.Hk3WorldResourceCatalog.Entry;
import com.sirin.hk3gtl.common.worldbubble.Hk3WorldRuntimeCatalog;
import net.minecraft.client.Minecraft;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.StringTag;
import net.minecraft.network.chat.Component;
import net.minecraftforge.common.crafting.CompoundIngredient;
import net.minecraftforge.common.crafting.StrictNBTIngredient;

import java.util.Collection;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.function.Consumer;
import java.util.stream.Collectors;

public final class Hk3WorldMiningJei {
    private Hk3WorldMiningJei() {}

    public static GTRecipe display(GTRecipe recipe) {
        return switch (recipe.data.getString(Hk3ResearchRecipeRuntime.PLAN)) {
            case "industrial_coordinate_solution" -> {
                var view = recipe.copy();
                view.getOutputContents(ItemRecipeCapability.CAP).add(item("hk3gtl:located_real_world_bubble", 10_000));
                yield view;
            }
            case "industrial_unmanned_mining_dispatch" -> mining(recipe);
            default -> recipe;
        };
    }

    private static GTRecipe mining(GTRecipe recipe) {
        var connection = Minecraft.getInstance().getConnection();
        var catalog = Hk3WorldRuntimeCatalog.preview(connection.getRecipeManager(), connection.registryAccess());
        var view = recipe.copy();
        var items = view.getOutputContents(ItemRecipeCapability.CAP);
        items.add(item(Hk3WorldMiningRewards.LEGACY, 10_000));
        items.add(item(Hk3WorldMiningRewards.SHIP, 100));
        items.add(item(Hk3WorldMiningRewards.RELIC, 10_000, "hk3gtl.recipe.world_mining.relic"));
        var itemGroups = catalog.items().stream().collect(Collectors.groupingBy(
                Entry::amount, LinkedHashMap::new, Collectors.toList()));
        pack(itemGroups.values(), Hk3WorldRuntimeCatalog.SAMPLING.itemKinds(), entries -> {
            var alternatives = entries.stream().map(Hk3WorldMiningJei::stack).map(StrictNBTIngredient::of)
                    .toArray(Ingredient[]::new);
            items.add(output(SizedIngredient.create(CompoundIngredient.of(alternatives), entries.get(0).amount()), 10_000));
        });
        var fluids = view.getOutputContents(FluidRecipeCapability.CAP);
        var fluidGroups = catalog.fluids().stream().collect(Collectors.groupingBy(entry -> {
            var data = entry.stackData();
            return entry.amount() + "/" + Hk3WorldResourceCatalog.canonical(data.getCompound("Tag"));
        }, LinkedHashMap::new, Collectors.toList()));
        pack(fluidGroups.values(), Hk3WorldRuntimeCatalog.SAMPLING.fluidKinds(), entries -> {
            var alternatives = entries.stream().map(Hk3WorldMiningJei::fluid).toArray(FluidStack[]::new);
            fluids.add(output(FluidIngredient.of(alternatives), 10_000));
        });
        return view;
    }

    private static void pack(Collection<List<Entry>> groups, int slots, Consumer<List<Entry>> add) {
        int size = groups.stream().mapToInt(List::size).sum();
        int available = slots - groups.size() + 1;
        int perSlot = (size + available - 1) / available;
        for (var entries : groups)
            for (int start = 0; start < entries.size(); start += perSlot)
                add.accept(entries.subList(start, Math.min(start + perSlot, entries.size())));
    }

    private static ItemStack stack(Entry entry) {
        var data = entry.stackData();
        data.putString("id", entry.id());
        data.putByte("Count", (byte) 1);
        return ItemStack.of(data);
    }

    private static FluidStack fluid(Entry entry) {
        var data = entry.stackData();
        data.putString("FluidName", entry.id());
        data.putLong("Amount", entry.amount());
        return FluidStack.loadFromTag(data);
    }

    private static Content item(String id, int chance) {
        return output(SizedIngredient.create(new ItemStack(BuiltInRegistries.ITEM.get(new ResourceLocation(id)))), chance);
    }

    private static Content item(String id, int chance, String tooltip) {
        var stack = new ItemStack(BuiltInRegistries.ITEM.get(new ResourceLocation(id)));
        var lore = new ListTag();
        lore.add(StringTag.valueOf(Component.Serializer.toJson(Component.translatable(tooltip))));
        stack.getOrCreateTagElement("display").put("Lore", lore);
        return output(SizedIngredient.create(stack), chance);
    }

    private static Content output(Object ingredient, int chance) {
        return new Content(ingredient, chance, 10_000, 0, null, null);
    }
}
