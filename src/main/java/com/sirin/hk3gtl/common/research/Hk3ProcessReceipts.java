package com.sirin.hk3gtl.common.research;

import com.gregtechceu.gtceu.api.recipe.GTRecipe;
import com.gregtechceu.gtceu.api.capability.recipe.ItemRecipeCapability;
import com.gregtechceu.gtceu.api.capability.recipe.FluidRecipeCapability;
import net.minecraft.nbt.*;
import net.minecraft.resources.ResourceLocation;
import java.util.UUID;

public final class Hk3ProcessReceipts {
    private Hk3ProcessReceipts() {}
    public static final String RECEIPTS = "hk3gtlProcessReceipts";
    public static String category(GTRecipe recipe) {
        String id = recipe.id.getPath();
        if (id.equals("industrial_liquid_honkai_refining/approved_hbv_c02")) return "medium";
        if (id.equals("industrial_liquid_honkai_refining/approved_hbv_c03")) return "heat";
        if (!id.startsWith("industrial_medium_regeneration/")) return "";
        if (id.endsWith("/industrial_stabilization_medium_recovery")) return "medium";
        if (id.endsWith("/industrial_heat_exchange")) return "heat";
        if (id.endsWith("/industrial_spent_rod_reprocessing") || id.endsWith("/approved_hdv_p25")) return "spent_rods";
        return "";
    }
    public static CompoundTag snapshot(GTRecipe recipe) {
        var result = new CompoundTag();
        result.putString("Category", category(recipe)); result.putString("Recipe", recipe.id.toString());
        result.put("Inputs", contents(recipe, true)); result.put("Outputs", contents(recipe, false));
        return result;
    }
    public static CompoundTag findSnapshot(GTRecipe recipe, ResourceLocation id) {
        if (!recipe.data.contains(Hk3ResearchRecipeRuntime.MERGED))
            return id.equals(recipe.id) ? snapshot(recipe) : null;
        for (var raw : recipe.data.getList(Hk3ResearchRecipeRuntime.MERGED, Tag.TAG_COMPOUND)) {
            var entry = (CompoundTag) raw;
            if (id.toString().equals(entry.getString("Recipe"))) return entry;
        }
        return null;
    }
    public static CompoundTag settle(CompoundTag source, String facility, long tick) {
        var result = source.copy(); result.putString("Facility", facility); result.putLong("Tick", tick);
        result.putUUID("Batch", UUID.nameUUIDFromBytes((facility + "/" + tick + "/" + source.getString("Recipe"))
                .getBytes(java.nio.charset.StandardCharsets.UTF_8)));
        return result;
    }
    private static CompoundTag contents(GTRecipe recipe, boolean input) {
        var result = new CompoundTag(); var items = new ListTag(); var fluids = new ListTag();
        var ic = ItemRecipeCapability.CAP; var fc = FluidRecipeCapability.CAP;
        for (var entry : input ? recipe.getInputContents(ic) : recipe.getOutputContents(ic)) {
            if (entry.chance <= 0) continue;
            var alternatives = new ListTag();
            for (var stack : ic.of(entry.content).getItems()) {var item=stack.save(new CompoundTag());item.putLong("ActualCount",stack.getCount());alternatives.add(item);}
            var line = new CompoundTag(); line.put("Alternatives", alternatives); line.putFloat("Chance", entry.chance);
            items.add(line);
        }
        for (var entry : input ? recipe.getInputContents(fc) : recipe.getOutputContents(fc)) {
            if (entry.chance <= 0) continue;
            var stack = fc.of(entry.content); var line = new CompoundTag();
            var alternatives=new ListTag();
            for(var fluid:stack.getStacks())alternatives.add(StringTag.valueOf(net.minecraft.core.registries.BuiltInRegistries.FLUID.getKey(fluid.getFluid()).toString()));
            line.put("Alternatives",alternatives);
            line.putLong("Amount", stack.getAmount()); line.putFloat("Chance", entry.chance); fluids.add(line);
        }
        if (!items.isEmpty()) result.put("Items", items);
        if (!fluids.isEmpty()) result.put("Fluids", fluids);
        return result;
    }
}

