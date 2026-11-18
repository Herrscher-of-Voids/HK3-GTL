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
        move(item, "item_in_0", 68, 0);
        for (int i = 1; i < 4; i++)
            children.add(move(item.copy(), "item_in_" + i, 68 + i * 18, 0));
        children.add(move(fluid.copy(), "fluid_in_0", 140, 0));

        var progress = widget(children, "progress");
        move(progress, "progress", 103, 19).getCompound("data").getCompound("size").putInt("height", 18);
        int byproductY = root.getCompound("size").getInt("height") + 2;
        for (int i = 0; i < ITEM_BYPRODUCTS; i++)
            children.add(move(item.copy(), "item_out_" + i, 59 + i * 18, byproductY));
        children.add(move(fluid, "fluid_out_0", 149, byproductY));
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
