package com.sirin.hk3gtl.common.recipe;

import com.gregtechceu.gtceu.api.recipe.GTRecipeType;
import com.gregtechceu.gtceu.api.recipe.ui.GTRecipeTypeUI;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import org.gtlcore.gtlcore.common.data.GTLRecipeTypes;

final class Hk3WorldMiningRecipeUI extends GTRecipeTypeUI {
    private static final int ITEM_BYPRODUCTS = 5;
    private final String recipeTypeId;
    private CompoundTag template;

    Hk3WorldMiningRecipeUI(GTRecipeType recipeType) {
        super(recipeType);
        recipeTypeId = recipeType.registryName.toString();
    }

    @Override public CompoundTag getCustomUI() {
        if (template != null) return template;
        var layout = GTLRecipeTypes.COSMOS_SIMULATION_RECIPES.getRecipeUI().getCustomUI().copy();
        if (layout.isEmpty()) return super.getCustomUI();
        layout.putString("recipe_type", recipeTypeId);
        var root = layout.getCompound("root");
        var children = root.getList("children", Tag.TAG_COMPOUND);
        var item = widget(children, "item_in_0");
        var fluid = widget(children, "fluid_out_0").copy();
        offsetOutputs(children);
        var mining = Hk3ResearchProcessPlans.all().stream().filter(p -> p.id().equals("industrial_unmanned_mining_dispatch")).findFirst().orElseThrow();
        int items = mining.inputs().size() + mining.catalysts().size() + (mining.circuit() > 0 ? 1 : 0);
        int extraHeight = 18 * ((items + mining.fluidInputs().size() - 1) / 8);
        for (var raw : children) {
            var pos = ((CompoundTag) raw).getCompound("data").getCompound("selfPosition");
            pos.putInt("y", pos.getInt("y") + extraHeight);
        }
        move(item, "item_in_0", 32, 0);
        for (int i = 1; i < items; i++)
            children.add(move(item.copy(), "item_in_" + i, 32 + i % 8 * 18, i / 8 * 18));
        for (int i = 0; i < mining.fluidInputs().size(); i++) {
            int slot = items + i;
            children.add(move(fluid.copy(), "fluid_in_" + i, 32 + slot % 8 * 18, slot / 8 * 18));
        }
        var progress = widget(children, "progress");
        move(progress, "progress", 103, 19 + extraHeight).getCompound("data").getCompound("size").putInt("height", 18);
        int byproductY = root.getCompound("size").getInt("height") + extraHeight + 2;
        for (int i = 0; i < ITEM_BYPRODUCTS; i++)
            children.add(move(item.copy(), "item_out_" + i, 50 + i * 18, byproductY));
        children.add(move(fluid, "fluid_out_0", 158, byproductY));
        root.getCompound("size").putInt("height", byproductY + 21);
        return template = layout;
    }

    @Override public void reloadCustomUI() {
        template = null;
        super.reloadCustomUI();
    }

    private static CompoundTag widget(ListTag children, String id) {
        return children.stream().map(CompoundTag.class::cast)
                .filter(child -> child.getCompound("data").getString("id").equals(id)).findFirst().orElseThrow();
    }

    private static void offsetOutputs(ListTag children) {
        for (var raw : children) {
            var data = ((CompoundTag) raw).getCompound("data");
            String id = data.getString("id");
            for (String prefix : new String[]{"item_out_", "fluid_out_"})
                if (id.startsWith(prefix)) {
                    int offset = prefix.equals("item_out_") ? ITEM_BYPRODUCTS : 1;
                    data.putString("id", prefix + (Integer.parseInt(id.substring(prefix.length())) + offset));
                }
            if (data.contains("children")) offsetOutputs(data.getList("children", Tag.TAG_COMPOUND));
        }
    }

    private static CompoundTag move(CompoundTag widget, String id, int x, int y) {
        var data = widget.getCompound("data");
        data.putString("id", id);
        var pos = data.getCompound("selfPosition");
        pos.putInt("x", x);
        pos.putInt("y", y);
        return widget;
    }
}
